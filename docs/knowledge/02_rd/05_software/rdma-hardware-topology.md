# RDMA 硬件管理与网络拓扑查看

> 操作手册：[RDMA 架构理论](rdma-architecture.md) → 硬件管理实践
> 来源: [johng.cn](https://johng.cn/ai/rdma-hardware-topology) | 归档: 2026-06-04

---

## 🎯 核心定位

RDMA 集群运维的实操工具指南，覆盖 **InfiniBand** 和 **RoCE** 两种场景下的硬件信息查看和拓扑发现。

---

## 📊 三大工具一览

| 工具 | 适用场景 | 核心功能 | 范围 | 来源 |
|:----|:---------|:---------|:-----|:-----|
| **`ibv_devinfo`** | InfiniBand / RoCE | 查看本节点 RDMA 设备详情 | 单节点 | `libibverbs-utils` |
| **`ibnetdiscover`** | InfiniBand | 查询 IB 子网全网拓扑 | **全集群** | `infiniband-diags` |
| **`lldpctl`** | RoCE (Ethernet) | 查看本节点 ↔ 直连交换机单跳拓扑 | **单跳**（仅本节点） | `lldpd` |

---

## 1️⃣ InfiniBand 场景

### 1.1 PCI 设备信息

```bash
# 查看 InfiniBand 网卡
lspci | grep -iE "InfiniBand|Mellanox"
```

典型输出（8卡节点 × 各配 1 张 ConnectX-7 双口 IB 卡 + 1 张 ConnectX-4 Lx 管理网卡）：

```
29:00.0 Infiniband controller: Mellanox MT2910 Family [ConnectX-7]
3b:00.0 Infiniband controller: Mellanox MT2910 Family [ConnectX-7]
4b:00.0 Infiniband controller: Mellanox MT2910 Family [ConnectX-7]
5d:00.0 Infiniband controller: Mellanox MT2910 Family [ConnectX-7]
98:00.0 Ethernet controller: Mellanox MT27710 Family [ConnectX-4 Lx]   ← 管理口
98:00.1 Ethernet controller: Mellanox MT27710 Family [ConnectX-4 Lx]   ← 管理口
ab:00.0 Infiniband controller: Mellanox MT2910 Family [ConnectX-7]
bb:00.0 Infiniband controller: Mellanox MT2910 Family [ConnectX-7]
cb:00.0 Infiniband controller: Mellanox MT2910 Family [ConnectX-7]
db:00.0 Infiniband controller: Mellanox MT2910 Family [ConnectX-7]
```

### 1.2 NFD 自动标签

→ 详见 [NFD & GFD 实践](nfd-gfd.md)

如果集群安装了 NFD，自动打上如下标签：

| 标签 | 含义 |
|:-----|:------|
| `rdma.available: "true"` | RDMA 资源可被 K8S 调度使用 |
| `rdma.capable: "true"` | 节点硬件具备 RDMA 能力 |
| `pci-10de.present: "true"` | NVIDIA GPU 设备存在 |
| `pci-10de.sriov.capable: "true"` | GPU 支持 SR-IOV |
| **`pci-15b3.present: "true"`** | **Mellanox 网卡存在**（0x15b3） |
| `pci-15b3.sriov.capable: "true"` | Mellanox 网卡支持 SR-IOV |
| `pci-1a03.present: "true"` | ASPEED BMC 管理芯片存在 |

### 1.3 RDMA 设备详情（ibv_devinfo）

```bash
ibv_devinfo
```

输出解读以 `mlx5_0` 为例：

```yaml
hca_id:   mlx5_0              # HCA设备ID
transport:  InfiniBand (0)    # 传输协议: InfiniBand
fw_ver:    28.39.4082         # 固件版本
node_guid: b8e9:2403:0045:99fe  # 全局唯一标识符
vendor_id: 0x02c9             # 厂商: Mellanox/NVIDIA
vendor_part_id: 4129          # 产品: ConnectX-7
phys_port_cnt: 1              # 物理端口数
port: 1
  state:     PORT_ACTIVE (4)  # 活跃(4) | 关闭(1)
  active_mtu: 4096 (5)        # 4096字节
  sm_lid:     75              # 子网管理器LID
  port_lid:   5               # 本端口LID（子网路由用）
  link_layer: InfiniBand      # 链路层
```

**状态判断**：
- `PORT_ACTIVE (4)` + `sm_lid > 0` + `port_lid < 65535` → ✅ 正常连接
- `PORT_DOWN (1)` + `sm_lid: 0` + `port_lid: 65535` → ❌ 链路未连接或禁用

### 1.4 全网拓扑发现（ibnetdiscover）

```bash
# 任意一个 IB 节点执行即可获取全网拓扑
ibnetdiscover
```

无需部署代理，直接查询子网管理器（SM）中维护的全集群拓扑表。

#### 输出结构解读

```
# ====== 交换机 ======
Switch 65 "S-b0cf0e0300d66c80"     # 端口总数65
  "MF0;DCXNYD-IB03-D1F2-D207-F08-U45:MQM9700/U1"  # 机架位置+型号
  lid 2  lmc 0

  # 交换机端口 → 主机映射
  [1] "H-b8e924030045aaae"[1]     # 端口1 → 主机GUID [端口号]
      "msxf-hpc-37-1-ai mlx5_0"   # 主机名 + 设备名
      lid 71  4xNDR               # 主机LID + 连接速率(NDR=400Gbps×4)

  [2] "H-b8e924030045981e"[1]
      "msxf-hpc-37-1-ai mlx5_2"   # 同一台主机另一张IB卡
      lid 73  4xNDR

  # ... 共16个主机端口 + 1个聚合节点端口(65)

# ====== 主机HCA ======
Ca 1 "H-b8e924030045b536"
  "msxf-hpc-37-4-ai mlx5_8"
  [1](b8e924030045b536) "S-b0cf0e0300d66c80"[16]   # ← 连到交换机端口16
  lid 11  4xNDR
```

**关键信息**：
| 字段 | 含义 |
|:-----|:------|
| `S-xxx` | 交换机 GUID |
| `H-xxx` / `msxf-hpc-37-1-ai` | 主机名 |
| `mlx5_0` | HCA 设备名（RDMA 设备） |
| `[1] → [16]` | 交换机端口1 → 主机，主机端口1 → 交换机端口16 |
| `4xNDR` | 速率：NDR(400Gbps) × 4 通道 |
| `lid 71` | 子网内路由 LID |

#### 拓扑可视化示例

基于 ibnetdiscover 输出可还原出拓扑：

```
┌──────────────────────────────────────────────────────┐
│              MQM9700 Switch (65 ports)               │
│ LID: 2  │  GUID: b0cf0e0300d66c80                   │
├──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬───┤
│1 │2 │3 │4 │5 │6 │7 │8 │9 │10│11│12│13│14│15│16│...│65│
├──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴───┤
│H1 H1 H1 H1 H2 H2 H2 H2 H3 H3 H3 H3 H4 H4 H4 H4    AG│
│m0 m2 m8 m6 m0 m2 m6 m8 m0 m2 m6 m8 m0 m2 m6 m8      │
└──────────────────────────────────────────────────────┘

4 台机器 × 4 HCA/台 = 16 个 IB 端口 → 1 台 MQM9700 交换机
聚合节点（Aggregation Node）挂在端口 65
```

---

## 2️⃣ RoCE 场景

### 2.1 PCI 设备信息

```bash
lspci | grep -iE "InfiniBand|Mellanox"
# 输出显示为 Ethernet controller，不再是 InfiniBand controller
d8:00.0 Ethernet controller: Mellanox MT27710 Family [ConnectX-4 Lx]
d8:00.1 Ethernet controller: Mellanox MT27710 Family [ConnectX-4 Lx]
```

### 2.2 NFD 标签

与 IB 场景的 NFD 标签相同：

```
feature.node.kubernetes.io/rdma.available: "true"
feature.node.kubernetes.io/rdma.capable: "true"
feature.node.kubernetes.io/pci-15b3.present: "true"
feature.node.kubernetes.io/pci-15b3.sriov.capable: "true"
```

### 2.3 RDMA 设备详情（ibv_devinfo）

```bash
ibv_devinfo
```

RoCE 设备输出示例：

```yaml
hca_id:  rocep216s0f0         # 命名: roce + PCI地址 + 功能号
transport:  InfiniBand (0)    # ⚠️ 仍显示 InfiniBand（RoCE使用IB协议栈上层）
fw_ver:    14.32.1010
vendor_part_id: 4117          # ConnectX-4 Lx
port: 1
  state:     PORT_ACTIVE (4)
  active_mtu: 1024 (3)        # 实际MTU 1500（以太网标准）
  sm_lid:     0               # ❌ 无子网管理器
  port_lid:   0               # ❌ 无LID寻址（使用MAC/IP）
  link_layer: Ethernet        # ✅ 关键区别：链路层为以太网
```

> **常见疑问**：`transport: InfiniBand (0)` 与 `link_layer: Ethernet` 不矛盾吗？
> 不矛盾。IB 是一套完整的 RDMA 协议标准，RoCE 属于 IB 协议体系，底层传输介质换为以太网。上层协议逻辑、交互规则、Verbs 接口与物理 IB 网卡完全一致。

> **双口网卡为何只看到一个 `ibv_devinfo` 条目？**
> Mellanox 双口网卡在 RDMA 驱动层被识别为 **一个 HCA 主设备**，两个物理网口是主设备下的子端口。如果只显示 `phys_port_cnt: 1`，说明只启用了一个端口的 RDMA 功能，另一个端口要么物理未插线/链路 Down，要么 RDMA 未启用。

### 2.4 Ethernet 拓扑信息（lldpctl）

RoCE 基于以太网 → 通过 **LLDP (Link Layer Discovery Protocol)** 发现拓扑。

#### 安装

```bash
apt install lldpd
```

#### 使用

```bash
lldpctl
```

#### 局限性

⚠️ **只能探测单跳拓扑**：本机网卡 ↔ 直连交换机。无法看到：
- 其他节点的拓扑
- 交换机之间的级联关系
- 跨节点的网络关系

#### 输出解读

```yaml
Interface: ens64f0np0, via: LLDP, RID: 1

Chassis:
  ChassisID: mac ec:cd:4c:e3:09:9c
  SysName:   DCXNYD-DMXCS-LEAF21_D1F2-D207-A09-U45-U43  # 交换机名
  SysDescr:  H3C S6850-56HF            # 交换机型号
  MgmtIP:    10.112.30.254             # 管理IP

Port:
  PortID:    ifname Twenty-FiveGigE2/0/1  # 交换机端口
  PortDescr: Twenty-FiveGigE2/0/1 Interface
  VLAN:      900, pvid: yes               # VLAN ID=900

PMD:
  MAU oper type: 25GbaseSR                # 25G短距多模光纤
```

---

## 3️⃣ 工具适用范围对比

| 能力 | `ibnetdiscover` (IB) | `lldpctl` (RoCE) |
|:-----|:--------------------:|:----------------:|
| 全集群拓扑 | ✅ 任意节点获取全网 | ❌ 只能看本机直连 |
| 交换机级联关系 | ✅ | ❌ |
| 跨节点拓扑 | ✅ | ❌ |
| 交换机型号信息 | ✅ 需解析MF0描述 | ✅ |
| 链路速率 | ✅ 精确(4xNDR) | ✅ (MAU oper type) |
| VLAN | ❌ (L2 LID寻址) | ✅ (VLAN ID) |
| 故障依赖 | 依赖SM存活 | 依赖lldpd服务 |
| 是否需要部署代理 | ❌ 无需（查询SM） | ✅ 每节点安装lldpd |

---

## 🔗 关联知识

| 模块 | 文件 | 关系 |
|:-----|:-----|:-----|
| 分布式OS | [RDMA 架构理论](rdma-architecture.md) | 本文的理论基础（IB协议栈/RC/UD/QoS） |
| 分布式OS | [GPU Direct 技术](gpu-direct-technology.md) | GPU Direct RDMA 依赖底层的 RDMA 硬件 |
| 分布式OS | [网络拓扑感知调度](network-topology-aware-scheduling.md) | ibnetdiscover 发现的拓扑是调度器输入 |
| 运维系统 | [NFD & GFD](nfd-gfd.md) | NFD 自动打 RDMA 标签的原理 + 实战 |
| 运维系统 | [GPU DCGM Exporter](ops-system/gpu-dcgm-exporter.md) | GPU 链路的 NVLink 监控（配合 RDMA 网络） |
