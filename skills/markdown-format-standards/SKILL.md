---
name: markdown-format-standards
description: |-
  Enforce markdown formatting standards for monospace code blocks in Chinese tech docs.
  Use when: (1) creating or editing .md files with code-block diagrams, (2) fixing
  misaligned ASCII art caused by CJK/ASCII width mismatch, (3) reviewing markdown
  for formatting consistency, (4) running check scripts to validate file format,
  (5) generating new markdown documents that need to be rendered correctly.
  Triggers: "markdown格式", "格式规范", "对齐", "format standards", "代码块变形",
  "图形错位", "ascii art", "check format", "格式检查", "文档生成规范".
metadata:
  requires:
    bins: ["python3"]
  emoji: 📐
---

# Markdown Format Standards

> **Core rule**: When code blocks (` ``` `) are rendered in monospace fonts, Chinese characters (full-width, 2 chars wide) mixed with ASCII (half-width, 1 char wide) cause misalignment of box-drawing, arrows, and indentation. **All diagrams in code blocks must use pure English ASCII.**

## 📋 Rule Hierarchy

```
Rule Priority: R1 (must-fix) > R2 (should-fix) > R3 (nice-to-have)
```

---

### R1 ⛔ Must-Fix: Code Block Diagram Alignment

Code blocks use monospace fonts (Courier/Consolas/Monaco). **Chinese + ASCII mixed alignment always breaks.**

#### R1.1 Box-drawing characters

| ❌ BAD (breaks alignment) | ✅ GOOD (always aligns) |
|:--------------------------|:------------------------|
| `┌───┐` `│text│` `└───┘` | `+---+` `|text|` `+---+` |
| `├───┤` `└───┘` `─` `│` | `+---+` `+---+` `-` `|` |
| `━` `┃` `┏` `┛` `╋` (heavy) | `=` `|` `+` `+` `+` (simple) |

**Rule**: Replace all box-drawing Unicode with pure ASCII `+`, `-`, `|`.

❌ Bad:
```text
+------------------+
| KLX 超节点方案 |
+------------------+
```

✅ Good:
```text
+--------------------+
| KLX Supernode Plan |
+--------------------+
```

#### R1.2 Network topology / Architecture diagrams

❌ Bad: Chinese text inside box frames
```text
+---------------------+
| Spine 交换机层 |
| +----------+ |
| | Spine-1 N台 |
| +----------+ |
```

✅ Good: Pure English, Chinese explanation outside
```text
+-----------------------+
| Spine Switch Layer     |
| +------------+        |
| | Spine-1 N units|    |
| +------------+        |
+-----------------------+
```

> Chinese explanation outside code block:
> Spine 交换机层配置有 N 台 Spine 交换机...

#### R1.3 Navigation / Tree diagrams

❌ Bad: ASCII tree with Chinese
```text
+- 场景分析
+- 方案对比
+- 结论
```

✅ Good: Markdown unordered list
```markdown
- **场景分析** ← 一、场景定义（场景和硬件规格）
- **方案对比** ← 二、方案评估（含决策树）
- **结论** ← 三、统一判断
```

#### R1.4 Decision trees

❌ Bad: Box with Chinese
```text
+------------------+
| Q: 采购可行？ |
+------------------+
| +- 是 → 方案A |
| +- 否 → 方案B |
+------------------+
```

✅ Good: Pure English text box
```text
+--------------------+
| Q: Procurement OK? |
+--------------------+
| +-> YES -> Plan A  |
| +-> NO  -> Plan B  |
+--------------------+
```

#### R1.5 Proportional bars / Timelines

❌ Bad: Unicode block fillers (░█▓▌)
```text
############  <- 80%
```

✅ Good: ASCII chars (`#` for filled, `.` for empty)
```text
####################........  <- 80%
```

#### R1.6 Data flow arrows

❌ Bad: Mixed arrows
```text
GPU → SSD (中文字段) ↑ 瓶颈1
```

✅ Good: Simple English, arrows outside code block
```text
+ In code block:
GPU -> SSD (sequential read) ^

+ Chinese explanation outside:
GPU → SSD 的端到端路径中，瓶颈在 SSD 写入带宽
```

---

### R2 🟡 Should-Fix: Markdown Structure

#### R2.1 Table formatting

- Use standard markdown tables, not code-block ASCII tables
- Align columns with `:---`, `:---:`, `---:`
- Keep tables < 20 rows; split large tables

```markdown
| Left | Center | Right |
|:-----|:------:|------:|
| text | text   |  text |
```

#### R2.2 Heading hierarchy

- Single `#` = document title only (one per file)
- `##` = major sections
- `###` = subsections
- `####` = sub-subsections (use sparingly)
- No heading level skipping (e.g. `#` → `###` without `##`)

#### R2.3 Code language specification

Always specify language in code-block fences:

```markdown
```python
```bash
```text     (for ASCII art / diagrams)
```markdown (for markdown examples)
```
```

#### R2.4 Link formatting

- Use descriptive link text, not bare URLs
- Validate internal links point to existing files
- Use relative paths for intra-doc links

```markdown
✅ Good: See [Bandwidth Analysis](../chapter3/bandwidth.md)
❌ Bad: See [link](../chapter3/bandwidth.md) or https://...
```

#### R2.5 List consistency

- Use `-` for unordered lists (not `*` or `+`)
- Use `1.` for ordered lists (not `1)` or `(1)`)
- Indent sub-lists with 2 spaces
- Keep list items parallel in structure

---

### R3 🔵 Nice-to-Have: Visual Polish

#### R3.1 Image alt text

```markdown
![Descriptive alt text for accessibility](path/to/image.png)
```

#### R3.2 Table of contents

For docs > 200 lines, include a ToC after the title:

```markdown
## Table of Contents

- [Section 1](#section-1)
- [Section 2](#section-2)
  - [Subsection 2.1](#subsection-21)
```

#### R3.3 Consistent emoji usage

Use emoji as semantic markers, not decoration:

| Marker | Meaning |
|:-------|:--------|
| ✅ | Confirmed / Yes |
| ❌ | Not supported / No |
| 🟡 | Partial / Conditional |
| 🔴 | Critical / High risk |
| 🟢 | Good / Low risk |
| ⭐ | Recommended / Highlight |
| ⚠️ | Warning / Caution |

#### R3.4 Data quality stamps

Every data point should include: `value + unit + baseline + condition`

```markdown
✅: 28.9% throughput gain (vs BF16, A100, batch=32)
❌: 28.9% throughput gain (no context — meaningless)
```

---

## 🔧 Workflow: Applying Standards

### When creating new .md files

1. Plan diagrams first: decide if they belong in code blocks (needs English) or outside
2. Write Chinese explanations **outside** code blocks
3. Use pure English ASCII inside code blocks
4. Run check script: `python3 scripts/check_md_format.py <file.md>`
5. Fix all R1 issues before committing

### When fixing existing .md files

1. Run check script to identify issues
2. Fix by priority: R1 → R2 → R3
3. For each code-block diagram with Chinese:
   - Replace box-drawing chars (++++++-|) with `+` `-` `|`
   - Move Chinese text outside the block
   - Replace block filler (##|) with `#` and `.`
   - Replace tree chars (++|) with `+` `+` `|`

### Quick reference: Diagram types

| Diagram Type | Box chars? | Use English? | Example |
|:-------------|:----------:|:------------:|:--------|
| Network topology | Replace with `+` `-` `|` | ✅ Full English | `+-------+` |
| Architecture flow | Replace with `+` `-` `|` `v` `^` | ✅ Full English | `+----+ v` |
| Decision tree | Replace with `+` `-` `|` `+->` | ✅ Full English | `+-> YES ->` |
| Navigation tree | **Use markdown list** ❌ No code block | ✅ N/A | `- item` |
| Timeline | Plain `|` `#` `.` `-` | ✅ Full English | `#######.....` |
| Data flow | Simple `->` `<-` `^` `v` | ✅ Node names in English | `GPU -> SSD` |
| Bar chart | `#` `=` `.` `-` | ✅ Full English | `###..... 30%` |
| Table | **Use markdown table** ❌ No code block | ✅ Column headers in English | `| A | B |` |

---

## 🔍 Validation Cheatsheet

Before submitting a .md file, check:

1. [ ] No box-drawing Unicode (`++++++-|+=|++`) in code blocks
2. [ ] No block fillers (`###|`) in code blocks
3. [ ] All code-block text is English (numbers, units, abbreviations OK)
4. [ ] Chinese text is outside code blocks, in regular paragraphs
5. [ ] Markdown tables used instead of ASCII tables
6. [ ] Language specified in all code fences
7. [ ] Heading hierarchy has no skips
8. [ ] Internal links point to existing files
9. [ ] Markdown lists use consistent markers (`-` / `1.`)
10. [ ] Image alt text present
11. [ ] Data has unit + baseline + condition
12. [ ] File header checked for auto-generation/managed-by constraints

## 🏃 Running the Check Script

```bash
# Check a single file
python3 scripts/check_md_format.py path/to/file.md

# Check with auto-fix (R1 issues only)
python3 scripts/check_md_format.py path/to/file.md --fix

# Check all .md files in a directory
python3 scripts/check_md_format.py path/to/dir/ --recursive

# Show only R1 (must-fix) issues
python3 scripts/check_md_format.py path/to/file.md --level R1
```
