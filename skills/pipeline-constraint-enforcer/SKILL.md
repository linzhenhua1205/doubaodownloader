---
name: pipeline-constraint-enforcer
description: "约束体系引擎——AI生产流水线阶段5 of 6。三层约束模型强制执行：安全红线（不可触碰）、质量标线（必须遵守）、工程约束（最佳实践）。自动检测约束失效模式（中间文件污染/依赖膨胀/复用不足/术语不一致等）。解析.agignore、审计依赖、校验格式。Use when: (1) 需要对输出做约束合规检查，(2) 要求'约束检查'/'安全红线'/'依赖审计'，(3) 检查是否遵守.agignore规则，(4) 检测复用不足或重复造轮子，(5) 项目需风格一致性校验，(6) part of pipeline-orchestrator pipeline execution。不用于：内容质量判断、创新性评估。"
metadata:
  requires:
    bins: ["python3"]
---
# Constraint Enforcer

**Pipeline Stage 5**: The deterministic skeleton of the pipeline. Enforces three-layer constraint model so that AI's non-deterministic intelligence operates within a controlled boundary.

## Three-Layer Constraint Model

```
┌───────────────────────────────────────────────┐
│  Layer 1: Safety Red-Line (NEVER touch)        │
│  - NEVER delete critical files                 │
│  - NEVER write API keys/tokens to output       │
│  - NEVER execute operations affecting production│
├───────────────────────────────────────────────┤
│  Layer 2: Quality Baseline (MUST follow)        │
│  - Output MUST have TOC/cross-links/changelog   │
│  - Claims MUST have source citations (S/A pref) │
│  - Data MUST have values+units+baseline+conditions│
├───────────────────────────────────────────────┤
│  Layer 3: Engineering Best Practice             │
│  - Reuse existing components (check inventory)  │
│  - New dependencies need approval               │
│  - Clean intermediate artifacts                 │
│  - Consistent style (terms/numbers/formatting)  │
└───────────────────────────────────────────────┘
```

## Constraint Failure Modes

| Failure Mode | Manifestation | Detection | Handling |
|:-------------|:--------------|:----------|:---------|
| **Temp file pollution** | Lots of uncleaned temp files | File diff (end vs start) | Auto-clean script |
| **Dependency inflation** | Continuously adding deps | `check_reuse.py` | New deps need approval |
| **Architecture drift** | Gradual deviation from initial design | Design consistency check | Rollback to checkpoint |
| **Reuse failure** | Reinventing the wheel | AST function name dedup | Tag + replacement suggestion |
| **Style inconsistency** | Multiple styles in same project | Lint scan | Auto-format |
| **Term inconsistency** | Different terms for same concept | Term consistency check | Auto-replace with standard |
| **Claim without source** | Conclusion without citation | Citation integrity check | Return for sourcing |

## `.agignore` Template

```gitignore
# .agignore — AI behavior constraint file

# --- Safety Red-Line (NEVER touch) ---
config/secret*
*.key
production/*

# --- Avoid temp file pollution ---
*.bak
*.swp

# --- AI writable directories only ---
# WORK_DIRS: src/, docs/, tests/, tmp/

# --- Custom rules ---
# NEW_DEPENDENCY_APPROVAL_REQUIRED: true
# MAX_NEW_FILES_PER_SESSION: 5
```

## Component Inventory Template

```markdown
# Project Component Inventory

> AI MUST check this first before writing any code — reuse existing components.

## Core Utils
| Component | Path | Function | Last Updated |
|:----------|:-----|:---------|:-------------|

## Dependencies (Approved)
| Package | Version | Purpose | Approval Date |
|:--------|:--------|:--------|:--------------|

## Reusable Patterns
| Pattern | Location | Scenario |
|:--------|:---------|:---------|
```

## Output Format

```yaml
constraint_result:
  layers:
    layer_1_safety:
      status: "pass"
      violations: []
    layer_2_quality:
      status: "conditional_pass"
      violations:
        - type: "missing_cross_links"
          severity: "minor"
          auto_fixed: true
    layer_3_engineering:
      status: "pass"
      violations: []
  auto_fixes_applied: 2
  issues_for_expert: []
  overall_verdict: "pass"
```

## Script

Scripts are in `<base_dir>/scripts/`.

```bash
# Check new code for reuse violations + dependency audit
python3 <base_dir>/scripts/check_reuse.py <file_path>

# Enforce .agignore rules on file operations
python3 <base_dir>/scripts/enforce_agignore.py --path <project_dir>  # ⚠️ 设计承诺（约束强制（部分可脚本化），当前由 LLM 按约束清单执行）
```

## References

See full methodology: `knowledge/05_tools/ai-production-pipeline/ai-production-pipeline-methodology.md` (§7)

See also: `RULE.md` (workspace rules), `.agignore` (project-specific constraints)
