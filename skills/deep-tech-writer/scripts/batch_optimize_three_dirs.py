#!/usr/bin/env python3
"""
三目录批量优化框架 - 数据与存储技术/数据中心与基础设施/网络与系统运维
功能：
1. 生成待处理文件列表（排除指定文件）
2. 进度追踪（JSON记录）
3. 20个文件分批
4. 逐文件处理模板
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(r"h:\github\cowkb\discover\newwiki2\docs")
PROGRESS_FILE = Path(r"h:\github\cowkb\skills\deep-tech-writer\scripts\opt_progress_three_dirs.json")
BATCH_SIZE = 20

EXCLUDE_FILES = {
    "index.md", "progress.md", "task_plan.md", "findings.md",
    "_filelist.txt", "_pending.txt", "_pending_files.txt", "filelist.txt",
    "error_log.json", "generation_progress.json", "README.md",
}

# 三个目标目录及对应题库和编号前缀
TARGET_DIRS = [
    {
        "name": "数据与存储技术",
        "dir": BASE_DIR / "数据与存储技术",
        "question_bank": "dst_q14_db_gz.md",
        "prefix": "dst_q",
        "category_cn": "数据与存储技术",
    },
    {
        "name": "数据中心与基础设施",
        "dir": BASE_DIR / "数据中心与基础设施",
        "question_bank": "dci_q3_ai.md",
        "prefix": "dci_q",
        "category_cn": "数据中心与基础设施",
    },
    {
        "name": "网络与系统运维",
        "dir": BASE_DIR / "网络与系统运维",
        "question_bank": "nso_q1_yw_ai.md",
        "prefix": "nso_q",
        "category_cn": "网络与系统运维",
    },
]

NOISE_KEYWORDS = [
    "低代码AI开发", "规模化落地", "范式跃迁", "Vibe Coding",
    "Agentic Engineering", "Cursor估值",
]


def collect_md_files(dir_info):
    """收集目录下的.md文件，排除指定文件和题库文件"""
    dir_path = dir_info["dir"]
    question_bank = dir_info["question_bank"]

    md_files = []
    for fpath in sorted(dir_path.glob("*.md")):
        fname = fpath.name
        if fname in EXCLUDE_FILES:
            continue
        if fname == question_bank:
            continue
        md_files.append(str(fpath))
    return md_files


def extract_q_number(filename, prefix):
    """从文件名提取Q编号，如 dst_q14_db_gz.md -> Q14"""
    m = re.search(rf"{re.escape(prefix)}(\d+)", filename, re.IGNORECASE)
    if m:
        return f"Q{m.group(1)}"
    return "Q1"


def init_progress():
    """初始化或加载进度文件"""
    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception):
            # 文件损坏，备份并重建
            import shutil
            backup = PROGRESS_FILE.with_suffix(".bak_" + datetime.now().strftime("%Y%m%d%H%M%S"))
            try:
                shutil.copy(PROGRESS_FILE, backup)
            except:
                pass
            print(f"⚠️ 进度文件损坏，已备份到 {backup.name}，将重新生成")

    all_files = []
    for dir_info in TARGET_DIRS:
        files = collect_md_files(dir_info)
        for fp in files:
            fname = os.path.basename(fp)
            q_num = extract_q_number(fname, dir_info["prefix"])
            all_files.append({
                "path": fp,
                "filename": fname,
                "dir": dir_info["name"],
                "category_cn": dir_info["category_cn"],
                "prefix": dir_info["prefix"],
                "question_bank": dir_info["question_bank"],
                "q_number": q_num,
                "status": "pending",  # pending / processing / done / skipped / error
                "batch": 0,
                "processed_at": None,
                "line_count": 0,
                "notes": "",
            })

    # 分配批次号（全局20个一批）
    for i, item in enumerate(all_files):
        item["batch"] = (i // BATCH_SIZE) + 1

    progress = {
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "total_files": len(all_files),
        "total_batches": (len(all_files) + BATCH_SIZE - 1) // BATCH_SIZE,
        "batch_size": BATCH_SIZE,
        "files": all_files,
        "stats": {
            "pending": len(all_files),
            "processing": 0,
            "done": 0,
            "skipped": 0,
            "error": 0,
        },
    }
    save_progress(progress)
    return progress


def save_progress(progress):
    """原子保存进度文件（先写临时文件再重命名，避免损坏"""
    import tempfile
    progress["updated_at"] = datetime.now().isoformat()
    pending = sum(1 for f in progress["files"] if f["status"] == "pending")
    processing = sum(1 for f in progress["files"] if f["status"] == "processing")
    done = sum(1 for f in progress["files"] if f["status"] == "done")
    skipped = sum(1 for f in progress["files"] if f["status"] == "skipped")
    error = sum(1 for f in progress["files"] if f["status"] == "error")
    progress["stats"] = {
        "pending": pending,
        "processing": processing,
        "done": done,
        "skipped": skipped,
        "error": error,
    }
    # 原子写入：写临时文件 → os.replace 原子替换
    tmp_path = PROGRESS_FILE.with_suffix(".tmp")
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
            f.flush()
            try:
                import os as _os
                _os.fsync(f.fileno())
            except:
                pass
        # 原子替换（Windows也支持os.replace）
        import os as _os
        _os.replace(tmp_path, PROGRESS_FILE)
    except Exception as e:
        # fallback：直接写入
        try:
            with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
                json.dump(progress, f, ensure_ascii=False, indent=2)
        except:
            pass


def get_batch_files(progress, batch_num):
    """获取某批次的所有文件"""
    return [f for f in progress["files"] if f["batch"] == batch_num]


def get_pending_batch(progress):
    """获取下一个待处理批次号"""
    for i in range(1, progress["total_batches"] + 1):
        batch_files = get_batch_files(progress, i)
        pending = [f for f in batch_files if f["status"] == "pending"]
        if pending:
            return i
    return None


def print_status(progress):
    """打印当前状态"""
    s = progress["stats"]
    print("=" * 70)
    print("📊 三目录批量优化进度")
    print("=" * 70)
    print(f"总文件数: {progress['total_files']}  |  总批次: {progress['total_batches']}  (每批{progress['batch_size']}个)")
    print(f"✅ 完成: {s['done']}  |  ⏳ 处理中: {s['processing']}  |  📋 待处理: {s['pending']}  |  ⏭ 跳过: {s['skipped']}  |  ❌ 错误: {s['error']}")
    pct = (s['done'] + s['skipped']) / progress['total_files'] * 100 if progress['total_files'] else 0
    print(f"进度: {pct:.1f}%")
    print()

    # 分目录统计
    for dir_info in TARGET_DIRS:
        dir_files = [f for f in progress["files"] if f["dir"] == dir_info["name"]]
        d_done = sum(1 for f in dir_files if f["status"] == "done")
        d_skip = sum(1 for f in dir_files if f["status"] == "skipped")
        d_total = len(dir_files)
        d_pct = (d_done + d_skip) / d_total * 100 if d_total else 0
        print(f"  📁 {dir_info['name']}: {d_done+d_skip}/{d_total} ({d_pct:.1f}%)")

    next_batch = get_pending_batch(progress)
    if next_batch:
        batch_files = get_batch_files(progress, next_batch)
        batch_pending = [f for f in batch_files if f["status"] == "pending"]
        print(f"\n🔜 下一批次: 第{next_batch}批 ({len(batch_pending)}个待处理)")
        for f in batch_pending[:5]:
            print(f"   - {f['filename'][:60]}")
        if len(batch_pending) > 5:
            print(f"   ... 等{len(batch_pending)}个文件")
    else:
        print("\n🎉 所有批次处理完成！")
    print("=" * 70)


def update_file_status(progress, file_path, status, notes="", save=True):
    """更新单个文件状态（save=False时不写入磁盘，由调用方统一save）"""
    for f in progress["files"]:
        if f["path"] == file_path:
            f["status"] = status
            f["processed_at"] = datetime.now().isoformat()
            if notes:
                f["notes"] = notes
            if status == "done":
                try:
                    with open(file_path, "r", encoding="utf-8") as fh:
                        f["line_count"] = len(fh.readlines())
                except:
                    pass
            break
    if save:
        save_progress(progress)


def list_batch(progress, batch_num):
    """列出某批次的文件清单"""
    batch_files = get_batch_files(progress, batch_num)
    print(f"\n📦 第{batch_num}批文件清单 ({len(batch_files)}个):")
    print("-" * 70)
    for i, f in enumerate(batch_files, 1):
        status_icon = {"pending": "📋", "processing": "⏳", "done": "✅", "skipped": "⏭", "error": "❌"}.get(f["status"], "?")
        print(f"{status_icon} {i:2d}. [{f['dir'][:4]}] {f['filename'][:65]}  {f['status']}")
    return batch_files


# ============== 辅助工具函数（供手动逐文件处理时使用） ==============

def count_lines(file_path):
    """统计文件行数"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return len(f.readlines())
    except:
        return 0


def has_summary_block(text):
    """检查是否已有概要+关键词blockquote"""
    return "> **概要**:" in text and "> **关键词**:" in text


def has_toc(text):
    """检查是否已有目录"""
    return "## 📑 目录" in text or "## 目录" in text


def has_references_section(text):
    """检查是否有参考文件章节"""
    return "## 🔗 参考文件" in text or "## 参考文件" in text or "## 参考来源" in text


def has_changelog_section(text):
    """检查是否有Changelog章节"""
    return "## Changelog" in text or "## changelog" in text or "## 更新日志" in text


def clean_noise(text):
    """清理噪声关键词所在的段落"""
    lines = text.split("\n")
    result_lines = []
    skip_until_blank = False

    for line in lines:
        stripped = line.strip()

        # 检查当前行是否包含噪声关键词
        has_noise = any(nk in stripped for nk in NOISE_KEYWORDS)

        if has_noise:
            # 跳过该行和后续连续非空行（同一段落）
            skip_until_blank = True
            continue

        if skip_until_blank:
            if stripped == "":
                skip_until_blank = False
                # 不保留多余空行（后续逻辑会处理）
                continue
            else:
                continue

        result_lines.append(line)

    return "\n".join(result_lines)


def generate_toc(text, max_depth=2):
    """根据H2/H3标题生成目录"""
    lines = text.split("\n")
    toc_entries = []
    in_frontmatter = False
    fm_count = 0

    for line in lines:
        stripped = line.strip()
        if stripped == "---":
            fm_count += 1
            if fm_count == 2:
                in_frontmatter = False
            elif fm_count == 1:
                in_frontmatter = True
            continue
        if in_frontmatter:
            continue

        if max_depth >= 2 and stripped.startswith("## ") and not stripped.startswith("### "):
            title = stripped[3:].strip()
            # 清理emoji和特殊标记
            title_clean = re.sub(r"^[🔍📑🔗📊🤖📐⚠️✅❌📁🎯💡🚀🔧🛡️📈]\s*", "", title)
            anchor = re.sub(r"[^\w\u4e00-\u9fff-]", "", title_clean.lower().replace(" ", "-"))
            toc_entries.append(f"- [{title}](#{anchor})")
        elif max_depth >= 3 and stripped.startswith("### "):
            title = stripped[4:].strip()
            title_clean = re.sub(r"^[🔍📑🔗📊🤖📐⚠️✅❌📁🎯💡🚀🔧🛡️📈]\s*", "", title)
            anchor = re.sub(r"[^\w\u4e00-\u9fff-]", "", title_clean.lower().replace(" ", "-"))
            toc_entries.append(f"  - [{title}](#{anchor})")

    if toc_entries:
        toc = "## 📑 目录\n\n" + "\n".join(toc_entries) + "\n"
        return toc
    return ""


def build_references_section(category_cn, question_bank):
    """构建参考文件章节"""
    return f"""## 🔗 参考文件

| 类型 | 文件 | 说明 |
|------|------|------|
| 📚 题库材料 | [{question_bank}](../{category_cn}/{question_bank}) | 本分类问答题库，包含原始Q/A对 |
| 📖 分类索引 | [index.md](../{category_cn}/index.md) | {category_cn}分类总目录 |
| 🏠 知识库首页 | [README.md](../README.md) | newwiki2 知识库总览 |

"""


def build_changelog_section():
    """构建Changelog三列表格（v1.0）"""
    return """## Changelog

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| v1.0 | 2026-07-29 | 🔧 全面深度优化：新增概要+关键词blockquote、📑目录（>100行）、噪声清理、🔍深度解读含量化数据、🔗参考文件章节、Changelog标准化 |

"""


def build_summary_blockq(category_cn, q_number, question_bank):
    """构建概要+关键词 blockquote 模板（占位符，后续需要大模型填充内容）"""
    # 这是模板结构，实际内容需要逐文件基于Q/A大模型总结填充
    placeholder = f"""
> **概要**: 本文档围绕{category_cn}领域Q{q_number}号问题展开深度解析，基于《{question_bank}》中的具体Q/A对进行系统化梳理与总结。内容涵盖核心概念定义、技术原理深度剖析、典型应用场景实践、关键性能指标量化对比，以及未来技术演进趋势研判。文档遵循第一性原理分析方法论，确保所有技术断言均有明确来源标注与数据支撑，为技术决策提供高质量参考依据。[来源: {category_cn}题库 {q_number}]
> **关键词**: {category_cn}·技术原理·量化分析·性能优化·最佳实践·发展趋势
"""
    return placeholder


# ============== CLI 命令 ==============

def cmd_init():
    """初始化进度"""
    progress = init_progress()
    print_status(progress)
    return progress


def cmd_status():
    """显示状态"""
    progress = init_progress()
    print_status(progress)
    return progress


def cmd_list(batch_num):
    """列出某批次"""
    progress = init_progress()
    list_batch(progress, int(batch_num))
    return progress


def cmd_next():
    """显示下一批次"""
    progress = init_progress()
    next_batch = get_pending_batch(progress)
    if next_batch:
        list_batch(progress, next_batch)
    else:
        print("✅ 所有批次已完成")
    return progress


def cmd_tools():
    """打印工具函数说明"""
    print("""
🛠️  可用辅助函数（在Python中交互使用）：
  count_lines(file_path)         - 统计文件行数
  has_summary_block(text)        - 检查是否有概要blockquote
  has_toc(text)                  - 检查是否有目录
  has_references_section(text)   - 检查是否有参考文件章节
  has_changelog_section(text)    - 检查是否有Changelog
  clean_noise(text)              - 清理噪声关键词段落
  generate_toc(text)             - 根据H2/H3生成目录
  build_references_section(cat, bank) - 生成参考文件章节
  build_changelog_section()      - 生成Changelog v1.0
  build_summary_blockq(cat, q, bank)  - 生成概要+关键词模板
  update_file_status(progress, path, status, notes) - 更新文件状态
  save_progress(progress)        - 保存进度
""")


if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    cmd = args[0] if args else "status"

    if cmd == "init":
        cmd_init()
    elif cmd == "status":
        cmd_status()
    elif cmd == "list" and len(args) > 1:
        cmd_list(args[1])
    elif cmd == "next":
        cmd_next()
    elif cmd == "tools":
        cmd_tools()
    elif cmd == "reset":
        if PROGRESS_FILE.exists():
            PROGRESS_FILE.unlink()
        print("🔄 进度已重置")
        cmd_init()
    else:
        print("""
用法: python batch_optimize_three_dirs.py <命令> [参数]
命令:
  init          初始化进度文件（首次运行）
  status        显示当前进度状态
  list <批次号>  列出指定批次的文件清单
  next          显示下一个待处理批次
  tools         打印可用辅助函数说明
  reset         删除并重建进度文件（慎用）
""")
