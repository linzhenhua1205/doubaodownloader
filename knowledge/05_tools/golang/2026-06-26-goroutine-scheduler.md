# Goroutine 调度器

> **概要**: Go语言Goroutine调度器原理，详解M:N线程模型与P/M/G核心组件
>
> **关键词**: Goroutine · 调度器 · M:N模型 · GMP · sysmon

---

## 📑 目录

- [为什么需要 Go 调度器](#为什么需要-go-调度器)
- [M:N 线程模型](#mn-线程模型)
- [核心组件：P、M、G](#核心组件pmg)
  - [三者的核心关系](#三者的核心关系)
- [调度流程](#调度流程)
  - [启动过程](#启动过程)
  - [创建 G (go func())](#创建-g-go-func)
  - [创建 M (内核线程)](#创建-m-内核线程)
  - [调度核心 (schedule)](#调度核心-schedule)
- [调度点（上下文切换时机）](#调度点上下文切换时机)
  - [sysmon（系统监控线程）](#sysmon系统监控线程)
- [现场处理](#现场处理)
- [参考链接](#参考链接)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

## 为什么需要 Go 调度器

- POSIX 线程有信号掩码、CPU affinity 等特征，对 Go 程序来说是累赘，上下文切换耗时高
- GC 需要所有 goroutine 暂停，依靠 OS 调度器会导致大量线程需要停止
- 自定义调度器可在 GC 时只等待当前 CPU 核上运行的线程，而非所有线程

## M:N 线程模型

| 模型 | 描述 | 缺点 |
|:-----|:-----|:------|
| **N:1** | 多个用户线程在一个内核线程上 | 无法利用多核 |
| **1:1** | 一个用户线程对应一个内核线程 | 上下文切换慢 |
| **M:N** (Go) | 多个 goroutine 在多个内核线程上 | 调度复杂度高，但兼具并发与效率 |

## 核心组件：P、M、G

```text
地鼠(M) 推着小车(P) 搬运砖块(G) 🐭🧱
```

| 组件 | 名称 | 角色 |
|:-----|:-----|:------|
| **M** | Machine (内核线程) | 真正干活的人，对应 OS 线程 |
| **P** | Processor (上下文) | 局部调度器，实现 N:1→M:N 映射的关键 |
| **G** | Goroutine | 协程，拥有自己的栈和指令指针 |
| **Sched** | 调度器 | 全局调度结构，维护 M/G 队列 |

### 三者的核心关系

- **P 的数量** = `runtime.GOMAXPROCS()`，代表真正的并发度
- 每个 M 都必须绑定一个 P 才能执行 G
- P 维护一个本地 **runqueue**（就绪 G 队列）
- 当 M 阻塞时，P 可以转到另一个 M 上运行

## 调度流程

### 启动过程

```text
asm_amd64.s -> runtime.schedinit (初始化 P) -> runtime.newproc (创建第一个 G) -> runtime.mstart (启动执行)
```

- `runtime.schedinit` 根据 `GOMAXPROCS` 创建最多 256 个小车 (P)，初始放入 `Sched.pidle` 链表
- 第一个 G 执行 `runtime.main`（即用户 Go 程序的入口）
- `runtime.main` 创建系统监控线程 sysmon

### 创建 G (go func())

- `go` 关键字 → `runtime.newproc` → 制造砖块 (G) 放入当前 M 的小车 (P) 中
- 新 G 有自己的栈，G.sched 保存栈地址和程序计数器

### 创建 M (内核线程)

- 砖(G) 太多，地鼠(M) 不够，还有空闲小车(P) → 从别处借地鼠（创建新 M）
- `runtime.newm` → `clone` 系统调用 → 新线程从 `runtime.mstart` 开始

### 调度核心 (schedule)

1. **runqget**: M 试图从自己的 P 取一个 G
2. **findrunnable**: 如果 P 中无 G → 去全局队列取 → 随机偷其他 P 一半的 G（work stealing）→ 多次失败则还回 P，线程 sleep
3. **wakep**: 如果 P 中 G 太多 + 有空闲 P + 有休眠 M → 唤醒休眠 M 分担工作；如果没有休眠 M → 创建新 M
4. **execute**: 真正执行 G

> **Work Stealing**：地鼠偷砖算法，确保 CPU 充分使用

## 调度点（上下文切换时机）

| 条件 | 触发函数 | 行为 |
|:-----|:---------|:------|
| goroutine 阻塞 (waiting) | `runtime.park` | G 设为 waiting，放弃 CPU，从 P 中移除 |
| 显式放弃 CPU | `runtime.gosched` | G 设为 runnable，放入全局等待队列 |
| 系统调用 | `entersyscall` / `exitsyscall` | P 标记为 syscall 状态 → sysmon 抢走 P 给新 M |
| 函数调用（Go 1.2+） | 编译器安插的指令 | 避免纯计算 goroutine 饿死其他 goroutine |

### sysmon（系统监控线程）

- 扫描所有 P，发现 syscall 状态的 P → 创建新 M 抢走 P
- 被抢走 P 的 M 从系统调用返回后，把 G 放回全局队列，自己 sleep

## 现场处理

- **保存现场**：`runtime.mcall` → goroutine 的栈地址和程序计数器保存到 `G.sched`
- **恢复现场**：`runtime.gogocall` → 从 `G.sched` 装载寄存器（在 execute 中调用）

## 参考链接

- <https://johng.cn/goroutine1-pmg/>
- <https://johng.cn/goroutine-scheduler-brief/>
- <http://morsmachine.dk/go-scheduler>

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- (无)

### 外部资料引用

- 来源: [johng.cn](https://johng.cn/programming/goroutine-scheduler) | **导入**: 2026-06-04

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-24 | v1.0 | 初始版本 |
