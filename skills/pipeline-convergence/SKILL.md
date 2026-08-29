---
name: pipeline-convergence
description: "Convergence and collation engine for the AI production pipeline. Stage 3 of 6. Merges results from multiple parallel processing paths into a coherent output — resolves conflicts via weighted source credibility, selects best versions per section, and cross-validates across paths. Use when: (1) needing to merge/consolidate multiple parallel analysis results, (2) asked to '汇聚' or '冲突消解', (3) multiple outputs need systematic merging (not simple concatenation), (4) resolving contradictions between different sources/viewpoints, (5) part of pipeline-orchestrator pipeline execution. Does NOT run parallel processing nor verification — only merge."
metadata:
  requires:
    bins: ["python3"]
---
# Convergence & Collation

**Pipeline Stage 3**: Systematically merge results from multiple parallel paths. NOT simple concatenation — conflict resolution, optimal selection, and cross-validation.

## Workflow

### Step 1 — Conflict Detection

Scan all path outputs for contradictions. Classify conflicts:

| Conflict Type | Detection Method | Resolution Strategy |
|:--------------|:-----------------|:--------------------|
| **Fact conflict** | Same data, different values | Higher credibility source wins; same level → mark for verification |
| **Opinion divergence** | Same question, different conclusions | Keep both views with divergence reason noted |
| **Completeness gap** | Different coverage | Union (A has X, B has Y → merge both) |
| **Quality gap** | Same content, different depth | Pick deeper version, lower quality as supplementary notes |

**Conflict marking format**:
```markdown
> ⚠️ **Conflict marker**: Path A says X=10, Path B says X=12
> - Source difference: A cites source1(S-grade), B cites source2(A-grade)  
> - Ruling: source1 prevails, X=10
> - Confidence: High (S-grade source + reproducible)
```

### Step 2 — Optimal Merge Strategy

Select merge strategy based on output type:

| Output Type | Merge Strategy | Example |
|:------------|:---------------|:--------|
| **Report/Document** | Structured merge: per-section pick best version | Analysis report |
| **Code** | Modular merge: different paths write different modules | Microservices |
| **Data tables** | Row/column append + conflict detection | Comparison tables |
| **Charts** | Pick best: directly use the best single-path result | Architecture diagrams |
| **Opinions/Conclusions** | Synthesis: common ground + mark divergence points | Decision recommendations |

### Step 3 — Cross-Validation

For key claims spanning multiple paths:
1. Find claims that appear in ≥2 paths independently
2. Cross-validate: do they agree? If not, activate conflict resolution
3. Tag confidence level for each claim:
   - **High**: ≥3 paths agree + S/A sources
   - **Medium**: 2 paths agree + B+ sources
   - **Low**: Single path + C/D sources

### Step 4 — Output Assembly

Build final merged output with:
1. **Merged content** (by optimal merge strategy)
2. **Conflict log** (all resolved/unresolved conflicts)
3. **Confidence map** (per-section confidence estimates)
4. **Issue list** (items needing expert attention)

## Output Format

```yaml
convergence_result:
  conflicts:
    - type: "fact_conflict"
      paths: ["path_A", "path_B"]
      subject: "Peak FLOPS"
      resolution: "path_A wins (S-grade source)"
      confidence: "high"
  merge_strategy: "structured_merge"
  per_section:
    - section: "performance"
      source_path: "path_A"
      confidence: "high"
    - section: "cost"
      source_path: "path_B"
      confidence: "medium"
  issues_for_expert:
    - "Cost data from 2025Q2, verify currency"
```

## Script

Scripts are in `<base_dir>/scripts/`.

```bash
python3 <base_dir>/scripts/merge_results.py --config merge_config.json  # ⚠️ 设计承诺（结果汇聚（语义判断），当前由 LLM 按收敛规则执行）
```

## References

See full methodology: `knowledge/05_tools/ai-production-pipeline/ai-production-pipeline-methodology.md` (§5)
