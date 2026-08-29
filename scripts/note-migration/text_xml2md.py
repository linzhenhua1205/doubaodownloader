#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""text_xml2md.py — 通用文本 XML → Markdown 转换 (需按实际结构配置)

因为"文本 XML"的具体结构未知, 本脚本分两步:
  1. --inspect <file>    查看 XML 结构 (打印前几层标签), 用于确定配置
  2. --config <cfg.json> <file|dir>  按配置转换

配置格式 (cfg.json):
{
  "item_xpath": "//article",          # 每条记录的定位 (XPath)
  "title": "./title",                 # 标题 (相对 item 的 XPath 或字符串常量)
  "body": ["./content", "./body"],    # 正文 (多个元素按序拼接)
  "list": ["./item"],                 # 列表元素 (转 Markdown 列表)
  "attrs_as_meta": ["date", "author"] # 属性写入 frontmatter
}

用法:
  python3 text_xml2md.py --inspect data.xml
  python3 text_xml2md.py --config cfg.json data.xml out/
  python3 text_xml2md.py --config cfg.json --dir input_dir --out out/

纯标准库, 无第三方依赖。
"""
import argparse
import json
import os
import sys
import xml.etree.ElementTree as ET


def _localname(tag: str) -> str:
    return tag.split("}")[-1]


def _text_of(elem: ET.Element) -> str:
    """取元素全部文本 (含子元素文本, 折叠空白)"""
    if elem is None:
        return ""
    parts = [elem.text or ""]
    for child in elem.iter():
        if child is not elem:
            parts.append(child.text or "")
            parts.append(child.tail or "")
    return " ".join("".join(parts).split())


def inspect_file(path: str, max_depth: int = 4, max_children: int = 8):
    """打印 XML 结构树 (前几层), 帮助确定配置"""
    tree = ET.parse(path)
    root = tree.getroot()

    def walk(elem, depth):
        if depth > max_depth:
            return
        attrs = " ".join(f'{k}="{v}"' for k, v in list(elem.attrib.items())[:4])
        print(f"{'  ' * depth}<{_localname(elem.tag)} {attrs}>".rstrip())
        children = list(elem)
        if not children and (elem.text or "").strip():
            print(f"{'  ' * (depth + 1)}[text]: {(elem.text or '').strip()[:80]}")
        for c in children[:max_children]:
            walk(c, depth + 1)
        if len(children) > max_children:
            print(f"{'  ' * (depth + 1)}... 共 {len(children)} 个子元素")

    print(f"文件: {path}")
    print(f"根元素: <{_localname(root.tag)}>")
    walk(root, 0)


def convert_one(item: ET.Element, cfg: dict) -> str:
    """按配置把单个 item 转成 Markdown 段落"""
    lines = []

    def resolve(xpath):
        if xpath.startswith("./") or xpath.startswith(".//"):
            return item.find(xpath)
        return item.find(xpath)

    # 标题
    title = ""
    t_cfg = cfg.get("title")
    if t_cfg:
        if isinstance(t_cfg, str) and not t_cfg.startswith((".", "/")):
            title = t_cfg
        else:
            el = resolve(t_cfg)
            title = _text_of(el) if el is not None else ""
    if title:
        lines.append(f"## {title}")
    else:
        lines.append("## (无标题)")

    # frontmatter 元数据 (attrs_as_meta: 从 item 属性取)
    meta = []
    for attr in cfg.get("attrs_as_meta", []):
        v = item.get(attr)
        if v:
            meta.append(f"{attr}: {v}")
    if meta:
        lines.insert(0, "---\n" + "\n".join(meta) + "\n---\n")

    # 正文
    for bp in cfg.get("body", []):
        for el in item.findall(bp):
            t = _text_of(el)
            if t:
                lines.append("")
                lines.append(t)

    # 列表
    for lp in cfg.get("list", []):
        for i, el in enumerate(item.findall(lp), 1):
            lines.append(f"{i}. {_text_of(el)}")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="通用文本 XML → Markdown")
    ap.add_argument("--inspect", metavar="FILE", help="查看 XML 结构")
    ap.add_argument("--config", metavar="CFG", help="转换配置 JSON")
    ap.add_argument("input", nargs="?", help="输入 XML 文件")
    ap.add_argument("output", nargs="?", help="输出 .md 或输出目录")
    ap.add_argument("--dir", help="批量转换: 输入目录")
    ap.add_argument("--out", help="批量转换: 输出目录")
    args = ap.parse_args()

    if args.inspect:
        inspect_file(args.inspect)
        return

    if not args.config:
        print("请先 --inspect 查看结构, 再 --config 提供转换配置")
        ap.print_help()
        return

    with open(args.config, encoding="utf-8") as fp:
        cfg = json.load(fp)

    def process_one(src: str, dst: str):
        tree = ET.parse(src)
        root = tree.getroot()
        # Element.findall 不支持绝对路径 //x, 需转为 .//x
        xpath = cfg["item_xpath"]
        if xpath.startswith("//"):
            xpath = "." + xpath
        items = root.findall(xpath)
        if not items:
            print(f"⚠️ {src}: item_xpath '{cfg['item_xpath']}' 无匹配")
            return 0
        parts = [convert_one(it, cfg) for it in items]
        with open(dst, "w", encoding="utf-8") as fp:
            fp.write("\n\n---\n\n".join(parts))
        print(f"✅ {src} → {dst} ({len(items)} 条)")
        return len(items)

    if args.dir:
        out_dir = args.out or os.path.join(os.path.dirname(os.path.abspath(args.dir)), "xml-md")
        os.makedirs(out_dir, exist_ok=True)
        total = 0
        for f in sorted(os.listdir(args.dir)):
            if f.lower().endswith((".xml", ".xml.txt")):
                total += process_one(os.path.join(args.dir, f),
                                     os.path.join(out_dir, os.path.splitext(f)[0] + ".md"))
        print(f"\n完成: 共转换 {total} 条记录")
        return

    if not args.input:
        ap.print_help()
        return

    if args.output and (args.output.endswith("/") or os.path.isdir(args.output)):
        os.makedirs(args.output, exist_ok=True)
        dst = os.path.join(args.output, os.path.splitext(os.path.basename(args.input))[0] + ".md")
    else:
        dst = args.output or os.path.splitext(args.input)[0] + ".md"
    process_one(args.input, dst)


if __name__ == "__main__":
    main()
