# git push 持续失败根因分析（2026-08-26 ~ 08-28）

> 元信息: 文件状态=最终 | 覆盖范围=本地环境 git 推送链路故障 | 版本=v1.0
> 适用范围: CowAgent 工作空间 git 运维 / 远程仓库凭据管理

## 目录

[TOC]

---

## 1. 引言与范围

### 1.1 故障现象

自 **2026-08-26 22:07**（`~/.git-credentials` 被清空）起，`git push` 持续失败，至 2026-08-28 07:29 排查时本地仍有 **ahead 1** 未推送（`7dd11d537`）。期间 08-28 06:06 用户导入 PAT 到 credential store，08-21 起 ssh config 指向新密钥，但推送始终未恢复。

### 1.2 影响范围

- 本地 `main` 分支超前 origin 1 commit（08-28 07:24 知乎日报）
- 08-26 ~ 08-28 三日共 **7+ 次 push 失败记录**（memory 日志），多条调研日报滞留本地
- 影响面：知识库同步链路中断（飞书日报依赖远端同步检查兜底）

### 1.3 排查范围

覆盖 git 推送链路的四层：认证凭据层、网络传输层、remote 配置层、密钥文件层。不涉及 git 本地仓库损坏（`git status`/`git fsck` 正常）。

---

## 2. 故障时间线（事件墙）

| 时间 | 事件 | 证据 |
|:-----|:-----|:-----|
| 06-04 | `github_backup` 密钥生成（未登记 GitHub） | `~/.ssh/github_backup.pub` mtime |
| 08-14 09:50 | `cowkb_ed25519` 密钥生成（未登记 GitHub） | `~/.ssh/cowkb_ed25519.pub` mtime |
| 08-14 | MEMORY 权威记录：origin=HTTPS；origin-old=SSH | MEMORY.md |
| 08-21 14:45 | `id_ed25519` 密钥生成（**带 passphrase**，464 字节） | `~/.ssh/id_ed25519` mtime |
| 08-21 14:50 | ssh config 主密钥切换为 id_ed25519 + IdentitiesOnly yes | `~/.ssh/config` mtime |
| 08-21 14:51 | known_hosts 更新（ssh.github.com:443 指纹） | `~/.ssh/known_hosts` mtime |
| 08-26 22:07 | `~/.git-credentials` 被清空 | memory/2026-08-27.md L50 |
| 08-27 | origin 被改为 SSH → 曾改回 HTTPS（未持久） | memory/2026-08-27.md L68 |
| 08-27 21:1x | HTTPS 报 Invalid username or token；SSH 报 key 未认证 | memory/2026-08-27.md L136 |
| 08-28 05:48 | commit 5f208491a 记录"推送失败" | git show 5f208491a |
| 08-28 06:06 | 用户导入 PAT 至 `~/.git-credentials`（**无效，API 401**） | `~/.git-credentials` mtime + curl 验证 |
| 08-28 07:24 | 最新 commit 7dd11d537，ahead 1 未推送 | git branch -vv |

> 关键观察：**所有认证路径（SSH×3 密钥、HTTPS×2 凭据源）在同一窗口期内全部失效**，且失效原因互不相同 —— 指向"凭据生命周期管理缺失"这一系统性根因，而非单一配置错误。

---

## 3. 诊断方法与证据

按 fault-diagnosis 五层诊断架构，从业务层（影响）逐层下沉到认证层：

### 3.1 认证路径全景测试（Layer 4-5）

| # | 认证路径 | 测试命令 | 结果 |
|:-:|:---------|:---------|:-----|
| 1 | SSH origin（当前 URL） | `git push origin main` | ❌ `Permission denied (publickey)` |
| 2 | SSH 三把密钥逐一 | `ssh -vT -i <key> -p 443 git@ssh.github.com` | ❌ 全部拒绝 |
| 3 | HTTPS PAT | `curl -H "Authorization: Bearer $PAT" api.github.com/user` | ❌ `HTTP 401 Bad credentials` |
| 4 | HTTPS gh CLI | `gh auth status` | ❌ token invalid |
| 5 | api.github.com 连通 | `curl https://api.github.com` | ✅ HTTP 200 (0.4s) |
| 6 | github.com 主站连通 | `curl https://github.com` | ❌ 15s 超时（exit 124） |
| 7 | ssh.github.com:443 | `ssh -vT git@github.com` | ✅ TCP 连接建立 |

**结论 3.1**：网络层仅 `ssh.github.com:443` 与 `api.github.com` 可达；`github.com:443` HTTPS 直连被阻断。**SSH 443 是唯一可行的推送路径** —— 修复必须走 SSH。

### 3.2 SSH 认证深挖（Layer 3-4）

`ssh -vT` 逐密钥判定"服务器是否认识该公钥"（Server accepts key = 公钥已登记）：

| 密钥 | 私钥加密状态 | Server accepts key | 判定 |
|:-----|:-----------:|:------------------:|:-----|
| `id_ed25519` | ✅ 加密（aes256-ctr+bcrypt，464B） | ✅ 接受 | 公钥已登记；但签名失败 → 非交互无法解锁 passphrase |
| `cowkb_ed25519` | ❌ 未加密（411B） | ❌ 拒绝 | 公钥未登记 GitHub |
| `github_backup` | ❌ 未加密（411B） | ❌ 拒绝 | 公钥未登记 GitHub |
| `cowkb_main_ed25519`（新） | ❌ 未加密 | ❌ 拒绝（待登记） | 修复用新密钥 |

> **矛盾解释**：用户"手工验证 SSH 正确"大概率发生在交互式终端（可输入 passphrase 解锁 id_ed25519）或 08-21 前的旧配置（cowkb_ed25519 时代）。当前自动化/非交互环境（BatchMode=yes）**必然失败** —— 加密私钥在无 passphrase 输入时无法完成签名。

### 3.3 HTTPS 凭据验证（Layer 4）

- `~/.git-credentials` 中 PAT：`github_pat_` 前缀（fine-grained，92 字符格式正确）→ GitHub API 返回 `401 Bad credentials` → **token 本身无效**（非权限问题，权限不足应返回 403）
- `~/.config/gh/hosts.yml`：gh CLI 判定 token invalid
- `.gitconfig` 中 `credential.https://github.com.helper = gh auth git-credential`：HTTPS 认证链被接管到 gh（gh 失效 → 链断裂）

### 3.4 配置漂移检测（Layer 3）

| 配置项 | MEMORY 权威值 | 当前实际值 | 漂移 |
|:-------|:-------------|:-----------|:-----|
| `remote.origin.url` | HTTPS | SSH（排查中曾改 HTTPS 又恢复） | ⚠️ 漂移 |
| ssh config IdentityFile | — | id_ed25519（加密）→ 已换 cowkb_main_ed25519 | 修复中 |
| credential helper | store | store + gh auth git-credential | ⚠️ 双 helper 叠加 |

---

## 4. 根因分析

### 4.1 5Why 追问

**Why1** — 为什么 push 失败？
→ 唯一网络可达路径（SSH 443）认证失败：`Permission denied (publickey)`

**Why2** — 为什么 SSH 认证失败？
→ ssh config 指定的 id_ed25519 私钥带 passphrase，BatchMode 下无法解锁签名
→ 另两把密钥（cowkb/github_backup）未登记 GitHub，直接被服务器拒绝

**Why3** — 为什么用带 passphrase 的密钥做非交互认证？
→ 08-21 ssh config 切换主密钥为 id_ed25519，`IdentitiesOnly yes` 排除了其他密钥
→ 生成时带 passphrase（交互安全习惯），但未适配自动化场景

**Why4** — 为什么 HTTPS 不能兜底？
→ ① remote 是 SSH URL，PAT 根本不参与认证（配置与凭据错配）
→ ② 即使改 HTTPS：github.com 主站直连被网络阻断（curl 超时）
→ ③ PAT 本身 401 无效（08-28 06:06 导入即失效，未做导入后验证）
→ ④ gh CLI token 亦失效，credential helper 链断裂

**Why5** — 为什么凭据会整体失效且无人发现？
→ 凭据生命周期管理缺失：无过期监控、无导入验证、无单一事实源（SSOT）
→ 三套凭据体系（SSH 密钥/PAT/gh token）各自维护，失效互不感知
→ 08-26 清空 credentials 后无恢复动作，故障持续 3 天

### 4.2 根因分类

| 层级 | 根因 | 类型 |
|:-----|:-----|:-----|
| **直接原因** | SSH 唯一可用路径的密钥无法完成非交互签名（passphrase） | 认证 |
| **直接原因** | remote origin=SSH 与 PAT 凭据错配（PAT 永不生效） | 配置 |
| **加重因素** | github.com HTTPS 直连网络阻断 → HTTPS 兜底路径不可用 | 网络 |
| **加重因素** | PAT/gh token 双失效且导入后未验证 | 凭据管理 |
| **根本原因** | 凭据生命周期管理缺失：多套凭据无 SSOT、无失效监控、无导入验证、无自动化兜底 | 管理 |

### 4.3 为什么 3 天未自动恢复

- push 由 `git-push-robust.py` 驱动，多策略（HTTPS→SSH→HTTPS+代理）全部依赖凭据/网络，凭据全失效时无"人工介入"信号
- memory 每日记录"待用户配置凭据后补推"，但无定时提醒/告警触发用户操作
- 缺少 `ssh -T` / `curl api` 健康检查前置门禁

---

## 5. 修复措施

### 5.1 已执行（本次排查）

| # | 操作 | 命令/文件 | 状态 |
|:-:|:-----|:----------|:----:|
| 1 | 备份 ssh config | `cp ~/.ssh/config tmp/bak/ssh-config-backup-20260828` | ✅ |
| 2 | 备份 remote 配置 | `tmp/git-remote-backup-20260828.txt` | ✅ |
| 3 | 生成无 passphrase 新密钥 | `~/.ssh/cowkb_main_ed25519`（SHA256:No8hNjQ+HTHJhBtyZ7ODh9dYn2mjr8nBOKjMtqaA7IQ） | ✅ |
| 4 | ssh config 指向新密钥 | IdentityFile=cowkb_main_ed25519 + IdentitiesOnly yes | ✅ |
| 5 | origin 恢复 SSH URL | `git@github.com:linzhenhua1205/cowkb.git` | ✅ |

### 5.2 待用户操作（1 步必做）

在 GitHub 网页 **Settings → SSH and GPG keys → New SSH key** 添加新公钥：

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINeCYfFc7dupo/NCMJcYj/+/+pDWe56IvJd8U3EyD4Mb cowkb-main-push
```

添加后执行验证：

```bash
ssh -T git@github.com    # expect: Hi linzhenhua1205! You've successfully authenticated
git push origin main     # expect: push succeeds
```

### 5.3 后续清理（建议）

| # | 项目 | 操作 |
|:-:|:-----|:-----|
| 1 | `~/.git-credentials` 无效 PAT | 重新生成有效 PAT 后覆盖；或确认不再用 HTTPS 后清空 |
| 2 | `~/.config/gh/hosts.yml` 失效 token | `gh auth logout -h github.com -u linzhenhua1205` 或重新 `gh auth login` |
| 3 | 旧密钥 `id_ed25519` | 若不再用交互式场景可移除（先确认无其他依赖） |
| 4 | MEMORY.md 配置记录 | 更新为 origin=SSH（HTTPS 网络不可达），经人工审核 |

---

## 6. 预防建议

1. **凭据 SSOT**：在 MEMORY.md/RULE.md 中维护唯一认证配置表（remote URL + 认证方式 + 密钥路径），任何变更走 Candidate.md 提案
2. **非交互密钥规范**：自动化环境的 SSH 密钥**一律无 passphrase**（`-N ""`）；交互密钥与自动化密钥分离
3. **导入即验证**：新凭据导入后立即执行最小验证（`ssh -T` / `curl api` / `git ls-remote`），验证通过才标记完成
4. **健康检查门禁**：`git-push-robust.py` 增加前置诊断（`ssh -T` 或 PAT API 检查），失败即明确报"凭据失效"而非静默重试
5. **网络路径备案**：HTTPS 直连不可达（github.com 超时）环境下，remote 固定 SSH 443，避免反复切换
6. **失效告警**：push 连续失败 N 次 → 定时任务/飞书告警，避免"每日记录但无人处理"

---

## 7. 参考文献与交叉链接

- [git 常见错误排查](2026-06-29-git-common-errors-troubleshooting.md) — 既有 git 排障文档（related）
- [git 基础日常工作流](2026-06-29-git-basics-daily-workflow.md) — git 工作流背景（related）
- [GitHub 官方：Using SSH over the HTTPS port](https://docs.github.com/en/authentication/troubleshooting-ssh/using-ssh-over-the-https-port) — ssh.github.com:443 依据 [来源: GitHub Docs]
- [GitHub 官方：Managing personal access tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) — PAT 生命周期规范 [来源: GitHub Docs]
- [GitHub 官方：SSH troubleshooting](https://docs.github.com/en/authentication/troubleshooting-ssh) — publickey 拒绝排查 [来源: GitHub Docs]
- memory/2026-08-27.md / memory/2026-08-28.md — 故障期事件记录（本地证据）

---

## 变更记录

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-28 | v1.0 | 首次创建：git push 持续失败（08-26~08-28）根因分析，三层失效（SSH passphrase / HTTPS 网络阻断 / PAT 无效）+ 配置漂移，修复已生成无密码密钥待登记 |
