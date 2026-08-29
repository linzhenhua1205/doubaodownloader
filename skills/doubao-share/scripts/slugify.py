#!/usr/bin/env python3
"""
Generate a URL-friendly slug from a Chinese conversation title.
Used by the doubao-share skill to create consistent knowledge base filenames.

Usage:
    python3 slugify.py "复杂系统与经验复用"
    Output: complex-system-and-experience-reuse

    python3 slugify.py "四种创造手法：从0构建到COW"
    Output: four-creation-method-from-building-to-cow
"""

import sys
import re


# Chinese-to-English mapping (sorted by length desc for greedy matching)
CHINESE_MAP_LIST = sorted([
    # Multi-word compounds first
    ("不可干预", "non-intervenable"),
    ("可干预", "intervenable"),
    ("因果关系", "causality"),
    ("强化学习", "reinforcement-learning"),
    ("基础设施化", "infrastructure"),
    ("生命周期", "lifecycle"),
    ("高性能", "high-performance"),
    ("相关性推断", "correlation-inference"),
    ("因果推断", "causal-inference"),
    ("设计活动", "design-activity"),
    ("方法论", "methodology"),
    ("分布式", "distributed"),
    ("跨域", "cross-domain"),
    ("知识库", "knowledge-base"),
    ("大模型", "llm"),
    ("裸信号", "raw-signal"),
    ("异步", "asynchronous"),
    ("同步", "synchronous"),
    ("人工智能", "ai"),
    ("机器学习", "machine-learning"),
    ("自然语言", "natural-language"),
    ("上下文", "context"),
    ("输入", "input"),
    ("输出", "output"),
    ("反馈", "feedback"),
    ("变量", "variable"),
    ("场景", "scenario"),
    ("Agent", "agent"),
    ("GPU", "gpu"),
    ("RAG", "rag"),
    ("MoE", "moe"),
    ("模拟", "simulation"),
    ("认知", "cognition"),
    ("系统", "system"),
    ("设计", "design"),
    ("模式", "pattern"),
    ("架构", "architecture"),
    ("框架", "framework"),
    ("方法", "method"),
    ("本质", "essence"),
    ("结构", "structure"),
    ("功能", "function"),
    ("模型", "model"),
    ("原理", "principle"),
    ("理论", "theory"),
    ("实践", "practice"),
    ("机制", "mechanism"),
    ("策略", "strategy"),
    ("算法", "algorithm"),
    ("协议", "protocol"),
    ("创造", "creation"),
    ("构建", "building"),
    ("复用", "reuse"),
    ("手法", "method"),
    ("模板", "template"),
    ("复制", "copy"),
    ("抄袭", "copying"),
    ("拼装", "assembly"),
    ("域", "domain"),
    ("代价", "cost"),
    ("经验", "experience"),
    ("能力", "capability"),
    ("模仿", "imitation"),
    ("观摩", "observation"),
    ("提炼", "extraction"),
    ("重现", "reproduction"),
    ("验证", "validation"),
    ("通信", "communication"),
    ("存储", "storage"),
    ("计算", "computing"),
    ("网络", "network"),
    ("安全", "security"),
    ("数据", "data"),
    ("芯片", "chip"),
    ("内存", "memory"),
    ("硬件", "hardware"),
    ("软件", "software"),
    ("创建", "creation"),
    ("演化", "evolution"),
    ("操作", "operation"),
    ("推理", "inference"),
    ("训练", "training"),
    ("部署", "deployment"),
    ("优化", "optimization"),
    ("测试", "testing"),
    ("集成", "integration"),
    ("回收", "reclamation"),
    ("编排", "orchestration"),
    ("智能", "intelligence"),
    ("注意力", "attention"),
    ("向量", "vector"),
    ("检索", "retrieval"),
    ("图谱", "graph"),
    ("伪装", "camouflage"),
    ("筛选", "filtering"),
    ("博弈", "gaming"),
    ("诈骗", "fraud"),
    ("人际", "interpersonal"),
    ("分层", "layering"),
    ("逻辑", "logic"),
    ("同源", "common-origin"),
    ("复杂", "complex"),
    ("简单", "simple"),
    ("通用", "universal"),
    ("并行", "parallel"),
    ("实时", "realtime"),
    ("企业", "enterprise"),
    ("管理", "management"),
    ("战略", "strategy"),
    ("组织", "organization"),
    ("人才", "talent"),
    ("决策", "decision"),
    ("事件", "event"),
    ("告警", "alert"),
    ("监控", "monitoring"),
    ("可观测", "observability"),
    ("产品", "product"),
    ("研发", "rd"),
    ("方案", "solution"),
    ("需求", "requirement"),
    ("消息", "message"),
    ("管道", "pipeline"),
    ("语言", "language"),
    ("产品", "product"),
    ("本质", "essence"),
    ("层面", "level"),
    ("视角", "perspective"),
    ("维度", "dimension"),
    ("与", "and"),
    ("从", "from"),
    ("到", "to"),
    ("和", "and"),
    ("或", "or"),
    ("的", ""),
    ("之", ""),
], key=lambda x: -len(x[0]))


def translate_chinese_segment(segment: str) -> str:
    """Translate a Chinese-only segment word by word (greedy longest match)."""
    result_parts = []
    i = 0
    while i < len(segment):
        matched = False
        for zh, en in CHINESE_MAP_LIST:
            if segment[i:i+len(zh)] == zh:
                if en:  # skip empty translations (like "的")
                    result_parts.append(en)
                i += len(zh)
                matched = True
                break
        if not matched:
            # Character not in map - skip it
            i += 1
    # Join translated words with hyphens
    return '-'.join(result_parts)


def slugify(text: str, max_len: int = 80) -> str:
    """Convert Chinese/English text to a kebab-case slug."""
    # Step 1: Tokenize into Chinese and non-Chinese segments
    tokens = re.findall(r'[\u4e00-\u9fff]+|[^\u4e00-\u9fff]+', text)

    # Step 2: Translate each segment
    translated_parts = []
    for token in tokens:
        if re.match(r'^[\u4e00-\u9fff]+$', token):
            translated = translate_chinese_segment(token)
            if translated:
                translated_parts.append(translated)
        else:
            # Non-Chinese - keep as is
            translated_parts.append(token.strip())

    # Step 3: Normalize
    result = ' '.join(translated_parts)
    result = result.lower().strip()

    # Replace non-alphanumeric chars (except hyphens) with spaces
    result = re.sub(r'[^a-z0-9\s-]', ' ', result)
    # Collapse spaces to hyphens
    result = re.sub(r'\s+', '-', result)
    # Remove consecutive hyphens
    result = re.sub(r'-+', '-', result)
    result = result.strip('-')

    # Step 4: Limit length at word boundary
    if len(result) > max_len:
        cut = result[:max_len].rfind('-')
        if cut > max_len // 2:
            result = result[:cut]
        else:
            result = result[:max_len]
        result = result.strip('-')

    return result if result else "conversation"


def main():
    if len(sys.argv) < 2:
        print("Usage: slugify.py <conversation-title>")
        print()
        print("Examples:")
        print('  slugify.py "复杂系统与经验复用"')
        print('  slugify.py "设计活动的本质：观摩·提炼·重现·验证"')
        sys.exit(1)

    title = ' '.join(sys.argv[1:])
    slug = slugify(title)
    print(slug)


if __name__ == "__main__":
    main()
