#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
import 目录去重脚本

功能：
  1. 以 import/ 下各子目录为单位进行去重（跨目录不处理）
  2. 重复文件移动到 import/dup/，保留原始目录结构信息
  3. 支持的重复模式：
     a. 文件大小相同 + 文件名差异为 (1)/(2)/(3) 或 _数字串
     b. 文件大小不同 + 文件名差异同上 → diff 比较内容包含关系
  4. 所有路径使用相对路径
  5. 提供可选命令参数进行深度去重
  6. 生成移动报告

用法:
  python scripts/dedup_import.py                    # 基础去重（dry-run）
  python scripts/dedup_import.py --execute          # 执行移动
  python scripts/dedup_import.py --execute --deep   # 深度去重（含内容hash）
  python scripts/dedup_import.py --execute --deep --hash-only  # 仅用hash去重
  python scripts/dedup_import.py --report-only      # 仅生成报告不移动
"""

import os
import re
import sys
import hashlib
import argparse
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# ============================================================
# 常量
# ============================================================

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
IMPORT_DIR = PROJECT_ROOT / "import"
DUP_DIR = IMPORT_DIR / "dup"
REPORT_FILE = IMPORT_DIR / "dup" / "dedup_report.md"

# 需要去重的子目录（dup 本身排除）
SKIP_DIRS = {"dup"}

# 文本文件扩展名（可做内容比较）
TEXT_EXTENSIONS = {".md", ".txt", ".html", ".htm", ".json", ".csv"}


# ============================================================
# 文件名模式解析
# ============================================================

# 匹配 (1), (2) 等括号数字模式（有扩展名）
PAREN_PATTERN = re.compile(r'^(.+?)\s*\((\d+)\)(\.[^.]+)$')
# 匹配 (1), (2) 等括号数字模式（无扩展名）
PAREN_NOEXT_PATTERN = re.compile(r'^(.+?)\s*\((\d+)\)$')
# 匹配 _123456 下划线数字模式（有扩展名）
UNDERSCORE_NUM_PATTERN = re.compile(r'^(.+?)(_\d+)(\.[^.]+)$')
# 匹配 _123456 下划线数字模式（无扩展名）
UNDERSCORE_NUM_NOEXT_PATTERN = re.compile(r'^(.+?)(_\d+)$')


def parse_filename(filename):
    """
    解析文件名，返回 (base_name, suffix_type, suffix_value, extension)

    suffix_type:
      - "none": 无重复后缀（原始文件）
      - "paren": (1), (2) 等括号数字模式
      - "underscore": _123456 等下划线数字模式
    """
    # 括号数字模式（有扩展名）
    m = PAREN_PATTERN.match(filename)
    if m:
        return m.group(1).strip(), "paren", m.group(2), m.group(3)

    # 括号数字模式（无扩展名）
    m = PAREN_NOEXT_PATTERN.match(filename)
    if m:
        return m.group(1).strip(), "paren", m.group(2), ""

    # 下划线数字模式（有扩展名）
    m = UNDERSCORE_NUM_PATTERN.match(filename)
    if m:
        return m.group(1).strip(), "underscore", m.group(2).strip("_"), m.group(3)

    # 下划线数字模式（无扩展名）
    m = UNDERSCORE_NUM_NOEXT_PATTERN.match(filename)
    if m:
        return m.group(1).strip(), "underscore", m.group(2).strip("_"), ""

    # 无后缀
    ext_match = re.match(r'^(.+)(\.[^.]+)$', filename)
    if ext_match:
        return ext_match.group(1), "none", "", ext_match.group(2)
    return filename, "none", "", ""


def get_base_key(filename):
    """获取文件名的 base key，用于分组匹配。返回 None 表示原始文件。"""
    base, suffix_type, suffix_val, ext = parse_filename(filename)
    if suffix_type == "none":
        return None
    return (base, ext)


# ============================================================
# 文件信息
# ============================================================

class FileInfo:
    def __init__(self, filepath, subdir):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.subdir = subdir
        self.size = os.path.getsize(filepath)
        self.base, self.suffix_type, self.suffix_val, self.ext = parse_filename(self.filename)
        self.content_hash = None
        self._content = None

    @property
    def abs_path(self):
        return PROJECT_ROOT / self.filepath

    def read_content(self):
        if self._content is None:
            try:
                with open(self.abs_path, 'r', encoding='utf-8', errors='replace') as f:
                    self._content = f.read()
            except Exception:
                self._content = ""
        return self._content

    def get_hash(self):
        if self.content_hash is None:
            h = hashlib.md5()
            with open(self.abs_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    h.update(chunk)
            self.content_hash = h.hexdigest()
        return self.content_hash


def scan_subdir(subdir_path, subdir_name):
    """扫描子目录，收集所有文件信息"""
    files = []
    if not subdir_path.exists():
        return files

    for root, dirs, filenames in os.walk(subdir_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fname in filenames:
            fpath = os.path.join(root, fname)
            rel_path = os.path.relpath(fpath, PROJECT_ROOT)
            try:
                fi = FileInfo(rel_path, subdir_name)
                files.append(fi)
            except OSError:
                continue
    return files


# ============================================================
# 内容包含检查
# ============================================================

def is_content_contained(fi_a, fi_b):
    """
    检查 a 的内容是否被 b 完全包含。
    使用严格规则：a 的去除空白后的全文必须是 b 的子串。
    """
    content_a = fi_a.read_content()
    content_b = fi_b.read_content()

    if not content_a or not content_b:
        return False
    if len(content_a) > len(content_b):
        return False

    a_stripped = content_a.strip()
    b_stripped = content_b.strip()

    if not a_stripped:
        return False

    # 严格规则：a 的全文是 b 的子串
    if a_stripped in b_stripped:
        return True

    # 放宽规则：去除所有空白后比较
    a_no_ws = re.sub(r'\s+', '', content_a)
    b_no_ws = re.sub(r'\s+', '', content_b)

    if len(a_no_ws) > len(b_no_ws):
        return False
    if len(a_no_ws) < 10:  # 太短不处理
        return False

    if a_no_ws in b_no_ws:
        return True

    return False


# ============================================================
# 去重器
# ============================================================

class Deduplicator:
    def __init__(self, execute=False, deep=False, hash_only=False):
        self.execute = execute
        self.deep = deep
        self.hash_only = hash_only
        self.moves = []        # [(src, dst, reason)]
        self.moved_set = set()  # 已标记移动的文件路径集合，防止重复标记

    def is_already_moved(self, fi):
        return fi.filepath in self.moved_set

    def move_to_dup(self, fi, reason):
        """将文件移动到 dup 目录"""
        if self.is_already_moved(fi):
            return False

        src = fi.abs_path
        if not src.exists():
            return False

        # dup 下的路径: import/dup/<subdir>/<filename>
        dst = DUP_DIR / fi.subdir / fi.filename

        # 处理目标已存在
        counter = 1
        while dst.exists():
            stem = dst.stem
            ext = dst.suffix
            dst = DUP_DIR / fi.subdir / f"{stem}_conflict{counter}{ext}"
            counter += 1

        if self.execute:
            dst.parent.mkdir(parents=True, exist_ok=True)
            import shutil
            shutil.move(str(src), str(dst))

        self.moves.append((fi.filepath, str(dst.relative_to(PROJECT_ROOT)), reason))
        self.moved_set.add(fi.filepath)
        return True

    # --------------------------------------------------------
    # 策略1: 同大小 + 文件名模式匹配
    # --------------------------------------------------------
    def dedup_same_size(self, files):
        """
        处理文件大小相同的重复：
        - 括号模式 (1)(2)(3)：有原始文件则保留原始，否则保留编号最小
        - 下划线模式 _123456：有原始文件则保留原始，否则保留数字最大
        """
        # 按 base key 分组
        groups = defaultdict(list)   # (base, ext) -> [FileInfo]
        originals = {}               # (base, ext) -> FileInfo

        for fi in files:
            if self.is_already_moved(fi):
                continue
            key = get_base_key(fi.filename)
            if key is None:
                btuple = (fi.base, fi.ext)
                if btuple not in originals:
                    originals[btuple] = fi
            else:
                groups[key].append(fi)

        for key, group in groups.items():
            base_name, ext = key
            original = originals.get(key)

            paren_files = [fi for fi in group if fi.suffix_type == "paren"
                          and not self.is_already_moved(fi)]
            underscore_files = [fi for fi in group if fi.suffix_type == "underscore"
                               and not self.is_already_moved(fi)]

            # --- 括号模式 (1)(2)(3) ---
            if paren_files:
                size_groups = defaultdict(list)
                for fi in paren_files:
                    size_groups[fi.size].append(fi)

                for size, same_size in size_groups.items():
                    if original and original.size == size:
                        # 原始文件大小相同 → 移动所有带括号副本
                        for fi in same_size:
                            self.move_to_dup(fi,
                                f"大小相同({size}B)，与原始文件 {original.filename} 重复")
                    elif len(same_size) > 1 and not original:
                        # 无原始文件 → 保留编号最小
                        same_size.sort(key=lambda x: int(x.suffix_val))
                        for fi in same_size[1:]:
                            self.move_to_dup(fi,
                                f"大小相同({size}B)，与 {same_size[0].filename} 重复")

            # --- 下划线模式 _123456 ---
            if underscore_files:
                size_groups = defaultdict(list)
                for fi in underscore_files:
                    size_groups[fi.size].append(fi)

                for size, same_size in size_groups.items():
                    if original and original.size == size:
                        # 原始文件大小相同 → 移动所有带下划线副本
                        for fi in same_size:
                            self.move_to_dup(fi,
                                f"大小相同({size}B)，与原始文件 {original.filename} 重复")
                    elif len(same_size) > 1 and not original:
                        # 无原始文件 → 保留数字最大
                        same_size.sort(key=lambda x: int(x.suffix_val), reverse=True)
                        for fi in same_size[1:]:
                            self.move_to_dup(fi,
                                f"大小相同({size}B)，与 {same_size[0].filename} 重复，保留数字最大版本")

    # --------------------------------------------------------
    # 策略2: 不同大小 + 内容包含检查
    # --------------------------------------------------------
    def dedup_diff_size(self, files):
        """
        处理文件大小不同但文件名相似的重复：
        diff 比较内容包含关系，移动被包含的文件
        """
        groups = defaultdict(list)
        originals = {}

        for fi in files:
            if self.is_already_moved(fi):
                continue
            key = get_base_key(fi.filename)
            if key is None:
                if key not in originals:
                    originals[key] = fi
            else:
                groups[key].append(fi)

        for key, group in groups.items():
            base_name, ext = key
            original = originals.get(key)

            paren_files = [fi for fi in group if fi.suffix_type == "paren"
                          and not self.is_already_moved(fi)]
            underscore_files = [fi for fi in group if fi.suffix_type == "underscore"
                               and not self.is_already_moved(fi)]

            # 只对文本文件做内容比较
            paren_text = [fi for fi in paren_files if fi.ext in TEXT_EXTENSIONS]
            under_text = [fi for fi in underscore_files if fi.ext in TEXT_EXTENSIONS]

            # --- 括号模式 vs 原始文件 ---
            if original and original.ext in TEXT_EXTENSIONS:
                for fi in paren_text:
                    if self.is_already_moved(fi):
                        continue
                    if is_content_contained(fi, original):
                        self.move_to_dup(fi,
                            f"内容被原始文件 {original.filename} 完全包含")
                    elif is_content_contained(original, fi):
                        # 原始文件被副本包含 → 移动原始文件
                        self.move_to_dup(original,
                            f"内容被 {fi.filename} 完全包含（原始文件较短）")

            # --- 括号模式副本之间 ---
            if len(paren_text) >= 2:
                self._compare_pairwise(paren_text)

            # --- 下划线模式 vs 原始文件 ---
            if original and original.ext in TEXT_EXTENSIONS:
                for fi in under_text:
                    if self.is_already_moved(fi):
                        continue
                    if is_content_contained(fi, original):
                        self.move_to_dup(fi,
                            f"内容被原始文件 {original.filename} 完全包含")
                    elif is_content_contained(original, fi):
                        self.move_to_dup(original,
                            f"内容被 {fi.filename} 完全包含（原始文件较短）")

            # --- 下划线模式副本之间（保留数字最大的） ---
            if len(under_text) >= 2:
                under_text.sort(key=lambda x: int(x.suffix_val), reverse=True)
                self._compare_pairwise(under_text)

    def _compare_pairwise(self, file_list):
        """两两比较内容包含关系"""
        active = [fi for fi in file_list if not self.is_already_moved(fi)]
        if len(active) < 2:
            return

        for i in range(len(active)):
            if self.is_already_moved(active[i]):
                continue
            for j in range(i + 1, len(active)):
                if self.is_already_moved(active[i]) or self.is_already_moved(active[j]):
                    continue

                a, b = active[i], active[j]
                a_in_b = is_content_contained(a, b)
                b_in_a = is_content_contained(b, a)

                if a_in_b and not b_in_a:
                    self.move_to_dup(a, f"内容被 {b.filename} 完全包含")
                elif b_in_a and not a_in_b:
                    self.move_to_dup(b, f"内容被 {a.filename} 完全包含")
                elif a_in_b and b_in_a:
                    # 双向包含 → 内容实质相同，保留文件名较短的
                    if len(a.filename) <= len(b.filename):
                        self.move_to_dup(b, f"内容与 {a.filename} 双向包含，保留较短文件名")
                    else:
                        self.move_to_dup(a, f"内容与 {b.filename} 双向包含，保留较短文件名")

    # --------------------------------------------------------
    # 策略3 (深度): 内容 hash 完全相同
    # --------------------------------------------------------
    def dedup_by_hash(self, files):
        """通过内容 hash 检测完全相同的文件"""
        hash_groups = defaultdict(list)
        for fi in files:
            if self.is_already_moved(fi):
                continue
            try:
                h = fi.get_hash()
                hash_groups[h].append(fi)
            except Exception:
                continue

        for h, group in hash_groups.items():
            if len(group) < 2:
                continue
            # 保留文件名最短的
            group.sort(key=lambda x: len(x.filename))
            keep = group[0]
            for fi in group[1:]:
                if not self.is_already_moved(fi):
                    self.move_to_dup(fi,
                        f"内容hash完全相同({h[:8]})，与 {keep.filename} 重复")

    # --------------------------------------------------------
    # 策略4 (深度): 模糊文件名匹配
    # --------------------------------------------------------
    def dedup_fuzzy_name(self, files):
        """
        模糊文件名匹配去重：
        - 文件名去除空格/特殊字符/大小写后相同
        """
        if not self.deep:
            return

        norm_groups = defaultdict(list)
        for fi in files:
            if self.is_already_moved(fi):
                continue
            norm_name = re.sub(r'[\s\-_\(\)（）]', '', fi.filename.lower())
            norm_name = re.sub(r'\.\w+$', '', norm_name)
            if norm_name and len(norm_name) > 3:
                norm_groups[norm_name].append(fi)

        for norm, group in norm_groups.items():
            if len(group) < 2:
                continue
            group.sort(key=lambda x: x.size, reverse=True)
            keep = group[0]
            for fi in group[1:]:
                if self.is_already_moved(fi):
                    continue
                if fi.ext in TEXT_EXTENSIONS:
                    if is_content_contained(fi, keep):
                        self.move_to_dup(fi,
                            f"模糊文件名匹配，内容被 {keep.filename} 包含")
                    elif fi.size == keep.size:
                        self.move_to_dup(fi,
                            f"模糊文件名匹配，大小相同({fi.size}B)，与 {keep.filename} 重复")
                elif fi.size == keep.size:
                    self.move_to_dup(fi,
                        f"模糊文件名匹配，大小相同({fi.size}B)，与 {keep.filename} 重复")

    # --------------------------------------------------------
    # 主流程
    # --------------------------------------------------------
    def run(self):
        """执行去重主流程"""
        print("=" * 70)
        mode = "执行" if self.execute else "预览(dry-run)"
        print(f"  import 目录去重工具 - {mode}")
        if self.deep:
            print(f"  深度模式: 开启")
        if self.hash_only:
            print(f"  Hash去重模式: 开启")
        print("=" * 70)

        subdirs = []
        for item in sorted(IMPORT_DIR.iterdir()):
            if item.is_dir() and item.name not in SKIP_DIRS:
                subdirs.append(item)

        for subdir_path in subdirs:
            subdir_name = subdir_path.name
            files = scan_subdir(subdir_path, subdir_name)

            if not files:
                continue

            before_count = len(self.moves)
            print(f"\n[*] {subdir_name}/ ({len(files)} 文件)")

            if self.hash_only:
                print(f"    [hash] 内容hash去重...")
                self.dedup_by_hash(files)
            else:
                print(f"    [1] 同大小重复检查...")
                self.dedup_same_size(files)
                print(f"        -> {len(self.moves) - before_count} 个")

                step2_base = len(self.moves)
                print(f"    [2] 内容包含检查...")
                self.dedup_diff_size(files)
                print(f"        -> {len(self.moves) - step2_base} 个")

                if self.deep:
                    step3_base = len(self.moves)
                    print(f"    [3] 内容hash去重...")
                    self.dedup_by_hash(files)
                    print(f"        -> {len(self.moves) - step3_base} 个")

                    step4_base = len(self.moves)
                    print(f"    [4] 模糊文件名匹配...")
                    self.dedup_fuzzy_name(files)
                    print(f"        -> {len(self.moves) - step4_base} 个")

            total = len(self.moves) - before_count
            print(f"    合计移动: {total} 个")

        self.generate_report()

        print(f"\n{'=' * 70}")
        print(f"  去重完成 | 总移动: {len(self.moves)} 个 | 模式: {mode}")
        print(f"  报告: {REPORT_FILE.relative_to(PROJECT_ROOT)}")
        print(f"{'=' * 70}")

        return self.moves

    # --------------------------------------------------------
    # 报告
    # --------------------------------------------------------
    def generate_report(self):
        DUP_DIR.mkdir(parents=True, exist_ok=True)

        lines = []
        lines.append(f"# import 目录去重报告\n")
        lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**执行模式**: {'实际移动' if self.execute else '预览(dry-run)'}")
        lines.append(f"**深度模式**: {'开启' if self.deep else '关闭'}")
        lines.append(f"**总移动文件数**: {len(self.moves)}\n")

        # 按子目录统计
        subdir_stats = defaultdict(int)
        for src, dst, reason in self.moves:
            parts = src.replace("\\", "/").split("/")
            subdir = parts[1] if len(parts) > 1 else "unknown"
            subdir_stats[subdir] += 1

        lines.append("## 统计摘要\n")
        lines.append("| 子目录 | 移动文件数 |")
        lines.append("|--------|-----------|")
        for subdir, count in sorted(subdir_stats.items()):
            lines.append(f"| {subdir}/ | {count} |")
        lines.append(f"| **合计** | **{len(self.moves)}** |\n")

        # 重复模式分析
        lines.append("## 重复模式分析\n")
        same_size_count = sum(1 for _, _, r in self.moves if "大小相同" in r)
        containment_count = sum(1 for _, _, r in self.moves if "完全包含" in r)
        hash_count = sum(1 for _, _, r in self.moves if "hash" in r.lower())
        fuzzy_count = sum(1 for _, _, r in self.moves if "模糊" in r)
        bidirectional_count = sum(1 for _, _, r in self.moves if "双向包含" in r)

        lines.append(f"- 同大小+文件名模式匹配: {same_size_count} 个")
        lines.append(f"- 内容完全包含: {containment_count} 个")
        lines.append(f"  - 其中双向包含: {bidirectional_count} 个")
        lines.append(f"- 内容hash相同: {hash_count} 个")
        lines.append(f"- 模糊文件名匹配: {fuzzy_count} 个\n")

        # 移动明细
        lines.append("## 移动明细\n")
        lines.append("| # | 源文件 | 目标位置 | 原因 |")
        lines.append("|---|--------|---------|------|")
        for i, (src, dst, reason) in enumerate(self.moves, 1):
            lines.append(f"| {i} | `{src}` | `{dst}` | {reason} |")
        lines.append("")

        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))


# ============================================================
# 主入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description='import 目录去重工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python scripts/dedup_import.py                     # 预览模式（dry-run）
  python scripts/dedup_import.py --execute           # 执行去重
  python scripts/dedup_import.py --execute --deep    # 深度去重（含hash+模糊匹配）
  python scripts/dedup_import.py --execute --hash-only  # 仅hash去重
  python scripts/dedup_import.py --report-only       # 仅生成报告
        """
    )
    parser.add_argument('--execute', action='store_true',
                        help='实际执行移动操作（默认为 dry-run 预览）')
    parser.add_argument('--deep', action='store_true',
                        help='开启深度去重（内容hash + 模糊文件名匹配）')
    parser.add_argument('--hash-only', action='store_true',
                        help='仅使用内容hash去重（跳过文件名模式匹配）')
    parser.add_argument('--report-only', action='store_true',
                        help='仅生成报告，不执行任何操作')

    args = parser.parse_args()

    if args.report_only:
        dedup = Deduplicator(execute=False, deep=args.deep, hash_only=args.hash_only)
        dedup.run()
        return

    dedup = Deduplicator(
        execute=args.execute,
        deep=args.deep,
        hash_only=args.hash_only
    )
    dedup.run()


if __name__ == '__main__':
    main()
