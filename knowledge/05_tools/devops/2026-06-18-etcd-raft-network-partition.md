# 当 leader 被隔离：etcd 网络分区深度分析 — 归档

> **概要**: etcd网络分区深度分析，剖析leader隔离、preVote机制与RecentActive设计
>
> **关键词**: etcd · Raft · 网络分区 · preVote · lease

---

## 📑 目录

- [文章结构](#文章结构)
  - [网络分区场景](#网络分区场景)
  - [几个关键问题](#几个关键问题)
  - [核心流程源码追踪](#核心流程源码追踪)
  - [preVote 机制](#prevote-机制)
- [🤔 反思](#反思)
  - [1. 这篇文章的核心贡献](#1-这篇文章的核心贡献)
  - [2. 知其所以然：RecentActive 的设计智慧](#2-知其所以然recentactive-的设计智慧)
  - [3. preVote + lease = 双重保险](#3-prevote-lease-双重保险)
  - [4. 交叉引用](#4-交叉引用)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

---

## 文章结构

### 网络分区场景

```text
t1: s1 = leader
t2: 网络分区
    分区 A: s1(旧leader) + s2(follower)
    分区 B: s3 + s4 + s5 -> s3 当选新 leader（有过半投票）
```

### 几个关键问题

| 问题 | 回答 |
|:-----|:------|
| **旧 leader s1 会退位吗？** | 不会主动退位。它继续发心跳，但只有 s2 回复 |
| **怎么判断自己不再是 leader？** | 通过 `RecentActive` 标志位 + `checkQuorum` 机制。每个 electionTimeout 周期统计活跃节点，未过半数则降级为 follower |
| **为什么需要 preVote？** | 防止 term 无意义递增+无效选举 |

### 核心流程源码追踪

1. **tickHeartbeat**（leader 侧）
   - 每次心跳自增 `heartbeatElapsed` 和 `electionElapsed`
   - `electionElapsed >= electionTimeout` → 发 `pb.MsgCheckQuorum` 给自身 raft 状态机
   - 普通心跳间隔：`heartbeatElapsed >= heartbeatTimeout` → 发 `pb.MsgBeat`（心跳消息）

2. **stepFollower**（follower 侧）
   - 收到 `MsgHeartbeat` → 重置 `electionElapsed = 0`，回复 `MsgHeartbeatResp`

3. **stepLeader**（leader 侧处理心跳回复）
   - 收到 `MsgHeartbeatResp` → 将该 follower 的 `RecentActive = true`（**不统计票数，而是打标记**）
   - 收到 `MsgCheckQuorum` → 判断 `QuorumActive()`：遍历所有节点，检查 `RecentActive` 是否过半数

4. **leader 退位时机**
   - 调用 `QuorumActive()` 返回 false → `becomeFollower(term, None)`
   - 然后重置所有 follower 的 `RecentActive = false`（滑动窗口）

### preVote 机制

**没有 preVote 的悲剧（旧版 raft）：**

- 分区 A 中 s1 降级后，s2 发起选举 → term 自增到 11 → 票不够 → VotePending
- s1 electionTimeout 到期 → 成为 candidate → term 自增到 12
- s1 和 s2 轮流递增 term，形成 term 膨胀
- 网络恢复后，s1/s2 的 term 比 s3 大 → **s3 被迫降级**，**导致集群产生无效选举**

**有 preVote 的解决（新版 etcd-raft）：**

- `becomePreCandidate()` **不增加 term**，只检查是否能获得多数票
- 分区 A 的 s1/s2 永远拿不到多数票 → 永远停在 preCandidate，term 不变
- 网络恢复后不影响 s3
- **关键升级**：新版 raft 在 `Step()` 中增加了 lease 检查：
  - follower 收到 term 更大的 `MsgVote/MsgPreVote` → 检查是否刚给合法 leader 投过票 → 是则忽略
  - leader 收到 term 更大的投票消息 → 检查本 electionTimeout 周期是否合法 → 是则忽略

> 通过 **preVote 保证 term 不递增** + **lease 锁防止 term 更大的无效投票**

---

## 🤔 反思

### 1. 这篇文章的核心贡献

它把 etcd-raft 网络分区场景下的 **旧 leader 行为** 讲清楚了——大多数人关注新 leader 如何产生，但旧 leader 在分区隔离后**不会立刻退位**，而是通过滑动窗口（RecentActive + checkQuorum）慢慢发现自己失去了多数支持。这种「慢反应」设计是有意为之——避免网络抖动导致频繁切换。

### 2. 知其所以然：RecentActive 的设计智慧

代码中有一个非常精巧的设计：

- 收到心跳回复时，不直接计数，只打 `RecentActive` 标记
- 每个 electionTimeout 周期结束时，统一检查标记分布
- 检查完成后，**统一重置所有标记**

这本质上是**滑动窗口统计**：用 `electionTimeout` 为窗口大小，统计窗口内活跃节点是否过半数。相比「收到 N 个回复就算过半数」，滑动窗口天然抵抗网络延迟和瞬态抖动。

### 3. preVote + lease = 双重保险

这篇文章展示了一对很好的组合设计思想：

| 机制 | 解决的问题 | 方式 |
|:-----|:-----------|:-----|
| **preVote** | term 膨胀 | 竞选前不修改 term，先探路 |
| **lease** | 大 term 劫持 | 即使收到更大 term 的消息，如果 leader 有效则拒绝 |

新版 raft 的高可用性不是靠单一机制保证的，而是靠这两个互补的防线。

### 4. 交叉引用

这篇与以下已有知识关联：

- **Prometheus 告警规则指南** → etcd 告警（`etcd_server_leader_changes` 等指标）的实际底层原理就在这里
- **云原生模块** → etcd 是 K8s 的控制平面存储，理解网络分区行为对运维 etcd 集群至关重要
- **可靠性与测试模块** → 网络分区是分布式系统最经典的故障模式之一

**谁需要回看这篇**：当你运维 etcd 集群发现 leader 频繁切换（term 持续递增）、或者网络恢复后 etcd 行为异常时，回来对比论文版 raft 和新版 etcd-raft 的差异。

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
