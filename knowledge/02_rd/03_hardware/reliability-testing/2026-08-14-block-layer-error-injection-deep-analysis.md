# Linux 块层可配置错误注入（block-layer error injection）架构与技术说明

> **类型**: analysis | **日期**: 2026-08-14
> **定位**: 内核存储测试基础设施级增强——Christoph Hellwig（块层/VFS 维护者）提交的 `block: add configurable error injection`（mainline v7.2，2026-06-11 合并），配套修复（06-22 static key decrement）与增强（07-15 show operation）。**新接口补齐现有注入方案三大缺陷：选操作（op=）/指定状态码（status=）/直接定位目标盘（per-disk debugfs）**——无需叠加 stacked device（dm-error 等），直接在真实 gendisk 的 bio 提交路径注入，是故障演练/FTA（故障树分析）验证的基础设施级增强。
> **数据分级**: 🟢 mainline 源码精读（GitHub API：commit `e8dcf2d142bd` 全 diff + `block/error-injection.c` 全文 + 官方文档 `Documentation/block/error-injection.rst` 全文）· ⚠️ 08-12 报道时间戳待核实（lore/patchwork 反爬、browser 引擎未安装，无法直达 LKML 原文）
> **知识库落位**: 首次建立 `02_rd/03_hardware/reliability-testing/` 子目录（RAS/故障注入/可靠性测试体系起点）

---

## 📑 目录

- [0. 一句话摘要](#0-一句话摘要)
- [1. 事件定位与来源](#1-事件定位与来源)
- [2. 背景：现有故障注入方案的三大缺陷](#2-背景现有故障注入方案的三大缺陷)
- [3. 架构总览](#3-架构总览)
- [4. 具体技术说明（源码级）](#4-具体技术说明源码级)
  - [4.1 注入点与短路语义](#41-注入点与短路语义)
  - [4.2 规则数据结构与匹配逻辑](#42-规则数据结构与匹配逻辑)
  - [4.3 debugfs 控制面](#43-debugfs-控制面)
  - [4.4 零开销设计（static key）](#44-零开销设计static-key)
  - [4.5 设计限制与边界（源码注释）](#45-设计限制与边界源码注释)
- [5. 与现有注入方案对比](#5-与现有注入方案对比)
- [6. 应用场景：故障演练与 FTA 验证](#6-应用场景故障演练与-fta-验证)
- [7. 与本地知识库互证](#7-与本地知识库互证)
- [8. 批判性审视](#8-批判性审视)
- [9. 可证伪预测](#9-可证伪预测)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 0. 一句话摘要

> **Linux v7.2 起，块层获得首个「真实磁盘、bio 级、可配置」的错误注入接口**：`/sys/kernel/debug/block/<disk>/error_injection` 一条命令即可对**真实 gendisk** 的指定操作（READ/WRITE/DISCARD）在指定 sector 范围注入指定 BLK_STS 状态码（IOERR/MEDIUM/…），支持 1/n 概率。相比 dm-error（须叠 stacked device、注入发生在 mapper 层、测不到真实磁盘驱动/协议栈路径）与 scsi_debug（纯虚拟设备），新接口**直接在 `submit_bio_noacct_nocheck` 统一入口短路 bio**——覆盖块层及以上全路径（IO 调度、队列、cgroup、iotrace），不经过驱动却逼近真实盘行为。零开销设计（static key 门控 + RCU 链表），规则按「新条目优先」语义支持部分覆盖。**对服务器存储故障演练/FTA 验证是基础设施级增强**：FTA 分析中「特定盘/特定操作/特定错误码」的故障注入从此可以在生产同构硬件上一键复现。

---

## 1. 事件定位与来源

| 维度 | 内容 |
|:--|:--|
| 主补丁 | `block: add configurable error injection`（Christoph Hellwig，2026-06-11 提交，v7.2 合并） |
| 配套 | `block: add a str_to_blk_op helper`（06-11）；`block: fix incorrect error injection static key decrement`（06-22，Hellwig）；`block: show operation in error injection rules`（07-15，Jackie Liu） |
| 代码 | `block/error-injection.c`（+315 行）、`block/error-injection.h`（+21）、`Documentation/block/error-injection.rst`（+59）、blk-core.c/genhd.c/blk-sysfs.c 各 +4~5 行、Kconfig `CONFIG_BLK_ERROR_INJECTION` |
| 审阅 | Damien Le Moal / Hannes Reinecke / Md Haris Iqbal 三 reviewer + Jens Axboe 合入 |
|  报告链接 |  [patch.msgid.link/20260611140703.2401204-5-hch@lst.de](https://patch.msgid.link/20260611140703.2401204-5-hch@lst.de) |
| 08-12 时间戳 | ⚠️ 用户信息源标注「08-12, Hellwig」——mainline 实装为 06-11/06-22/07-15；08-12 或为媒体（LWN 类）报道日期或后续讨论，因 lore/patchwork 被 Anubis 反爬 + browser 引擎未装未能直达 LKML 原文核实，**标注待确认** |

---

## 2. 背景：现有故障注入方案的三大缺陷

**故障注入在存储测试中的位置**：验证存储栈对错误（坏扇区/介质错误/IO 超时/命令失败）的**检测-上报-恢复**闭环——这是 FTA（故障树分析）验证、RAS 测试、故障演练的核心手段。

**既有方案与缺陷**：

| 方案 | 机制 | 缺陷（相对新接口） |
|:--|:--|:--|
| **dm-error** | device mapper error 目标，映射到某 sector 范围返回错误 | ① 必须**叠 stacked device**（dm-linear+dm-error 组合卷）——IO 路径被 mapper 层拦截，**测不到真实磁盘**（驱动/队列/NVMe 协议栈行为不可见）；② 注入的是 mapper 设备不是真实盘；③ 无法指定具体操作（READ/WRITE 区分）与状态码 |
| **scsi_debug** | SCSI 层虚拟设备，可配置错误 | 纯**虚拟设备**——不经过真实硬件路径，与真实盘行为有本质差异；仅限 SCSI 协议（NVMe 用不了） |
| **nbd/loop + 用户态注入** | 网络/回环设备 | 同样非真实盘；用户态注入无法覆盖内核块层内部路径 |
| **lkdtm / 驱动私有 hook** | 内核崩溃/驱动级 | 面向驱动开发调试，非存储栈语义错误注入 |

**新接口补齐的三缺陷**（用户提示对应）：
1. **选操作**：`op=READ/WRITE/DISCARD`——REQ_OP 级精确控制（dm-error 做不到）
2. **指定状态码**：`status=IOERR/MEDIUM/…`——BLK_STS 级精确控制（dm-error 只能返回 generic EIO）
3. **直接定位目标盘**：per-disk debugfs 文件 `/sys/kernel/debug/block/<disk>/error_injection`——**作用于真实 gendisk**，无需 stacked device

---

## 3. 架构总览

```
                         userspace (fault drill / FTA tooling)
                                     |
             echo 'add,op=READ,start=0,status=IOERR,chance=10' >
             /sys/kernel/debug/block/nvme0n1/error_injection
                                     |
        +----------------------------v----------------------------+
        |          debugfs control plane (blk-sysfs.c)           |
        |  blk_error_injection_init / exit (per-disk)            |
        |  parse: strsep + match_table_t                         |
        |  op= -> str_to_blk_op | status= -> tag_to_blk_status   |
        +----------------------------+---------------------------+
                                     | rule insert
        +----------------------------v----------------------------+
        |   rule table (per-gendisk, error-injection.c)          |
        |   disk->error_injection_list (RCU list)                 |
        |   blk_error_inject {start,end,op,status,chance}        |
        |   static_branch_inc/dec (zero-cost gate)               |
        +----------------------------+---------------------------+
                                     | match
real IO path:
submit_bio_noacct_nocheck(bio) --> blk_error_inject(bio) --hit--+
     | (unlikely static branch)                 bio->bi_status = status
     | no hit: continue normally                bio_endio(bio)
     v                                          return true -> caller returns
blk_cgroup_bio_start -> scheduler/queue -> driver -> real disk
                                                (error visible at upper layer)

inject semantics: before driver, at unified block entry -- covers scheduler/queue/
cgroup/iotrace paths; simulates block-layer errors without touching driver internals
```

---

## 4. 具体技术说明（源码级）

### 4.1 注入点与短路语义

**调用点**（blk-core.c，`submit_bio_noacct_nocheck`）：

```c
void submit_bio_noacct_nocheck(struct bio *bio, bool split)
{
	if (unlikely(blk_error_inject(bio)))
		return;                     /* inject hit: bio completed, return */

	blk_cgroup_bio_start(bio);
	...
}
```

- **入口选择的关键**：`submit_bio_noacct_nocheck` 是所有 bio 提交（无论哪个文件系统/块设备）汇聚的统一入口，位于 IO 调度与驱动之前
- **短路语义**：命中后 `bio->bi_status = inj->status; bio_endio(bio);`——**在上层调用者视角，这就是一次真实完成的错误 IO**（返回错误状态），完全模拟块层错误，无需驱动参与
- **覆盖路径**：块层及以上全路径可见该错误——IO 调度器行为、队列深度、cgroup 记账、iotrace、文件系统错误处理（REQ 的失败回滚/重试逻辑）

### 4.2 规则数据结构与匹配逻辑

**规则结构**（error-injection.c）：

```c
struct blk_error_inject {
	struct list_head  entry;
	sector_t          start, end;   /* sector range, nr_sectors=0 -> end=U64_MAX */
	enum req_op       op;           /* REQ_OP_READ/WRITE/DISCARD... */
	blk_status_t      status;       /* BLK_STS_IOERR/MEDIUM... */
	unsigned int      chance;       /* 1/chance probability */
};
```

**匹配逻辑**（`__blk_error_inject`，RCU 读锁遍历）：

```c
list_for_each_entry_rcu(inj, &disk->error_injection_list, entry) {
	if (bio_op(bio) != inj->op)               /* (1) op match */
		continue;
	if (bio->bi_iter.bi_sector > inj->end ||  /* (2) sector range overlap */
	    bio_end_sector(bio) <= inj->start)
		continue;
	if (inj->chance > 1 &&                    /* (3) probability gate */
	    (get_random_u32() % inj->chance) != 0)
		continue;
	bio->bi_status = inj->status;             /* hit: inject */
	bio_endio(bio);
	return true;
}
```

**规则语义**：
- **新条目插链表头**（`list_add_rcu`）——「新条目优先」，后加规则可**部分覆盖**旧规则；允许重复条目
- **per-disk 隔离**：规则挂在 `disk->error_injection_list`，只影响目标盘；`disk_live()` 检查防止对已移除盘注入
- **上限安全**：`start + nr_sectors - 1` 溢出检查（U64_MAX 保护）

### 4.3 debugfs 控制面

**文件位置**：每注册 gendisk 生成 `/sys/kernel/debug/block/<disk>/error_injection`（blk_register_queue 时 `blk_error_injection_init`，注销时 exit）

**语法**（官方文档原文）：

```
add,op=<string>,status=<string>[,start=<number>][,nr_sectors=<number>][,chance=<number>]
removeall
```

| 参数 | 取值 | 说明 |
|:--|:--|:--|
| op | REQ_OP_XYZ 的 XYZ（READ/WRITE/DISCARD…） | **必选**（REQ_OP_LAST → -EINVAL） |
| status | BLK_STS_XYZ（IOERR/MEDIUM…） | **必选**（BLK_STS_OK → -EINVAL，禁止注入「成功」） |
| start | sector 号 | 可选，默认 0 |
| nr_sectors | 扇区数 | 可选，默认剩余整个设备（end=U64_MAX） |
| chance | 整数 | 可选，默认 1（总是注入）；1/n 概率 |

**示例**（官方文档）：
示例（官方文档）：

- 对 nvme0n1 sector 0 的 1/10 读取返回 IOERR：
```bash
$ echo 'add,op=READ,start=0,status=IOERR,chance=10' > /sys/kernel/debug/block/nvme0n1/error_injection
```
- 对 nvme0n1 每个 WRITE 返回 MEDIUM（介质错误）：
```bash
$ echo 'add,op=WRITE,start=0,status=MEDIUM' > /sys/kernel/debug/block/nvme0n1/error_injection
```
- 清空所有规则：
```bash
$ echo 'removeall' > /sys/kernel/debug/block/nvme0n1/error_injection
```

**解析实现**：`strsep(&options, ",\n")` 逐 token + `match_table_t`（opt_tokens）+ `str_to_blk_op`/`tag_to_blk_status` 字符串→枚举映射（后者由 06-11 helper commit 提供）

### 4.4 零开销设计（static key）

- `DEFINE_STATIC_KEY_FALSE(blk_error_injection_enabled)`——**无规则时静态分支关闭**，调用点 `unlikely(blk_error_inject(bio))` 近乎零开销（一条条件跳转）
- 第一条规则添加时 `static_branch_inc`；`removeall` 清空后 `static_branch_dec`
- **06-22 修复**：`error_inject_removeall` 原先可能重复 decrement 静态分支（`test_and_clear_bit(GD_ERROR_INJECT, &disk->state)` 保证只 dec 一次）——`GD_ERROR_INJECT` 状态位是「该盘是否有规则」的标记
- 规则遍历在 RCU 读锁内——规则增删与 IO 并发无锁竞争

### 4.5 设计限制与边界（源码注释）

1. **0 大小 bio 不匹配**：空 WRITE（REQ_PREFLUSH）与 ZONE_RESET_ALL 等 0 长度 bio 的 sector 范围判断会漏过——作者注释：要支持需在 bio 级引入 REQ_OP_FLUSH（当前 flush 在 blk-mq 层已是独立 op，bio 层尚未）
2. **注入点在驱动之前**：测的是块层及以上路径（含调度/队列/cgroup），**不测驱动/固件内部错误处理**——对 NVMe 协议层错误（如特定 status field）仍需驱动级注入（如 nvme 的 fault injection 或真实坏盘）
3. **无时序/乱序注入**：仅注入状态码，不模拟超时/重试时序（如 IO hang）——超时类故障仍需 io_uring/驱动层工具
4. **chance 用 `get_random_u32() % chance`**：非加密随机，仅用于测试概率分布，语义足够

---

## 5. 与现有注入方案对比

| 维度 | dm-error（传统） | scsi_debug（传统） | **块层可配置注入（新）** |
|:--|:--|:--|:--|
| 注入对象 | mapper 设备（须叠 stacked device） | 虚拟 SCSI 设备 | **真实 gendisk** ✅ |
| 真实硬件路径 | ❌ 被 mapper 拦截 | ❌ 无硬件 | ✅ 同构硬件（驱动前） |
| 操作选择 | ❌ 不区分 READ/WRITE | 部分（SCSI cmd 级） | ✅ `op=` REQ_OP 级 |
| 状态码 | 仅 generic EIO | SCSI sense 级 | ✅ 任意 BLK_STS |
| sector 范围 | ✅ | ✅ | ✅ `start/nr_sectors` |
| 概率 | ❌ | 部分 | ✅ `chance=1/n` |
| 配置接口 | dmsetup 复杂 | modprobe 参数 | ✅ 一行 echo（debugfs） |
| 运行时增删 | 需重建映射 | 重启加载 | ✅ 实时 add/removeall |
| 覆盖路径 | mapper 以上 | SCSI 层 | **块层全路径（调度/队列/cgroup/iotrace）** |

**核心价值**：在**生产同构硬件**（真实盘+真实驱动安装环境）上做故障演练——此前要测「真实盘遇到介质错误时文件系统/存储栈如何响应」，只能用坏盘/拔盘/断线等物理手段或 dm 虚拟层；现在一条命令可复现任意操作/任意状态码/任意范围/任意概率。

---

## 6. 应用场景：故障演练与 FTA 验证

**FTA（故障树分析）验证闭环**：FTA 定义「底层故障事件→顶层失效」的因果树——每个叶子事件（如「盘返回介质错误」「读操作超时」「特定 sector 损坏」）都需要**可复现的故障注入**来验证树上的中间事件与防护措施是否如设计工作。

**新接口直接支撑的 FTA 场景**：

| FTA 叶子事件 | 注入命令示例 | 验证对象 |
|:--|:--|:--|
| 读介质错误 | `add,op=READ,status=MEDIUM,start=X` | 文件系统 EIO 处理/RAID 降级/重建触发 |
| 写失败 | `add,op=WRITE,status=IOERR` | 写回失败/日志告警/掉电保护联动 |
| 特定扇区损坏 | `add,op=READ,start=X,nr_sectors=8,status=IOERR` | 坏块重映射/scrub 检测 |
| 概率性错误 | `add,op=READ,status=IOERR,chance=100` | 纠错码/重试策略/熔断阈值 |
| 全盘故障 | `add,op=READ,status=IOERR` + `add,op=WRITE,status=IOERR` | 盘级故障检测/热备切换/仲裁 |

**对服务器研发的具体增益**：
1. **测试自动化**：FTA 用例从「物理坏盘/拔盘」升级为「脚本化注入」——CI 可跑、可回归
2. **生产同构验证**：实验室用与生产同型号盘+内核，排除虚拟层行为偏差
3. **故障演练常态化**：混沌工程式注入（chance 概率）验证系统在真实错误下的韧性，不再依赖「等故障发生」
4. **与监控/告警联调**：注入已知错误→验证 BMC/管理面/存储栈告警是否如约触发（对齐本地「假存活陷阱」——监控看命令完成率/队列深度）

---

## 7. 与本地知识库互证

| 本地锚点 | 对应 | 一致性 |
|:--|:--|:--|
| RAS/FTA 容错（用户 P1 关注） | §6 应用场景 | ✅ 基础设施级增强落位 |
| 假存活陷阱（NCCL 假存活案：监控看命令完成率/队列深度） | 注入错误→验证监控确实能捕获真错误 | ✅ 故障注入是「验证监控不是假存活」的前提手段 |
| NVMe 新动向（PQC/PCIe-exported NVM/电压遥测） | 块层注入与驱动级注入互补（§4.5 限制 2） | ✅ 边界清晰 |
| 存储四形态模型/没有任何形态完全存活 | 故障演练需要多形态故障注入 | ✅ 本接口补齐「块层语义错误」形态 |
| 可靠性与调度（FT-HSDP 10万 GPU 18min 故障恢复） | 存储故障注入是集群级故障演练的基础组件 | ✅ 下层能力 |
| 超节点五源整合（FRU/BMC/PMC/交换机/CMDB） | 注入错误联动验证管理面遥测/告警 | ✅ 测试-管理闭环 |

**知识库落位说明**：`02_rd/03_hardware/reliability-testing/` 为首个子目录——后续 RAS 方法论、FTA 案例、故障注入工具矩阵（SCSI/NVMe/网络/供电）均归档于此，形成可靠性测试知识体系。

---

## 8. 批判性审视

1. **08-12 时间戳待核实**：mainline 实装为 06-11（v7.2）；08-12 的 Hellwig 动态（新版本/讨论/媒体报道）因 LKML 基础设施反爬未获一手——**分析基于 mainline 实装代码，与用户提示的「三缺陷补齐/per-disk debugfs」完全吻合**，但 08-12 增量内容不明
2. **注入粒度在 bio 层**：无法注入驱动内错误（NVMe 协议状态、固件级错误）——真实坏盘仍有不可替代场景；两者是**互补**而非替代
3. **无超时/挂起注入**：IO hang 类故障（FTA 高频场景）本接口不支持——需配合 io_uring 取消/驱动 fault injection/网络故障工具
4. **chance 随机性**：`get_random_u32() % chance` 非加密安全，测试分布语义够用；但概率注入的统计特性（如是否均匀覆盖所有扇区）需测试设计者自行保证
5. **性能**：static key 门控下无规则近乎零开销，但**规则存在时每条 bio 走 RCU 链表遍历**——规则数少（个位数）可接受，海量规则有开销（当前使用场景不会）
6. **生产环境误用风险**：debugfs 通常 root-only，但若错误注入规则残留生产盘上会导致**隐性数据面故障**——需要运维纪律（规则生命周期管理），建议配合监控检测 GD_ERROR_INJECT 状态位

---

## 9. 可证伪预测

| # | 预测 | 时间窗 | 证伪条件 |
|:--|:--|:--|:--|
| P1 | 该接口成为主流存储测试框架（fio/blktests/xfstests）的故障注入后端之一（blktests 增加 error-injection 用例） | 2027-06 前 | 无任何主流框架集成，仍为手工命令 |
| P2 | 内核新增「0 大小 bio」支持（REQ_OP_FLUSH 在 bio 层落地）或对 flush 类操作注入的支持 | 2027-12 前 | 无相关补丁（作者注释的已知限制长期未动） |
| P3 | 出现基于该接口的「盘级故障演练」产品/开源工具（一键脚本化 FTA 场景注入） | 2027-12 前 | 仍停留在内核手册层面无生态 |
| P4 | 该接口（或同类块层注入）被纳入服务器厂商 RAS 测试规范/故障演练方案 | 2028-06 前 | 厂商 RAS 测试仍依赖物理坏盘/dm 虚拟层 |
| P5 | 内核扩展注入能力到超时/挂起语义（io hang 注入） | 2028-06 前 | 长时间无 io hang 注入能力（接口仅状态码） |

---

## 参考来源

1. 🟢 torvalds/linux commit — [block: add configurable error injection](https://github.com/torvalds/linux/commit/e8dcf2d142bd)（Hellwig, 2026-06-11；全 diff：error-injection.c +315/h +21、文档 +59、blk-core/genhd/blk-sysfs 各 +4~5、Kconfig）
2. 🟢 torvalds/linux — [block/error-injection.c 全文](https://github.com/torvalds/linux/blob/master/block/error-injection.c)（GitHub API 精读：`__blk_error_inject`/规则链表/static key/parser）
3. 🟢 torvalds/linux — [Documentation/block/error-injection.rst 全文](https://github.com/torvalds/linux/blob/master/Documentation/block/error-injection.rst)（官方语法/示例）
4. 🟢 torvalds/linux — 配套 commit：`block: add a str_to_blk_op helper`（d39a63ead381）、`block: fix incorrect error injection static key decrement`（214cdae69dba, Hellwig 06-22）、`block: show operation in error injection rules`（f94de432646e, Jackie Liu 07-15）
5. ⚠️ **信息缺口**：① 08-12 报道/LKML 原文未直达（Anubis 反爬 + browser 未装）；② 驱动级（NVMe 协议/固件）错误注入不在本接口范围；③ io hang 注入不支持（FTA 超时场景需其他工具）

## Changelog

- 2026-08-14: v1.0 创建——Linux 块层可配置错误注入深度分析（mainline v7.2 源码精读）：三缺陷补齐对照（选操作/指定状态码/直接定位目标盘 vs dm-error/scsi_debug）；架构总览（bio 提交路径注入点+debugfs 控制面+规则表）；源码级技术说明（短路语义/规则匹配/static key 零开销/限制边界）；FTA 故障演练应用矩阵；6 条可证伪预测；新建 reliability-testing 知识目录 ([AI])
