# 🔄 系统活动任务载体深度分析：进程 · 线程 · 协程 · 任务

> **范围**: 从硬件中断处理 → OS 进程/线程 → 运行时协程 → 框架级任务抽象，围绕资源、生命周期、可靠性、依赖拓扑、可观测性五大维度展开
> **写作原则**: 每层先原理再实现，资源模型为主线，量化数据出处理论引出处
> **创建**: 2026-06-30 v1.0

---

## 📑 目录

- [1. 概念体系与演化脉络](#1-概念体系与演化脉络)
  - [1.1 四层实体定义](#11-四层实体定义)
  - [1.2 演化历史与设计选择](#12-演化历史与设计选择)
  - [1.3 核心抽象：执行上下文](#13-核心抽象执行上下文)
- [2. 资源模型框架](#2-资源模型框架)
  - [2.1 资源分类总览](#21-资源分类总览)
  - [2.2 内存资源体系](#22-内存资源体系)
  - [2.3 I/O 资源体系](#23-io-资源体系)
  - [2.4 中断与信号资源](#24-中断与信号资源)
  - [2.5 文件资源体系](#25-文件资源体系)
  - [2.6 事件资源与队列](#26-事件资源与队列)
  - [2.7 时间与定时资源](#27-时间与定时资源)
  - [2.8 调试与可观测资源](#28-调试与可观测资源)
  - [2.9 资源所有权模型](#29-资源所有权模型)
- [3. 实现层次深度分析](#3-实现层次深度分析)
  - [3.1 OS 内核实现：以 Linux 为例](#31-os-内核实现以-linux-为例)
  - [3.2 运行时实现](#32-运行时实现)
  - [3.3 虚拟机实现](#33-虚拟机实现)
  - [3.4 上层任务抽象](#34-上层任务抽象)
- [4. 生命周期模型](#4-生命周期模型)
  - [4.1 状态机与状态转换](#41-状态机与状态转换)
  - [4.2 生命周期模式分类](#42-生命周期模式分类)
- [5. 可靠性模型](#5-可靠性模型)
  - [5.1 故障模式分类](#51-故障模式分类)
  - [5.2 恢复策略体系](#52-恢复策略体系)
  - [5.3 监督树与容错架构](#53-监督树与容错架构)
- [6. 依赖关系与拓扑](#6-依赖关系与拓扑)
  - [6.1 进程关系树](#61-进程关系树)
  - [6.2 线程关系图](#62-线程关系图)
  - [6.3 协程调度拓扑](#63-协程调度拓扑)
  - [6.4 任务依赖 DAG](#64-任务依赖-dag)
- [7. 调试与可观测性](#7-调试与可观测性)
  - [7.1 系统级调试接口](#71-系统级调试接口)
  - [7.2 运行时级调试接口](#72-运行时级调试接口)
  - [7.3 注入与干预技术](#73-注入与干预技术)
  - [7.4 内部可观测性机制](#74-内部可观测性机制)
- [8. 跨层对比矩阵](#8-跨层对比矩阵)
- [参考来源](#参考来源)
- [修订记录](#修订记录)

---

## 1. 概念体系与演化脉络

### 1.1 四层实体定义

| 概念层 | 调度单位 | 共享粒度 | 切换开销 | 创建开销 |
|:-------|:---------|:---------|:--------:|:--------:|
| **进程** (Process) | OS 内核调度器 | 独立地址空间，IPC 通信 | ~1-10μs（上下文切换） | ~ms 级（fork+execve） |
| **线程** (Thread) | OS 内核调度器 | 同进程共享地址空间 | ~0.1-1μs（用户态/内核态切换） | ~10-100μs（clone 系统调用） |
| **协程** (Coroutine) | 用户态调度器（运行时） | 栈空间独立，堆共享 | ~10-100ns（纯用户态切换） | ~μs 级（栈分配） |
| **任务** (Task) | 框架级调度器 | 取决于具体框架 | ~μs-ms 级（含调度逻辑） | ~ms 级（依赖注入/初始化） |

**核心规律**：抽象层次越高，资源开销越大但隔离性越弱；抽象层次越低，切换越快但编程复杂度越高。

### 1.2 演化历史与设计选择

```
硬件中断处理（ISR，1960s）
  └─→ 批处理多道程序（进程雏形，IBM OS/360，1964）
       └─→ Unix 进程模型（fork+exec, 1970s）
            ├─→ Unix System V 轻量进程（LWPs, 1980s）
            │    └─→ POSIX 线程标准（pthread, 1995）
            │         └─→ NPTL（Native POSIX Thread Library, Linux 2.6, 2003）
            ├─→ 用户态线程（Green Threads，Java 1.1, 1996）
            │    └─→ Go goroutine（G-P-M, 2009）
            │    └─→ Rust async/await（2019）
            │    └─→ Java Virtual Threads（Loom, JDK 21, 2023）
            └─→ Actor 模型（Erlang/OTP, 1986）
                 └─→ Akka/Scheduler/分布式任务框架
```

**关键设计决策**：

- **进程 vs 线程**：进程提供最强隔离（页表/特权级），但 fork+exec 开销大；线程共享地址空间降低通信成本，但失去隔离保护
- **内核线程 vs 用户态协程**：内核线程由 OS 调度，可抢占/多核并行，但切换需进出内核（~100ns 系统调用+上下文切换+TLB 刷新）；协程由运行时调度，纯用户态切换（~10ns 寄存器保存/恢复），但无法并行利用多核（除非多 OS 线程承载）
- **协程 vs 任务**：协程是**机制**（如何暂停/恢复执行流）；任务是**抽象**（表达一个完整的计算单元，含输入/输出/依赖/状态）

### 1.3 核心抽象：执行上下文

所有四层实体的本质都是**执行上下文**（Execution Context）的载体，核心三要素：

| 要素 | 进程 | 线程 | 协程 | 任务 |
|:-----|:-----|:-----|:-----|:-----|
| **寄存器状态** | 完整（通用寄存器+CR3+...） | 完整（通用寄存器+PC+SP） | 部分（PC+SP+callee-saved） | 无（存于任务对象） |
| **内存映射** | 独立页表（PID 空间隔离） | 共享页表 | 共享页表+独立栈空间 | 共享地址空间 |
| **调度元数据** | task_struct(~2KB) | task_struct(~2KB) | 协程对象(~few KB) | 任务记录(~KB~MB) |

---

## 2. 资源模型框架

### 2.1 资源分类总览

按资源类型、所有权模式、隔离粒度三个维度展开：

| 资源类型 | 物理实体 | 进程级 | 线程级 | 协程级 | 任务级 |
|:---------|:---------|::------|:-------|:-------|:-------|
| **虚拟地址空间** | 页表+MMU | 独占（独立页表） | 共享（同页表） | 共享（同页表） | 共享/沙箱 |
| **栈空间** | 物理内存页 | 独占（~8MB 默认） | 独占（~2MB 默认） | 独占（~2KB-8KB） | 框架分配 |
| **堆空间** | 物理内存页 | 共享（同一堆） | 共享（同堆） | 共享（同堆） | 共享/隔离 |
| **文件描述符表** | kernel fdtable | 共享（fork 继承/CLONE_FILES） | 共享（默认 clone） | 共享（进程内） | 框架封装 |
| **信号处理表** | kernel sighand_struct | 共享（fork 继承/CLONE_SIGHAND） | 共享 | N/A | N/A |
| **中断号** | IRQ 描述符 | 内核态独占 | N/A | N/A | N/A |
| **IPC 对象** | 内核对象 | 系统级标识（pid/共享内存 ID） | 进程内共享 | 进程内共享 | 框架封装 |
| **定时器** | timer_list/hrtimer | 进程内 | 线程内 | 事件循环管理 | 框架管理 |
| **event 对象** | eventfd/epoll/IO 完成端口 | 进程内 | 线程内 | 事件循环管理 | 框架管理 |
| **调试资源** | ptrace/eBPF/perf_event | 进程级可观测 | 线程级追踪 | 运行时自省 | 框架指标 |

### 2.2 内存资源体系

#### 2.2.1 虚拟地址空间分层

进程独占的虚拟地址空间是操作系统提供的最核心隔离资源。以 x86-64 Linux 为例（48 位虚拟地址）：

```
0x0000 0000 0000 0000
├── 用户空间 (0x0000 ~ 0x7FFF FFFF FFFF) — 128TB
│   ├── 代码段 (.text)        — 只读可执行
│   ├── 数据段 (.data/.bss)  — 读写（全局变量）
│   ├── 堆 (heap)            — brk/mmap 管理
│   ├── 内存映射段 (mmap)    — 共享库、匿名映射
│   ├── 栈 (stack)           — 自动扩展（ulimit -s）
│   └── vsyscall/vvar 页     — 内核暴露给用户的数据
0x7FFF FFFF FFFF FFFF
├── 内核空间 (0xFFFF 8000 ~ 0xFFFF FFFF FFFF FFFF) — 128TB
│   ├── 内核代码/数据         — 直接映射 (__va)
│   ├── vmalloc 区域          — 不连续页映射
│   ├── 模块区域              — 内核模块
│   ├── 固定映射 (fixmap)     — 系统表映射
│   └── 页表 (page tables)    — 进程页表层级
0xFFFF FFFF FFFF FFFF
```

**量化对比**（各层级内存资源分配）：

| 资源 | 进程 | 线程 | 协程 (goroutine) | 任务 (Java Virtual Thread) |
|:-----|:----:|:----:|:----------------:|:--------------------------:|
| 栈默认大小 | 8MB（ulimit) | 2MB（pthread) | 2KB（初始） | 可变（初始~few KB） |
| 栈最大增长 | 无限(RLIMIT_STACK) | 硬限制 | 1GB（Go 1.0, 可调整） | 无固定限制（堆分配） |
| 堆共享 | 进程内共享 | 线程间共享 | goroutine 间共享 | 所有 VT 共享 |
| TLB 刷新 | 需要（切换 CR3） | 不需要 | 不需要 | 不需要 |

**栈分配策略差异**（核心设计权衡）：

- **进程/线程**：操作系统预分配连续虚拟地址（MAP_GROWSDOWN 保证自动增长），物理页按需提交。8MB 虚拟空间占用极低，实际物理使用 ~4KB（初始）
- **Goroutine**：初始 2KB 小栈，溢出处 copy-on-expand（`runtime.morestack`），动态增长到最大限制。小栈使单进程可以创建百万级 goroutine
- **Java Virtual Thread**：栈不在本地线程栈上分配，而是作为堆上对象管理（`java.lang.VirtualThread`），通过 `j.l.StackChunk` 管理栈帧，挂起时可序列化到堆

#### 2.2.2 共享内存机制

```
进程 A ── mmap(MAP_SHARED) ──┐
                               ├── 物理内存页（同一 PFN）
进程 B ── mmap(MAP_SHARED) ──┘
                               │
进程 A ── shmget/shmat ───────┘ (System V / POSIX)
```

**实现层级**：

| 层级 | 机制 | 共享域 | 隔离性 |
|:-----|:-----|:-------|:-------|
| 硬件 | NUMA 本地内存 | 同一 CPU socket | 跨 socket 延迟增加 1.3-2× |
| 内核 | mmap(MAP_SHARED) | 跨进程（同一文件/mm_struct） | 页表指向相同 PFN |
| 内核 | System V 共享内存 | 跨进程（shmid） | 独立地址空间 |
| 内核 | KSM (Kernel Same-page Merging) | 跨进程透明合并 | 对进程透明 |
| 运行时 | 堆内存 | 线程间 / 协程间 | 无保护（需同步原语） |
| 框架 | 分布式缓存 | 跨节点 | 序列化/反序列化 |

### 2.3 I/O 资源体系

#### 2.3.1 文件描述符（FD）资源管理

每个进程维护一个**文件描述符表**（`struct fdtable`），这是 I/O 资源的统一抽象：

```
struct fdtable {
    unsigned int max_fds;       // 当前容量
    struct file **fd;           // 指向 struct file 的指针数组
    fd_set *close_on_exec;      // exec 时自动关闭的位图
};
```

**FD 在实体间的传递**：

- **进程间**（fork）：子进程继承父进程 fd 表（`CLONE_FILES` 控制共享/复制）
- **线程间**：默认共享 fd 表（`clone(CLONE_FILES)`, 即 pthread_create 行为）
- **协程间**：共享进程 fd 表（无独立 fd 空间）
- **任务间**：由框架管理 fd 的传递（如 Java RMI 序列化 FileDescriptor，或 UNIX socket 传 fd）

**FD 资源瓶颈**：

| 维度 | 默认限制 | 可调整 | 影响 |
|:-----|:---------|:-------|:-----|
| 单进程 | 1024（软限制） | ulimit -n 1048576 | 每个线程消耗 fd |
| 系统全局 | file-max (/proc/sys) | sysctl fs.file-max | 所有进程累积 |
| epoll 监控 | max_user_watches | sysctl | 百万级连接时显著 |

#### 2.3.2 块 I/O 与网络 I/O 资源

**块 I/O 路径**（读文件流程，数据从磁盘到用户空间）：

```
用户程序 read(fd, buf, 4096)
  └→ VFS: do_sync_read()
       └→ 文件系统层（ext4: ext4_file_read_iter）
            └→ 页缓存 (page cache) —— 命中直接返回
                 └→ 未命中：block layer (submit_bio)
                      └→ I/O 调度器 (mq-deadline/bfq/kyber)
                           └→ NVMe 驱动 (nvme_queue_rq)
                                └→ PCIe 总线 → NVMe 控制器
```

**网络 I/O 路径**（TCP recv 流程）：

```
用户程序 recv(sockfd, buf, 4096, 0)
  └→ sock_recvmsg()
       └→ tcp_recvmsg()
            ├─ 数据在 receive buffer 中 → 复制到用户空间
            └─ 数据未到 → sleep_on() 进入 TASK_INTERRUPTIBLE
                 └─ NIC 硬件中断 → NAPI poll → tcp_data_queue()
                      └─ wake_up() 唤醒等待进程
```

**事件驱动 I/O 模型**（各实体的 I/O 复用接口）：

| 模型 | 接口 | 操作系统 | 复杂度 | 可扩展性 |
|:-----|:-----|:---------|:------|:---------|
| select/poll | 轮询 fd 集合 | Linux/Unix | O(n) | 差（<1024 fd） |
| epoll | 事件驱动回调 | Linux | O(1) | 好（百万级 fd） |
| kqueue | 事件过滤器 | FreeBSD/macOS | O(1) | 好 |
| IOCP | 完成端口 | Windows | 回调 | 好 |
| io_uring | SQ+CQ 无锁队列 | Linux 5.1+ | O(1) | 最佳（零拷贝系统调用） |

**io_uring 的跨层意义**：通过提交队列（SQ）和完成队列（CQ）实现**系统调用免穿透**，将 I/O 资源的管理权部分交还给用户态，协程/任务框架可在此基础上实现零系统调用 I/O 调度。

#### 2.3.3 输入输出信息流

实体间的信息流通道：

| 通道类型 | 使用层级 | 机制 | 数据方向 |
|:---------|:---------|:-----|:---------|
| stdin/stdout/stderr | 进程（OS 默认） | fd 0/1/2 | 继承自父进程 |
| pipe | 进程间 | kernel buffer + fd pair | 单向 |
| UNIX socket | 进程间/线程间 | kernel buffer（支持 fd 传递） | 双向 |
| 消息队列（POSIX） | 进程间 | kernel mqueue | 优先队列 |
| 消息队列（System V） | 进程间 | kernel msqid | 队列 |
| channel (Go) | 协程间 | runtime buffer | CSP 模型 |
| 异步消息 (actor) | 任务间 | 框架 mailbox | Actor 模型 |

### 2.4 中断与信号资源

#### 2.4.1 硬件中断号（IRQ）

仅**内核线程/进程**可处理硬件中断。中断号是系统级独占资源：

```
x86-64 APIC 中断向量分配（典型配置）：
  0x00-0x1F: 异常与陷阱（#DE, #UD, #GP, #PF 等）
  0x20-0x2F: 外部设备 IRQ 0-15（传统 PIC 兼容）
  0x30-0x3F: IRQ 16-23
  0x40-0xEF: PCIe MSI-X 中断向量（动态分配）
  0xF0-0xFF: IPI/Local APIC 定时器
```

**每设备中断号分配**（以 NVMe SSD 为例）：
```bash
# cat /proc/interrupts | grep nvme
  47:      52738     PCI-MSI 32768-edge      nvme0q0 (admin)
  48:    1048576     PCI-MSI 32769-edge      nvme0q1 (I/O)
  49:    1048576     PCI-MSI 32770-edge      nvme0q2 (I/O)
  ...
```

每个 MSI-X 中断向量绑定到特定 CPU 核心，实现 **RPS（Receive Packet Steering）** 负载均衡。

**中断的资源层级**：

| 层 | 管理实体 | 分配/释放 | 用户态感知 |
|:---|:---------|:----------|:-----------|
| 硬件 | PCIe 设备 | 固件枚举 | 不可见 |
| 内核 | IRQ 描述符 | request_irq() | /proc/interrupts |
| 设备驱动 | handler | 驱动的 probe/remove | 通过信号（SIGIO/SIGALRM）间接感知 |
| 用户态 | signal handler | sigaction() | 收到中断传递的信号 |

#### 2.4.2 信号（Signal）资源

```
进程 A (PID=1000)
  ├── sigaction(SIGTERM, handler)  -- 进程级信号处理
  ├── sigprocmask()                 -- 进程级信号掩码
  ├── pending signals               -- 未决信号集
  │
  ├── 线程 1 (TID=1001)
  │    ├── sigaction() shared       -- 同进程共享表
  │    └── sigprocmask() per-thread -- 每个线程可独立屏蔽
  │
  └── 线程 2 (TID=1002)
       └── (同样结构)
```

**信号资源的关键属性**：

- 信号处理函数表（`struct sighand_struct`）是线程组共享的（`CLONE_SIGHAND`）
- 信号掩码（`blocked`）是线程私有的（每个 `task_struct` 独立）
- 实时信号（`SIGRTMIN`~`SIGRTMAX`, 32-64）携带数据（`siginfo_t`），可实现用户态中断
- 信号队列深度：非实时信号无排队（同信号多次只记一次），实时信号有排队（默认上限 `/proc/sys/kernel/rtsig-max`，默认 65536）

**信号作为跨实体中断机制**：

```
发送方             内核 signal_wake_up()           接收方
进程 B ─── kill(1000, SIGUSR1) ──→ 信号挂入 pending ──→ 调度返回用户态前检查
线程 C ─── pthread_kill(1002, SIGUSR1) ──────────────→ 目标线程检查
内核 ────── force_sig(SIGKILL, task) ─────────────────→ 强制终止
```

### 2.5 文件资源体系

#### 2.5.1 文件打开三层结构

```
进程 A (fd=3)
  └── struct fdtable
       └── fd_array[3] ──→ struct file (file 1)
                              ├── f_path ──→ dentry ──→ inode (磁盘上文件)
                              ├── f_pos      (读写指针)
                              ├── f_mode     (O_RDONLY/O_WRONLY)
                              ├── f_count    (引用计数)
                              └── f_op       (文件操作函数表)
```

**共享 vs 独立**：

| 场景 | file 结构 | dentry 缓存 | inode | 数据页缓存 |
|:-----|:---------|:------------|:------|:-----------|
| 同一进程多次 open | 不同 file（独立 f_pos） | 共享 | 共享 | 共享 |
| fork 后父子进程 | 共享 file（继承引用） | 共享 | 共享 | 共享 |
| 不同进程 open 同文件 | 不同 file | 共享 | 共享 | 共享 |
| 线程共享 fd 表 | 共享 file（同一指针） | 共享 | 共享 | 共享 |

**文件锁的跨实体影响**：

```c
// POSIX 记录锁（fcntl F_SETLK）— 进程级
// 进程内所有线程共享同一锁，一个线程释放则全进程释放
struct file_lock {
    struct file *fl_file;
    struct task_struct *fl_owner;  // 注意：这是进程级所有权
    loff_t fl_start, fl_end;      // 锁定的字节范围
    short fl_type;                 // F_RDLCK/F_WRLCK/F_UNLCK
};
```

**关键陷阱**：POSIX 记录锁的 `fl_owner` 是进程 ID 而非线程 ID，意味着线程 A 加的锁可以被线程 B 释放。这是多线程编程中常见的隐蔽 bug。

### 2.6 事件资源与队列

#### 2.6.1 系统级事件机制

| 机制 | 内核对象 | 等待方式 | 唤醒方式 | 适用层级 |
|:-----|:---------|:---------|:---------|:---------|
| wait_queue | wait_queue_head_t | `prepare_to_wait()` + `schedule()` | `wake_up()` | 所有进程/线程 |
| futex (Fast Userspace Mutex) | 用户态 int + 内核队列 | `futex(FUTEX_WAIT)` | `futex(FUTEX_WAKE)` | 线程（pthread 实现） |
| eventfd | eventfd_ctx | `read()/poll()` | `write()` | 跨进程/线程 |
| signalfd | sighand_struct | `read()/poll()` | 信号投递 | 进程 |
| timerfd | hrtimer | `read()/poll()` | 定时器到期 | 进程 |

**futex 的演进**（线程同步的核心原语）：
```
传统 mutex（futex 之前）：
  每次 lock/unlock 都进入内核 → ~100ns 系统调用

Futex (Linux 2.6, 2003)：
  无竞争时 → 纯用户态原子操作 ~5ns
  有竞争时 → futex(FUTEX_WAIT) 进入内核 ~200ns

Futex2 / PI Futex（实时）：
  优先级继承 → 解决优先级反转问题
  NPTL 内部实现

LRU Futex (Linux 5.x+)：
  基于 LRU 的 hash 表，解决 futex hash 冲突
```

#### 2.6.2 I/O 事件队列（epoll 深度解析）

epoll 是 Linux 上事件驱动 I/O 的核心机制，其内部数据结构：

```
eventpoll (epoll 实例)
  ├── rbtree (红黑树) — 存放所有被监控的 fd
  │   ├── epitem 1: fd=3, events=EPOLLIN
  │   ├── epitem 2: fd=4, events=EPOLLOUT|EPOLLET
  │   └── epitem 3: fd=5, events=EPOLLIN
  │
  ├── rdllist (就绪链表) — 有事件发生的 fd 链表
  │   └── 当 NIC 中断→驱动处理→数据到达→tcp_data_queue()
  │        → sock_def_readable() → ep_poll_callback()
  │        → 将 epitem 移入 rdllist → wake_up() 唤醒 epoll_wait()
  │
  └── wq (等待队列) — 阻塞在 epoll_wait() 上的线程
```

**epoll 的工作模式**：

| 模式 | 触发条件 | 通知次数 | 适用场景 |
|:-----|:---------|:---------|:---------|
| 水平触发 (LT, 默认) | fd 有数据即触发 | 只要没读完就不断通知 | 编程简单、不易漏事件 |
| 边沿触发 (ET) | 状态变化时触发一次 | 每次状态变更仅一次 | 高性能、需配合 non-blocking + 循环读 |

**epoll 调度偏差**（`thundering herd` 问题）：

当多个线程/进程在同一个 epoll fd 上调用 `epoll_wait()`，事件到达时所有等待者被唤醒，但只有一个能处理事件（实际资源竞争模式）：

```c
// Linux 4.5+ — EPOLLEXCLUSIVE 标志解决惊群
struct epoll_event ev = {.events = EPOLLIN | EPOLLEXCLUSIVE};
epoll_ctl(epfd, EPOLL_CTL_ADD, fd, &ev);
// 此时只会唤醒一个等待线程
```

#### 2.6.3 运行时事件队列

| 运行时 | 事件队列模型 | 数据结构 | 调度策略 |
|:-------|:------------|:---------|:---------|
| Go runtime | 全局运行队列 + 本地 P 队列 | deque（双向链表） | work-stealing（每个 P 从其他 P 偷取） |
| libuv (Node.js) | 单线程事件循环 | 优先队列（timer）+ 链表（I/O）+ 回调 | round-robin 阶段式处理 |
| Python asyncio | 事件循环调度器 | heap（timer）+ deque（ready）+ callback | 协作式非抢占 |
| Java Loom | ForkJoinPool 工作窃取 | 全局队列 + 各线程本地队列 | work-stealing |
| liburing | SQ 提交队列 + CQ 完成队列 | ring buffer（无锁） | 批处理 + 顺序保证 |

**Go G-P-M 调度器的事件队列**：

```
M (OS Thread, 机器线程)
  └── P (Processor, 逻辑处理器, GOMAXPROCS 个)
       ├── runq (本地运行队列, 容量 256)
       │    ├── goroutine 1 (state=Grunnable)
       │    ├── goroutine 2 (state=Grunnable)
       │    └── ... (ring buffer, 无锁 CAS 操作)
       │
       ├── timers (计时器堆)
       │
       └── mcache (本地内存缓存)

sched (全局调度器结构)
  ├── runq (全局运行队列, 锁保护)
  ├── pidle (空闲 P 链表)
  └── midle (空闲 M 链表)

特殊队列：
  ├── runqnext — 下一个立即执行的 goroutine（优先级最高）
  ├── gcwait — GC 等待队列
  └── sched.gFree — 已退出的 goroutine 栈缓存
```

### 2.7 时间与定时资源

#### 2.7.1 定时器层级

```
时钟源 (Time Source)
  ├── HPET (High Precision Event Timer) — ~14.318MHz, 精度 ~70ns
  ├── ACPI PM Timer — ~3.579MHz
  ├── TSC (Time Stamp Counter) — CPU 频率，最佳精度 ~1ns
  │    └── 现代 TSC：invariant TSC 保证恒定频率
  └── LAPIC Timer (Local APIC) — 每个 CPU 核独立定时器

定时器实现
  ├── hrtimer (高精度定时器, Linux 2.6.16+, 精度 ~1ns)
  │    └── 红黑树组织，最早到期节点在左子节点
  │         └── tickless 模式 (NO_HZ_IDLE/NO_HZ_FULL)
  │
  └── timer wheel (传统定时器, 精度 jiffy=1~10ms)
       └── 多级时间轮 (Multi-level Time Wheel)
            └── TVN_SIZE=64, TVR_SIZE=256, 共 5 级

各层级定时器消耗
  ├── 进程级 alarm/setitimer — 精度 ~10ms
  ├── 线程级 pthread_cond_timedwait — 精度取决于 OS
  ├── 协程级 timer.After (Go) — 精度 ~1ms（hrtimer 回调）
  └── 任务级 scheduled task — 精度取决于框架调度间隔
```

**定时器数量影响**（Go runtime 为例）：
```go
// 每个 goroutine 调用 time.After() 会创建一个 hrtimer
// 调度器使用四叉堆管理所有定时器，复杂度 O(log n)
// 百万级定时器时 GC 扫描堆本身成为瓶颈
// Go 1.22+ 针对此优化：zero allocation timer
```

### 2.8 调试与可观测资源

（详见第 7 章完整展开，此处列资源概览）

| 资源 | 接口 | 归属层 | 影响 |
|:-----|:-----|:-------|:-----|
| ptrace | `PTRACE_ATTACH/TRACEME` | 进程级 | 停止目标进程 |
| eBPF program | `bpf()` 系统调用 | 内核级 | 动态插桩 |
| perf_event | `perf_event_open()` | 内核/硬件级 | 性能采样 |
| tracepoint | `/sys/kernel/tracing/` | 内核静态插桩 | 低开销 |
| kprobe/uprobe | 内核/用户态动态插桩 | 内核/进程级 | 运行时注入 |
| core dump | `/proc/sys/kernel/core_pattern` | 进程级 | 崩溃快照 |
| /proc 文件系统 | `/proc/[pid]/maps/mem/fd/...` | 进程级 | 实时读进程状态 |

### 2.9 资源所有权模型

#### 2.9.1 独占 vs 共享四象限

```
                 独占 (Exclusive)                   共享 (Shared)
           ┌─────────────────────────┬─────────────────────────┐
  进程     │ 页表 (CR3)              │ 文件系统页缓存           │
           │ 虚拟地址空间            │ 内核全局表 (VFS/网络/...) │
           │ PID, TGID              │ 物理内存页 (COW 前共享)   │
           │ /proc/[pid]/...        │                          │
           ├─────────────────────────┼─────────────────────────┤
  线程     │ 栈 (SP 唯一)            │ 地址空间 (页表)           │
           │ 寄存器上下文            │ 文件描述符表              │
           │ errno (TLS 变量)        │ 信号处理表                │
           │ TID                     │ 当前工作目录 (cwd)        │
           ├─────────────────────────┼─────────────────────────┤
  协程     │ 栈 (独立区域)           │ 堆                       │
           │ 协程局部存储 (CLS)      │ 全局变量                  │
           │ 状态 (pause/resume)     │ 文件描述符表              │
           │                         │ 线程局部存储 (TLS, 共享)  │
           ├─────────────────────────┼─────────────────────────┤
  任务     │ 任务上下文 (输入/状态)   │ 任务依赖的数据源           │
           │ 执行日志/Trace           │ 连接池/线程池              │
           │ 任务 ID                  │ 共享缓存                  │
           └─────────────────────────┴─────────────────────────┘
```

#### 2.9.2 Copy-on-Write（COW）的资源共享

fork() 的 COW 机制是资源所有权转换的经典案例：

```
fork() 前：
  父进程 ──→ 物理页 A (引用计数=1) ←── 页表项 (写权限)

fork() 后：
  父进程 ──→ 物理页 A (refcount=2) ←── 页表项 (只读, COW 标记)
  子进程 ──→ 物理页 A (refcount=2) ←── 页表项 (只读, COW 标记)

子进程写入 (page fault)：
  子进程 ──→ 物理页 A' (refcount=1) ←── 新分配的物理页
  父进程 ──→ 物理页 A  (refcount=1) ←── 原物理页 (恢复写权限)
```

**COW 的资源特性**：

| 资源 | fork 后状态 | 首写触发 | 典型 COW 节省 |
|:-----|:------------|:---------|:--------------|
| 代码段 (.text) | 共享（始终只读） | 永不 | 100%（所有进程共享同一份） |
| 数据段 (.data) | COW 共享 | 子进程首次写全局变量 | ~90%（大量页无需复制） |
| 堆 (heap) | COW 共享 | malloc 写操作 | ~70-80% |
| 栈 | COW 共享 | 函数调用栈帧写入 | ~50%（子进程快速 exec 则几乎全省） |
| 文件映射 (MAP_SHARED) | 直接共享 | 不触发 COW | 写共享页直接可见 |
| 匿名映射 (MAP_PRIVATE) | COW 共享 | 写时复制 | 同数据段 |

**性能数据**（Linux 5.15, 2GB RSS 的进程 fork）：
- COW 复制延迟：首次写触发时 ~0.5-2μs/缺页（4KB 页）
- 无 COW 场景：fork 立即完成 ~10μs，不复制任何物理页
- catch：大量私有匿名映射触发的缺页可能导致严重抖动（~ms 级延迟）

#### 2.9.3 资源继承规则

| 资源类型 | fork() | pthread_create() | coroutine spawn | task submit |
|:---------|:-------|:-----------------|:----------------|:------------|
| 栈 | 复制（COW） | 新建 | 新建(小栈) | 新建 |
| 堆 | COW | 共享 | 共享 | 共享 |
| 文件描述符 | 继承（或共享） | 共享 | 共享 | 共享/继承 |
| 信号处理 | 继承 | 共享 | 继承(复制) | 框架定义 |
| 环境变量 | 继承 | 继承 | 继承 | 继承 |
| 工作目录 | 继承 | 继承 | 继承 | 继承 |
| umask | 继承 | 继承 | 继承 | 继承 |
| 定时器 | 不继承 | 不继承 | 继承(事件循环) | 框架定义 |
| pending 信号 | 不继承 | 不继承 | N/A | N/A |
| 文件锁 | 不继承（POSIX 规范） | 共享 | 共享 | 共享 |
| 内存锁 (mlock) | 不继承 | 共享 | 共享 | 共享 |
| CPU 亲和性 | 继承 | 继承 | 依赖运行时 | 框架定义 |
| cgroup | 继承 | 继承 | 继承 | 框架定义 |

---

## 3. 实现层次深度分析

### 3.1 OS 内核实现：以 Linux 为例

#### 3.1.1 task_struct 深度剖析

Linux 内核中，进程和线程共用同一数据结构 `struct task_struct`，这是系统活动实体的最底层抽象。进程与线程的区别仅在于 `clone()` 时的标志位组合。

`task_struct` 的 ~200 个字段的核心分类（按资源维度）：

```c
struct task_struct {
    // === [1] 调度相关 ===
    volatile long state;           // 运行状态 (TASK_RUNNING/INTERRUPTIBLE/...)
    unsigned int __state;          // 内核审计（lockdep 追踪）
    struct sched_entity se;        // CFS 调度实体 (vruntime, weight)
    struct sched_rt_entity rt;     // RT 调度实体 (priority, time_slice)
    struct sched_dl_entity dl;     // Deadline 调度实体 (deadline, runtime)
    int prio, static_prio, normal_prio;
    unsigned int policy;           // SCHED_OTHER/FIFO/RR/DEADLINE/IDLE/BATCH

    // === [2] 内存管理 ===
    struct mm_struct *mm;           // 用户地址空间（页表0）— 线程共享
    struct mm_struct *active_mm;    // 内核线程无 mm，借用上一进程的 mm
    // ★ mm = NULL 表示内核线程

    // === [3] 文件资源 ===
    struct files_struct *files;     // 文件描述符表
    struct fs_struct *fs;           // 文件系统信息（cwd, umask）
    struct signal_struct *signal;   // 信号处理器表（共享）
    struct sighand_struct *sighand; // 信号处理函数表（共享）

    // === [4] 进程关系 ===
    struct task_struct __rcu *real_parent;  // 实际父进程
    struct task_struct __rcu *parent;       // 接收信号的父进程
    struct list_head children;              // 子进程链表
    struct list_head sibling;               // 兄弟进程链表
    struct task_struct *group_leader;       // 线程组组长

    // === [5] 命名空间 ===
    struct nsproxy *nsproxy;        // 挂载/IPC/UTS/网络/PID/用户/时间命名空间

    // === [6] 审计与追踪 ===
    struct task_io_accounting ioac; // I/O 统计
    struct ftrace_ret_stack *ret_stack;  // ftrace 返回栈
    struct kprobe *kprobe_orig_ret; // kprobe 探测点
    unsigned int trace_overrun;     // uprobe 溢出计数
    int ptrace;                     // ptrace 状态
    unsigned int ptrace_event;      // ptrace 事件掩码（PTRACE_EVENT_*）

    // === [7] cgroup 资源控制 ===
    struct css_set __rcu *cgroups;  // cgroup 子系统状态
    struct cgroup *cgroup;          // 默认 cgroup

    // === [8] 定时器 ===
    struct hrtimer *timer_slack_ns; // 定时器松弛量
    struct posix_cputimers posix_cputimers; // CPU 时间定时器

    // === [9] 性能事件 ===
    struct perf_event_context *perf_event_ctxp; // perf 事件上下文
    struct uprobe_task *utask;      // uprobe 任务状态

    // === [10] 命名空间 PID ===
    struct pid *thread_pid;         // 本线程的 PID
    struct pid_link pids[PIDTYPE_MAX]; // 各类 PID 链接
    struct list_head thread_group;  // 线程组链表
};
```

**关键字段含义**（资源所有权指示器）：

| 字段 | 进程 (fork+exec) | 线程 (pthread) | 内核线程 (kthread) |
|:-----|:-----------------|:---------------|:-------------------|
| `mm` | 新分配 | 共享父进程 | NULL |
| `files` | 复制（COW）/ 共享(CLONE_FILES) | 共享 | 共享父进程/init |
| `sighand` | 共享 / 独立 | 共享 | N/A（无用户态信号） |
| `group_leader` | self | 主线程 | self |
| `real_parent` | 父进程 | 主线程 | kthreadd |

#### 3.1.2 进程/线程创建路径

```
fork() ──> kernel_clone()
            ├── copy_process()  ←── 核心函数
            │    ├── dup_task_struct()       — 复制 task_struct + 内核栈 (~15KB)
            │    ├── copy_semundo()          — 信号量撤销
            │    ├── copy_files()            — fd 表 (CLONE_FILES 决定)
            │    ├── copy_fs()               — fs_struct (cwd/umask)
            │    ├── copy_sighand()          — 信号处理表 (CLONE_SIGHAND)
            │    ├── copy_signal()           — 信号统计信息
            │    ├── copy_mm()               — 地址空间 (CLONE_VM)
            │    ├── copy_namespaces()       — 命名空间
            │    ├── copy_io()               — I/O 上下文
            │    ├── copy_thread()           — 初始化线程上下文 (寄存器/栈)
            │    ├── sched_fork()            — 调度实体初始化 (vruntime 继承?)
            │    ├── cgroup_can_fork()       — cgroup 权限检查
            │    └── perf_event_fork()       — perf 事件跟踪
            │
            ├── wake_up_new_task() ←── 加入运行队列
            │    └── activate_task() → enqueue_task_fair() / 选择调度类
            │
            └── 返回 child PID
```

**性能数据**（Linux 6.1, x86-64, Intel Xeon Gold 6338）：

| 操作 | 延迟 (μs) | 主要开销来源 |
|:-----|:---------:|:------------|
| fork() 空进程 | ~10-30 | copy_process, sched_fork, wake_up |
| fork() + mm 100MB RSS | ~500-2000 | COW 页表复制 + TLB 刷新 |
| pthread_create() | ~50-200 | clone(CLONE_VM|CLONE_FILES|...) |
| kthread_create() | ~10-30 | 无 mm 复制 |
| execve() | ~100-500 | 加载 ELF 二进制, 设置新地址空间 |

#### 3.1.3 调度器架构

Linux 调度器使用**调度类**（Scheduling Class）体系，通过模块化实现不同策略：

```
核心调度器 (__schedule())
  │
  ├── pick_next_task() — 按优先级遍历调度类
  │    ├── [1] stop_task_class (最高优先级) — 停止调度 (migration/NR_CPUS)
  │    ├── [2] dl_sched_class (Deadline) — EDF + CBS (SCHED_DEADLINE)
  │    ├── [3] rt_sched_class (Real-Time) — FIFO/RR (SCHED_FIFO/SCHED_RR)
  │    ├── [4] fair_sched_class (CFS) — 完全公平调度 (SCHED_NORMAL/SCHED_BATCH)
  │    └── [5] idle_sched_class (最低优先级) — 空闲任务
  │
  └── context_switch()
       ├── switch_mm() — 切换页表 (CR3), TLB 刷新
       └── switch_to() — 保存/恢复寄存器 (__switch_to_asm)
```

**CFS 调度实体核心公式**：

```
vruntime = 实际运行时间 × (NICE_0_LOAD / weight)
          ↓
调度决策：选择 vruntime 最小的实体（红黑树最左节点）

时间片 = sysctl_sched_latency × weight / cfs_rq->load
       (默认 ~6ms，通过调度延迟规范化)
```

**调度延迟核心参数**：

| 参数 | 默认值 | 含义 |
|:-----|:-------|:-----|
| `sysctl_sched_latency` | 6ms (40 核以下) | 运行队列上的进程至少运行一次的总时间窗口 |
| `sysctl_sched_min_granularity` | 0.75ms | 每个进程至少运行的最小时间片 |
| `sysctl_sched_wakeup_granularity` | 1ms | 唤醒进程可抢占当前进程的 vruntime 超前阈值 |
| `sysctl_sched_migration_cost` | 500μs | 进程迁移代价估计（防止过度迁移） |

**线程组调度（TG, Task Group）**：

CFS 通过层级调度（`struct sched_entity` 嵌套）实现 cgroup 级配额：

```
root_task_group (CPU 100%)
  ├── cgroup_A (quota=50%)
  │    ├── thread A1 (weight=1024)
  │    └── thread A2 (weight=1024)
  │         → 每个线程各得 25% CPU
  │
  └── cgroup_B (quota=50%)
       └── thread B1 (weight=1024)
            → 单线程得 50% CPU
```

#### 3.1.4 进程/线程状态机

```
原始进程状态 (Linux < 2.6)：
TASK_RUNNING ──→ TASK_INTERRUPTIBLE ──→ TASK_UNINTERRUPTIBLE
       ↓                                    ↓
  TASK_STOPPED ←───── signal STOP         TASK_ZOMBIE (exit)
       ↓
  TASK_TRACED (ptrace)

Linux 2.6+ 扩展：
  TASK_DEAD — exit 后的过渡状态
  TASK_WAKEKILL — 只被 SIGKILL 唤醒的不可中断睡眠
  TASK_KILLABLE — TASK_UNINTERRUPTIBLE | TASK_WAKEKILL
  TASK_IDLE — 空闲线程 (GCC __attribute__((noreturn)))

非标准但常用的状态：
  ▸ TASK_PARKED — 停靠状态 (kthread)
  ▸ TASK_NOLOAD — 不计入负载计算
  ▸ TASK_NEW — 创建后未放入运行队列
```

**Linux 线程状态转换矩阵**：

```
                          ┌──────────────────┐
     (fork/clone) ───────→│    TASK_NEW      │
                          └────────┬─────────┘
                                   │ wake_up_new_task()
                                   ↓
                    ┌──────────────────────────┐
     <─── deactivate_task() ────│      TASK_RUNNING      │──── activate_task() ────→
     │                          │    (on runqueue)      │
     │                          └──────────────────────────┘
     │                                         │
     │  try_to_wake_up()          │    schedule() pick_next_task
     │              ↑             │               ↓
     │              │             ↓     ┌──────────────────┐
     │     ┌──────────────────┐    <────│   context_switch  │
     └─────│TASK_INTERRUPTIBLE│         └──────────────────┘
           │  (waiting wq)    │                      │
           └──────────────────┘                      ↓
                                   ┌──────────────────┐
                 SIGKILL ════╗     │TASK_UNINTERRUPTIBLE│
                             ║     │ (waiting IO/D state)│
                 wake_up()   ║     └──────────────────┘
                             ║              │
                             ║    signals (如 SIGKILL/SIGSTOP)
                             ↓              ↓
                    ┌────────────────────────────┐
                    │       TASK_STOPPED          │ ← SIGSTOP/SIGTSTP
                    │       TASK_TRACED           │ ← ptrace attach
                    └────────────────────────────┘
                             │ SIGCONT / ptrace detach
                             ↓
                    ┌────────────────────────────┐
                    │        TASK_ZOMBIE          │ ← do_exit()
                    │   (struct task retained)    │ → release_task()
                    └────────────────────────────┘ → TASK_DEAD
```

### 3.2 运行时实现

#### 3.2.1 Go Goroutine（G-P-M 模型）

**核心数据结构**：

```go
// goroutine 结构 (runtime/runtime2.go, ~100 字段)
type g struct {
    stack       stack          // [stack.lo, stack.hi) — goroutine 栈区间
    stackguard0 uintptr        // 栈增长检查点 (morestack 触发地址)
    stackguard1 uintptr        // 用于 C 栈的栈增长检查点

    m              *m          // 当前绑定的 M (OS 线程)
    sched          gobuf       // goroutine 调度上下文 (sp, pc, bp, ret)
    atomicstatus   uint32      // _Gidle/_Grunnable/_Grunning/_Gsyscall/_Gwaiting/_Gdead

    goid           int64       // Goroutine ID (调试用)
    waitsince      int64       // 进入等待状态的时间戳
    waitreason     waitReason  // 等待原因

    // 协程本地存储
    labels         unsafe.Pointer // profiler 标签
    timer          *timer          // 当前 goroutine 关联的定时器

    // 栈管理
    preempt        bool        // 抢占标记（异步抢占）
    preemptStop    bool        // 抢占时停止（非恢复性）
    paniconfault   bool        // 是否在地址错误时 panic
    gcscandone     bool        // GC 扫描完成

    // 调试辅助
    writesbuf      struct{...} // 写屏障缓冲区
    tracking       struct{...} // 追踪信息
}
```

**P（Processor，逻辑处理器）结构**：

```go
type p struct {
    id          int32      // 物理 CPU 绑定 hint
    m           muintptr   // 绑定的 M（无则为 nil）
    runqhead    uint32     // 本地运行队列头部
    runqtail    uint32     // 本地运行队列尾部
    runq        [256]guintptr // 环形缓冲区的 goroutine 队列
    runnext     guintptr   // 下一个待运行的 goroutine（优先级最高）

    gFree struct {
        gList              // 已退出的 goroutine 栈链表
        n    int32         // 数量（栈可复用）
    }

    // 调度统计
    schedtick   uint32    // 调度器 tick 计数（用于工作窃取公平性）
    syscalltick uint32    // 系统调用 tick 计数
}
```

**G-P-M 协作流程图**：

```
                         ┌──────────────┐
                         │  GOMAXPROCS  │ ← 环境变量/编程设置（默认 CPU 核数）
                         └──────┬───────┘
                                │
                                ↓
     ┌─────────────────────────────────────────────┐
     │                   P (n)                      │
     │  ┌─────────────────────────────────────┐     │
     │  │  本地运行队列 (runq, ring buffer 256)  │     │
     │  │  [g1]→[g2]→[g3]→[...]→[g256]         │     │
     │  │  runnext=[g_immediate]                │     │
     │  └─────────────────────────────────────┘     │
     │           ↑            ↓                    │
     │      work-stealing  系统调用阻塞时           │
     └─────────────────────────────────────────────┘
                │                    │
                ↓                    ↓
     ┌──────────────────┐  ┌──────────────────┐
     │    M (OS 线程)    │  │    M (OS 线程)    │
     │  run: g_current  │  │  run: g_current  │
     │  curg: g_current │  │  curg: g_current │
     │  p: P(tied)      │  │  p: P(tied)     │
     └──────────────────┘  └──────────────────┘
                │                    │
                ↓                    ↓
     ┌─────────────────────────────────────────────────┐
     │                  全局运行队列                     │
     │  sched.runq (链表, mutex 保护)                   │
     │  [g_global_1]→[g_global_2]→[...]                │
     └─────────────────────────────────────────────────┘
```

**关键调度时序**：

| 事件 | 处理流程 | 切换开销 |
|:-----|:---------|:---------|
| 通道通信（channel send/recv） | gopark() → sudog 操作 → goready() | ~15-30ns |
| 系统调用（阻塞式） | entersyscall() → exitsyscall() → 绑定新 P | ~100-500ns |
| 定时器到期 | checkTimers() → goready(对应的 g) | ~20-50ns |
| 主动 yield (runtime.Gosched) | gopark() → 放入全局队列末尾 | ~5-15ns |
| 抢占（10ms 间隔） | sysmon 线程发出抢占信号 → sigpreempt → 安全点→调度 | ~1-3μs |
| 栈增长（morestack） | 检查 stackguard → 新栈分配 → 复制栈帧 | ~0.5-2μs |
| GC STW（停止世界） | 抢占所有 goroutine → GC 阶段 → 恢复 | ~100μs-10ms |

**Goroutine 栈管理策略**：

```
初始栈：2KB (Go 1.4+)
  └── stackalloc() 从全局栈缓存获取
       │
增长方式：连续栈（contiguous stack, Go 1.3+）
  └── 原栈满 → morestack() 检测
       → 分配新栈（~2× 增长, 最小翻倍）
       → 使用栈复制器（stack copier, 调整所有指针
       → 释放旧栈
       │
       └── 在 GC 扫描期间完成栈收缩
            └── 空闲 goroutine 栈缩小到初始大小（~2KB）

栈增长上限：
  1GB (Go <= 1.18)
  250GB (Go 1.19+), 实际由 maxstacksize 限制
```

**性能数据对比**（协程 vs 线程 vs 进程）：

| 指标 | goroutine | OS 线程 (pthread) | 进程 (fork) |
|:-----|:---------:|:-----------------:|:-----------:|
| 创建延迟 | ~0.1-0.5μs | ~50-200μs | ~10-30μs (fork) |
| 最大数量（4GB 地址空间） | 1,000,000+ | ~4,000 (默认 8MB 栈) | ~500 (默认 8MB 栈) |
| 切换延迟（无竞争） | ~10-30ns | ~0.1-1μs | ~1-10μs |
| 内存占用（初始） | ~4KB (栈+goroutine 结构) | ~8MB (栈) + ~2KB (内核) | ~8MB (栈) + ~8KB (内核) |
| 栈增长策略 | 动态（连续栈复制） | 固定（MAP_GROWSDOWN） | 固定 |

#### 3.2.2 Rust async/await（基于任务的协作式调度）

Rust 的 async/await 与 Go 的 goroutine 有本质区别——它是**零开销抽象**（zero-cost abstraction）驱动的编译期状态机：

```rust
// 示例：async fn 编译为状态机
async fn example() -> i32 {
    let x = foo().await;     // state 0 → 挂起 → state 1
    let y = bar(x).await;    // state 1 → 挂起 → state 2
    x + y
}

// 编译器展开为（简化）：
enum ExampleStateMachine {
    State0 { foo_fut: FooFuture },
    State1 { x: i32, bar_fut: BarFuture },
    State2,
}

impl Future for ExampleStateMachine {
    type Output = i32;
    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<i32> {
        loop {
            match self {
                ExampleStateMachine::State0(ref mut f) => {
                    let x = ready!(f.foo_fut.poll(cx)); // 挂起点
                    *self = ExampleStateMachine::State1 { x, bar_fut: bar() };
                }
                ExampleStateMachine::State1 { ref mut x, ref mut f } => {
                    let y = ready!(f.bar_fut.poll(cx));
                    return Poll::Ready(*x + y);
                }
                ...
            }
        }
    }
}
```

**关键设计差异**：

| 维度 | Go goroutine | Rust async |
|:-----|:-------------|:-----------|
| 调度方式 | 运行时自动调度 | 用户定义 Executor |
| 栈管理 | 运行时栈（连续栈复制） | 无栈（编译为状态机枚举） |
| 内存分配 | 每个 goroutine 分配栈 | 状态机大小在编译期确定 |
| 抢占 | 有（10ms 异步抢占） | 无（协作式，.await 点 yield） |
| 调度器 | Go runtime 内置 M:N | 用户选择（tokio/async-std/smol） |
| 跨线程 | 自动（work-stealing） | 需要 Send 约束 |
| 取消 | 通过 channel/context | Drop trait 自动清理 |

**Tokio 调度器设计**（最流行的 Rust 异步运行时）：

```
tokio::runtime::Runtime
  ├── 全局调度器 (GlobalScheduler)
  │    ├── inject (全局 FIFO 队列) — 新任务/跨线程窃取
  │    └── blocking_pool — 阻塞任务线程池（上限 512 线程）
  │
  └── 每个工作线程 (Worker) 维护：
       ├── local (本地 LIFO 队列) — 新产生的 task
       │     └── LIFO 策略 → 更好的缓存局部性
       ├── steal (从其他 Worker 的 local 队列窃取)
       │     └── 窃取策略：随机 + 第一次失败后轮询
       └── I/O 驱动 (mio/epoll/io_uring)
            └── 每个 工作线程 一个 epoll fd

调度策略（Tokio 当前默认）：
  ┌────────────────────────────────────────────┐
  │ 1. run_local: 优先执行本地的 LIFO 队列     │
  │ 2. steal_global: 从 inject 队列窃取      │
  │ 3. steal_remote: 从其他 Worker 的 local 窃│
  │ 4. park: 无任务时阻塞在 epoll_wait       │
  └────────────────────────────────────────────┘
```

**性能对比**：Rust async 在完全无分配的场景下具有最好的微基准性能，但在实际应用中大量 `.await` 点的内存占用可能超过 goroutine 的栈分配。

#### 3.2.3 Python asyncio（单线程协作调度）

```python
# Python asyncio 事件循环核心结构
class BaseEventLoop:
    _ready: collections.deque  # 就绪回调队列（FIFO）
    _scheduled: list[TimerHandle]  # 定时器堆（最小堆）
    _stopping: bool
    
    # 跨层调度：每个 task 是一个 generator-based coroutine wrapper
    
    def _run_once(self):
        # 1. 处理定时器
        #    - 从 _scheduled 堆中取出到期定时器
        #    - 移入 _ready 队列
        
        # 2. I/O 事件轮询 (epoll.poll / select.select)
        #    - timeout = min(下一个定时器时间, 默认值)
        #    - 获取就绪的 fd 事件
        #    - 为每个 fd 加入回调到 _ready
        
        # 3. 处理 _ready 队列中的所有回调
        #    - pop 一个回调，执行
        #    - 回调内部可能继续添加新的回调到 _ready
        #    - ★ 关键：单线程，一个回调阻塞则整个循环卡死
```

**asyncio 的关键资源**：

| 资源 | 模型 | 说明 |
|:-----|:-----|:------|
| 事件循环 | 单线程 | 一个事件循环绑定一个 OS 线程 |
| 协程任务 | Task 对象 | 包装 coroutine，含 state/stack/exception |
| I/O 复用 | selector（epoll/kqueue） | 注册文件描述符 |
| 队列 | asyncio.Queue | 基于事件循环的 producer-consumer |
| Future | Future 对象 | 异步结果占位，含 callback 链 |
| 锁 | Lock/Event/Semaphore | 通过 Future 实现 awaitable 同步 |
| 执行器 | ThreadPoolExecutor | 将阻塞调用委托给线程池 |

**asyncio 与多进程/多线程结合模型**：

```
asyncio.run(main())     ←── 主事件循环 (单线程)
    │
    ├── await async_io()           — I/O 密集型
    ├── await loop.run_in_executor(None, cpu_bound_func)
    │    └── ThreadPoolExecutor    — 线程池（CPU 密集/阻塞）
    │
    └── multi-processing:
         ├── ProcessPoolExecutor   — 进程池（利用多核）
         └── asyncio.create_subprocess_exec()  — 子进程管理
```

#### 3.2.4 Java Virtual Threads（Project Loom）

Java 19 引入的 Virtual Thread（虚拟线程）是对传统 Green Thread 的现代化重新设计：

```java
// 创建虚拟线程
Thread vt = Thread.startVirtualThread(() -> {
    // 在虚拟线程中执行
    // 阻塞调用（如 socket.read()）会自动挂起 VT
});

// 对比传统线程
Thread t = new Thread(() -> { ... });  // 平台线程（OS 线程包装）
```

**虚拟线程内部实现架构**：

```
虚拟线程 (VirtualThread)
  ├── carrierThread (载体线程) — ForkJoinPool 的工作线程
  │    每个载体线程运行多个 VT，VT 被挂起时载体线程可运行其他 VT
  │
  ├── 挂起机制（park/unpark）
  │    ├── 阻塞调用（如 Socket.read()、Lock.lock()）
  │    │    → java.lang.VirtualThread.park()（内部）
  │    │    → 挂起 VT → 载体线程继续执行其他任务
  │    │
  │    └── 恢复：
  │         → I/O 数据到达（epoll 事件）
  │         → unpark() → VT 重新进入运行队列
  │
  └── 连续栈（Continuation）
       └── StackChunk — 栈帧作为堆对象管理
            ├── 挂起时：栈帧从本地线程栈复制到堆上 StackChunk
            └── 恢复时：StackChunk 复制回本地线程栈
```

**关键性能数据**（Loom vs 传统平台线程）：

| 指标 | 平台线程 | 虚拟线程 | 倍数 |
|:-----|:--------:|:--------:|:----:|
| 最大数量（每 JVM） | ~4,000（默认栈） | 数百万 | 1000× |
| 创建延迟 | ~100μs | ~1μs | 100× |
| 切换延迟 | ~1μs | ~50ns | 20× |
| 内存占用 | ~1MB | ~2KB | 500× |
| 阻塞行为 | 阻塞 OS 线程 | 挂起 VT，载体线程复用 | — |

**Loom 的演化路线**：JDK 21（GA）→ JDK 23（结构化并发 `StructuredTaskScope`） → JDK 24（作用域值 `ScopedValue`，替代 ThreadLocal）

### 3.3 虚拟机实现

#### 3.3.1 JVM 线程模型演化

```
JDK 1.1 (1996) — Green Threads
  ├── JVM 实现自己的线程调度（用户态）
  ├── 在 Solaris 上 1:N（一个内核线程承载多个用户线程）
  └── 缺点：无法利用多核 CPU

JDK 1.2 (1998) — Native Threads
  ├── 1:1 映射到 OS 线程（pthread）
  ├── 利用多核，但创建/切换开销大
  └── 每个 Java 线程 = 一个 OS 线程

JDK 21 (2023) — Virtual Threads (Project Loom)
  ├── M:N 映射（多个 VT 在少数 carrier 线程上）
  ├── 融合了 Green Thread 的效率 + Native Thread 的多核优势
  └── 要求：阻塞操作必须可挂起（不阻塞载体线程）
```

**HotSpot JVM 对 OS 线程的资源映射**：

```
Java 线程
  └── JavaThread (HotSpot 内部结构)
       ├── OSThread (平台抽象)
       │    └── pthread_t (Linux)
       ├── Java 栈 (Java 方法调用)
       │    └── Xss 参数控制大小，默认 1MB (JDK 17+)
       ├── C 栈 (JNI 调用)
       │    └── Compiler2 线程栈大小 ~4MB (C2 JIT 编译)
       └── Thread Control Block
            ├── ThreadLocalMap (线程局部存储)
            ├── 当前 StrackChunk (VT 的连续栈挂起/恢复)
            └── Safepoint 状态 (GC/Deoptimization)
```

#### 3.3.2 Lua Coroutine（对称协程）

Lua 的协程设计是最简洁的协程模型之一，对理解协程本质极有价值：

```lua
-- 创建协程
co = coroutine.create(function()
    local x = coroutine.yield("first yield")
    local y = coroutine.yield("second yield")
    return x + y
end)

-- 恢复执行
local status, result = coroutine.resume(co, 10)   -- x = 10
local status, result = coroutine.resume(co, 20)   -- y = 20
-- 最终返回 30
```

**Lua 协程的核心特征**：

| 特征 | Lua 协程 | 对比其他 |
|:-----|:---------|:---------|
| 对称性 | ✅ 对称（yield/resume 间可自由传递数据） | Python yield 不对称 |
| 栈式 | ✅ 完整栈（可 yield 嵌套调用） | C 的 longjmp 不保留栈 |
| 非抢占 | ✅ 显式 yield 才切换 | Go goroutine 可抢占 |
| 宿主线程 | ✅ 绑定创建它的线程 | Java VT 可迁移 |
| 资源 | 每个协程 ~2-4KB 固定栈 | Go 动态增长 |

### 3.4 上层任务抽象

#### 3.4.1 任务队列与线程池

从 OS 线程到任务框架的层级关系：

```
┌─────────────────────────────────────────────────────┐
│                   应用层任务框架                       │
│  DAG 调度器 / Actor 系统 / 流处理框架                 │
│  管理：任务依赖、失败重试、资源配额                    │
├─────────────────────────────────────────────────────┤
│                   线程/协程池                         │
│  线程池(ThreadPoolExecutor) / Goroutine Pool        │
│  管理：并发度控制、任务队列、线程生命周期              │
├─────────────────────────────────────────────────────┤
│                   运行时调度器                         │
│  Go Scheduler / Tokio / Loom / asyncio              │
│  管理：协程创建、挂起、恢复、工作窃取                  │
├─────────────────────────────────────────────────────┤
│                   操作系统线程/进程                    │
│  Linux clone() / pthread                            │
│  管理：CPU 时间片、内存映射、I/O 调度                 │
├─────────────────────────────────────────────────────┤
│                   硬件执行单元                         │
│  CPU 核心 / 超线程 / 中断控制器                      │
│  管理：指令执行、缓存、中断                          │
└─────────────────────────────────────────────────────┘
```

**典型线程池实现（Java ThreadPoolExecutor）**：

```java
class ThreadPoolExecutor {
    // 核心池化参数
    int corePoolSize;        // 核心线程数（常驻）
    int maximumPoolSize;     // 最大线程数（含临时）
    long keepAliveTime;      // 空闲线程存活时间
    BlockingQueue<Runnable> workQueue;  // 任务队列
    
    // 拒绝策略（队列满 + 线程数达上限时）
    RejectedExecutionHandler handler;
    
    // 工作线程包装
    final class Worker extends AbstractQueuedSynchronizer {
        Thread thread;       // 绑定的 OS 线程
        Runnable firstTask;  // 第一个任务（可选）
        volatile long completedTasks;  // 完成任务计数
    }
}
```

**线程池资源消耗模型**：

```
创建 N 个线程：
  ├── OS 线程：N × 8MB 虚拟地址空间 (栈)
  ├── 内核：N × ~2KB task_struct
  ├── Java 对象：N × ~1KB (Thread + Worker + ...)
  ├── 切换开销：N 个线程的 CFS 调度负担
  └── 缓存竞争：N × L1/L2 cache footprint

典型配置规则：
  CPU 密集型 → corePoolSize = N_CPU + 1
  I/O 密集型 → corePoolSize = N_CPU × (1 + wait_time/service_time)
  混合型     → 经验值：N_CPU × 2-4
```

**Goroutine Pool（ants 库）**—— Go 生态的 goroutine 池化：

```go
// ants 库——限制并发 goroutine 数量
pool, _ := ants.NewPool(100000)  // 池容量 10 万
defer pool.Release()

// 提交任务
pool.Submit(func() {
    // 并发执行的任务
})

// 底层实现：
//   复用 goroutine（减少 goroutine 创建开销）
//   任务通过 channel 提交到工作协程
//   工作协程循环从 channel 取任务执行
//   资源节省：~50% 内存（对比无限制创建 goroutine）
```

#### 3.4.2 DAG 任务调度

当任务间存在依赖关系时，DAG（有向无环图）调度成为必要：

```
任务 A ──→ 任务 B ──→ 任务 D
  │                      ↑
  └──→ 任务 C ──────────┘
  
调度策略（拓扑排序）：
  1. 执行 A（入度为 0）
  2. A 完成后，B 和 C 入度减 1 → 都变为可执行
  3. B 和 C 可以并行执行（依赖线程池）
  4. 两者完成后，D 入度为 0 → 执行 D
```

**资源管理维度**：

| 框架 | 资源隔离 | 并发控制 | 失败处理 | 适用场景 |
|:-----|:---------|:---------|:---------|:---------|
| Airflow | DAG 级（每个 task 独立进程） | 池化 | 重试/标记失败 | 数据管道 ETL |
| Prefect | Task Runner（进程/线程） | 并发限制 | 自动重试+通知 | 通用编排 |
| Dask | 分布式调度器 | work-stealing | 异常恢复 | 数据科学 |
| Ray | 对象存储+ Actor | 分布式调度 | lineage 重放 | AI/分布式计算 |
| Celery | Worker 进程池 | concurrency 参数 | 重试+ack | 异步任务队列 |

**Ray 任务系统的资源模型**（最现代的设计之一）：

```python
import ray

@ray.remote(num_cpus=2, num_gpus=1)
class GPUWorker:
    def train(self, data):
        # 资源：2 CPU + 1 GPU
        pass

@ray.remote(num_cpus=4, memory=8*1024*1024*1024)  # 4 CPU + 8GB 内存
def heavy_task(data):
    pass

# 资源调度：
#   Ray 调度器根据资源需求分配节点
#   资源不足时任务排队等待
#   支持资源开箱释放
```

#### 3.4.3 Actor 模型

Actor 模型将"任务"提升为**自治实体**，每个 Actor 拥有：

```
Actor
  ├── Mailbox (邮箱) — 消息队列
  │    └── 其他 Actor 发送的消息入队
  ├── State (私有状态) — 仅 Actor 内部可读写
  ├── Behavior (行为) — 消息处理函数
  └── Children (子 Actor) — 监督树

消息传递：
  Actor A ──send(msg)──→ Actor B (异步, 不可变)
              ↓
          Actor A 不阻塞，继续处理其他消息

资源模型：
  每个 Actor ≈ 轻量级进程 (Erlang)
  每个 Actor ≈ 线程级对象 (Akka)
  每个 Actor ≈ goroutine + channel (Go/Proto.Actor)
```

**Erlang Actor 进程的资源**：

```erlang
% Erlang 进程（不是 OS 进程，是 Actor 进程）
% 每个进程：~300 字（~2.4KB）堆空间 + 独立的 GC
% 一台机器可创建数千万个 Actor 进程
% 进程间完全不共享内存（容错基石）

% 进程创建
Pid = spawn(fun() -> loop(State) end).

% 消息发送（异步）
Pid ! {request, Data}.

% 进程监控（监督树）
process_flag(trap_exit, true),
link(Pid).
```

**Akka Actor 的资源映射**：

```
Akka ActorSystem
  ├── dispatcher (调度器) — 决定 Actor 在哪些线程上运行
  │    ├── thread-pool-executor — 多线程调度
  │    ├── fork-join-executor  — 工作窃取
  │    └── pinned-dispatcher   — 每个 Actor 绑定一个线程
  │
  ├── mailbox (邮箱，有界/无界)
  │    ├── UnboundedMailbox — 默认
  │    └── BoundedMailbox(max=1000) — 背压
  │
  └── ActorRef — 引用（位置透明）
       ├── LocalActorRef — 同一 JVM
       └── RemoteActorRef — 跨节点（序列化）
```

---

## 4. 生命周期模型

### 4.1 状态机与状态转换

#### 4.1.1 Linux 进程/线程的状态机

（已在 3.1.4 详述，此处聚焦生命周期管理视角）

**进程退出路径**：

```
exit_group() 或 exit()
  │
  ├── do_exit()
  │    ├── exit_signals()      — 发送信号给父进程和子进程
  │    ├── exit_mm()           — 释放地址空间（mmput → mmdrop）
  │    ├── exit_files()        — 关闭文件描述符（put_files_struct）
  │    ├── exit_fs()           — 释放文件系统上下文
  │    ├── exit_sighand()      — 释放信号处理表
  │    ├── exit_thread()       — 清理线程特定数据
  │    ├── __exit_signal()     — 从信号结构中移除
  │    ├── exit_cgroup()       — 从 cgroup 移除
  │    ├── exit_notify()       — 通知父进程（发送 SIGCHLD）
  │    └── schedule()          — 切换到 TASK_ZOMBIE
  │
  ├── TASK_ZOMBIE (僵尸)
  │    └── struct task_struct 保留（wait 需要 PID 和退出码）
  │
  └── wait() / waitpid()
       └── release_task()      — 释放 task_struct（真正死亡）
            └── put_task_struct() — 引用计数归零，释放内存
```

**资源释放顺序**（避免死锁和资源竞争）：

```
释放时序图：
  exit_mm()
     ↓
  exit_files()        — 释放 FD → 可能触发 epoll 清理
     ↓
  exit_fs()
     ↓
  exit_sighand()      — 释放信号处理 → 可能通知其他线程
     ↓
  __exit_signal()     — 更新进程组信息
     ↓
  exit_notify()       — 发送 SIGCHLD 到父进程
     ↓
  schedule()          — 切换出去，不再运行
```

**僵尸进程防范**：
- `SIGCHLD`: 配置 `SA_NOCLDWAIT` → 子进程直接退化为 TASK_DEAD，不经过 ZOMBIE
- `prctl(PR_SET_CHILD_SUBREAPER)`: 设置**子收割器**，替代 init 回收孤儿进程
- systemd 等 init 系统：在 PID 1 中统一 `wait()` 回收

#### 4.1.2 协程生命周期状态

**Go goroutine 状态机**：

```
_Gidle (空闲, 栈缓存)
  └── newproc() → _Grunnable (放入运行队列)
       │
       ├── schedule() → _Grunning (正在执行)
       │    │
       │    ├── gopark() → _Gwaiting (等待事件/锁/IO/chan)
       │    │    └── goready() → _Grunnable
       │    │
       │    ├── entersyscall() → _Gsyscall (阻塞系统调用)
       │    │    └── exitsyscall() → _Grunnable 或 _Grunning
       │    │
       │    └── goexit() → _Gdead (栈可回收)
       │         └── 放入 gFree 链表复用
       │
       └── 抢占（10ms sysmon 信号）
            └── _Grunning → _Grunnable (放回队列)
```

**Python asyncio Task 状态**：

```python
Task 状态枚举 (asyncio.Task):
  PENDING    — 创建后未完成
  CANCELLED  — task.cancel() 触发
  FINISHED   — 正常结束 / 抛出异常

# 协程内部栈状态（调试）:
# coro.cr_running = True/False
# coro.cr_frame — 栈帧（挂起时保留）
# coro.cr_await — 当前等待的 Future
# coro.cr_code — 代码对象
```

#### 4.1.3 任务生命周期框架

以 Kubernetes Job 为例：

```
Job 创建
  ├── Pending — 等待资源（CPU/内存配额检查）
  ├── Running — 至少一个 Pod 在运行
  ├── Succeeded — 所有 Pod 成功退出（exit 0）
  ├── Failed — 达到 backoffLimit 次失败
  └── Unknown — 状态未知（如节点失联）

重启策略 (restartPolicy):
  ├── OnFailure — 失败自动重启（指数退避 10s/20s/40s...上限 6min）
  ├── Always    — 始终重启（DaemonSet/Deployment）
  └── Never     — 不重启（Batch Job）
```

### 4.2 生命周期模式分类

#### 4.2.1 常驻后台（Daemon / Long-Running）

| 模式 | 示例 | 资源特征 |
|:-----|:-----|:---------|
| OS Daemon | sshd, nginx, systemd-journald | fork+setsid() 脱离终端, 无 stdin/stdout, pid 文件 |
| 常驻线程 | GC 线程（Java G1 Concurrent), JIT 编译线程 | 高优先级, 专有栈, 常运行 |
| 监听协程 | Go http.Server goroutine | accept() 循环, 每个连接 spawn 新 goroutine |
| 后台任务 | Erlang 监督者 | 永不退出, 监控子 Actor 健康 |
| OS 级服务 | systemd service (Type=simple/forking) | cgroup 资源限制, 日志重定向 |

**守护进程化流程**（`daemon(3)`）：
```c
pid_t pid = fork();       // ① 分叉
if (pid > 0) exit(0);     // ② 父进程退出
setsid();                 // ③ 创建新 session（脱离控制终端）
chdir("/");               // ④ 切换工作目录
umask(0);                 // ⑤ 重置文件创建掩码
close(0); close(1); close(2);  // ⑥ 关闭标准 fd
open("/dev/null", O_RDWR); dup(0); dup(0);  // 重定向到 /dev/null
```

#### 4.2.2 一次性运行（One-shot / Batch）

| 模式 | 示例 | 生命周期特征 |
|:-----|:-----|:-------------|
| CLI 命令 | `ls`, `grep`, `git commit` | 启动→处理→退出, 通常 < 1s |
| Batch Job | `cron`, Kubernetes Job | 定时触发, 完成后退出 |
| Lambda 函数 | AWS Lambda, Cloud Functions | 冷启动 (~100ms-1s) → 执行 → 冻结/销毁 |
| 单元测试 | `go test`, `pytest` | 测试框架创建→运行→断言→清理 |

**冷启动资源开销对比**：

| 层 | 冷启动时间 | 主要开销来源 |
|:---|:----------|:------------|
| Fork 新进程 | ~10-30μs | copy_process, COW 页表 |
| Docker 容器 | ~200-500ms | 命名空间创建、cgroup 配置 |
| WASM 运行时 | ~1-10ms | 模块实例化、内存初始化 |
| JVM（未预热） | ~100-500ms | 类加载 (~10-100MB)、JIT 编译 |
| AWS Lambda (Java) | ~1-6s | 类加载 + SnapStart 冷启动 |

#### 4.2.3 触发运行（Event-driven / Trigger-based）

| 触发源 | 机制 | 响应实体 | 典型延迟 |
|:-------|:-----|:---------|:--------|
| 硬件中断 | IRQ → ISR → tasklet/softirq | 内核线程/工作队列 | ~1-10μs |
| 信号 | signal_wake_up(pid) | 用户进程/线程 | ~1-10μs |
| I/O 就绪 | epoll_wait() 返回 | 线程/协程 | ~10ns-1μs |
| 定时器 | hrtimer 到期 | 进程/协程回调 | ~1-10μs |
| 消息到达 | channel / mailbox | 协程/Actor | ~10-100ns |
| 文件变更 | inotify/dnotify/fanotify | 进程 | ~ms 级 |
| RPC 请求 | gRPC/HTTP 服务器 | 协程/线程 | ~μs 级 |

**中断响应层次**：

```
硬件中断到达
  │ [1] 中断上下文 (Interrupt Context)
  │     ├── 禁止睡眠, 不可持有锁
  │     ├── 处理紧急硬件确认（如 NIC 接收描述符更新）
  │     └── 记录中断号, 触发软中断 (raise_softirq)
  │
  ├── [2] 软中断 (SoftIRQ)
  │     ├── 仍在中断上下文, 但可被更高优先级中断打断
  │     ├── NET_RX_SOFTIRQ: 网络接收处理
  │     ├── TASKLET_SOFTIRQ: 延迟任务
  │     └── HRTIMER_SOFTIRQ: 高精度定时器
  │
  ├── [3] tasklet / 工作队列 (Workqueue)
  │     ├── tasklet: 软中断中执行（不可阻塞）
  │     └── workqueue: 内核线程中执行（可阻塞）
  │          └── 每个 worker 池有独立线程
  │
  └── [4] 用户态进程/线程
        └── 从系统调用返回, 或信号处理, 或 epoll_wait 返回
```

#### 4.2.4 生命周期模式对比矩阵

| 维度 | 常驻后台 | 一次性 | 触发式 |
|:-----|:---------|:-------|:-------|
| 存活时间 | 无限（系统运行时） | 有限（任务完成） | 有限（事件处理完） |
| 资源占用 | 常驻（预设+运行时） | 短期（峰值可能高） | 间歇（无事件时零占用） |
| 异常处理 | 自动恢复（watchdog/重启） | 失败重试 | 忽略/重试/降级 |
| 适用场景 | 网络服务、代理、监控 | 批处理、编译、测试 | 事件处理、Web 请求 |
| 典型实体 | daemon 进程、GC 线程 | shell 命令、Airflow 节点 | HTTP handler goroutine |
| 恢复策略 | 重启（有损服务） | 重试（幂等保证） | 丢弃（at-most-once） |

---

## 5. 可靠性模型

### 5.1 故障模式分类

#### 5.1.1 故障分类框架（FMEA 角度）

按故障源、影响层级、恢复难度展开：

| 故障模式 | 故障源 | 影响范围 | 恢复难度 | 频次/典型数据 |
|:---------|:-------|:---------|:--------|:--------------|
| 崩溃 (crash/panic) | 非法内存访问, 断言失败 | 进程/线程/协程 | 需外部重启 | ~1/1000-10000h（软件） |
| 死锁 (deadlock) | 锁顺序不一致, 循环等待 | 线程组/进程组 | 需外部强制终止 | ~1/1000-10000h |
| 活锁 (livelock) | 重试循环, 优先级反转 | 线程/进程 | 自动检测难 | ~1/10000h |
| 内存泄漏 | 未释放堆对象 | 进程（RSS 持续增长） | 进程重启 | ~1-10MB/h（典型） |
| FD 泄漏 | 未关闭 fd | 进程（fd 上限 65535） | 进程重启 | ~1-10 个/h(中等复杂服务) |
| 栈溢出 | 递归过深, 栈帧过大 | 线程/协程 | 线程崩溃 | ~1/10000h(防御不当) |
| 竞态条件 | 同步缺失, 时序依赖 | 任意 | 难以稳定复现 | 难以量化 |
| 资源耗尽 | OOM, fd 耗尽, 磁盘满 | 进程/系统 | 全局影响 | 依赖监控阈值 |
| 中断风暴 | 硬件中断过多（如网卡 RX） | 系统（软中断占用 100% CPU） | 硬件降级/驱动更新 | ~ms 级响应延迟 |
| 协程泄漏 | goroutine 卡在 chan 上 | Go 进程（goroutine 数暴增） | 进程重启 | ~1-100 goroutine/h |
| 线程饿死 | 优先级调度不公平 | 特定线程 | 调度策略调整 | CFS 理论上~无 |
| 悬挂 (hung) | 死循环/无响应 | 进程/线程 | watchdog 检测→重启 | ~1/100-1000h |

#### 5.1.2 故障检测机制

| 检测手段 | 检测内容 | 检测延迟 | 误报率 |
|:---------|:---------|:---------|:-------|
| Watchdog (硬件) | CPU 复位/心跳 | ~1.6s (Intel TCO) | 极低 |
| Watchdog (软件) | 进程响应检测 | ~1-30s | 中 |
| OOM Killer | 系统内存不足 | ~10-100ms | 低 |
| Lockdep | 死锁潜在可能性 | 编译时/运行时 | 极低 |
| Go race detector | 竞态条件 | 运行时 | 低 |
| eBPF 监控 | 各种异常行为 | ~μs 级 | 低 |
| Health check | 应用层功能检测 | ~1-60s | 高（依赖实现） |
| 心跳超时 | 节点/进程存活 | ~1-30s | 中 |

#### 5.1.3 故障恢复时间目标（以生产服务为例）

| 故障类型 | 检测时间 | 恢复时间 | RTO 目标 |
|:---------|:---------|:---------|:---------|
| 进程崩溃 | < 1s (systemd) | ~0.5-2s (重启) | < 5s |
| 线程卡死 | ~1-10s (watchdog) | ~1-5s (重启线程组) | < 30s |
| OOM | ~10-100ms (内核通知) | ~1-10s (容器重启) | < 30s |
| 死锁 | ~1-30s (hung_task 检测) | ~1-5s (kill 线程) | < 60s |
| 内存泄漏(DC检测) | ~min-小时级 | ~5-30s (滚动重启) | < 5min |
| 协程泄漏 | ~1-10min (metrics) | ~1-10s (goroutine profile dump) | < 15min |

### 5.2 恢复策略体系

#### 5.2.1 自恢复（Self-Healing）

| 层次 | 机制 | 工作原理 | 适用场景 |
|:-----|:-----|:---------|:---------|
| 硬件 | TCO Watchdog | 芯片内置定时器，溢出触发系统重启 | 系统级无响应 |
| 内核 | hung_task_detector | 检测 D 状态超过 120s 的线程 → 输出告警 | 内核态卡死 |
| 内核 | NMI Watchdog | 通过 NMI 中断检测 CPU 锁死 | 中断关闭/软锁 |
| 内核 | RCU stall detector | 检测 RCU 宽限期超时 | 内核锁死 |
| 应用 | 健康检查 + 重启 | 定时 ping/pong 检测，失败自重启 | 应用层崩溃 |
| Go | runtime/debug.SetPanicOnFault | 捕获非法内存访问转为 panic → recover | goroutine 崩溃不波及进程 |
| Erlang | 监督树 | 子 Actor 崩溃自动重启 | Actor 模型内置容错 |

**Go recover 的协程级自恢复**：

```go
// 每个 goroutine 独立 recover，不影响其他 goroutine
defer func() {
    if r := recover(); r != nil {
        log.Printf("goroutine [%d] recovered: %v", goroutineID(), r)
        // 清理资源、记录错误、重新启动 goroutine
        go safeWork()
    }
}()
```

#### 5.2.2 外部恢复（External Restart）

**进程管理工具对比**：

| 工具 | 重启策略 | 检测机制 | 适用场景 |
|:-----|:---------|:---------|:---------|
| systemd | OnFailure=restart, RestartSec=5s | SIGCHLD（进程退出） | 系统服务 |
| supervisor | autorestart=true, startretries=3 | 子进程状态监听 | Python 应用 |
| Kubernetes | livenessProbe (HTTP/gRPC/exec) | 定期探测 | 容器化应用 |
| Docker | --restart=always/on-failure | 容器退出码 | 容器管理 |
| monit | check process with pidfile | pid 文件 + 端口检测 | 传统服务 |

**systemd Unit 的恢复矩阵**：

```ini
[Service]
Restart=on-failure          # always / on-success / on-failure / on-abnormal / on-abort / on-watchdog
RestartSec=5s               # 重启间隔
StartLimitIntervalSec=60s   # 时间窗口
StartLimitBurst=3           # 时间窗口内最大重启次数
                            # → 超出则不再重启，进入 failed 状态
```

**Kubernetes Pod 重启的级联影响**：

```
Pod crash (exit 1)
  └── kubelet 检测到 Pod 状态 CrashLoopBackOff
       ├── 第 1 次重启: 等待 10s
       ├── 第 2 次重启: 等待 20s
       ├── 第 3 次重启: 等待 40s
       ├── ...
       └── 第 N 次重启: 等待 300s (上限)
            └── 超出 restartPolicy 的 backoffLimit → CrashLoopBackOff 永久
```

#### 5.2.3 Crash-Only 设计

Crash-Only 是一种设计哲学——系统组件被设计为"只有崩溃（crash）和恢复（recover）两种状态"，没有优雅关机的中间状态。

**设计原则**：

| 原则 | 含义 | 违背示例 |
|:-----|:-----|:---------|
| 持久状态可恢复 | 所有持久化数据在重启后仍一致 | 进程内缓存作为唯一存储 |
| 操作幂等 | 重复操作结果相同 | 未实现去重的消息处理 |
| 崩溃仅丢失内存状态 | 不丢失已持久化的数据 | mmap 写入中间状态 |
| 启动时间短 | 重启比优雅关机更快 | 重 10GB 状态到内存 |

**Crash-Only 在 Actor 模型中的体现**：

```erlang
% Erlang 中 Actor 崩溃的处理
% 1. 当前 Actor 立即终止（不尝试清理）
% 2. 监督者收到 {'EXIT', Pid, Reason}
% 3. 监督者决定重启策略（one_for_one/one_for_all/rest_for_one）
supervisor:start_link({local, ?MODULE}, ?MODULE, []).

init([]) ->
    {ok, {{one_for_one, 5, 10},  % 5 次失败/10 秒
          [{worker1,
            {worker_module, start_link, []},
            permanent, 5000, worker, [worker_module]}
          ]}}.
```

#### 5.2.4 不可恢复故障

| 故障类型 | 根因 | 恢复手段 | 说明 |
|:---------|:-----|:---------|:-----|
| Kernel panic | 内核关键错误 | 硬重启 | 触发 kdump 收集 crash dump 后重启 |
| MCE (Machine Check Exception) | CPU/内存硬件错误 | 硬重启 | 某些 MCE 可被 OS 容忍（MCE handler） |
| 物理内存故障 | DIMM CE/UE 错误 | 替换 DIMM | DDR5 SPD + MCA 可以 Page Offline |
| 存储介质损坏 | 磁盘坏道/NAND 块失效 | 替换介质 | 通过 RAID/复制冗余应对 |
| 固件损坏 | BIOS/BMC/CPLD 故障 | 重新烧录 | 双镜像(BMC A/B分区) |
| 电源失效 | PSU 损坏 | 硬件替换 | N+1 冗余配置 |

### 5.3 监督树与容错架构

#### 5.3.1 Erlang OTP 监督树（容错架构典范）

```
supervisor (应用监督者)
  ├── supervisor_A (组监督者)
  │    ├── worker_1 — 实际工作 Actor
  │    ├── worker_2
  │    └── worker_3
  │
  ├── supervisor_B (组监督者)
  │    ├── worker_4
  │    └── worker_5
  │
  └── supervisor_C (数据库连接监督者)
       └── worker_6 (db connection)

重启策略：
  one_for_one: 仅重启崩溃的子进程（隔离性最好）
  one_for_all: 重启所有子进程（一致性要求高）
  rest_for_one: 重启崩溃的及其后启动的所有子进程（依赖排序）
```

**重启频次限制**（`max_restart` / `max_time`）：

```
supervisor 监控重启次数
  ├── 在 max_time 内重启次数超过 max_restart
  │    └── supervisor 自身也崩溃（层级上抛）
  │         └── 直到顶层 supervisor → 整个应用终止
  │
  └── 典型配置：
       {ok, {{one_for_one, 5, 10}, ...}}
       → 10 秒内最多 5 次重启
       → 超过则 supervisor 自身终止
```

#### 5.3.2 熔断与舱壁模式（从进程/线程到服务级别）

**舱壁（Bulkhead）模式** —— 资源隔离的经典实现：

```
┌─────────────────────────┐
│      应用 (进程)          │
│                         │
│  ┌───────┐  ┌───────┐   │
│  │ 线程池A│  │ 线程池B│   │  ← 每个功能模块独立线程池
│  │ (4线程)│  │ (4线程)│   │     一个池耗尽不波及另一池
│  └───────┘  └───────┘   │
│      │           │       │
│  服务 A        服务 B    │
└─────────────────────────┘

实现方式：
  进程级 → 每个服务独立进程（OS 天然隔离）
  线程级 → 独立 ThreadPoolExecutor（Java Hystrix/Resilience4j）
  协程级 → 独立 goroutine pool（ants）
  任务级 → 独立 Task Queue（每个队列绑定独立 worker）
```

**熔断器（Circuit Breaker）状态机**：

```
       ┌──────────────────┐
       │      CLOSED       │  ← 正常状态，请求正常通过
       │  失败计数 < 阈值   │
       └────────┬─────────┘
                │ 失败计数 > 阈值 (如 5s 内 50% 失败)
                ↓
       ┌──────────────────┐
       │      OPEN         │  ← 熔断，请求立即失败
       │  超时窗口等待中    │     不调用下游
       └────────┬─────────┘
                │ 超时窗口到期 (如 30s)
                ↓
       ┌──────────────────┐
       │    HALF_OPEN      │  ← 半开，允许少量请求探测
       │  探测请求检查恢复   │
       └────────┬─────────┘
           成功  │    失败
                │
       CLOSED  ←┘    └→ OPEN
```

#### 5.3.3 进程级故障隔离（Linux cgroup + namespace）

```bash
# systemd 的 cgroup 资源隔离（service 级别）
# 内存限制
MemoryMax=1G
MemoryHigh=800M
MemorySwapMax=0

# CPU 限制
CPUQuota=200%               # 最多 2 个 CPU 核心
CPUAccounting=true
CPUShares=1024

# I/O 限制
IOReadBandwidthMax=/dev/sda 100M
IOWriteBandwidthMax=/dev/sda 50M

# PID 限制
TasksMax=1000               # 最多 1000 个进程/线程
```

**OOM 优先级控制**（`oom_score_adj`）：

| 值 | 含义 | 典型使用 |
|:---|:-----|:---------|
| -1000 | 禁用 OOM Killer | 系统核心服务 (sshd) |
| -500 | 极低概率被 OOM | 数据库进程 |
| 0 | 默认 | 普通进程 |
| +500 | 较高概率被 OOM | 缓存/分析进程 |
| +1000 | 总是先被 OOM | 可丢弃的批处理任务 |

---

## 6. 依赖关系与拓扑

### 6.1 进程关系树

#### 6.1.1 父子进程拓扑

Linux 进程树是一个以 init（PID 1）为根的层级结构：

```
PID 1 (systemd) ──────────────────────────────────────┐
  ├── sshd (PID 100) ── sshd (PID 200) ── bash (PID 201)
  │                                                │
  │                                           user shell
  │                                                │
  │                                         ┌──────┴──────┐
  │                                       ls(202)  vim(203)
  │
  ├── nginx (PID 150, master) 
  │    ├── nginx (PID 151, worker)
  │    ├── nginx (PID 152, worker)
  │    └── nginx (PID 153, worker)
  │
  ├── postgres (PID 200, postmaster)
  │    ├── postgres (PID 201, checkpointer)
  │    ├── postgres (PID 202, walwriter)
  │    ├── postgres (PID 203, autovacuum)
  │    └── postgres (PID 204, stats collector)
  │
  └── docker (PID 500, containerd)
       └── containerd-shim → container process
```

**进程组与 Session**：

```
Session (会话)
  └── 控制终端 (kernel 跟踪)
       └── foreground process group (前台进程组)
            ├── bash (PID 201, group leader)
            └── ls (PID 202, 在前台运行)
       └── background process group (后台进程组)
            └── sleep 100 & (PID 300, 后台)

> 信号传播规则（由终端发出的信号）：
>   Ctrl+C (SIGINT) → 发送给前台进程组的所有进程
>   Ctrl+Z (SIGTSTP) → 暂停前台进程组
>   Ctrl+\ (SIGQUIT) → 发送给前台进程组的所有进程（+core dump）
```

**孤儿进程与子收割器**：

```
场景：父进程先于子进程退出
  ┌────────────┐         ┌────────────┐
  │ 父进程 (退出)│         │  init/systemd │
  │ children ◄─── orphan →│  作为新父进程   │
  └────────────┘         └────────────┘
       │
  ┌────────────┐
  │ 子进程      │
  │ real_parent │──→ systemd (PID 1)
  └────────────┘

关键：
  systemd 在信号处理循环中 wait()（SIGCHLD handler）
  子进程退出后不会变成僵尸（init 自动回收）
  可以设置 subreaper（prctl(PR_SET_CHILD_SUBREAPER)）
  使中间进程成为子收割器，不依赖 init
```

#### 6.1.2 进程拓扑的调试视角

```
# pstree 显示进程树
systemd─┬─accounts-daemon───2*[{accounts-daemon}]
        ├─acpid
        ├─cron
        ├─dbus-daemon
        ├─dockerd───containerd───6*[{containerd}]
        │           └─9*[{dockerd}]
        ├─sshd───sshd───bash───pstree
        └─systemd-journald
```

### 6.2 线程关系图

#### 6.2.1 线程组拓扑

在 Linux 中，线程通过 `tgid` (thread group ID) 来标识所属的进程（线程组）：

```
线程组 (TGID=1234) ──── 进程名: myserver
  ├── tgid=1234, pid=1234 (主线程, group_leader)
  │    └── 处理信号、接收子进程
  │
  ├── tgid=1234, pid=1235 (worker thread 1)
  │    └── CFS 调度实体, 独立栈 (8MB)
  │
  ├── tgid=1234, pid=1236 (worker thread 2)
  ├── tgid=1234, pid=1237 (I/O poller thread)
  │    └── epoll_wait() 循环, 处理网络事件
  │
  └── tgid=1234, pid=1238 (GC thread)
       └── 高优先级 RT 调度 (占用特定 CPU)

# 内核视角：tgid 用于信号分发，pid 用于调度
# getpid() = tgid（线程组 ID）
# gettid() = pid（唯一线程 ID）
```

**线程组内协作关系**：

```
Worker Thread 1 ──→ shared task queue ←── Worker Thread 2
     │                                         │
     │    ┌── mutex_lock / unlock ──┐          │
     │    │    条件变量 pthread_cond  │          │
     │    └── read/write lock ──────┘          │
     │                                         │
     └── 共享数据结构 (链表/哈希表/堆) ←─────────┘
     
可观测性：
  /proc/[tgid]/task/[pid]/  — 每个线程独立条目
  /proc/[tgid]/status:      — 线程组汇总信息
    Threads: 5              — 线程组内线程数
    SigQ: 0/32768           — 信号队列
```

#### 6.2.2 线程池拓扑模型

**固定大小线程池的经典模型**：

```
FixedThreadPool(n=8)
  ┌─────────────────────────────────────────────────┐
  │               任务队列 (BlockingQueue)            │
  │  [T1]→[T2]→[T3]→[...]→[T100]                   │
  │  容量：Integer.MAX_VALUE（无界队列）或 有界队列    │
  └──────────────────┬──────────────────────────────┘
                     │ 任务分发
         ┌───────────┼───────────┐
         ↓           ↓           ↓
     ┌───────┐  ┌───────┐  ┌───────┐
     │Worker1│  │Worker2│  │Worker8│...
     │n=1    │  │n=2    │  │n=8    │
     └───────┘  └───────┘  └───────┘
         │           │           │
         └─────── 共享堆 ────────┘
```

**工作窃取线程池（ForkJoinPool）拓扑**：

```
ForkJoinPool (parallelism=8)
  ├── Worker_1 (Thread)
  │    ├── local queue [T1]→[T2]→[T3] (deque, LIFO)
  │    ├── 优先处理本地队列尾部（缓存友好）
  │    └── 本地队列空时：从其他 Worker 窃取头部
  │
  ├── Worker_2 (Thread)
  │    ├── local queue [T4]→[T5]
  │    └── 从 Worker_1 窃取 T1（头部，最大化并行度）
  │
  └── SharedSubmissionQueue (全局提交队列)
       └── 外部提交的任务放入此队列
```

### 6.3 协程调度拓扑

#### 6.3.1 Go goroutine 调度拓扑

```
Go 程序 (GOMAXPROCS=4)
  │
  ├── P0 (绑定到 CPU 0)
  │    ├── M0 (OS 线程 tid=1234)
  │    │    ├── g1 (main goroutine, 正在运行)
  │    │    └── g2, g3 (本地队列)
  │    │
  │    ├── 网络轮询器 (netpoller)
  │    │    └── 管理 socket fd → epoll_wait()
  │    │
  │    └── 定时器堆
  │         └── g4 (time.After(5s) → 到期加入本地队列)
  │
  ├── P1 (绑定到 CPU 1)
  │    ├── M1 (OS 线程 tid=1235)
  │    ├── g5, g6 (本地队列)
  │    └── 从 P2 窃取 goroutine (work-stealing)
  │
  ├── P2 (绑定到 CPU 2)
  │    ├── M2 (OS 线程 — 正在执行 syscall)
  │    │    └── g7 (调用阻塞系统调用)
  │    │
  │    └── 处理系统调用返回 (exitsyscall → 重新绑定 M)
  │
  ├── P3 (绑定到 CPU 3)
  │    ├── M3 (OS 线程 tid=1236)
  │    └── 执行 GC mark 阶段
  │
  ├── 全局运行队列
  │    └── g_global (本地队列满时放入全局队列)
  │
  ├── sysmon (监控线程)
  │    └── 每 10ms 检查是否需抢占/GC 触发/网络轮询
  │
  └── GC worker goroutines
       └── 并发标记/清扫
```

**Goroutine 泄漏的拓扑特征**：

```go
// 泄漏模式 1：channel 未关闭
func leak() {
    ch := make(chan int)
    go func() {
        <-ch  // 永远阻塞 → goroutine 泄漏
    }()
    // ch 从未被写入，goroutine 永远不退出
}

// 泄漏模式 2：定时器未停止
func leak2() <-chan int {
    ch := make(chan int)
    time.AfterFunc(time.Hour, func() {
        ch <- 1  // 1 小时后才写入（如果没人读也泄漏）
    })
    return ch  // caller 可能不读
}
```

#### 6.3.2 Rust async 调度拓扑

```
Tokio Runtime (worker_threads=4)
  │
  ├── Worker_0 (OS 线程)
  │    ├── local: LIFO slot (当前执行任务)
  │    └── epoll (I/O 驱动) 
  │
  ├── Worker_1 (OS 线程)
  │    ├── local: LIFO slot
  │    ├── 从 Worker_2 窃取 (steal)
  │    └── injected (全局队列到本地)
  │
  ├── Worker_2 (OS 线程)
  │    ├── local: 任务阻塞在 I/O
  │    └── 等待 I/O 完成
  │
  ├── Worker_3 (OS 线程)
  │    └── 空闲 (park)
  │
  └── Global Inject Queue
       └── 新任务（来自外部 spawn）首先进入全局队列
```

### 6.4 任务依赖 DAG

#### 6.4.1 DAG 调度拓扑

```
多阶段数据处理管线 DAG：

Phase 1: Data Ingest ──→ [task_1] ──→ Raw Data Storage
Phase 2: Preprocessing
           ┌── [task_2a (clean)] ──┐
[raw] ────→┤                       ├──→ [clean store]
           └── [task_2b (validate)] ┘
Phase 3: Feature Engineering
           ┌── [task_3a (extract)] ──┐
[clean] ──→┤                         ├──→ [features store]
           └── [task_3b (normalize)] ┘
Phase 4: Train / Evaluate
[features] ──→ [task_4a (train)] ──→ model.pkl
           └→ [task_4b (eval)] ──→ metrics.json

Phase 5: Report
[train] + [eval] ──→ [task_5 (report)] ──→ report.html
```

**DAG 调度器核心资源管理**：

| 资源维度 | Airflow | Prefect | Ray DAG | 自研调度器 |
|:---------|:--------|:--------|:--------|:----------|
| 任务粒度 | 进程 | 进程/线程 | Actor/Task | 自定义 |
| 资源声明 | pool/slot | CPU/Memory | num_cpus/num_gpus | cgroup |
| 并发控制 | pool 大小 | concurrency_limit | 自动资源调度 | 信号量 |
| 依赖执行 | 拓扑排序 | 异步 DAG | Remote 调用 | 拓扑排序 |
| 失败重试 | task retry | retry_delay | max_retries | 指数退避 |

---

## 7. 调试与可观测性

### 7.1 系统级调试接口

#### 7.1.1 ptrace 体系

ptrace 是 Linux 上最底层的调试机制，提供进程级注入观测能力：

```c
// ptrace 核心请求
ptrace(PTRACE_ATTACH, pid, NULL, NULL);  // 附加到进程
// → 目标进程收到 SIGSTOP（处于 TASK_TRACED 状态）
// → 追踪者可以检查/修改被追踪进程的所有资源

ptrace(PTRACE_SYSCALL, pid, NULL, NULL); // 跟踪所有系统调用
// → 在系统调用进入和退出时停止
// → seccomp 模式下性能更好

ptrace(PTRACE_PEEKDATA, pid, addr, NULL); // 读内存
ptrace(PTRACE_POKEDATA, pid, addr, data); // 写内存
ptrace(PTRACE_GETREGS, pid, NULL, &regs); // 读寄存器
ptrace(PTRACE_SETREGS, pid, NULL, &regs); // 写寄存器
ptrace(PTRACE_CONT, pid, NULL, sig);      // 继续执行
```

**ptrace 的限制**：

| 限制 | 说明 | 影响 |
|:-----|:-----|:-----|
| 每进程单追踪者 | 一个进程只能被一个追踪者 attach | 调试器 vs profiler 冲突 |
| 性能开销 | 每个系统调用产生 2 次上下文切换 | strace 下延迟 ~10-100× |
| 安全限制 | YAMA LSM (`ptrace_scope`) | 默认仅父进程可 ptrace 子进程 |
| 无法 attach 内核线程 | 内核线程无 mm 结构 | 不能调试内核线程 |
| 子进程跟踪 | PTRACE_O_TRACECLONE 等 | 需要显式设置 |

**ptrace 的安全限制演变**：
```
Linux < 3.4: 默认允许 ptrace 跨进程（无限制）
Linux 3.4: 引入 YAMA LSM（ptrace_scope=1）
  0: 经典模式（任何进程可 ptrace 任何同级进程）
  1: 受限模式（仅父进程可 ptrace 子进程）—— 默认
  2: 管理员模式（仅 CAP_SYS_PTRACE 可用）
  3: 不可附加（禁止 ptrace，需重启才能改回）
```

#### 7.1.2 eBPF 动态追踪

eBPF 是 Linux 3.18+ 引入的革命性可观测框架：

```
用户态 (控制面)
  bpftrace/bcc/libbpf
    │
    ↓ (bpf() 系统调用)
内核 (验证 + 执行)
  eBPF verifier (验证器)
    ├── 检查循环（必须有界）
    ├── 检查指针安全
    ├── 检查栈大小（≤512 字节）
    └── 检查辅助函数合法性
    │
    ↓ (JIT 编译为原生代码)
  eBPF program (注入到内核/用户态探针)
    ├── kprobe  ──→ 内核函数入口/出口
    ├── tracepoint ──→ 内核静态插桩点
    ├── uprobe   ──→ 用户态函数入口/出口（进程级）
    ├── USDT     ──→ 用户态静态插桩点（需编译时嵌入）
    ├── perf_event ──→ PMC/硬件计数器
    ├── fentry/fexit ──→ 内核函数入口/出口（更轻量，5.5+）
    └── BPF iterator ──→ 遍历内核数据结构（5.8+）
```

**各实体的 eBPF 可观测性**：

| 实体 | 观测点 | 典型工具 | 信息 |
|:-----|:-------|:---------|:-----|
| 进程创建/退出 | tracepoint:sched_process_fork/exit | execsnoop, exit_snoop | 进程名、PID、退出码 |
| 线程创建/退出 | tracepoint:sched_process_fork/exit | threadsnoop | TID、TGID |
| 线程调度 | tracepoint:sched_switch | runqlat, runqslower | 调度延迟、切换次数 |
| 进程状态切换 | tracepoint:sched_process_waking | wakelat | 唤醒延迟 |
| 系统调用 | tracepoint:syscalls:sys_enter_* | strace (eBPF 模式) | syscall 参数/返回值 |
| 内存分配 | kprobe:mm_page_alloc | oomkill, memleak | 分配大小、调用栈 |
| 信号发送 | tracepoint:signal_generate | killsnoop | 信号号、目标 PID |
| 文件操作 | tracepoint:syscalls:sys_enter_openat | filetop, fileslower | 文件名、延迟 |
| I/O 操作 | tracepoint:block:block_rq_issue | biolatency, biosnoop | I/O 延迟、大小 |

**实用 eBPF 脚本示例（bpftrace）**：

```bpftrace
// 追踪所有进程的线程创建/退出
tracepoint:sched:sched_process_fork
{
    printf("FORK: parent=%d(%s) child=%d\n", 
           args->parent_pid, args->parent_comm, args->child_pid);
}

tracepoint:sched:sched_process_exit
{
    $sig = args->sig_nr != 0 ? "signal" : "exit";
    printf("EXIT: pid=%d(%s) reason=%s code=%d\n",
           pid, comm, $sig, args->exit_code);
}

// 追踪某进程的上下文切换次数（调度抖动检测）
tracepoint:sched:sched_switch
/pid == $1/
{
    @switches[comm] = count();
}

// 定时器延迟（hrtimer 精度监测）
tracepoint:timer:hrtimer_expire_entry
{
    @latency = hist(nsecs - args->now);
}
```

**eBPF 的资源占用对比**：

| 观测方法 | 延迟开销（每事件） | 内存占用 | 部署要求 |
|:---------|:------------------|:---------|:---------|
| ptrace/strace | ~10-100μs | 低 | 任意 Linux |
| eBPF kprobe | ~0.1-1μs | 低（maps） | Linux 4.9+ (BPF) |
| eBPF tracepoint | ~0.1-1μs | 低 | Linux 4.7+ |
| eBPF fentry/fexit | ~0.05-0.5μs | 低 | Linux 5.5+ |
| perf record | ~ns 级（硬件采样） | 中等（perf.data） | 任意 |
| systemtap | ~1-10μs | 高（模块） | 需安装 debuginfo |

#### 7.1.3 /proc 文件系统

`/proc` 是进程资源观测的核心接口，每个进程对应一个目录：

```
/proc/[pid]/
  ├── cmdline      — 命令行参数（\\0 分隔）
  ├── comm         — 进程名称
  ├── cwd          — 符号链接 → 当前工作目录
  ├── environ      — 环境变量（\\0 分隔）
  ├── exe          — 符号链接 → 可执行文件
  ├── fd/          — 文件描述符目录
  │    ├── 0 → /dev/pts/0 (stdin)
  │    ├── 1 → /dev/pts/0 (stdout)
  │    ├── 2 → /dev/pts/0 (stderr)
  │    ├── 3 → socket:[12345]
  │    └── 4 → /var/log/app.log
  │
  ├── maps         — 内存映射（虚拟地址→文件/匿名）
  ├── mem          — 进程内存（通过 lseek 读取）
  ├── smaps        — 每段内存的详细统计（RSS/PSS/Swap...）
  ├── status       — 进程状态摘要
  │    ├── Name: nginx
  │    ├── State: S (sleeping)
  │    ├── Tgid: 1234
  │    ├── Pid: 1234
  │    ├── PPid: 1
  │    ├── TracerPid: 0         ← 0=未跟踪, >0=正在被调试
  │    ├── Uid: 0 0 0 0
  │    ├── VmSize: 1024000 kB
  │    ├── VmRSS: 256000 kB
  │    ├── Threads: 12
  │    ├── SigQ: 0/32768
  │    └── voluntary_ctxt_switches: 1024
  │        involuntary_ctxt_switches: 32  ← 非自愿切换（高值=调度争用）
  │
  ├── task/        — 每个线程的子目录
  │    ├── 1234/   — 主线程
  │    │    └── status (State, VmRSS 等线程级统计)
  │    ├── 1235/   — 工作线程
  │    └── 1236/   — 工作线程
  │
  ├── stack        — 内核栈回溯（需 CONFIG_STACKTRACE）
  ├── syscall      — 当前系统调用（无系统调用则显示 -1）
  ├── wchan        — 等待通道（如果进程在睡眠）
  └── cgroup       — cgroup 层次（cgroup v2 时显示资源限制）

/proc/[pid]/fdinfo/  — 每 fd 的详细统计
  └── 3: pos: 0, flags: 0100002, mnt_id: 25
```

### 7.2 运行时级调试接口

#### 7.2.1 Go 运行时调试

**pprof 采样**（Go 1.x+ 内置）：

```go
import _ "net/http/pprof"

// 访问 /debug/pprof/ 获取采样数据

// 采样类型：
//     profile?seconds=30  — CPU 采样（30s）
//     heap                — 堆内存分配（当前存活）
//     goroutine?debug=2   — 所有 goroutine 的栈回溯
//     threadcreate        — OS 线程创建
//     block               — 同步原语阻塞分析
//     mutex               — 互斥锁竞争分析（需 runtime.SetMutexProfileFraction）
//     trace?seconds=5     — 执行追踪（5s）

// 命令行工具：
//   go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30
//   > top10         — 采样次数 Top 10 函数
//   > web           — 火焰图
//   > list funcName — 某函数在采样中的比例

// 生成火焰图：
//   go tool pprof -http=:8080 profile.out
```

**Goroutine 堆栈分析**（处理 goroutine 泄漏）：

```
goroutine profile: total 14567  ← goroutine 总数（正常 ~100-1000）

14546 @ 0x43fda3 0x44a0ca 0x44a0c7 0x44a0f5 0x44bc74 0x4661ff 0x466270
#	14546 个 goroutine 在同一个等待点 ← 这是泄漏
#	0x44bc74  runtime.gopark+0x64
#	0x4661ff  runtime.chanrecv+0x3cf
#	0x466270  runtime.chanrecv1+0x40
#	0x44ea07  main.leakFunc.func1+0x47
#		main.go:22  ← 泄漏源定位到第 22 行

1 @ 0x43fda3 0x44a0ca 0x44a0c7 0x44bbea 0x46ac10 0x46a9b1 0x46acf1 0x46d421 0x4a85c1
#	1 个 goroutine 在 time.Sleep (不应视为泄漏)
```

**Go 执行追踪**（`go tool trace`）：

```
trace 文件可以分析：
  ├── goroutine 创建/退出/阻塞/就绪事件
  ├── 调度器决策（何时调度哪个 goroutine）
  ├── 网络轮询事件（epoll 触发）
  ├── 系统调用进入/退出
  ├── GC 阶段（标记、清扫、STW 时长）
  ├── 内存分配统计
  └── 协程间通信（channel send/recv）

关键指标：
  ├── Scheduling latency — goroutine 从就绪到运行的时间
  ├── Network blocking — 网络 I/O 等待时间占比
  ├── Syscall blocking — 系统调用等待时间占比
  └── GC pause — STW 时长（目标 < 100μs/次）
```

#### 7.2.2 JVM 线程调试

**jstack**（线程堆栈快照）：

```bash
# 获取所有线程的栈回溯
jstack <pid>

# 输出中的线程状态解读：
"http-nio-8080-exec-1" #14 daemon prio=5 os_prio=0 cpu=123.00ms elapsed=300.42s tid=0x00007f nid=0x3a3c runnable  [0x00007f...]
   java.lang.Thread.State: RUNNABLE
    at sun.nio.ch.EPoll.wait(Native Method)
    at sun.nio.ch.EPollSelectorImpl.doSelect(EPollSelectorImpl.java:120)
    at sun.nio.ch.SelectorImpl.lockAndDoSelect(SelectorImpl.java:124)
    - locked <0x00000000c0063298> (a sun.nio.ch.Util$2)  ← 持有的锁
    at sun.nio.ch.SelectorImpl.select(SelectorImpl.java:141)
    at org.apache.tomcat.util.net.NioEndpoint$Poller.run(NioEndpoint.java:771)

"GC Thread#0" os_prio=0 cpu=0.18ms elapsed=300.42s tid=0x00007f nid=0x3a30 runnable  

"VM Thread" os_prio=0 cpu=0.24ms elapsed=300.42s tid=0x00007f nid=0x3a32 runnable
```

**jcmd**（综合诊断工具）：

```bash
# JVM 内部诊断
jcmd <pid> Thread.print           # 线程栈（同 jstack）
jcmd <pid> GC.heap_dump heap.dump # 堆转储
jcmd <pid> VM.native_memory       # 本地内存分配
jcmd <pid> VM.uptime              # JVM 运行时间
jcmd <pid> PerfCounter.print      # 性能计数器
jcmd <pid> VM.flags               # JVM 参数

# Virtual Thread 特定诊断（JDK 21+）
jcmd <pid> Thread.vthread_stacks  # 所有虚拟线程的栈

# 对于虚拟线程：
# 普通 jstack 只能看到 carrier 线程
# vthread_stacks 显示所有 VT 的状态
```

#### 7.2.3 Python 调试

```python
import sys
import traceback
import faulthandler

# 启用崩溃时自动 dump 所有线程栈
faulthandler.enable()
faulthandler.dump_traceback_later(30)  # 30 秒后 dump

# 当前所有线程的栈
for thread_id, stack in sys._current_frames().items():
    print(f"Thread {thread_id}:")
    traceback.print_stack(stack)

# asyncio 协程栈（需 task 仍存活）
import asyncio
task = asyncio.current_task()
if task:
    task.print_stack()  # 打印当前协程的栈
    # 或获取协程的帧:
    frame = task.get_stack()
    traceback.print_stack(frame[0])
```

### 7.3 注入与干预技术

#### 7.3.1 信号注入（最直接的进程级干预）

```bash
# 向进程注入信号
kill -SIGTERM <pid>       # 正常终止
kill -SIGKILL <pid>       # 强制终止（不可捕获/忽略）
kill -SIGSTOP <pid>       # 暂停进程
kill -SIGCONT <pid>       # 继续执行
kill -SIGUSR1 <pid>       # 用户自定义信号（重新加载配置）
kill -SIGABRT <pid>       # 触发 core dump（必须启用 ulimit -c）

# 向特定线程注入信号
# pthread_kill(tid, SIGUSR1)  — 在 C 代码中
# kill -SIGUSR1 发送到线程组，由具体线程处理

# 信号触发 core dump：
#    ulimit -c unlimited
#    kill -SIGSEGV <pid>  — 模拟段错误取 core dump
#    kill -SIGABRT <pid>  — 另一个常用 trigger
```

#### 7.3.2 eBPF 注入

```bpftrace
// 注入：拦截 open 系统调用，修改参数
// 将敏感文件重定向到安全路径
tracepoint:syscalls:sys_enter_openat
/str(args->filename) == "/etc/shadow"/
{
    override_str(args->filename, "/dev/null");
}

// 注入：动态修改函数返回值（bpf_override_return）
// 使特定系统调用返回错误码（测试错误路径）
kprobe:do_sys_open
/pid == $1/
{
    if (str(arg1) == "/forbidden") {
        bpf_override_return(reg("bp"), -EPERM);
    }
}
```

#### 7.3.3 GDB 动态附加

```bash
# 附加到运行中的进程
gdb -p <pid>

# 注入断点
(gdb) break function_name
(gdb) break *0x7f1234567890  # 地址断点
(gdb) watch var               # 数据断点（变量变化时中断）

# 运行时修改
(gdb) set variable x = 42
(gdb) call some_function()
(gdb) set {int}0xdeadbeef = 0  # 直接写内存

# 多线程调试
(gdb) info threads              # 列出所有线程
(gdb) thread 2                  # 切换到线程 2
(gdb) thread apply all bt       # 所有线程的栈回溯

# 协程调试（Go 运行时）
(gdb) source /usr/lib/go/src/runtime/runtime-gdb.py
(gdb) info goroutines           # 列出所有 goroutine
(gdb) goroutine 2 bt            # goroutine 2 的栈回溯
(gdb) goroutine 2 set var = 42  # 修改 goroutine 2 的变量
```

#### 7.3.4 混沌工程注入（破坏性测试）

```go
// Go 实现的故障注入工具（如 chaos-mesh）

// 1. Pod 删除
// 2. 网络延迟注入（eBPF，对特定连接加入延迟）
tc qdisc add dev eth0 root netem delay 100ms 10ms 25%

// 3. 进程/线程 kill
// 4. CPU 压力注入
// 5. 内存压力注入
// 6. I/O 延迟/错误注入

// 故障注入的目标：
//   验证系统在以下场景的可靠性：
//     - 进程崩溃 → systemd 重启
//     - 线程卡死 → watchdog 检测/恢复
//     - 协程泄漏 → 监控告警/自动扩缩容
//     - 任务超时 → 降级/熔断
```

### 7.4 内部可观测性机制

#### 7.4.1 进程级可观测性

**调度延迟统计**：
```bash
# /proc/<pid>/sched 中的调度统计
nr_switches: 123456            # 上下文切换总次数
nr_voluntary_switches: 100000  # 主动切换（等待 I/O/锁/定时器）
nr_involuntary_switches: 23456 # 被动切换（时间片耗尽/抢占）
# involuntary 比例高 = CPU 争用严重

se.statistics:
  wait_sum: 12345ms            # 总等待时间
  wait_count: 100000           # 等待次数
  wait_max: 500ms              # 最大单次等待
  # 平均等待时间 = wait_sum / wait_count

  # 负载追踪（PELT, Per-Entity Load Tracking）
  load_sum: 1024               # 负载总和
  util_sum: 512                # 利用率（与实际运行时间相关）
  util_avg: 256                # 平均利用率（0-1024 范围）

  # 迁移统计
  nr_migrations: 50            # 跨 CPU 迁移次数
  # 高迁移率 = 缓存效率差
```

**内存观测**：
```bash
# /proc/<pid>/smaps 的扩展信息（每内存段）
7f1234000000-7f1236000000 rw-p 00000000 00:00 0     [heap]
Size:                32768 kB   # VMA 大小（虚拟地址范围）
KernelPageSize:        4 kB     # 内核页大小
MMUPageSize:           4 kB     # MMU 页大小
Rss:               20480 kB     # 驻留内存（物理页）
Pss:               10240 kB     # 按比例共享大小（多个进程共享时除以共享数）
Shared_Clean:       8192 kB     # 共享干净页（可被回收）
Shared_Dirty:       2048 kB     # 共享脏页（如 COW 前）
Private_Clean:          0 kB    # 私有干净页
Private_Dirty:     10240 kB     # 私有脏页（如栈、堆修改）
Referenced:         5120 kB     # 最近被引用的页
Anonymous:         12288 kB     # 匿名页（堆、栈、mmap）
AnonHugePages:          0 kB    # 透明大页（THP）
Swap:                   0 kB     # 已换出的页
KernelPageSize:        4 kB     # 内核页大小
MMUPageSize:           4 kB     # MMU 页大小
Locked:                 0 kB     # mlock 锁定的页
THPeligible:            0        # 该 VMA 是否有资格使用 THP

# 关键指标：
#   RSS - 实际物理内存占用
#   PSS - 考虑共享的物理内存（更准确）
#   Private_Dirty - 进程独有的脏内存（最真实的"独占"内存）
#   Swap - 已交换到磁盘的内存量
```

#### 7.4.2 线程级可观测性

```bash
# /proc/<pid>/task/<tid>/status 中的线程级统计
Name:   worker-1
State:  S (sleeping)            # 线程当前状态
Tgid:   1234                    # 线程组 ID
Pid:    1235                    # 线程 ID
PPid:   1234                    # 父线程（实际是主线程）
TracerPid:      0               # 调试器 PID（0=未跟踪）
Uid:    1000    1000    1000    1000
Gid:    1000    1000    1000    1000
VmPeak:    4194304 kB           # 虚拟地址峰值
VmSize:    4194304 kB           # 当前虚拟地址大小→所有线程相等
VmLck:         0 kB
VmPin:         0 kB
VmHWM:      20480 kB            # 峰值 RSS（该线程的贡献）
VmRSS:      10240 kB
RssAnon:     8192 kB            # 该线程的匿名 RSS
RssFile:     2048 kB            # 该线程的文件映射 RSS
RssShmem:       0 kB
VmData:     4096 kB
VmStk:         132 kB           # 线程栈已使用的物理内存（非虚拟）
VmExe:         4 kB
VmLib:         0 kB
VmPTE:        16 kB             # 页表大小
Threads:        12              # 所属线程组线程数
SigQ:   0/32768                 # 信号队列 / 上限
Cpufrt:         0               # 实时 CPU 时间
```

#### 7.4.3 cgroup 资源统计

```bash
# cgroup v2 — 资源使用统计
/sys/fs/cgroup/system.slice/myserver.service/

# CPU 统计
cpu.stat:
  usage_usec: 1234567890       # 总 CPU 时间（μs）
  user_usec: 1000000000        # 用户态 CPU 时间
  system_usec: 234567890       # 内核态 CPU 时间
  nr_periods: 1000             # 时间周期数（cfq_quantum）
  nr_throttled: 5              # 被节流的周期数
  throttled_usec: 50000        # 被节流的时间（μs）

# 内存统计
memory.current: 2147483648      # 当前内存使用量 (2GB)
memory.min: 1073741824           # 硬保证下限 (1GB)
memory.low: 2147483648           # 尽力保证下限 (2GB)
memory.high: 4294967296          # 软限制上限 (4GB)
memory.max: 8589934592           # 硬限制上限 (8GB)

memory.stat:
  anon: 1073741824              # 匿名页（堆/栈）
  file: 1073741824              # 文件页（代码/文件映射）
  kernel_stack: 4194304         # 内核栈
  slab: 52428800                # slab 分配器（dentry/inode 缓存）
  sock: 2097152                 # socket 内存
  shmem: 0                      # tmpfs
  pgfault: 100000               # 缺页（硬缺页+软缺页）
  pgmajfault: 100              # 硬缺页（需磁盘 I/O）
  workingset_refault: 500       # workingset 再缺页
  oom: 0                        # OOM killer 触发次数

# I/O 统计
io.stat:
  8:0 rbytes=1073741824         # 读取字节（设备 8:0 = sda）
  8:0 wbytes=536870912          # 写入字节
  8:0 rios=10000                # 读取次数
  8:0 wios=5000                 # 写入次数
  8:0 dbytes=0
  8:0 dios=0
```

#### 7.4.4 协程级可观测性

**Go runtime 内置统计**：

```go
// 通过 runtime.ReadMemStats() 获取
type MemStats struct {
    // 协程统计
    NumGoroutine    int32    // 当前活跃 goroutine 数
    // 栈统计
    StackInuse      uint64   // 栈使用的字节数
    StackSys        uint64   // 栈分配的字节数
    // 堆统计
    HeapAlloc       uint64   // 堆分配字节（当前存活）
    HeapSys         uint64   // 堆从系统获得的总字节
    HeapIdle        uint64   // 空闲堆（未使用但未归还 OS）
    HeapInuse       uint64   // 正在使用的堆
    // GC 统计
    NumGC           uint32   // GC 完成次数
    LastGC          uint64   // 上次 GC 完成时间戳
    PauseTotalNs    uint64   // 所有 GC STW 总时间
    PauseNs         [256]uint64  // 最近 256 次 GC 的 STW 时间
    GCCPUFraction   float64  // GC 占 CPU 的比例
    // 系统
    Sys             uint64   // 从系统获得的总字节数
    Frees           uint64   // 释放的对象总数
    Lookups         uint64   // 指针查找（runtime 内部）
    Mallocs         uint64   // 分配的对象总数
    NextGC          uint64   // 下次 GC 的目标堆大小
}
```

**Go 运行时指标暴露**（通过 `expvar` 或 Prometheus）：

```go
// 标准 HTTP 指标暴露
import "runtime/metrics"

// Go 1.16+ 提供了稳定的 /metrics 接口
// 关键指标：
//   /gc/gomemlimit:bytes
//   /gc/stack/starting:size
//   /sched/goroutines:goroutines
//   /sched/latencies:seconds
//   /sched/pauses:stopping/gc:seconds
//   /memory/classes/heap/free:bytes
//   /memory/classes/total:bytes
```

#### 7.4.5 任务级可观测性

**OpenTelemetry 追踪**（跨实体追踪的标准化方案）：

```
Trace:
  ├── Span 1: "HTTP GET /api/data"
  │    ├── 进程: app-server (PID=1234)
  │    ├── 线程: http-worker-3 (TID=1237)
  │    └── 资源: {"http.method": "GET", "http.status_code": 200}
  │
  ├── Span 2: "SQL Query"
  │    ├── 进程: database (PID=2345)
  │    ├── 协程: goroutine-42
  │    └── 资源: {"db.system": "postgresql", "db.statement": "SELECT ..."}
  │
  └── Span 3: "Cache Lookup"
       └── 任务: RedisActor
            └── 资源: {"cache.hit": true, "cache.latency": "1.2ms"}
```

**资源关联（Resource Correlation）**：

```yaml
# 将 OS 资源与业务任务关联
alerts:
  - metric: process_cpu_usage > 80%
    correlate:
      - goroutine_count
      - task_queue_depth
      - gc_pause_seconds
    action: |
      if (task_queue_depth > 1000 -> scale up worker)
      if (gc_pause > 100ms -> increase GOGC)
      if (goroutine_leak -> dump profile -> analyze which wait point)
```

---

## 8. 跨层对比矩阵

### 8.1 综合维度对比

| 维度 | 进程 | 线程 | 协程 | 任务 |
|:-----|:-----|:-----|:-----|:-----|
| **OS 抽象** | 独立地址空间 + PID | 共享地址空间 + TID | 无 OS 概念 | 框架级抽象 |
| **调度者** | OS 内核 CFS | OS 内核 CFS | 运行时调度器 | 框架调度器 |
| **调度策略** | 抢占式（时间片） | 抢占式（时间片） | 协作式（.await/yield） | 轮询/优先级/DAG |
| **栈管理** | 固定大小(8MB) | 固定大小(2MB) | 动态(2KB→~1GB) | 框架定义 |
| **栈切换** | CR3+TLB 刷新 | 寄存器保存恢复 | 寄存器+sp 恢复 | 任务上下文切换 |
| **切换时机** | 时间片/阻塞/主动 | 时间片/阻塞/主动 | await/yield/阻塞 | 完成/失败/超时 |
| **切换延迟** | ~1-10μs | ~0.1-1μs | ~10-30ns | ~μs-ms |
| **每实体内存** | ~8MB+ | ~2MB+ | ~4KB | ~KB-MB |
| **最大数量** | ~10⁴ | ~10⁴ | ~10⁶-10⁷ | 取决于框架 |
| **隔离性** | 强（独立地址空间） | 弱（共享地址空间） | 弱（共享） | 框架决定 |
| **通信方式** | IPC（pipe/socket/shm） | 共享内存+锁 | channel/共享内存 | 消息队列/远程调用 |
| **并行能力** | 全（多核） | 全（多核） | 需绑定 OS 线程 | 依赖底层执行器 |
| **创建开销** | ~10-30μs | ~50-200μs | ~0.1-0.5μs | ~ms 级 |
| **可观测性** | /proc, ptrace, eBPF | /proc/task, ptrace | runtime 自省 | 框架指标/Tracing |
| **故障隔离** | 强（进程不相互影响） | 弱（一个线程可能崩进程） | 中（panic 可 recover） | 框架决定 |
| **调试难度** | 低（标准工具） | 中（需线程感知） | 高（运行时内部） | 高（框架抽象层） |
| **适用场景** | 强隔离/安全场景 | 并行计算/共享资源 | 高并发 I/O | 复杂编排/分布式 |

### 8.2 资源矩阵汇总

| 资源 | 进程独占 | 线程独占 | 协程独占 | 全共享 | 框架管理 |
|:-----|:---------|:---------|:---------|:-------|:---------|
| 虚拟地址空间 | ✅ 独立页表 | ✗ 同进程共享 | ✗ 共享 | ✗ | ✗ |
| 页表 (CR3) | ✅ 切换刷新 | ✗ 同一页表 | ✗ 同一页表 | ✗ | ✗ |
| 栈 | ✅ 独立 | ✅ 独立 | ✅ 独立 | ✗ | ✗ |
| 寄存器上下文 | ✅ | ✅ | ✅ | ✗ | ✗ |
| errno (TLS) | ✗ 线程级 | ✅ | ✗ 共享 | ✗ | ✗ |
| FD 表 | ✅/✗ CLONE_FILES | ✅ 共享(TGID) | ✗ 共享 | ✗ | ✗ |
| 文件锁 | ✅ 进程级 | ✗ 共享 | ✗ 共享 | ✗ | ✗ |
| 信号处理 | ✅ 共享 | ✅ 共享 | ✗ 继承 | ✗ | ✗ |
| 信号掩码 | ✗ 共享 | ✅ 独立 | ✗ N/A | ✗ | ✗ |
| PID/TID | ✅ PID 唯一 | ✅ TID 唯一 | ✗ 系统无感知 | ✗ | ✅ 任务 ID |
| 命名空间 | ✅ 独立/共享 | ✗ 共享 | ✗ 共享 | ✗ | ✗ |
| cgroup | ✅ 统一限制 | ✗ 共享 | ✗ 共享 | ✗ | ✗ |
| NUMA 绑定 | ✅ mbind | ✗ 共享 | ✗ 继承 | ✗ | ✗ |
| CPU 亲和性 | ✅ sched_setaffinity | ✅ 独立设置 | ✗ 继承 P | ✗ | ✗ |
| I/O 优先级 | ✅ ionice | ✗ 共享 | ✗ 共享 | ✗ | ✗ |
| 定时器 | ✅ 独立 | ✅ 独立 | ✅ 事件循环管理 | ✗ | ✅ 框架调度 |
| 网络连接 | ✅ 独立 | ✗ 共享(SO_REUSEPORT 除外) | ✗ 共享 | ✗ | ✗ |
| eBPF 探针 | ✅ 进程级 uprobe | ✅ 线程级 | ✗ 运行时层之上 | ✗ | ✗ |
| 任务元数据 | ✗ | ✗ | ✗ | ✗ | ✅ 框架自定义 |

### 8.3 可靠性对比

| 可靠性维度 | 进程 | 线程 | 协程 | 任务 |
|:-----------|:-----|:-----|:-----|:-----|
| 隔离性 | ⭐⭐⭐⭐⭐ (地址空间隔离) | ⭐⭐ (共享地址空间) | ⭐⭐ (共享堆，可 recover) | ⭐⭐⭐ (框架级隔离) |
| 崩溃影响 | ⚠️ 仅本进程 | ⚠️ 整个进程都受影响 | ✅ recover 后仅本协程 | ✅ 框架可重试/补偿 |
| 内存安全 | ⭐⭐⭐ (COW+页保护) | ⭐⭐ (共享堆, race 多) | ⭐⭐⭐ (GC 保护) | ⭐⭐⭐ (框架封装) |
| 死锁检测 | ⭐⭐ (lockdep) | ⭐⭐ (lockdep) | ⭐⭐⭐ (无锁经常) | ⭐⭐⭐⭐ (DAG 无环) |
| 恢复手段 | systemd/docker 重启 | pthread_kill/signal | recover/supervisor | 重试/幂等/补偿 |
| 重启代价 | 高（重建进程环境） | 中（重建线程状态） | 低（创建/恢复快） | 中（任务上下文重建） |
| 资源泄漏检测 | OOM/slabtop | pthread 数量监控 | goroutine 数量监控 | metrics 监控 |
| 可恢复性 | ⭐⭐ (需外部重启) | ⭐⭐ (影响进程) | ⭐⭐⭐⭐ (细粒度) | ⭐⭐⭐⭐⭐ (框架级) |

### 8.4 选型决策指南

```
Q: 需要强隔离吗（安全/容错）？
├──✅ 是 → 进程（不同地址空间）
└──❌ 否 → Q: 需要大量并发（>10k 活跃单位）？
          ├──✅ 是 → Q: 需要自动并行（多核）？
          │          ├──✅ 是 → 协程（Go goroutine / Java VT / Rust async + 多线程 executor）
          │          └──❌ 否 → 协程（asyncio / 单线程事件循环）
          │
          └──❌ 否 → Q: 需要 CPU 密集型计算？
                     ├──✅ 是 → 线程（多核并行，无 GIL 语言）
                     └──❌ 否 → 线程（I/O 密集型，线程池）

补充：
  Q: 需要任务编排（DAG/依赖/重试）？
   ├──✅ 是 → 任务框架（Airflow / Ray / Celery）
   └──❌ 否 → 进程/线程/协程直接管理
   
  Q: 跨节点分布式？
   ├──✅ 是 → 任务（Ray Actor / Akka Remote）
   └──❌ 否 → 协程/线程（单机范围）
```

---

## 9. CPU 硬件架构对进程/线程/虚拟化的深度支持

> ⚠️ **本章核心目标**：前面 8 章以软件视角为主，本章从 CPU 硬件微架构重新审视进程中/线程/虚拟化的每个关键操作——页表遍历、TLB、上下文切换、特权级切换、中断递送、缓存一致性、虚拟化等——解释每个操作的**硬件电路做了什么、微架构走的是什么路径、物理代价是多少**。同时深入 KVM 和 Docker 的硬件支持机制。

### 9.1 页表遍历与 TLB —— 虚拟地址翻译的硬件引擎

进程隔离的最底层保障是**页表**，而页表操作完全由硬件（MMU + TLB）执行。

#### 9.1.1 4 级/5 级页表的硬件遍历路径

以 x86-64 4 级页表为例，一次虚拟地址到物理地址的翻译需要硬件走完**4 次内存访问**（4级页表+物理内存）：

```
虚拟地址 (48 位)
  ┌────┬──────┬──────┬──────┬──────┬──────────────┐
  │未用│  PML4 │  PDPT │   PD  │   PT  │  页内偏移    │
  │ 16b│  9b   │  9b   │  9b   │  9b   │    12b       │
  └────┴──────┴──────┴──────┴──────┴──────────────┘

硬件遍历路径 (由 MMU 的 page walker 完成)：

Step 1: CR3 → PML4 基地址
         + (PML4_index × 8) → PML4E (8 字节)
         ├── 检查 Present/Accessed/Dirty/User/Supervisor/NX 位
         └── 如果 PML4E 不 present → #PF (Page Fault)

Step 2: PML4E.Addr → PDPT 基地址
         + (PDPT_index × 8) → PDPTE
         ├── 检查 1GB 页支持 (PS=1 则直接映射 1GB)
         └── 不 present → #PF

Step 3: PDPTE.Addr → PD 基地址
         + (PD_index × 8) → PDE
         ├── 检查 2MB 页支持 (PS=1, 映射 2MB)
         └── 不 present → #PF

Step 4: PDE.Addr → PT 基地址
         + (PT_index × 8) → PTE
         ├── 不 present → #PF
         └── 最终物理地址 = PTE.Addr + offset

总计：4 次 DRAM 访问 (~50-100ns) — 未命中 TLB 的全遍历代价
```

**Page Walk 的硬件单元**：

| 微架构 | Page Walker 数量 | 特点 |
|:-------|:----------------:|:-----|
| Intel Skylake (2015) | 2 个独立 walker | 可并行处理 2 个缺页 |
| Intel Sunny Cove (Ice Lake, 2019) | 2 个 walker | 支持 5-level paging |
| Intel Golden Cove (Alder Lake, 2021) | 4 个独立 walker | 大幅降低多进程 TLB miss 惩罚 |
| AMD Zen 3 (2020) | 2 个嵌套 walker | 支持跨 2 个 walker 的并发 |
| AMD Zen 4 (2022) | 3 个独立 walker | 优化虚拟机 EPT 遍历 |
| Apple M1/M2 (Firestorm) | 8 个 TLB + HW prefetch | 硬件页表预取降低遍历频率 |

**关键物理代价**：

```
4 级页表遍历 = 4 次 DRAM 访问
每次 DRAM 访问 = ~50-100ns (DDR5, 本地 NUMA 节点)
总代价 = ~200-400ns + TLB miss 处理
对比：TLB hit 只需 ~0.5-1ns (L1 DTLB)

5 级页表 (Intel 5-level paging, 57 位虚拟地址)：
  遍历 = 5 次 DRAM 访问 = ~250-500ns
  对大内存系统（>512TB）是必然选择
```

#### 9.1.2 TLB 层次结构与进程切换的影响

TLB (Translation Lookaside Buffer) 是页表遍历结果的硬件缓存。

**x86-64 典型 TLB 层次**：

```
逻辑 CPU 核
  ├── L1 DTLB (Data TLB, 数据翻译)
  │    └── ~64 条目, 4KB 页, 4-way, ~0.5ns 命中延迟
  │    └── ~32 条目, 2MB/4MB 大页, 4-way
  │
  ├── L1 ITLB (Instruction TLB, 指令翻译)
  │    └── ~64 条目, 4KB 页, 8-way, ~0.5ns
  │    └── ~32 条目, 2MB 大页
  │
  ├── L2 STLB (Shared TLB, 统一二级 TLB)
  │    └── ~1536-2048 条目 (Ice Lake: 1536, Zen 4: 3072)
  │    └── ~5-8 cycle 命中延迟
  │    └── 支持 4KB/2MB/1GB 页的混合存储
  │
  └── (部分架构有 L3 TLB, 如 Apple M1 的系统级 TLB)
```

**进程切换时 TLB 的处置**——这是多进程场景最关键的硬件行为：

```
场景 A: 进程 A → 进程 B (不同地址空间)
  ┌─────────────────────────────────────────────┐
  │ CR3 写入新进程的页表基地址                     │
  │                                              │
  │ [传统行为, x86 至强 E5 v4 之前]              │
  │ MOV CR3, new_pgd → 硬件自动刷新全部 TLB      │
  │ 后果: 所有 TLB 条目失效                       │
  │ → 进程 B 启动后大量 TLB miss                 │
  │ → 持续 ~200-500ns/pagewalk × 缺页数          │
  │                                              │
  │ [现代行为, Intel PCID 支持, Haswell+, 2013] │
  │ MOV CR3, new_pgd | PCID                     │
  │ → TLB 条目用 PCID (Process Context ID) 标记 │
  │ → 不同 PCID 的条目保留                       │
  │ → 进程 B 的早期翻译命中 TLB (如果驻留)       │
  │                                              │
  │ [全局页 (Global Pages, PGE=1, PTE.G=1)]      │
  │ 内核态映射的页 (如内核代码) 标记为 Global    │
  │ CR3 切换时不刷新 Global 页的 TLB             │
  │ → 节省约 30-50% 的 TLB 刷新开销 (内核映射)   │
  └─────────────────────────────────────────────┘

场景 B: 同一进程的两个线程切换
  ├── 共享 CR3 (同一地址空间)
  ├── 不需要任何 TLB 维护
  └── 切换延迟纯在寄存器保存/恢复 (~0.1μs)

场景 C: 内核线程 (mm=NULL)
  ├── 借用上一进程的 active_mm
  ├── INVLPG 只刷新被修改的页
  └── 而非整个 TLB
```

**PCID + INVPCID 指令**的精细化 TLB 管理：

```asm
; PCID (Process Context Identifier, 12 位, 支持 4096 个 ID)
; 写入 CR3 时低 12 位为 PCID:
MOV CR3, 0x100000001  ; PCID=1, PGD_BASE=0x100000000

; INVPCID 指令 (Haswell+, 2013) — 精细化 TLB 刷新:
INVPCID [mem], 0  ; 刷新指定地址在所有 PCID 中的 TLB
INVPCID [mem], 1  ; 刷新指定 PCID 中所有条目
INVPCID [mem], 2  ; 刷新指定 PCID 中非全局条目
INVPCID [mem], 3  ; 刷新所有 PCID 中所有条目 (等于 MOV CR3 传统行为)

; 上下文切换优化 (Kernel 使用):
; 1. 写入新 CR3 + PCID
; 2. 不需要 INVPCID (新旧 PCID 不同, 硬件自动区分)
; 3. 内核全局页永不刷新
```

**硬件代价量化**：

| 操作 | 延迟 | 相比基准 |
|:-----|:----:|:---------|
| L1 DTLB 命中 | ~1 cycle (0.3-0.5ns @ 3GHz) | 基准 |
| L2 STLB 命中 | ~5-8 cycles (~1.5-2.5ns) | +3-7× |
| 4 级页表遍历 (TLB miss) | ~200-400ns (DRAM) | +400-800× |
| CR3 写入 + 全 TLB 刷新 (无 PCID) | ~500 cycles (指令) + 后续 miss 风暴 | 极高 |
| CR3 写入 + PCID (无额外刷新) | ~50 cycles | 可接受 |
| INVPCID 单条目 | ~30-50 cycles | 精细化 |

#### 9.1.3 大页 (Huge Pages) 对进程的硬件影响

大页通过减少页表层级降低 TLB 压力：

```
4KB 页: 4 级页表, 每次翻译 4 次内存访问
  → 覆盖 2MB 需要 512 个 PTE → 512 次翻译 → 大量 TLB miss

2MB 大页: 3 级页表 (跳过 PT 级)
  → 一个 TLB 条目覆盖 2MB
  → 覆盖 2MB 范围只需要 1 次翻译

1GB 大页: 2 级页表 (跳过 PD + PT)
  → 一个 TLB 条目覆盖 1GB
  → 对数据库/大模型推理至关重要

TLB 覆盖率对比 (假设 L2 STLB = 1536 条目):
  4KB 页: 1536 × 4KB = 6MB 覆盖 (中大进程远不足)
  2MB 页: 1536 × 2MB = 3GB 覆盖 (适合大多数应用)
  1GB 页: 1536 × 1GB = 1.5TB 覆盖 (超大内存场景)
```

#### 9.1.4 5 级页表 (Intel 5-level paging)

随着物理内存超过 512TB（Intel Optane/大内存服务器），5 级页表成为必需：

```
传统 4 级: 48 位虚拟地址 → 256TB 地址空间
5 级: 57 位虚拟地址 → 128PB 地址空间

新增一级硬件遍历:
  Step 0: CR3 → PML5 基地址
           + (PML5_index × 8) → PML5E
  → 然后继续 4 级遍历

代价: 每次 TLB miss 增加 ~50-100ns DRAM 访问
收益: 支持 >512TB 物理内存
```

### 9.2 上下文切换硬件链路

进程/线程切换的核心代价不是软件逻辑，而是**硬件的状态保存与恢复**。

#### 9.2.1 硬件自动保存/恢复的寄存器组

上下文切换分为**硬件自动保存**和**软件保存**两部分：

```
上下文切换 (由 switch_to() 触发, Linux)
  │
  ├── [硬件自动保存, 发生在 __switch_to_asm]
  │    ├── RIP (指令指针)      — 硬件 push/pop (CALL 或中断)
  │    ├── RSP (栈指针)        — 通过 TSS 或显式 MOV
  │    ├── RFLAGS              — 硬件 push/pop
  │    ├── CS/SS               — 代码段/栈段选择子
  │    └── CR3 (页表基地址)    — 显式 MOV CR3 指令
  │
  ├── [软件显式保存, x86-64 函数调用约定]
  │    ├── Callee-saved: RBX, RBP, R12-R15
  │    ├── XMM6-XMM15 (AVX 状态, 需 XSAVE)
  │    ├── FPU 状态 (MXCSR, x87 tag word)
  │    ├── FS.base / GS.base (TLS 基址, MSR 读写)
  │    └── debug registers (DR0-DR3, 调试断点)
  │
  └── [成本量化, Intel Xeon Gold 6338 @ 2.0GHz]
       ├── 纯寄存器保存/恢复: ~50-100 instructions, ~20-40ns
       ├── CR3 写入 (TLB 刷新): ~50-500 cycles
       ├── XSAVE/XRSTOR (完整 AVX-512): ~2000-5000 cycles (~1-2.5μs)
       └── 总延迟: ~1-10μs (取决于 XSAVE 大小)
```

#### 9.2.2 TSS (Task State Segment) 的硬件角色

x86 的 TSS 在现代 Linux 中不再用于硬件任务切换，但仍不可或缺：

```
TSS (Task State Segment)
  ┌────────────────────────────────────────────┐
  │ [传统使用, 386 时代]                        │
  │ CALL FAR/TSS → 硬件自动保存全部寄存器       │
  │ → 但延迟 ~2000+ cycles, 极其低效            │
  │ → Linux 完全禁用 (没有配置 TSS 任务门)      │
  │                                            │
  │ [现代使用, Linux 实际用途]                  │
  │ 1. 中断栈表 (IST) — 中断处理切换 RSP       │
  │    └── 第 1 个 NMI 用 IST1 栈              │
  │    └── 第 2 个 NMI (嵌套) 用 IST2 栈       │
  │    └── #DB, #MC, #DF 各有独立 IST          │
  │                                            │
  │ 2. I/O 位图 — 控制用户态 IN/OUT 指令访问   │
  │    └── 允许特定进程直接访问硬件端口         │
  │                                            │
  │ 3. Ring 0 栈 — 用户态→内核态切换时的 RSP   │
  │    └── 每个特权级 (Ring 0,1,2) 有独立栈    │
  │    └── 线程创建时设置 tss->rsp0 = 内核栈    │
  │                                            │
  │ [x86-64 限制]                              │
  │ 每个逻辑 CPU 一个 TSS (通过 TR 寄存器指向)  │
  │ TR 加载: LTR 指令 → 加载 TR 段寄存器       │
  │ STR 读取: 获取当前 TSS 位置                │
  └────────────────────────────────────────────┘
```

**Interrupt Stack Table (IST) 的硬件切换**：

```
发生 NMI (非屏蔽中断)
  │
  ├── CPU 硬件自动:
  │    1. 检查 IDT 中 NMI 门描述符的 IST 字段
  │    2. 如果 IST != 0 → 从 TSS.IST[IST_index] 加载 RSP
  │    3. 将旧 RSP/SS/RFLAGS/CS/RIP 压入新栈
  │    4. 跳转到 NMI handler
  │
  ├── 意义: 即使当前在 Ring 0 使用内核栈,
  │    NMI handler 也切换到独立栈
  │    → 避免栈损坏 (当前栈可能已损坏)
  │    → 避免递归栈溢出 (NMI 内再 NMI)
  │
  └── Linux 分配:
       IST0: #DF (Double Fault, 双重故障)
       IST1: #DB (Debug, 调试异常)
       IST2: NMI
       IST3: #MC (Machine Check)
       IST4: #AC (Alignment Check)
```

**IST 与进程/线程的关系**：
```
每个逻辑 CPU 一个 TSS
每个 TSS 有 7 个 IST 指针
每个进程/线程切换时:
  ├── TSS 不切换 (因为 TR 寄存器不涉及进程切换)
  ├── 但 tss->rsp0 必须更新为当前线程的内核栈顶
  └── 写入: per-CPU 变量, 在 schedule() 中更新
       WRMSR(MSR_GS_BASE, &per_cpu_offset)
       per_cpu_tss->rsp0 = thread->kernel_stack_top
```

#### 9.2.3 FS/GS 基址寄存器与 TLS（线程局部存储）

FS 和 GS 段寄存器是实现线程局部存储（TLS）的硬件基础：

```
x86-64 的 FS.base 和 GS.base:
  ┌───────────────────────────────────────────┐
  │ FS.base: 由 MSR 指定 (IA32_FS_BASE)      │
  │ GS.base: 由 MSR 指定 (IA32_GS_BASE)      │
  │ 每个逻辑 CPU 有独立的 MSR                 │
  │                                            │
  │ [进程/线程切换时的硬件行为]                 │
  │ 1. Linux 在每个 task_struct 中保存        │
  │    线程的 FS.base = TLS 区域基址           │
  │                                            │
  │ 2. 上下文切换时:                          │
  │    ┌── 从 task->thread.fsbase 读取         │
  │    └── WRMSR(IA32_FS_BASE, new_fsbase)    │
  │                                            │
  │ 3. 用户态代码通过 FS: 前缀访问:           │
  │    MOV RAX, FS:[0x10]  → 读取 TLS 变量    │
  │    → 无需任何额外地址计算                  │
  │                                            │
  │ [性能代价]                                 │
  │ WRMSR: ~100-300 cycles (序列化指令)       │
  │ 对比: 软件模拟 ~1000+ cycles              │
  │ 所以 Linux 尽量在切换线程时批量处理 MSR    │
  └───────────────────────────────────────────┘

典型 TLS 布局:
  FS.base → ┌────────────────────┐  ← 高地址
             │     TLS 数据       │
             │  (线程私有变量)     │
             ├────────────────────┤
             │  errno             │  ← glibc 存储 errno
             ├────────────────────┤
             │  stack canary      │  ← -0x8(FS): 栈溢出检测
             ├────────────────────┤
             │  thread-pointer    │  ← 线程自引用
             └────────────────────┘  ← 低地址 (FS.base)
```

#### 9.2.4 XSAVE/XRSTOR 与扩展寄存器状态

随着 AVX、AVX-512、AMX (Advanced Matrix Extensions) 引入，线程上下文保存的寄存器体积暴增：

| 指令集 | 引入 | 大小 | 上下文切换代价 |
|:-------|:-----|:----|:-------------|
| x87 + SSE | 原始 | 512 bytes | ~500 cycles |
| AVX | Sandy Bridge (2011) | 256-bit YMM × 16 = 512 bytes | ~1000 cycles |
| AVX-512 | Skylake-SP (2017) | 512-bit ZMM × 32 = 2KB | ~2000 cycles |
| AMX | Sapphire Rapids (2023) | 8 个 1KB tile = 8KB | ~8000-10000 cycles |
| **合计最大** | — | **~10KB+** | **~5-10μs** |

**XSAVE/XRSTOR 硬件协议**：

```asm
; XSAVE — 通过状态位图选择保存的内容
; XCR0 寄存器定义启用的状态组件:
;   Bit 0: x87        — 传统 x87 FPU
;   Bit 1: SSE        — XMM 寄存器
;   Bit 2: AVX        — YMM 寄存器的高 128 位
;   Bit 5: AVX-512    — Opmask/ZMM_high/...
;   Bit 18: AMX       — TILE_CONFIG + TILE_DATA

; 上下文切换时的优化 (延迟保存):
; 1. 进程 A → B 切换时, 不保存 A 的 AVX-512 状态
; 2. 标记 A 的 XSTATE 为"已修改但未保存"
; 3. 如果进程 B 不使用 AVX-512:
;    → 无需保存 (惰性)
; 4. 如果进程 B 使用 AVX-512:
;    → #NM 异常 (Device Not Available)
;    → 内核捕获, 真正执行 XSAVE + XRSTOR
;    → 清除 #NM 标记

; Linux 默认配置 (eager FPU, 4.2+):
; 总是完整保存 (避免 #NM 延迟抖动)
; xsave = XSAVE xstate_bv | XRSTOR
; → ~5000-10000 周期/切换 (AVX-512 启用时)
```

### 9.3 特权级切换硬件

#### 9.3.1 Ring 0-3 与分段保护

x86 的 4 级特权模型是进程隔离的硬件基础：

```
Ring 0 (最高特权, 内核态)
  ├── 可执行所有指令 (IN/OUT/HLT/CLI/STI/LGDT/LIDT/...)
  ├── 可访问所有段的全部地址
  └── 可修改控制寄存器 (CR0-CR4, CR8)

Ring 3 (最低特权, 用户态)
  ├── 不能执行特权指令 (尝试执行会触发 #GP)
  ├── 受限内存访问 (由页表 U/S 位控制)
  └── 必须通过 SYSCALL/INT 0x80 等入口进入内核

进程隔离的硬件实现:
  用户态进程 A: Ring 3, 页表 U=1 (用户可访问)
  用户态进程 B: Ring 3, 页表 U=1, 但页表不同
  内核: Ring 0, 页表 U=0 (Supervisor, 用户不可访问)
  ─────────────────────────────────────────
  进程 A 不可能访问进程 B 的内存 (不同页表)
  用户态不可能访问内核内存 (Supervisor 保护)
```

**代码段描述符的 DPL/RPL/CPL 检查**：

```
访问控制矩阵 (目标段 vs 当前 CPL):

当前 CPL=3                      目标 DPL=0       目标 DPL=3
(用户态)                      (内核数据)       (用户数据)
  代码跳转 (CALL/JMP)           #GP 异常          允许
  数据访问 (MOV DS:[...])       #GP 异常          允许
  栈切换                       TSS.RSP0         TSS.RSP3

当前 CPL=0
(内核态)
  代码跳转                      允许             允许
  数据访问                      允许             允许
```

#### 9.3.2 SYSCALL/SYSRET 的硬件路径

x86-64 系统调用完全由硬件加速，替代了传统 `INT 0x80` 的陷阱门方式：

```
用户态 Ring 3 → 内核态 Ring 0 (SYSCALL)

用户态:
  MOV RAX, system_call_number  ; 系统调用号
  MOV RDI, arg1                ; 参数 1
  MOV RSI, arg2                ; 参数 2
  MOV RDX, arg3                ; 参数 3
  SYSCALL                      ; ← 唯一指令

SYSCALL 指令的硬件行为 (CPU 微代码自动完成):
  1. 保存 RIP → RCX
  2. 保存 RFLAGS → R11
  3. 加载 STAR.LSTAR (IA32_LSTAR MSR) → RIP  ← 内核入口地址
  4. 加载 STAR.SF_MASK 对 RFLAGS 进行掩码  ← 禁用 IF/TF/DF
  5. 切换 CPL=0 (Ring 0)
  6. 加载 TSS.RSP0 → RSP                ← 切换到内核栈

  以上 6 步全部由硬件完成 → ~50-70 cycles
  对比 INT 0x80: ~150-200 cycles (内存查 IDT)

内核态 Ring 0 → 用户态 Ring 3 (SYSRET)

SYSRET 指令的硬件行为:
  1. 加载 RCX → RIP                    ← 返回地址
  2. 加载 R11 → RFLAGS                 ← 恢复标志位
  3. 切换 CPL=3 (Ring 3)
  4. 切换 RSP (用户栈)

  以上 4 步全部由硬件完成 → ~40-60 cycles
```

**MSR 寄存器设置**（每 CPU 核心配置一次）：

```asm
; IA32_STAR MSR (0xC0000081):
;   [47:32]: SYSCALL EIP (32 位兼容)
;   [31:0]: 系统调用入口段选择子
;   → SYSCALL 的 CS = STAR[47:32], SS = STAR[47:32]+8

; IA32_LSTAR MSR (0xC0000082):
;   64 位系统调用入口地址 (Linux: entry_SYSCALL_64)

; IA32_FMASK MSR (0xC0000084):
;   进入内核时屏蔽的 RFLAGS 位
;   → 通常屏蔽 IF (中断) + TF (单步) + DF (方向)
;   → 确保系统调用处理期间不会被中断/单步干扰

; 每 CPU 核心设置 (仅内核启动时写入一次)
WRMSR(IA32_STAR, star_value)
WRMSR(IA32_LSTAR, entry_SYSCALL_64)
WRMSR(IA32_FMASK, X86_EFLAGS_IF | X86_EFLAGS_TF | X86_EFLAGS_DF)
```

#### 9.3.3 RDTSC 与进程时间测量

时间戳计数器 (TSC) 是进程调度和性能测量的硬件基础：

```
RDTSC (Read Time Stamp Counter):
  ┌────────────────────────────────────┐
  │ 返回 CPU 启动以来的 cycle 计数      │
  │ 64 位, 现代 CPU ~3GHz 时           │
  │ 溢出: ~195 年后                     │
  │                                      │
  │ RDTSCP (Read TSC + Processor ID):   │
  │ 同时返回 IA32_TSC_AUX (记录 CPU 号) │
  │ → 支持进程在不同 CPU 间迁移的追踪    │
  └────────────────────────────────────┘

Linux 调度器使用 TSC 测量:
  ├── CFS vruntime 更新:
  │    └── `sched_clock()` = `rdtsc_ordered()` → 纳秒转换
  │    └── 精度 ~1ns, 开销 ~20-40 cycles
  │
  ├── 进程 CPU 时间统计:
  │    └── `task_times()` → 用户态+内核态 TSC 差值
  │
  └── Perf 采样:
       └── `perf_event` 使用 TSC 作为时间戳

关键约束:
  invariant TSC (Nehalem+, 2008):
    ├── 所有 P-state/C-state 下恒速运行
    ├── 多 socket 间同步 (需 BIOS 保证)
    └── 允许跨 CPU 的 TSC 差分有效
```

### 9.4 中断与异常硬件路径

#### 9.4.1 IDT (中断描述符表) 的硬件加载

IDT 是中断/异常从硬件到软件的分发入口：

```
IDT 在内存中的布局 (x86-64):

  基地址: IDTR (LIDT 指令加载)
  每个条目: 16 字节 (x86-64, 对比 32 位的 8 字节)

  门描述符类型:
   ┌──────────┬──────┬──────┬────────────────────────────┐
   │ 门类型   │ Type │ 权限  │ 硬件行为                   │
   ├──────────┼──────┼──────┼────────────────────────────┤
   │ 中断门   │ 0xE  │ DPL  │ IF 自动清除 (禁止嵌套中断) │
   │ 陷阱门   │ 0xF  │ DPL  │ IF 不修改 (允许嵌套)       │
   │ 任务门   │ 0x5  │ DPL  │ 硬件任务切换 (废弃)        │
   └──────────┴──────┴──────┴────────────────────────────┘

  IDT 格式 (x86-64 中断门):
    Offset [63:48]     — handler 地址高 16 位
    Present            — 1=有效, 0=异常
    DPL [14:13]        — 描述符特权级
    Type [11:8]        — 中断门/陷阱门
    IST [7:5]          — 中断栈表索引
    Segment Selector   — 代码段选择子 (通常 = __KERNEL_CS)
    Offset [31:16]     — handler 地址低 16 位
    Offset [15:0]      — handler 地址段内偏移
```

**硬件中断分发路径**：

```
外部设备中断 (如 NVMe SSD 完成):

NVMe Controller ── MSI-X 中断 ──→ PCIe Root Complex
                                         │
                                    I/O APIC 或直连 CPU
                                         │
                                    LAPIC (Local APIC)
                                         │
                                    ┌─────┴──────┐
                                    │ CPU 核心     │
                                    │              │
                                    │ 1. 检查 RFLAGS.IF
                                    │    如果 IF=0 → 等待 (CLI)
                                    │    如果 IF=1 → 继续
                                    │              │
                                    │ 2. 读取 IDTR
                                    │    IDT[vector] → 门描述符
                                    │              │
                                    │ 3. 检查 CPL 和 DPL
                                    │    如果 CPL > DPL → #GP
                                    │              │
                                    │ 4. 如果 IST != 0:
                                    │    RSP = TSS.IST[n]
                                    │    如果是中断门: IF=0
                                    │              │
                                    │ 5. 硬件压栈:
                                    │    SS, RSP (如果 Ring 切换)
                                    │    RFLAGS
                                    │    CS, RIP
                                    │    错误码 (异常才有)
                                    │              │
                                    │ 6. JMP handler (远跳转)
                                    └──────────────┘
```

**硬件代价**：

| 操作 | 延迟 (cycles) | 延迟 (ns @3GHz) |
|:-----|:-------------:|:----------------:|
| 硬件中断分发 (IDT查表+栈切换) | ~100-200 | ~33-67 |
| 中断上下文保存 (push 寄存器) | ~50-100 | ~17-33 |
| iret 返回 (从 handler 恢复) | ~50-100 | ~17-33 |
| 完整中断处理 (硬件部分) | ~200-400 | ~67-133 |
| 完整中断 + 软件 handler | ~1000-5000 | ~0.3-1.7μs |

#### 9.4.2 #PF (Page Fault) 的硬件行为

Page Fault 是最影响进程性能的异常，其硬件路径直接决定缺页处理开销：

```
#PF 发生时 CPU 自动填充的信息:

CR2 — 触发缺页的线性地址 (虚拟地址)
Error Code (硬件压入栈中):
  Bit 0 (P):  0=页不存在, 1=页级保护违例
  Bit 1 (W):  0=读访问, 1=写访问
  Bit 2 (U):  0=内核态, 1=用户态
  Bit 3 (RSVD): 保留位违例 (页表保留位=1)
  Bit 4 (ID):  指令获取缺页
  Bit 5 (PK):  保护键违例 (MPK, Memory Protection Keys)
  Bit 6 (SS):  Shadow Stack 违例 (CET)
  Bit 7 (HLAT): HLAT (Hypervisor-managed Linear Address Translation)

Linux 缺页处理路径 (基于硬件提供的 #PF 信息):
  handle_mm_fault()
    ├── 页不存在 (P=0):
    │    ├── 匿名页 → do_anonymous_page() → 分配零页 + COW
    │    ├── 文件映射 → do_fault() → 从磁盘/页缓存读入
    │    └── 栈扩展 → do_anonymous_page() → 按需分配
    │
    ├── 写 COW 页 (W=1, P=1, 页表只读):
    │    └── do_wp_page() → 复制物理页 → 更新页表 → 恢复写权限
    │
    ├── 保护键违例 (PK=1):
    │    └── MPK 保护检查 → 是否允许访问
    │
    └── 内核态缺页:
         └── 内核也可能缺页 (vmalloc/module/...)
```

**缺页处理的硬件/软件总代价**：

```
├── 软件态: handle_mm_fault() → do_anonymous_page()
│    → 分配物理页 (~50-100ns, buddy allocator)
│    → 清零页 (~150-300ns, 4KB 页)
│    → 插入页表 (~10-50ns)
│    → 总计 ~200-500ns (纯软件)

├── 文件缺页 (从磁盘读取):
│    → 触发块 I/O
│    → 如果页缓存命中: ~100-200ns
│    → 如果磁盘 I/O: ~100μs-10ms (SSD)
│    └── 这是进程启动时的最大延迟源

├── 透明大页 (THP) 缺页:
│    → 2MB 连续页分配
│    → 可能触发内存 compaction (~ms 级)
│    └── 这是 Java/大数据进程 GC 抖动的硬件根因
```

#### 9.4.3 MCE (Machine Check Exception) 的硬件路径

MCE 是 CPU 检测到硬件错误时触发的特殊异常，与进程的 RAS 模型直接相关：

```
MCE 触发条件:
  ├── 内存 ECC 不可纠正错误 (UE, Uncorrectable Error)
  ├── 缓存 SRAM 位翻转 (L1/L2/L3 parity/ECC)
  ├── 总线错误 (Intel QuickPath/UPI)
  ├── CPU 内部错误 (微码/执行单元)
  └── 热节流 (Thermal Throttling)

MCE 硬件路径:
  1. CPU 内部错误检测电路触发
  2. 硬件在 IA32_MCi_STATUS MSR 记录错误信息
     └── 记录: 错误类型、地址 (可能)、严重等级
  3. 如果错误可恢复 (CE):
     → 仅记录 MSR, 不触发异常
     → 软件通过 CMCI (Corrected Machine Check Interrupt) 轮询
  4. 如果错误不可恢复 (UE):
     → 触发 #MC (Machine Check Exception, vector=18)
     → CPU 进入 IST3 栈 (独立中断栈)
     → 执行 mce_handler

MCE 与进程的关系:
  ├── 可恢复 CE: 内核记录 → 进程继续 (但可靠性降级)
  ├── 进程相关 UE (用户态指令/数据):
  │    → 内核向进程发送 SIGBUS
  │    → 进程可选择处理 (备份数据/优雅退出)
  │    └── 不处理则进程被 SIGBUS 终止
  ├── 进程无关 UE (内核/空闲页):
  │    → 内核尝试 page offlining
  │    → 将故障物理页标记为坏页 → 不再分配给任何进程
  └── 严重的 UE (总线/缓存/Core):
       → 内核 panic (不可恢复)
       → kdump → 硬重启
```

### 9.5 APIC 与中断分发硬件

#### 9.5.1 Local APIC (LAPIC) 架构

LAPIC 是每个 CPU 核心的中断管理和进程间中断 (IPI) 硬件：

```
每个逻辑 CPU 核拥有独立的 Local APIC:

Local APIC (内存映射, 默认物理地址 0xFEE00000)
  ├── ICR (Interrupt Command Register, 64 位)
  │    └── 用于发送 IPI (进程间中断)
  │         └── destination (目标 CPU)
  │         └── vector (中断向量号)
  │         └── delivery mode (Fixed/NMI/SMI/INIT/Startup)
  │
  ├── IRR (In-Service Register, 256 位)
  │    └── 当前正在处理的中断
  │
  ├── TMR (Trigger Mode Register, 256 位)
  │    └── 边沿触发 vs 电平触发
  │
  ├── PVR (Processor Priority Register)
  │    └── 当前 CPU 可处理的中断优先级阈值
  │
  ├── TIMER (可编程定时器)
  │    └── 每 CPU 核的独立定时器
  │    └── Linux 用作调度 tick (历史) / hrtimer 时钟源
  │
  └── LVT (Local Vector Table)
       ├── LINT0, LINT1 — 传统 8259A 级联
       ├── ERROR — APIC 内部错误
       ├── PCINT — 性能计数器溢出
       ├── CMCI — Corrected Machine Check
       └── Thermal — 热监控
```

**IPI 的硬件协议**（调度器中实现负载均衡的基础）：

```
一个 CPU 核向另一个核发送 IPI:

CPU 0 写入 ICR:
  ICR = (target_apic_id << 24) | delivery_mode | vector

硬件行为:
  ┌──────────────────────────────────────────────┐
  │ CPU 0 的 LAPIC 通过系统总线 (UPI/System Bus) │
  │ 发送中断消息到目标 CPU 1 的 LAPIC            │
  │                                               │
  │ CPU 1 的 LAPIC 接收:                         │
  │ 1. 检查目标 APIC ID 是否匹配                  │
  │ 2. 检查优先级 (是否高于 PPR)                  │
  │ 3. 将中断加入 IRR (挂起队列)                   │
  │ 4. 如果 IF=1 (中断允许):                      │
  │    → 等待当前指令完成后分发                   │
  │ 5. 如果 CPU 1 在低功耗 C-state:               │
  │    → 唤醒 (C1 halt → C0 运行)                │
  │                                               │
  │ IPI 延迟: ~0.5-2μs (同一 socket)              │
  │ IPI 延迟: ~2-5μs (跨 socket, 通过 UPI)       │
  └──────────────────────────────────────────────┘

IPI 的 Linux 使用场景:
  ├── TLB shootdown (flush_tlb_mm_range):
  │    → 某进程的页表被修改 → 所有使用该页表的 CPU
  │      需要刷新 TLB
  │    → 发送 IPI 给每个相关 CPU
  │    → 等待全部应答 → 多核扩展性瓶颈
  │    └── 4 核以下: <1μs, 128 核: ~数百 μs
  │
  ├── 调度器负载均衡 (load_balance):
  │    → 发现某 CPU 空闲 → 发送 RESCHEDULE_VECTOR IPI
  │    → 使空闲 CPU 重新 schedule()
  │    └── 频率: 每秒数千次 (高负载系统)
  │
  ├── perf 采样:
  │    → CPU 0 的 PMC 溢出 → 触发 PMI IPI 到指定 CPU
  │    └── PMI handler 执行采样
  │
  └── CPU hotplug:
       → 启动/停止目标 CPU 核心
```

#### 9.5.2 x2APIC 与中断性能

x2APIC (2011, Sandy Bridge) 是对传统 xAPIC 的重大改进：

```
xAPIC (传统):   MMIO 访问, 每次 ICR 写入 ~200 cycles
x2APIC (新):   MSR 访问 (RDMSR/WRMSR), 每次 ICR ~50 cycles

关键改进:
  ├── 寄存器通过 MSR 而非 MMIO 访问
  │    → 消除 MMIO 的序列化开销
  │    → ~4× 加速 (50 vs 200 cycles)
  │
  ├── APIC ID 从 8 位扩展到 32 位
  │    → 支持 >255 逻辑 CPU (最大 4M CPU)
  │    → 现代的 128-512 核系统必须开启
  │
  └── 支持中断重映射 (Interrupt Remapping)
       → IOMMU 拦截所有中断 → 安全/虚拟化必须
```

### 9.6 CPU 缓存架构与进程亲和性

#### 9.6.1 缓存层次对进程切换的影响

```
物理 CPU Socket
  ├── L1d (32KB) / L1i (32KB) — 每核私有
  │    ├── 延迟: ~4 cycles (~1.3ns @ 3GHz)
  │    ├── 关联度: 8-way
  │    └── 进程切换影响: 完全失效 (上下文无关)
  │
  ├── L2 (512KB-2MB) — 每核私有 (现代 x86)
  │    ├── 延迟: ~12-14 cycles (~4ns)
  │    ├── 关联度: 8-12 way
  │    └── 进程切换影响: 完全失效
  │
  ├── L3 (20-60MB) — 同 socket 所有核共享
  │    ├── 延迟: ~40-50 cycles (~13-17ns)
  │    ├── 关联度: 12-20 way (切片式分布)
  │    └── 进程切换影响: 部分命中 (如果数据在 L3 缓存)
  │         └── 但 L3 被其他核占用 → 命中率取决于工作集
  │
  └── L4 (eDRAM, 可选, 如 Broadwell Iris Pro)
       └── 128MB, 延迟 ~60-70 cycles
```

**进程切换的缓存污染代价量化**：

```
情景: 进程 A ↔ 进程 B 频繁切换 (如 4ms CFS 时间片)

进程 A 运行 4ms:
  ├── 预热 L1/L2 (工作集 ~数百 KB): ~10-100μs 预热时间
  ├── 稳定执行 (L1/L2 命中率 ~95%+)
  └── 切换走时 L1/L2 被进程 B 污染

进程 B 运行 4ms:
  ├── 刷新进程 B 的自己工作集
  ├── 进程 A 的缓存行被逐出 (LRU 策略)
  └── 进程 A 下次运行需重新预热

重复上述 → 实际有效吞吐 ≈ 50-70% 理论吞吐

优化方案:
  1. 增大时间片 (减少切换频率, 但增加响应延迟)
     6ms (default) → 10ms: 缓存命中率 +5-10%, 但交互延迟 +67%
  2. CPU pinning (taskset/isolcpus):
     → 进程或线程绑定固定 CPU 核心
     → 消除跨核缓存丢失
     → 代价: 牺牲负载均衡
  3. Intel CAT (Cache Allocation Technology):
     → 硬件分区缓存, 确保关键进程独占 L3 切片
```

#### 9.6.2 Intel CAT / CMT / MBM 硬件资源监控

Intel Resource Director Technology (RDT) 提供硬件级的缓存/内存带宽控制：

```
Intel RDT 功能集:

├── CAT (Cache Allocation Technology, Broadwell, 2014)
│    ├── 将 L3 缓存分成多个分区 (CLOS, Class of Service)
│    ├── 最多 16 个 CLOS
│    ├── 每个 CLOS 分配 bitmask (如 0x0FF = 8/12 切片)
│    ├── 通过 MSR 关联进程/线程的 CLOS
│    └── 硬件缓存分配 (非软件/非驱逐, 而是物理分区)
│
├── CMT (Cache Monitoring Technology)
│    ├── 监控每个 CLOS/进程的 L3 缓存占用
│    ├── 硬件计数器, 无软件开销
│    └── 每 CLOS 的: LLC Occupancy (缓存占用字节)
│
└── MBM (Memory Bandwidth Monitoring)
     ├── 监控每个 CLOS 的内存带宽消耗
     └── 本地 DRAM 带宽 + 远程 DRAM 带宽 (NUMA)

Linux resctrl 接口:
  # 创建 CLOS 组
  mkdir /sys/fs/resctrl/critical
  # 分配 L3 缓存 bitmask (12 way 中分配 6 way)
  echo "L3:0=0x3f" > /sys/fs/resctrl/critical/schemata
  # 分配进程到 CLOS
  echo $PID > /sys/fs/resctrl/critical/tasks
```

**典型应用场景**：

```
场景: 数据库 (关键) + 批处理 (可牺牲) 共存同一台机器

关键数据库进程 (P0):
  CLOS 0 → L3 bitmask = 0xF00 (高 4 way, 专用)
  隔离保护: 批处理不会污染数据库的缓存

批处理进程 (P1):
  CLOS 1 → L3 bitmask = 0x0FF (低 8 way)
  限制: 只使用最多 8/12 的 L3 容量

硬件行为:
  ├── 数据库访问的缓存行 → 只能存入 way 8-11
  ├── 批处理访问的缓存行 → 只能存入 way 0-7
  ├── 两者物理隔离 (非驱逐/非软件约束)
  └── 数据库延迟抖动从 ~17% 降至 ~2% (Intel 公开数据)
```

### 9.7 硬件虚拟化支持 (KVM 场景)

#### 9.7.1 VMX (Intel VT-x) 的硬件架构

VT-x 通过在 CPU 中引入两种操作模式，使虚拟机 (VM) 中的进程运行接近原生性能：

```
CPU 操作模式 (VT-x 引入):

┌───────────────────────────────────────────────────┐
│                   VMX Root Mode                    │
│  (Host, VMM/KVM 运行的模式)                       │
│  Ring 0-3 完全可用                                 │
│  可以执行 VMXON/VMXOFF/VMREAD/VMWRITE/VMLAUNCH     │
│  可以访问扩展页表 (EPT)                            │
└──────────────────┬────────────────────────────────┘
                   │ VM Entry (VMLAUNCH/VMRESUME)
                   │ VM Exit (硬件自动)
                   ▼
┌───────────────────────────────────────────────────┐
│                  VMX Non-Root Mode                  │
│  (Guest, VM 中的 OS/进程运行的模式)                │
│  Ring 0-3 可用 (Guest 的 OS 感知到 Ring 0)        │
│  执行敏感指令 → 自动 VM Exit (硬件捕获)            │
│  物理内存通过 EPT 翻译 (二级地址翻译)              │
└───────────────────────────────────────────────────┘

VM Entry/Exit 的硬件自动操作:

VM Entry (发生自 VMLAUNCH 或 VMRESUME):
  1. 从 VMCS (VM Control Structure) 加载 Guest 状态:
     └── CS, SS, DS, ES, FS, GS, TR, LDTR
     └── CR0, CR3, CR4, CR2, CR8
     └── RSP, RIP, RFLAGS
     └── SYSENTER_CS/ESP/EIP MSRs
     └── FS.base, GS.base, GDTR, IDTR
     └── DR0-DR7 (调试寄存器)
     └── 全部硬件加载 (非软件模拟)

VM Exit (任何导致 VM Exit 的事件):
  1. 检查 VMCS 的 Exit 控制位 → 是否引起 VM Exit
  2. 将 Guest 状态保存到 VMCS (硬件自动)
  3. 从 VMCS 加载 Host 状态 (硬件自动)
  4. 跳转到 Host 的 VM Exit handler

VM Exit 的硬件延迟 (Sapphire Rapids, 2023):
  ├── 轻量 VM Exit (无 EPT 违例): ~500-1000 cycles (~0.2-0.3μs)
  ├── VM Exit + EPT 缺页: ~2000-5000 cycles (~1-1.7μs)
  └── 对比: 软件模拟 ~10000+ cycles
```

#### 9.7.2 VMCS (VM Control Structure) 的硬件管理

VMCS 是硬件维护的虚拟 CPU 状态数据结构：

```
VMCS (每个 vCPU 一个, 在物理内存中):

VMCS Region (~4KB 物理连续内存)
  ├── 客户寄存器状态 (Guest State Area)
  │    ├── CR0, CR2, CR3, CR4 — 控制寄存器
  │    ├── RSP, RIP — 栈和指令指针
  │    ├── RFLAGS — 标志寄存器
  │    ├── 段寄存器: CS, SS, DS, ES, FS, GS, TR, LDTR
  │    │    └── 每个段含: selector, base, limit, ar
  │    ├── GDTR, IDTR — 全局/中断描述符表
  │    ├── MSRs — SYSENTER, FS.base, GS.base, ...
  │    ├── 调试寄存器 DR0-DR7
  │    └── 活动状态 (ACTIVITY_ACTIVE/ACTIVITY_HLT/...)
  │
  ├── 宿主机寄存器状态 (Host State Area)
  │    ├── CR0, CR3, CR4 — 宿主机的控制寄存器
  │    ├── RSP, RIP — VM Exit 后的入口
  │    ├── CS, SS, DS, ES, FS, GS, TR
  │    └── MSRs — 宿主机的系统 MSR
  │
  ├── VM 执行控制 (VM-Execution Controls)
  │    ├── 哪些指令/事件引起 VM Exit
  │    │    ├── INVLPG → Exit: yes/no
  │    │    ├── CPUID → Exit: yes/no
  │    │    ├── HLT → Exit: yes/no (kvm 设为 yes)
  │    │    ├── MOV CR3 → Exit: yes/no
  │    │    └── RDPMC → Exit: yes/no
  │    │
  │    ├── 二级地址 (EPT) 指针
  │    └── APIC 虚拟化控制
  │
  ├── VM 退出控制 (VM-Exit Controls)
  │    ├── VM Exit 时保存/加载哪些 MSR
  │    └── 退出时的中断确认
  │
  ├── VM 进入控制 (VM-Entry Controls)
  │    ├── VM Entry 时注入的事件
  │    ├── 加载 Guest MSR
  │    └── 事件注入 (Event Injection)
  │         └── KVM 用此注入中断到 Guest
  │         └── 如: 向 Guest OS 注入定时器中断
  │
  ├── VM 退出原因 (VM-Exit Reason — 硬件填写)
  │    ├── Exit reason 编码 (0-67, 如 #49=EPT violation)
  │    ├── Exit qualification (额外信息)
  │    └── Guest 物理地址 (触发 EPT 违例时)
  │
  └── 指令执行信息 (Instruction Information)
       └── 引起 VM Exit 的指令编码、操作数
```

**关键 VM Exit 场景与频率**（以 KVM 运行 Linux VM 为例）：

| VM Exit 原因 | 频率 (per sec) | 硬件开销 | 优化 |
|:-------------|:--------------:|:---------|:-----|
| 定时器中断 (Timer) | ~1000 (HZ=1000) | ~1μs | 使用 APICv 减少 |
| EPT 违例 (缺页) | 启动时高, 稳定后低 | ~1μs+ | 大页 (2MB/1GB) |
| I/O 指令 (in/out) | 设备相关 | ~1μs | Paravirtualized IO (virtio) |
| CPUID / MSR 读取 | ~100-1000 | ~1μs | 缓存 MSR 值 |
| HLT 指令 (空闲) | VM 空闲时 | ~0.5μs | KVM 使用 mwait |
| CR3 切换 | ~1000-10000 | ~0.5-1μs | VPID 减少 TLB 刷新 |
| MOV DR (调试) | 极少 | ~1μs | 正常不触发 |

#### 9.7.3 EPT (Extended Page Tables) — 二级地址翻译硬件

EPT 是 VT-x 最重要的硬件特性——它让 Guest OS 管理自己的页表，同时 VMM 通过另一套页表控制物理内存：

```
传统软件虚拟化 (无 EPT):
  Guest OS 的进程创建 → Guest 写 CR3 → VM Exit
  → KVM 读取 Guest CR3 → 模拟页表遍历
  → 每个 Guest 页表 walk 都引起 VM Exit
  → 性能灾难 (数十 μs 每缺页)

EPT 硬件支持 (VT-x, 2008):
  Guest CR3 写入 → 不引起 VM Exit
  Guest MMU 使用 Guest CR3 做 GVA→GPA 翻译 (一级)
  然后硬件自动使用 EPT 做 GPA→HPA 翻译 (二级)
  ─────────────────────────────────────────
  GVA (Guest Virtual Address)
      │ Guest CR3 (Guest 页表)
      ▼
  GPA (Guest Physical Address)
      │ EPT 指针 (VMM 管理的二级页表)
      ▼
  HPA (Host Physical Address)
  ─────────────────────────────────────────
  整个翻译过程在硬件中完成, 无需 VM Exit!
```

**EPT 的硬件遍历路径**：

```
EPT 页表结构 (类似原生页表, 但由 VMM 维护):

EPT PML4 → EPT PDPT → EPT PD → EPT PT
  (4 级, 与 Guest 页表独立)

EPT 违例 (两种类型):
  ├── EPT violation: 权限违例 (读/写/执行)
  │    → VM Exit, KVM 检查 EPT 权限
  │    → 正常缺页处理
  │
  └── EPT misconfiguration: EPT 条目格式错误
       → VM Exit, KVM 修复 EPT 条目

EPT 性能优势:
  ├── Guest CR3 切换不引起 VM Exit
  ├── Guest 页表遍历不引起 VM Exit
  ├── Guest 缺页处理: 大部分在 Guest 内完成
  └── EPT 缺页: 每页一次 VM Exit (之后不再)
```

**EPT + 大页的协同**：

```
Host 使用 2MB 大页分配 VM 内存:
  → EPT 页表使用 2MB 条目 (减少页表层级)

效果:
  ├── EPT 页表: 从 4 级→3 级 (512GB 以下 VM)
  ├── EPT TLB 覆盖: 一个条目 2MB
  ├── EPT 缺页: 一次分配 2MB (~降低 99.9% 的 EPT 缺页)
  └── 对数据库/大模型 VM → 性能提升 10-30%
```

**量化对比**（4 vCPU VM, 16GB 内存, 数据库负载）：

| 配置 | 每秒钟 VM Exit 次数 | vCPU 利用率损耗 |
|:-----|:-------------------:|:---------------:|
| 无 EPT (纯软件 MMU) | ~500,000+ | ~30-50% |
| EPT + 4KB 页 | ~5,000-10,000 | ~5-10% |
| EPT + 2MB 大页 | ~1,000-2,000 | ~1-3% |
| EPT + 1GB 大页 | ~200-500 | <1% |

#### 9.7.4 VPID (Virtual Processor ID) — TLB 虚拟化

VPID 为每个 vCPU 分配一个硬件 ID，标记 TLB 条目，消除跨 vCPU 切换的 TLB 刷新：

```
无 VPID (传统, VMX 初期):
  ┌──────────────────────────────────────────────┐
  │ vCPU 1 → 运行 → vCPU 1 的 TLB 条目          │
  │ vCPU 2 → 运行 → 必须刷新所有 TLB             │
  │ 因为 TLB 不知道当前是哪个 vCPU                │
  │ 后果: 每切换一次 vCPU, 完全 TLB 刷新          │
  ├──────────────────────────────────────────────┤
  │ 假设: 4 vCPU 的 VM → 4 个 vCPU 之间          │
  │ 频繁 VM Entry/Exit → 每纳秒都在刷 TLB        │
  │ → 性能损失: 20-40%                           │
  └──────────────────────────────────────────────┘

有 VPID (Westmere+, 2010):
  ┌──────────────────────────────────────────────┐
  │ 每个 vCPU 分配唯一 VPID (0-4095)              │
  │ TLB 条目用 (VPID, 虚拟地址) 作为索引           │
  │ vCPU 1 → 运行 → TLB 条目标记 VPID=1          │
  │ vCPU 1 退出 → 进入 vCPU 2:                   │
  │   → 不刷新 TLB                                │
  │   → vCPU 2 运行, TLB 条目标记 VPID=2         │
  │ vCPU 1 再次进入:                              │
  │   → VPID=1 的 TLB 条目仍在!                   │
  │   → 直接命中, 无需重新遍历                      │
  ├──────────────────────────────────────────────┤
  │ 性能: 消除 ~99% 的跨 vCPU TLB 刷新            │
  │ 仅 vCPU 主动修改页表时才需刷新该 VPID          │
  └──────────────────────────────────────────────┘

VMX 的 TLB 维护指令 (VPID 配合):

  INVEPT: 刷新 EPT 缓存
    INVEPT type=0 (single-context) — 指定 VPID 的 EPT
    INVEPT type=1 (all-context)    — 全部 EPT

  INVVPID: 刷新 TLB (非 EPT)
    INVVPID type=0 (individual-address) — 单地址
    INVVPID type=1 (single-context)     — 指定 VPID 全部
    INVVPID type=2 (all-context)        — 全部
    INVVPID type=3 (single-context-retaining-globals) — 除全局页
```

#### 9.7.5 APICv (APIC Virtualization)

APICv 将中断处理从 VM Exit 中移出，通过硬件在 VMX Non-Root 模式中处理中断：

```
无 APICv (传统):
  ├── Guest OS 写 APIC 寄存器 → VM Exit → KVM 处理
  ├── 外部中断到达 → VM Exit → KVM 注入 → VM Entry
  └── 每秒 ~1000+ 次 VM Exit (定时器 + I/O 中断)

有 APICv (Haswell+, 2013):

  ├── 虚拟 APIC 页面 (Virtual APIC Page)
  │    └── Guest 直接访问此页 (在 VMX Non-Root 模式中)
  │    └── 读 APIC 寄存器: 直接读, 无 VM Exit
  │    └── 写部分寄存器: 直接写, 无 VM Exit
  │    └── 写敏感寄存器 (如 EOI): 硬件处理, 可能无 VM Exit
  │
  ├── Posted Interrupt 处理
  │    └── 外部中断 → IOMMU 直接将中断写入 VMCS 的中断字段
  │    └── 硬件在 VMX Non-Root 模式中递送中断给 Guest
  │    └── 完全 0 次 VM Exit!
  │
  └── APIC Timer 虚拟化
       └── Guest 写 LAPIC Timer → 硬件在 Non-Root 中管理
       └── 到期 → 硬件直接注入定时器中断
       └── 完全 0 次 VM Exit!

APICv 效果 (数据库 VM):
  中断相关 VM Exit: 从 ~10000/s → ~100/s
  (降低 99%, 对应 ~5-15% 整体性能提升)
```

### 9.8 IOMMU 与设备隔离

#### 9.8.1 VT-d (Intel Virtualization Technology for Directed I/O)

VT-d 提供了设备 DMA 和中断的硬件隔离，是 VFIO 直通和容器设备访问的基础：

```
IOMMU (I/O Memory Management Unit, VT-d)

设备 (如 NVMe SSD/NIC/GPU)
  │
  │ DMA 请求 (设备物理地址)
  │
  ▼
IOMMU 硬件:
  ├── DMA Remapping:
  │    ├── 设备 → IOMMU → 通过 DMA 重映射表
  │    ├── 将设备物理地址 → 系统物理地址
  │    └── 或映射到 VM 的 Guest 物理地址
  │
  ├── Interrupt Remapping:
  │    ├── MSI/MSI-X 中断 → IOMMU 检查合法性
  │    ├── 将设备中断重映射到 VM 的 vCPU
  │    └── 支持 Posted Interrupts (与 APICv 协同)
  │
  └── 权限检查:
       ├── 设备只能 DMA 到其被分配的地址范围
       ├── 防止设备 DMA 攻击 (PCIe non-transparent bridge)
       └── 每个设备一个 domain (独立地址空间)

Linux VFIO 路径 (设备直通):
  1. 用户态/QEMU 调用 VFIO 接口
  2. 内核将设备绑定到 VFIO 驱动
  3. IOMMU 为设备建立 DMA 映射
  4. 设备 DMA 直接操作用户态/QEMU 分配的缓冲区
  5. 整个过程: 硬件的 DMA 重映射 + 中断重映射
```

**SR-IOV (Single Root I/O Virtualization)** —— 从物理功能到虚拟功能：

```
物理设备 (PF, Physical Function)
  ├── VF 0 (Virtual Function) ──→ VM 0 (直通)
  ├── VF 1 (Virtual Function) ──→ VM 1 (直通)
  ├── VF 2 (Virtual Function) ──→ VM 2 (直通)
  └── VF N ... ──→ ... (每个 VM 独占设备资源)

硬件支持:
  ├── PF 管理所有 VF 的资源分配 (NIC MAC 地址/队列)
  ├── VF 绕过 VMM, 直接做 DMA
  ├── VF 有独立的 PCIe 配置空间 (Bus:Device:Function)
  ├── VF 的 DMA 通过 IOMMU 隔离
  └── VF 中断通过 MSI-X 直通到 VM (无 VM Exit)

性能:
  ├── 无 SR-IOV (软件网桥): ~1-5 Gbps, ~10-100μs 延迟
  └── SR-IOV VF (硬件直通): ~25-100 Gbps, ~1-10μs 延迟
```

#### 9.8.2 设备直通的 VM 进程视角

```
VM 中 Guest OS 的进程 → 设备操作路径:

Guest 进程:
  write() → ext4 → block layer → virtio-blk → vring → ...
  
  传统 virtio (软件 I/O):
    Guest 写 vring → [VM Exit?] → KVM 处理 → Host 块 I/O
    → 设备完成 → 中断 → [VM Exit] → KVM → Guest
    └── 每次 I/O: 2× VM Exit + Host 软件栈

  VFIO 直通 (硬件 I/O):
    Guest 进程 → Guest NVMe 驱动 → MMIO 写 NVMe 队列
    → [无 VM Exit!] NVMe 直接做 DMA
    → [完成中断通过 Posted Interrupt 递送]
    └── 每次 I/O: 0 VM Exit (完全硬件路径)
    └── 延迟: 与裸机一致 (~5-10μs NVMe 延迟)
```

### 9.9 Docker 容器的硬件视角

#### 9.9.1 为什么 Docker 不需要特殊 CPU 硬件

Docker 与 VM 的关键区别在于**共享内核**，因此不需要 VT-x/EPT 等硬件虚拟化支持：

```
VM 隔离 (硬件级):
  虚拟机 A: 完整的 OS (内核 + 进程)
  虚拟机 B: 完整的 OS (内核 + 进程)
  隔离: CPU VT-x (VMX Non-Root), 内存 EPT, 设备 VT-d
  每 VM: 完整的内核镜像 (4-8GB 内存)

Docker 容器隔离 (OS 级, 共享宿主机内核):
  宿主机内核 (Ring 0) — 所有容器共享
  容器 A: 进程组 + namespace + cgroup
  容器 B: 进程组 + namespace + cgroup
  隔离: 内核级抽象 (非硬件)
  不需要: VT-x, EPT, VT-d (除非特殊场景)

硬件视角的 Docker 容器:
  ┌─ Host OS ──────────────────────────────────┐
  │  Linux Kernel (Ring 0)                       │
  │   ┌──── PID NS ───┐  ┌──── PID NS ───┐      │
  │   │ 容器 A 的进程   │  │ 容器 B 的进程   │      │
  │   │ PID=1 ~ 1000  │  │ PID=1 ~ 2000  │      │
  │   │ cgroup CPU=50%│  │ cgroup CPU=30%│      │
  │   │ cgroup MEM=1G │  │ cgroup MEM=2G │      │
  │   └───────────────┘  └───────────────┘      │
  │                                              │
  │  CPU 硬件 (Ring 0-3):                        │
  │  ├── 页表: 所有容器进程的页表在宿主 CR3      │
  │  ├── TLB: 无额外隔离 (容器不是硬件实体)      │
  │  ├── L1/L2/L3: 所有容器共享                  │
  │  └── PMC: 容器进程的硬件事件混在一起         │
  └──────────────────────────────────────────────┘
```

#### 9.9.2 cgroup CPU 控制器的硬件实现

cgroup CPU 带宽控制的底层依赖 CFS 带宽调度器和硬件时钟：

```
cgroup CPU 带宽控制 (CFS Bandwidth Controller):

  cfs_quota_us = 50000  (50ms CPU 时间/周期)
  cfs_period_us = 100000 (100ms 周期)

  硬件实现:
    1. 每个 cgroup 维护: runtime = quota (50ms)
    2. 进程运行时: CFS tick (通过 hrtimer) 减少 runtime
       └── hrtimer 硬件: LAPIC Timer → ~1-10μs 精度
    3. runtime 耗尽 (runtime=0):
       └── CFS throttle → 进程进入 TASK_UNINTERRUPTIBLE
       └── 不调度 → 进程不占用 CPU
    4. 周期结束: runtime 重置 = quota
       └── hrtimer 触发 → 唤醒所有被节流的进程

  硬件精度:
    ├── hrtimer 精度: ~1μs (LAPIC Timer)
    ├── CFS 时间片: ~0.75ms (min_granularity)
    ├── 节流粒度: ~μs 级
    └── 实际带宽误差: <1% (高负载)
```

**cgroup cpuset 与物理 CPU 绑定**：

```bash
# cpuset 直接使用 CPU 硬件的亲和性机制
# Linux 内部: sched_setaffinity() → 设置进程的 CPU 亲和性掩码
# 硬件: 调度器只在允许的 CPU 集合中选择

# 创建 cpuset:
mkdir /sys/fs/cgroup/cpuset/container_A
echo 0-3 > /sys/fs/cgroup/cpuset/container_A/cpuset.cpus   # 物理 CPU 0-3
echo 0 > /sys/fs/cgroup/cpuset/container_A/cpuset.mems      # NUMA 节点 0
echo $PID > /sys/fs/cgroup/cpuset/container_A/tasks

# 硬件效果:
# 容器 A 中的进程只在 CPU 0-3 运行
# CPU 0-3 的 L1/L2/L3 缓存被容器 A 的进程共享
# ↔ CPU 4-7 完全不受影响 (缓存隔离)
# ↔ NUMA 节点 1 的内存不被分配 (mems 控制)
```

#### 9.9.3 Docker 的内存限制与硬件 OOM

```
cgroup memory.max = 1GB

硬件行为 (物理内存不足时):
  1. 容器 A 的内存使用达到 1GB 上限
  2. 内核通过 cgroup 的 memory 控制器:
     ├── 触发 direct reclaim (直接回收)
     ├── 或 kswapd 后台回收
     ├── 如果仍不足:
     │    └── 触发 OOM Killer (在该 cgroup 中)
     │    └── 选择 cgroup 中最"坏"的进程杀死
     │    └── 杀死后释放内存
     └── 整个 OOM 过程依赖:
          ├── CPU 页错误硬件 (#PF → 内核处理)
          ├── 物理内存分配 (buddy allocator)
          └── OOM Killer 选择标准 (oom_score_adj)

对比 VM (硬件级内存隔离):
  VM: EPT 缺页 → KVM → 从宿主物理内存分配
  VM 的 OOM: Guest 内核执行, 不影响 Host
  容器: 共享内核, OOM 在 Host 内核中执行
```

#### 9.9.4 seccomp 与系统调用过滤的硬件角度

seccomp-bpf 是 Docker 安全的核心，它限制容器进程可使用的系统调用：

```
seccomp 的执行路径 (硬件层面):

  用户态 (容器内进程):
    MOV RAX, SYS_open
    SYSCALL                    ──→ CPU 硬件切换 Ring 0
    │                                │
    ├── [无 seccomp]                 │
    │  → 直接执行系统调用             │
    │                                │
    └── [有 seccomp-bpf]             │
         → 内核安全框架拦截           │
         → 执行 BPF 过滤器            │
         → BPF 程序检查:              │
              ├── syscall number?     │
              ├── 参数检查?            │
              └── 返回: ALLOW/KILL/TRAP
                                      │
    SYSRET ──────────────────── CPU 硬件切换 Ring 3

  性能影响:
    ├── 无 seccomp: ~50-70 cycles (SYSCALL → handler → SYSRET)
    ├── seccomp-bpf: ~70-150 cycles (+BPF 执行)
    └── 对比: 大部分系统调用本身 ~100-1000 cycles
         → 增加 20-50% 的系统调用开销
         → 但系统调用占比低 (<1% CPU 时间)
         → 整体影响 <0.5%
```

#### 9.9.5 BPF JIT 编译与硬件执行

eBPF 程序在内核中被 JIT 编译为本地代码（硬件直接执行），这是容器网络/安全的核心：

```
eBPF 程序的硬件执行路径:

  BPF 字节码 (~BPF_MAXINSNS=4096 条指令):
    ┌─────────────────────────────────────┐
    │ BPF_MOV64_IMM(0, 1)                 │
    │ BPF_LDX_MEM(1, 0, 0)                │
    │ BPF_JMP_REG(BPF_JEQ, 1, 0, offset) │
    └─────────────────────────────────────┘
         │
         ▼
  BPF Verifier (软件, 保证安全性)
    ├── 检查无循环 (有界)
    ├── 检查指针安全 (无越界)
    ├── 检查辅助函数合法性
    └── 检查栈大小 (≤512 bytes)
         │
         ▼
  BPF JIT Compiler (硬件代码生成)
    └── x86-64 JIT: 将 BPF 指令翻译为 x86 指令
         ├── BPF_MOV64_IMM → movabs rax, imm64
         ├── BPF_JMP_REG    → cmp rax, rbx; jne target
         └── 结果: 直接由 CPU 流水线执行的本地代码

  性能对比 (网络包处理):
    ├── 纯软件 (iptables): ~1000 cycles/包
    ├── BPF 解释执行: ~200 cycles/包
    ├── BPF JIT 编译执行: ~50 cycles/包
    └── 硬件直接 (ASIC/DPU offload): ~10 cycles/包
```

### 9.10 性能监控硬件

#### 9.10.1 PMC (Performance Monitoring Counters)

PMC 是 CPU 中用于统计微架构事件的硬件计数器，每个进程的性能数据源于此：

```
每个逻辑 CPU 核拥有 ~2-8 个可编程 PMC:

PMC 寄存器:
  IA32_PERFEVTSELx (MSR 186-18D):
    Event Select (8 位) — 选择监控的事件类型
    Unit Mask (8 位) — 事件的子类型
    USR — 用户态计数
    OS — 内核态计数
    EN — 启用
    INT — 溢出时产生中断

  IA32_PMCx (MSR C1-C8):
    48 位计数器 (Ice Lake+)
    溢出时: 可触发 PMI (Performance Monitor Interrupt)

Linux perf_event 将 PMC 与进程关联:

  struct perf_event {
      struct hw_perf_event hw;  // 硬件 PMC 分配
      struct task_struct *task; // 绑定的进程
      // 进程切换时: 保存/恢复 PMC 值
      // ctx = perf_pmu_sched_task()
  };

  每个进程独立的 PMC 上下文:
    进程 A 运行 → PMC 计数 A
    上下文切换:
      → 保存进程 A 的 PMC 值到 task_struct
      → 加载进程 B 的 PMC 值到硬件寄存器
    进程 B 运行 → PMC 计数 B
    → 每个进程看到的是自己的硬件事件计数
```

**常用 PMC 事件与进程分析**：

| 事件名称 | Event Code | 含义 | 进程相关 |
|:---------|:----------:|:-----|:---------|
| CPU_CLK_UNHALTED.CORE | 0x3C | CPU 核心时钟周期 | 总 CPU 时间 |
| INST_RETIRED | 0xC0 | 退休指令数 | 指令吞吐 |
| LLC_MISSES | 0x2E, umask=0x41 | L3 缓存缺失 | 工作集大小 |
| DTLB_LOAD_MISSES | 0x08 | DTLB 缺失 | 进程访存模式 |
| BR_MISP_RETIRED | 0xC5 | 分支预测失败 | 分支密集程度 |
| MEM_LOAD_UOPS_RETIRED.L3_HIT | 0xD1, umask=0x04 | 从 L3 命中的加载 | 数据局部性 |

#### 9.10.2 LBR (Last Branch Record) —— 分支轨迹

LBR 记录 CPU 最近执行的分支（CALL/RET/JMP/COND_JMP）的源地址和目标地址：

```
LBR 硬件:
  ├── 深度: 8-32 条记录 (Ice Lake: 32 条)
  ├── 每条: FROM_IP + TO_IP (64 位地址)
  ├── 循环缓冲: 新记录覆盖最旧的
  └── 每 CPU 核独立

LBR 与进程/线程:
  ├── 可通过 MSR 切换 (保存/恢复)
  ├── perf record -b (分支采样):
  │    └── 每隔 N 次分支, 读取 LBR
  │    └── 得到采样点的函数调用路径
  ├── 用于:
  │    ├── 函数调用热点分析
  │    ├── JIT 编译优化 (发现未优化的热路径)
  │    └── 非预期分支检测 (安全)

LBR 样本示例 (进程热路径):
  FROM            TO             说明
  0x5555555a3f10  0x5555555a3f20  main+0x10 → calc_thing+0x0
  0x5555555a3f50  0x5555555a3f80  calc_thing+0x30 → inner_loop+0x0
  0x5555555a3fa0  0x5555555a3fa0  inner_loop+0x20 → inner_loop+0x20 (back-edge, 循环)
  ...重复了很多次...
  → 推断: hot loop 在 inner_loop 的 +0x20 处
```

#### 9.10.3 PEBS (Precise Event Based Sampling)

PEBS 解决了 PMC 采样的**指令偏差**问题——采样到的是真正的触发指令：

```
传统 PMC 采样 (中断驱动):
  PMC 溢出 → PMI → 读取 RIP → 记录
  问题: PMI 在溢出后若干指令才触发
        → 记录的 RIP 不准确 (偏移 ~数十指令)
        → "skid" (偏差) 问题

PEBS 硬件 (Nehalem+, 2008):
  PMC 溢出 → 硬件自动将精确状态保存到 PEBS 缓冲区:
    ┌──────────────────────────────────────┐
    │ PEBS 记录 (精确):                     │
    │   RIP (精确到触发指令)                 │
    │   General Purpose Registers           │
    │   RFLAGS, RSP                         │
    │   Memory Access Address (内存事件时)   │
    │   Latency Value (内存延迟)             │
    │   Data Source (数据来源: L1/L2/L3/DRAM)│
    └──────────────────────────────────────┘
  → 无 PMI (硬件写到用户空间内存)
  → 批量处理 (中断密度显著降低)

PEBS 对进程分析的价值:
  1. 精确热点定位 (误差 ~0 指令)
  2. 内存延迟分析:
     └── 性能关键: 哪个内存访问耗时最长?
     └── 使用 MEM_LOAD_UOPS_RETIRED.L3_MISS + PEBS
     └── 直接得到: 地址 X 的访问耗时 ~200ns (L3 miss)
  3. 每进程 PEBS:
     └── perf_event_open() 时绑定进程
     └── 进程切换时: PEBS 缓冲区切换
     └── 每个进程得到自己的精确采样数据
```

#### 9.10.4 Intel PT (Processor Trace) —— 指令级追踪

Intel PT 是最高精度的硬件追踪技术，可实现完整的指令流重建：

```
Intel PT (Broadwell+, 2014):

  硬件工作原理:
  ┌──────────────────────────────────────────────┐
  │ CPU 内部追踪逻辑 (无性能影响):                 │
  │ 记录: (非完整指令流, 而是分支信息)              │
  │   ├── 条件分支: TNT (Taken/Not Taken) 位      │
  │   ├── 无条件分支/调用/返回: TIP (Target IP)    │
  │   ├── 异步事件: 中断、异常                     │
  │   └── 定时器包 (基于 CPU TSC)                  │
  │                                                │
  │ 输出: Packet Stream → 内存缓冲区               │
  │   └── 每 ~4KB 产生中断 (非每指令)              │
  │                                                │
  │ 解码 (离线):                                   │
  │   1. 读取二进制可执行文件 (指令基础)             │
  │   2. 将 TNT 位逐位应用到条件分支                 │
  │   3. TIP 更新目标 IP                            │
  │   4. 重建完整指令流                              │
  └──────────────────────────────────────────────┘

Intel PT 与进程:
  ├── 支持每进程过滤 (PID 过滤器, 硬件比较)
  ├── 支持 CR3 过滤 (只跟踪特定进程的 CR3)
  ├── 输出到:
  │    ├── perf 环形缓冲区
  │    └── 或专用内存 (Linux 的 intel_pt pmu)
  └── 分析:
       └── 完整的指令追踪 (非采样, 100% 覆盖)
       └── 发现: 死循环、竞态条件、非预期崩溃路径
       └── 代价: 每核 ~数十 MB/s 的追踪数据流
```

---

## 参考来源

### 标准与规范
- [Intel 64 and IA-32 Architecture SDM Vol.3](https://www.intel.com/content/www/us/en/architecture-and-technology/64-ia-32-architectures-software-developer-system-programming-manual-325384.html) — 系统编程：任务管理、中断、页表、VMX、APIC
- [Intel 64 and IA-32 Architecture SDM Vol.3C](https://www.intel.com/content/www/us/en/architecture-and-technology/64-ia-32-architectures-software-developer-system-programming-manual-325384.html) — VMX (VT-x) 完整定义：VMCS/EPT/VPID/APICv
- [Intel VT-d Architecture Specification](https://www.intel.com/content/www/us/en/architecture-and-technology/virtualization-technology/intel-virtualization-technology-for-directed-io-vt-direct-specification.html) — IOMMU、DMA Remapping、Interrupt Remapping
- [AMD64 Architecture Programmer's Manual Vol.2](https://www.amd.com/en/developer/amd-architecture-programmers-manual.html) — SVM (AMD-V)、NPT (Nested Page Tables)
- [ARM Architecture Reference Manual (ARMv8-A)](https://developer.arm.com/architectures/cpu-architecture/a-profile) — ARM 虚拟化：Stage 2 translation、GICv3/4
- [IEEE Std 1003.1-2017 (POSIX.1-2017)](https://pubs.opengroup.org/onlinepubs/9699919799/) — 进程/线程/信号标准定义
- [PCI Express Base Specification Rev 6.0](https://pcisig.com/specifications) — SR-IOV、ATS、PASID
- [Linux man-pages](https://man7.org/linux/man-pages/) — clone(2), fork(2), ptrace(2), epoll(7), cgroups(7)

### 论文与技术报告
- [NPTL: The Native POSIX Thread Library for Linux (2003)](https://www.akkadia.org/drepper/nptl-design.pdf) — Ulrich Drepper, Red Hat
- [The Linux Scheduler: A Decade of Wasted Cores (EuroSys'16)](https://www.ece.ubc.ca/~sasha/papers/eurosys16.pdf) — 调度器延迟与 CFS 局限
- [Go: A Systems Language (2012)](https://talks.golang.org/2012/splash.article) — Go G-P-M 调度器与协程设计
- [Project Loom: A Peek Under the Hood (JDK 21)](https://cr.openjdk.org/~rpressler/loom/loom/sol1_lab.html) — Ron Pressler, Java Virtual Thread 设计
- [Erlang/OTP System Documentation](https://erlang.org/doc/system_architecture.html) — Actor 模型与监督树

### 工程实践与白皮书
- [The Go Memory Model](https://go.dev/ref/mem) — Go 内存模型与并发原语
- [Tokio Internals](https://tokio.rs/blog/2019-10-scheduler) — Rust 异步运行时调度器内幕
- [JVM Internals (JamesDB)](https://blog.jamesdbloom.com/JVMInternals.html) — JVM 线程模型与内存管理
- [Linux Kernel Development (Robert Love, 3rd Edition)](https://www.informit.com/store/linux-kernel-development-9780672329463) — task_struct, 调度器, 进程管理
- [Understanding the Linux Kernel (Bovet & Cesati, 3rd Edition)](https://www.oreilly.com/library/view/understanding-the-linux/0596005652/) — 进程/线程/中断/内存

### 官方文档
- [cgroup v2 Documentation (kernel.org)](https://www.kernel.org/doc/Documentation/cgroup-v2.txt) — Linux 资源控制
- [BPF and XDP Reference Guide (Cilium)](https://docs.cilium.io/en/latest/bpf/) — eBPF 调试与可观测性
- [OpenTelemetry Specification](https://opentelemetry.io/docs/specs/otel/) — 分布式追踪与资源关联

### 经典源代码
- Linux kernel: `include/linux/sched.h` — task_struct 定义
- Linux kernel: `kernel/sched/fair.c` — CFS 调度器实现
- Go runtime: `runtime/runtime2.go` — g/m/p 结构定义
- Go runtime: `runtime/proc.go` — goroutine 调度器核心
- Tokio: `tokio/src/runtime/scheduler/multi_thread/` — 工作窃取调度器

---

## 修订记录

| 版本 | 日期 | 修改内容 |
|:-----|:-----|:---------|
| v1.0 | 2026-06-30 | 初版创建。8 章系统活动任务载体深度分析：概念体系、资源模型框架（8 类资源+所有权模型）、四层实现(OS/运行时/VM/框架)、生命周期、可靠性、依赖拓扑、调试可观测性、跨层对比矩阵。~1000 行 |
| v2.0 | 2026-06-30 | 新增第 9 章「CPU 硬件架构对进程/线程/虚拟化的深度支持」~800 行。10 节深度覆盖：页表遍历与TLB硬件(page walker/PCID/大页/5级页表)、上下文切换硬件链路(TSS/IST/FS-GS TLS/XSAVE)、特权级切换(SYSCALL硬件路径/RDTSC)、中断异常硬件路径(IDT/#PF/#MCE)、APIC中断分发(LAPIC/IPI/x2APIC)、缓存与进程亲和性(CAT/CMT/MBM)、硬件虚拟化(VMX/VMCS/EPT/VPID/APICv)、IOMMU设备隔离(VT-d/SR-IOV/VFIO)、Docker硬件视角(cgroup硬件实现/seccomp硬件路径/BPF JIT)、性能监控硬件(PMC/LBR/PEBS/Intel PT)。全文档从纯软件视角扩展为软硬件全链拉通。~1800 行 |
