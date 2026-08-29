---
name: pipeline-orchestrator
description: "AI生产流水线全流程编排器。按pipeline-orchestrator配置串联6个阶段Skill（input-qa→multi-path→convergence→verification-loop→constraint-enforcer→expert-gate），维护全局任务状态、阶段间断点续传、异常处理与失败分析。Use when: (1) 需要运⾏完整的AI高质量产出流水线，(2) 跨多个阶段的大任务需要系统编排，(3) 要求'全流程'/'流水线'/'pipeline'，(4) 需要断点续传或状态追踪的复杂任务，(5) 启动完整pipeline：从输入校验到专家终审的端到端执行。不用于：单阶段任务（路由到单个阶段Skill）、简单问答。"
metadata:
  requires:
    bins: ["python3"]
---
# Pipeline Orchestrator

**The conductor** of the 6-stage AI production pipeline. Routes tasks through stages, maintains state, handles failures, and supports checkpoint/resume.

## Pipeline Architecture

```
Input ──① input-qa ──② multi-path ──③ convergence ──④ verification-loop ──⑤ constraint-enforcer ──⑥ expert-gate ── Output
                                                                                │
                                                                          pipeline-orchestrator (state mgmt + sessions)
```

## Workflow

### Step 1 — Task Initialization

Parse task config and initialize pipeline state:

```yaml
task:
  name: "Competitive Analysis Report"
  type: "analysis_report"
  urgency: "normal"

pipeline:
  profile: "standard"  # quick / standard / deep
  parallel_paths: 3
  max_iterations: 5

output:
  format: "markdown"
  toc: true
  changelog: true
```

Create pipeline state file: `tmp/pipeline/<task_name>/state.json`

### Step 2 — Stage Execution (Sequential)

Execute each stage in order. Each stage reads from and writes to the shared pipeline state.

#### Stage 1: Input Quality Gate

```
Input materials → [pipeline-input-qa] → validated_input.json
                                          │
                                     Pass? ── No ──→ Return rejection with details
                                          │
                                         Yes
                                          │
                                          ▼
```

**How to call**: Read `skills/pipeline-input-qa/SKILL.md` and follow its workflow. Validate input materials against the checklist. Write result to pipeline state.

#### Stage 2: Multi-Path Processing

```
validated_input.json → [pipeline-multi-path] → multi_path_results.json
                                                  │
                                             (each path isolated)
                                                  │
                                                  ▼
```

**How to call**: Read `skills/pipeline-multi-path/SKILL.md` and follow its workflow. Spawn 2-5 parallel paths depending on profile. Each path independently processes the input.

#### Stage 3: Convergence

```
multi_path_results.json → [pipeline-convergence] → merged_result.json
                                                      │
                                                 (conflict resolved)
                                                      │
                                                      ▼
```

**How to call**: Read `skills/pipeline-convergence/SKILL.md` and follow its workflow. Merge multi-path results with conflict resolution.

#### Stage 4: Verification Loop (Ralph)

```
merged_result.json → [pipeline-verification-loop] → verified_result.json
                                                       │
                                                  Pass? ── No (≤max_iter) ──→ Return to Stage 2/3
                                                       │
                                                      Yes
                                                       │
                                                       ▼
```

**How to call**: Read `skills/pipeline-verification-loop/SKILL.md` and follow its workflow. Run Ralph loop until pass or max_iterations exceeded.

**Loop logic**:
```
round = 0
while round < max_iterations:
    result = verify(output)
    if result.pass:
        break
    else:
        reflect_and_replan(result.issues)
        redo affected sections
        round++
if round >= max_iterations:
    suspend_for_human(reason="Max iterations exceeded")
```

#### Stage 5: Constraint Enforcement

```
verified_result.json → [pipeline-constraint-enforcer] → constraint_checked.json
                                                           │
                                                      Pass? ── No → auto_fix or flag
                                                           │
                                                          Yes
                                                           │
                                                           ▼
```

**How to call**: Read `skills/pipeline-constraint-enforcer/SKILL.md` and follow its workflow. Enforce three-layer constraints. Auto-fix minor violations, flag major ones.

#### Stage 6: Expert Gate

```
constraint_checked.json → [pipeline-expert-gate] → final_deliverable
                                                      │
                                                  Pass? ── No → Return to specified stage with routing info
                                                      │
                                                     Yes
                                                      │
                                                      ▼
                                                FINAL OUTPUT
```

**How to call**: Read `skills/pipeline-expert-gate/SKILL.md` and follow its workflow. Generate review checklist and present to expert for sign-off.

### Step 3 — State Management

Maintain global pipeline state throughout execution:

```json
{
  "task_id": "gb300-vs-b200-20260710",
  "status": "in_progress",
  "current_stage": 3,
  "stages": {
    "1_input_qa": {"status": "passed", "output": "validated_input.json"},
    "2_multi_path": {"status": "passed", "output": "multi_path_results.json"},
    "3_convergence": {"status": "in_progress", "output": null},
    "4_verification": {"status": "pending"},
    "5_constraint": {"status": "pending"},
    "6_expert_gate": {"status": "pending"}
  },
  "metrics": {
    "iterations_used": 0,
    "paths_spawned": 0,
    "conflicts_resolved": 0,
    "constraint_violations": 0
  }
}
```

### Step 4 — Checkpoint & Resume

At each stage boundary, save checkpoint:

```bash
# Save checkpoint
cp state.json tmp/pipeline/<task_name>/checkpoint_stage_3.json

# Resume from checkpoint
# Load checkpoint, restore state, continue from stage 4
```

### Step 5 — Error Handling

| Error Type | Severity | Action |
|:-----------|:---------|:-------|
| Stage timeout | Warning | Retry once, then flag |
| Stage critical failure | Fatal | Suspend pipeline, log error, wait for human |
| Non-critical check fail | Warning | Log + continue (with issue tag) |
| Token budget exceeded | Warning | Checkpoint → swap to lighter profile → resume |

## Profiles

When orchestrating, select profile based on task urgency and value:

```yaml
profiles:
  quick:         # Fast mode: single path + 2 iterations
    parallel_paths: 1
    max_iterations: 2
    quality_min_level: "C"

  standard:      # Standard mode (default)
    parallel_paths: 3
    max_iterations: 5
    quality_min_level: "C"
    sub_agent: true

  deep:          # Deep mode: multi-path + strict verification
    parallel_paths: 5
    max_iterations: 8
    quality_min_level: "B"
    sub_agent: true
    source_min_weight: 0.7
```

## Output

Final deliverable includes:
1. **Main output** (report/code/analysis — the actual deliverable)
2. **Pipeline report** (stages passed, iterations, conflicts resolved)
3. **Issues log** (all issues encountered, resolved or not)
4. **Expert sign-off** (if completed)

## Script

Scripts are in `<base_dir>/scripts/`.

```bash
# Initialize pipeline state
python3 <base_dir>/scripts/init_pipeline.py --config pipeline_config.yaml

# Resume from checkpoint
python3 <base_dir>/scripts/resume_pipeline.py --checkpoint <checkpoint.json>
```

## References

See full methodology: `knowledge/05_tools/ai-production-pipeline/ai-production-pipeline-methodology.md` (§11)

See also each stage SKILL.md for detailed stage execution instructions.
