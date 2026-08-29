#!/usr/bin/env python3
"""Validate the structural integrity of server_design_roadmap.md"""

import re
import os
import sys

ROADMAP = "knowledge/server_design_roadmap.md"

def main():
    issues = []
    if not os.path.exists(ROADMAP):
        print(f"❌ File not found: {ROADMAP}")
        sys.exit(1)
    
    with open(ROADMAP, "r") as f:
        content = f.read()
        lines = content.split("\n")
    
    # 1. Check all 14 domain headings exist
    expected_domains = [
        "系统架构", "硬件设计", "固件/BMC", "软件/驱动",
        "结构设计", "散热设计", "供应链/采购", "项目管理",
        "售后运维", "售前", "需求管理", "客户关系",
        "系统集成", "生产与交付"
    ]
    
    h2_headings = [l for l in lines if l.startswith("## ")]
    found_domains = []
    for h in h2_headings:
        for d in expected_domains:
            if d in h:
                found_domains.append(d)
                break
    
    missing = [d for d in expected_domains if d not in found_domains]
    if missing:
        issues.append(f"❌ Missing domain sections: {missing}")
    else:
        print(f"✅ All {len(expected_domains)} domains present")
    
    # 2. Check no duplicate domain headings
    seen = {}
    for h in h2_headings:
        for d in expected_domains:
            if d in h:
                seen.setdefault(d, 0)
                seen[d] += 1
                if seen[d] > 1:
                    issues.append(f"❌ Duplicate heading for domain: {d}")
                    break
    
    if not any("Duplicate" in i for i in issues):
        print("✅ No duplicate domain headings")
    
    # 3. Check changelog is at bottom (not version in header)
    header_lines = lines[:15]
    header_text = "\n".join(header_lines)
    
    # Check if the version line in header is too long (indicates detailed log in header)
    version_lines = [l for l in header_lines if "v3." in l]
    for vl in version_lines:
        if len(vl) > 200:
            issues.append(f"⚠️  Header version line is very long ({len(vl)} chars) - may contain detailed changelog")
    
    # Check Changelog appendix exists
    if "## 附录 C" not in content and "变更日志" not in content:
        issues.append("⚠️  No Changelog appendix found")
    else:
        # Check changelog is near the bottom
        changelog_idx = content.find("## 附录 C")
        if changelog_idx > 0:
            # Should be in last 20% of file
            if changelog_idx < len(content) * 0.7:
                issues.append("⚠️  Changelog is not near the bottom of the file")
            else:
                print("✅ Changelog positioned at bottom")
    
    # 4. Check for misplaced content between domain sections
    # Look for "✦" activity tables that appear between domain header and their domain section
    # This is a heuristic check
    empty_sections_between = 0
    for i, line in enumerate(lines):
        if line.strip() == "---" and i > 0:
            prev_section = lines[i-1].strip() if i-1 >= 0 else ""
            next_section = lines[i+1].strip() if i+1 < len(lines) else ""
            # Check if empty section divider has content before/after that seems misplaced
            if not prev_section and not next_section:
                empty_sections_between += 1
    
    if empty_sections_between > 30:
        issues.append(f"⚠️  {empty_sections_between} empty sections found - possible formatting issues")
    else:
        print(f"✅ Formatting clean ({empty_sections_between} empty separators)")
    
    # 5. Check link format consistency
    md_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
    broken_links = []
    for text, url in md_links:
        # Skip external/absolute URLs and anchors
        if url.startswith("http") or url.startswith("#") or url.startswith("../import/") or "#" in url:
            continue
        # Check relative links point to existing files
        full_path = os.path.join("knowledge", url)
        if not os.path.exists(full_path) and not url.endswith("/"):
            broken_links.append((text, url))
    
    # Only report a sample - there may be many broken links from import/ references
    if broken_links:
        # Filter out import/ references which are expected to be broken
        real_broken = [(t, u) for t, u in broken_links if not u.startswith("../import/")]
        if real_broken:
            issues.append(f"⚠️  {len(real_broken)} potentially broken links (excluding import/)")
    
    # Summary
    print(f"\n{'='*50}")
    if issues:
        print(f"Found {len(issues)} issue(s):")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        sys.exit(1)
    else:
        print("✅ All checks passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()
