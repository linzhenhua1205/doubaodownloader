---
name: evolver
description: Agent自进化引擎。让你的AI助手越用越聪明——自动识别短板、优化策略、迭代进化。基于GEP基因组进化协议，实现协议约束下的自主进化。
user-invocable: true
---

# 🧬 Evolver

**"Evolution is not optional. Adapt or die."**

The Evolver is a meta-skill that allows AI agents to inspect their own runtime history, identify failures or inefficiencies, and autonomously write new code or update their own memory to improve performance.

## Features

- **Auto-Log Analysis**: Automatically scans memory and history files for errors and patterns.
- **Self-Repair**: Detects crashes and suggests patches.
- **GEP Protocol**: Standardized evolution with reusable assets.
- **One-Command Evolution**: Just run `/evolve`.

## Usage

### Standard Run (Automated)
Runs the evolution cycle. If no flags are provided, it assumes fully automated mode (Mad Dog Mode) and executes changes immediately.
```bash
/evolve
```

### Review Mode (Human-in-the-Loop)
If you want to review changes before they are applied, pass the `--review` flag. The agent will pause and ask for confirmation.
```bash
/evolve --review
```

### Mad Dog Mode (Continuous Loop)
To run in an infinite loop (e.g., via cron or background process), use the `--loop` flag.
```bash
/evolve --loop
```

## Setup

### Environment Variables

```bash
export GEP_ASSETS_DIR=skills/evolver/assets/gep
export EVOLVE_STRATEGY=balanced
export EVOLVER_ROLLBACK_MODE=stash
```

Or in your agent config:

```json
{
  "env": {
    "GEP_ASSETS_DIR": "skills/evolver/assets/gep",
    "EVOLVE_STRATEGY": "balanced"
  }
}
```

## Configuration

### Required Environment Variables

| Variable | Default | Description |
|---|---|---|
| `GEP_ASSETS_DIR` | `skills/evolver/assets/gep` | Path to GEP gene/capsule/event data |

### Optional Environment Variables

| Variable | Default | Description |
|---|---|---|
| `EVOLVE_STRATEGY` | `balanced` | Evolution strategy: balanced, innovate, harden, repair-only |
| `EVOLVER_ROLLBACK_MODE` | `hard` | Rollback strategy on failure: hard, stash, none |
| `EVOLVER_LLM_REVIEW` | `0` | Set to 1 to enable second-opinion LLM review before solidification |
| `EVOLVER_AUTO_ISSUE` | `0` | Set to 1 to auto-create GitHub issues on repeated failures |
| `RANDOM_DRIFT` | `0` | Enable random drift in evolution strategy selection |

## GEP Genome Evolution Protocol

### Gene Structure
```json
{
  "gene_id": "gene_xxxxxxxx",
  "name": "Error Recovery - API Timeout",
  "trigger_pattern": "TimeoutError|api_timeout",
  "modification": "When API timeout occurs, implement retry mechanism with exponential backoff",
  "validation_command": "python -m pytest tests/test_retry.py -v",
  "confidence": 0.85,
  "category": "reliability"
}
```

### Capsule Structure
```json
{
  "capsule_id": "capsule_error_recovery",
  "name": "Error Recovery Capsule",
  "genes": ["gene_timeout_retry", "gene_connection_retry", "gene_degradation_switch"],
  "description": "Collection of genes for handling runtime errors and failures"
}
```

### Evolution Event Structure
```jsonl
{"event_id": "event_001", "timestamp": "2026-06-27T10:00:00", "trigger": "API timeout in session 2026-06-27", "gene_selected": "gene_timeout_retry", "validation_result": "PASS", "applied": true}
```

## Evolution Strategies

| Strategy | Innovation | Optimization | Repair | Use Case |
|---|---|---|---|---|
| **balanced** | 50% | 30% | 20% | Daily operation (default) |
| **innovate** | 80% | 10% | 10% | Stable systems, accelerate exploration |
| **harden** | 20% | 40% | 40% | Post-major changes, need convergence |
| **repair-only** | 0% | 0% | 100% | Emergency fix mode |

## Working Mechanism

### Step 1: Log Scanning
Scans `conversation-log/` directory for session records, identifying:
- Error patterns and crashes
- Performance bottlenecks
- User feedback and satisfaction
- Skill usage frequency and success rates

### Step 2: Gene Matching
Matches identified issues against genes in `assets/gep/genes.json`, selecting the most appropriate evolution strategy.

### Step 3: Validation
Executes validation commands to ensure proposed changes are safe and effective.

### Step 4: Application
Applies changes to:
- `skills/` directory for skill updates
- `RULE.md` for guideline injections
- `MEMORY.md` for memory updates
- `conversation-log/user_indent.md` for intent analysis improvements

### Step 5: Event Logging
Records the complete evolution event in `assets/gep/events.jsonl` for audit trail.

## Project Path Mapping

| OpenClaw Path | This Project Equivalent |
|---|---|
| `~/.openclaw/agents/` | `conversation-log/` |
| `AGENTS.md` | `.trae/rules/RULE.md` |
| `SOUL.md` | `MEMORY.md` |
| `~/.evomap/node_id` | `skills/evolver/assets/gep/node_id` |
| `GEP_ASSETS_DIR` | `skills/evolver/assets/gep/` |

## Directory Structure

```
evolver/
├── SKILL.md                    # This file
├── assets/
│   └── gep/
│       ├── genes.json          # Reusable logic and behavior definitions
│       ├── capsules.json       # Successful reasoning patterns
│       ├── events.jsonl        # Append-only audit trail
│       └── node_id             # Node identity persistence
├── memory/                     # Evolution memory, narrative, reflection logs
│   ├── narrative.log           # Detailed narrative logs
│   └── reflection.log          # Reflection and insights
├── scripts/                    # Evolution scripts
│   ├── scan_logs.py            # Scan conversation logs for patterns
│   ├── match_genes.py          # Match issues against gene library
│   ├── apply_changes.py        # Apply evolution changes
│   └── validate.py             # Validate proposed changes
└── references.md               # Reference documentation
```

## Safety Mechanisms

- **No Auto Code Execution**: Only generates guidance and suggestions
- **Auditable Logs**: Complete evolution event tracking
- **Rollback Support**: git stash/hard reset for failed evolutions
- **Permission Control**: Configurable self-modification permissions

## Shell Commands Used

| Command | Purpose |
|---|---|
| `git checkout`, `git log`, `git status`, `git diff` | Version control for evolution cycles |
| `git reset --hard` | Rollback failed evolution (when EVOLVER_ROLLBACK_MODE=hard) |
| `git stash` | Preserve failed evolution changes (when EVOLVER_ROLLBACK_MODE=stash) |

## File Access

| Direction | Paths | Purpose |
|---|---|---|
| Read | `conversation-log/` | Session history analysis |
| Read | `skills/` | Skill inspection |
| Read | `assets/gep/*` | GEP gene/capsule/event data |
| Read | `memory/*` | Evolution memory |
| Write | `assets/gep/*` | Updated genes, capsules, evolution events |
| Write | `memory/*` | Memory graph, narrative log |
| Write | `skills/` | Evolved skills |
| Write | `RULE.md` | Injected guidelines |

## Output

- **Evolution Report**: Summary of identified issues and applied fixes
- **Gene Updates**: Modified or new genes in `assets/gep/genes.json`
- **Event Log**: Complete audit trail in `assets/gep/events.jsonl`
- **Skill Updates**: Enhanced skills in `skills/` directory
- **Guideline Updates**: Updated `RULE.md` with new best practices

## Tips

1. Run `/evolve --review` first to see what changes will be made
2. Start with `EVOLVE_STRATEGY=balanced` for daily use
3. Use `EVOLVE_STRATEGY=repair-only` for emergency situations
4. Check `assets/gep/events.jsonl` for complete audit trail
5. Regularly review and clean up ineffective genes
