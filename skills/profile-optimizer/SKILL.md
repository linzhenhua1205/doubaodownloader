---
name: profile-optimizer
description: "Optimize and maintain the four workspace identity files (AGENT.md, USER.md, MEMORY.md, RULE.md). Use when the user asks to: (1) optimize/restructure/slim down the workspace profile files, (2) extract user identity/patterns from conversation logs into profile files, (3) audit and fix content that's in the wrong file, (4) consolidate scattered user information into proper locations, (5) 优化身份/记忆/规则/用户文件, 重构配置文件. Do NOT use for: writing knowledge base documents, daily memory entries."
---

# Profile Optimizer

Optimize the four identity files (`AGENT.md`, `USER.md`, `MEMORY.md`, `RULE.md`) to maintain clean separation of concerns and extract patterns from conversation logs.

## File Responsibility Boundaries

Maintain these strict boundaries:

| File | Stores | Example content | Max target |
|:-----|:-------|:----------------|:----------:|
| **AGENT.md** | Agent persona & behavior | Name, role, personality traits, communication style, core principles, behavioral rules | 40 lines |
| **USER.md** | User identity & preferences | Name, domain expertise, working style, quality standards, tech focus, communication preferences | 40 lines |
| **MEMORY.md** | Long-term immutable facts | Core workflow preferences, key decisions, lessons learned, persistent system/tool facts | 50 lines |
| **RULE.md** | Workspace rules & constraints | Directory structure, file operation rules, security constraints | 60 lines |

## Workflow

### Step 1: Read Current State

Read all four files in one batch:
```bash
# Use read tool for: AGENT.md, USER.md, MEMORY.md, RULE.md
```

### Step 2: Extract Patterns from Conversation Logs

Read `conversation-log/user_indent.md` if it exists — it contains intent analysis.

Also read the last 5 daily memory files from `memory/` to extract recent behavioral patterns.

Key patterns to look for:
- **User's recurrent demands**: What topics/requests appear repeatedly?
- **Error correction patterns**: What did the user explicitly correct?
- **Quality expectations**: What standards did the user enforce?
- **Work patterns**: Does the user prefer iteration? One-shot? Detailed vs summary?
- **Tech focus**: What domains/technologies get the most attention?

### Step 3: Redistribute Content

Move content between files following the boundary table above:

**Common misplacements to fix:**
- `RULE.md` often accumulates methodology cheatsheets → move to `MEMORY.md` as working principles, or `knowledge/` as reference
- `MEMORY.md` often accumulates daily logs → move to `memory/YYYY-MM-DD.md`
- `MEMORY.md` often accumulates industry news → move to `knowledge/01_survey/` or similar
- `AGENT.md` often stays as a skeleton → enrich with behavioral patterns from user interactions
- `USER.md` often stays empty → populate from conversation-log/user_indent.md

### Step 4: Rewrite with Compact Precision

For each file:

**AGENT.md** (persona & behavior):
- Name, role, personality (keep from current)
- Communication style preferences (enrich from observed patterns)
- Core principles (extract from repeated behaviors)
- Behavioral guidelines specific to working with this user
- **Signature workflow patterns** the agent should follow

**USER.md** (identity & preferences):
- Name, domain, expertise areas
- Working style (iterative, structured, etc.)
- Quality standards enforced
- Tech focus areas & priorities
- Communication preferences (level of detail, format expectations)

**MEMORY.md** (core long-term memory):
- Working principles & analysis standards (user-enforced)
- Key decisions about workflow & system
- Persistent tool/config preferences
- Important lessons learned
- **NOT**: daily logs, industry news, temporary tracking

**RULE.md** (rules & constraints):
- Workspace directory structure (keep but simplify)
- File operation iron rules (delete, modify constraints)
- Storage rules (brief summary, reference AGENT.md for details)
- Security constraints
- **NOT**: methodology frameworks, knowledge system how-to, memory system how-to

### Step 5: Write Files

Use `write` tool for complete rewrites.

### Step 6: Sync Log

After updates, append summary to `knowledge/log.md` via `kb-log-append.py` only（`README.md`/`index.md` not touched by AI——batch-refreshed by scripts; no reserved dirs since 2026-08-19）.

## Cross-File Consistency

After rewriting, run this self-check:

1. **No duplicate content**: Same info should not appear in two files
2. **Non-contradiction**: Nothing in one file contradicts another
3. **AGENT.md ≠ USER.md**: Agent's persona is not the user's identity
4. **MEMORY.md is not RULE.md**: Facts about user/system are not operational rules
5. **Everything referenced exists**: If RULE.md mentions a directory, verify it exists

## Evaluation Criteria

| Criterion | Standard | Check |
|:----------|:---------|:------|
| **Separation** | Each file contains only its domain | Read each file — does any line belong to another file? |
| **Precision** | No filler, no vague templates | Every line carries specific information about THIS workspace |
| **Compactness** | Files are as small as possible | Can any section be merged or removed without losing info? |
| **Utility** | Each file serves its purpose when loaded into context | Would a new session benefit from this content? |
