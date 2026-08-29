#!/usr/bin/env python3
"""table-fixer.py — 最小干预 Markdown 表格修复器（零内容丢失）

修复范围（严格限定表格结构）：
- C1: 分隔行格式错误（| --- | 数量/格式）
- C3: 表格缺分隔行 → 按表头列数补分隔行
- C2: 单元格列数 < 分隔行列数 → 补空单元格（不删不并，内容零丢失）
- 不做全表格对齐（避免大 diff）；多余列（内容级问题）只报不修

用法：
  python3 scripts/check/table-fixer.py [--dir knowledge/02_rd] [--dry-run] [--json]
默认: 全库扫描 + dry-run 报告
"""
import argparse
import json
import re
import sys
from pathlib import Path

KNOWLEDGE = Path(__file__).resolve().parents[2] / "knowledge"
SKIP = {"bak", "oldbak", "tmp", ".git", "node_modules"}

SEP_CELL = re.compile(r"^:?-{1,}:?$")  # --- | :--- | ---: | :---:

def is_separator_row(line: str) -> bool:
    """判断是否为合法分隔行（每格都是 - 或 :--: 形态）"""
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return len(cells) > 0 and all(SEP_CELL.match(c) for c in cells)

def fix_table(lines: list, start: int) -> tuple:
    """修复从 start 开始的表格块。返回 (修复后的行, 统计dict)"""
    stats = {"files": 0, "c1_sep": 0, "c3_missing": 0, "c2_pad": 0}
    # 定位表格范围
    i = start
    while i < len(lines) and lines[i].strip().startswith("|"):
        i += 1
    block = lines[start:i]
    if len(block) < 2:
        return lines, stats
    # 表头行
    header = [c.strip() for c in block[0].strip().strip("|").split("|")]
    ncols = len(header)
    # 找分隔行
    sep_idx = None
    for j in range(1, min(3, len(block))):
        if is_separator_row(block[j]):
            sep_idx = j
            break
    out = list(block)
    if sep_idx is None:
        # C3: 补分隔行（在表头后）
        sep = "| " + " | ".join(["---"] * ncols) + " |"
        out.insert(1, sep)
        stats["c3_missing"] += 1
        sep_idx = 1
    else:
        # C1: 规范化分隔行（列数与表头一致）
        sep_cells = [c.strip() for c in out[sep_idx].strip().strip("|").split("|")]
        if len(sep_cells) != ncols:
            # 以表头列数为准补/删分隔单元
            if len(sep_cells) < ncols:
                sep_cells += ["---"] * (ncols - len(sep_cells))
            else:
                sep_cells = sep_cells[:ncols]
            out[sep_idx] = "| " + " | ".join(sep_cells) + " |"
            stats["c1_sep"] += 1
        else:
            # 分隔符本身可能格式错误（如 |--| 或 | -- |）
            norm = ["---" if not SEP_CELL.match(c) else c for c in sep_cells]
            if norm != sep_cells:
                out[sep_idx] = "| " + " | ".join(norm) + " |"
                stats["c1_sep"] += 1
    # C2: 数据行列数补足（只补不删）
    for j in range(sep_idx + 1, len(out)):
        row = out[j].strip()
        if not row.startswith("|"):
            continue
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if len(cells) == ncols:
            continue
        if len(cells) < ncols:
            out[j] = "| " + " | ".join(cells + [""] * (ncols - len(cells))) + " |"
            stats["c2_pad"] += 1
    return lines[:start] + out + lines[i:], stats

def process(path: Path, dry_run: bool) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.split("\n")
    stats = {"c1_sep": 0, "c3_missing": 0, "c2_pad": 0}
    new_lines = list(lines)
    changed = False
    j = 0
    while j < len(new_lines):
        if new_lines[j].strip().startswith("|") and not new_lines[j].strip().startswith("| "):
            # 需要后续行确认表格上下文
            pass
        if new_lines[j].strip().startswith("|"):
            # 检查是否是表格（后 1-2 行有分隔行或都是 | 行）
            k = j + 1
            while k < len(new_lines) and new_lines[k].strip().startswith("|"):
                k += 1
            # 表格块至少 2 行
            if k - j >= 2:
                new_lines, s = fix_table(new_lines, j)
                for key in stats:
                    stats[key] += s[key]
                if any(s.values()):
                    changed = True
                j = k
                continue
        j += 1
    if changed and not dry_run:
        path.write_text("\n".join(new_lines), encoding="utf-8")
    return stats

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=None, help="目标目录，默认全库")
    ap.add_argument("--dry-run", action="store_true", default=True, help="仅报告（默认）")
    ap.add_argument("--apply", action="store_true", help="实际写回")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.apply:
        args.dry_run = False
    root = Path(args.dir).resolve() if args.dir else KNOWLEDGE
    total = {"c1_sep": 0, "c3_missing": 0, "c2_pad": 0}
    nfiles = 0
    for p in sorted(root.rglob("*.md")):
        if KNOWLEDGE not in p.parents and p != KNOWLEDGE:
            continue
        s = process(p, args.dry_run)
        if any(s.values()):
            nfiles += 1
            for k in total:
                total[k] += s[k]
    if args.json:
        print(json.dumps({"files": nfiles, **total}, ensure_ascii=False))
    else:
        print(f"扫描完成: 修改 {nfiles} 文件 (dry-run={args.dry_run})")
        for k, v in total.items():
            print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
