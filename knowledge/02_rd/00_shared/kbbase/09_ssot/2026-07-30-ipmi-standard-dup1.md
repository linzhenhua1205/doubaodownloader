# IPMI标准规范

> **概要**: IPMI标准规范定义、架构、版本与BMC功能
>
> **关键词**: IPMI · BMC · 带外管理 · 服务器管理 · 硬件监控

---

## 📑 目录

- [1. IPMI概述](#1-ipmi概述)
  - [1.1 IPMI定义](#11-ipmi定义)
  - [1.2 IPMI架构](#12-ipmi架构)
  - [1.3 IPMI版本](#13-ipmi版本)
- [2. BMC功能](#2-bmc功能)
  - [2.1 核心功能](#21-核心功能)
  - [2.2 高级功能](#22-高级功能)
- [3. IPMI通信接口](#3-ipmi通信接口)
  - [3.1 LAN接口](#31-lan接口)
  - [3.2 IPMB接口](#32-ipmb接口)
  - [3.3 系统接口](#33-系统接口)
- [4. IPMI命令](#4-ipmi命令)
  - [4.1 命令分类](#41-命令分类)
  - [4.2 常用命令](#42-常用命令)
    - [4.2.1 电源控制命令](#421-电源控制命令)
    - [4.2.2 传感器命令](#422-传感器命令)
    - [4.2.3 用户管理命令](#423-用户管理命令)
    - [4.2.4 FRU命令](#424-fru命令)
    - [4.2.5 SEL命令](#425-sel命令)
- [5. IPMI安全](#5-ipmi安全)
  - [5.1 认证机制](#51-认证机制)
  - [5.2 加密机制](#52-加密机制)
  - [5.3 用户权限](#53-用户权限)
- [6. IPMI传感器](#6-ipmi传感器)
  - [6.1 传感器类型](#61-传感器类型)
  - [6.2 传感器阈值](#62-传感器阈值)
  - [6.3 传感器事件](#63-传感器事件)
- [7. IPMI SEL（System Event Log）](#7-ipmi-selsystem-event-log)
  - [7.1 SEL结构](#71-sel结构)
  - [7.2 SEL操作](#72-sel操作)
- [8. IPMI FRU（Field Replaceable Unit）](#8-ipmi-frufield-replaceable-unit)
  - [8.1 FRU信息](#81-fru信息)
  - [8.2 FRU格式](#82-fru格式)
- [9. 平台事件过滤（PEF）](#9-平台事件过滤pef)
  - [9.1 PEF功能](#91-pef功能)
  - [9.2 PEF配置](#92-pef配置)
- [10. IPMI Web GUI配置](#10-ipmi-web-gui配置)
  - [10.1 登录配置](#101-登录配置)
  - [10.2 网络配置](#102-网络配置)
  - [10.3 用户管理](#103-用户管理)
  - [10.4 传感器配置](#104-传感器配置)
  - [10.5 固件更新](#105-固件更新)
- [11. IPMI最佳实践](#11-ipmi最佳实践)
  - [11.1 安全配置](#111-安全配置)
  - [11.2 监控配置](#112-监控配置)
  - [11.3 远程管理](#113-远程管理)
  - [11.4 日志管理](#114-日志管理)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

## 1. IPMI概述

### 1.1 IPMI定义

IPMI（Intelligent Platform Management Interface）是一种标准化的平台管理接口，用于远程管理服务器硬件。

### 1.2 IPMI架构

IPMI架构包括：

- **BMC（Baseboard Management Controller）**：基板管理控制器
- **IPMB（Intelligent Platform Management Bus）**：智能平台管理总线
- **传感器**：温度、电压、风扇等传感器
- **FRU（Field Replaceable Unit）**：现场可更换单元信息

### 1.3 IPMI版本

IPMI主要版本：

- **IPMI 1.0**：初始版本
- **IPMI 1.5**：增加LAN接口支持
- **IPMI 2.0**：增加安全特性和更多功能

## 2. BMC功能

### 2.1 核心功能

- **远程电源控制**：开机、关机、重启、电源循环
- **传感器监测**：温度、电压、风扇、功率等
- **事件日志**：记录系统事件
- **FRU信息**：设备识别信息
- **远程控制台**：KVM over IP、虚拟媒体

### 2.2 高级功能

- **平台事件过滤（PEF）**：配置事件触发动作
- **告警通知**：SNMP Trap、邮件告警
- **固件更新**：远程更新BIOS、BMC固件
- **安全管理**：用户认证、SSL加密

## 3. IPMI通信接口

### 3.1 LAN接口

通过以太网进行IPMI通信，支持：

- **RMCP（Remote Management Control Protocol）**：远程管理控制协议
- **RMCP+**：加密的RMCP协议
- **端口**：默认UDP 623（非安全）、UDP 664（安全）

### 3.2 IPMB接口

通过I2C总线进行板级通信：

- **IPMB-L**：本地IPMB总线
- **IPMB-S**：卫星IPMB总线

### 3.3 系统接口

通过系统总线与主机通信：

- **SMIC（System Management Interface Chip）**
- **KCS（Keyboard Controller Style）**
- **BT（Block Transfer）**
- **SSIF（SMBus System Interface）**

## 4. IPMI命令

### 4.1 命令分类

IPMI命令分为以下类别：

- **Chassis Commands**：机箱命令（电源控制、状态查询）
- **Bridge Commands**：桥接命令（IPMB通信）
- **Sensor Event Commands**：传感器事件命令（阈值设置、事件查询）
- **Application Commands**：应用命令（用户管理、FRU信息）
- **Firmware Commands**：固件命令（固件更新）
- **Storage Commands**：存储命令（SEL、FRU数据）

### 4.2 常用命令

#### 4.2.1 电源控制命令

- `Chassis Control`：控制机箱电源状态
- `Chassis Status`：查询机箱状态

#### 4.2.2 传感器命令

- `Get Sensor Reading`：获取传感器读数
- `Set Sensor Thresholds`：设置传感器阈值
- `Get Sensor Thresholds`：获取传感器阈值

#### 4.2.3 用户管理命令

- `Get User Access`：获取用户权限
- `Set User Access`：设置用户权限
- `Set User Name`：设置用户名
- `Set User Password`：设置用户密码

#### 4.2.4 FRU命令

- `Get FRU Inventory Area Info`：获取FRU信息
- `Read FRU Data`：读取FRU数据

#### 4.2.5 SEL命令

- `Get SEL Info`：获取SEL信息
- `Get SEL Entry`：获取SEL条目
- `Clear SEL`：清除SEL

## 5. IPMI安全

### 5.1 认证机制

IPMI支持多种认证机制：

- **None**：无认证
- **MD2**：MD2摘要认证
- **MD5**：MD5摘要认证
- **OEM**：OEM自定义认证
- **IPMI v2.0/RMCP+**：更强的认证机制

### 5.2 加密机制

- **AES-CBC**：对称加密
- **RSA**：非对称加密
- **SSL/TLS**：传输层加密

### 5.3 用户权限

IPMI定义了用户权限级别：

- **Administrator**：管理员权限
- **Operator**：操作员权限
- **User**：用户权限
- **OEM**：OEM权限

## 6. IPMI传感器

### 6.1 传感器类型

IPMI支持多种传感器类型：

- **温度传感器**：CPU温度、内存温度、机箱温度
- **电压传感器**：输入电压、CPU电压、内存电压
- **风扇传感器**：风扇转速
- **功率传感器**：电源功率
- **电流传感器**：电源电流

### 6.2 传感器阈值

每个传感器可以设置多个阈值：

- **Lower Non-Recoverable (LNR)**：下限不可恢复
- **Lower Critical (LC)**：下限临界
- **Lower Non-Critical (LNC)**：下限非临界
- **Upper Non-Critical (UNC)**：上限非临界
- **Upper Critical (UC)**：上限临界
- **Upper Non-Recoverable (UNR)**：上限不可恢复

### 6.3 传感器事件

传感器事件包括：

- **Threshold Event**：阈值事件
- **Discrete Event**：离散事件
- **OEM Event**：OEM事件

## 7. IPMI SEL（System Event Log）

### 7.1 SEL结构

SEL记录系统事件，每条记录包含：

- **记录ID**：唯一标识
- **时间戳**：事件发生时间
- **传感器类型**：产生事件的传感器类型
- **传感器编号**：传感器编号
- **事件方向**：事件方向（assert/deassert）
- **事件数据**：事件详细数据

### 7.2 SEL操作

- **读取SEL**：读取SEL条目
- **清除SEL**：清除所有SEL条目
- **添加SEL**：添加新的SEL条目

## 8. IPMI FRU（Field Replaceable Unit）

### 8.1 FRU信息

FRU信息包括：

- **Chassis Info**：机箱信息
- **Board Info**：主板信息
- **Product Info**：产品信息
- **Multi Record**：多记录信息

### 8.2 FRU格式

FRU数据使用标准格式：

- **Common Header**：公共头
- **Internal Use Area**：内部使用区域
- **Chassis Info Area**：机箱信息区域
- **Board Info Area**：主板信息区域
- **Product Info Area**：产品信息区域
- **Multi Record Area**：多记录区域

## 9. 平台事件过滤（PEF）

### 9.1 PEF功能

PEF允许配置事件触发动作，包括：

- **系统关机**
- **系统重启**
- **发送告警**
- **记录事件**

### 9.2 PEF配置

PEF配置包括：

- **Event Filters**：事件过滤器
- **Alert Policies**：告警策略
- **LAN Destinations**：LAN目的地

## 10. IPMI Web GUI配置

### 10.1 登录配置

- **用户名/密码**：默认admin/admin
- **SSL认证**：支持双向SSL认证

### 10.2 网络配置

- **IP地址**：静态或DHCP
- **子网掩码**：IPv4/IPv6
- **网关**：默认网关
- **DNS**：DNS服务器配置

### 10.3 用户管理

- **添加用户**：创建新用户
- **删除用户**：删除用户
- **权限设置**：设置用户权限
- **密码管理**：修改密码

### 10.4 传感器配置

- **阈值设置**：配置传感器阈值
- **告警设置**：配置告警规则

### 10.5 固件更新

- **BMC固件更新**：更新BMC固件
- **BIOS固件更新**：更新BIOS固件
- **固件备份**：备份固件配置

## 11. IPMI最佳实践

### 11.1 安全配置

- **修改默认密码**：首次登录后修改默认密码
- **启用加密**：使用SSL加密通信
- **限制访问**：配置防火墙规则
- **定期更新**：定期更新BMC固件

### 11.2 监控配置

- **设置阈值**：合理设置传感器阈值
- **配置告警**：配置告警通知方式
- **定期检查**：定期检查传感器状态

### 11.3 远程管理

- **测试远程控制**：测试远程电源控制功能
- **配置KVM**：配置KVM over IP
- **配置虚拟媒体**：配置虚拟媒体功能

### 11.4 日志管理

- **定期清理**：定期清理SEL日志
- **备份日志**：备份重要日志
- **分析日志**：分析日志发现问题

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
