#!/usr/bin/env python3
"""
rotate_pdf.py — PDF 页面旋转工具（skill-creator 建议落地）

用途: 处理扫描件/竖版图混排 PDF 的页面旋转（0/90/180/270）。
替代文档中"设计承诺"的 rotate_pdf 脚本，提供确定性实现。

用法:
  python3 scripts/tools/rotate_pdf.py <file.pdf> --angle 90 [--pages 1,3-5] [--output out.pdf]
  python3 scripts/tools/rotate_pdf.py <file.pdf> --angle 180 --all        # 全部页面
  python3 scripts/tools/rotate_pdf.py <file.pdf> --inspect                # 仅查看页数

依赖: pypdf (pip install pypdf) — 纯 Python，无系统依赖
"""

import argparse
import sys
from pathlib import Path


def inspect_pdf(path: Path):
    try:
        from pypdf import PdfReader
    except ImportError:
        print("❌ 需要 pypdf: pip install pypdf")
        sys.exit(1)
    reader = PdfReader(str(path))
    print(f"📄 {path.name}: {len(reader.pages)} 页")
    for i, page in enumerate(reader.pages, 1):
        r = page.rotation if hasattr(page, "rotation") else 0
        print(f"  p{i}: rotation={r}°")


def rotate_pdf(path: Path, angle: int, pages: str = None, output: Path = None):
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        print("❌ 需要 pypdf: pip install pypdf")
        sys.exit(1)

    if angle not in (0, 90, 180, 270):
        print(f"❌ 角度必须是 0/90/180/270，收到: {angle}")
        sys.exit(1)

    reader = PdfReader(str(path))
    total = len(reader.pages)
    writer = PdfWriter()

    # 解析页面选择
    target = set()
    if pages is None or pages.strip() == "":
        target = set(range(total))
    else:
        for part in pages.split(","):
            part = part.strip()
            if "-" in part:
                a, b = part.split("-", 1)
                target.update(range(int(a) - 1, int(b)))
            else:
                target.add(int(part) - 1)

    for i in range(total):
        page = reader.pages[i]
        if i in target:
            page.rotate(angle)
        writer.add_page(page)

    out = output or path.with_name(f"{path.stem}_rot{angle}{path.suffix}")
    with open(out, "wb") as f:
        writer.write(f)
    print(f"✅ 已旋转 {len(target)} 页 (angle={angle}°) → {out}")


def main():
    parser = argparse.ArgumentParser(description="PDF 页面旋转工具")
    parser.add_argument("file", help="PDF 文件路径")
    parser.add_argument("--angle", type=int, choices=[0, 90, 180, 270], default=90)
    parser.add_argument("--pages", help="页面选择，如 '1,3-5'（默认全部）")
    parser.add_argument("--output", "-o", help="输出文件（默认 <原名>_rot<angle>.pdf）")
    parser.add_argument("--inspect", action="store_true", help="仅查看页数与旋转信息")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"❌ 文件不存在: {path}")
        sys.exit(1)

    if args.inspect:
        inspect_pdf(path)
    else:
        rotate_pdf(path, args.angle, args.pages, Path(args.output) if args.output else None)


if __name__ == "__main__":
    main()
