---
name: arch-presentation-builder
description: Generate PPT-style architecture review presentation materials from technical analysis data. Use when: (1) user asks to generate/create/revise a汇报材料/汇报/报告 from an architecture review document, (2) user has a .html or .md analysis document and wants PPT-style presentation output, (3) user needs MECE-structured competitive analysis that decomposes from market to R&D metrics, (4) user wants indicators broken down from user-facing to technical R&D level with same-dimension comparisons, (5) user mentions 汇报/汇报材料/汇报PPT/指标体系/竞争力拆解. Do NOT use for: general document writing, simple data summarization, creative writing, or slides that are not architecture-review oriented.
---

# Architecture Review Presentation Builder

## Overview

Generate PPT-style architecture review presentation materials (HTML slide deck) with a strict top-down decomposition structure:
**Market Positioning → User-Facing Indicators → System-Level Indicators → R&D-Level Indicators**

Each level maps to the next via causal/driving relationships. All comparisons are **same-dimension** (compare capability to capability, not capability to solution). Data must be traceable to source documents. Unverified data must be explicitly tagged.

## Principles (Enforce Always)

### P1: Top-Down Decomposition Chain
```
Market Positioning (why this matters)
  → User-Facing Indicators (what users see/feel)
    → System-Level Indicators (how the system delivers)
      → R&D-Level Indicators (what engineers build/measure)
```

Each level **drives** the next. A change in lower level propagates upward quantifiably.

### P2: Same-Dimension Comparison
**Never compare capability vs solution.** Examples:
- ✅ Correct: KLX HBM BW 1,889 TB/s vs H100 HBM BW 1,809 TB/s (same dimension: BW)
- ❌ Wrong: KLX HBM capacity advantage vs H100 NVLink speed (different dimensions)
- ✅ Correct: KLX Scale-Out 380 Gbps/GPU vs H100 Scale-Out 200 Gbps/GPU (same dimension: per-GPU BW)
- ❌ Wrong: KLX more GPU memory vs H100 has faster interconnect (mixing capability dimensions)

**Comparison template**:
```
<System A> <metric> <value> vs <System B> <same metric> <value> → <conclusion>
```

### P3: MECE Structure
- **Mutually Exclusive**: No overlap between categories (e.g., don't have "成本" and "TCO" as separate sections)
- **Collectively Exhaustive**: Cover all relevant dimensions for the claim being made
- **Check before output**: Scan each category pair for overlap

Standard MECE dimensions for architecture review:
```
┌─ Tier 1: 算力 (Compute)     ─ raw FLOPS, HBM BW, capacity
├─ Tier 2: 吞吐 (Throughput)  ─ effective tok/s, MFU, scaling efficiency
├─ Tier 3: 成本 (Cost)        ─ $/Token, TCO, $/GPU-hr
├─ Tier 4: 效率 (Efficiency)  ─ MFU decomposition, comm ratio
├─ Tier 5: 可靠 (Reliability) ─ Goodput, MTBF, CKPT recovery
└─ Tier 6: 诊断 (Diagnostics) ─ MTTD, fault domain, diagnostic density
```

### P4: Data Source Tracing
Every quantified value must be traceable:
- Source document path (relative from knowledge/)
- Confidence tag (see below)
- If from calculation: show method / formula reference

### P5: Confidence Tags (Mandatory)
Every quantified indicator must carry one of four tags:

| Tag | Label | Meaning | Color |
|:---|:------|:--------|:------|
| `conf-verified` | ✅ 已验证 | Closed-form formula + public data cross-validated | green |
| `conf-est` | 📐 合理估计 | Reasonable assumption, no public data | blue |
| `conf-bound` | ⚠️ 边界敏感 | Depends on key assumptions | yellow |
| `conf-tbd` | ❓待验证 | No production data yet, theoretical only | gray |

### P6: Slide Limit
Total slides ≤ 15. Each slide = one clear message.

## Output Format

Generate a **single self-contained HTML file** with:
- Slide-based layout (each `<div class="slide">` = one page)
- Dark theme (dark background, readable contrast)
- Navigation bar at top (anchor links to each slide)
- CSS-inlined, no external dependencies
- Tables, bar charts, highlight boxes for visual structure
- Print-friendly: each slide ≤ 1 screen height where possible

## Standard Workflow: 15-Slide Structure

### 1. Title Slide (Slide 1)
- Title: architecture name + "体系化架构评审汇报"
- Subtitle: one-line positioning
- Metadata: GPU count, TCO range, target scenarios
- Confidence legend (4 tags)

### 2. Executive Summary (Slide 2)
- 3-5 bullet points: what makes this architecture win/lose
- One table: Top 3 strengths × Top 3 risks
- **No new data here** — summarize from later slides

### 3. Market Positioning & Scenario Map (Slide 3)
- Which market segments this targets
- Competitiveness landscape: 5-star rating per scenario
- **Source**: evaluation documents, market analysis

### 4. Competitiveness Pyramid (Slide 4)
- 5-layer pyramid: 算力 → 吞吐 → 效率 → 成本 → 可靠
- Each layer: key indicator + value + confidence tag
- Dashed line: H100 baseline comparison
- **MECE check**: no overlapping layers

### 5. Top-Down Indicator Decomposition (Slide 5)
- Sankey-style or chain diagram showing:
  `Market → User → System → R&D`
- At each level: 3-5 key indicators
- Arrows with "drives" / "limits" labels
- **Key**: show the causal chain, not just enumeration

### 6. Compute & Memory Tier (Slide 6)
| Indicator | KLX | H100 | Ratio | Tag |
|:----------|:---|:-----|:-----:|:---:|
| BF16 TFLOPS | 332.8 PF | 504 PF*8 | 0.66× | ✅ |
| HBM BW | 1,889 TB/s | 1,809 TB/s | 1.04× | ✅ |
| HBM Capacity | 72 TB | 40.9 TB | 1.76× | ✅ |

*8× PCIe connected H100, not NVLink

### 7. Throughput Decomposition (Slide 7)
- Training throughput: peak vs effective
- Inference throughput: online vs batch vs long-context
- **All same-dimension**: KLX tok/s vs H100 tok/s for same model/batch

### 8. Efficiency Analysis (Slide 8)
- MFU decomposition: η_total = η_compute × η_comm × η_memory × η_overlap
- KLX vs H100 at each factor
- Comm ratio breakdown: NVLink 0% vs 100% on Scale-Out
- **Tags on all η values**

### 9. Cost & TCO (Slide 9)
- 3-year TCO breakdown: hardware + power + network
- $/Token comparison
- **Data source**: chip pricing estimates → tag as ⚠️ or ❓
- Sensitivity: what if GPU price changes ±20%

### 10. Reliability & Diagnostics (Slide 10)
- Goodput estimation
- MTBF, CKPT recovery time
- **Competitive advantage**: fault domain size comparison
- Diagnostic capability: KLX vs H100 per dimension table

### 11. Risk Matrix (Slide 11)
- Top 6-8 risks sorted by probability × impact
- Include confidence assessment
- **Clear separation**: technical risk vs market risk vs timeline risk

### 12. Architecture Decision Matrix (Slide 12)
- 8-10 scenarios × 5-star rating
- One-line recommendation per scenario
- **Link back to Slide 3** Market Positioning

### 13. Key Differentiators (Slide 13)
- Top 3 things KLX does better than H100
- Top 3 things KLX is worse at
- **Honest assessment**: no marketing fluff
- Each claim has data backing

### 14. Data Confidence Summary (Slide 14)
- What's verified ✅, what's estimated 📐, what's uncertain ⚠️❓
- If any P0 data is ❓ → this is a **risk flag** for the review
- Next steps: what data to prioritize for validation

### 15. Conclusions & Recommendations (Slide 15)
- **Clear verdict**: invest / hold / avoid
- Recommended: top 2-3 use cases
- Not recommended: which scenarios to avoid
- **One actionable takeaway** for the decision maker

## Integration with Source Documents

When generating from existing analysis, follow:

1. Read the source document (the .html or .md file)
2. Map its content to the 15-slide structure above
3. Extract quantified indicators with their confidence tags
4. Identify gaps — if a required indicator is missing, note as ❓待验证
5. Check MECE — if two slides have overlapping content, merge or split
6. Check same-dimension — if comparison mixes dimensions, fix
7. Generate the HTML

## HTML Template Elements

Use these CSS classes (same as existing arch-review HTML):
- `.slide` — each page
- `.grid2`, `.grid3`, `.grid4` — grid layouts
- `.card` — info card with `.label` / `.value` / `.unit`
- `.val-good` (green), `.val-warn` (yellow), `.val-danger` (red), `.val-accent` (blue)
- `.badge-good`, `.badge-warn`, `.badge-danger`, `.badge-info`, `.badge-tbd`
- `.conf-tag .conf-verified` (✅), `.conf-est` (📐), `.conf-bound` (⚠️), `.conf-tbd` (❓)
- `.verdict-box verdict-pass/warn/fail` — conclusion boxes
- `.highlight` — key insight boxes
- `.method-box` — methodology explanation
- `.diagram` — monospace ASCII diagrams
- `nav` — fixed top navigation bar with anchor links
- `.footer` — document footer

## Self-Check Before Output

Before delivering the final HTML, scan:
- [ ] ≤ 15 slides
- [ ] Every quantified value has a confidence tag
- [ ] No mixed-dimension comparisons (P2)
- [ ] No overlapping MECE categories (P3)
- [ ] Each data point traceable to source (P4)
- [ ] Clear conclusion with actionable recommendation
- [ ] Navigation bar links work
- [ ] HTML closes properly (count `<div>` vs `</div>`)
