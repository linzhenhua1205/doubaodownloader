---
name: pipeline-input-qa
description: "Input quality gate for the AI production pipeline. Stage 1 of 6. Validates task inputs for completeness, source credibility, consistency, and feasibility before entering the pipeline. Use when: (1) starting a new AI-assisted task that needs quality-gated input, (2) checking input materials for completeness and source credibility, (3) asked to '质量把关' or '输入校验', (4) enhancing/patching incomplete input before processing, (5) part of pipeline-orchestrator pipeline execution. Does NOT process or generate output content — only validates/enhances input."
metadata:
  requires:
    bins: ["python3"]
---
# Input Quality Gate

**Pipeline Stage 1**: Validates and enhances input before it enters the production pipeline. "Garbage in, garbage out" — input quality directly determines the ceiling of output quality.

## Workflow

### Step 1 — Input Quality Checklist

For every incoming task, run systematic checks:

```
□ [Completeness] Task objective is clear and measurable?
□ [Completeness] Background info sufficient? (who/what/why/boundaries)
□ [Completeness] Existing materials complete? (data/docs/references)
□ [Credibility] Information sources are traceable?
□ [Credibility] Data has values + units + baseline + test conditions?
□ [Consistency] No internal contradictions in input materials?
□ [Feasibility] Can be completed within current context window/tool scope?
```

### Step 2 — Source Credibility Grading

Classify each source by credibility level:

| Level | Description | Examples | Weight |
|:-----:|:------------|:---------|:------:|
| **S** | Standards/Offi docs/Measured data | IEEE/PCI-SIG specs, chip Datasheet | 1.0 |
| **A** | Authoritative whitepapers/Top conf papers/Official reports | NVIDIA whitepapers, ODCC specs | 0.9 |
| **B** | Industry analysis/First-party tech blogs | DIGITIMES/SemiAnalysis | 0.7 |
| **C** | Self-media/Personal blogs/Unverified forums | Zhihu analysis, WeChat articles | 0.4 |
| **D** | LLM generated/Unknown origin | Assertions without citation | 0.1 |

**Grading rules**:
- Multi-path processing should use different credibility levels per path (covering S/A/B)
- Convergence uses higher-weighted sources for conflict resolution
- C/D level sources are supplementary only, not core evidence

### Step 3 — Input Enhancement (auto-triggered when quality insufficient)

1. **Missing info patching**: Identify missing dimensions → targeted search/clarify
2. **Structure normalization**: Convert unstructured input to standard format
3. **Context expansion**: Query knowledge base for relevant background
4. **Boundary clarification**: Identify ambiguous statements → generate boundary assumptions → request confirmation

### Step 4 — Gate Decision

| Verdict | Condition | Action |
|:--------|:----------|:-------|
| **🟢 Pass** | All checks pass + sources >= level C | Forward to next stage |
| **🟡 Conditional pass** | Minor issues (enhancement auto-applied) | Forward with issue log |
| **🔴 Reject** | Core checks fail / no credible sources | Return with specific rejection reason |

## Output Format

Write validated output as structured YAML in the pipeline state:

```yaml
quality_gate_result:
  verdict: "pass" | "conditional_pass" | "reject"
  source_grades:
    - source: "NVIDIA GB300 Whitepaper"
      level: "S"
      weight: 1.0
  issues:  # if conditional
    - type: "missing_data"
      detail: "Power consumption data missing, auto-patched from knowledge base"
  enhancement_log:
    - action: "context_expansion"
      detail: "Added relevant knowledge base entry on GB200 baseline"
```

## Script

Scripts are in `<base_dir>/scripts/`.

```bash
python3 <base_dir>/scripts/quality_check.py <input.json>
```

Outputs JSON with: `{verdict, source_grades, issues, enhancement_log}`.

## References

See full methodology: `knowledge/05_tools/ai-production-pipeline/ai-production-pipeline-methodology.md` (§3)
