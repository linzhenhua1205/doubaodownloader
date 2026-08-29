#!/usr/bin/env python3
"""
文档批量转换工具 — 将 PDF/DOC/DOCX/HTML 转换为 Markdown
保持原有目录结构，支持递归遍历。

用法:
  python convert-to-markdown.py --input <源目录> [--output <输出目录>] [--dry-run]

依赖:
  pip install markitdown pymupdf4llm mammoth markdownify beautifulsoup4

  # 或按需安装:
  pip install markitdown          # 全格式主转换器 (Microsoft)
  pip install pymupdf4llm         # PDF 高质量转换 (备选)
  pip install mammoth             # DOCX 转换 (备选)
  pip install markdownify         # HTML 转换 (备选)
"""

import argparse
import sys
import os
import shutil
import traceback
from pathlib import Path

# 支持的文件扩展名
SUPPORTED_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.html', '.htm', '.pptx', '.xlsx'
}

# 转换结果统计
stats = {
    'total': 0,
    'success': 0,
    'failed': 0,
    'skipped': 0,
    'errors': []
}


def check_dependencies():
    """检查可用的转换库，返回可用的转换器字典"""
    converters = {}

    try:
        from markitdown import MarkItDown
        converters['markitdown'] = MarkItDown()
        print("[OK] markitdown 可用 (全格式主转换器)")
    except ImportError:
        print("[--] markitdown 未安装 (pip install markitdown)")

    try:
        import pymupdf4llm
        converters['pymupdf4llm'] = pymupdf4llm
        print("[OK] pymupdf4llm 可用 (PDF 高质量转换)")
    except ImportError:
        print("[--] pymupdf4llm 未安装 (pip install pymupdf4llm)")

    try:
        import mammoth
        converters['mammoth'] = mammoth
        print("[OK] mammoth 可用 (DOCX 转换)")
    except ImportError:
        print("[--] mammoth 未安装 (pip install mammoth)")

    try:
        from markdownify import markdownify as md_convert
        converters['markdownify'] = md_convert
        print("[OK] markdownify 可用 (HTML 转换)")
    except ImportError:
        print("[--] markdownify 未安装 (pip install markdownify)")

    if not converters:
        print("\n[ERROR] 没有可用的转换库，请至少安装一个:")
        print("  pip install markitdown  # 推荐，全格式支持")
        sys.exit(1)

    return converters


def convert_with_markitdown(md, file_path):
    """使用 markitdown 转换"""
    result = md.convert(str(file_path))
    return result.text_content


def convert_pdf(file_path, converters):
    """转换 PDF 文件"""
    # 优先使用 pymupdf4llm (质量更高)
    if 'pymupdf4llm' in converters:
        try:
            return converters['pymupdf4llm'].to_markdown(str(file_path))
        except Exception:
            pass  # 回退到 markitdown

    if 'markitdown' in converters:
        return convert_with_markitdown(converters['markitdown'], file_path)

    raise RuntimeError("无可用的 PDF 转换器")


def convert_docx(file_path, converters):
    """转换 DOCX 文件"""
    # 优先使用 mammoth (对 docx 支持更好)
    if 'mammoth' in converters:
        try:
            with open(file_path, 'rb') as f:
                result = converters['mammoth'].convert_to_markdown(f)
                return result.value
        except Exception:
            pass  # 回退到 markitdown

    if 'markitdown' in converters:
        return convert_with_markitdown(converters['markitdown'], file_path)

    raise RuntimeError("无可用的 DOCX 转换器")


def convert_html(file_path, converters):
    """转换 HTML 文件"""
    # 优先使用 markdownify
    if 'markdownify' in converters:
        try:
            from bs4 import BeautifulSoup
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                html = f.read()
            soup = BeautifulSoup(html, 'html.parser')
            # 移除 script 和 style 标签
            for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
                tag.decompose()
            return converters['markdownify'](str(soup), heading_style='ATX')
        except ImportError:
            # markdownify 已导入但 bs4 未安装，直接转换
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                html = f.read()
            return converters['markdownify'](html, heading_style='ATX')
        except Exception:
            pass  # 回退到 markitdown

    if 'markitdown' in converters:
        return convert_with_markitdown(converters['markitdown'], file_path)

    raise RuntimeError("无可用的 HTML 转换器")


def convert_doc(file_path, converters):
    """转换旧版 DOC 文件 (需要 markitdown 或 libreoffice)"""
    if 'markitdown' in converters:
        try:
            return convert_with_markitdown(converters['markitdown'], file_path)
        except Exception:
            pass

    # 尝试 libreoffice 转换
    try:
        import subprocess
        tmp_dir = file_path.parent / '.tmp_convert'
        tmp_dir.mkdir(exist_ok=True)
        subprocess.run(
            ['libreoffice', '--headless', '--convert-to', 'docx',
             '--outdir', str(tmp_dir), str(file_path)],
            capture_output=True, timeout=60
        )
        docx_path = tmp_dir / (file_path.stem + '.docx')
        if docx_path.exists():
            content = convert_docx(docx_path, converters)
            shutil.rmtree(tmp_dir)
            return content
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    raise RuntimeError("旧版 .doc 文件需要 libreoffice 或 markitdown 支持")


def convert_file(file_path, converters):
    """根据文件类型选择转换器"""
    ext = file_path.suffix.lower()

    if ext == '.pdf':
        return convert_pdf(file_path, converters)
    elif ext == '.docx':
        return convert_docx(file_path, converters)
    elif ext == '.doc':
        return convert_doc(file_path, converters)
    elif ext in ('.html', '.htm'):
        return convert_html(file_path, converters)
    elif ext in ('.pptx', '.xlsx'):
        if 'markitdown' in converters:
            return convert_with_markitdown(converters['markitdown'], file_path)
        raise RuntimeError(f"{ext} 需要 markitdown 支持")
    else:
        raise RuntimeError(f"不支持的文件类型: {ext}")


def process_directory(input_dir, output_dir, converters, dry_run=False):
    """递归遍历目录并转换所有支持的文件"""
    input_path = Path(input_dir).resolve()
    output_path = Path(output_dir).resolve()

    if not input_path.exists():
        print(f"[ERROR] 输入目录不存在: {input_path}")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"  输入目录: {input_path}")
    print(f"  输出目录: {output_path}")
    print(f"  模式: {'预览 (dry-run)' if dry_run else '转换'}")
    print(f"{'='*60}\n")

    # 收集所有待转换文件
    files_to_convert = []
    for root, dirs, files in os.walk(input_path):
        for f in files:
            file_path = Path(root) / f
            if file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                files_to_convert.append(file_path)

    stats['total'] = len(files_to_convert)
    print(f"发现 {stats['total']} 个待转换文件\n")

    if dry_run:
        print("[预览模式] 以下文件将被转换:\n")
        for fp in files_to_convert:
            rel = fp.relative_to(input_path)
            out_file = output_path / rel.with_suffix('.md')
            print(f"  {rel}  →  {out_file}")
        print(f"\n共 {stats['total']} 个文件")
        return

    # 逐个转换
    for i, file_path in enumerate(files_to_convert, 1):
        rel_path = file_path.relative_to(input_path)
        # 保持目录结构，仅改变扩展名
        out_file = output_path / rel_path.with_suffix('.md')
        out_file.parent.mkdir(parents=True, exist_ok=True)

        # 如果输出文件已存在且比源文件新，跳过
        if out_file.exists():
            src_mtime = file_path.stat().st_mtime
            dst_mtime = out_file.stat().st_mtime
            if dst_mtime > src_mtime:
                stats['skipped'] += 1
                print(f"[{i}/{stats['total']}] SKIP  {rel_path} (已是最新)")
                continue

        print(f"[{i}/{stats['total']}] CONV  {rel_path} ...", end=' ', flush=True)

        try:
            content = convert_file(file_path, converters)
            if content and content.strip():
                with open(out_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                stats['success'] += 1
                print(f"OK ({len(content)} chars)")
            else:
                stats['failed'] += 1
                stats['errors'].append(f"{rel_path}: 转换内容为空")
                print("FAILED (空内容)")
        except Exception as e:
            stats['failed'] += 1
            error_msg = f"{rel_path}: {type(e).__name__}: {e}"
            stats['errors'].append(error_msg)
            print(f"FAILED ({e})")

    # 打印统计
    print(f"\n{'='*60}")
    print(f"  转换完成")
    print(f"  总计: {stats['total']}")
    print(f"  成功: {stats['success']}")
    print(f"  跳过: {stats['skipped']}")
    print(f"  失败: {stats['failed']}")
    print(f"{'='*60}")

    if stats['errors']:
        print(f"\n失败详情:")
        for err in stats['errors']:
            print(f"  - {err}")


def main():
    parser = argparse.ArgumentParser(
        description='批量转换 PDF/DOC/DOCX/HTML 为 Markdown，保持目录结构',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python convert-to-markdown.py --input ./docs
  python convert-to-markdown.py --input ./docs --output ./markdown
  python convert-to-markdown.py --input ./docs --dry-run

支持的格式: PDF, DOC, DOCX, HTML, HTM, PPTX, XLSX
        """
    )
    parser.add_argument(
        '--input', '-i', required=True,
        help='输入目录（递归遍历）'
    )
    parser.add_argument(
        '--output', '-o', default=None,
        help='输出目录（默认在输入目录旁创建 _markdown/）'
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help='仅预览，不实际转换'
    )
    args = parser.parse_args()

    # 确定输出目录
    input_dir = Path(args.input).resolve()
    if args.output:
        output_dir = Path(args.output).resolve()
    else:
        output_dir = input_dir.parent / f"{input_dir.name}_markdown"

    # 检查依赖
    print("检查转换库...")
    converters = check_dependencies()

    # 执行转换
    process_directory(input_dir, output_dir, converters, args.dry_run)


if __name__ == '__main__':
    main()
