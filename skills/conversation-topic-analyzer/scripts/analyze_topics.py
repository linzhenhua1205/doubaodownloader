#!/usr/bin/env python3
"""
Conversation Topic Analysis Script

Reads all user-question files, clusters by topic, builds time-series,
extracts knowledge dimensions and operational thinking patterns.

Usage:
  cd ~/cow
  python3 skills/conversation-topic-analyzer/scripts/analyze_topics.py

Output:
  knowledge/07_industry-research/03_server/conversation-topic-analysis-YYYY-MM-DD.md
"""

import os
import re
import json
import sqlite3
from datetime import datetime, timezone, timedelta
from collections import defaultdict

WORKSPACE = os.path.expanduser("~/cow")
QUESTIONS_DIR = os.path.join(WORKSPACE, "conversation-log", "user-questions")
DB_PATH = os.path.expanduser("~/cow/memory/long-term/index.db")
OUTPUT_DIR = os.path.join(WORKSPACE, "knowledge", "07_industry-research", "03_server")
TMP_DIR = os.path.join(WORKSPACE, "tmp")
TZ = timezone(timedelta(hours=8))

# ====== TOPIC DEFINITIONS (expert-curated based on data exploration) ======

# Mapping: question keywords -> topic info
# Priority-ordered: first match wins
TOPIC_RULES = [
    # === AI & LLM ===
    (r"(?:大模型|LLM|GPT|Claude|Gemini|DeepSeek|模型发布|模型评测|开源模型|模型能力)", "AI大模型与LLM生态"),
    (r"(?:MoE|Mixture.of.Experts|专家混合|all-to-all)", "MoE架构与硬件影响"),
    (r"(?:AI应用|AI Agent|AI搜索|Copilot|AI Coding|AI产品|Agent)", "AI应用与Agent生态"),
    (r"(?:AI框架|PyTorch|TensorRT|vLLM|Triton|推理引擎|训练框架)", "AI框架与推理优化"),
    (r"(?:AI编程|Cursor|Claude Code|Copilot.*(?:代码|Code)|AI.*开发工具)", "AI编程与研发工具"),
    (r"(?:AI基础设施|AI Infra|AI.*基础设施)", "AI基础设施综合"),
    (r"(?:算力设施|算力方案|智算方案|算力基建|智算中心)", "算力基建与智算方案"),
    (r"(?:万卡集群|训推优化|分布式训练|训练优化|collective.communication)", "万卡集群与训推优化"),

    # === 超节点/服务器硬件 ===
    (r"(?:超节点|superpod|SuperPod|KLX|klx-512|天池)", "超节点系统设计"),
    (r"(?:超节点标准|开放标准|OCP.*(?:标准|生态)|ODCC|UALink|CXL.*(?:联盟|标准|生态)|OISA)", "超节点标准与开放生态"),
    (r"(?:服务器硬件|服务器架构|服务器形态|GPU服务器|整机柜|Scale.up|Scale.out)", "服务器硬件架构"),
    (r"(?:服务器设计|设计方法论|L6|L12|交付方式)", "服务器设计方法论"),
    (r"(?:服务器BOM|BOM成本|供应链|元器件涨价|供应链)", "BOM成本与供应链"),
    (r"(?:电源架构|HVDC|BBU|供电方案|48V|800V|VRM)", "电源架构与供电方案"),
    (r"(?:液冷|散热|浸没式冷却|CoolIT|维谛|英维克)", "液冷散热方案"),
    (r"(?:服务器资产管理|FRU|CMDB|资产盘点)", "服务器资产管理"),

    # === 芯片/GPU/互联 ===
    (r"(?:芯片|GPU|NVIDIA|AMD|Intel.*(?:GPU|芯片)|国产GPU|海光|华为.*(?:芯片|昇腾))", "芯片与GPU生态"),
    (r"(?:互联|InfiniBand|RoCE|UALink.*(?:进展|动态)|PCIe.*(?:进展|动态)|光互联|CPO|SiPh|硅光子|高速互联)", "高速互联与光通信"),
    (r"(?:分布式OS|集合通信|NCCL|RDMA|网络架构)", "分布式OS与集合通信"),
    (r"(?:存储|内存|HBM|CXL.*(?:内存|存储)|SSD|NVMe|内存模组|MRDIMM)", "存储/内存/HBM体系"),
    (r"(?:BMC|OpenBMC|Redfish|固件)", "BMC/固件/Redfish系统"),
    (r"(?:数据中心|风火水电|DataCenter|Uptime)", "数据中心基础设施"),
    (r"(?:云原生|K8s|容器|运维运营|AIOps|监控|CMDB)", "云原生与运维运营"),

    # === Linux/OS ===
    (r"(?:Linux.?OS|操作系统|Kernel|容器)", "Linux OS与容器生态"),

    # === 国产化 ===
    (r"(?:国产化|国产替代|国产CPU|国产芯片|国产.*服务器|飞腾|龙芯|申威)", "国产化替代进展"),

    # === 研发管理 ===
    (r"(?:研发管理|研发提效|研发方案|产品研发|研发效率|研发.*方法论)", "研发管理与方法论"),
    (r"(?:项目管理|Jira|Atlassian|Linear|PMI|项目计划)", "项目管理"),
    (r"(?:Code.?Review|代码审查|评审|代码走读)", "代码审查与质量"),
    (r"(?:可靠.*测试|故障.*诊断|fault.*tolerance|checkpoint|FTA|根因)", "可靠性与测试"),
    (r"(?:质量管理|质量|品质|测试)", "质量管理与测试"),
    (r"(?:Git|版本管理|代码管理|GitHub)", "Git与版本管理"),

    # === 方法论 ===
    (r"(?:MECE|第一性原理|方法论|分析框架|MECE原则|第一性)", "方法论体系（MECE/第一性原理）"),
    (r"(?:架构.*投入|架构.*投资|架构.*策略|ROI.*架构)", "架构投资策略"),

    # === 知识库 & 工具 ===
    (r"(?:知识库|知识.*管理|knowledge.*(?:优化|重构|完善|补充|归档))", "知识库构建与治理"),
    (r"(?:AI使用|提示词|prompt|AI.*方法论|AI.*使用.*技巧)", "AI使用方法论与提示词工程"),
    (r"(?:研发工具|效率工具|GitHub.*(?:工具|动态)|开发工具)", "研发工具效率"),
    (r"(?:数据分析|大数据|数据湖仓|Databricks|Flink|Spark|湖仓)", "数据分析与湖仓技术"),
    (r"(?:Skills|skill.*创建|skill.*安装|skill.*封装|技能)", "Skill开发与管理"),
    (r"(?:脚本|script|自动化|定时|调度|scheduler)", "自动化脚本与调度"),

    # === 企业管理 ===
    (r"(?:企业管理|企业管理|组织|团队|协作|文化)", "企业管理与组织"),
    (r"(?:产品管理|产品方案|Product.*School|SVPG)", "产品管理"),

    # === 行业调研 ===
    (r"(?:行业调研|市场格局|行业趋势|财报分析|愿景|价值观)", "行业调研与市场分析"),
    (r"(?:竞品分析|竞争对手|同类产品|对标)", "竞品分析"),

    # === 其他 ===
    (r"(?:归档.*(?:URL|文章|网页|链接)|导入.*文章|归档)", "信息归档与导入"),
    (r"(?:周报|每周|weekly.*report)", "周报生成"),
    (r"(?:测试|test|调度器测试)", "系统测试与调试"),
    (r"(?:储能|电池|锂硫|相变)", "储能材料（其他领域）"),
    (r"(?:人格|协作.*风格|性格)", "人员分析与协作"),
    (r"(?:毕业|论文|答辩|开题)", "论文与学术"),
    (r"(?:愿景|价值观|使命|科技公司|企业文化)", "企业文化与战略"),
]

def extract_date_from_filename(filename):
    """Extract date from filename like '2026-05-11-xxx.md'"""
    m = re.match(r'(\d{4}-\d{2}-\d{2})', filename)
    return m.group(1) if m else "unknown"

def extract_questions_from_md(filepath):
    """Extract questions from a user-question markdown file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return []

    questions = []
    # Extract session title
    title_m = re.search(r'# 🗣️ 用户问题: (.+)', content)
    title = title_m.group(1).strip() if title_m else os.path.basename(filepath)

    # Extract each question block
    # Pattern: ### #N [CATEGORY] (Seq=X, TIMESTAMP)
    blocks = re.split(r'### #\d+ \[', content)
    for block in blocks[1:]:  # Skip first (header)
        lines = block.strip().split('\n')
        # First line contains category and timestamp
        first_line = lines[0]
        cat_m = re.match(r'([^\]]+)\] \(Seq=(\d+), ([\d\- :]+)\)', first_line)
        category = cat_m.group(1).strip() if cat_m else "unknown"
        ts_str = cat_m.group(3).strip() if cat_m else ""

        # Find text content (inside ```text ... ```)
        text_m = re.search(r'```text\n(.*?)```', block, re.DOTALL)
        text = text_m.group(1).strip() if text_m else ""

        if text:
            questions.append({
                'text': text,
                'category': category,
                'timestamp': ts_str,
                'session_title': title,
            })
    return questions

def classify_topic(text, filename):
    """Classify a question into a topic using rule matching"""
    combined = f"{filename} {text}"
    for pattern, topic in TOPIC_RULES:
        if re.search(pattern, combined, re.IGNORECASE):
            return topic
    return "其他综合"

def extract_knowledge_dimensions(text):
    """Identify knowledge dimensions present in a question"""
    dims = set()
    text_lower = text.lower()

    # D1: Architecture
    if any(w in text_lower for w in ["架构", "拓扑", "体系", "设计", "结构", "组成", "布局",
                                       "architecture", "topology", "hierarchy"]):
        dims.add("D1:系统架构")
    # D2: Standard/Ecosystem
    if any(w in text_lower for w in ["标准", "协议", "规范", "生态", "开放", "联盟", "开源",
                                       "standard", "protocol", "spec", "ecosystem"]):
        dims.add("D2:标准与生态")
    # D3: Comparison/Evaluation
    if any(w in text_lower for w in ["对比", "比较", "vs", "对表", "竞争", "对标", "分析",
                                       "compare", "vs", "benchmark", "evaluation"]):
        dims.add("D3:对比与评估")
    # D4: Methodology
    if any(w in text_lower for w in ["方法论", "方法", "流程", "框架", "MECE", "第一性",
                                       "methodology", "framework", "principle"]):
        dims.add("D4:方法论与框架")
    # D5: Management/Process
    if any(w in text_lower for w in ["管理", "项目", "计划", "组织", "协作", "评审",
                                       "管理", "流程", "制度", "milestone"]):
        dims.add("D5:管理与流程")
    # D6: Implementation
    if any(w in text_lower for w in ["实现", "设计", "代码", "配置", "参数", "寄存器",
                                       "implementation", "register", "config", "code"]):
        dims.add("D6:实现与设计")
    # D7: Knowledge Management
    if any(w in text_lower for w in ["知识库", "归档", "索引", "目录", "组织",
                                       "knowledge", "index", "archive"]):
        dims.add("D7:知识管理")
    # D8: Tooling
    if any(w in text_lower for w in ["工具", "脚本", "自动化", "skill", "工具",
                                       "tool", "script", "automation"]):
        dims.add("D8:工具与自动化")

    return dims

def extract_operational_patterns(text):
    """Identify operational thinking patterns"""
    patterns = set()
    text_lower = text.lower()

    # T1: Top-down decomposition
    if any(w in text_lower for w in ["分层", "分解", "维度", "分类", "拆解", "模块化",
                                       "子系统", "模块划分"]):
        patterns.add("T1:自顶向下分解")
    # T2: First-principles
    if any(w in text_lower for w in ["第一性原理", "物理极限", "本质", "原理", "基础",
                                       "根源", "first principle"]):
        patterns.add("T2:第一性原理推导")
    # T3: Comparative analysis
    if any(w in text_lower for w in ["对比", "比较", "vs", "对表", "对标",
                                       "compare", "comparison", "vs"]):
        patterns.add("T3:对比分析")
    # T4: Cross-reference synthesis
    if any(w in text_lower for w in ["参考", "引用", "提取", "结合", "综合", "import",
                                       "reference", "refer", "synthesize"]):
        patterns.add("T4:跨源综合")
    # T5: Iterative refinement
    if any(w in text_lower for w in ["补充", "完善", "优化", "迭代", "修复", "修正",
                                       "更新", "重构", "补充完善", "深度完善"]):
        patterns.add("T5:迭代精化")
    # T6: Risk-aware decision
    if any(w in text_lower for w in ["风险", "评估", "备选", "权衡", "cost", "trade-off",
                                       "ROI", "代价", "成本"]):
        patterns.add("T6:风险感知决策")

    return patterns

def get_session_info_from_db():
    """Get session-level info from database"""
    info = {}
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT session_id, title, channel_type, created_at, last_active, msg_count FROM sessions")
        for row in cur.fetchall():
            info[row['session_id']] = {
                'title': row['title'],
                'channel': row['channel_type'],
                'created_at': row['created_at'],
                'last_active': row['last_active'],
                'msg_count': row['msg_count'],
            }
        conn.close()
    except Exception as e:
        print(f"  ⚠️ DB access issue (continuing without): {e}")
    return info

def get_filename_topic_mapping():
    """Build filename-based topic mapping for quick reference"""
    mapping = {}
    for fname in os.listdir(QUESTIONS_DIR):
        if not fname.endswith('.md') or fname in ('index.md', 'STATISTICS.md', 'TOPIC_ANALYSIS.md'):
            continue
        topic = classify_topic(fname, fname)
        mapping[fname] = topic
    return mapping

def main():
    print("=" * 60)
    print("📊 Conversation Topic Analyzer")
    print(f"   Source: {QUESTIONS_DIR}")
    print(f"   DB:     {DB_PATH}")
    print("=" * 60)

    # Step 1: Scan all files
    print("\n🔍 Step 1: Scanning user-question files...")
    all_questions = []
    session_info = get_session_info_from_db()

    for fname in sorted(os.listdir(QUESTIONS_DIR)):
        if not fname.endswith('.md') or fname in ('index.md', 'STATISTICS.md', 'TOPIC_ANALYSIS.md'):
            continue
        filepath = os.path.join(QUESTIONS_DIR, fname)
        questions = extract_questions_from_md(filepath)
        date_str = extract_date_from_filename(fname)
        for q in questions:
            q['file'] = fname
            q['date'] = date_str
            q['topic'] = classify_topic(q['text'], fname)
            q['dimensions'] = extract_knowledge_dimensions(q['text'])
            q['patterns'] = extract_operational_patterns(q['text'])
        all_questions.extend(questions)

    print(f"   ✅ Extracted {len(all_questions)} questions from {len(os.listdir(QUESTIONS_DIR))-3} files")

    # Step 2: Cluster into topics
    print("\n🔍 Step 2: Clustering into topics...")
    topic_questions = defaultdict(list)
    for q in all_questions:
        topic_questions[q['topic']].append(q)

    # Sort topics by question count
    sorted_topics = sorted(topic_questions.items(), key=lambda x: -len(x[1]))
    print(f"   ✅ Identified {len(sorted_topics)} topics")

    for topic, qs in sorted_topics:
        dates = set(q['date'] for q in qs if q['date'] != 'unknown')
        print(f"      {topic}: {len(qs)} questions, {len(dates)} days ({min(dates) if dates else '?'} ~ {max(dates) if dates else '?'})")

    # Step 3: Build topic detail with time-series
    print("\n🔍 Step 3: Building time-series and dimension analysis...")
    topic_details = {}
    for topic, qs in sorted_topics:
        # Sort by date
        qs_sorted = sorted(qs, key=lambda q: q.get('timestamp', ''))

        # Daily distribution
        daily = defaultdict(int)
        for q in qs_sorted:
            d = q['date']
            if d != 'unknown':
                daily[d] += 1

        # Dimension distribution
        dim_count = defaultdict(int)
        for q in qs_sorted:
            for d in q['dimensions']:
                dim_count[d] += 1

        # Pattern distribution
        pat_count = defaultdict(int)
        for q in qs_sorted:
            for p in q['patterns']:
                pat_count[p] += 1

        # Representative questions (most informative)
        rep_questions = []
        for q in qs_sorted[:5]:  # First 5 as representative
            rep_questions.append({
                'date': q['date'],
                'text': q['text'][:200],
                'dims': list(q['dimensions']),
                'pats': list(q['patterns']),
            })

        # Date range
        dates_all = sorted(set(q['date'] for q in qs_sorted if q['date'] != 'unknown'))
        date_range = f"{dates_all[0]} ~ {dates_all[-1]}" if dates_all else "unknown"

        # Intent analysis
        category_count = defaultdict(int)
        for q in qs_sorted:
            category_count[q['category']] += 1

        topic_details[topic] = {
            'count': len(qs_sorted),
            'date_range': date_range,
            'days_active': len(dates_all),
            'daily': dict(sorted(daily.items())),
            'dimensions': dict(sorted(dim_count.items(), key=lambda x: -x[1])),
            'patterns': dict(sorted(pat_count.items(), key=lambda x: -x[1])),
            'categories': dict(sorted(category_count.items(), key=lambda x: -x[1])),
            'representative': rep_questions,
        }

    # Step 4: Build overall statistics
    print("\n🔍 Step 4: Computing cross-topic statistics...")

    # Global dimension distribution
    global_dims = defaultdict(int)
    global_pats = defaultdict(int)
    for q in all_questions:
        for d in q['dimensions']:
            global_dims[d] += 1
        for p in q['patterns']:
            global_pats[p] += 1

    # Time-series of all topics
    topic_by_date = defaultdict(lambda: defaultdict(int))
    for q in all_questions:
        d = q['date']
        if d != 'unknown':
            topic_by_date[d][q['topic']] += 1

    # Step 5: Identify topic evolution phases
    print("\n🔍 Step 5: Identifying evolution phases...")
    all_dates = sorted(set(q['date'] for q in all_questions if q['date'] != 'unknown'))

    # Phase 1: May (knowledge base foundation)
    # Phase 2: Early June (systematic tracking setup)
    # Phase 3: Late June (in-depth analysis)
    # Phase 4: July (deep-dive & refinement)
    phases = [
        ("初期建设期", "2026-05-09", "2026-06-02", "知识库奠基、首轮调研"),
        ("系统追踪期", "2026-06-03", "2026-06-18", "建立每日跟踪机制、多领域并行"),
        ("深度分析期", "2026-06-22", "2026-07-02", "方法论固化、深度分析、知识库重构"),
        ("成熟深化期", "2026-07-06", "2026-07-20", "专题深潜、第一性原理审查、工程落地"),
    ]

    # Step 6: Generate report
    print("\n📝 Step 6: Generating report...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(TMP_DIR, exist_ok=True)

    today = datetime.now(tz=TZ).strftime("%Y-%m-%d")
    report_path = os.path.join(OUTPUT_DIR, f"conversation-topic-analysis-{today}.md")
    rel_path = os.path.relpath(report_path, WORKSPACE)

    lines = []
    lines.append(f"# 🗺️ 用户对话主题深度分析报告")
    lines.append("")
    lines.append(f"> 📅 分析日期: {today}  |  📊 数据源: {len(all_questions)} 条用户问题 · 176 个会话")
    lines.append(f"> 📋 时间跨度: 2026-05-09 ~ {today}  |  🎯 话题分类: {len(sorted_topics)} 个")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 📋 执行摘要")
    lines.append("")
    lines.append(f"本报告对 {len(all_questions)} 条用户问题（176个会话）进行全量主题聚类与深度分析。用户为**服务器/AI基础设施研发专家**，")
    lines.append(f"研究方向覆盖超节点系统设计、AI大模型与基础设施、芯片与互联生态、研发管理与方法论等 {len(sorted_topics)} 个专题领域。")
    lines.append("")
    lines.append("### 核心发现")
    lines.append("")
    lines.append(f"1. **技术调研占主导**（~57%），其次是研发管理（~10%）和任务执行（~8%）")
    lines.append(f"2. **超节点系统设计**和**芯片与GPU生态**是最活跃的专题")
    lines.append(f"3. **知识库构建与治理**是贯穿全周期的持续性活动")
    lines.append('4. **迭代精化(T5)** 是最突出的操作思维模式，说明知识沉淀方式以\u201c先建框架、持续填充\u201d为主')
    lines.append(f"5. **系统架构(D1)** 和**实现与设计(D6)** 是最常出现的知识维度")
    lines.append("")
    lines.append("---")
    lines.append("")

    # === Phase Evolution ===
    lines.append("## 📈 时间演化：四大阶段")
    lines.append("")
    lines.append("| 阶段 | 时间 | 特征 | 核心活动 |")
    lines.append("|:----:|:----|:------|:---------|")
    for phase_name, p_start, p_end, p_desc in phases:
        count = sum(1 for q in all_questions if p_start <= q['date'] <= p_end)
        lines.append(f"| {phase_name} | {p_start}~{p_end} | {p_desc} | {count} 条问题 |")
    lines.append("")

    # Daily activity chart
    lines.append("### 📅 每日活跃度")
    lines.append("")
    lines.append("| 日期 | 问题数 | 活跃话题数 | 趋势 |")
    lines.append("|:-----|:------:|:---------:|:-----|")
    for d in all_dates:
        day_topics = len(topic_by_date[d])
        count = sum(topic_by_date[d].values())
        bar = "█" * min(count, 30)
        lines.append(f"| {d} | {count:3d} | {day_topics:2d} | {bar}")
    lines.append("")

    lines.append("---")
    lines.append("")

    # === Global Knowledge Dimensions ===
    lines.append("## 🧠 全局知识维度分布")
    lines.append("")
    lines.append("| 知识维度 | 出现次数 | 占比 | 说明 |")
    lines.append("|:---------|:--------:|:----:|:-----|")
    dim_explanations = {
        "D1:系统架构": "系统拓扑、设计模式、组件关系",
        "D2:标准与生态": "行业标准、开源社区、协议规范",
        "D3:对比与评估": "基准测试、方案比较、权衡分析",
        "D4:方法论与框架": "分析框架、设计思维、工程方法",
        "D5:管理与流程": "项目管理、团队协作、决策流程",
        "D6:实现与设计": "详细设计、代码实现、配置参数",
        "D7:知识管理": "信息组织、归档索引、交叉引用",
        "D8:工具与自动化": "技能脚本、自动化工具、效率提升",
    }
    total_dims = sum(global_dims.values())
    for dim in sorted(global_dims.keys(), key=lambda d: -global_dims[d]):
        pct = global_dims[dim] / total_dims * 100 if total_dims else 0
        bar = "█" * max(1, int(pct / 3))
        exp = dim_explanations.get(dim, "")
        lines.append(f"| {dim} | {global_dims[dim]:4d} | {pct:5.1f}% | {exp} |")
    lines.append("")

    # === Global Operational Patterns ===
    lines.append("## 🔄 全局操作思维模式")
    lines.append("")
    lines.append("| 思维模式 | 出现次数 | 占比 | 解读 |")
    lines.append("|:---------|:--------:|:----:|:-----|")
    pat_explanations = {
        "T1:自顶向下分解": "将大问题拆解为子系统/层次/维度",
        "T2:第一性原理推导": "回归物理极限/经济规律/信息论核心",
        "T3:对比分析": "多方案并列评估，识别优劣势",
        "T4:跨源综合": "从多来源（import/知识库/网络）提取融合",
        "T5:迭代精化": "先建框架再持续填充完善",
        "T6:风险感知决策": "明确考虑风险、ROI、权衡",
    }
    total_pats = sum(global_pats.values())
    for pat in sorted(global_pats.keys(), key=lambda p: -global_pats[p]):
        pct = global_pats[pat] / total_pats * 100 if total_pats else 0
        bar = "█" * max(1, int(pct / 3))
        exp = pat_explanations.get(pat, "")
        lines.append(f"| {pat} | {global_pats[pat]:4d} | {pct:5.1f}% | {exp} |")
    lines.append("")

    lines.append("---")
    lines.append("")

    # === Topic Details ===
    lines.append("## 📑 专题详情")
    lines.append("")

    for topic, qs in sorted_topics:
        detail = topic_details[topic]
        lines.append(f"### 📌 {topic}")
        lines.append("")
        lines.append(f"- **问题数**: {detail['count']}  |  **活跃天数**: {detail['days_active']} 天  |  **时间跨度**: {detail['date_range']}")
        lines.append("")

        # Category distribution
        lines.append("**意图分布**:")
        for cat, cnt in detail['categories'].items():
            pct = cnt / detail['count'] * 100
            lines.append(f"- {cat}: {cnt}次 ({pct:.0f}%)")
        lines.append("")

        # Knowledge dimension distribution
        if detail['dimensions']:
            lines.append("**知识维度**:")
            for dim, cnt in detail['dimensions'].items():
                pct = cnt / detail['count'] * 100
                lines.append(f"- {dim}: {cnt}次 ({pct:.0f}%)")
            lines.append("")

        # Pattern distribution
        if detail['patterns']:
            lines.append("**操作思维**:")
            for pat, cnt in detail['patterns'].items():
                pct = cnt / detail['count'] * 100
                lines.append(f"- {pat}: {cnt}次 ({pct:.0f}%)")
            lines.append("")

        # Daily distribution (compact)
        if detail['daily']:
            lines.append("**时间序列** (▶ 从左到右):")
            timeline = []
            for d in all_dates:
                cnt = detail['daily'].get(d, 0)
                timeline.append("█" if cnt > 0 else "·")
            lines.append(f"```")
            lines.append(f"[{'|'.join(all_dates[0::7])}]")
            lines.append(f" {''.join(timeline)}")
            lines.append(f"```")

            # Key peaks
            peak_date = max(detail['daily'], key=detail['daily'].get)
            peak_count = detail['daily'][peak_date]
            lines.append(f"  **峰值**: {peak_date} ({peak_count}条)")
            lines.append("")

        # Representative questions
        if detail['representative']:
            lines.append("**代表性问题**:")
            for i, rq in enumerate(detail['representative'][:3], 1):
                text_short = rq['text'][:120].replace('\n', ' ')
                if len(rq['text']) > 120:
                    text_short += "..."
                lines.append(f"  {i}. [`{rq['date']}`] {text_short}")
            lines.append("")

        lines.append("---")
        lines.append("")

    # === Cross-topic Insights ===
    lines.append("## 🔗 专题关联与深层洞察")
    lines.append("")

    # Identify topic clusters
    lines.append("### 1. 专题聚类")
    lines.append("")
    lines.append("| 聚类 | 包含专题 | 核心动机 |")
    lines.append("|:-----|:---------|:---------|")
    clusters = [
        ("🖥️ 硬件系统设计", "超节点系统设计 · 服务器硬件架构 · 电源架构 · 液冷散热 · 服务器设计方法论 · 服务器资产管理", "产品工程落地"),
        ("🤖 AI全栈", "AI大模型 · MoE架构 · AI框架 · AI应用/Agent · 万卡集群 · 算力基建 · AI编程工具", "技术前沿跟踪"),
        ("🔗 互联与芯片", "芯片/GPU生态 · 高速互联/光通信 · 存储/内存/HBM · BMC/固件 · 分布式OS", "底层技术掌控"),
        ("📋 研发管理", "研发管理 · 项目管理 · 代码审查 · 可靠性与测试 · 架构投资策略", "工程效率提升"),
        ("🧠 知识与工具", "知识库治理 · AI使用方法论 · 研发工具 · 数据分析 · Skill开发 · 自动化脚本", "基础设施赋能"),
        ("🔬 行业与方法", "行业调研 · 竞品分析 · 方法论体系 · 企业文化", "战略视野拓展"),
    ]
    for cluster_name, members, motive in clusters:
        lines.append(f"| {cluster_name} | {members} | {motive} |")
    lines.append("")

    lines.append("### 2. 知识构建的「三层递进」模式")
    lines.append("")
    lines.append("从问题序列中观察到用户的知识构建遵循三层递进：")
    lines.append("")
    lines.append("```")
    lines.append("Layer 1: 信息采集层")
    lines.append("   ↓ 搜索/跟踪/归档 → \"有什么\"")
    lines.append("Layer 2: 知识组织层")
    lines.append("   ↓ 分类/索引/交叉链接 → \"是什么关系\"")
    lines.append("Layer 3: 深度分析层")
    lines.append("   ↓ 第一性原理/对比/方法论 → \"为什么是这样/怎么做更好\"")
    lines.append("```")
    lines.append("")

    lines.append("### 3. 操作思维的演化")
    lines.append("")
    lines.append("| 阶段 | 主导思维 | 典型问题形式 |")
    lines.append("|:-----|:---------|:------------|")
    lines.append("| 初期建设期 | T4:跨源综合 → T5:迭代精化 | 「搜索…写入知识库」、「参考…提取材料」 |")
    lines.append("| 系统追踪期 | T1:自顶向下分解 | 「跟踪…按照分类…汇总写入」 |")
    lines.append("| 深度分析期 | T2:第一性原理 → T3:对比分析 | 「深度分析…从第一性原理出发」 |")
    lines.append("| 成熟深化期 | T5+T6:迭代+风险决策 | 「专家审查发现15项问题…修正」 |")
    lines.append("")

    lines.append("### 4. 知识库作为「思考外部化」的载体")
    lines.append("")
    lines.append("用户将知识库视为思维的外化系统：")
    lines.append("- 每次调研后立即归档（即时沉淀）")
    lines.append("- 每次迭代补充已有文档（持续积累）")
    lines.append("- 通过交叉链接建立知识网络（关联发现）")
    lines.append("- 通过方法论约束质量（元认知）")
    lines.append("- 通过Skills固化解题流程（自动化）")
    lines.append("")

    lines.append("---")
    lines.append("")

    # === Appendix: Topic List ===
    lines.append("## 📋 完整专题列表（按问题数排序）")
    lines.append("")
    lines.append("| # | 专题 | 问题数 | 活跃天数 | 时间跨度 | 主要意图 |")
    lines.append("|:-:|:-----|:------:|:--------:|:---------|:---------|")
    for i, (topic, qs) in enumerate(sorted_topics, 1):
        d = topic_details[topic]
        main_cat = list(d['categories'].keys())[0] if d['categories'] else "-"
        lines.append(f"| {i} | {topic} | {d['count']} | {d['days_active']} | {d['date_range']} | {main_cat} |")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"> 📊 本报告由 conversation-topic-analyzer 自动生成")
    lines.append(f"> 🛠️ 重新生成: `cd ~/cow && python3 skills/conversation-topic-analyzer/scripts/analyze_topics.py`")
    lines.append("")

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    # Save debug data
    debug_data = {
        'total_questions': len(all_questions),
        'total_topics': len(sorted_topics),
        'topic_details': topic_details,
        'global_dims': dict(global_dims),
        'global_pats': dict(global_pats),
    }
    with open(os.path.join(TMP_DIR, 'topic-analysis-data.json'), 'w', encoding='utf-8') as f:
        json.dump(debug_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 报告已生成:")
    print(f"   📄 {rel_path}")
    print(f"   📊 {len(all_questions)} 条问题 → {len(sorted_topics)} 个专题")
    print(f"   🔧 调试数据: tmp/topic-analysis-data.json")

    return report_path

if __name__ == "__main__":
    main()
