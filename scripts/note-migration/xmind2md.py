#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""xmind2md.py — XMind 思维导图 → Markdown 转换脚本

支持:
  - XMind 8 及更早: content.xml (xmap-content 树)
  - XMind 2020+:   content.json (新版格式, 优先使用)
  - 单文件或整个目录批量转换

用法:
  python3 xmind2md.py <输入.xmind> [输出.md]
  python3 xmind2md.py --dir <输入目录> --out <输出目录>
  python3 xmind2md.py --inspect <输入.xmind>   # 只查看结构, 不转换

纯标准库 (zipfile/xml.etree/json), 无第三方依赖, Python 3.6+ 可跑。
"""
import argparse
import json
import os
import sys
import zipfile
import xml.etree.ElementTree as ET

NS = {"x": "urn:xmind:xmap:xmlns:content:2.0"}


def _clean_text(s: str) -> str:
    """清洗节点文本: 去空白/换行折叠"""
    if not s:
        return ""
    return " ".join(s.split())


def walk_json(topic: dict, lines: list, depth: int):
    """遍历 XMind content.json 的 topic 树"""
    title = _clean_text(topic.get("title", ""))
    indent = "  " * depth
    if depth == 0:
        lines.append(f"## {title}" if title else "## (无标题)")
    else:
        lines.append(f"{indent}- {title}" if title else f"{indent}- (无标题)")
    # 备注 (plain text)
    notes = topic.get("notes", {}).get("plain", {}).get("content", "")
    if notes:
        for ln in notes.strip().splitlines():
            lines.append(f"{indent}  > {ln}")
    # 子主题
    for child in topic.get("children", {}).get("attached", []) or []:
        walk_json(child, lines, depth + 1)


def walk_xml(elem: ET.Element, lines: list, depth: int):
    """遍历 XMind content.xml 的 topic 树"""
    title = _clean_text(elem.get("title", ""))
    indent = "  " * depth
    if depth == 0:
        lines.append(f"## {title}" if title else "## (无标题)")
    else:
        lines.append(f"{indent}- {title}" if title else f"{indent}- (无标题)")
    # 备注
    for notes in elem.findall(".//x:notes", NS):
        for p in notes.iter("{urn:xmind:xmap:xmlns:content:2.0}plain"):
            if p.text and p.text.strip():
                for ln in p.text.strip().splitlines():
                    lines.append(f"{indent}  > {ln}")
        break  # 只取第一个 notes
    # 子主题
    for child in elem.findall("x:children/x:topics/x:topic", NS):
        walk_xml(child, lines, depth + 1)


def convert_file(xmind_path: str) -> str:
    """转换单个 .xmind 文件 → Markdown 文本"""
    with zipfile.ZipFile(xmind_path) as zf:
        # 新版: content.json 优先
        if "content.json" in zf.namelist():
            data = json.loads(zf.read("content.json").decode("utf-8"))
            parts = []
            for sheet in data:
                title = _clean_text(sheet.get("title", os.path.basename(xmind_path)))
                root = sheet.get("rootTopic", {})
                lines = [f"# {title}", ""]
                walk_json(root, lines, 0)
                parts.append("\n".join(lines))
            return "\n\n---\n\n".join(parts)
        # 旧版: content.xml
        if "content.xml" in zf.namelist():
            root = ET.fromstring(zf.read("content.xml"))
            parts = []
            for sheet in root.findall("x:sheet", NS):
                title = _clean_text(sheet.get("title", os.path.basename(xmind_path)))
                lines = [f"# {title}", ""]
                topic = sheet.find("x:topic", NS)
                if topic is not None:
                    walk_xml(topic, lines, 0)
                parts.append("\n".join(lines))
            return "\n\n---\n\n".join(parts)
    raise ValueError("未找到 content.json 或 content.xml, 可能不是有效 XMind 文件")


def inspect_file(xmind_path: str):
    """只查看文件内部结构 (帮助判断新旧格式/排查问题)"""
    with zipfile.ZipFile(xmind_path) as zf:
        print(f"文件: {xmind_path}")
        print(f"内部条目 ({len(zf.namelist())} 个):")
        for n in zf.namelist():
            print(f"  - {n} ({zf.getinfo(n).file_size} bytes)")
        if "content.json" in zf.namelist():
            data = json.loads(zf.read("content.json").decode("utf-8"))
            print(f"\ncontent.json 顶层结构: {list(data[0].keys()) if data else '空'}")
            if data:
                rt = data[0].get("rootTopic", {})
                print(f"rootTopic keys: {list(rt.keys())}")
        if "content.xml" in zf.namelist():
            root = ET.fromstring(zf.read("content.xml"))
            print(f"\ncontent.xml 根标签: {root.tag}, 子元素: {[c.tag for c in root][:5]}")


def main():
    ap = argparse.ArgumentParser(description="XMind → Markdown 转换")
    ap.add_argument("input", nargs="?", help="输入 .xmind 文件")
    ap.add_argument("output", nargs="?", help="输出 .md 文件 (默认同名)")
    ap.add_argument("--dir", help="批量转换: 输入目录")
    ap.add_argument("--out", help="批量转换: 输出目录 (默认 input/../xmind-md)")
    ap.add_argument("--inspect", metavar="FILE", help="查看 XMind 内部结构")
    args = ap.parse_args()

    if args.inspect:
        inspect_file(args.inspect)
        return

    if args.dir:
        out_dir = args.out or os.path.join(os.path.dirname(os.path.abspath(args.dir)), "xmind-md")
        os.makedirs(out_dir, exist_ok=True)
        files = sorted(f for f in os.listdir(args.dir) if f.lower().endswith(".xmind"))
        if not files:
            print(f"⚠️ {args.dir} 下没有 .xmind 文件")
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
