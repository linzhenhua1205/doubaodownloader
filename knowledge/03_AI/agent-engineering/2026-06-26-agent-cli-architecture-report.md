# Agent CLI 实现方案调研报告

> **概要**: 调研6个主流Agent CLI实现，拆解架构、工具系统、上下文管理与安全模型，提供选型与自研决策框架
>
> **关键词**: Agent CLI · Agentic Loop · 上下文管理 · MCP/Skills · 架构对比

---

## 📑 目录

- [📖 报告摘要](#报告摘要)
- [一、为什么 Agent CLI 是下一个范式](#一为什么-agent-cli-是下一个范式)
  - [1.1 核心命题](#11-核心命题)
  - [1.2 关键驱动力](#12-关键驱动力)
- [二、主流 Agent CLI 实现深度对比](#二主流-agent-cli-实现深度对比)
  - [2.1 全景对比矩阵](#21-全景对比矩阵)
  - [2.2 Claude Code — 架构参考实现（最完整）](#22-claude-code-架构参考实现最完整)
  - [2.3 GitHub Copilot CLI — 生态深度集成](#23-github-copilot-cli-生态深度集成)
  - [2.4 Zencoder — 多模型编排架构](#24-zencoder-多模型编排架构)
  - [2.5 Trae CLI — 轻量级参考](#25-trae-cli-轻量级参考)
- [三、核心技术架构解析](#三核心技术架构解析)
  - [3.1 Agentic Loop 引擎](#31-agentic-loop-引擎)
  - [3.2 工具系统设计](#32-工具系统设计)
  - [3.3 上下文管理（最关键的设计挑战）](#33-上下文管理最关键的设计挑战)
  - [3.4 会话与持久化](#34-会话与持久化)
- [四、Agent CLI 实现方案架构设计](#四agent-cli-实现方案架构设计)
  - [4.1 整体系统架构](#41-整体系统架构)
  - [4.2 分层设计详解](#42-分层设计详解)
    - [Layer 1: CLI 解析层](#layer-1-cli-解析层)
    - [Layer 2: Session 管理层](#layer-2-session-管理层)
    - [Layer 3: Agent Loop 引擎](#layer-3-agent-loop-引擎)
  - [4.3 工具系统实现](#43-工具系统实现)
- [五、安全与权限系统](#五安全与权限系统)
  - [5.1 权限模型设计](#51-权限模型设计)
  - [5.2 工具级权限规则](#52-工具级权限规则)
  - [5.3 自动模式分类器架构](#53-自动模式分类器架构)
- [六、扩展性设计：MCP / Skills / Hooks](#六扩展性设计mcp-skills-hooks)
  - [6.1 MCP（Model Context Protocol）](#61-mcpmodel-context-protocol)
  - [6.2 Skills 系统](#62-skills-系统)
  - [6.3 Hooks 系统](#63-hooks-系统)
- [七、选型与实现建议](#七选型与实现建议)
  - [7.1 场景选型建议](#71-场景选型建议)
  - [7.2 自研 Agent CLI 的最小可用架构](#72-自研-agent-cli-的最小可用架构)
  - [7.3 关键技术决策](#73-关键技术决策)
- [八、趋势与总结](#八趋势与总结)
  - [8.1 核心趋势](#81-核心趋势)
  - [8.2 关键结论](#82-关键结论)
- [附录](#附录)
  - [A. 参考来源](#a-参考来源)
  - [B. 更新日志](#b-更新日志)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

---

## 📖 报告摘要

Agent CLI 是 2025-2026 年 AI 编程领域最核心的范式转变——从"IDE 插件辅助补全"到"终端原生 Agent 自主编程"。本报告深入调研 **6 个主流 Agent CLI 实现**，拆解其架构模式、工具系统、上下文管理、安全模型等关键设计维度，为 Agent CLI 实现或选择提供完整的决策框架。

---

## 一、为什么 Agent CLI 是下一个范式

### 1.1 核心命题

| 维度 | 传统 AI 编程助手 | Agent CLI |
|:-----|:----------------|:----------|
| 交互界面 | IDE 插件 / 侧边栏 Chat | **终端 / Shell** |
| 操作范围 | 当前文件 / 选中代码段 | **整个代码仓库 + Shell 命令** |
| 执行模式 | 被动响应（用户问→AI 答） | **主动 Agentic Loop**（规划→执行→验证） |
| 工具能力 | 仅代码补全 | 文件读写 + Shell 执行 + Git 操作 + 搜索 + Web |
| 上下文 | 当前文件 | **全仓库索引 + Git 历史 + 项目配置 + 记忆** |
| 自动化 | 手动触发 | **非交互式管道 + CI/CD 集成 + 定时任务** |

### 1.2 关键驱动力

1. **Unix 哲学兼容**: 管道组合（`tail -200 app.log | claude -p "分析异常"`）、CI 集成、脚本编排
2. **环境无关性**: 不依赖特定 IDE，可在 SSH 远程、CI Runner、容器、任何终端中运行
3. **全自主闭环**: Agentic Loop 让 AI 能自主规划、执行、验证，而不仅仅是补全
4. **工具即能力**: Agent CLI 的核心创新是将 Shell 命令和文件操作作为 AI 可调用的"工具"

---

## 二、主流 Agent CLI 实现深度对比

### 2.1 全景对比矩阵

| 维度 | Claude Code | GitHub Copilot CLI | Zencoder | Trae CLI |
|:-----|:-----------|:-------------------|:---------|:---------|
| **开发商** | Anthropic | GitHub / Microsoft | For Good AI | 字节跳动 |
| **定位** | 全功能 Agent CLI / SDK | 面向 GitHub 生态的 Agent | 多模型编排 Agent CLI | 轻量辅助 CLI |
| **核心模型** | Claude Opus/Sonnet | GPT-4o/多种 | Opus+Gemini+Codex | 多种（可配置） |
| **架构层级** | 全栈 Agent 框架 | 轻量 Agent | 全栈 + CI/CD Agent | 基础辅助 |
| **Agentic Loop** | ✅ 完整闭环 | ✅ 基础闭环 | ✅ 完整闭环 | ❌ 被动响应 |
| **SDK 支持** | ✅ Python + TypeScript | ✅ TypeScript | ❌ API 对接 | ❌ |
| **Tool 系统** | 14 个内置工具 | 基础工具 | 6+ 核心工具 | 基础文件操作 |
| **子 Agent** | ✅ Agent/Spawn | ❌ | ✅ 并行 Agent | ❌ |
| **MCP 支持** | ✅ 原生 | ✅ | ✅ | ❌ |
| **Hooks** | ✅ Pre/PostToolUse | ❌ | ❌ | ❌ |
| **非交互模式** | ✅ `-p` 管道 | ✅ | ✅ | ❌ |
| **定时任务** | ✅ Routines | ❌ | ✅ 定时 | ❌ |
| **权限模型** | 5 级模式 + 规则 | 基础 | 基础 | 无 |
| **Checkpoint** | ✅ 文件快照 | ❌ | ❌ | ❌ |
| **配置文件** | CLAUDE.md | .github/copilot-instructions.md | .zencoder/ | 无 |
| **开源** | ❌ SDK 开源 | ❌ | ❌ | ❌ |
| **适合场景** | 全栈开发/自动化 | GitHub 工作流 | 企业级编排 | 个人简单辅助 |

### 2.2 Claude Code — 架构参考实现（最完整）

**文件结构:**

```text
~/.claude/                         # 用户级配置
+-- settings.json                  # 全局设置
+-- skills/                        # 用户级技能
+-- projects/                      # 会话持久化 (JSONL)

<project>/
+-- .claude/
|   +-- settings.json              # 项目设置
|   +-- settings.local.json        # 本地覆盖
|   +-- CLAUDE.md                  # 项目级指令
|   +-- skills/                    # 项目级技能
|   |   +-- <name>/
|   |       +-- SKILL.md
|   +-- hooks/                     # 自动化钩子
|   |   +-- prescript.sh
|   |   +-- postscript.sh
|   +-- plugins/                   # 插件
|   +-- worktrees/                 # git worktree 隔离
+-- MEMORY.md                      # 自动记忆（自动保存）
+-- CLAUDE.md                      # 根级项目指令
```

**Agentic Loop 三阶段:**

```text
+-----------------------------------------------------+
|                  Agentic Loop                        |
|                                                       |
|  1. Gather Context ---> 2. Take Action ---> 3. Verify   |
|       |                      |              |         |
|       v                      v              v         |
|   Read files            Edit files        Run tests   |
|   Search codebase       Bash commands     Check type  |
|   Grep patterns         Web fetch         Lint check  |
|   LSP intelligence      Git operations    Re-run      |
|       |                      |              |         |
|       +----------------------+--------------+         |
|                    循环迭代                            |
+-----------------------------------------------------+
```

**工具系统分类（14个内置工具）:**

| 类别 | 工具 | 是否需权限 | 说明 |
|:-----|:-----|:-----------|:-----|
| **文件操作** | Read | ❌ | 读取文件（支持图片/PDF/Notebook） |
| | Write | ✅ | 创建/覆写文件 |
| | Edit | ✅ | 精确字符串替换（非正则，需 read-before-edit） |
| | Glob | ❌ | 文件模式匹配（支持 `**`） |
| **搜索** | Grep | ❌ | 基于 ripgrep 的内容搜索 |
| | LSP | ❌ | 语言服务器协议：跳转定义/查找引用/类型检查 |
| **执行** | Bash | ✅ | Shell 命令执行（持久化cd/不持久化env） |
| | PowerShell | ✅ | Windows 原生 |
| | Monitor | ✅ | 后台监控（tail log/轮询状态→主动通知） |
| **Web** | WebSearch | ✅ | 搜索引擎（内部后端，不可配置） |
| | WebFetch | ✅ | 网页抓取（自动 Markdown 转换，有损耗） |
| **编排** | Agent | ❌ | 子 Agent 生成（独立上下文窗口） |
| | Skill | ❌ | 技能执行 |
| | Workflow | ❌ | 动态工作流编排 |
| **其他** | AskUserQuestion | ❌ | 向用户提问 |
| | NotebookEdit | ✅ | Jupyter 编辑 |
| | TodoWrite | ❌ | 任务列表管理 |

**权限分级模型（5级）:**

```text
bypassPermissions  --- 完全跳过，仅限隔离容器
        ^
    auto  --- 分类器自动决策（研究预览）
        ^
    acceptEdits  --- 自动通过文件编辑 + 常见 fs 命令
        ^
    default  --- 每次操作询问
        ^
    plan  --- 只读模式，仅规划不执行
```

**会话模型:**

- 每个会话独立 JSONL 文件存储
- `-c` / `--continue` 恢复最近会话
- `-r` / `--resume` 按 ID/名称恢复
- `--fork-session` 分支（复制历史到新 ID）
- Worktree 隔离：`-w feature-auth` 自动创建 git worktree

### 2.3 GitHub Copilot CLI — 生态深度集成

**关键架构特征:**

- 从 `gh copilot` 插件演进为独立 CLI
- 深度集成 GitHub：Issue/PR/Actions/Code Review
- Cloud Agent 支持远程执行 + 自定义 Agent 创建
- **Copilot SDK**（TypeScript）支持编程化 Agent
- Hooks 系统（PreToolUse/PostToolUse/SessionLifecycle）
- MCP 支持 + Skills 系统
- **CI/CD 原生**: Automations，Fix with Copilot for Actions

**核心能力:**

- 多 Agent 任务并行执行
- 1M Token 上下文窗口
- 可配置推理深度（effort level）
- Enterprise Teams GA（跨 50+ 组织统一管理）

### 2.4 Zencoder — 多模型编排架构

**核心创新: 模型分工**

```text
Plan 阶段 ---> Claude Opus（最强推理，写 Spec/决策）
Build 阶段 ---> Google Gemini（快速执行）
Review 阶段 ---> OpenAI Codex（第三方审查，发现盲区）
```

**关键特性:**

- **Zenflow 工作流**: 代码 + 工作流双模式
- **并行 Agent 执行**: 数十个 Agent 同时在隔离环境中工作
- **跨 Agent 审查**: Agent A 产出 → Agent B 审查
- **定时自动化**: 每日 Bug 分类 / PR 审查 / 依赖更新
- **IDE 集成**: VS Code + JetBrains
- **企业级**: SOC 2 Type II + ISO 27001/42001

### 2.5 Trae CLI — 轻量级参考

字节跳动推出的轻量 CLI，作为 Trae IDE 的命令行延伸：

- 基础代码生成 + 简单批量修改 + 单文件操作
- `被动响应式`：缺乏自主规划能力
- 支持多模型集成 + 自定义 Agent
- 适合个人开发者简单场景

**与全套 Agent CLI 的核心差距:**

- 无 Agentic Loop（无自主规划/执行/验证闭环）
- 无限界上下文理解（无法做架构级分析和重构）
- 无工具系统（不可执行 Shell/搜索/Web）

---

## 三、核心技术架构解析

### 3.1 Agentic Loop 引擎

```text
+----------------------------------------------------+
|                  Agent Loop Engine                   |
|                                                      |
|  +----------+   +----------+   +----------+         |
|  |  Model   |   |   Tool   |   |  Result  |         |
|  | Reason   |-->|  Execute |-->| Process  |--+      |
|  +----------+   +----------+   +----------+  |      |
|       |              |              |         |      |
|       |              |              |         |      |
|       +--------------+--------------+         |      |
|                       |                       |      |
|                  More actions? -- yes --------+      |
|                       |                              |
|                      no                               |
|                       v                              |
|                  Done / Return                        |
+----------------------------------------------------+
```

**关键实现要素:**

1. **模型调用**: 每次 tool use 后重新调用 LLM，传入 tool result
2. **循环控制**: max_turns 上限 + timeout 控制
3. **流式输出**: 实时展示中间步骤
4. **中断恢复**: 用户可随时 Esc 中断，继续指令

### 3.2 工具系统设计

**工具注册 → 执行 → 结果闭环:**

```typescript
interface Tool {
  name: string;           // 工具名 (如 "Bash", "Edit")
  description: string;    // 给 LLM 的描述
  parameters: JSONSchema; // 参数 Schema

  // 执行方法
  execute(params: Record<string, unknown>): Promise<ToolResult>;
}

interface ToolResult {
  success: boolean;
  output: string;        // 返回给 LLM 的结果文本
  metadata?: {           // 额外信息（权限、文件路径等）
    error?: string;
    truncated?: boolean;
    filePath?: string;
  };
}
```

**工具执行模式对比:**

| 特征 | 直接执行型 | 权限代理型 | 后台监控型 |
|:-----|:----------|:----------|:----------|
| 工具示例 | Read/Glob/Grep | Bash/Edit/Write | Monitor |
| 执行时机 | 立即 | 等待审批 | 持续后台运行 |
| 返回方式 | 同步结果 | 同步（审批后） | 异步事件推送 |
| 安全控制 | 无（只读） | 权限系统 | 权限+沙箱 |
| 典型应用 | 文件读取/搜索 | 修改/执行/网络 | 日志监控/轮询 |

### 3.3 上下文管理（最关键的设计挑战）

**分层上下文架构:**

```text
+-------------------------------------------------+
|                 System Prompt                     | <- 系统指令（固定）
+-------------------------------------------------+
|                 CLAUDE.md                         | <- 项目级指令（固定）
+-------------------------------------------------+
|                 MEMORY.md                         | <- 自动记忆（200行/25KB）
+-------------------------------------------------+
|             Skill Descriptions                    | <- 轻量描述（惰性加载）
+-------------------------------------------------+
|           Conversation History                    | <- 对话历史（线性增长）
+-------------------------------------------------+
|           Current Tool Results                    | <- 命令输出（最大）
+-------------------------------------------------+
|              Pending Task                         | <- 当前任务描述
+-------------------------------------------------+
```

**压缩策略（Claude Code 实现）:**

| 策略 | 触发条件 | 行为 |
|:-----|:---------|:-----|
| 自动裁剪 | 上下文接近限制 | 清除旧 tool output → 摘要对话 |
| 手动 Compact | `/compact` 命令 | 按 focus 条件保留关键信息 |
| 子 Agent 隔离 | 调用 Agent 工具 | 独立上下文窗口，返回摘要 |
| Skill 惰性加载 | Skill 被触发 | 按需加载全量内容 |
| Tool Search | MCP 工具定义 | 仅名称在上下文，使用才加载 |

### 3.4 会话与持久化

**会话架构:**

```text
+---------------------------------------------+
|                 Session Manager               |
|                                               |
|  +----------+  +----------+  +----------+   |
|  | Session 1|  | Session 2|  | Session 3|   |
|  | (Active) |  | (Saved)  |  | (Forked) |   |
|  +----------+  +----------+  +----------+   |
|       |             |             |          |
|       v             v             v          |
|  +--------------------------------------+    |
|  |       存储：~/.claude/projects/       |    |
|  |       JSONL 格式，事件序列流           |    |
|  +--------------------------------------+    |
+---------------------------------------------+
```

**关键设计决策:**

- **JSONL 格式**: 每行一个事件，支持流式追加
- **会话 ID**: UUID 标识，支持 resume/fork
- **Checkpointing**: 每次编辑前快照文件，支持 `Esc Esc` 撤销
- **Worktree 隔离**: `-w` 标志自动创建 git worktree，多任务并行

---

## 四、Agent CLI 实现方案架构设计

### 4.1 整体系统架构

```text
+--------------------------------------------------------------+
|                      Agent CLI Application                     |
+--------------------------------------------------------------+
|  +---------+  +----------+  +-------------+                 |
|  |  CLI     |  |  Session  |  |  LLM        |                 |
|  |  Parser  |--|  Manager  |--|  Adapter    |                 |
|  +---------+  +----------+  +------+-------+                 |
|                                    |                         |
|  +---------------------------------+--------------------+    |
|  |                   Agent Loop Engine                    |    |
|  |  +-----------+  +-----------+  +----------------+    |    |
|  |  |  Reason   |  |   Plan    |  |   Execute      |    |    |
|  |  |  (Model)  |--| (Divide)  |--| (Tool Runner)  |    |    |
|  |  +-----------+  +-----------+  +-------+--------+    |    |
|  +------------------------------------------+------------+    |
|                                             |                 |
|  +------------------------------------------+------------+    |
|  |                 Tool System                            |    |
|  |  +------+ +------+ +------+ +------+ +------+       |    |
|  |  |Read  | |Edit  | |Bash  | |Search| |Agent |       |    |
|  |  |Write | |      | |Web   | |Glob  | |Work  |       |    |
|  |  |      | |      | |      | |Grep  | |flow  |       |    |
|  |  +------+ +------+ +------+ +------+ +------+       |    |
|  +------------------------------------------------------+    |
|                                                              |
|  +----------+  +----------+  +--------------------------+   |
|  |  Context  |  |  Permission|  |  Extensions              |   |
|  |  Manager  |  |  System   |  |  (MCP/Skills/Hooks)      |   |
|  +----------+  +----------+  +--------------------------+   |
+--------------------------------------------------------------+
```

### 4.2 分层设计详解

#### Layer 1: CLI 解析层

```text
cli <command> [flags] [--] [query]
+-- 子命令: agents, attach, resume, daemon, auth, mcp, project
+-- 模式: 交互式 (默认) / 管道 (-p) / 后台 (--bg)
+-- 标志: --model, --permission-mode, --effort, --worktree
+-- 输入: 直接参数 / 标准输入管道 / 文件重定向
```

**实现注意:**

- 使用 `cobra` (Go) / `click` (Python) / `commander` (TS) 等成熟 CLI 框架
- 管道输入探测: `isatty(STDIN_FILENO)` 判断是否有管道数据
- 输出格式: `text`(默认) / `json` / `stream-json` 三种模式

#### Layer 2: Session 管理层

```text
Session {
  id: string;             // UUID
  project: string;        // 项目路径
  startTime: number;

  // 状态
  conversation: Message[];
  contextWindow: ContextWindow;
  permissionMode: PermissionMode;

  // 持久化
  persist(): void;        // 追加写入 JSONL
  checkpoint(): void;     // 文件快照
  fork(): Session;        // 分支复制
}
```

**持久化格式 (JSONL):**

```jsonl
{"type":"user_msg","id":"m1","ts":1749100000000,"content":"分析这个bug"}
{"type":"tool_call","id":"t1","ts":1749100001000,"tool":"Grep","params":{"pattern":"error","path":"src/"}}
{"type":"tool_result","id":"t1r","ts":1749100002000,"tool":"Grep","output":"..."}
{"type":"assistant_msg","id":"m2","ts":1749100003000,"content":"找到了，在auth.go的45行..."}
{"type":"checkpoint","id":"cp1","ts":1749100004000,"files":["src/auth.go"]}
```

#### Layer 3: Agent Loop 引擎

```python
async def agent_loop(prompt: str, tools: list[Tool], max_turns: int = 50):
    messages = [UserMessage(prompt)]

    for turn in range(max_turns):
        # 1. 调用 LLM
        response = await llm.chat(messages, tools=tool_definitions)

        if response.stop_reason == "stop":
            return response.content  # 正常结束

        if response.stop_reason == "tool_use":
            # 2. 解析工具调用
            for tool_call in response.tool_calls:
                tool = find_tool(tool_call.name)

                # 3. 权限检查
                if not permission_system.check(tool, tool_call.params):
                    await permission_system.request_approval(tool, tool_call.params)

                # 4. 执行工具
                result = await tool.execute(tool_call.params)

                # 5. 结果加入上下文
                messages.append(ToolResultMessage(tool_call.id, result))

            continue  # 继续循环

        if response.stop_reason == "max_tokens":
            # 上下文管理
            context_manager.compress(messages)
            continue

    return "达到最大轮数限制"
```

### 4.3 工具系统实现

```python
class ToolRegistry:
    """工具注册中心"""

    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool):
        self._tools[tool.name] = tool

    def get_definitions(self) -> list[dict]:
        """返回 OpenAI/Tool 格式的定义"""
        return [t.definition for t in self._tools.values()]

    def execute(self, name: str, params: dict) -> ToolResult:
        tool = self._tools.get(name)
        if not tool:
            raise ToolNotFoundError(name)
        return tool.execute(params)


# 文件操作工具示例
class EditTool(Tool):
    """精确文本替换工具"""

    name = "Edit"
    description = "在文件中执行精确字符串替换"
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "文件路径"},
            "old_string": {"type": "string", "description": "被替换文本（精确匹配）"},
            "new_string": {"type": "string", "description": "新文本"},
            "replace_all": {"type": "boolean", "default": False}
        },
        "required": ["file_path", "old_string", "new_string"]
    }

    def execute(self, params: dict) -> ToolResult:
        content = read_file(params["file_path"])

        if params["old_string"] not in content:
            return ToolResult(success=False, error="old_string 未找到")

        count = content.count(params["old_string"])
        if count > 1 and not params.get("replace_all"):
            return ToolResult(success=False, error="找到多处匹配，请提供更精确的上下文")

        new_content = content.replace(params["old_string"], params["new_string"],
                                       -1 if params.get("replace_all") else 1)
        write_file(params["file_path"], new_content)

        return ToolResult(success=True, output=f"{'全部' if params.get('replace_all') else '一处'}替换完成")


# 执行工具示例
class BashTool(Tool):
    """Shell 命令执行工具，带安全沙箱"""

    def execute(self, params: dict) -> ToolResult:
        cmd = params["command"]

        # 安全校验
        if not self._is_allowed(cmd):
            return ToolResult(success=False, error="命令被禁止")

        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
                timeout=params.get("timeout", 120),
                cwd=params.get("working_dir")
            )
            return ToolResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr if result.returncode != 0 else None
            )
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error="命令超时")
```

---

## 五、安全与权限系统

### 5.1 权限模型设计

```text
                +-------------------------+
                |    by pass Permissions    | <- 完全跳过（隔离容器）
                +-----------+-------------+
                            |
                +-----------+-------------+
                |     Auto Mode             | <- 分类器自动决策
                |  (AI Classifier 代理)     |
                +-----------+-------------+
                            |
                +-----------+-------------+
                |   Accept Edits           | <- 自动通过文件编辑
                |  + 常见 fs 命令           |
                +-----------+-------------+
                            |
                +-----------+-------------+
                |     Default              | <- 逐个审批
                |  (每次操作都询问)          |
                +-----------+-------------+
                            |
                +-----------+-------------+
                |     Plan Mode            | <- 只读，仅规划
                |  (不能修改或执行)          |
                +-------------------------+
```

### 5.2 工具级权限规则

```json
{
  "permissions": {
    "defaultMode": "acceptEdits",
    "allow": [
      "Bash(git *)",           // 允许所有 git 命令
      "Read(src/**)",          // 允许读取 src 目录
      "WebFetch(domain:docs.python.org)"  // 允许特定域名
    ],
    "deny": [
      "Bash(*rm *)",           // 禁止删除命令
      "Bash(curl * | bash*)",  // 禁止远程执行
      "Edit(.env*)",           // 禁止修改 .env
      "WebFetch"               // 禁止所有网页抓取
    ]
  }
}
```

### 5.3 自动模式分类器架构

```text
用户请求 ---> 工具执行请求 ---> 分类器模型 ---> 允许/拒绝
                                   ^
                                 读取:
                          - 对话历史（工具调用）
                          - CLAUDE.md
                          - 安全检查规则
                          (⚠ 不读取 tool result，防注入)
```

**分类器默认阻断:**

- `curl | bash` 类远程代码执行
- 向外部端点发送敏感数据
- 生产部署、数据库迁移
- 大量删除云存储 / 授权操作
- 强制推送 main 分支

---

## 六、扩展性设计：MCP / Skills / Hooks

### 6.1 MCP（Model Context Protocol）

开放标准，连接 AI 工具与外部数据源：

```text
Agent CLI <----> MCP Client <----> MCP Server (自定义工具)
                                 +-- Jira API
                                 +-- Google Drive
                                 +-- Slack
                                 +-- 数据库
                                 +-- 自定义
```

**实现示例:**

```python
# Agent CLI 中的 MCP 集成
mcp_servers = {
    "jira": {"command": "npx", "args": ["@jira/mcp-server"]},
    "playwright": {"command": "npx", "args": ["@playwright/mcp@latest"]},
}

# 客户端连接
async with mcp_client(mcp_servers["playwright"]) as client:
    tools = await client.list_tools()
    for tool in tools:
        tool_registry.register(MCPServerTool(client, tool))
```

### 6.2 Skills 系统

可重用的工作流封装，团队可共享：

```yaml
# skills/review-pr/SKILL.md
---
name: review-pr
description: Review a pull request for code quality and security
allowed-tools: [Read, Glob, Grep, LSP, Bash]
---
You are a senior code reviewer. Review the changes for:
1. Security vulnerabilities
2. Performance issues
3. Code style consistency
4. Test coverage
```

### 6.3 Hooks 系统

Agent 生命周期事件的回调机制：

| Hook 点 | 触发时机 | 用途 |
|:--------|:---------|:-----|
| **PreToolUse** | 工具执行前 | 审计日志、自定义检查、阻止危险操作 |
| **PostToolUse** | 工具执行后 | 记录变更、触发通知、文件格式化 |
| **SessionStart** | 会话开始 | 加载环境、验证配置 |
| **SessionEnd** | 会话结束 | 清理、汇总报告 |
| **UserPromptSubmit** | 用户提问 | 预处理指令、添加上下文 |

---

## 七、选型与实现建议

### 7.1 场景选型建议

| 场景 | 推荐方案 | 理由 |
|:-----|:---------|:------|
| 个人全栈开发 | **Claude Code** | 工具最全、Agent 能力最强 |
| 企业 GitHub 工作流 | **GitHub Copilot CLI** | 生态集成最深、CI/CD 原生 |
| 需要多模型编排 | **Zencoder** | Plan/Build/Review 分模型最优 |
| 极简轻量辅助 | **Trae CLI** | 入门门槛低 |
| 嵌入式/资源受限 | **自研轻量方案** | 最小可用集 |

### 7.2 自研 Agent CLI 的最小可用架构

如果决定自行实现，建议的分层架构：

```text
Layer 1: CLI 界面
  +-- 命令解析 + 管道输入 + 输出格式化
  +-- 交互式/非交互式模式切换

Layer 2: 会话管理
  +-- 会话创建/恢复/分支
  +-- JSONL 持久化
  +-- Checkpoint 快照

Layer 3: Agent Loop
  +-- LLM Adapter（多模型切换）
  +-- Tool 注册/执行/结果处理
  +-- 上下文窗口管理（压缩策略）

Layer 4: 工具系统
  +-- 核心：Read/Write/Edit/Glob/Grep
  +-- 执行：Bash/Monitor
  +-- 扩展：MCP Client / WebSearch / WebFetch

Layer 5: 安全
  +-- 权限分级（Default/AcceptEdits/Plan）
  +-- 工具级 allow/deny 规则
  +-- 保护路径机制

Layer 6: 扩展
  +-- MCP Client 集成
  +-- Skills 工作流
  +-- Hooks 生命周期
```

### 7.3 关键技术决策

| 决策点 | 选项 | 推荐 | 理由 |
|:-------|:-----|:-----|:------|
| 编程语言 | Python / TypeScript / Go / Rust | **TypeScript（全栈）/ Rust（性能）** | TS 生态好、LLM 框架成熟；Rust 适合 CLI 性能敏感 |
| LLM 协议 | OpenAI API / Anthropic API | **双协议支持** | 灵活切换模型 |
| 工具定义格式 | OpenAI Function Calling / Anthropic Tool | **OpenAI 兼容格式** | 兼容性最广 |
| 会话存储 | JSONL / SQLite / 内存 | **JSONL** | 简单、可追加、可 grep 调试 |
| 权限控制 | 提示式 / 规则引擎 / AI 分类器 | **规则引擎 + AI 分类器** | 灵活性和安全性平衡 |
| 沙箱机制 | Docker / gVisor / 进程级 | **Docker（稳定）/ 进程级（轻量）** | 按安全需求定 |
| MCP 支持 | 可选 / 强制 | **强制** | 关键差异化能力 |
| 配置文件格式 | YAML / TOML / JSON / Markdown | **Markdown + JSON** | Markdown 用户友好（CLAUDE.md），JSON 程序友好 |

---

## 八、趋势与总结

### 8.1 核心趋势

1. **从 IDE 插件到终端原生**: CLI 正成为 AI 编程的首选入口
2. **Agentic Loop 标准化**: 规划→执行→验证的闭环将成为标配
3. **MCP 作为通用集成协议**: 开放工具生态正在形成，非 MCP 兼容将逐渐边缘化
4. **多模型编排**: 不同阶段使用不同模型（Plan/Build/Review）成为企业级最佳实践
5. **安全与治理前置**: Auto mode 分类器、权限规则系统成为差异化竞争力
6. **CI/CD 深度集成**: 定时任务、PR 自动审查、CI 失败修复成为标配

### 8.2 关键结论

- **Claude Code 是当前最完整的 Agent CLI 参考实现**，其 Agentic Loop、工具系统、权限模型、扩展架构可供任何实现借鉴
- **工具系统是 Agent CLI 的核心竞争力**，工具越多越丰富，Agent 的自主能力越强
- **上下文管理是最难的设计挑战**，没有通用的完美方案，需要根据场景选择（子 Agent 隔离/压缩/惰性加载的组合策略）
- **安全模型不可忽视**，权限分级 + 工具级规则 + 分类器的三层防御是成熟方案的基础
- **MCP 支持正在成为必要条件**，单一的封闭工具集将无法满足复杂场景

---

## 附录

### A. 参考来源

| 来源 | 链接 |
|:-----|:------|
| Claude Code Docs | <https://docs.anthropic.com/en/docs/claude-code> |
| Claude Code Agent SDK | <https://docs.anthropic.com/en/docs/claude-code/agent-sdk> |
| GitHub Copilot CLI | <https://docs.github.com/en/copilot/using-github-copilot> |
| Zencoder | <https://zencoder.ai> |
| Cursor CLI | <https://docs.cursor.com> |
| MCP Specification | <https://modelcontextprotocol.io> |

### B. 更新日志

| 日期 | 版本 | 更新内容 |
|:-----|:-----|:---------|
| 2026-06-05 | v1.0 | 初始版本，覆盖 6 个 Agent CLI 实现 |

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- (无)

### 外部资料引用

- (无)

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-24 | v1.0 | 初始版本 |
