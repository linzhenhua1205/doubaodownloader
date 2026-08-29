---
name: git-submodule-import
description: 用 git submodule 方式导入外部 GitHub 仓库（书籍/资料/工具/参考代码）到工作空间，支持国内镜像通道、版本固定、元信息归档与降级预案。当用户需要导入 GitHub 仓库、书籍、开源资料作为子模块参考时使用，或需要批量/重复导入外部仓库并沉淀索引时使用。 | 导入GitHub仓库, submodule导入, 外部资料归档, 镜像clone, 仓库版本固定
version: 1.0.0
---

# 🔌 Git Submodule 导入技能

将外部 GitHub 仓库以 submodule 方式导入工作空间（默认 `import/<repo-name>/`），沉淀"导入脚本 + 元信息 + 一键填充"三段式能力。

## 适用场景

- 用户分享/指定 GitHub 仓库（书籍、技术资料、开源工具）需要导入参考
- 需要固定版本、可追踪更新、不污染主仓库历史的资料引用
- 国内网络环境（直连 GitHub 不通时自动走镜像）

## 工作流（4 步）

### Step 1: 预检与探测

```bash
cd /home/lzh/cow
# 检查直连
timeout 8 curl -sI https://github.com | head -1
# 检查镜像(实测 git 协议, 比 curl 网页更真实)
timeout 15 git ls-remote --heads https://ghproxy.net/https://github.com/bojieli/ai-agent-book >/dev/null && echo "ghproxy 可用"
```

### Step 2: 尝试标准导入（网络可达时）

```bash
bash scripts/git-submodule-import/import-repo.sh \
    https://github.com/<owner>/<repo> [target-path] [--branch main]
```

脚本自动：探测通道 → clone（失败自动切换镜像）→ 注册 .gitmodules（保留官方 URL）→ 版本固定 → 生成 `<repo>.info/README.md` 元信息。

### Step 3: 降级预案（网络不可达时——本次 ai-agent-book 实测场景）

```bash
# 3a. 用 web_fetch 抓 README 了解仓库(服务端网络可达)
web_fetch https://raw.githubusercontent.com/<owner>/<repo>/main/README.md

# 3b. 用 ls-remote 拿 HEAD(镜像可达)
git ls-remote https://ghproxy.net/https://github.com/<owner>/<repo> | grep HEAD

# 3c. 手动登记 submodule 元数据(gitlink 指向已知 HEAD)
mkdir -p import/<repo>
git config -f .gitmodules "submodule.import/<repo>.path" "import/<repo>"
git config -f .gitmodules "submodule.import/<repo>.url" "https://github.com/<owner>/<repo>"
git config "submodule.import/<repo>.active" true
git update-index --add --cacheinfo "160000,<HEAD>,import/<repo>"

# 3d. 生成元信息目录
mkdir -p import/<repo>.info   # README.md(仓库信息/HEAD/填充方法) + README.original.md(原文)

# 3e. 交付填充命令给用户(网络恢复后执行)
#     git submodule update --init import/<repo>
```

### Step 4: 索引沉淀

- 知识库 log 记录（kb-log-append.py）
- 元信息目录随 git 提交（`git add import/<repo>.info .gitmodules`）

## 镜像通道备忘（2026-08 实测）

| 通道 | 实测表现 | 备注 |
|:-----|:---------|:-----|
| 直连 github.com | ❌ 443 不通 | 需代理/VPN |
| ghproxy.net | ⚠️ ls-remote ✅ / clone 不稳定 / zip ~35KB/s | 最常用，fetch 可重试 |
| ghfast.top | ⚠️ 网页 200 / clone 超时 | — |
| gitclone.com | ❌ 502 | — |
| gh-proxy.com | ⚠️ 卡住 | — |
| ghps.cc | ❌ 525 | — |

**关键经验**：
1. **探测通道用 `git ls-remote` 而非 curl**（镜像网页可能 403 但 git 协议可用）
2. **clone 失败是镜像 checkout 阶段通病**——降级为 `git init + fetch + checkout FETCH_HEAD` 手动流程
3. **大仓库（>100MB）镜像下载不现实**（35KB/s）——登记元数据 + 待网络填充是正解
4. **管道会吞退出码**（`cmd | tail` 返回 tail 的码）——关键命令用 `${PIPESTATUS[0]}` 或分步执行

## 产物规范

```
import/<repo>/            # submodule 工作区(可能待填充)
import/<repo>.info/       # 元信息(README.md + README.original.md)
.gitmodules               # submodule 登记(官方 URL)
```

## 质量检查清单

- [ ] .gitmodules 含 path + url（url 必须是官方地址，不能是镜像）
- [ ] gitlink 已写入 index（`git ls-files --stage import/<repo>` 显示 160000）
- [ ] 元信息目录含 HEAD/填充方法/仓库简介
- [ ] 无法填充时：交付明确的恢复命令，不假装成功
- [ ] 大仓库（>100MB）在元信息中标注体积与导入方式建议

## Changelog

| 日期 | 版本 | 变更 |
|:----|:-----|:-----|
| 2026-08-13 | 1.0.0 | 创建：4 步工作流（预检/标准导入/降级预案/索引沉淀）、镜像通道实测备忘、关键经验（ls-remote 探测/管道吞退出码/大仓库登记策略） |
