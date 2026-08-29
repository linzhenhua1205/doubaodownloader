#!/usr/bin/env python3
"""import-to-knowledge.py — FR-28: discover → knowledge 导入

将通过质量门禁的内容归档到 knowledge/ 对应模块，自动更新 index.md + log.md。
当前为原型版本，核心导入逻辑待实现。

用法:
  python3 scripts/discover/import-to-knowledge.py --input discover/newwiki2/file.md --target knowledge/02_rd/
  python3 scripts/discover/import-to-knowledge.py --input discover/newwiki2/server-hardware/ --auto-classify
  python3 scripts/discover/import-to-knowledge.py --input discover/newwiki2/ --gate-only
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

from config import DISCOVER_DIR, KNOWLEDGE_DIR, CLASSIFICATION_SYSTEM


def quality_gate_check(content: str, file_path: Path) -> tuple[bool, list[str]]:
    """质量门禁检查（Q-03~Q-09）"""
    passed = True
    checks = []

    # Q-03: 断言可追溯
    has_source = bool(re.search(r"(?:来源|参考|根据|数据来自|引自|参见|http)", content))
    checks.append(("Q-03 断言可追溯", has_source, "核心断言需标注来源"))
    if not has_source:
        passed = False

    # Q-04: 数据四要素
    has_unit = bool(re.search(r"\d+\.?\d*\s*(?:TB|GB|MB|KW|W|ns|μs|ms|GHz|MHz|%|x|倍)", content))
    checks.append(("Q-04 数据四要素", has_unit, "量化数据需含数值+单位+基线+条件"))
    if not has_unit:
        passed = False

    # Q-05: 非空摘要
    has_summary = (content.startswith("> **摘要**") or "## 摘要" in content[:500]
                   or content[:200].strip().startswith("# "))
    checks.append(("Q-05 非空摘要", has_summary, "文件开头需有 2-5 句摘要"))
    if not has_summary:
        passed = False

    # Q-06: 格式合规（基本检查）
    has_headings = bool(re.search(r"^#{1,4}\s", content, re.MULTILINE))
    checks.append(("Q-06 格式合规", has_headings, "文档需有标题层级"))

    # Q-08: 有明确归入模块
    target = infer_knowledge_target(content, file_path)
    checks.append(("Q-08 明确归入模块", target is not None, f"无法确定归入 knowledge/ 哪个模块"))

    # Q-09: 无 bak 引用
    # bak/引用规则 — check 模式：检测引用
    no_bak = "tmp/bak" not in content and "knowledge/bak" not in content
    checks.append(("Q-09 无 bak 引用", no_bak, "不可引用 bak 内容"))
    if not no_bak:
        passed = False

    return passed, checks


def infer_knowledge_target(content: str, file_path: Path) -> str | None:
    """推断内容应归入 knowledge/ 的哪个模块"""
    text = (content[:3000] + " " + file_path.name).lower()

    # 按分类体系匹配
    best_match = None
    best_score = 0
    for category, info in CLASSIFICATION_SYSTEM.items():
        score = sum(text.count(kw.lower()) for kw in info["keywords"])
        if score > best_score:
            best_score = score
            best_match = info["knowledge_target"]

    return best_match


def update_index_and_log(target_path: Path, file_name: str):
    """更新索引和 log（V3: 全局模块分布式 index.md 已废弃）。

    - 保留目录（weekly-reports）: 继续写目标目录 index.md；01_survey 不再维护 index（2026-08-19 起）
    - 全局模块: 不写 index.md，提示走 README.md 条目库（人工）+ kb-global-index.py 刷新
    """
    # index.md 追加（仅保留分布式机制的目录）
    KEEP_DISTRIBUTED = ("01_survey", "weekly-reports")
    is_kept = any(part in KEEP_DISTRIBUTED for part in target_path.parts)
    index_file = target_path / "index.md"
    if is_kept and index_file.exists():
        entry = f"| `{file_name}` | — | 从 discover/ 导入 |\n"
        with open(index_file, "a", encoding="utf-8") as f:
            f.write(entry)
        print(f"  [INDEX] 已追加到 {index_file.name}")
    elif not is_kept:
        print("  [INDEX] 全局模块 index.md 已废弃（V3）；2026-08-15 起 AI/脚本日常不动 index.md/README.md，由 kb-global-index.py 批量刷新，只追加 log.md")
    else:
        print(f"  [WARN] index.md 不存在: {index_file}")

    # log.md 追加
    log_file = target_path / "log.md"
    if log_file.exists():
        today = datetime.now().strftime("%Y-%m-%d")
        log_entry = f"| {today} | 从 discover/ 导入: `{file_name}` |\n"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
        print(f"  [LOG] 已追加到 {log_file.name}")


def main():
    parser = argparse.ArgumentParser(
        description="FR-28: discover → knowledge 导入",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--input", "-i", required=True, help="输入文件或目录路径")
    parser.add_argument("--target", "-t", default=None, help="目标 knowledge/ 子目录（可选，默认自动分类）")
    parser.add_argument("--auto-classify", action="store_true", help="自动分类到 knowledge/ 对应模块")
    parser.add_argument("--gate-only", action="store_true", help="仅执行质量门禁检查，不实际导入")
    parser.add_argument("--dry-run", action="store_true", help="预览模式")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = DISCOVER_DIR.parent / input_path

    if not input_path.exists():
        print(f"[ERROR] 路径不存在: {input_path}", file=sys.stderr)
        sys.exit(1)

    # 收集文件
    files = []
    if input_path.is_dir():
        files = sorted(input_path.rglob("*.md"))
    else:
        files = [input_path]

    if not files:
        print("[WARN] 未找到 .md 文件")
        sys.exit(0)

    # 排除 index.md / log.md
    files = [f for f in files if f.name not in ("index.md", "log.md")]

    print(f"[INFO] 待处理: {len(files)} 个文件")

    passed_count = 0
    failed_count = 0

    for f in files:
        print(f"\n  📄 {f.name}")

        try:
            content = f.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            print(f"    [ERROR] 读取失败: {e}")
            continue

        # 质量门禁
        passed, checks = quality_gate_check(content, f)
        all_ok = all(ok for _, ok, _ in checks)

        print(f"    {'✅' if all_ok else '❌'} 质量门禁:")
        for name, ok, desc in checks:
            status = "✅" if ok else "❌"
            print(f"      {status} {name} — {'通过' if ok else desc}")

        if args.gate_only or not all_ok:
            if not all_ok:
                failed_count += 1
            continue

        passed_count += 1

        # 确定目标路径
        if args.target:
            target_path = Path(args.target)
            if not target_path.is_absolute():
                target_path = KNOWLEDGE_DIR.parent / target_path
        elif args.auto_classify:
            target = infer_knowledge_target(content, f)
            if target:
                target_path = Path(target)
                if not target_path.is_absolute():
                    target_path = KNOWLEDGE_DIR.parent / target_path
                print(f"    → 自动分类至: {target_path.name}")
            else:
                print(f"    [WARN] 无法自动分类，跳过")
                continue
        else:
            target_path = KNOWLEDGE_DIR
            print(f"    → 导入到: {target_path.name}")

        if not args.dry_run:
            # 复制文件
            target_path.mkdir(parents=True, exist_ok=True)
            target_file = target_path / f.name
            target_file.write_text(content, encoding="utf-8")
            print(f"    [OK] 已复制到 {target_file}")

            # 更新 index + log
            update_index_and_log(target_path, f.name)

    # 汇总
    print(f"\n{'='*60}")
    print(f"  导入汇总")
    print(f"{'='*60}")
    print(f"  总文件:     {len(files)}")
    print(f"  通过门禁:   {passed_count}")
    print(f"  未通过:     {failed_count if not args.gate_only else 0}")
    if args.gate_only:
        print(f"  (仅门禁检查，未实际导入)")
    if args.dry_run:
        print(f"  (预览模式，未实际操作)")


if __name__ == "__main__":
    main()
