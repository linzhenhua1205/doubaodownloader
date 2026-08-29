# 📘 OpenStack 1.7.2 & Ceph 9.2.1 运维命令速查

> **概要**: OpenStack与Ceph运维命令速查手册，涵盖实例、服务、存储与OSD运维
>
> **关键词**: OpenStack · Ceph · 运维命令 · OSD · Cinder

---

## 📑 目录

- [📋 核心内容一览](#核心内容一览)
  - [1️⃣ 实例管理](#1-实例管理)
  - [2️⃣ 服务状态检查](#2-服务状态检查)
  - [3️⃣ 计算节点维护](#3-计算节点维护)
  - [4️⃣ Keystone 项目管理](#4-keystone-项目管理)
  - [5️⃣ RAID 检查](#5-raid-检查)
  - [6️⃣ Ceph 9.2.1 集群运维（核心篇幅）](#6-ceph-921-集群运维核心篇幅)
  - [7️⃣ Cinder 块存储操作](#7-cinder-块存储操作)
  - [8️⃣ OSD 目录结构与故障处理](#8-osd-目录结构与故障处理)
  - [9️⃣ 服务重启命令 + 顺序](#9-服务重启命令-顺序)
  - [🔟 日志与配置文件](#日志与配置文件)
- [🧠 核心运维经验](#核心运维经验)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

---

## 📋 核心内容一览

文章是一份**完整的 OpenStack + Ceph 运维命令速查手册**，涵盖 12 个大类，适用于传统 OpenStack (Mitaka/Newton 世代) + Ceph Jewel 集群的日常运维场景。

### 1️⃣ 实例管理

- `openstack server list` / `nova list` 查看列表，支持按 host/ip/status/image/flavor/all-tenants 过滤
- `openstack server show` / `nova show` 查看详情
- 硬重启 (`--hard`) vs 软重启
- 实例恢复三板斧：`nova reset-state --active` → `virsh destroy` → `openstack server delete --force`

### 2️⃣ 服务状态检查

- **Nova**: `nova service-list` / `openstack compute service list`
- **Neutron**: `neutron agent-list` / `openstack network agent list`
- **Cinder**: `openstack volume service list`
- **全局**: `nova hypervisor-stats` 查看 memory/vcpus/running_vms 资源概况

### 3️⃣ 计算节点维护

- systemctl 管理 nova-compute / libvirtd
- 日志定位（`grep ERROR` 过滤崩溃原因）
- **RabbitMQ 连通性测试**: `rabbitmqctl status`

### 4️⃣ Keystone 项目管理

- `openstack project list` / `openstack user list --project <project>`

### 5️⃣ RAID 检查

- **软件 RAID**: `cat /proc/mdstat`
- **硬件 RAID**: `lspci | grep -i raid`

### 6️⃣ Ceph 9.2.1 集群运维（核心篇幅）

- **基础状态**: `ceph status` / `ceph health detail` / `ceph --version`
- **OSD 性能监控**: `ceph osd perf` — 关注 `fs_commit_latency`（健康 <10ms）和 `fs_apply_latency`
- **PG 管理**: `ceph pg repair` / `ceph pg dump_stuck degraded` / `watch ceph -s`
- **OSD 管理**: `ceph osd find` / `ceph osd tree` / `ceph osd df` / `ceph osd reweight`
- **存储池**: 设置 size / min_size，推荐 size=3, min_size=2
- **存储阈值**: `ceph osd set_nearfull_ratio 0.90` / `set_full_ratio 0.95`
- **OSD 状态控制**: `ceph osd set norecover|nobackfill|nodown` 三件套（维护时禁用恢复/回填/离线检测）
- **核心排错**: `ceph osd dump` — 完整 OSD Map 全量元数据

### 7️⃣ Cinder 块存储操作

- `cinder list --all-tenants` 查看卷
- **数据库层面删除**: 三步走 — `UPDATE volumes SET deleted=1` → `DELETE FROM volume_attachment` → `DELETE FROM volume_metadata`
- **Ceph RBD 清理**: `rbd ls -p volumes | grep <id>` → `rbd rm -f volumes/<name>` → `rbd status`

### 8️⃣ OSD 目录结构与故障处理

- **OSD 目录结构详解**（10 个关键文件/目录说明）：
  - `current/` — 真实业务数据，删除=永久丢失
  - `journal` — 软链接到 SSD 分区
  - `superblock` — OSD 超级块，存储 PG 映射、容量等核心元数据
  - `whoami` — 标记 OSD 编号
  - `fsid` / `ceph_fsid` — 集群 UUID 校验
  - `activate.monmap` — Monitor 拓扑映射
  - `keyring` — 安全认证（600 权限）
  - `magic` — FileStore vs BlueStore 标识
- **SSD Journal 故障处理**（FileStore 时代经典）：
  - `rm -f journal journal_uuid` → `ceph-osd -i <id> --rebuild-journal --journal-inline` → `chown ceph:ceph` → `systemctl start`
  - 核心逻辑：删除损坏 SSD 软链接，在内盘重建内联 Journal，数据完整保留
- **存储引擎检查**: `ceph osd count-metadata osd_objectstore`

### 9️⃣ 服务重启命令 + 顺序

- 列出 Nova/Neutron/Cinder/Glance 全部服务 systemctl 命令
- **⚠️ 重启顺序铁律**: **先 Ceph → 后 OpenStack**
  - `nova service-disable` (维护前禁用调度)
  - 停止所有 Ceph OSD → 重启 → 确认恢复
  - 逐节点重启 OpenStack 服务 → 重新启用调度

### 🔟 日志与配置文件

- OpenStack 所有组件日志路径（Controller / Compute 节点分角色）
- Ceph 日志路径（`ceph.log` / `ceph-mon.*.log` / `ceph-osd.<id>.log`）
- 配置文件目录：`/etc/nova/` `/etc/neutron/` `/etc/cinder/` `/etc/glance/` `/etc/keystone/` `/etc/ceph/`
- `find /etc -name "*.conf" | grep -E "(nova|neutron|cinder|glance|keystone)"` 快速定位

---

## 🧠 核心运维经验

1. **"先 Ceph 后 OpenStack"** — 重启顺序失误是经典翻车场景
2. **SSD Journal 自愈** — FileStore 时代外置 SSD 损坏后可用内联 Journal 恢复，数据不丢
3. **OSD 阈值管理** — `nearfull_ratio 0.90` / `full_ratio 0.95`，满了就是只读
4. **维护三件套** — `set norecover + nobackfill + nodown` 禁用自动恢复，防止维护期间数据风暴
5. **Cinder 卷彻底清理** — 不能只删 OpenStack 侧，Ceph RBD 里的镜像文件也要删

---

> **适用场景**: 传统 OpenStack + Ceph 架构的运维排障、集群迁移、节点维护（Kilo/Mitaka/Newton 等较老版本京东云/电信云等存量环境仍可见）

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- (无)

### 外部资料引用

- 来源: 博客园「人生的哲理」

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-24 | v1.0 | 初始版本 |
