#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
consistency-scan.py v2.0 — 超节点规格一致性门禁扫描器（配置驱动，全面版）

背景: 对齐 08-27 三层治理文档 §5.4 设计（DEC 登记表驱动的字段级一致性扫描）。
      C1-C32 六篇裁决文档已定义 SSOT 锚点表 + 校验门禁（grep 分散于 3 篇文档），
      本脚本将其收敛为单一可执行门禁，输出 = 自动生成的回写 checklist。

v2.0 变更（2026-08-28 全面版）:
  1. 修复 v1.0 误报：R1 豁免"旧式/解释/本方案规范为"；R4 豁免"客户需求/变更评估/直连"；
     R8 豁免"缺陷优先级/分诊/评审分级"（C29 只管发现生命周期命名）
  2. 新增语义规则 R15（存储 9 台残留）/R16（兜底 IP 去柜号）/R17（CX8 预留正向提示）
     /R20（术语表同义异表述，TERMS 配置驱动）
  3. 新增结构规则 R21（交叉链接死链）/R22（头部元数据三要素）/R23（文件命名规范）
     /R24（管道表格格式）/R25（跨文档版本引用漂移）
  4. 新增回写状态核验 R26（C17-C20 functional 升版）/R27（C21-C24 PXE 回写）——状态类输出
  5. CX7 角色限定（C28-C32 门禁 4）以 R10 INFO 级提示保留人工抽查（v1.0 判定噪音大，维持降级）

用法:
  python3 scripts/consistency-scan.py                       # 全目录扫描
  python3 scripts/consistency-scan.py --since 2026-08-25    # 仅近 N 日文件
  python3 scripts/consistency-scan.py --rules R4,R13,R21    # 只跑指定规则
  python3 scripts/consistency-scan.py --json                # JSON 输出（审计报告引用）
  python3 scripts/consistency-scan.py --exclude '*.audit*.md'  # 豁免元文档
  python3 scripts/consistency-scan.py --terms               # 仅跑术语表规则 R20
  python3 scripts/consistency-scan.py --list                # 列出全部规则说明

配置模型（每行 = 一条门禁）:
  {id, dec, field, pattern, exempt, scope, severity, note}
  - pattern : 违规正则（命中即 FAIL，除非命中 exempt 行）
  - exempt  : 行级豁免正则（旧口径声明/参考平台/作废注记等合法语境）
  - severity: HIGH（裁决已定案残留）/ MED（口径/元数据）/ LOW / INFO（不计 FAIL）

规则来源: C1-C9 §4 / C10-C16 §5 / C28-C32 §7 锚点表与门禁 + 08-28 审计报告新增规则
         + 08-28 全面版治理方案 §3（术语治理/结构治理/版本引用治理）。
"""
import argparse
import fnmatch
import json
import re
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

KB = Path(__file__).resolve().parent.parent / "knowledge"
DEFAULT_SCOPES = [
    # 2026-08-28: 10_supernode-rack 已合并入 01_superpod（git c6c1ae6d），仅保留现行路径
    KB / "02_rd" / "02_project" / "01_superpod",
]

# ─────────────────────────── 门禁规则表（配置驱动核心） ───────────────────────────
# pattern 命中且不被 exempt 豁免 → FAIL。severity: HIGH/MED/LOW/INFO
# 豁免词设计原则：裁决文档取证引用/门禁命令示例/历史声明/需求与变更评估为合法语境，不判 FAIL
RULES = [
    # ── 编址域（C1-C9 §4） ──────────────────────────────────────────────
    dict(id="R1", dec="C1", field="Scale-Up 公式", severity="HIGH",
         pattern=r"S\*12\+P|S×12\+P|10\.1\.<R>\.96\+slot|200\+n",
         exempt=r"取代|作废|旧公式|原公式|旧式|越界|早期|历史|证据|回写|已执行|禁止出现|门禁|grep|✅|问题复述|替代旧|改写引入|规范为|本方案|推荐|静态兜底|option 82|为什么|解释|示例|演示",
         note="Scale-Up 旧公式/带柜号兜底/200+n 残留，应零命中；作废口径作候选选项亦命中（ac-rack PMC-2 属此类）"),
    dict(id="R2", dec="C2", field="VLAN 编号", severity="HIGH",
         pattern=r"VLAN\s*(100|200|300)\b",
         exempt=r"取代|作废|旧编号|历史|101-104|证据|回写|已执行|禁止|门禁|grep|✅|用户矛盾",
         note="VLAN 权威口径 101-104，100/200/300 仅允许取代头注/历史声明"),
    dict(id="R3", dec="C3", field="IP 网段框架", severity="HIGH",
         pattern=r"10\.100\.",
         exempt=r"取代|作废|早期|已被.*取代|废弃|迁移|原始|历史|旧",
         note="10.100 旧框架须带取代/废弃标注"),
    # ── 硬件/BOM 域（C10-C16 §5） ───────────────────────────────────────
    dict(id="R4", dec="C10", field="网卡型号 CX8", severity="HIGH",
         pattern=r"\bCX8\b",
         exempt=r"reserve|reference|NVL72|GB300|downgraded|future|预留|参考|取代|作废|证据|矛盾描述|回写|已执行|禁止|门禁|grep|✅|双镜像|双基线|客户|需求|变更|评估|直连|预算|候选|选项",
         note="CX8 仅允许 reserve/reference/需求分析/双镜像基线语境，现役 = 4×CX7"),
    dict(id="R5", dec="C12", field="功耗口径", severity="MED",
         pattern=r"77\s*kW|4\.8\s*kW",
         exempt=r"GPU 域|口径|近似|机电|精确值|inrush|裁决|证据|矛盾描述|回写|门禁|grep|基准|来源|差异|注",
         note="77kW/4.8kW 裸用须带口径注（GPU 域近似/机电口径）；ASCII 图内注释亦须注"),
    dict(id="R6", dec="C11", field="参考平台混入", severity="MED",
         pattern=r"dayu-klx|配对直联|32 根 DAC",
         exempt=r"reference|not-this-project|参考平台|非本项目|参考|证据|裁决|门禁|禁止|矛盾描述|grep|作废|改判|假设|材料|信源",
         note="dayu-klx 配对直联仅允许参考平台标注语境；NVL72 行业参照不作门禁（INFO 见 R14）"),
    # ── 拓扑/验证域（C28-C32 §7） ───────────────────────────────────────
    dict(id="R7", dec="C28", field="Rail 语义", severity="HIGH",
         pattern=r"每 POD 4 Rail|4-Rail|16\s*\*\s*\(Rail-1\)|64\s*\*\s*\(POD-1\)",
         exempt=r"取代|作废|旧|历史|已被.*取代|4-Rail 源文档|08-20|证据|裁决|禁止回退|残留|门禁|索引越界|引用作废|来源|零命中|model|模型|node index|节点编号",
         note="4-Rail 节点分组旧语义，现行 = 2 rail × 2 卡（端口分组）"),
    dict(id="R8", dec="C29", field="生命周期命名", severity="MED",
         pattern=r"生命周期.*P0|发现.*P0|P0~P3|P0-P3",
         exempt=r"F0~F3|上电|P0-P7|P4\.5|P5\.5|P6\.5|证据|裁决|门禁|替换|残留|作废|缺陷|分诊|优先级|评审|分级|严重度",
         note="发现生命周期应 F0~F3，禁止 P 前缀（与上电阶段撞名）；缺陷优先级/评审分级 P0-P3 不属此管辖"),
    dict(id="R9", dec="C30", field="硬编码邻接", severity="MED",
         pattern=r"rack_adj\s*=\s*\{|hardcod|硬编码.*邻接|硬编码.*adj",
         exempt=r"删除|去硬编码|不再|作废|裁决|证据|禁止|门禁|数据源",
         note="邻接矩阵必须读 inter-rack topology matrix，禁止硬编码"),
    dict(id="R10", dec="C28-C32", field="CX7 角色限定", severity="INFO",
         pattern=r"\bCX7\b(?!.*(?:SO|SCH|角色|现役|Scale-Out|调度))",
         exempt=r"门禁|grep|证据|裁决|禁止|规则|示例|changelog|版本",
         note="C28-C32 门禁 4：提及 CX7 应限定角色（SO/SCH）；纯提示供人工抽查（v1.0 判定噪音大，维持降级）"),
    # ── 台账/口径（08-28 审计报告新增） ─────────────────────────────────
    dict(id="R11", dec="C6", field="台账计数", severity="HIGH",
         pattern=r"\b2609\b",
         exempt=r"旧|作废|历史|残留|2609→2612|→2612|已执行|回写|门禁|n 语义未定义|为什么|解释|v1\.1 台账|复验",
         note="台账总数权威 = 2612（C6 修复后），2609 残留应消除；带 v1.1 版本限定的历史引用豁免"),
    dict(id="R12", dec="C21", field="PXE 服务承载", severity="MED",
         pattern=r"PXE 镜像服务",
         exempt=r"管理服务器存储网口|部署节点|承载实体|证据|裁决|回写",
         note="PXE 镜像服务须点名承载实体（管理服务器存储网口）"),
    dict(id="R13", dec="C32", field="版本元数据", severity="MED",
         pattern=r"(?!)", exempt=r"",
         note="头部版本行 = changelog 最新条目（独立实现 check_version_metadata）"),
    dict(id="R14", dec="C11", field="NVL72 行业参照", severity="INFO",
         pattern=r"NVL72",
         exempt=r"对照|对比|行业|参考|引用|来源|佐证|实证|类|官方|标准|调研|笔记|GB300|替代",
         note="NVL72 行业参照为 INFO 提示（项目对象表混入时才升级）——仅供人工抽查"),
    # ── v2.0 新增语义规则（08-28 全面版） ───────────────────────────────
    dict(id="R15", dec="C6", field="存储台数 9 台残留", severity="MED",
         pattern=r"存储[^。\n]{0,20}(9 台|9台)|9 台.*存储|9台.*存储",
         exempt=r"旧残留|旧口径|作废|取代|历史|参考|证据|裁决|回写|已执行|门禁|3 台",
         note="C6 权威 = 存储服务器 3 台（G3.5×2+G4×1），9 台为旧残留须带标注"),
    dict(id="R16", dec="C5", field="兜底 IP 去柜号", severity="MED",
         pattern=r"10\.1\.[0-9]+\.255|10\.1\.<R>\.255|255\.<96\+slot>",
         exempt=r"取代|作废|旧|历史|去柜号|统一|权威|M11|证据|裁决|回写|已执行|门禁",
         note="C5 权威 = 兜底 IP `10.1.255.<96+slot>`（去柜号），带柜号兜底为旧口径"),
    dict(id="R17", dec="C10", field="CX8 预留正向提示", severity="INFO",
         pattern=r"\bCX8\b",
         exempt=r"预留|reserve|reference|future|参考|取代|作废|需求|客户|变更|直连|预算|downgraded|双镜像|双基线|评估|候选|选项|证据|裁决|门禁|grep|✅|矛盾描述|回写|已执行|禁止",
         note="正向提示：CX8 出现但行内无预留/参考等限定词，供人工判断是否现役语境"),
    # R18 预留位（功耗 4.8kW 已并入 R5）；R19 预留位（关键参数表并入 R20 术语表）
]

# ─────────────────────────── 术语表（R20，配置驱动） ───────────────────────────
# {canonical 权威写法, variants 违规变体正则列表, note}
# 检测策略（v2.0 降噪）：文档级混用检测——同文档内权威写法与变体并存才报（每文档每术语 ≤1 条）；
# 全小写统一风格（无权威写法出现）不算违规（中文文档常规可读写法）。
# 匹配时排除权威写法本身（变体正则可能误匹配权威写法，用文本比对区分）。
TERMS = [
    dict(canonical="Scale-Out", variants=[r"scale-out", r"scale out", r"Scale Out", r"ScaleOUT", r"scaleout"],
         note="网卡/网络域术语统一 Scale-Out（C10/C28 锚点表写法）"),
    dict(canonical="Scale-Up", variants=[r"scale-up", r"scale up", r"Scale Up", r"ScaleUP", r"scaleup"],
         note="与 Scale-Out 对称，统一 Scale-Up"),
    dict(canonical="GPU 域", variants=[r"GPU域", r"gpu 域"],
         note="功耗口径语境统一『GPU 域』（C12 锚点表写法）"),
    dict(canonical="circuit-id", variants=[r"circuit id", r"circuit_id", r"Circuit-ID"],
         note="DHCP option 82 字段名统一 circuit-id（C4/C25 锚点表写法）"),
    dict(canonical="OOB-ACC", variants=[r"OOB ACC", r"OOB_ACC", r"oob-acc"],
         note="带外管理接入控制器统一 OOB-ACC（C8/C15 锚点表写法）"),
    dict(canonical="FSW", variants=[r"Fabric Switch", r"fabric-switch", r"FabricSwitch"],
         note="交换设备统一缩写 FSW（C14 锚点表：12 FSW/柜×8=96）"),
    dict(canonical="inter-rack topology matrix", variants=[r"interrack", r"inter rack topology", r"Golden Topology"],
         note="期望邻居矩阵数据源统一 inter-rack topology matrix（C30 锚点表）"),
    dict(canonical="2 rail × 2 卡", variants=[r"2 rail\s*x\s*2 卡", r"2rail", r"2 rail×2卡"],
         note="Rail 语义权威表述（C28 锚点表：端口分组 2 rail × 2 卡）"),
]


def check_terms(path: Path) -> list:
    """R20 术语表文档级混用检测：同文档权威写法 + 变体并存 → 1 条/术语/文档。"""
    issues = []
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return issues
    # 排除代码块内容（脚本输出/命令示例内的术语不计）
    lines = text.split("\n")
    body, in_code = [], False
    for ln in lines:
        if ln.strip().startswith("```"):
            in_code = not in_code
            continue
        if not in_code:
            body.append(ln)
    body_text = "\n".join(body)

    for term in TERMS:
        canon = term["canonical"]
        canon_pat = re.compile(re.escape(canon))
        var_pat = re.compile("|".join(term["variants"]), re.IGNORECASE)
        canon_hit = canon_pat.search(body_text)
        var_hits = []
        for m in var_pat.finditer(body_text):
            seg = m.group(0)
            # 变体正则可能误匹配权威写法（大小写不敏感）：文本与权威写法相同 → 跳过
            if seg.lower() == canon.lower():
                continue
            var_hits.append(m)
        if canon_hit and var_hits:
            # 定位第一条变体的行号
            line_no = body_text[:var_hits[0].start()].count("\n") + 1
            issues.append(dict(
                id="R20", dec="GOV", field="术语表", severity="LOW",
                file=str(path.relative_to(KB)), line=line_no,
                text=f"术语混用: 权威『{canon}』与变体『{var_hits[0].group(0)}』同文档并存（变体 {len(var_hits)} 处）",
                note=term["note"],
            ))
    return issues

# ─────────────────────────── 版本元数据检查（C32） ───────────────────────────
VERSION_HEAD_RE = re.compile(r"版本[^v\d\n]{0,8}[:：]\s*v?(\d+\.\d+)")
CHANGELOG_RE = re.compile(r"^\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*v?(\d+\.\d+)\s*\|", re.M)

# 元文档（记录层）：裁决/治理/审计/登记表——使命即记录旧口径作证，取证引用豁免
# 治理方案 §5.2 原则：SSOT 锚点表=投影视图；回写目标是业务文档，记录层不判 FAIL
META_RE = re.compile(r"rectification|governance|audit|register|decision", re.IGNORECASE)
# v2.0：元文档除 R13/R14 外，仍执行结构规则（链接/命名/表格）——结构问题是普适的
META_RULES_IDS = {"R13", "R14"}           # 语义规则：记录层只跑版本+INFO
STRUCT_RULES_IDS = {"R21", "R22", "R23", "R24", "R25"}  # 结构规则：全量执行

# 回写状态核验目标（R26/R27，状态类输出，非正则门禁）
REWRITE_TARGETS = {
    "R26": dict(dec="C17-C20", field="functional 升版 v1.2",
                file="2026-08-26-supernode-power-on-functional-verification-deep-analysis.md",
                expect_version=(1, 2),
                note="C17 裁决要求 functional-verification 升版 v1.2（A1-A12 十二处章节级修改）"),
    "R27": dict(dec="C21-C24", field="PXE 回写 10 处",
                file="2026-08-27-pxe-installation-chain-consistency-rectification-c21-c24-deep-analysis.md",
                note="C21-C24 裁决回写清单 10 处执行状态（需人工核验，脚本仅定位）"),
}


def parse_version(s: str):
    return tuple(int(x) for x in s.split("."))


def get_version_meta(path: Path):
    """返回 (head_version, changelog_versions) 或 (None, [])"""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return None, []
    head_m = VERSION_HEAD_RE.search(text[:1200])
    head_ver = parse_version(head_m.group(1)) if head_m else None
    ch_vers = [parse_version(m.group(2)) for m in CHANGELOG_RE.finditer(text)]
    return head_ver, ch_vers


def check_version_metadata(path: Path) -> list:
    """头部版本行 == changelog 最新条目版本（C32 门禁 5）。"""
    issues = []
    head_ver, ch_vers = get_version_meta(path)
    if not head_ver or not ch_vers:
        return issues
    latest = max(ch_vers)
    if head_ver != latest:
        issues.append(dict(
            id="R13", dec="C32", field="版本元数据", severity="MED",
            file=str(path.relative_to(KB)), line=1,
            text=f"头部版本 v{'.'.join(map(str, head_ver))} ≠ changelog 最新 v{'.'.join(map(str, latest))}",
            note="头部版本行必须 = changelog 最新条目版本",
        ))
    return issues


# ─────────────────────────── 结构规则（v2.0 新增） ───────────────────────────
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def check_links(path: Path) -> list:
    """R21 交叉链接死链：相对路径 resolve 到 knowledge/ 下验证存在性。"""
    issues = []
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return issues
    base = path.parent
    for i, line in enumerate(text.split("\n"), 1):
        for m in LINK_RE.finditer(line):
            target = m.group(1).strip()
            # 跳过外部链接 / 纯锚点 / 图片 / 空
            if not target or target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            # 去 # 锚点后再解析路径（xxx.md#section → xxx.md）
            target = target.split("#")[0].strip()
            if not target:
                continue
            if target.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".svg")):
                continue
            # 解析相对路径：基准 = 文档所在目录，向上可出 knowledge/（禁止）
            try:
                resolved = (base / target).resolve()
            except Exception:
                continue
            try:
                resolved.relative_to(KB)
            except ValueError:
                issues.append(dict(
                    id="R21", dec="GOV", field="交叉链接越界", severity="MED",
                    file=str(path.relative_to(KB)), line=i,
                    text=f"链接 {target} 解析到 knowledge/ 之外", note="内部相对链接必须指向 knowledge/ 内",
                ))
                continue
            if not resolved.exists():
                issues.append(dict(
                    id="R21", dec="GOV", field="交叉链接死链", severity="MED",
                    file=str(path.relative_to(KB)), line=i,
                    text=f"死链: {target} → {resolved.relative_to(KB)} 不存在",
                    note="内部交叉链接指向的文件不存在",
                ))
    return issues


def check_metadata(path: Path) -> list:
    """R22 头部元数据三要素：版本行 / TOC / changelog。"""
    issues = []
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return issues
    name = path.name
    if not re.match(r"\d{4}-\d{2}-\d{2}-", name):
        return issues  # 非日期前缀文档跳过
    n_lines = text.count("\n")
    if n_lines < 40:
        return issues  # 短文跳过
    head_ver, ch_vers = get_version_meta(path)
    if head_ver is None:
        # 宽松判定：头部 1200 字符内存在 vX.Y 版本标记（兼容 版本=/文件状态= 等格式）
        if not re.search(r"\bv\d+\.\d+\b", text[:1200]):
            issues.append(dict(id="R22", dec="GOV", field="头部元数据", severity="MED",
                               file=str(path.relative_to(KB)), line=1,
                               text="头部缺少版本标记（> 版本: vX.Y / 版本=vX.Y）", note="规格文档头部应含版本行"))
    if "[TOC]" not in text and "## 📑 目录" not in text and "## 目录" not in text:
        issues.append(dict(id="R22", dec="GOV", field="头部元数据", severity="LOW",
                           file=str(path.relative_to(KB)), line=1,
                           text="缺少目录标记（[TOC] 或 ## 📑 目录 均可）", note="深度文档应含目录（>100 行强制）"))
    if not ch_vers:
        issues.append(dict(id="R22", dec="GOV", field="头部元数据", severity="LOW",
                           file=str(path.relative_to(KB)), line=1,
                           text="缺少 changelog 变更记录表", note="深度文档应含变更记录表"))
    return issues


def check_filename(path: Path) -> list:
    """R23 文件命名规范：YYYY-MM-DD-英文小写-连字符.md。"""
    issues = []
    name = path.stem
    if not re.match(r"^\d{4}-\d{2}-\d{2}-[a-z0-9-]+$", name):
        issues.append(dict(id="R23", dec="GOV", field="文件命名规范", severity="MED",
                           file=str(path.relative_to(KB)), line=0,
                           text=f"文件名不符合 YYYY-MM-DD-英文小写-连字符 规范: {path.name}",
                           note="2026-08-03 文件名规范（kb-index-check C8）"))
    return issues


def check_tables(path: Path) -> list:
    """R24 管道表格格式：表头行后须紧跟 |--- 分隔行（降噪版：排除代码块/ASCII 图）。"""
    issues = []
    try:
        lines = path.read_text(encoding="utf-8").split("\n")
    except Exception:
        return issues
    in_code = False
    prev_pipe = False  # 上一行是管道行（表体中间行跳过）
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("```"):
            in_code = not in_code
            prev_pipe = False
            continue
        if in_code:
            prev_pipe = False
            continue
        if s.startswith("|") and "|" in s[1:]:
            # 分隔行本身 / 表体行（上一行也是管道行）→ 跳过
            if re.search(r"^\|[\s\-:|]*\|$", s) or prev_pipe:
                prev_pipe = True
                continue
            # 疑似 ASCII 图（含 -> + < > 等元素）→ 跳过
            if re.search(r"[-+<>→↑↓]", s):
                prev_pipe = False
                continue
            nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
            if nxt.startswith("|") and re.search(r"^\|[\s\-:|]*\|$", nxt):
                prev_pipe = True  # 表头后正常分隔行
                continue
            # 管道行但下一行不是分隔行 → 疑似表头缺分隔行
            if len(issues) < 60:  # 全库限流
                issues.append(dict(id="R24", dec="GOV", field="表格格式", severity="LOW",
                                   file=str(path.relative_to(KB)), line=i + 1,
                                   text="疑似表格表头缺 |--- 分隔行（或为列表/ASCII 图误判）",
                                   note="表格规范：表头后紧跟分隔行"))
            prev_pipe = False
        else:
            prev_pipe = False
    return issues


# 高频被引用文档的版本引用漂移核验（R25）：引用方标注版本 vs 目标 changelog 最新
# key = 文件名关键字，value = 目标文档名（完整）
VERSION_REF_TARGETS = [
    ("power-on-sequence", "2026-08-25-supernode-power-on-sequence-ip-auto-config-deep-analysis.md"),
    ("ip-scripts", "2026-08-26-supernode-ip-allocation-detailed-scripts-verification-deep-analysis.md"),
    ("interconnect", "2026-08-26-supernode-interconnect-topology-discovery-deep-analysis.md"),
]


def check_version_refs(path: Path) -> list:
    """R25 跨文档版本引用漂移：引用方标注的版本号 vs 目标文档 changelog 最新。
    记录层（裁决/审计/治理）豁免——其使命即记录当时引用的历史版本作证。"""
    issues = []
    if META_RE.search(path.name):
        return issues
    if "power-on-sequence" in path.name or "ip-scripts" in path.name or "interconnect" in path.name:
        return issues  # 自身是被引用方，跳过
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return issues
    for kw, target_name in VERSION_REF_TARGETS:
        if kw not in text:
            continue
        target_path = KB / "02_rd" / "02_project" / "01_superpod" / target_name
        if not target_path.exists():
            continue
        _, ch_vers = get_version_meta(target_path)
        if not ch_vers:
            continue
        latest = max(ch_vers)
        # 找引用上下文中的版本号（vX.Y，距关键字 ±60 字符内）
        for m in re.finditer(re.escape(kw), text):
            ctx = text[max(0, m.start() - 60):m.end() + 80]
            ref_vers = set(re.findall(r"v(\d+\.\d+)", ctx))
            for rv in ref_vers:
                if parse_version(rv) != latest:
                    line = text[:m.start()].count("\n") + 1
                    issues.append(dict(
                        id="R25", dec="C32", field="版本引用漂移", severity="MED",
                        file=str(path.relative_to(KB)), line=line,
                        text=f"引用 {kw} 标注 v{rv}，目标文档 changelog 最新 v{'.'.join(map(str, latest))}",
                        note="跨文档引用版本应指向目标文档当前版本（B2 模式防复发）",
                    ))
    return issues[:20]


def check_rewrite_status(scopes: list) -> list:
    """R26/R27 回写状态核验：目标文档是否达到裁决要求的版本/状态（跨 scope 去重）。"""
    issues = []
    for rid, spec in REWRITE_TARGETS.items():
        fp = None
        for scope in scopes:
            cand = scope / spec["file"]
            if cand.exists():
                fp = cand
                break
        if fp is None:
            issues.append(dict(id=rid, dec=spec["dec"], field=spec["field"], severity="HIGH",
                               file=str(spec["file"]), line=0,
                               text=f"目标文档在扫描范围内不存在: {spec['file']}", note=spec["note"]))
            continue
        head_ver, ch_vers = get_version_meta(fp)
        if "expect_version" in spec:
            ok = head_ver is not None and head_ver >= spec["expect_version"]
            issues.append(dict(
                id=rid, dec=spec["dec"], field=spec["field"],
                severity="INFO" if ok else "HIGH",
                file=str(spec["file"]), line=1,
                text=(f"✅ 头部版本 v{'.'.join(map(str, head_ver))} ≥ v{'.'.join(map(str, spec['expect_version']))} 升版已执行"
                      if ok else f"头部版本 {head_ver and 'v'+'.'.join(map(str, head_ver)) or '缺失'} < v{'.'.join(map(str, spec['expect_version']))}，C17 升版未执行"),
                note=spec["note"]))
        else:
            issues.append(dict(id=rid, dec=spec["dec"], field=spec["field"], severity="INFO",
                               file=str(spec["file"]), line=1,
                               text="C21-C24 回写 10 处执行状态需人工核验（脚本仅定位目标）", note=spec["note"]))
    return issues


# ─────────────────────────── 扫描主逻辑 ───────────────────────────
def scan_file(path: Path, rules: list, run_structure: bool = True) -> list:
    """返回 issues。元文档（记录层）豁免取证引用，只跑 R13/R14 + 结构规则。"""
    issues = []
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        return [dict(id="ERR", dec="-", field="读取失败", severity="HIGH",
                     file=str(path), line=0, text=str(e), note="")]

    m = re.match(r"(\d{4}-\d{2}-\d{2})", path.name)
    fdate = m.group(1) if m else ""
    is_meta = bool(META_RE.search(path.name))

    lines = text.split("\n")
    for rule in rules:
        if is_meta and rule["id"] not in META_RULES_IDS:
            continue  # 记录层取证引用豁免
        pat = re.compile(rule["pattern"], re.IGNORECASE)
        ex_re = re.compile(rule["exempt"], re.IGNORECASE) if rule["exempt"] else None
        for i, line in enumerate(lines, 1):
            if not pat.search(line):
                continue
            if ex_re and ex_re.search(line):
                continue  # 行级豁免（旧口径声明等合法语境）
            issues.append(dict(
                id=rule["id"], dec=rule["dec"], field=rule["field"],
                severity=rule["severity"], file=str(path.relative_to(KB)),
                line=i, text=line.strip()[:140], note=rule["note"], fdate=fdate,
            ))

    # 版本元数据（R13）
    issues.extend(check_version_metadata(path))

    # 术语表（R20，文档级混用检测）
    issues.extend(check_terms(path))

    # 结构规则（全量执行，含元文档）
    if run_structure:
        issues.extend(check_links(path))
        issues.extend(check_metadata(path))
        issues.extend(check_filename(path))
        issues.extend(check_tables(path))
        issues.extend(check_version_refs(path))

    return issues


def main():
    ap = argparse.ArgumentParser(description="超节点规格一致性门禁扫描器 v2.0（全面版）")
    ap.add_argument("--since", type=str, default=None,
                    help="仅扫描文件名日期 >= 该日期（YYYY-MM-DD），如 2026-08-25")
    ap.add_argument("--rules", type=str, default=None,
                    help="逗号分隔的规则 ID 子集，如 'R4,R13,R21'")
    ap.add_argument("--exclude", type=str, default=None,
                    help="文件名 glob 豁免（可逗号分隔多个），如 '*.audit*.md'")
    ap.add_argument("--json", action="store_true", help="JSON 输出")
    ap.add_argument("--paths", type=str, default=None,
                    help="覆盖默认扫描目录（逗号分隔，相对 knowledge/ 的路径）")
    ap.add_argument("--terms", action="store_true", help="仅跑术语表规则 R20")
    ap.add_argument("--list", action="store_true", help="列出全部规则说明")
    args = ap.parse_args()

    if args.list:
        print(f"语义规则 {len(RULES)} 条 + 术语表 {len(TERMS)} 条 + 结构规则 5 条 + 回写状态 2 条:")
        for r in RULES:
            print(f"  {r['id']} [{r['severity']:5s}] {r['dec']} {r['field']} — {r['note'][:60]}")
        for t in TERMS:
            print(f"  R20 [{t['canonical']}] 变体={t['variants']} — {t['note'][:50]}")
        for rid, spec in REWRITE_TARGETS.items():
            print(f"  {rid} [{spec['dec']}] {spec['field']} — {spec['note'][:60]}")
        print("  R21 [GOV] 交叉链接死链/越界 — 结构规则")
        print("  R22 [GOV] 头部元数据三要素（版本/TOC/changelog） — 结构规则")
        print("  R23 [GOV] 文件命名规范 — 结构规则")
        print("  R24 [GOV] 管道表格格式 — 结构规则")
        print("  R25 [C32] 跨文档版本引用漂移 — 结构规则")
        return

    if args.paths:
        scopes = [KB / p for p in args.paths.split(",")]
    else:
        scopes = DEFAULT_SCOPES

    if args.terms:
        rules = [r for r in RULES if r["id"] in ("R10", "R17", "R14")]  # INFO 提示类仍跑
        run_structure = False
    else:
        rules = RULES
        run_structure = True
    if args.rules:
        want = set(x.strip() for x in args.rules.split(","))
        rules = [r for r in RULES if r["id"] in want]
        run_structure = any(x in want for x in STRUCT_RULES_IDS) or args.terms
    since = date.fromisoformat(args.since) if args.since else None
    excludes = [g.strip() for g in (args.exclude or "").split(",") if g.strip()]

    files = []
    for scope in scopes:
        if not scope.exists():
            print(f"[warn] 目录不存在: {scope}", file=sys.stderr)
            continue
        files.extend(p for p in scope.rglob("*.md"))
    files = sorted(set(files))

    if since:
        files = [p for p in files
                 if (re.match(r"(\d{4}-\d{2}-\d{2})", p.name))
                 and date.fromisoformat(re.match(r"(\d{4}-\d{2}-\d{2})", p.name).group(1)) >= since]

    all_issues = []
    meta_exempt = 0
    for f in files:
        if any(fnmatch.fnmatch(f.name, g) for g in excludes):
            continue
        issues = scan_file(f, rules, run_structure)
        all_issues.extend(issues)
        if META_RE.search(f.name):
            meta_exempt += 1

    # 回写状态核验（R26/R27，全量执行）
    all_issues.extend(check_rewrite_status(scopes))

    # 汇总
    by_rule = defaultdict(list)
    for it in all_issues:
        by_rule[it["id"]].append(it)

    # 默认隐藏 INFO 级（R10/R14/R17 等提示类），--rules 指定时显示
    hide_info = not args.rules

    if args.json:
        print(json.dumps(dict(
            tool_version="2.0",
            scanned_files=len(files),
            scanned_dirs=[str(s.relative_to(KB)) for s in scopes],
            since=args.since,
            total_issues=len(all_issues),
            rules_used=[r["id"] for r in rules] if not args.terms else ["R10", "R14", "R17", "R20"],
            issues=all_issues,
        ), ensure_ascii=False, indent=1))
        return

    print(f"═══ consistency-scan v2.0 ═══ 扫描 {len(files)} 篇文档 | 规则 {len(rules)}+{len(TERMS)}+结构5+状态2 | since={args.since or 'all'}")
    print(f"扫描范围: {', '.join(str(s.relative_to(KB)) for s in scopes)} | 元文档(记录层) {meta_exempt} 篇")
    for rid in sorted(by_rule):
        items = by_rule[rid]
        r = next((x for x in rules if x["id"] == rid), None)
        if r is None:
            r = {"id": rid, "severity": "?", "field": rid, "dec": "-", "note": ""}
        if hide_info and r["severity"] == "INFO":
            continue
        print(f"\n── {rid} [{r['severity']}] {r['field']} ({r['dec']}) — {len(items)} 命中")
        for it in items[:12]:
            print(f"   {it['file']}:{it['line']}  {it['text'][:90]}")
        if len(items) > 12:
            print(f"   ... 另有 {len(items)-12} 处")
    fail = [x for x in all_issues if x["severity"] not in ("INFO", "LOW")]
    print(f"\n═══ 总计 {len(all_issues)} 处命中（FAIL {len(fail)} 处 + LOW/INFO 提示 {len(all_issues)-len(fail)} 处）═══")
    sev = defaultdict(int)
    for it in all_issues:
        sev[it["severity"]] += 1
    print("  级别分布: " + ", ".join(f"{k}={v}" for k, v in sorted(sev.items())))
    print("  提示: HIGH/MED = 待回写 checklist；LOW/INFO = 提示项人工确认；R26/R27 = 回写状态")


if __name__ == "__main__":
    main()
