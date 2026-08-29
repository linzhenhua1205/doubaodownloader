# Git + AI 集成方案

> **概要**: Git与AI集成方案，涵盖pre-commit AI审查、GitLab Webhook CodeReview、GitNexus上下文增强与Copilot替代
>
> **关键词**: Git · AI集成 · pre-commit · WebHook · Copilot替代

---

## 📑 目录

- [一、pre-commit AI 审查 + 测试生成](#一pre-commit-ai-审查-测试生成)
  - [1.1 整体架构](#11-整体架构)
  - [1.2 核心脚本：`ai-commit-check.sh`](#12-核心脚本ai-commit-checksh)
  - [1.3 注册为 Git Hook](#13-注册为-git-hook)
- [二、GitLab WebHook + AI CodeReview 服务](#二gitlab-webhook-ai-codereview-服务)
  - [2.1 整体链路](#21-整体链路)
  - [2.2 服务核心流程](#22-服务核心流程)
  - [2.3 评审结果格式](#23-评审结果格式)
  - [🔴 严重（1）](#严重1)
  - [🟡 警告（2）](#警告2)
- [三、GitNexus + AI 上下文增强](#三gitnexus-ai-上下文增强)
- [四、GitHub Copilot 替代方案](#四github-copilot-替代方案)
  - [4.1 Copilot 新计费问题](#41-copilot-新计费问题)
  - [4.2 国产替代方案对比](#42-国产替代方案对比)
  - [4.3 替代方案接入 Git 工作流](#43-替代方案接入-git-工作流)
- [五、工具与框架推荐](#五工具与框架推荐)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

**交叉引用**: [提交信息规范与校验](2026-06-29-git-commit-convention-and-validation.md) | [GitLab 集成与自动化](2026-06-29-gitlab-integration-automation.md) | [GitHub Actions CI/CD](2026-06-29-github-actions-cicd.md)

---

## 一、pre-commit AI 审查 + 测试生成

### 1.1 整体架构

```text
git commit 触发
      v
git diff --cached 获取变更文件
      v
按文件扩展名分类（C/C++/Shell/Python/JS）
      v
调用 Continue CLI / OpenAI API 进行代码走读
      v
生成审查报告 + 单元测试用例
      v
审查通过？-> commit 继续；不通过？-> 中断提交
```

### 1.2 核心脚本：`ai-commit-check.sh`

```bash
#!/bin/bash
set -e

# Git提交前AI自动审查 + 自动生成测试用例
# 支持：C / C++ / Shell / Python / JavaScript
# 依赖：continue CLI

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}===== Git 提交前 AI 自动审查开始 =====${NC}"

# 获取本次提交的所有变更文件（排除删除文件）
CHANGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

if [ -z "$CHANGED_FILES" ]; then
    echo -e "${YELLOW}没有检测到变更文件，跳过审查${NC}"
    exit 0
fi

# 按文件扩展名分组
C_FILES=()
CPP_FILES=()
SH_FILES=()
PY_FILES=()
JS_FILES=()

while IFS= read -r file; do
    case "$file" in
        *.c) C_FILES+=("$file") ;;
        *.cpp|*.cc|*.cxx|*.hpp) CPP_FILES+=("$file") ;;
        *.sh) SH_FILES+=("$file") ;;
        *.py) PY_FILES+=("$file") ;;
        *.js|*.jsx|*.ts|*.tsx) JS_FILES+=("$file") ;;
    esac
done <<< "$CHANGED_FILES"

# 对每种语言调用 Continue CLI 做审查
review_file() {
    local file="$1"
    local lang="$2"

    echo -e "\n${YELLOW}[审查] $file ($lang)${NC}"

    # 获取文件 diff
    local diff_content=$(git diff --cached "$file")

    # 调用 Continue CLI 做代码走读
    continue --input "请对以下 $lang 代码做走读审查，检查：
1. 安全漏洞
2. 代码规范
3. 性能问题
4. 逻辑错误

\`\`\`$lang
$diff_content
\`\`\`" 2>/dev/null || echo "Continue CLI 调用失败"
}

# 对每个文件执行审查
for file in "${C_FILES[@]}"; do review_file "$file" "c"; done
for file in "${CPP_FILES[@]}"; do review_file "$file" "cpp"; done
for file in "${SH_FILES[@]}"; do review_file "$file" "bash"; done
for file in "${PY_FILES[@]}"; do review_file "$file" "python"; done
for file in "${JS_FILES[@]}"; do review_file "$file" "javascript"; done

echo -e "\n${GREEN}===== AI 自动审查完成 =====${NC}"
```

### 1.3 注册为 Git Hook

```bash
# 保存脚本到项目目录
cp ai-commit-check.sh .githooks/pre-commit
chmod +x .githooks/pre-commit

# 配置 Git 使用自定义 hooks 目录
git config core.hooksPath .githooks

# 或直接安装到 .git/hooks/
cp ai-commit-check.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

---

## 二、GitLab WebHook + AI CodeReview 服务

### 2.1 整体链路

```text
开发者提交 MR/Push
        v
GitLab 触发 WebHook
        v
AI CodeReview 服务接收 POST 请求
        v
解析 WebHook Payload，提取 Diff
        v
需要上下文时 -> Git 拉取完整源码 + GitNexus 获取函数上下文
        v
送入大模型做代码评审
        v
评审结果回写 GitLab MR 评论区（折叠展示）
```

### 2.2 服务核心流程

```python
# 伪代码：AI CodeReview 服务核心逻辑
def handle_gitlab_webhook(payload):
    # 1. 鉴权
    verify_token(request.headers['X-GitLab-Token'])

    # 2. 提取变更信息
    project_id = payload['project']['id']
    diff = payload['object_attributes']['diff']
    mr_iid = payload['object_attributes']['iid']

    # 3. 拉取完整上下文
    full_source = clone_and_read_file(project_id, file_path)

    # 4. 补充函数上下文（调用 GitNexus）
    context = gitnexus_get_function_context(project_id, file_path, function_name)

    # 5. 大模型评审
    review_result = llm_review(diff, full_source, context)

    # 6. 回写 Note（折叠格式）
    post_note(project_id, mr_iid, format_folded_note(review_result))
```

### 2.3 评审结果格式

```html
<details>
<summary>🔍 AI 代码审查报告（共发现 3 个问题）</summary>

### 🔴 严重（1）
- **文件**: src/auth/login.py:45
- **问题**: SQL 注入风险
- **建议**: 使用参数化查询替代字符串拼接

### 🟡 警告（2）
- **文件**: src/auth/login.py:78
- **问题**: 未处理的异常
- **建议**: 添加 try-except 块

</details>
```

---

## 三、GitNexus + AI 上下文增强

GitNexus 提供代码知识图谱能力，为 AI 审查补充函数级上下文：

```bash
# 查询函数定义
gitnexus query --repo path/to/repo --function "authenticate_user"

# 查询调用链
gitnexus trace --repo path/to/repo --function "authenticate_user" --depth 3

# 查询跨文件依赖
gitnexus depends --repo path/to/repo --file "src/auth/login.py"
```

> 详见 [GitNexus 纯本地代码情报引擎](2026-06-26-gitnexus.md)

---

## 四、GitHub Copilot 替代方案

### 4.1 Copilot 新计费问题

2026 年 6 月，GitHub Copilot 调整计费规则为 **AI Credits 代币 + 超额按量付费**：

| 问题 | 表现 |
|:-----|:------|
| 消耗速度远超预期 | 2 天耗尽 7000 内置 Credits + 10 美元备用金 |
| 定价不透明 | Credits 与 token 换算标准未公开 |
| 功能捆绑扣费 | 基础补全与高阶 Chat/Agent 共用额度 |

### 4.2 国产替代方案对比

| 方案 | 优势 | 适用场景 |
|:-----|:------|:---------|
| **DeepSeek** | 本地私有化部署，零隐形成本 | 个人开发者、企业内网 |
| **通义灵码** | 阿里云生态，VS Code 插件完善 | Java/Spring 生态 |
| **豆包 MarCode** | 字节跳动，IDE 集成，免费额度 | 中小团队 |
| **自建 + 开源模型** | 完全可控 | 涉密环境、合规要求 |

### 4.3 替代方案接入 Git 工作流

```bash
# 本地 pre-commit 调用 DeepSeek
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
CHANGED_FILES=$(git diff --cached --name-only)
for file in $CHANGED_FILES; do
    diff_content=$(git diff --cached "$file")
    curl -s https://api.deepseek.com/v1/chat/completions \
      -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
      -d '{"model":"deepseek-coder","messages":[{"role":"user","content":"审查以下代码:\n'"$diff_content"'"}]}'
done
EOF
chmod +x .git/hooks/pre-commit
```

---

## 五、工具与框架推荐

| 工具 | 用途 | 集成方式 |
|:-----|:------|:---------|
| **Continue CLI** | 本地 AI 代码助手，支持自定义模型 | pre-commit Hook / CLI |
| **GitNexus** | 代码知识图谱，提供函数级上下文 | API / CLI |
| **OpenClaw** | AI Agent 编排，可自动化 Code Review | WebHook + Agent |
| **CodeRabbit** | AI Code Review 平台 | PR 自动触发 |
| **PR-Agent** | 开源 AI PR Review | GitHub App / GitLab Integration |
| **Qodo (CodiumAI)** | 自动生成测试用例 | IDE 插件 / CLI |

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- Git 提交 AI 自动审查 + 生成测试用例脚本 - 豆包整理 — 关联
- GitLab WebHook + AI CodeReview 集成 - 豆包整理 — 关联
- GitNexus 纯本地代码情报引擎 - 豆包整理 — 关联

### 外部资料引用

- 来源: [GitHub Copilot 新版计费翻车 - cnblogs](https://www.cnblogs.com/lsjwq/p/20304480)
- 来源: --

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-24 | v1.0 | 初始版本 |
