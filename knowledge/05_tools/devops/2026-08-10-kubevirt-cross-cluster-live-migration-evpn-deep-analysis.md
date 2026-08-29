# 🌐 KubeVirt 跨集群热迁移：网络才是真难点——OpenPERouter 把 EVPN/VXLAN 变成 3 个 CRD（TNS 8/8 本期主线）

> **统一主线**: KubeVirt 跨集群实时迁移的**技术已就绪（v1.6 decentralized live migration），真正的卡点是网络**——stretched L2（保 MAC/IP）+ 专用迁移带宽。传统解法（新 VLAN/交换机配置/变更窗口/数周）把 VM 移动变成网络团队的长周期工单；OpenPERouter 用 3 个 CRD 把 EVPN/VXLAN 变成 Kubernetes 原生声明式资源，迁移走独立 VNI 666 与业务（VNI 110）物理隔离。**本质是控制面/数据面分离 + 权属边界转移：underlay 归网络团队、overlay 归平台团队——「从申请物理变更并等待 → apply 一个 CR，overlay 自己收敛」。**
>
> **关键词**: KubeVirt · 跨集群实时迁移 · EVPN/VXLAN · CRD · stretched L2 · VNI 隔离 · underlay/overlay 权属 · 声明式网络
>
> **数据源**: ✅ TNS 全文一手抓取：
> - [Why your KubeVirt VMs can't move between clusters — and how EVPN fixes it](https://thenewstack.io/kubevirt-evpn-vm-migration/)（Miguel Duarte Barroso, **08-08 10:00am**）— 含 YAML 配置示例
>
> **素材分级**: ✅ 一手全文（含 2 个 L2VNI CR 示例 + 迁移资源示例）· 🔵 既有知识库锚点（MEMORY 网络第一原则 / 05_tools/devops / 超节点 O&M）
>
> **日期**: 2026-08-10 | **领域**: 虚拟化 / 云原生网络 / 平台工程

---

## 📑 目录

- [〇、结论概要](#〇结论概要)
- [一、为什么「迁移技术不是问题，网络才是」](#一为什么迁移技术不是问题网络才是)
  - [1.1 KubeVirt 迁移技术已就绪（v1.6）](#11-kubevirt-迁移技术已就绪v16)
  - [1.2 两个网络硬需求：stretched L2 + 专用迁移路径](#12-两个网络硬需求stretched-l2--专用迁移路径)
  - [1.3 传统方案的真实成本：变更窗口与数周等待](#13-传统方案的真实成本变更窗口与数周等待)
- [二、OpenPERouter：EVPN 配置的 K8s 原生化（3 个 CRD）](#二openperouterevpn-配置的-k8s-原生化3-个-crd)
  - [2.1 Underlay CR：BGP peering](#21-underlay-crbgp-peering)
  - [2.2 L2VNI CR：业务网络（VNI 110 / VRF red）](#22-l2vni-cr业务网络vni-110--vrf-red)
  - [2.3 L3VNI CR：跨子网路由](#23-l3vni-cr跨子网路由)
  - [2.4 迁移网络：第二个 L2VNI（VNI 666 / VRF rouge）](#24-迁移网络第二个-l2vnivni-666--vrf-rouge)
- [三、Day 2 运营：迁移的实际操作](#三day-2-运营迁移的实际操作)
  - [3.1 IPAM 分区（Whereabouts exclude ranges）](#31-ipam-分区whereabouts-exclude-ranges)
  - [3.2 三步迁移（WaitAsReceiver + receiver/sender 对）](#32-三步迁移waitasreceiver--receiversender-对)
- [四、运维权属转移：underlay/overlay 边界](#四运维权属转移underlayoverlay-边界)
- [五、本地知识库闭环：网络第一原则的第三次落地](#五本地知识库闭环网络第一原则的第三次落地)
- [六、批判性审视](#六批判性审视)
- [七、可证伪预测（P1-P4）](#七可证伪预测p1-p4)
- [八、对超节点运维 / 本系统的启示](#八对超节点运维--本系统的启示)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 〇、结论概要

**一句话：KubeVirt 跨集群迁移的瓶颈不在 KVM 虚拟化层（v1.6 已支持 decentralized live migration），而在网络层——VM 要在目标集群保住 MAC/IP（stretched L2），迁移流量要走独立通道（专用带宽）。OpenPERouter 证明：这两件事可以全部变成 Kubernetes CRD，由平台团队声明式完成，无需网络团队变更窗口。**

1. **技术就绪**：KubeVirt decentralized live migration v1.6 落地（2025-07），v1.8 稳定（2026-03）——虚拟化层已能跨集群迁移。
2. **网络是卡点**：两个硬需求——①stretched L2 域（同 MAC/IP/广播域，否则状态应用断连）②专用迁移路径（GB 级内存状态实时传输，与业务流量混跑会拥塞且不可观测）。
3. **传统方案贵**：新 VLAN + 交换机配置 + 可能新硬件 + 变更窗口 + 工单 + 数周。
4. **OpenPERouter 的解法**：EVPN/VXLAN 配置变成 3 个 CRD（Underlay BGP / L2VNI 业务 VNI 110 / L3VNI 路由）；迁移网络=第二个 L2VNI（VNI 666 / VRF rouge）与业务物理隔离；VXLAN 隧道端点无需同段，站点间 IP 可达即收敛。
5. **权属边界转移**：underlay（路由器端点/链路/站点间路由）仍归网络团队；**overlay（stretched L2、迁移网络、VRF 隔离）全部通过 CRD 由平台团队声明式管理**——「申请物理变更并等待」→「apply 一个 CR，overlay 自己收敛」。

**对超节点运维的直接含义**：多集群容灾/迁移是超节点（万卡集群）O&M 的核心场景；「迁移流量独立 VNI」与本地 MEMORY 的「管理网/Scale-Up 网必独立」「数据流/控制流=带宽与状态分离」是同一第一原则在虚拟化层的落地。

---

## 一、为什么「迁移技术不是问题，网络才是」

### 1.1 KubeVirt 迁移技术已就绪（v1.6）

| 里程碑 | 时间 | 内容 |
|:-------|:-----|:-----|
| KubeVirt 加入 CNCF | 2019-09 | 接受为 Sandbox 项目 |
| CNCF Incubating | 2022-04 | 成熟度提升 |
| **decentralized live migration** | **v1.6（2025-07）** | 跨集群迁移技术能力落地 |
| v1.8 | 2026-03 | 该特性保持稳定 |

**「技术不是问题」的依据**：虚拟化层已有跨集群迁移的机制（receiver/sender 模式，见 §3.2）——缺的是**承载它的网络**。

### 1.2 两个网络硬需求：stretched L2 + 专用迁移路径

| 需求 | 为什么必需 | 不满足的后果 |
|:-----|:-----------|:-------------|
| **stretched L2 域** | VM 落地目标集群须保持同 MAC/IP/广播域 | 每次迁移都要 IP 重分配 + DNS 更新 + 连接中断；**同步复制的 PostgreSQL、持 TCP 会话的消息队列等状态应用无法容忍** |
| **专用迁移路径** | 迁移传输 GB 级内存状态 | 与业务流量混跑 → 拥塞、延迟不可预测、两流量类无法独立监控 |

**第一性理解**：live migration 的本质是「把正在运行的进程状态搬走」，对网络而言=「广播域要跨站点 + 状态搬运不能影响业务」。标准 K8s 网络（CNI 集群内 L2/L3）两者都不覆盖——**这不是 KubeVirt 的缺陷，是网络模型的代际差异**。

### 1.3 传统方案的真实成本：变更窗口与数周等待

> 「In traditional infrastructure, you're looking at new VLANs, switch configurations, and possibly even new hardware. A change window. A ticket. Weeks.」

传统虚拟化平台的解法：**专用迁移 VLAN + 厂商私有虚拟交换机构件**——硬件耦合、厂商绑定、常按 socket 计费。开源等效物必须：作为 overlay 工作、声明式管理、不碰物理网络。

---

## 二、OpenPERouter：EVPN 配置的 K8s 原生化（3 个 CRD）

### 2.1 Underlay CR：BGP peering

**作用**：建立每个 K8s 集群与其 ToR（top-of-rack）交换机之间的 BGP peering——这是 overlay 的物理基础，只需配置一次。

### 2.2 L2VNI CR：业务网络（VNI 110 / VRF red）

**作用**：创建 L2 overlay 网络，由 VNI 标识的 VXLAN 段实现，scope 到 VRF。原文示例（业务网络）：

```yaml
apiVersion: openpe.openperouter.github.io/v1alpha1
kind: L2VNI
metadata:
  name: application-net
  namespace: openperouter-system
spec:
  vni: 110
  vrf: red
  hostmaster:
    type: linux-bridge
    linuxBridge:
      autoCreate: true
      l2gatewayips: ["192.170.10.1/24"]
```

**关键点**：两个集群部署**完全相同的 L2VNI 资源** → 两集群 VM 共享 192.170.1.0/24 的 L2 邻接——A 集群 192.170.1.3 的 VM 与 B 集群 192.170.1.30 的 VM 如同在同一交换机上。

### 2.3 L3VNI CR：跨子网路由

**作用**：实现不同子网间的 IP 路由，并把集群连接到外部网络——L3 层的 EVPN 网关。

### 2.4 迁移网络：第二个 L2VNI（VNI 666 / VRF rouge）

```yaml
apiVersion: openpe.openperouter.github.io/v1alpha1
kind: L2VNI
metadata:
  name: migration-net
  namespace: openperouter-system
spec:
  vni: 666
  vrf: rouge
  hostmaster:
    type: linux-bridge
    linuxBridge:
      autoCreate: true
      l2gatewayips: ["192.170.10.1/24"]
```

**迁移网络的全部要求 = 一个唯一 VNI + VRF**（示例 666 / rouge）——迁移流量与业务流量（VNI 110）**物理隔离**（不同 VXLAN 段）。

**最反直觉的设计点**：VXLAN 隧道端点**不需要在同一网络段**——只要站点间 IP 可达（可跨任意多跳路由），overlay 就自动收敛。

> 「Two CRDs define what used to require a network team and a change window.」——两个 CRD 定义了过去需要网络团队 + 变更窗口的东西。

---

## 三、Day 2 运营：迁移的实际操作

### 3.1 IPAM 分区（Whereabouts exclude ranges）

跨集群 IP 管理需要**无中心协调的防冲突策略**：

| 方案 | 设计 |
|:-----|:-----|
| Whereabouts + 互补 exclude ranges | 两集群的 Network Attachment Definition 覆盖同一 192.170.10.0/24，但各自排除对方一半 |
| 效果 | 集群 A 从低段分配、集群 B 从高段分配——无冲突、无中心协调 |
| 说明 | Whereabouts 是设计选择非硬性要求；任何能分区 IPAM 均可 |

### 3.2 三步迁移（WaitAsReceiver + receiver/sender 对）

| 步骤 | 资源 | 要点 |
|:-----|:-----|:-----|
| **1. 目标 VM 预备** | runStrategy: **WaitAsReceiver** | 集群 B 上创建相同 MAC/IP 的 VM，空闲等待接收 |
| **2. 接收端声明就绪** | VirtualMachineInstanceMigration（receive） | `migrationID: cross-cluster-demo` + `vmiName`；暴露接收端迁移 IP |
| **3. 发送端发起** | VirtualMachineInstanceMigration（sendTo） | `connectURL: <receiver .status.synchronizationAddresses[0]>:9185` + 同 migrationID |

**迁移完成后的网络收敛**：EVPN 更新 MAC/IP 通告 → 指向 VM 的流量开始到达新集群——**无 DNS 变更、无 IP 重分配、无连接重置**（这就是 stretched L2 的收益）。

---

## 四、运维权属转移：underlay/overlay 边界

| 角色 | 传统虚拟化 | KubeVirt + OpenPERouter |
|:-----|:-----------|:------------------------|
| **网络管理员** | 管理物理交换机、VLAN、硬件配置——每次 VM 移动都依赖工单 + 变更窗口 | 只负责 foundational IP 连接、路由器端点、链路（**underlay**） |
| **K8s 管理员** | 依赖网络团队 | 通过 CRD 声明式管理 overlay 网络、BGP/EVPN 配置、VM 移动性 |

> 「The operational model shifts from 'request physical network changes and wait' to 'apply a CR and the overlay converges.'」——运营模型从「申请物理变更并等待」变成「apply 一个 CR，overlay 自己收敛」。

**边界划分的合理性**：underlay 是物理事实（IP 编址、链路、站点路由），改变它需要硬件/物理介入——归网络团队天经地义；overlay 是逻辑构造（VNI/VRF/广播域），本质是声明式状态——归平台团队与 K8s 哲学一致。**边界不是「谁技术强」，而是「谁拥有变化面」：物理面变化慢且贵 → 网络团队；逻辑面变化快且可版本化 → 平台团队。**

---

## 五、本地知识库闭环：网络第一原则的第三次落地

| 锚点 | 闭环内容 |
|:-----|:---------|
| **MEMORY：管理网/Scale-Up 网必独立** | 迁移 VNI 666 独立于业务 VNI 110 = 同一原则：**关键流量类必须物理/逻辑隔离**（超节点里是管理网 vs 数据面；这里是迁移流量 vs 业务流量） |
| **MEMORY：数据流/控制流=带宽与状态分离** | overlay 收敛（控制面）与迁移数据搬运（数据面）分离；「状态分离」在迁移场景=MAC/IP 身份与物理位置解耦（EVPN 通告） |
| **控制面/数据面分离第三次落地** | ①网络数据流/控制流 ②KV 分层 ③本次 overlay/underlay——**模式识别：分离的不是「网」是「变化面与流量面」** |
| **05_tools/devops/ 既有 K8s 运维** | etcd-raft-network-partition（网络分区故障）→ 跨集群迁移是网络分区之外的主动性动作 |
| **「工具化=确定性外壳」** | CRD 声明式网络 = 把「网络变更」从工单/人工执行变成确定性可复现的声明——与本地「修补工具化」方法论同构 |
| **平台工程权属** | underlay/overlay 分工 = 「平台三态（工具/治理/认知）」中治理层的落地案例 |

---

## 六、批判性审视

1. **来源性质**：TNS 文章是 OpenPERouter 的**推广性技术文**（含 vendor 视角），无独立第三方生产验证——「3 个 CRD」的简洁性是作者叙事，真实运营复杂度（BGP 收敛、故障转移、安全边界）需实测。
2. **VNI 隔离的边界**：VNI 666 隔离的是**数据面**；控制面（BGP/EVPN 通告）仍共享——「物理隔离」措辞应理解为「逻辑隔离」。
3. **迁移带宽未量化**：文章未给迁移 VNI 的带宽/时延要求——「专用迁移路径」解决的是拥塞与可观测性，不是带宽保证本身。
4. **IPAM 分区是手动设计**：Whereabouts exclude ranges 是静态分区，跨集群扩缩容时（新增集群/子网）需要人工同步——真正的动态 IPAM 仍是开放问题。
5. **状态应用的一致性**：文章说「无连接重置」，但同步复制 PostgreSQL 的**事务一致性**在迁移瞬间仍依赖上层复制协议——网络保 MAC/IP 不解决应用层一致性。
6. **KubeVirt 生态成熟度**：decentralized live migration 是较新特性（v1.6 起），生产环境大规模验证案例有限。

---

## 七、可证伪预测（P1-P4）

- **P1（高置信）**：12 个月内出现 ≥3 个基于 OpenPERouter 或同类 CRD 化 EVPN 的跨集群迁移生产案例报告（非 vendor 宣传），声明式 overlay 成为 KubeVirt 跨集群迁移主流网络范式（2027-08 核验）。
- **P2（中置信）**：「迁移流量独立 VNI」成为 KubeVirt 迁移文档/最佳实践的标准要求——就像超节点「管理网独立」成为共识一样（2027-08 核验）。
- **P3（中置信）**：动态 IPAM（非静态分区）成为下一瓶颈：12 个月内出现与 CRD 化 EVPN 配套的跨集群动态 IPAM 方案（2027-08 核验）。
- **P4（低置信）**：underlay/overlay 权属分离模式从虚拟化外溢到**GPU 集群编排**——超节点 O&M 中「物理网络归网络团队、逻辑拓扑（拓扑感知调度所需的 VNI/路由）归平台团队」成为标准（2027-08 核验）。

---

## 八、对超节点运维 / 本系统的启示

1. **迁移即治理边界样板**：KubeVirt 案例是「网络治理边界」的完整样板——**变化面（物理 vs 逻辑）决定权属**。超节点运维可直接借用：物理互连（光缆/交换机/供电）归基础设施团队，逻辑拓扑（NCCL 拓扑文件、VNI 划分、QoS 策略）归平台/SRE 团队。
2. **流量类隔离的可复用清单**：迁移流量独立 VNI 的模式可映射到超节点：**checkpoint 流量、遥测流量、管理流量**应分别有独立通道（本地 MEMORY 已有管理网独立；本案例补充「运维动作流量」维度）。
3. **声明式=可审计**：CRD 化网络的最大收益不是「快」而是「可版本化可回滚」——本系统知识库治理的「声明式契约」（三件套纪律）同理：**把变化变成可 review 的声明，而不是不可追溯的执行**。
4. **对国产虚拟化/超节点软件栈**：国产替代若做虚拟化层跨节点迁移（如基于 KVM 的国产云），网络层 stretched L2 + 独立迁移通道是**必须内建**的能力，而非事后补——OpenPERouter 的 CRD 化是值得参考的开源路径（避免重蹈「厂商私有迁移网络」覆辙）。

---

## 参考来源

- [Why your KubeVirt VMs can't move between clusters — and how EVPN fixes it](https://thenewstack.io/kubevirt-evpn-vm-migration/) — Miguel Duarte Barroso，The New Stack，2026-08-08 10:00am（✅ 全文一手抓取，含 YAML 示例）
- [OpenPERouter examples / docs](https://github.com/openperouter) — 文中引用（Stretched L2 Network between Clusters、Dedicated Migration Network for Cross-Cluster Live Migration）
- 本地：MEMORY.md（管理网/Scale-Up 网独立；数据流/控制流=带宽与状态分离）
- 本地：[etcd-raft-network-partition](knowledge/05_tools/devops/2026-06-18-etcd-raft-network-partition.md)（网络分区运维）
- 本地：[AI 工程经济学深潜](2026-08-10-ai-engineering-economics-measurement-adoption-deep-analysis.md)（同日姊妹篇，平台工程治理）

> **诚实标注**：TNS 文章为 OpenPERouter 技术介绍文，含 vendor 视角；无独立第三方生产数据。VNI 隔离为逻辑隔离非物理隔离。迁移带宽/一致性细节未量化。本分析为技术解读，非采购建议。

---

## Changelog

- 2026-08-10：创建。素材=TNS KubeVirt/EVPN 全文一手抓取（含 2 个 L2VNI CR + 迁移资源 YAML）；主线=跨集群迁移的真正卡点是网络（stretched L2 + 专用通道），OpenPERouter 以 3 CRD 把 EVPN 声明式化；权属边界=underlay 归网络团队/overlay 归平台团队；与 MEMORY 网络第一原则（管理网独立/带宽状态分离）构成第三次落地；P1-P4 可证伪预测。
