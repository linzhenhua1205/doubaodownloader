#!/usr/bin/env python3
"""
web-archive — 网页归档框架（v2.0 扩展版）

将网页保存为知识库 Markdown，具备：
  1. Markdown 格式存储 (YYYY-MM-DD-英文描述.md, 符合 design-003 命名规范)
  2. 图片保留为 web 链接方式 (不下载, 绝对 URL)
  3. 内容去噪: 过滤导航/广告/侧栏/页脚/推荐等非内容信息
  4. 批判辩证分析 + 底层原理 + 市场机会补充 (LLM 增强或规则模板)
  5. 纯 scripts 实现 (框架化, 站点适配器模式)
  6. 针对各类网站的适配器加速处理 (按域名注册, 通用回退)
  7. 保存到 knowledge/06_others/sources/

架构:
    web-archive.py            CLI 入口 (本文件)
    lib/fetcher.py            抓取器 (requests 优先, browser 回退)
    lib/extractor.py          正文提取与去噪 (trafilatura + 站点规则)
    lib/markdown.py           Markdown 生成器 (图片URL化/去噪/骨架)
    lib/analyzer.py           批判分析 + 原理/市场机会增强
    adapters/base.py          站点适配器基类 (注册表)
    adapters/*.py             站点特定适配器 (技术栈/公众号/CSDN/InfoQ...)

Usage:
    python3 scripts/tools/web-archive/web-archive.py --url <URL> [--dry-run] [--no-analyze]
    python3 scripts/tools/web-archive/web-archive.py --url <URL> --slug <自定义slug>
    python3 scripts/tools/web-archive/web-archive.py --url <URL> --out <自定义路径>
"""
import argparse
import json
import sys
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.fetcher import fetch_html, FetchResult
from lib.extractor import extract_content, ExtractedArticle
from lib.markdown import render_markdown, slugify_title
from lib.analyzer import enhance_analysis
from lib.adapter_registry import get_adapter


def main():
    ap = argparse.ArgumentParser(description="Web Archive — 网页归档框架 v2.0")
    ap.add_argument("--url", required=True, help="要归档的网页 URL")
    ap.add_argument("--slug", default=None, help="自定义文件名 slug (默认由标题生成)")
    ap.add_argument("--out", default=None, help="输出 .md 文件路径 (默认 knowledge/06_others/sources/)")
    ap.add_argument("--dry-run", action="store_true", help="只提取不写入")
    ap.add_argument("--no-analyze", action="store_true", help="跳过批判分析/原理/市场机会增强")
    ap.add_argument("--raw-json", default=None, help="调试: 输出提取结果 JSON 到指定路径")
    args = ap.parse_args()

    # 1. 站点适配器识别 (框架化加速)
    adapter = get_adapter(args.url)
    print(f"🔌 站点适配器: {adapter.name} ({adapter.domain_patterns})")

    # 2. 抓取
    result = fetch_html(args.url, adapter)
    if not result.ok:
        print(f"❌ 抓取失败: {result.error}")
        sys.exit(1)
    print(f"📥 抓取成功: {result.status} / {len(result.html)} bytes")

    # 3. 提取正文 (适配器规则 + trafilatura 回退)
    article = extract_content(result.html, args.url, adapter)
    print(f"📄 标题: {article.title}")
    print(f"📄 正文: {len(article.text)} chars / 图片 {len(article.images)} 张 / 链接 {len(article.links)} 个")

    # 4. 批判分析 + 原理 + 市场机会增强
    if not args.no_analyze:
        article = enhance_analysis(article, args.url)

    # 5. 生成 slug / 输出路径 (符合 design-003: YYYY-MM-DD-英文描述.md)
    if not args.slug:
        args.slug = slugify_title(article.title)
    from datetime import datetime as _dt
    today = _dt.now().strftime("%Y-%m-%d")
    # 归档日取自文章发布时间(若有) 否则当天; 文件名=日期-描述.md
    file_stem = args.slug
    if not re.match(r"^\d{4}-\d{2}-\d{2}-", file_stem):
        file_stem = f"{today}-{file_stem}"
    if args.out:
        out_path = Path(args.out)
    else:
        out_path = ROOT / "knowledge" / "06_others" / "sources" / f"{file_stem}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # 6. 渲染 Markdown
    md = render_markdown(article, args.url, out_path)

    if args.raw_json:
        Path(args.raw_json).write_text(json.dumps({
            "title": article.title,
            "text_len": len(article.text),
            "images": article.images,
            "links": article.links[:50],
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"📦 原始提取: {args.raw_json}")

    if args.dry_run:
        print("🔎 DRY-RUN: 不写入文件")
        print(md[:2000])
        sys.exit(0)

    # 7. 写入
    if out_path.exists():
        print(f"⚠️ 文件已存在: {out_path} (将覆盖)")
    out_path.write_text(md, encoding="utf-8")
    print(f"✅ 已保存: {out_path} ({len(md)} chars)")

    # 8. 三同步提示
    print("\n🔗 下一步 (三同步):")
    print(f"   ① README.md 条目库: knowledge/README.md 当日分节追加")
    print(f"   ② log.md 追加: knowledge/log.md 当日分节 (ingest 📥)")
    print(f"   ③ index.md 刷新: python3 scripts/tools/kb-global-index.py")
    print(f"   ④ 格式检查: python3 scripts/check/format-validator.py {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
