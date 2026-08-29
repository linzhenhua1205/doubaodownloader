#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
consistency-rectify.py v1.0 — 超节点一致性治理配套「排查/回写/验证」工具
（consistency-scan.py 的配套闭环脚本）

定位:
  consistency-scan.py 只做「扫描检测」（发现 FAIL → 输出待回写清单）；
  本脚本补上治理闭环的后三段 —— 排查定位 / 安全回写 / 回写验证：
    scan ──▶ plan（排查清单）──▶ apply（自动回写）──▶ verify（DoD 验证）

设计原则:
  1. 不重复造轮子: 通过 subprocess 调用 consistency-scan.py --json 复用规则引擎，
     扫描结果（文件:行号）是本脚本的唯一事实源 —— 只处理 scan 报告的 FAIL 行，
     绝不全文替换，从根上避免误伤豁免行/越界修改。
  2. 语义映射驱动: VLAN 旧编号是「语义映射」而非顺序映射
     （100 training→103 Scale-Out / 200 data plane→102 存储 / 300 control→101 管理），
     映射表 RECTIFY_MAP 配置化，新增回写项 = 加一行配置。
  3. 安全优先: --apply 默认 dry-run 预览；--yes 执行前自动备份到 tmp/bak/rectify-<ts>/；
     只改业务文档（元文档记录层不动）；逐处替换留痕（--json 可追溯）。
  4. 量化验证: --verify 重跑对应规则 → 剩余命中归零 = DoD 完成，输出 13 项 checklist 状态表。

模式:
  python3 scripts/consistency-rectify.py --plan                 # 排查清单（默认）
  python3 scripts/consistency-rectify.py --plan --since 2026-08-25
  python3 scripts/consistency-rectify.py --apply --dry-run      # 预览自动回写（安全）
  python3 scripts/consistency-rectify.py --apply --yes          # 执行自动回写（先备份）
  python3 scripts/consistency-rectify.py --apply --yes --ids P0-1,P0-2   # 只回写指定项
  python3 scripts/consistency-rectify.py --verify               # 回写验证（DoD 完成度）
  python3 scripts/consistency-rectify.py --list                 # 列出回写映射表

依赖: consistency-scan.py（同目录）；Python 3.8+ 标准库。
"""
import argparse
import fnmatch
import json
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KB = ROOT / "knowledge"
SCAN = ROOT / "scripts" / "consistency-scan.py"
BAK_ROOT = ROOT / "tmp" / "bak" / f"rectify-{datetime.now():%Y%m%d-%H%M%S}"

# ─────────────────────────── 回写映射表（配置驱动核心） ───────────────────────────
# mode:
#   AUTO      : 行级正则替换（只处理 scan --json 报告的 FAIL 行，行内 pattern→repl）
#   ALIGN_HEAD: 头部版本行对齐 changelog 最新条目（R13 专属，独立逻辑）
#   MANUAL    : 需人工判断（脚本仅输出精确指引：文件:行 + 上下文 + 建议动作）
# file_glob: 文件名 glob（相对 knowledge/ 的完整路径也参与匹配，取 basename 匹配）
RECTIFY_MAP = [
    # ── P0-1 VLAN 语义回写（C2 权威: 101 管理 / 102 存储 / 103 Scale-Out / 104 Scale-Up）──
    dict(id="P0-1", rule="R2", dec="C2", mode="AUTO", prio="P0",
         file_glob="*pxe-os-installation*",
         pattern=r"VLAN\s*100(?:\s*\([^)]*\))?", repl="VLAN 103 (Scale-Out)",
         note="语义映射: 旧 100 training/compute → 103 Scale-Out（C2 权威 101 管理/102 存储/103 Scale-Out/104 Scale-Up；行内旧注释一并替换避免冗余）"),
    dict(id="P0-1", rule="R2", dec="C2", mode="AUTO", prio="P0",
         file_glob="*pxe-os-installation*",
         pattern=r"VLAN\s*200(?:\s*\([^)]*\))?", repl="VLAN 102 (存储)",
         note="语义映射: 旧 200 data plane/storage → 102 存储"),
    dict(id="P0-1", rule="R2", dec="C2", mode="AUTO", prio="P0",
         file_glob="*pxe-os-installation*",
         pattern=r"VLAN\s*300(?:\s*\([^)]*\))?", repl="VLAN 101 (管理)",
         note="语义映射: 旧 300 control/mgmt → 101 管理"),
    # ── P0-2 台账计数（C6 权威 2612）──
    dict(id="P0-2", rule="R11", dec="C6", mode="AUTO", prio="P0",
         file_glob="*ip-allocation-detailed-scripts*",
         pattern=r"\b2609\b", repl="2612",
         note="C6 台账权威 2612；2609 残留消除（含 L472 行内 2612/2609 矛盾，替换后行内一致）"),
    # ── P0-3 网卡型号（C10 现役 4×CX7；scan 已豁免 reserve/参考/需求语境）──
    #   覆盖三个位置：07 目录部署设计（审计 9 处）/ 02_rd 源头设计（新发现 5 处）/ todo 清单（新发现 2 处）
    dict(id="P0-3", rule="R4", dec="C10", mode="AUTO", prio="P0",
         file_glob="*compute-platform-software-deployment*",
         pattern=r"\bCX8\b", repl="CX7",
         note="C10 现役 4×CX7；CX8 仅 reserve/参考/需求分析语境（scan 豁免行不会被处理）"),
    dict(id="P0-3", rule="R4", dec="C10", mode="AUTO", prio="P0",
         file_glob="*superpod-data-path-deployment*",
         pattern=r"\bCX8\b", repl="CX7",
         note="02_rd 源头部署设计 5 处现役 CX8（L91/L120/L135/L189/L285）——审计 P0-3 跨目录盲区，08-28 全量回归新发现"),
    dict(id="P0-3", rule="R4", dec="C10", mode="AUTO", prio="P0",
         file_glob="*project-management-todo*",
         pattern=r"\bCX8\b", repl="CX7",
         note="todo 清单 2 处现役 CX8（L76 节点形态表 / L127 网卡型号冻结决策项）——C10 裁决后应同步；L539 类历史引用描述不在此列（scan 豁免）"),
    # ── P1-7 固件清单 CX8（external-delivery-model，或注明历史）──
    dict(id="P1-7", rule="R4", dec="C10", mode="AUTO", prio="P1",
         file_glob="*external-delivery-model*",
         pattern=r"\bCX8\b", repl="CX7",
         note="C10 现役 4×CX7；external-delivery-model 固件清单 CX8→CX7（历史语境由 scan 豁免）"),
    # ── P1-6 头部版本行对齐 changelog 最新（R13，6 篇，ALIGN_HEAD 自动）──
    dict(id="P1-6", rule="R13", dec="C32", mode="ALIGN_HEAD", prio="P1",
         file_glob="*", pattern=None, repl=None,
         note="头部版本行 = changelog 最新条目版本（check_version_metadata 判定不一致的文件自动对齐）"),

    # ── 人工项（MANUAL，脚本只出指引，不给自动改）──────────────────────────────
    dict(id="P1-4", rule="R5", dec="C12", mode="MANUAL", prio="P1",
         file_glob="*", pattern=None, repl=None,
         note="77kW/4.8kW 加『GPU 域近似』口径注（firmware-baseline L126、timing-diagram L437/L449 等，位置语义不同需人工）"),
    dict(id="P1-5", rule="R12", dec="C21", mode="MANUAL", prio="P1",
         file_glob="*ip-allocation-detailed-scripts*", pattern=None, repl=None,
         note="ip-scripts L195 PXE 镜像服务须点名承载实体『管理服务器存储网口（部署节点）』"),
    dict(id="P1-8", rule="R1", dec="C1", mode="MANUAL", prio="P1",
         file_glob="*ac-rack*", pattern=None, repl=None,
         note="ac-rack PMC-2 选项 A 标注『200+n 已作废』或移除（L563 附近）"),
    dict(id="P1-9", rule="R4", dec="C17", mode="MANUAL", prio="P1",
         file_glob="*power-on-functional-verification*", pattern=None, repl=None,
         note="functional-verification L539 引用版本更新为 v1.4（C17 升版后引用漂移）"),
    dict(id="P1.5-10", rule="R21", dec="GOV", mode="MANUAL", prio="P1.5",
         file_glob="*", pattern=None, repl=None,
         note="死链 14 处（E1）：不存在文件 6 处需确认/改名、路径层级 5 处修正（03_server 需 ../ 非 ../../）、DECISIONS.md 创建 1 处——明细见审计报告 §8.6"),
    dict(id="P1.5-11", rule="R25", dec="C32", mode="MANUAL", prio="P1.5",
         file_glob="*", pattern=None, repl=None,
         note="版本引用漂移 6 处统一 power-on-sequence v1.4（5 篇业务文档；记录层豁免）"),
    dict(id="P1.5-12", rule="R20", dec="GOV", mode="MANUAL", prio="P1.5",
         file_glob="*", pattern=None, repl=None,
         note="术语混用 15 处（Scale-Out/Up 大小写、circuit-id、inter-rack matrix）——变体替换有误伤风险，人工确认后回写"),
    dict(id="P1.5-13", rule="R22", dec="GOV", mode="MANUAL", prio="P1.5",
         file_glob="*firmware-baseline*", pattern=None, repl=None,
         note="firmware-baseline 头部补版本标记（R22 三要素缺失，E2）"),
]

# 13 项 checklist 完整映射（含非自动项说明），用于 --verify 汇总
CHECKLIST = [
    ("P0-1", "pxe 全文 VLAN 旧编号→101-104（19 处）", "AUTO"),
    ("P0-2", "ip-scripts 2609→2612（8 处）", "AUTO"),
    ("P0-3", "C10 全库 CX8→CX7（07部署2+02_rd源头5+todo2）", "AUTO"),
    ("P1-4", "77kW/4.8kW 口径注（3 处）", "MANUAL"),
    ("P1-5", "PXE 承载实体点名（1 处）", "MANUAL"),
    ("P1-6", "6 篇头部版本对齐 changelog", "AUTO"),
    ("P1-7", "external-delivery 固件 CX8→CX7", "AUTO"),
    ("P1-8", "ac-rack PMC-2 200+n 作废注", "MANUAL"),
    ("P1-9", "functional L539 引用版本 v1.4", "MANUAL"),
    ("P1.5-10", "死链修复 14 处", "MANUAL"),
    ("P1.5-11", "版本引用统一 v1.4（6 处）", "MANUAL"),
    ("P1.5-12", "术语混用回写（15 处）", "MANUAL"),
    ("P1.5-13", "firmware-baseline 头部版本标记", "MANUAL"),
]


# ─────────────────────────── 复用 scan 引擎 ───────────────────────────
def run_scan(rules: str | None = None, since: str | None = None,
             exclude: str | None = None) -> dict:
    """调用 consistency-scan.py --json，返回结构化结果。"""
    cmd = [sys.executable, str(SCAN), "--json"]
    if rules:
        cmd += ["--rules", rules]
    if since:
        cmd += ["--since", since]
    if exclude:
        cmd += ["--exclude", exclude]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        print(f"[error] scan 失败: {r.stderr[-500:]}", file=sys.stderr)
        sys.exit(1)
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        print(f"[error] scan JSON 解析失败: {r.stdout[-500:]}", file=sys.stderr)
        sys.exit(1)


def issues_by_rule(data: dict) -> dict:
    by = defaultdict(list)
    for it in data.get("issues", []):
        by[it["id"]].append(it)
    return by


# ─────────────────────────── --plan 排查清单 ───────────────────────────
def cmd_plan(args) -> None:
    data = run_scan(rules=args.rules, since=args.since, exclude=args.exclude)
    by_rule = issues_by_rule(data)
    all_issues = data.get("issues", [])

    print(f"═══ consistency-rectify --plan ═══ scan {data.get('scanned_files')} 篇 | "
          f"total {data.get('total_issues')} 命中 | since={args.since or 'all'}")
    print("按 13 项回写 checklist 分组（AUTO=可自动回写 / MANUAL=人工指引）:\n")

    # 将 scan 命中按 RECTIFY_MAP 条目归类
    consumed = set()  # 已被 AUTO/ALIGN 条目覆盖的 (file, line)
    for item in RECTIFY_MAP:
        hits = []
        for it in all_issues:
            if it["id"] != item["rule"]:
                continue
            if item["file_glob"] != "*" and not fnmatch.fnmatch(it["file"], item["file_glob"]):
                continue
            if item["mode"] == "AUTO":
                key = (it["file"], it["line"])
                if key in consumed:
                    continue
                consumed.add(key)
            hits.append(it)
        if not hits:
            continue
        kind = "🛠️ AUTO" if item["mode"] == "AUTO" else \
               ("🔧 ALIGN" if item["mode"] == "ALIGN_HEAD" else "👤 MANUAL")
        print(f"── [{item['id']}] {item['prio']} {kind} {item['rule']} {item['dec']} — {len(hits)} 处")
        for it in hits[:15]:
            print(f"   {it['file']}:{it['line']}  {it['text'][:80]}")
        if len(hits) > 15:
            print(f"   ... 另有 {len(hits)-15} 处")
        print(f"   ↳ {item['note']}\n")

    # 未被映射覆盖的命中（需要新增映射或人工）
    covered = consumed | {
        (it["file"], it["line"]) for it in all_issues
        for m in RECTIFY_MAP if m["mode"] == "MANUAL"
        and m["file_glob"] != "*" and fnmatch.fnmatch(it["file"], m["file_glob"])
        and it["id"] == m["rule"]
    }
    orphan = [it for it in all_issues if (it["file"], it["line"]) not in covered
              and it["severity"] in ("HIGH", "MED")]
    if orphan:
        print(f"── ⚠️ 未归类命中 {len(orphan)} 处（映射表未覆盖，建议新增 RECTIFY_MAP 条目）:")
        for it in orphan[:12]:
            print(f"   {it['file']}:{it['line']}  R{it['id']} {it['text'][:80]}")

    # 汇总
    auto_n = sum(1 for m in RECTIFY_MAP if m["mode"] in ("AUTO", "ALIGN_HEAD"))
    man_n = sum(1 for m in RECTIFY_MAP if m["mode"] == "MANUAL")
    print(f"\n═══ 汇总: 自动项 {auto_n}（--apply --yes 一键回写）/ 人工项 {man_n}（按指引手改）═══")
    print("下一步: python3 scripts/consistency-rectify.py --apply --dry-run  # 预览自动回写")


# ─────────────────────────── --apply 自动回写 ───────────────────────────
def load_scan_anchor(data: dict) -> dict:
    """从 scan --json 提取 (file, line) 锚点集，按文件聚合。"""
    anchors = defaultdict(set)
    for it in data.get("issues", []):
        anchors[it["file"]].add(it["line"])
    return anchors


def align_version_head(path: Path) -> tuple[int, str]:
    """R13 版本头对齐：头部版本行改为 changelog 最新。返回 (改动数, 说明)。"""
    text = path.read_text(encoding="utf-8")
    head_re = re.compile(r"(版本[^v\d\n]{0,8}[:：]\s*)v?(\d+\.\d+)")
    ch_re = re.compile(r"^\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*v?(\d+\.\d+)\s*\|", re.M)
    ch_vers = [tuple(int(x) for x in m.group(2).split(".")) for m in ch_re.finditer(text)]
    if not ch_vers:
        return 0, "无 changelog，跳过"
    latest = max(ch_vers)
    latest_s = ".".join(map(str, latest))
    m = head_re.search(text[:1200])
    if not m:
        return 0, "无头部版本行，跳过（R22 场景走 MANUAL）"
    cur = m.group(2)
    if cur == latest_s:
        return 0, f"已一致 v{latest_s}"
    new_text = text[:m.start(1)] + m.group(1) + latest_s + text[m.end(2):]
    path.write_text(new_text, encoding="utf-8")
    return 1, f"头部 v{cur} → v{latest_s}"


def cmd_apply(args) -> None:
    ids = set(x.strip() for x in (args.ids or "").split(",")) if args.ids else None
    targets = [m for m in RECTIFY_MAP if m["mode"] in ("AUTO", "ALIGN_HEAD")
               and (ids is None or m["id"] in ids)]
    if not targets:
        print("[info] 无匹配的自动回写条目（--ids 检查或映射表为空）")
        return

    # 需要哪些规则命中作为锚点
    need_rules = ",".join(sorted({m["rule"] for m in targets if m["mode"] == "AUTO"}))
    data = run_scan(rules=need_rules or None, since=args.since, exclude=args.exclude)
    anchors = load_scan_anchor(data)

    if not args.yes:
        print(f"═══ consistency-rectify --apply --dry-run ═══（{len(targets)} 条目，预览不落盘）")
        print("确认无误后加 --yes 执行；执行前自动备份到 tmp/bak/rectify-<ts>/\n")

    # 统计待处理（按条目）；changes = (item_id, rel, ln, pattern, repl, old, new)
    changes = []
    for item in targets:
        if item["mode"] == "ALIGN_HEAD":
            # 版本头对齐：需要 R13 判定不一致的文件（scan 的 R13 输出 file 集合）
            files = {it["file"] for it in data.get("issues", []) if it["id"] == "R13"}
            for rel in sorted(files):
                fp = KB / rel
                if not fp.exists():
                    continue
                changes.append((item["id"], rel, 0, None, None, "版本头", "对齐 changelog 最新"))
            continue
        for rel in sorted(anchors):
            if not fnmatch.fnmatch(rel, item["file_glob"]):
                continue
            fp = KB / rel
            if not fp.exists():
                continue
            lines = fp.read_text(encoding="utf-8").split("\n")
            pat = re.compile(item["pattern"])
            for ln in sorted(anchors[rel]):
                if ln < 1 or ln > len(lines):
                    continue
                old = lines[ln - 1]
                new, n = pat.subn(item["repl"], old)
                if n and new != old:
                    changes.append((item["id"], rel, ln, item["pattern"], item["repl"],
                                    old.strip()[:90], new.strip()[:90]))

    if not changes:
        print("[info] 无可执行回写（对应规则已零命中，或目标文件无 FAIL 行）")
        return

    # 按文件聚合，倒序行号执行（避免行号漂移）
    per_file = defaultdict(list)
    for c in changes:
        per_file[c[1]].append(c)

    if not args.yes:
        print(f"共 {len(changes)} 处将修改：")
        cur = None
        for item_id, rel, ln, _p, _r, old, new in changes:
            if item_id != cur:
                print(f"\n[{item_id}]")
                cur = item_id
            print(f"   {rel}:{ln}\n      - {old}\n      + {new}")
        print("\n--dry-run 结束，未做任何修改。")
        return

    # 执行：备份 + 替换（同一行多处命中按条目顺序依次替换，行号逆序防漂移）
    BAK_ROOT.mkdir(parents=True, exist_ok=True)
    total = 0
    for rel, cs in per_file.items():
        fp = KB / rel
        # 备份
        bak_dir = BAK_ROOT / str(fp.parent.relative_to(KB))
        bak_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(fp, bak_dir / fp.name)
        lines = fp.read_text(encoding="utf-8").split("\n")
        # by_line[行号] = [(pattern, repl), ...]；aligns = ALIGN_HEAD 条目
        by_line = defaultdict(list)
        aligns = []
        for item_id, _, ln, pattern, repl, _old, _new in cs:
            if ln == 0:
                aligns.append(item_id)
            else:
                by_line[ln].append((pattern, repl))
        for ln in sorted(by_line, reverse=True):  # 倒序防行号漂移
            for pattern, repl in by_line[ln]:
                lines[ln - 1] = re.sub(pattern, repl, lines[ln - 1])
                total += 1
        fp.write_text("\n".join(lines), encoding="utf-8")
        # ALIGN_HEAD（整文件独立逻辑）
        for item_id in aligns:
            n, msg = align_version_head(fp)
            total += n
        print(f"✅ {rel} 修改 {len(cs)} 处（备份: {bak_dir / fp.name}）")

    print(f"\n═══ 执行完成: 共修改 {total} 处 | 备份目录: {BAK_ROOT} ═══")

    # ── 残留 sanity check：scan 模式可能漏掉"简写裸编号"（如 VLAN 300→200 的 →200）──
    residual_pats = [
        (r"VLAN\s*(?:100|200|300)\b", "旧 VLAN 编号（VLAN 前缀形式）"),
        (r"→\s*(?:100|200|300)\b", "旧 VLAN 编号（简写 →NNN 形式）"),
        (r"\b2609\b", "旧台账计数 2609"),
    ]
    warns = []
    for rel, cs in per_file.items():
        fp = KB / rel
        text = fp.read_text(encoding="utf-8")
        for pat, label in residual_pats:
            for m in re.finditer(pat, text):
                ln = text[:m.start()].count("\n") + 1
                warns.append(f"  ⚠️ {rel}:{ln} 残留 {label}: {m.group(0)[:40]}")
    if warns:
        print("\n残留检查（scan 模式盲区防御）发现：")
        print("\n".join(warns[:15]))
        if len(warns) > 15:
            print(f"  ... 另有 {len(warns)-15} 处")
        print("→ 需人工处理或扩展 RECTIFY_MAP 映射")
    else:
        print("残留检查: 无旧编号残留 ✅")

    print("下一步: python3 scripts/consistency-rectify.py --verify   # DoD 验证")


# ─────────────────────────── --verify 回写验证 ───────────────────────────
def cmd_verify(args) -> None:
    auto_rules = sorted({m["rule"] for m in RECTIFY_MAP
                         if m["mode"] in ("AUTO", "ALIGN_HEAD")})
    data = run_scan(rules=",".join(auto_rules), since=args.since, exclude=args.exclude)
    by_rule = issues_by_rule(data)

    print(f"═══ consistency-rectify --verify ═══ 13 项回写 checklist 状态（规则: {','.join(auto_rules)}）\n")
    print(f"{'#':<8}{'动作':<42}{'类型':<8}{'状态':<10}剩余")
    print("-" * 78)
    done = total_auto = 0
    for cid, desc, kind in CHECKLIST:
        if kind == "MANUAL":
            print(f"{cid:<8}{desc:<42}{'👤 人工':<8}{'待执行':<10}-")
            continue
        total_auto += 1
        items = [m for m in RECTIFY_MAP if m["id"] == cid
                 and m["mode"] in ("AUTO", "ALIGN_HEAD")]
        if not items:
            continue
        rule_ids = {m["rule"] for m in items}
        resid = sum(1 for rid in rule_ids for it in by_rule.get(rid, [])
                    if any(m["file_glob"] == "*" or fnmatch.fnmatch(it["file"], m["file_glob"])
                           for m in items))
        # R13 是 ALIGN_HEAD 全域条目，按 file_glob * 统计全部 R13 残留
        if resid == 0:
            done += 1
            print(f"{cid:<8}{desc:<42}{'🛠️ 自动':<8}{'✅ 完成':<10}0")
        else:
            print(f"{cid:<8}{desc:<42}{'🛠️ 自动':<8}{'⚠️ 残留':<10}{resid}")

    print("-" * 78)
    print(f"自动项完成度: {done}/{total_auto}（{'全部清零 ✅' if done == total_auto else '仍有残留，重跑 --apply --yes 或人工处理'}）")
    print("人工项 8 项：按 --plan 输出的 MANUAL 指引逐项手改；改完重跑 --verify 复核")


# ─────────────────────────── --list ───────────────────────────
def cmd_list() -> None:
    print("consistency-rectify v1.0 回写映射表（配置驱动，13 项 checklist）:\n")
    for item in RECTIFY_MAP:
        kind = {"AUTO": "🛠️ AUTO", "ALIGN_HEAD": "🔧 ALIGN", "MANUAL": "👤 MANUAL"}[item["mode"]]
        pat = item.get("pattern") or "-"
        repl = item.get("repl") or "-"
        print(f"  [{item['id']}] {item['prio']} {kind} {item['rule']} {item['dec']} | "
              f"glob={item['file_glob']} | {pat} → {repl}")
        print(f"       {item['note']}\n")


# ─────────────────────────── main ───────────────────────────
def main():
    ap = argparse.ArgumentParser(
        description="超节点一致性治理配套排查/回写/验证工具 v1.0（consistency-scan.py 配套闭环）")
    ap.add_argument("--plan", action="store_true", help="排查清单（默认）")
    ap.add_argument("--apply", action="store_true", help="自动回写（配合 --yes 执行，默认 dry-run）")
    ap.add_argument("--verify", action="store_true", help="回写验证（DoD 完成度）")
    ap.add_argument("--list", action="store_true", help="列出回写映射表")
    ap.add_argument("--ids", type=str, default=None, help="--apply 只回写指定条目，逗号分隔如 P0-1,P0-2")
    ap.add_argument("--yes", action="store_true", help="--apply 实际执行（否则仅预览）")
    ap.add_argument("--since", type=str, default=None, help="仅处理文件名日期 >= 该日期（YYYY-MM-DD）")
    ap.add_argument("--rules", type=str, default=None, help="--plan 限定规则子集，逗号分隔")
    ap.add_argument("--exclude", type=str, default=None, help="文件名 glob 豁免（逗号分隔）")
    args = ap.parse_args()

    if args.list:
        cmd_list()
    elif args.apply:
        cmd_apply(args)
    elif args.verify:
        cmd_verify(args)
    else:
        cmd_plan(args)


if __name__ == "__main__":
    main()
