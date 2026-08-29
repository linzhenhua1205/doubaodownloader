---
name: pipeline-expert-gate
description: "专家把关——AI生产流水线阶段6 of 6（终审）。自动化流程可跑99%工序，但最终责任归属和判断力在人。生成结构化专家审查清单、标注AI生成内容边界、差异化标注需要人类判断的维度、提供退回路由（退回哪个阶段+原因）。Use when: (1) 需要做最终质量把关/终审，(2) 要求'专家把关'/'专家审查'/'终审'，(3) 需要判断自动化无法验证的定性维度，(4) 检查AI产出是否可归责、边界条件是否清晰，(5) part of pipeline-orchestrator pipeline execution。不用于：自动化验证（已在Stage 4完成）、内容生成。"
metadata: {}
---
# Expert Gate

**Pipeline Stage 6 (Final)**: The human terminal. Automation runs 99% of the process, but final accountability and judgment belong to the human expert.

## Workflow

### Step 1 — Generate Expert Review Checklist

Generate a tailored checklist focusing on dimensions that **automation cannot verify**:

```
□ [Core Judgment] Are automation-unverifiable qualitative judgments correct?
   - Strategic direction correct?
   - Innovation points genuinely valuable?
   - Conclusions stand up to scrutiny?

□ [Accountability] Is output attributable?
   - Clear which parts are AI-generated vs human-modified?
   - AI-generated content flagged?

□ [Boundary Conditions] Are applicability boundaries clear?
   - Under what conditions do conclusions hold?
   - Assumptions stated?
   - Limitations noted?

□ [Deliverability] Is output ready for use?
   - Meets delivery format standards?
   - Missing any necessary info?

□ [Compliance] Ethical/regulatory risks?
   - Sensitive information involved?
   - Conclusions exaggerated?
   - Infringement risks?
```

### Step 2 — Automation vs Human Boundary Map

| Type | Handled by Automation | Handled by Expert |
|:-----|:---------------------|:------------------|
| **Fact checking** | Data consistency, format compliance, traceability | Professional judgment, strategic direction, innovation assessment |
| **Iteration** | Ralph loop auto-iteration | Which stage to return to for failed items |
| **Risk detection** | Red-line check, dependency audit, format scan | Qualitative risk assessment, business impact |
| **Modification** | Format fix, auto-source supplement, temp cleanup | Core direction adjustment, major rewrites, content decisions |

### Step 3 — Return Routing

When expert rejects, route back to the correct stage:

| Issue Type | Return To | Routing Reason |
|:-----------|:----------|:---------------|
| Input missing/inaccurate | Stage 1: QA Gate | "Source data X is incorrect, needs replacement" |
| Single dimension shallow | Stage 2: Multi-path | "Need a new perspective: regulatory analysis" |
| Poor merge/conflicts unresolved | Stage 3: Convergence | "Section A and B contradict on claim X, re-merge" |
| Core check gate failed | Stage 4: Verification Loop | "Fact accuracy check failed for section Y" |
| Constraint violation | Stage 5: Constraint | "Unapproved new dependency detected" |

## Output Format

```yaml
expert_gate_result:
  verdict: "pass" | "conditional_pass" | "reject"
  expert_notes:
    - dimension: "core_judgment"
      assessment: "Approved - conclusions well-supported"
    - dimension: "accountability"
      assessment: "Approved - AI sections clearly marked"
  if_rejected:
    return_to_stage: 3
    reason: "Section A data conflict with knowledge base"
    recommended_action: "Re-merge with knowledge base as additional path"
  sign_off:
    expert: "[name]"
    date: "2026-07-10"
    signature_required: true
```

## Script

Scripts are in `<base_dir>/scripts/`.

```bash
python3 <base_dir>/scripts/generate_checklist.py <input.json>  # ⚠️ 设计承诺（专家清单生成（语义判断），当前由 LLM 按模板生成）
```

## References

See full methodology: `knowledge/05_tools/ai-production-pipeline/ai-production-pipeline-methodology.md` (§8)
