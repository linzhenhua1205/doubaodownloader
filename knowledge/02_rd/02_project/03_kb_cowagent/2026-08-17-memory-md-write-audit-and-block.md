# MEMORY.md 写入场景审计与屏蔽：Deep Dream 蒸馏直写管控

> **类型**: 工程审计 + 安全加固 | **日期**: 2026-08-17 | **版本**: v1.0
> **定位**: 审计 CowAgent 中所有修改 MEMORY.md 的代码路径，确认违规直写点（Deep Dream 蒸馏），并实施双层屏蔽（代码守卫 + 配置开关）——落实 RULE.md「MEMORY.md 禁止直接编辑，走 candidate-append.py → 人工审核导入」的管控原则。
> **代码基线**: `/home/lzh/CowAgent` @ `d9b72d2`（2026-08-14）+ 本次修改
> **衔接**: RULE.md §MEMORY.md 管控 ｜ 记忆架构 [`2026-07-31-kb-retrieval-mechanism-and-enhancement-design.md`](2026-07-31-kb-retrieval-mechanism-and-enhancement-design.md)

---

## 目录

- [0. 一句话结论](#0-一句话结论)
- [1. 审计范围与方法](#1-审计范围与方法)
- [2. 修改 MEMORY.md 场景全景](#2-修改-memorymd-场景全景)
- [3. 核心违规点：Deep Dream 蒸馏直写](#3-核心违规点deep-dream-蒸馏直写)
- [4. 屏蔽实施（双层防线）](#4-屏蔽实施双层防线)
- [5. 保留的合规写入路径](#5-保留的合规写入路径)
- [6. 验证结果](#6-验证结果)
- [7. 遗留风险与建议](#7-遗留风险与建议)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 0. 一句话结论

> **CowAgent 中唯一直接覆写 MEMORY.md 的路径是 Deep Dream 记忆蒸馏（`summarizer.py` L529-540）**——它绕过 RULE.md 的管控（MEMORY.md 只能经 candidate-append.py → 人工审核导入），把 LLM 蒸馏结果整体覆写。**已实施双层屏蔽**：① 代码守卫 `memory_overwrite_blocked = True`（拦截所有触发路径，含手动 `/memory dream` 的 force=True）；② 配置开关 `deep_dream_enabled: False`（同时省掉每日 LLM 蒸馏调用）。dream diary（梦境日记）功能保留，仅禁 MEMORY.md 直写。

---

## 1. 审计范围与方法

**审计范围**: `/home/lzh/CowAgent` 全部 Python 代码中引用 `MEMORY.md` 的路径

**方法**: 全局 grep `MEMORY.md` → 按读写性质分类 → 逐点读取上下文确认写入行为 → 与 RULE.md 管控规则比对 → 判定合规性

**管控基线**（RULE.md）:

> **RULE.md §MEMORY.md 管控**: ≤5KB；禁止直接编辑，走 candidate-append.py → Candidate.md → 人工审核导入。存储规则：长期决策 | MEMORY.md | 月

**核心冲突**: CowAgent 的 Deep Dream 设计为「定期把 daily 蒸馏进 MEMORY.md」（`summarizer.py` docstring: *"Distill recent daily memories into MEMORY.md"*）——这与工作空间的 MEMORY.md 管控直接冲突。

---

## 2. 修改 MEMORY.md 场景全景

| # | 场景 | 代码位置 | 写入行为 | 合规性 |
|:-:|:-----|:---------|:---------|:-------|
| 1 | **Deep Dream 定时蒸馏**（每日 23:50） | `agent/memory/summarizer.py` L529-540 | `main_file.write_text(new_memory)` **整体覆写** | ❌ **违规**（绕过管控） |
| 2 | **手动 /memory dream** | `plugins/cow_cli/cow_cli.py` L1405/1423 → `deep_dream(force=True)` | 同上（force 绕过配置开关） | ❌ **违规** |
| 3 | 每日 flush → daily 文件 | `summarizer.py` L236/L380 | 写 `memory/YYYY-MM-DD.md` | ✅ 合规 |
| 4 | evolution executor | `agent/evolution/executor.py` L375-376 | 仅**备份** MEMORY.md，写入 daily | ✅ 合规 |
| 5 | create_memory_files_if_needed | `summarizer.py` L851 | 首次创建空文件（非覆写） | ✅ 合规 |
| 6 | 上下文注入（builder/workspace） | `agent/prompt/*` | 只读/模板，不写 | ✅ 合规 |

**结论**: 违规点收敛为**1 个函数**（`deep_dream` 的覆写段），**2 个触发入口**（定时 + 手动）。这是"单一故障点"型设计——屏蔽一处即全链路生效。

---

## 3. 核心违规点：Deep Dream 蒸馏直写

### 3.1 代码链路

**触发入口**:
- [定时] `bridge/agent_initializer.py` L673-680 — Phase 2 Deep Dream → `dream_candidate.deep_dream()`
- [手动] `plugins/cow_cli/cow_cli.py` L1405/1423 — `/memory dream` → `deep_dream(force=True)`

**执行链路**（`agent/memory/summarizer.py: deep_dream()`）:
1. L465-466 读 MEMORY.md + daily（材料收集）
2. L477-483 md5 去重（仅 hash daily_content）
3. L495-516 LLM 蒸馏（_dream_user_prompt / temperature=0.3）
4. L523 解析 [MEMORY]/[DREAM] 分节
5. L529-540 ⚠️ `main_file.write_text(new_memory)` ← 违规覆写
6. L553-558 写 dream diary（memory/dreams/YYYY-MM-DD.md）

### 3.2 违规细节

| 项 | 值 |
|:---|:---|
| 覆写函数 | `get_main_memory_file(user_id)` → 根目录 `MEMORY.md`（或 user 目录） |
| 覆写方式 | `write_text(new_memory + "\n")` —— **整体替换**（非追加） |
| 影响面 | 若 LLM 蒸馏结果质量差/截断，**原 MEMORY.md 内容永久丢失**（无版本回滚，除非 evolution 备份） |
| 配置绕过 | `deep_dream_enabled` 只挡定时；手动 `force=True` **无条件执行**（设计如此，注释明示） |
| 去重局限 | md5 仅 hash daily_content（注释解释了为何不含 memory_content——因覆写会污染 hash） |

### 3.3 与管控的冲突本质

Deep Dream 的哲学是「LLM 自主蒸馏长期记忆」；RULE.md 的哲学是「长期记忆人工审核导入」。两者对**长期记忆的写入权**有根本分歧：

| 维度 | Deep Dream 设计 | RULE.md 管控 |
|:-----|:----------------|:-------------|
| 写入者 | LLM 自主（无人工） | 人工审核（candidate-append.py 提案） |
| 写入方式 | 整体覆写 | 增量提案 |
| 风险控制 | md5 去重 + 日志 | 候选审核 + ≤5KB 限额 |
| 回滚能力 | 依赖 evolution 备份（非保证） | 提案留档可追溯 |

**判定**: 在本工作空间的管控语境下，Deep Dream 的直写应被屏蔽——不是否定蒸馏的价值（dream diary 保留），而是**长期记忆的写入权必须收归人工**。

---

## 4. 屏蔽实施（双层防线）

### 4.1 代码守卫（第一层，拦截所有路径）

`agent/memory/summarizer.py` L529-540 重构：

```python
# Overwrite MEMORY.md — BLOCKED (2026-08-17): RULE.md mandates
# MEMORY.md is managed ONLY via candidate-append.py -> manual review.
# Direct rewrite bypasses that control, so the write is disabled even
# for manual `/memory dream` (force=True). Dream diary still runs below.
memory_overwrite_blocked = True  # HARD BLOCK: do not flip without user approval
if not memory_overwrite_blocked:
    try:
        main_file = self.get_main_memory_file(user_id)
        old_size = len(memory_content)
        main_file.write_text(new_memory + "\n", encoding="utf-8")
        logger.info(...)
    except Exception as e:
        logger.warning(f"[DeepDream] Failed to write MEMORY.md: {e}")
        return False
else:
    logger.info(
        "[DeepDream] MEMORY.md overwrite BLOCKED by policy "
        "(RULE.md: managed via candidate-append.py); skipping write, "
        "keeping dream diary generation"
    )
```

**设计要点**:
- `memory_overwrite_blocked = True` 硬编码守卫——**不依赖配置文件**（防配置被误改/环境变量覆盖）
- 注释明确「HARD BLOCK: do not flip without user approval」——解除需人工决策
- blocked 时**仍继续执行 dream diary 写入**（蒸馏的"日记"价值保留）
- 写失败路径 `return False` 语义保留（仅 in not-blocked 分支）

### 4.2 配置开关（第二层，省 LLM 调用）

`config.py` L271:

```python
# 2026-08-17: DISABLED — MEMORY.md overwrite is blocked by policy in
# summarizer.py (RULE.md: managed via candidate-append.py -> manual review).
# Keeping the flag off also skips the nightly LLM call entirely.
"deep_dream_enabled": False,   # scheduled deep dream switch; manual /memory dream is unaffected
```

**作用**: 定时调度（agent_initializer）检查该开关 → False 时**连 LLM 蒸馏调用都跳过**（省 token）；代码守卫是兜底（即使有人手动改回 True，覆写仍被拦）。

---

## 5. 保留的合规写入路径

| 路径 | 文件 | 说明 |
|:-----|:-----|:-----|
| daily 记忆 | `memory/YYYY-MM-DD.md` | flush/每日摘要追加（L236/L380）——daily 文件不受管控，照常 |
| dream diary | `memory/dreams/YYYY-MM-DD.md` | Deep Dream 蒸馏的日记产物（L619）——保留 |
| 长期记忆 | `MEMORY.md` | **仅经 candidate-append.py → 人工审核导入**（工作流不变） |

---

## 6. 验证结果

| 检查项 | 结果 |
|:-------|:-----|
| `python3 -m py_compile summarizer.py` | ✅ 语法通过 |
| `python3 -m py_compile config.py` | ✅ 语法通过 |
| 全工程 grep 其他 MEMORY.md 覆写 | ✅ 无（唯一覆写点已守卫） |
| 运行时配置覆盖检查（config.json 等） | ✅ 无覆盖（默认值生效） |
| scheduler/cron 引用检查 | ✅ 无（Deep Dream 由 agent_initializer 内建定时，已拦截） |
| 修改前 cow/MEMORY.md 状态 | 7.4KB（超 5KB 上限），无 Deep Dream 痕迹——手动管控一直有效 |

---

## 7. 遗留风险与建议

1. **【中】evolution executor 的编辑能力**：`_ALLOWED_TOOLS` 含 `edit`/`write`，`_WATCH_SUBDIRS` 含 MEMORY.md——虽然当前逻辑只备份，但**若未来 evolution 策略编辑 MEMORY.md，将再次绕过管控**。建议在 evolution 的工具限制中显式排除 MEMORY.md
2. **【低】LLM 蒸馏价值保留**：Deep Dream 的蒸馏思路本身有价值——可改为「蒸馏结果写入 `memory/dreams/` + 提示人工审核」，而非直写 MEMORY.md（相当于把 Deep Dream 接入 candidate-append 流程）
3. **【低】MEMORY.md 超限**：当前 7.4KB > RULE.md 5KB 上限，建议下次人工整理时瘦身
4. **【低】文档同步**：CowAgent docs 中 Deep Dream 说明（`docs/zh/README.md` L156）与当前行为不一致，建议标注「MEMORY.md 写入已禁用」

---

## 参考来源

- [1] CowAgent 源码 @ `d9b72d2` + 本次修改：`agent/memory/summarizer.py`、`bridge/agent_initializer.py`、`plugins/cow_cli/cow_cli.py`、`config.py`、`agent/evolution/executor.py`、`agent/prompt/{builder,workspace}.py`
- [2] RULE.md §MEMORY.md 管控（≤5KB / candidate-append.py / 人工审核导入）
- [3] 知识库衔接：2026-07-31 kb-retrieval-mechanism-and-enhancement-design（记忆架构）

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-17 | v1.0 | 首次创建：MEMORY.md 写入场景全审计（6 场景）+ 核心违规点定位（Deep Dream L529-540）+ 双层屏蔽实施（代码守卫+配置开关）+ 合规路径保留（daily/dream diary）+ 4 项遗留建议 |


---

## 8. 升级：自动记忆写入重定向到 Candidate.md（2026-08-17 下午）

上一版实施的是「屏蔽」——Deep Dream 蒸馏结果被丢弃（仅 dream diary 保留）。本轮按用户需求升级为**重定向**：自动记忆写入 `Candidate.md`，MEMORY.md 彻底收归人工维护。

### 8.1 架构调整

**写路径演进**: `[旧]` LLM 蒸馏 → 覆写 MEMORY.md（违规）→ `[上一版]` 屏蔽丢弃 → `[本版]` 追加 Candidate.md
**读路径不变**: `_read_main_memory` → MEMORY.md（人工维护基线）

### 8.2 代码改动（CowAgent @ 08-17）

| 文件 | 改动 |
|:-----|:-----|
| `summarizer.py` | 新增 `get_candidate_memory_file()`（返回 Candidate.md）；deep_dream 写目标从 `get_main_memory_file()` → `get_candidate_memory_file()`；**追加模式**（`open(..., "a")`）累积提案，带时间戳分节；读路径 `_read_main_memory` 不变 |
| `workspace.py` | 中/英系统提示词：存储规则「动态记忆 → MEMORY.md」→「自动记忆提案 → Candidate.md」；目录说明 + 长期记忆段加 Candidate.md 条目与「人工维护」标注；USER.md 模板指引同步 |
| `builder.py` | 存储规则「长期核心信息 → MEMORY.md」→「Candidate.md（人工审核后并入）」；记忆文件结构说明同步 |
| `memory_search.py` | 无记忆提示语：「写入 MEMORY.md」→「写入 Candidate.md（MEMORY.md 人工维护）」 |
| `RULE.md`（工作区） | MEMORY.md 管控：**仅人工维护**，禁止 Agent 自动写入；存储规则表新增「自动记忆提案 → Candidate.md」 |

### 8.3 保持不变（符合需求）

- **加载仍读 MEMORY.md**：`workspace.py load_context_files()`、`builder.py` 全部「已自动加载」表述
- **每日对话摘要仍写 `memory/YYYY-MM-DD.md`**（不经 MEMORY.md，只在 Deep Dream 时被蒸馏）

### 8.4 注意点处理

1. **Candidate.md 懒创建**：工作区已有 Candidate.md（08-14 创建，原用途=文件修改提案）——已更新头部说明为**双用途**（文件修改提案 + 自动记忆提案），Deep Dream 首次写入自动追加
2. **记忆检索索引**（可选，未做）：`manager.py` 扫描 MEMORY.md + memory/*.md，根目录 Candidate.md **不在索引范围**——自动记忆在合并前不可检索（符合"候选"语义）。如需可检索需手动加入

### 8.5 验证

- ✅ 全工程 `compileall` 通过（exit=0）
- ✅ 读路径/写路径/追加模式静态验证通过
- ✅ 全工程无其他 MEMORY.md 自动写入点
- ✅ Candidate.md 可写、MEMORY.md md5 不变（只读基线）
