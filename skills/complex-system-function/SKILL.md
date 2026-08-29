---
name: complex-system-function
description: Analyze and design complex systems using the "Function as Life-Giving Mechanism" framework. Use when user asks about: (1) system analysis from input→function→output→feedback perspective, (2) understanding how "dead" information becomes "alive" through function processing, (3) experience reuse across different contexts, (4) decision-making based on cost-calibrated analysis, (5) mapping systems to the four creation methods framework. Triggers: "活的系统", "function", "输入输出", "反馈", "系统分析", "经验复用", "场景变量", "complex system", "system function", "context reuse".
---

# Complex System Function Analysis Skill

Analyze complex systems using the **Function as Life-Giving Mechanism** framework — the insight that piled-up information/matter becomes "alive" when it has input, state, output, and feedback.

## Core Framework

### The Life-Giving Function

```
Dead Stack (无生命堆积) → Function(Input → State → Output → Feedback) → Living System
```

A system is **alive** when:
1. **Input** — Receives data/matter from outside
2. **State** — Maintains internal conditions
3. **Output** — Produces results/deliverables
4. **Feedback** — Output loops back to affect future input

### Function's Complexity Sources

Functions are not simple `y = f(x)`. They can be:

| Complexity | Description | Example |
|:-----------|:------------|:--------|
| **Multi-branch** | Not linear, a decision tree | `if-else if-else` chain |
| **Context-dependent** | Same input, different output per context | Code review with vs without knowledge base |
| **Resource-constrained** | Input size/count limits | Max 20 files per API call |
| **Demand-layered** | Different outputs for different needs | Report vs specific issue detection |
| **Interfering mechanisms** | Multiple sub-functions interact | Scheduling + security + reliability logic |

## Three Model Framework

### Model 1: Complex Input Mapping System

```
Input Set → Multi-layer Decision Logic → Targeted Output
```

Use this model when analyzing **tools, APIs, or automated systems**:

1. **Identify all input sources and constraints**
   - Primary input (core data)
   - Contextual input (knowledge base, history)
   - Rate limits and boundaries
   
2. **Map the decision layer**
   - Not a single output — multiple possible outputs per demand type
   - Each user type needs a different output dimension

3. **Characterize the system**
   - Simple linear → easy
   - Multi-constraint, multi-branch, multi-objective coupled system → complex

### Model 2: Task Workflow Closure

```
Start → Collect → Produce Output (file) → Verify → Value Judge
```

Use this model when analyzing **human workflows, project deliverables, or processes**:

1. **Base layer**: Input → Process → Output (obvious deliverable)
2. **Value-add layer 1 — Verification**: Output ≠ closure. Must include implementation plan + execution steps
3. **Value-add layer 2 — Cost-Calibrated Decision Making**:

| Investment Level | Decision Approach | Effort |
|:-----------------|:------------------|:-------|
| Small (¥5-level) | Gut feeling, low deliberation | Minimal |
| Large (¥5M-level) | Full dimensional analysis, expert support | Heavy |

### Model 3: Core Personal Capability Baseline

1. Deep text/language comprehension
2. Multi-layer logic decomposition + complex system analysis
3. Financial/industry research and judgment

**Action**: Select targets → deep analysis → accumulate over time

## Experience Reuse Across Scenarios

### The Core Problem

> "Experience from past success is a matched closed-loop of input + context + resources + relationships under the OLD scenario. When you change scenarios, ALL four variables change."

### Four Variables That Change

1. **Context baseline** — Industry, business goals, constraints
2. **Resource boundary** — People, budget, tools, data access
3. **Relationship inversion** — Old supporter → New blocker (most overlooked)
4. **Hidden constraints** — Risk tolerance, KPIs, compliance

### Reuse Protocol

1. **Scenario variable audit** — List and compare old vs new context/resources/stakeholders/constraints
2. **Match verification depth to investment** — Small = quick check, Large = full plan + backup paths + external review
3. **Experience = reference base, NOT final solution** — Reconstruct steps under new constraints
4. **Set stop-loss criteria** — If resources are insufficient or leadership keeps pushing back, pivot early

## Connection to Four Creation Methods

| Method | Function Form | Example |
|:-------|:--------------|:--------|
| **1: Raw Build** | One-off function | Hand-write script for single file processing |
| **2: Template/Copy** | Parameterized function | Abstract to function library |
| **3: Combine/Plagiarize** | Compose existing functions | Use OSS libraries + business logic |
| **4: Infrastructure** | Platform/DSL/Engine | Low-code platform, workflow engine, AI Agent orchestration |

## Unified Methodology (Reusable for All Tasks)

1. **Abstract inputs, constraints, and branch rules first** — Distinguish simple linear from complex coupled systems
2. **Calibrate decision rigor to investment size** — Don't over-analyze low-value items
3. **Deliverables in two layers** — Base deliverable + Implementation plan
4. **Build three core capabilities** — Reading comprehension, logic decomposition, industry judgment
5. **Start with small concrete cases** — Lower resistance, visible results
6. **Audit scenario variables before cross-context reuse**

## Scripts

Scripts are in this skill's `scripts/` directory (relative to the skill's base directory shown in skill listing).

### analyze_system_function.py

Analyzes any system/process/tool using the Function-Life framework:

```bash
python3 "<base_dir>/scripts/analyze_system_function.py" --name "Code Review Tool" --input "defer file, context KB, history" --output "quality report, specific issues" --complexity high --decision-cost large
```

### check_experience_reuse.py

Checks whether past experience can be safely reused in a new scenario:

```bash
python3 "<base_dir>/scripts/check_experience_reuse.py"
```

Interactive Q&A: walks through the four scenario variables (context, resources, relationships, constraints) and outputs a reuse risk assessment.

## References

See the knowledge base archive for the full conversation and framework details:

- `knowledge/enterprise-mgmt/sources/2026-06-18-complex-system-function-input-output.md` — Complete archive with framework connections
- `knowledge/enterprise-mgmt/sources/2026-06-18-four-creation-methods-patterns.md` — Four creation methods framework (2294 lines)
- `knowledge/enterprise-mgmt/sources/2026-06-18-communication-four-methods.md` — Communication as remote function call
