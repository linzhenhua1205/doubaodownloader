#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""freemind2md.py — FreeMind 思维导图 (.mm) → Markdown 转换脚本

FreeMind .mm 是纯 XML 大纲结构:
  <map><node TEXT="根">
    <node TEXT="子1"/>
    <node TEXT="子2"><node TEXT="孙"/></node>
  </node></map>

用法:
  python3 freemind2md.py <输入.mm> [输出.md]
  python3 freemind2md.py --dir <输入目录> --out <输出目录>

纯标准库 (xml.etree), 无第三方依赖。
"""
import argparse
import html
import os
import re
import xml.etree.ElementTree as ET


def _clean_text(s: str) -> str:
    """清洗节点文本: 去 HTML 标签/实体、折叠空白"""
    if not s:
        return ""
    s = re.sub(r"<[^>]+>", "", s)      # 去掉富文本标签
    s = html.unescape(s)               # &amp; → & 等
    return " ".join(s.split())


def walk(node: ET.Element, lines: list, depth: int, is_root: bool):
    text = _clean_text(node.get("TEXT", ""))
    link = node.get("LINK", "")
    indent = "  " * depth
    if is_root:
        lines.append(f"# {text}" if text else "# (无标题)")
    else:
        marker = "- "
        lines.append(f"{indent}{marker}{text}" if text else f"{indent}{marker}(无标题)")
        if link:
            lines.append(f"{indent}  🔗 {link}")
    for child in node:
        if child.tag == "node":
            walk(child, lines, depth + 1, False)


def convert_file(mm_path: str) -> str:
    tree = ET.parse(mm_path)
    root = tree.getroot()
    if root.tag != "map":
        raise ValueError(f"根标签不是 <map>, 而是 <{root.tag}>, 可能不是 FreeMind 文件")
    lines = []
    for node in root:
        if node.tag == "node":
            walk(node, lines, 0, True)
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="FreeMind .mm → Markdown 转换")
    ap.add_argument("input", nargs="?", help="输入 .mm 文件")
    ap.add_argument("output", nargs="?", help="输出 .md 文件 (默认同名)")
    ap.add_argument("--dir", help="批量转换: 输入目录")
    ap.add_argument("--out", help="批量转换: 输出目录 (默认 input/../freemind-md)")
    args = ap.parse_args()

    if args.dir:
        out_dir = args.out or os.path.join(os.path.dirname(os.path.abspath(args.dir)), "freemind-md")
        os.makedirs(out_dir, exist_ok=True)
        files = sorted(f for f in os.listdir(args.dir) if f.lower().endswith(".mm"))
        if not files:
            print(f"⚠️ {args.dir} 下没有 .mm 文件")
            return
        ok, fail = 0, []
        for f in files:
            src = os.path.join(args.dir, f)
            dst = os.path.join(out_dir, os.path.splitext(f)[0] + ".md")
            try:
                md = convert_file(src)
                with open(dst, "w", encoding="utf-8") as fp:
                    fp.write(md)
                ok += 1
                print(f"✅ {f} → {os.path.basename(dst)}")
            except Exception as e:
                fail.append((f, str(e)))
                print(f"❌ {f}: {e}")
        print(f"\n完成: 成功 {ok}/{len(files)}" + (f", 失败 {len(fail)}: {fail}" if fail else ""))
        return

    if not args.input:
        ap.print_help()
        return

    md = convert_file(args.input)
    dst = args.output or os.path.splitext(args.input)[0] + ".md"
    with open(dst, "w", encoding="utf-8") as fp:
        fp.write(md)
    print(f"✅ {args.input} → {dst} ({len(md)} chars)")


if __name__ == "__main__":
    main()
