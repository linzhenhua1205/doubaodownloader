---
name: index-log-maintainer
description: |-
  ⚠️ 已废弃 — 请使用 skills/knowledge-index-manager/SKILL.md（统一索引管理技能）
  原功能（index/log 合规检查与修复）已合并至 knowledge-index-manager 的 audit/maintain 模式。
  保留本文件仅用于向后兼容，新操作请使用新技能。
---

# Index/Log Maintainer

Check and repair `index.md` / `log.md` files so every knowledge directory conforms to the per-directory rules defined in `RULE.md` and `skills/knowledge-wiki/SKILL.md`.

## The Four Rules

1. **Every directory has index.md + log.md** (except `bak/`, `oldbak/`, `import-modules/`)
2. **Only describe the own directory** — index/log must not describe subdirectory internals
3. **index.md lists only files/subdirs + summary** — NO reference relationships, cross-domain matrices, migration notes, or log-like content
4. **Format consistent with skills**:
   - index.md = table + minimal emoji (📁/📄 only)
   - log.md = heading-list (`## YYYY-MM-DD` + `- **op** | `file` — desc`), no tables, no emoji, newest-first

## Core Script

`scripts/check/index-log-normalizer.py` — the canonical tool. Reuses `extract_metadata()` from `extract-index-metadata.py` and `parse_log()` from `reformat-log.py`.

## Workflows

### 1. Check (audit) — read-only, safe

```bash
# Single directory
python scripts/check/index-log-normalizer.py knowledge/02_rd --check

# Full library (excluding bak/oldbak/import-modules)
python scripts/check/index-log-normalizer.py knowledge/ --all --check
```

Reports violations per directory; exit code 1 if any found. Violation types: missing index.md/log.md, index contains references/migration/log-like content, index describes subdirectory files, index not table-based, log contains tables/emoji.

### 2. Preview — dry-run, safe

```bash
python scripts/check/index-log-normalizer.py knowledge/ --all --dry-run
```

Shows which index.md / log.md would be rewritten and size deltas, without writing.

### 3. Init — create missing files only

```bash
python scripts/check/index-log-normalizer.py knowledge/ --all --init
```

Creates template index.md / log.md only for directories that lack them. Safe — never overwrites existing files.

### 4. Fix — rewrite to conform (DESTRUCTIVE: backs up first)

```bash
# ALWAYS dry-run first
python scripts/check/index-log-normalizer.py knowledge/ --all --dry-run

# Then fix — old files backed up to tmp/bak/index-log-fix-YYYY-MM-DD/
python scripts/check/index-log-normalizer.py knowledge/ --all --fix

# Verify
python scripts/check/index-log-normalizer.py knowledge/ --all --check
```

`--fix` regenerates index.md from the filesystem (own files + own subdirs only, extracting title/summary via `extract_metadata`), and reformats log.md to heading-list. Before overwriting index.md, it scans the old index for explicit log-like lines (bold-op bullets, 🔥 markers, op-first table rows) and merges them into log.md to preserve migration/新増 history. Cross-directory log entries are moved to a `## 待迁移` section at the bottom.

## Safety Constraints

- **dry-run before fix**: always run `--dry-run` and review before `--fix`
- **automatic backup**: `--fix` copies old index.md/log.md to `tmp/bak/index-log-fix-<date>/` mirroring relative paths
  <!-- bak/引用规则 — 备份目标路径，非引用 bak 内容 -->
- **idempotent**: running `--fix` twice produces no change on the second run (already conformant)
- **exclusions**: `bak/`, `oldbak/`, `import-modules/`, hidden dirs are always skipped
- **info preservation**: unparseable log lines are kept (emoji-stripped) under their date rather than discarded; only explicit log entries are extracted from old index.md

## Pipeline Integration

The normalizer is wired as stage 6 (`scope`) of `scripts/check/knowledge-normalizer.py`:

```bash
python scripts/check/knowledge-normalizer.py --only scope        # check
python scripts/check/knowledge-normalizer.py --only scope --fix  # fix
```

## When to Use

- After bulk imports or reorganizations that created new directories
- When `knowledge/index.md` or module indexes grow cross-references/migration noise
- Periodic health checks: `--all --check` as part of KB hygiene
- Before committing a knowledge refactor — run `--check` to catch scope violations
