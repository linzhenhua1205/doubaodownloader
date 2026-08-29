# Git 工具集

跨平台的 Git 辅助脚本集合，解决网络不稳定环境下的推送/提交问题。

## 脚本清单

| 脚本 | 功能 | 用法 |
|:-----|:-----|:-----|
| `git-auto-commit.py` | **AI 自动提交**（规范 message + AI/人工身份区分） | `python git-auto-commit.py -m "..."` |
| `git-push-robust.py` | 可靠推送（多策略+重试+诊断） | `python git-push-robust.py --help` |
| `git-pull-robust.py` | 可靠拉取（多策略+重试+stash+clone） | `python git-pull-robust.py --help` |

---

## git-auto-commit.py

**AI 操作文件后的自动提交脚本** — 规范 commit message + 区分 AI/人工提交。

### 为什么需要

- 过去 AI 完成文件操作后不自动提交，提交由外部/手动完成，message 简单（如 `jbof, kv cache, zhbm`），且**无法区分哪些是 AI 提交、哪些是人工提交**，追溯困难。
- 本脚本让 AI 在每批文件操作收尾时显式调用，自动：`git add` → 推断 type/scope → 生成规范 message（含文件清单 body）→ 以 **AI 独立身份**提交。

### 区分机制（双保险）

| 维度 | AI 提交（默认） | 人工提交（`--manual` 或直接 `git commit`） |
|:-----|:---------------|:------------------------------------------|
| author/committer | `cowagent <cowagent@cowkb.local>` | 本机 git config（`linzhenhua1205`） |
| message 前缀 | `[AI]` | `[manual]` / 无前缀 |
| 查看方式 | `git log --format="%an | %s"` 按作者筛选 | 同左 |

### 快速使用

```bash
# 默认：add 全部 + 自动推断 type/scope + AI 身份提交（不推送）
python scripts/git/git-auto-commit.py -m "FMS P2 系列 DRAM 供给传导深度分析"

# 指定类型/范围 + 附加说明（来源/质量结果进 body）
python scripts/git/git-auto-commit.py -t knowledge -s 03_AI \
    -m "zHBM 对超节点散热设计影响" -n "一手来源 StorageReview; md-format 0 问题"

# 只提交指定文件/目录
python scripts/git/git-auto-commit.py --paths "knowledge/03_AI/train/ai-storage/" -m "..."

# 提交后推送（复用 git-push-robust.py 多策略）
python scripts/git/git-auto-commit.py -m "..." --push

# 人工规范提交（本机身份 + [manual] 前缀）
python scripts/git/git-auto-commit.py -m "..." --manual

# 预览不执行
python scripts/git/git-auto-commit.py -m "..." --dry-run
```

### commit message 规范

```text
[AI] knowledge(03_AI): FMS 会后系列 P0+P2+T25 六篇深度分析归档

一手来源 STH/StorageReview/TrendForce; md-format 0 问题 + link-validator 0 问题

变更统计:
  knowledge/03_AI/train/ai-storage/2026-08-06-xxx.md | 390 +++++
  1 file changed, 390 insertions(+)

新增 (1):
- knowledge/03_AI/train/ai-storage/2026-08-06-xxx.md
```

- **type 取值**：`knowledge / docs / feat / fix / chore / refactor / memory / spec`
- **scope 自动推断**：`02_rd / 03_AI / 04_person / 05_tools / 06_others / 07_industry-research / 01_survey / weekly-reports / meta / daily / scripts / skills / spec / logs ...`
- 未指定 `-m` 时自动生成 `<type>(<scope>): N files updated`

### 参数说明

| 参数 | 说明 | 默认值 |
|:-----|:-----|:------:|
| `-m / --message` | commit summary（建议必填） | 自动生成 |
| `-t / --type` | commit 类型 | 路径自动推断 |
| `-s / --scope` | commit 范围 | 路径自动推断 |
| `-n / --note` | body 附加说明 | 无 |
| `--paths` | 仅提交指定路径（可多次） | `git add -A` 全部 |
| `--push` | 提交后调用 git-push-robust.py | False |
| `--manual` | 人工提交（本机身份 + `[manual]`） | False（AI 身份） |
| `--dry-run` | 仅预览不执行 | False |

## git-push-robust.py

解决 GitHub 网络问题导致的推送失败。

### 特性

- **3 策略自动切换**：HTTPS 直连 → SSH 协议 → HTTPS+代理
- **指数退避重试**：4s → 6s → 10s → 18s → 34s
- **自动代理检测**：扫描 7890/1080/10808 等常见端口
- **Git 配置优化**：500MB 缓冲 + 低压缩 + 10 分钟超时
- **网络诊断**：DNS/HTTPS/SSH/代理端口一键检测
- **纯标准库**：无需 pip install 任何依赖

### 快速使用

```bash
# 推送当前分支
python scripts/git/git-push-robust.py

# 先 commit 再 push
python scripts/git/git-push-robust.py --commit -m "update docs"

# 指定代理推送
python scripts/git/git-push-robust.py --proxy http://127.0.0.1:7890

# 诊断网络问题
python scripts/git/git-push-robust.py --diagnose

# 指定分支 + 10次重试 + 强制推送
python scripts/git/git-push-robust.py -b main -n 10 --force
```

### 参数说明

| 参数 | 说明 | 默认值 |
|:-----|:-----|:------:|
| `-b / --branch` | 目标分支 | 当前分支 |
| `-n / --max-retries` | 每策略最大重试次数 | 5 |
| `--proxy` | 指定代理地址 | 自动检测 |
| `--commit` | 推送前先 commit | False |
| `-m / --message` | commit 消息 | 时间戳 |
| `--diagnose` | 仅诊断不推送 | False |
| `--force` | 强制推送 | False |
| `-r / --remote` | 远程仓库名 | origin |

---

## git-pull-robust.py

解决 GitHub 网络问题导致的 pull/fetch/clone 失败。

### 特性

- **3 策略自动切换**：HTTPS 直连 → SSH 协议 → HTTPS+代理
- **指数退避重试**：4s → 6s → 10s → 18s → 34s
- **自动代理检测**：扫描 7890/1080/10808 等常见端口
- **工作区安全检查**：拉取前检测未提交变更，防止覆盖
- **自动 stash**：`--stash` 自动暂存/恢复
- **冲突检测**：CONFLICT 时立即停止，提示手动解决
- **支持 clone**：`--clone` 模式支持克隆远程仓库
- **纯标准库**：无需 pip install 任何依赖

### 快速使用

```bash
# 拉取当前分支
python scripts/git/git-pull-robust.py

# 指定分支拉取
python scripts/git/git-pull-robust.py -b main

# 仅 fetch 不 merge
python scripts/git/git-pull-robust.py --fetch

# pull --rebase
python scripts/git/git-pull-robust.py --rebase

# 自动 stash 后拉取
python scripts/git/git-pull-robust.py --stash

# 指定代理
python scripts/git/git-pull-robust.py --proxy http://127.0.0.1:7890

# 克隆仓库
python scripts/git/git-pull-robust.py --clone https://github.com/user/repo.git

# 诊断网络
python scripts/git/git-pull-robust.py --diagnose
```

### 参数说明

| 参数 | 说明 | 默认值 |
|:-----|:-----|:------:|
| `-b / --branch` | 目标分支 | 当前分支 |
| `-n / --max-retries` | 每策略最大重试次数 | 5 |
| `--proxy` | 指定代理地址 | 自动检测 |
| `--fetch` | 仅 fetch 不 merge | False |
| `--rebase` | pull --rebase（默认 merge） | False |
| `--stash` | 自动 stash 未提交变更 | False |
| `--clone URL` | 克隆模式 | — |
| `-d / --dir` | clone 目标目录 | — |
| `--diagnose` | 仅诊断不拉取 | False |
| `-r / --remote` | 远程仓库名 | origin |
