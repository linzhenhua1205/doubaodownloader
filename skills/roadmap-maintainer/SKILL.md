---
name: roadmap-maintainer
description: Maintain and restructure the server product R&D knowledge roadmap (knowledge/server_design_roadmap.md). Use when (1) adding new domains or restructuring the 14-domain × lifecycle matrix, (2) moving version history/changelog to bottom, (3) adding/verifying cross-links to knowledge base files, (4) updating the coverage heatmap, (5) cleaning up misplaced sections or formatting inconsistencies in the roadmap file.
metadata:
  requires:
    bins: ["python3"]
---

# Roadmap Maintainer

Maintain `knowledge/server_design_roadmap.md` — the 14-domain × IPD lifecycle matrix that serves as the master index for server product R&D knowledge.

## Structure Conventions

### File Architecture

```
server_design_roadmap.md
├── 🏗️ Header (brief: version + date + coverage count)
├── 📐 Matrix overview (ASCII table)
├── 📑 TOC
├── ①-⑭ Domain sections (ordered by domain number)
│   ├── P0/P7 lifecycle subsections
│   │   ├── File links (markdown table)
│   │   ├── ⭐ Activity tables (engineering activities)
│   │   ├── ⬜ Placeholder entries (待填充)
│   │   └── Tracking log links
│   └── ...
├── 📋 Appendix A: Coverage heatmap
├── 📋 Appendix B: Tracking log index
├── 📋 Appendix C: Changelog (version history)
└── 📋 Usage guide (footer)
```

### Header Format

Keep the header concise (≤6 lines). Version detailed log goes to Appendix C:

```markdown
> **版本**: v{version} | **更新**: {YYYY-MM-DD}
> **覆盖**: 14大领域 × TR1-TR6 + P0/P7 | **映射文件**: ~500+
```

### Section Anchor Format

Domain sections use level-2 headings with consistent format:

```markdown
## {N}. {Domain Name} ({Abbreviation})
```

Each domain section starts with:
- **核心职责**: One-line summary
- **IPD参与**: TR-stage participation

### Activity Table Format

Use ⭐ to mark engineering detail tables:

```markdown
**✦ {Activity Name}** ⭐

| {Col1} | {Col2} | {Col3} |
|:-------|:-------|:-------|
```

### Placeholder Format

```markdown
⬜ **{Title} ({Stage} 待填充)**
```

### Link Format

All links are relative to `knowledge/` directory:
```markdown
[Display Text](subdirectory/file.md)
[Display Text](subdirectory/)  — for directories
```

External links (../import/) use full relative path from knowledge/.

## Changelog Maintenance

### Header Version Line

```markdown
> **版本**: v3.10（简要描述本次更新的主要内容）
```

### Appendix C — Changelog Entry Format

List entries in reverse chronological order (newest first):

```markdown
## 附录 C：变更日志

### v3.10 - 2026-06-25
- **格式重构**: 移动版本日志至附录C；修复HW/FW域间缺失的section错位；精简header
- **HW域**: 新增{具体内容}
- **PROD域**: 新增{具体内容}
```

Each entry should be concise (2-5 bullets). Detailed content descriptions go in the domain sections themselves.

## When Adding New Domains

1. Choose next available domain number (currently ①-⑭)
2. Add to the matrix ASCII table in the overview section
3. Add to the TOC
4. Create the domain section with consistent formatting
5. Update Appendix A (coverage heatmap)
6. Update Appendix B (tracking log index) if applicable
7. Update the header file count

## Link Verification

When verifying links:
- Knowledge base links: use relative path from `knowledge/`
- Skills links: use `../skills/...` path
- Import links: use `../import/...` path
- All links should be verified with `bash` commands

## Script Usage

### validate_structure.py

Run to verify the file's structural integrity:

```bash
python3 skills/roadmap-maintainer/scripts/validate_structure.py
```

Checks:
- All 14 domain sections exist and are numbered correctly
- Changelog is at the bottom (not in header)
- No duplicate section headers
- No misplaced sections between domains
- Link format consistency
