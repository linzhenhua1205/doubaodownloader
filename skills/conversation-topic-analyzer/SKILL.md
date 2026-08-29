---
name: conversation-topic-analyzer
description: Comprehensive topic analysis and knowledge dimension extraction from conversation logs. Use when: (1) user wants to analyze conversation history for thematic patterns, (2) user needs to understand topic evolution over time, (3) user asks to extract knowledge dimensions and operational thinking from past questions, (4) user wants to cluster and categorize user questions by domain, (5) user wants to generate topic analysis reports with intent classification. Triggers: 对话分析、主题分析、话题聚类、意图分析、知识维度提取、操作思维提取、conversation analysis、topic analysis、knowledge dimension.
metadata:
  requires:
    bins: ["python3"]
---

# Conversation Topic Analyzer

## Overview

Analyze conversation logs (user questions) to extract:
- **Topic clustering**: Group related questions into meaningful topics
- **Time-series evolution**: Show how topics emerge, peak, and evolve
- **Topic category & intent**: What each topic is about and why the user asked
- **Knowledge dimensions**: The knowledge structures being built
- **Operational thinking**: Problem-solving patterns and thinking approaches

## Data Sources

| Source | Path | Description |
|--------|------|-------------|
| User Questions (flat) | `conversation-log/user-questions/` | 177 files, brief questions per session |
| Full Sessions (DB) | `~/cow/memory/long-term/index.db` | SQLite DB with full messages |
| Full Sessions (files) | `conversation-log/db-sessions/` | 263 files, complete session exports |
| Existing Analysis | `conversation-log/user-questions/TOPIC_ANALYSIS.md` | Earlier partial analysis (outdated) |

## Analysis Methodology

### Layer 1: Topic Clustering (纬度聚合)

Use multi-dimensional clustering:
1. **Surface-level**: Keywords from filenames and question text
2. **Domain-level**: Map to knowledge base domains (superpod/AI/BMC/hardware/network/software/management)
3. **Intent-level**: Why was this asked? (knowledge_build / research / troubleshooting / methodology / management / task)
4. **Action-level**: What operation? (search/create/analyze/architect/review/fix/plan/compare)

### Layer 2: Time-Series Organization (时间序列)

Track for each topic:
- **First appearance**: When did this topic first emerge?
- **Active period**: When was it most discussed?
- **Peak intensity**: Maximum questions per day on this topic
- **Evolution**: How did the focus shift within the topic?

### Layer 3: Knowledge Dimensions (知识维度)

Extract 8 knowledge dimensions:

| Dimension | Description | Example |
|-----------|-------------|---------|
| D1: Architecture | System topology, design patterns, component relationships | PCIe topology, NVLink fabric |
| D2: Standard/Ecosystem | Industry standards, open source, protocols | ODCC, OCP, UALink, Redfish |
| D3: Comparison/Evaluation | Benchmarking, trade-off analysis | H100 vs B200, performance metrics |
| D4: Methodology | Frameworks, processes, design thinking | MECE, first principles, IPD |
| D5: Management/Process | Project mgmt, team collaboration, decision-making | R&D planning, code review |
| D6: Implementation | Design details, coding, configuration | HW strap pin, CPLD registers |
| D7: Knowledge Management | How info is organized, archived, linked | Knowledge base structure, cross-refs |
| D8: Tooling/Automation | Skills, scripts, tools, automation | Scheduling tasks, export scripts |

### Layer 4: Operational Thinking Patterns (操作思维)

Extract 6 thinking patterns:

| Pattern | Description | Signal |
|---------|-------------|--------|
| T1: Top-Down Decomposition | Break big problem into subsystems | "分层", "维度", "分类" |
| T2: First-Principles Derivation | Back to fundamentals | "第一性原理", "物理极限" |
| T3: Comparative Analysis | Side-by-side evaluation | "对比", "对表", "vs" |
| T4: Cross-Reference Synthesis | Combine multiple sources | "参考import", "提取材料" |
| T5: Iterative Refinement | Repeatedly improve | "补充", "完善", "优化" |
| T6: Risk-Aware Decision | Explicit risk consideration | "风险", "评估", "备选" |

## Execution

### Analyze and Generate Report

Use the analysis script:

```bash
cd ~/cow
python3 skills/conversation-topic-analyzer/scripts/analyze_topics.py
```

This will:
1. Scan all 176+ user-question files
2. Cluster questions into coherent topics
3. Build time-series for each topic
4. Extract knowledge dimensions and operational patterns
5. Generate comprehensive report

### Output

The script outputs:
- **Report file**: `knowledge/01_survey/industry-research/03_server/conversation-topic-analysis-YYYY-MM-DD.md`
- **Temporary data**: `tmp/topic-analysis-data.json` (for debugging/iteration)
- **Updates**: append to `knowledge/log.md` only（`kb-log-append.py`；`index.md`/`README.md` not touched by AI, batch-refreshed by scripts; `01_survey/` follows daily-report rule）

### Manual Refinement

After script runs, review the report for:
- Topic boundaries that might need splitting/merging
- Intent descriptions that need deeper interpretation
- Knowledge dimensions that were missed
- Operational patterns that need correction
