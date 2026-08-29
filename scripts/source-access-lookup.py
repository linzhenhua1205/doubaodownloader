#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#================================================================
# source-access-lookup.py v1 — 网站访问方式查表（token 优先）
#
# 用途：为「访问某个网站/URL」提供**查表方案**：根据数据源注册表
#       （source-registry.json SSOT）返回该源的访问方式优先级链，
#       按 token 从省到贵排序；AI 访问前先查表，按优先级依次尝试，
#       失败自动降级，避免每次从最重的浏览器/CDP 开始试。
#
# 优先级原则（token 省 → 费，第一性原理：结构化 < 正文提取 < 原始渲染）：
#   rss/api   结构化数据（最小 token，若有 RSS/API 最优先）
#   jina      r.jina.ai 转 Markdown（省 token，限 20 RPM，正文类页面）
#   static    curl/requests 直连静态 HTML → 正文提取
#   web_fetch WebFetch 工具（小模型按 prompt 提取，返回提取结果）
#   js        JS 渲染页面（需渲染执行，token 高）
#   browser   CDP 浏览器（最重，登录态/交互/反爬兜底）
#   local     本地文件（子模块/离线数据）
#
# 用法：
#   python3 scripts/source-access-lookup.py --url https://www.servethehome.com/xxx
#   python3 scripts/source-access-lookup.py --domain tomshardware.com
#   python3 scripts/source-access-lookup.py --id arxiv
#   python3 scripts/source-access-lookup.py --list            # 全表
#   python3 scripts/source-access-lookup.py --list --json     # 全表 JSON
#   python3 scripts/source-access-lookup.py --recommend <id>  # 推荐首选方式
#
# 输出：紧凑单行（省 token）：id: chain=[web_fetch, static, jina] 推荐=web_fetch
#
# 变更日志：
#   2026-08-14 v1 created（网站访问方式查表 + 优先级链，token 降本）
#================================================================

import argparse
import json
import os
import sys
from pathlib import Path

WORKSPACE = Path.home() / "cow"
REGISTRY_FILE = WORKSPACE / "skills" / "web-access" / "scripts" / "config" / "source-registry.json"

# token 省→费 的通用优先级模板（policy 引用；每源 access_chain 是其可用子集）
ACCESS_PRIORITY = ["rss", "api", "jina", "static", "web_fetch", "js", "browser", "local"]
ACCESS_COST = {  # token 相对成本定性标注（供输出展示）
    "rss": "最低(结构化)", "api": "最低(结构化)", "jina": "低(Markdown)",
    "static": "中(HTML提取)", "web_fetch": "中(工具提取)", "js": "高(渲染)",
    "browser": "最高(浏览器)", "local": "零(本地)",
}


def load_registry() -> dict:
    if not REGISTRY_FILE.exists():
        print(f"[ERR] 注册表不存在: {REGISTRY_FILE}", file=sys.stderr)
        sys.exit(2)
    try:
        return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"[ERR] 注册表损坏: {e}", file=sys.stderr)
        sys.exit(2)


def _all_sources(reg: dict) -> list:
    """合并 professional_sites + content_sources，统一视图。"""
    out = []
    for key in ("professional_sites", "content_sources"):
        for s in reg.get(key, []):
            s = dict(s)
            s["_group"] = key
            out.append(s)
    return out


def _chain(s: dict) -> list:
    """源的有效访问链：显式 access_chain > 单值 access > 默认（web_fetch）。"""
    chain = s.get("access_chain")
    if chain:
        return [c for c in chain if c in ACCESS_PRIORITY]
    access = s.get("access")
    if access and access != "?":
        return [access] if access in ACCESS_PRIORITY else ["web_fetch"]
    return ["web_fetch"]


def _match(reg: dict, url: str = "", domain: str = "", src_id: str = "") -> dict:
    """按 url 域名 / domain / id 匹配源；返回源 dict 或 None。"""
    # 归一化输入
    dom = domain.strip().lower().lstrip("*.") if domain else ""
    if url:
        u = url.lower()
        for prefix in ("https://", "http://", "www."):
            u = u.replace(prefix, "")
        dom = u.split("/")[0].split("?")[0] if not dom else dom

    for s in _all_sources(reg):
        if src_id and s.get("id") == src_id:
            return s
        if dom:
            for cand in (s.get("id", "").lower(), s.get("url", "").lower()):
                # 空 cand 是任何字符串的子串（"" in x == True），必须排除
                if cand and (dom in cand or cand in dom):
                    return s
    return None


def _format(src: dict, chain: list) -> str:
    rec = chain[0] if chain else "web_fetch"
    costs = ";".join(f"{c}={ACCESS_COST.get(c,'?')}" for c in chain)
    return (f"{src.get('id','?')}: chain=[{', '.join(chain)}] 推荐={rec} "
            f"reachable={src.get('reachable')} grade={src.get('grade','?')} "
            f"[{costs}]")


def main():
    ap = argparse.ArgumentParser(description="网站访问方式查表（token 优先）")
    ap.add_argument("--url", help="目标 URL")
    ap.add_argument("--domain", help="目标域名")
    ap.add_argument("--id", help="源 id（如 arxiv / servethehome）")
    ap.add_argument("--list", action="store_true", help="列出全部源及访问链")
    ap.add_argument("--json", action="store_true", help="--list 时输出 JSON")
    ap.add_argument("--recommend", metavar="ID", help="推荐某源的首选访问方式")
    args = ap.parse_args()

    reg = load_registry()

    if args.list:
        rows = []
        for s in _all_sources(reg):
            rows.append({"id": s.get("id"), "group": s["_group"], "grade": s.get("grade"),
                         "reachable": s.get("reachable"), "chain": _chain(s)})
        if args.json:
            print(json.dumps(rows, ensure_ascii=False, indent=1))
        else:
            print(f"# 网站访问方式查表（{len(rows)} 源）— token 省→费: {' > '.join(ACCESS_PRIORITY)}")
            for r in rows:
                print(f"{r['id']:28s} [{', '.join(r['chain'])}] "
                      f"reach={r['reachable']} grade={r['grade']} ({r['group'][:12]})")
        sys.exit(0)

    if args.recommend:
        s = _match(reg, src_id=args.recommend)
        if not s:
            print(f"[ERR] 未找到源: {args.recommend}", file=sys.stderr)
            sys.exit(1)
        chain = _chain(s)
        rec = chain[0] if chain else "web_fetch"
        print(f"{args.recommend}: 首选={rec}（chain=[{', '.join(chain)}]）")
        sys.exit(0)

    if not (args.url or args.domain or args.id):
        ap.print_help()
        sys.exit(1)

    s = _match(reg, url=args.url, domain=args.domain, src_id=args.id)
    if not s:
        print(f"[INFO] 未注册源（{args.url or args.domain or args.id}），默认链=[web_fetch, jina, browser] "
              f"推荐=web_fetch；可在 source-registry.json 注册后获得专属链")
        sys.exit(0)

    print(_format(s, _chain(s)))


if __name__ == "__main__":
    main()
