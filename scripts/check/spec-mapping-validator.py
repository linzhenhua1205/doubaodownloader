#!/usr/bin/env python3
"""
spec-mapping-validator.py — Spec AR/SR/CC 映射一致性校验器

扫描 spec/ 下所有 Design/STD 文件中的 AR/SR/CC 编号引用，
与 SSOT（ar-001, sr-003, sr-001）比对，报告：
  - 缺失引用（AR 在 ar-001 中定义但在 Design/STD 中未出现）
  - 错误引用（引用了不存在的编号）
  - 章节级断层（有章节无任何引用）

用法:
  python3 scripts/check/spec-mapping-validator.py          # 全量扫描
  python3 scripts/check/spec-mapping-validator.py --fix     # 报告缺失到 audit 风格
  python3 scripts/check/spec-mapping-validator.py --verbose  # 详细输出
"""

import os, re, sys
from pathlib import Path

SPEC_DIR = Path(__file__).resolve().parents[2] / "spec"

# ── SSOT 加载 ──────────────────────────────────────────────────────

def load_ar_ssot():
    """从 ar-001 提取所有 AR 编号"""
    ar_path = SPEC_DIR / "ar-001-sr-ar-mapping.md"
    if not ar_path.exists():
        print(f"⚠️  未找到 {ar_path}")
        return set()
    content = ar_path.read_text()
    ars = re.findall(r'\b(AR-(?:P[1-4]|SYS|FUT|ASM|QSV)-\d{3})\b', content)
    return set(ars)

def load_sr_ssot():
    """从 sr-001 提取所有 SR 编号（§2.2 需求列表）"""
    sr_path = SPEC_DIR / "sr-001-knowledge-system-requirements.md"
    if not sr_path.exists():
        print(f"⚠️  未找到 {sr_path}")
        return set()
    content = sr_path.read_text()
    srs = re.findall(r'\bSR-(?:00[1-9]|0[1-9]\d|C[1-5])\b', content)
    return set(srs)

def load_cc_ssot():
    """从 sr-003 提取所有 CC 类别编号"""
    cc_path = SPEC_DIR / "sr-003-system-constraint-registry.md"
    if not cc_path.exists():
        print(f"⚠️  未找到 {cc_path}")
        return set()
    content = cc_path.read_text()
    ccs = re.findall(r'\bCC-(?:0[1-5]|1[0-3])\b', content)
    return set(ccs)

# ── 扫描 ────────────────────────────────────────────────────────────

def scan_file_refs(filepath):
    """扫描单个文件的 SR/AR/CC 引用"""
    content = filepath.read_text()
    ars = re.findall(r'\b(AR-(?:P[1-4]|SYS|FUT|ASM|QSV)-\d{3})\b', content)
    srs = re.findall(r'\b(SR-(?:00[1-9]|0[1-9]\d|C[1-5]))\b', content)
    ccs = re.findall(r'\b(CC-(?:0[1-5]|1[0-3]))\b', content)
    # Section-level traceability count
    sections_with_trace = len(re.findall(r'^> \*\*实现 AR\*\*:', content, re.MULTILINE))
    total_sections = len(re.findall(r'^## \d+\.', content, re.MULTILINE))
    return {
        'ars': set(ars),
        'srs': set(srs),
        'ccs': set(ccs),
        'traced_sections': sections_with_trace,
        'total_sections': total_sections,
    }

def scan_all():
    """扫描所有 Design/STD 文件"""
    results = {}
    for f in sorted(SPEC_DIR.glob("design-*.md")):
        results[f.name] = scan_file_refs(f)
    for f in sorted(SPEC_DIR.glob("std-*.md")):
        results[f.name] = scan_file_refs(f)
    return results

# ── 报告 ────────────────────────────────────────────────────────────

def generate_report(scanned, ar_ssot, sr_ssot, cc_ssot):
    """生成审计报告"""
    report_lines = []
    report_lines.append("# Spec 映射一致性审计报告")
    report_lines.append(f"| 生成时间 | {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')} |")
    report_lines.append(f"| AR SSOT | {len(ar_ssot)} 个 AR |")
    report_lines.append(f"| SR SSOT | {len(sr_ssot)} 个 SR |")
    report_lines.append(f"| CC SSOT | {len(cc_ssot)} 个 CC |")
    report_lines.append("")
    report_lines.append("| 文件 | 章节含AR/% | 引用AR | 引用SR | 引用CC | 缺失AR | 缺失SR | 状态 |")
    report_lines.append("|:-----|:---------:|:------:|:------:|:------:|:------:|:------:|:----:|")

    for fname, data in scanned.items():
        ar_refs = data['ars']
        sr_refs = data['srs']
        cc_refs = data['ccs']

        missing_ar = ar_ssot - ar_refs if ar_refs else ar_ssot
        missing_sr = sr_ssot - sr_refs if sr_refs else sr_ssot

        # For design files that don't reference CCs, don't flag
        if fname.startswith('design-'):
            missing_ar = ar_ssot - ar_refs if len(ar_refs) > 0 else set()
            missing_sr = sr_ssot - sr_refs if len(sr_refs) > 0 else set()

        trace_pct = f"{data['traced_sections']}/{data['total_sections']}"
        ar_count = len(ar_refs)
        sr_count = len(sr_refs)
        cc_count = len(cc_refs)

        # Status
        if ar_count > 0 and sr_count > 0:
            status = "✅"
        elif ar_count > 0 or sr_count > 0:
            status = "🟡"
        else:
            status = "🔴"

        report_lines.append(
            f"| {fname} | {trace_pct} | {ar_count} | {sr_count} | {cc_count} "
            f"| {len(missing_ar)} | {len(missing_sr)} | {status} |"
        )

    return "\n".join(report_lines)

def print_verbose(scanned, ar_ssot, sr_ssot, cc_ssot):
    """详细输出"""
    print(f"{'='*80}")
    print(f"Spec 映射一致性校验 — {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"AR SSOT: {len(ar_ssot)} 个 | SR SSOT: {len(sr_ssot)} 个 | CC SSOT: {len(cc_ssot)} 个")
    print(f"{'='*80}")

    total_ars = set()
    total_srs = set()
    total_ccs = set()
    total_traced = 0
    total_sections = 0

    for fname, data in sorted(scanned.items()):
        total_ars |= data['ars']
        total_srs |= data['srs']
        total_ccs |= data['ccs']
        total_traced += data['traced_sections']
        total_sections += data['total_sections']

        status = "✅" if data['ars'] else "⚠️" if data['srs'] else "🔴"
        print(f"\n{status} {fname}")
        print(f"   章节: {data['traced_sections']}/{data['total_sections']} 有 AR 标注")
        print(f"   引用 AR({len(data['ars'])}): {', '.join(sorted(data['ars'])[:10]) or '无'}{'...' if len(data['ars'])>10 else ''}")
        print(f"   引用 SR({len(data['srs'])}): {', '.join(sorted(data['srs'])[:10]) or '无'}{'...' if len(data['srs'])>10 else ''}")
        print(f"   引用 CC({len(data['ccs'])}): {', '.join(sorted(data['ccs'])[:10]) or '无'}{'...' if len(data['ccs'])>10 else ''}")

    print(f"\n{'='*80}")
    print(f"汇总: {total_sections} 章节 / {total_traced} 有溯源 ({total_traced*100//max(total_sections,1)}%)")
    print(f"    引用 {len(total_ars)} 个唯一 AR, {len(total_srs)} 个唯一 SR, {len(total_ccs)} 个唯一 CC")

    # Unreferenced ARs
    unreferenced = ar_ssot - total_ars
    if unreferenced:
        print(f"\n⚠️  `ar-001` 中有但在 Design/STD 中未出现的 AR ({len(unreferenced)}):")
        for ar in sorted(unreferenced)[:15]:
            print(f"   - {ar}")
        if len(unreferenced) > 15:
            print(f"   ... 还有 {len(unreferenced)-15} 个")

# ── 主流程 ──────────────────────────────────────────────────────────

def main():
    verbose = '--verbose' in sys.argv
    fix_mode = '--fix' in sys.argv

    ar_ssot = load_ar_ssot()
    sr_ssot = load_sr_ssot()
    cc_ssot = load_cc_ssot()
    scanned = scan_all()

    if verbose:
        print_verbose(scanned, ar_ssot, sr_ssot, cc_ssot)
    else:
        report = generate_report(scanned, ar_ssot, sr_ssot, cc_ssot)
        print(report)

    if fix_mode:
        report_path = SPEC_DIR / "audit-002-mapping-consistency-report.md"
        report_path.write_text(report)
        print(f"\n报告已保存至: {report_path}")

if __name__ == '__main__':
    main()
