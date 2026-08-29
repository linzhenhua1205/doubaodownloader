#!/usr/bin/env python3
"""
ref-drift-detector.py — Knowledge Base Reference Drift Detector

Detects when source files have been updated but their referencing files
haven't been synchronized — the "copy-paste drift" problem in Markdown.

Scans knowledge/ for @ref markers and performs three-level drift detection:

  L1 PATH_DRIFT   — Source file was moved or deleted
  L2 TIME_DRIFT   — Source file modified after last-verified date
  L3 CONTENT_DRIFT— Source content hash doesn't match stored hash

@ref marker format (in HTML comments, doesn't affect rendering):

  <!-- @ref: path/to/source.md, YYYY-MM-DD, hash:xxxxxxxxxxxx -->
  <!-- @ref: path/to/source.md#section, YYYY-MM-DD, hash:xxxxxxxxxxxx -->

Usage:
    python3 scripts/check/ref-drift-detector.py                         # Full scan
    python3 scripts/check/ref-drift-detector.py --module 02_rd          # Per-module
    python3 scripts/check/ref-drift-detector.py --file report.md        # Single file
    python3 scripts/check/ref-drift-detector.py --json                  # JSON output
    python3 scripts/check/ref-drift-detector.py --drifted-only          # Drifts only
    python3 scripts/check/ref-drift-detector.py --graph                 # Print dependency graph
"""

import os
import re
import sys
import json
import hashlib
import argparse
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

from scripts.shared.workspace import WORKSPACE_ROOT, KNOWLEDGE_ROOT  # sr-008


# ── Constants ──────────────────────────────────────────────────────────────────

# Knowledge base root (this script is at scripts/check/ref-drift-detector.py)
KNOWLEDGE_ROOT = WORKSPACE_ROOT / "knowledge"

# Regex for extracting @ref markers from HTML comments
# Matches: <!-- @ref: path/to/file.md, YYYY-MM-DD, hash:xxxx -->
REF_PATTERN = re.compile(
    r'<!--\s*@ref:\s*(\S+?)(?:#(\S+?))?\s*,\s*(\d{4}-\d{2}-\d{2})\s*,\s*hash:(\w+)\s*-->',
    re.IGNORECASE
)

# Date format for last-verified
DATE_FMT = "%Y-%m-%d"

# Output directory for artifacts
OUTPUT_DIR = Path(__file__).resolve().parent / "ref-graph"


# ── Data Structures ────────────────────────────────────────────────────────────

class RefMarker:
    """A single @ref marker found in a file."""
    def __init__(self, source_file: Path, ref_target: str, section: Optional[str],
                 last_verified: str, stored_hash: str, line_no: int):
        self.source_file = source_file          # The file containing this marker
        self.ref_target = ref_target            # Relative path to target (from knowledge/)
        self.section = section                  # Optional section anchor
        self.last_verified = last_verified      # YYYY-MM-DD string
        self.stored_hash = stored_hash.lower()  # Stored hash from marker
        self.line_no = line_no                  # Line number in source file

    @property
    def target_abs_path(self) -> Path:
        """
        Resolve relative target path to absolute path.

        Paths in @ref markers follow Markdown link conventions:
        relative to the source file's directory, not relative to
        the knowledge base root.
        """
        return (self.source_file.parent / self.ref_target).resolve()

    @property
    def target_rel_path(self) -> str:
        """Get target path relative to knowledge root for display."""
        try:
            return str(self.target_abs_path.relative_to(KNOWLEDGE_ROOT))
        except ValueError:
            return str(self.target_abs_path)

    @property
    def is_valid_path(self) -> bool:
        return self.target_abs_path.exists()

    def __repr__(self):
        return (f"RefMarker(src={self.source_file.name}, "
                f"target={self.ref_target}#{self.section or ''}, "
                f"verified={self.last_verified}, hash={self.stored_hash})")


class DriftResult:
    """Result of drift detection for a single ref marker."""
    def __init__(self, marker: RefMarker):
        self.marker = marker
        self.status = "UNKNOWN"         # GREEN / YELLOW / RED / MISSING
        self.detail = ""                # Human-readable detail
        self.current_hash = ""          # Actual hash of target content

    def to_dict(self) -> dict:
        return {
            "source_file": str(self.marker.source_file.relative_to(WORKSPACE_ROOT)),
            "target_file": self.marker.ref_target,
            "target_resolved": self.marker.target_rel_path,
            "section": self.marker.section or "",
            "last_verified": self.marker.last_verified,
            "stored_hash": self.marker.stored_hash,
            "current_hash": self.current_hash,
            "status": self.status,
            "detail": self.detail,
            "line_no": self.marker.line_no,
        }


# ── Core Functions ─────────────────────────────────────────────────────────────

def compute_file_hash(filepath: Path) -> str:
    """Compute SHA256 hash (first 12 chars) of a file."""
    hasher = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                hasher.update(chunk)
        return hasher.hexdigest()[:12]
    except (IOError, PermissionError):
        return ""


def compute_section_hash(filepath: Path, section: Optional[str] = None) -> str:
    """
    Compute SHA256 hash of a specific section (or whole file if no section).
    Section is matched by anchor ID {#section} or ## section header.
    """
    if not section:
        return compute_file_hash(filepath)

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except (IOError, PermissionError):
        return ""

    # Try to find section by anchor {#section}
    anchor_pattern = re.compile(r'{#' + re.escape(section) + r'}\s*\n(.*?)(?=\n##|\Z)', re.DOTALL)
    match = anchor_pattern.search(content)
    if match:
        return hashlib.sha256(match.group(1).encode()).hexdigest()[:12]

    # Try to find section by header matching section name
    header_pattern = re.compile(
        r'^##\s+.*?' + re.escape(section.replace('-', ' ').replace('_', ' ')) + r'.*?\n(.*?)(?=\n##|\Z)',
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )
    match = header_pattern.search(content)
    if match:
        return hashlib.sha256(match.group(1).encode()).hexdigest()[:12]

    # Section not found, hash whole file as fallback
    return compute_file_hash(filepath)


def get_file_mtime(filepath: Path) -> Optional[datetime]:
    """Get file modification time as UTC datetime."""
    try:
        mtime = os.path.getmtime(filepath)
        return datetime.fromtimestamp(mtime, tz=timezone.utc)
    except OSError:
        return None


def scan_file_for_refs(filepath: Path) -> List[RefMarker]:
    """Scan a single .md file for @ref markers.

    Skips content inside fenced code blocks (``` ... ```) to avoid
    matching example references in documentation.
    """
    markers = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except (IOError, PermissionError) as e:
        print(f"  ⚠️  Cannot read {filepath}: {e}", file=sys.stderr)
        return markers

    in_code_block = False
    for lineno, line in enumerate(lines, 1):
        # Toggle code block state (fenced code blocks only)
        stripped = line.strip()
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            continue

        # Skip lines inside code blocks
        if in_code_block:
            continue

        for match in REF_PATTERN.finditer(line):
            ref_target = match.group(1)
            section = match.group(2)
            last_verified = match.group(3)
            stored_hash = match.group(4)
            marker = RefMarker(
                source_file=filepath,
                ref_target=ref_target,
                section=section,
                last_verified=last_verified,
                stored_hash=stored_hash,
                line_no=lineno
            )
            markers.append(marker)

    return markers


def scan_knowledge_base(module: Optional[str] = None,
                        single_file: Optional[str] = None) -> List[RefMarker]:
    """Scan the knowledge base for all @ref markers."""
    all_markers = []

    if single_file:
        # Scan a single file
        filepath = (WORKSPACE_ROOT / single_file).resolve()
        if not filepath.exists():
            print(f"❌ File not found: {single_file}", file=sys.stderr)
            sys.exit(1)
        if filepath.suffix == '.md':
            markers = scan_file_for_refs(filepath)
            all_markers.extend(markers)
            print(f"  📄 {filepath.relative_to(WORKSPACE_ROOT)}: {len(markers)} ref(s)")
        return all_markers

    # Determine scan root
    if module:
        scan_root = KNOWLEDGE_ROOT / module
        if not scan_root.exists():
            print(f"❌ Module not found: {module}", file=sys.stderr)
            sys.exit(1)
        print(f"🔍 Scanning module: {module}")
    else:
        scan_root = KNOWLEDGE_ROOT
        print(f"🔍 Scanning entire knowledge base")

    # Walk through all .md files
    md_files = list(scan_root.rglob("*.md"))
    print(f"   Found {len(md_files)} .md files")

    for filepath in md_files:
        # Skip node_modules, bak, etc.
        rel = filepath.relative_to(KNOWLEDGE_ROOT)
        parts = rel.parts
        if 'node_modules' in parts or 'bak' in parts or '.git' in parts:
            continue

        markers = scan_file_for_refs(filepath)
        if markers:
            all_markers.extend(markers)

    return all_markers


def detect_drift(markers: List[RefMarker]) -> List[DriftResult]:
    """Perform three-level drift detection on all markers."""
    results = []

    for marker in markers:
        result = DriftResult(marker)

        # L1: Path drift — does the target exist?
        if not marker.is_valid_path:
            result.status = "MISSING"
            result.detail = f"🔴 Target file not found: {marker.ref_target}"
            results.append(result)
            continue

        target_path = marker.target_abs_path

        # Compute current hash
        current_hash = compute_section_hash(target_path, marker.section)
        result.current_hash = current_hash

        # L3: Content drift — hash comparison
        if current_hash and current_hash != marker.stored_hash:
            result.status = "DRIFTED"
            result.detail = (f"🟠 Content changed: hash {marker.stored_hash} → {current_hash}"
                             f" (in {marker.ref_target}"
                             f"{'#' + marker.section if marker.section else ''})")
            results.append(result)
            continue

        # L2: Time drift — file mtime vs last-verified
        mtime = get_file_mtime(target_path)
        if mtime:
            try:
                verified_date = datetime.strptime(marker.last_verified, DATE_FMT)
                verified_date = verified_date.replace(tzinfo=timezone.utc)
                if mtime > verified_date:
                    # File modified after last-verified, but content hash matches
                    # This means the file was touched but the relevant section didn't change
                    # Still, flag it as YELLOW for human review
                    result.status = "TOUCHED"
                    result.detail = (f"🟡 File modified after last-verified: "
                                     f"mtime={mtime.strftime(DATE_FMT)} > verified={marker.last_verified}"
                                     f" (but hash matches, section unchanged)")
                    results.append(result)
                    continue
            except ValueError:
                pass

        # All checks passed
        result.status = "GREEN"
        result.detail = f"✅ Up to date (verified {marker.last_verified})"
        results.append(result)

    return results


def build_dependency_graph(markers: List[RefMarker]) -> Dict[str, List[dict]]:
    """Build a dependency graph: source → list of referencing files."""
    graph = defaultdict(list)

    for marker in markers:
        target = marker.target_rel_path
        graph[target].append({
            "source_file": str(marker.source_file.relative_to(WORKSPACE_ROOT)),
            "ref_target": marker.ref_target,
            "section": marker.section or "",
            "line_no": marker.line_no,
            "last_verified": marker.last_verified,
        })

    return dict(graph)


def print_report(results: List[DriftResult], drifted_only: bool = False):
    """Print human-readable drift report."""
    total = len(results)
    green = sum(1 for r in results if r.status == "GREEN")
    yellow = sum(1 for r in results if r.status == "TOUCHED")
    red = sum(1 for r in results if r.status == "DRIFTED")
    missing = sum(1 for r in results if r.status == "MISSING")

    print("\n" + "=" * 70)
    print("  📊 Reference Drift Detection Report")
    print("=" * 70)

    # Summary
    print(f"\n  Total refs: {total}")
    print(f"  ✅ GREEN:   {green}")
    print(f"  🟡 TOUCHED: {yellow}")
    print(f"  🟠 DRIFTED: {red}")
    print(f"  🔴 MISSING: {missing}")

    if red > 0 or missing > 0:
        print(f"\n  ⚠️  {red + missing} issue(s) require attention!")

    # Details
    print("\n" + "-" * 70)
    print("  Details")
    print("-" * 70)

    for result in results:
        if drifted_only and result.status == "GREEN":
            continue

        marker = result.marker
        src_rel = marker.source_file.relative_to(WORKSPACE_ROOT)

        status_icon = {
            "GREEN": "✅",
            "TOUCHED": "🟡",
            "DRIFTED": "🟠",
            "MISSING": "🔴",
            "UNKNOWN": "❓"
        }.get(result.status, "❓")

        print(f"\n  {status_icon} [{result.status}]")
        print(f"     Source:   {src_rel}:{marker.line_no}")
        print(f"     Refers:   {marker.ref_target}"
              f"{'#' + marker.section if marker.section else ''}")
        print(f"     Resolved: {marker.target_rel_path}")
        print(f"     Detail:   {result.detail}")

    print("\n" + "=" * 70)


def print_graph(graph: Dict[str, List[dict]]):
    """Print dependency graph in human-readable format."""
    print("\n" + "=" * 70)
    print("  🔗 Reference Dependency Graph")
    print("=" * 70)

    if not graph:
        print("\n  (no references found)")
        return

    # Sort by number of referencing files (most referenced first)
    sorted_targets = sorted(graph.items(), key=lambda x: len(x[1]), reverse=True)

    for target, refs in sorted_targets:
        print(f"\n  📄 {target} — referenced by {len(refs)} file(s):")
        for ref in refs:
            print(f"       ← {ref['source_file']}:{ref['line_no']}"
                  f"{'  (§' + ref['section'] + ')' if ref['section'] else ''}"
                  f"  (as `{ref['ref_target']}`)")

    # Statistics
    all_refs = sum(len(refs) for _, refs in sorted_targets)
    print(f"\n  📊 Total: {len(graph)} source files, {all_refs} references")
    print("=" * 70)


def save_json_report(results: List[DriftResult], graph: dict):
    """Save JSON report to output directory."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Drift results
    report_data = {
        "scan_time": datetime.now(timezone.utc).isoformat(),
        "knowledge_root": str(KNOWLEDGE_ROOT),
        "summary": {
            "total": len(results),
            "green": sum(1 for r in results if r.status == "GREEN"),
            "touched": sum(1 for r in results if r.status == "TOUCHED"),
            "drifted": sum(1 for r in results if r.status == "DRIFTED"),
            "missing": sum(1 for r in results if r.status == "MISSING"),
        },
        "results": [r.to_dict() for r in results],
        "dependency_graph": graph,
    }

    json_path = OUTPUT_DIR / "ref-drift-report.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    print(f"\n  💾 JSON report saved to: {json_path.relative_to(WORKSPACE_ROOT)}")

    # Also save a markdown report
    md_path = OUTPUT_DIR / "ref-drift-report.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("# 🔗 Reference Drift Detection Report\n\n")
        f.write(f"> Scan time: {datetime.now(timezone.utc).isoformat()}\n\n")
        f.write("## Summary\n\n")
        f.write(f"| Status | Count |\n|:-------|:-----:|\n")
        f.write(f"| ✅ GREEN | {report_data['summary']['green']} |\n")
        f.write(f"| 🟡 TOUCHED | {report_data['summary']['touched']} |\n")
        f.write(f"| 🟠 DRIFTED | {report_data['summary']['drifted']} |\n")
        f.write(f"| 🔴 MISSING | {report_data['summary']['missing']} |\n")
        f.write(f"| **Total** | **{report_data['summary']['total']}** |\n")

        # Issues section
        issues = [r for r in results if r.status in ("DRIFTED", "MISSING", "TOUCHED")]
        if issues:
            f.write("\n## ⚠️ Issues Requiring Attention\n\n")
            for r in issues:
                m = r.marker
                src_rel = m.source_file.relative_to(WORKSPACE_ROOT)
                f.write(f"- **[{r.status}]** `{src_rel}:{m.line_no}` → "
                        f"`{m.ref_target}#{m.section or ''}`\n")
                f.write(f"  - {r.detail}\n")

        # All clear
        if not issues:
            f.write("\n## ✅ All Clear\n\nNo drift issues detected.\n")

        f.write("\n---\n")
        f.write(f"> Auto-generated by `ref-drift-detector.py`\n")

    print(f"  💾 Markdown report saved to: {md_path.relative_to(WORKSPACE_ROOT)}")


# ── Main ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Detect reference drift in knowledge base Markdown files"
    )
    parser.add_argument('--module', type=str, default=None,
                        help='Scan a specific module (e.g., "02_rd")')
    parser.add_argument('--file', type=str, default=None,
                        help='Scan a single file (relative to workspace root)')
    parser.add_argument('--json', action='store_true', default=False,
                        help='Output JSON report instead of text')
    parser.add_argument('--drifted-only', action='store_true', default=False,
                        help='Show only drifted/missing items')
    parser.add_argument('--graph', action='store_true', default=False,
                        help='Print dependency graph')
    parser.add_argument('--save', action='store_true', default=True,
                        help='Save reports to ref-graph/ directory')

    args = parser.parse_args()

    print(f"🔄 Reference Drift Detector v1.0")
    print(f"   Knowledge base: {KNOWLEDGE_ROOT}")

    # Step 1: Scan for ref markers
    markers = scan_knowledge_base(module=args.module, single_file=args.file)

    if not markers:
        print("\n📭 No @ref markers found in scanned files.")
        print("   Tip: Add <!-- @ref: path/to/file.md, YYYY-MM-DD, hash:xxxx -->")
        print("   above referenced content to enable drift detection.")
        sys.exit(0)

    print(f"\n📌 Found {len(markers)} @ref marker(s)")

    # Step 2: Build dependency graph
    graph = build_dependency_graph(markers)

    if args.graph:
        print_graph(graph)

    # Step 3: Detect drift
    results = detect_drift(markers)

    # Step 4: Output
    if args.json:
        report_data = {
            "scan_time": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total": len(results),
                "green": sum(1 for r in results if r.status == "GREEN"),
                "touched": sum(1 for r in results if r.status == "TOUCHED"),
                "drifted": sum(1 for r in results if r.status == "DRIFTED"),
                "missing": sum(1 for r in results if r.status == "MISSING"),
            },
            "results": [r.to_dict() for r in results],
            "dependency_graph": graph,
        }
        print(json.dumps(report_data, indent=2, ensure_ascii=False))
    else:
        print_report(results, drifted_only=args.drifted_only)

    # Save reports
    if args.save:
        save_json_report(results, graph)

    # Exit with code
    drifted = sum(1 for r in results if r.status in ("DRIFTED", "MISSING"))
    sys.exit(1 if drifted > 0 else 0)


if __name__ == '__main__':
    main()
