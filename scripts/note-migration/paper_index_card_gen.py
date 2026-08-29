#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""paper_index_card_gen.py — 纸件索引卡批量生成

为 60 本纸件笔记生成索引卡骨架 (每本一个 Markdown 文件),
后续由人工填写: 主题/时间跨度/字迹评估/关键事件/A类标注。

生成目录结构:
  out/
  ├── README.md          # 60 本总台账
  └── NW-001.md ... NW-060.md   # 索引卡 (NW = Notebook)

用法:
  python3 paper_index_card_gen.py --count 60 --out <目录>

纯标准库。
"""
import argparse
import os
import sys
from datetime import date


TEMPLATE = """# 索引卡 {code}: {title}

> **状态**: ⬜ 待整理 | **A 类占比**: ?% | **更新**: {today}

## 基本信息

| 项 | 内容 |
|:---|:-----|
| 编号 | {code} |
| 封面标题 | |
| 时间跨度 | ~ 至 ~ |
| 页数 | ~ 页 |
| 字迹评估 | ⬜ 工整 / ⬜ 一般 / ⬜ 潦草 |
| 内容类型 | ⬜ 工作 ⬜ 学习 ⬜ 生活 ⬜ 混合 |
| 物理位置 | |

## 章节目录 (每章: 主题 + 页码)

| 页码范围 | 主题 | A类? |
|:--------|:-----|:----:|
| | | ⬜ |
| | | ⬜ |
| | | ⬜ |

## 关键事件/要点 (按页定位)

- 第 ~ 页: 
- 第 ~ 页: 

## 数字化记录

- [ ] 已扫描? (路径: )
- [ ] 已 OCR? (识别率: %)
- [ ] 已提取入知识库? (链接: )

## 备注

"""


def main():
    ap = argparse.ArgumentParser(description="纸件索引卡批量生成")
    ap.add_argument("--count", type=int, default=60, help="笔记本数量 (默认 60)")
    ap.add_argument("--out", default="paper-index-cards", help="输出目录")
    ap.add_argument("--prefix", default="NW", help="编号前缀 (默认 NW)")
    ap.add_argument("--title", default="待填", help="默认标题")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    today = date.today().isoformat()

    # 总台账
    lines = [f"# 纸件笔记总台账 ({args.count} 本)", "",
             f"> 生成: {today} | 每本索引卡见同目录 NW-XXX.md", "",
             "| 编号 | 封面标题 | 时间跨度 | 页数 | 字迹 | A类? | 状态 |",
             "|:-----|:---------|:---------|:-----|:-----|:----:|:----:|"]
    for i in range(1, args.count + 1):
        code = f"{args.prefix}-{i:03d}"
        lines.append(f"| {code} | | | | | ⬜ | ⬜ 待整理 |")
    with open(os.path.join(args.out, "README.md"), "w", encoding="utf-8") as fp:
        fp.write("\n".join(lines))

    # 索引卡
    for i in range(1, args.count + 1):
        code = f"{args.prefix}-{i:03d}"
        content = TEMPLATE.format(code=code, title=args.title, today=today)
        with open(os.path.join(args.out, f"{code}.md"), "w", encoding="utf-8") as fp:
            fp.write(content)

    print(f"✅ 已生成 {args.count} 张索引卡 + README 台账 → {args.out}/")
    print("   接下来: 人工填写每张卡 (封面标题/时间跨度/章节/关键事件/A类标注)")


if __name__ == "__main__":
    main()
