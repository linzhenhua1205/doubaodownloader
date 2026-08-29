#!/usr/bin/env python3
"""批判分析增强 — 批判辩证分析 + 底层原理 + 市场机会

策略 (分层):
  1. 若配置了 LLM API (OPENAI_API_KEY 等) → 调 LLM 生成高质量分析
  2. 无 LLM → 规则模板兜底 (基于文本信号生成结构化分析骨架)

输出写入 article.analysis / article.principles / article.opportunities。
"""
import os
import re
from lib.extractor import ExtractedArticle

# 领域关键词 → 底层原理提示 (规则兜底用)
DOMAIN_PRINCIPLES = {
    "kvcache|kv cache|key-value": "KV Cache 本质是注意力计算的增量结果缓存: O(n²) 注意力 → O(1) 增量; 容量随 seq_len×layers×heads×d_model 增长, 与权重内存解耦",
    "rdma|roce|nvlink|infiniband": "高速互联的物理基础: 铜缆/光模块信号完整性, 拥塞控制 (PFC/ECN), 端到端延迟分解 (NIC 处理→链路→交换)",
    "gpu|hbm|hbm4": "HBM 堆叠 DRAM: TSV 硅通孔 + 3D 堆叠, 带宽 vs 容量 vs 成本的三角权衡; 工艺/良率/散热约束",
    "liquid cooling|液冷": "液体比热容 vs 空气: 水的比热 4.18 kJ/(kg·K) 约为空气的 4 倍; 冷却能力由流量×ΔT×比热决定",
    "cxl|pcie|内存池": "PCIe/CXL 串行链路: 差分信号对, 每通道速率 (Gen5 32GT/s), 内存池化依赖 CXL.mem 一致性语义",
    "ai server|服务器|超节点": "超节点设计的第一性约束: 总线带宽×规模 vs 成本, Scale-up 域 vs Scale-out 域的分界 (交换机 radix)",
    "moE|mixture": "MoE 稀疏激活: 路由开销 vs 计算节省, 专家并行通信 (all-to-all) 是扩展瓶颈",
    "dram|存储|ssd|flash": "存储层级: 延迟-容量-成本曲线, NAND 3D 堆叠层数 vs 可靠性, QLC/TLC 写入寿命",
    "inference|推理": "推理成本分解: prefill (计算密集) vs decode (访存密集), KV cache 是 decode 阶段带宽瓶颈",
}


def enhance_analysis(article: ExtractedArticle, url: str) -> ExtractedArticle:
    """为文章附加批判分析/底层原理/市场机会。"""
    text = (article.text or "")[:12000]
    title = article.title or ""

    # 1. 尝试 LLM 增强
    llm_out = _try_llm(title, text, url)
    if llm_out:
        article.analysis = llm_out.get("analysis", "")
        article.principles = llm_out.get("principles", "")
        article.opportunities = llm_out.get("opportunities", "")
        return article

    # 2. 规则模板兜底
    article.analysis = _rule_analysis(title, text)
    article.principles = _rule_principles(title, text)
    article.opportunities = _rule_opportunities(title, text)
    return article


def _try_llm(title: str, text: str, url: str) -> dict:
    """尝试调用 OpenAI 兼容 API。返回 {analysis, principles, opportunities} 或 None。"""
    # 端点/密钥匹配: DEEPSEEK key → DEEPSEEK base; OPENAI key → OPENAI base
    deepseek_key = os.environ.get("DEEPSEEK_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    if deepseek_key and not openai_key:
        api_key = deepseek_key
        base = os.environ.get("DEEPSEEK_API_BASE") or "https://api.deepseek.com/v1"
        model = os.environ.get("WEB_ARCHIVE_LLM_MODEL") or "deepseek-chat"
    elif openai_key:
        api_key = openai_key
        base = os.environ.get("OPENAI_API_BASE") or "https://api.openai.com/v1"
        model = os.environ.get("WEB_ARCHIVE_LLM_MODEL") or "gpt-4o-mini"
    else:
        return None
    try:
        import requests
        prompt = f"""请对以下技术文章进行专业分析，输出 JSON（三个字段）：
1. analysis: 批判辩证分析（≤300字）— 作者观点/论据的强弱点、可能的偏差、反方观点、数据可信度
2. principles: 底层原理补充（≤300字）— 用第一性原理解释文中技术现象的本质机制
3. opportunities: 市场机会（≤200字）— 该技术方向的商业化机会、市场规模信号、落地路径

文章标题: {title}
文章内容(截取): {text[:6000]}

输出格式: {{"analysis": "...", "principles": "...", "opportunities": "..."}}"""
        r = requests.post(f"{base}/chat/completions",
                          headers={"Authorization": f"Bearer {api_key}"},
                          json={"model": model, "messages": [{"role": "user", "content": prompt}],
                                "temperature": 0.4, "max_tokens": 1500},
                          timeout=60)
        if r.status_code == 200:
            content = r.json()["choices"][0]["message"]["content"]
            return _parse_llm_json(content)
    except Exception:
        pass
    return None


def _parse_llm_json(content: str) -> dict:
    """解析 LLM JSON 输出 (容忍代码块包裹/前后噪声)"""
    m = re.search(r"\{.*\}", content, re.S)
    if not m:
        return None
    import json
    try:
        return json.loads(m.group(0))
    except Exception:
        # 容错: 逐字段提取
        out = {}
        for k in ("analysis", "principles", "opportunities"):
            fm = re.search(rf'"{k}"\s*:\s*"(.+?)"', m.group(0), re.S)
            if fm:
                out[k] = fm.group(1).replace("\\n", "\n")
        return out or None


def _rule_analysis(title: str, text: str) -> str:
    """规则兜底: 批判辩证分析骨架"""
    signals = []
    if re.search(r"\d+(\.\d+)?%|\d+(\.\d+)?x|\d+\s*(GB|TB|MB|PB)", text):
        signals.append("文中含量化数据，需核对来源与对比基线（数值+单位+条件）")
    else:
        signals.append("文中量化数据偏少，结论可能依赖定性判断，需补充可验证指标")
    if re.search(r"作者|我们认为|本文认为|总结", text):
        signals.append("存在主观论断，需区分事实与观点")
    if re.search(r"可能|或许|大概|预计", text):
        signals.append("存在不确定性表述，需标注置信度/假设条件")
    return (
        "**批判辩证分析（规则模板，建议 LLM 增强）**\n\n"
        "1. **论点强度**: 核心主张需回溯原始数据源验证；单一来源结论需多源交叉。\n"
        f"2. **信号提示**: {'；'.join(signals) if signals else '常规技术报道'}\n"
        "3. **反方视角**: 技术宣传常高估短期收益、低估工程落地成本（维护/兼容/人才）；"
        "注意供应链、标准竞争、生态锁定等非技术变量。\n"
        "4. **时效性**: 技术文章结论受版本迭代影响，归档时标注发布时间与适用版本。"
    )


def _rule_principles(title: str, text: str) -> str:
    """规则兜底: 底层原理 (领域关键词匹配)"""
    hits = []
    for pat, principle in DOMAIN_PRINCIPLES.items():
        if re.search(pat, (title + " " + text)[:3000], re.I):
            hits.append(principle)
    if hits:
        return "**底层原理补充（规则模板）**\n\n" + "\n".join(f"- {h}" for h in hits[:4])
    return (
        "**底层原理补充（规则模板）**\n\n"
        "本文涉及技术的第一性约束建议从以下维度补全：\n"
        "- **物理极限**: 带宽/延迟/容量的物理决定因素（信号速率、介质、距离）\n"
        "- **经济规律**: 成本结构（资本开支/运维/折旧）与规模效应\n"
        "- **信息论**: 压缩/编码/校验的理论边界\n"
        "- **系统权衡**: 文中方案在哪些维度做了取舍（如带宽 vs 延迟 vs 成本）"
    )


def _rule_opportunities(title: str, text: str) -> str:
    """规则兜底: 市场机会"""
    signals = []
    if re.search(r"市场|规模|亿美元|亿元|增长|份额", text):
        signals.append("文中含市场数据，可作为市场机会线索")
    if re.search(r"英伟达|nvidia|amd|intel|华为|浪潮|联想|超聚变", text):
        signals.append("涉及主要厂商，可跟踪其产品节奏与生态布局")
    return (
        "**市场机会（规则模板，建议结合行业调研补全）**\n\n"
        "1. **需求侧**: 该技术解决的痛点规模（训练/推理成本、效率瓶颈）与客户付费意愿。\n"
        f"2. **信号**: {'；'.join(signals) if signals else '需进一步调研市场信号（TAM/SAM/增长率）'}\n"
        "3. **落地路径**: 从 POC → 规模化部署的典型周期与关键决策点；"
        "标准卡位窗口（2026H2）与生态合作策略。\n"
        "4. **风险**: 技术路线被替代风险、供应链依赖、客户集中度。"
    )
