---
name: pipeline-multi-path
description: "Multi-path parallel processing engine for the AI production pipeline. Stage 2 of 6. Splits a single task into multiple independent processing paths running in parallel — each with isolated context, separate token budgets, and independent failure domains. Use when: (1) running a task that benefits from multiple perspectives/viewpoints, (2) asked to '多路并行' or '多视角处理', (3) processing high-value tasks that need cross-validation, (4) decomposing large complex tasks into parallel sub-tasks, (5) part of pipeline-orchestrator pipeline execution. Does NOT merge results — output to convergence stage."
metadata:
  requires:
    bins: ["python3"]
---
# Multi-path Parallel Processing

**Pipeline Stage 2**: Execute the same task from multiple independent angles simultaneously. Each path has isolated context, separate token budget, and independent failure handling.

## Workflow

### Step 1 — Select Parallel Mode

Choose based on task type:

#### Mode A: Multi-Perspective (most common)
Same problem, different angles:
```
Input: "Analyze chip X competitiveness"

Path A ── Technical specs (perf/power/area/cost)
Path B ── Market positioning (price/supply/ecosystem/alternatives)  
Path C ── Timeline (evolution roadmap/generational gap/trends)
```

**Best for**: Comprehensive analysis, research, reports

#### Mode B: Multi-Model/Agent
Same task, different models/agents:
```
Path A ── DeepSeek (strong reasoning/long-form)
Path B ── GPT (structured/code)  
Path C ── Claude (analysis/safety)
```

**Best for**: High-value/high-risk tasks needing cross-validation

#### Mode C: Multi-Method
Same problem, different solution methods:
```
Input: "Calculate system TCO"

Path A ── Top-down (from budget)
Path B ── Bottom-up (component sum)
Path C ── Benchmarking (competitor estimate)
```

**Best for**: Numerical computation, cost estimation, performance prediction

#### Mode D: Multi-Stage (pipeline within pipeline)
```
              ┌── Sub-task A1 (independent agent)
Input ── Decompose ── Sub-task A2 (independent agent) ── Sub-convergence ── Main convergence
              └── Sub-task A3 (independent agent)
```

**Best for**: Large documents, complex system decomposition

### Step 2 — Path Isolation

Each path MUST be strictly isolated:

| Isolation Dimension | Requirement |
|:--------------------|:------------|
| **Context isolation** | Each path has independent context window, no cross-reading |
| **Token budget** | Each path allocated independent token quota, no preemption |
| **Tool calls** | Tool results from one path not leaked to others |
| **Intermediate files** | Namespace isolation per path (e.g., `tmp/path_A/`) |
| **Failure isolation** | One path failure doesn't affect others |

### Step 3 — Sub-Agent Offloading

For heavy/specialized tasks, offload to sub-agents:

```
Main Agent
  ├── Sub-agent A (research/search, independent Ralph loop)
  ├── Sub-agent B (data analysis, independent token budget)
  └── Sub-agent C (chart generation, independent context)
```

**Sub-agent protocol**:
1. Main agent issues clear task definition (with completion criteria)
2. Sub-agent runs its own TAOR loop independently
3. Sub-agent completes → returns only summary to main agent
4. Main agent context unaffected by sub-agent consumption

### Step 4 — Output per Path

Each path outputs:
1. **Result content** (in standard format matching task type)
2. **Source references** (with credibility grades)
3. **Confidence score** (0.0-1.0)
4. **Issues/uncertainties** noted during processing

## Output Format

```yaml
multi_path_result:
  paths:
    - id: "path_A"
      mode: "multi_perspective"
      perspective: "technical_specs"
      result: "(full output content)"
      sources: ["NVIDIA GB300 Whitepaper (S)"]
      confidence: 0.95
      issues: []
    - id: "path_B"
      mode: "multi_perspective"
      perspective: "market"
      result: "(full output content)"
      sources: ["DIGITIMES Report (B)"]
      confidence: 0.70
      issues: ["Cost data from 2025Q2, may be outdated"]
```

## Script

Scripts are in `<base_dir>/scripts/`.

```bash
python3 <base_dir>/scripts/spawn_paths.py --config paths_config.json  # ⚠️ 设计承诺（多路分支生成（语义判断），当前由 LLM 按配置直接执行）
```

## References

See full methodology: `knowledge/05_tools/ai-production-pipeline/ai-production-pipeline-methodology.md` (§4)
