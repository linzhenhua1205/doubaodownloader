# Linux 端口转发的几种常用方法

> **概要**: Linux端口转发常用方法速查，涵盖SSH、iptables、firewall-cmd、socat等
>
> **关键词**: 端口转发 · SSH · iptables · socat · 内网穿透

---

## 📑 目录

- [速查矩阵](#速查矩阵)
- [一、SSH 端口转发（最常用）](#一ssh-端口转发最常用)
  - [本地转发（-L）](#本地转发-l)
  - [远程转发（-R）](#远程转发-r)
  - [动态转发（-D, SOCKS 代理）](#动态转发-d-socks-代理)
  - [常用参数](#常用参数)
- [二、iptables 端口转发（CentOS 6/7）](#二iptables-端口转发centos-67)
  - [本地端口映射](#本地端口映射)
  - [跨机器转发](#跨机器转发)
- [三、firewall-cmd 端口转发（CentOS 7+/RHEL 8+）](#三firewall-cmd-端口转发centos-7rhel-8)
- [四、rinetd — 轻量级 TCP 转发](#四rinetd-轻量级-tcp-转发)
- [五、ncat — 应急调试](#五ncat-应急调试)
- [六、socat — 灵活首选（支持双向/复杂协议）](#六socat-灵活首选支持双向复杂协议)
- [七、portmap (lcx) — 内网穿透](#七portmap-lcx-内网穿透)
- [八、选型建议](#八选型建议)
- [关联知识](#关联知识)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

---

## 速查矩阵

| 工具 | 适用场景 | 配置复杂度 | 加密 | 持久化 | 推荐 |
|:-----|:---------|:----------:|:----:|:------:|:----:|
| **SSH** | 临时转发/跨跳板机 | ⭐ | ✅ 加密 | ❌ | ⭐ 日常首选 |
| **iptables** | CentOS 6/7 以下内核转发 | ⭐⭐⭐ | ❌ | ✅ | CentOS 6/7 标配 |
| **firewall-cmd** | CentOS 7+/RHEL 8+ | ⭐⭐ | ❌ | ✅ | CentOS 8+ 标配 |
| **rinetd** | 简单 TCP 转发 | ⭐ | ❌ | ✅ 配置文件 | 轻量场景 |
| **ncat** | 临时端口映射 | ⭐⭐ | ❌ | ❌ | 应急调试 |
| **socat** | 复杂协议转换/双向通道 | ⭐⭐ | ❌ | ❌ | 灵活首选 |
| **portmap** (lcx) | 内网穿透/渗透测试 | ⭐⭐ | ❌ | ❌ | 安全场景 |

---

## 一、SSH 端口转发（最常用）

SSH 转发自带**加密**，适合跨公网安全转发，无需额外服务。

### 本地转发（-L）

将本地端口流量经 SSH 隧道送达目标主机：

```bash
ssh -fgN -L 2222:localhost:22 localhost
```

→ 访问本机 `2222` 端口 = 通过 SSH 到达本机 `22` 端口

### 远程转发（-R）

将远程端口流量回传到本地：

```bash
ssh -fgN -R 2222:host1:22 localhost
```

→ 访问远程 `2222` 端口 = 到达 `host1:22`

### 动态转发（-D, SOCKS 代理）

```bash
ssh -fgN -D 12345 root@host1
```

→ 本地 `12345` 端口提供 SOCKS 代理，所有流量经 `host1` 转发

### 常用参数

| 参数 | 含义 |
|:-----|:------|
| `-f` | 后台运行 |
| `-g` | 允许远程主机连接本地转发端口 |
| `-N` | 不执行远程命令（纯端口转发） |
| `-L` | 本地端口转发 |
| `-R` | 远程端口转发 |
| `-D` | 动态转发（SOCKS） |

---

## 二、iptables 端口转发（CentOS 6/7）

**前置条件**：开启 IP 转发

```bash
# /etc/sysctl.conf 添加
net.ipv4.ip_forward=1
sysctl -p
```

### 本地端口映射

```bash
iptables -t nat -A PREROUTING -p tcp --dport 2222 \
  -j REDIRECT --to-port 22
```

### 跨机器转发

```bash
# DNAT：修改目标地址
iptables -t nat -A PREROUTING -d 192.168.172.130 -p tcp --dport 8000 \
  -j DNAT --to-destination 192.168.172.131:80

# SNAT：修改源地址（让目标机器知道回包该发给谁）
iptables -t nat -A POSTROUTING -d 192.168.172.131 -p tcp --dport 80 \
  -j SNAT --to 192.168.172.130
```

```bash
# 清空 nat 表
iptables -t nat -F PREROUTING
```

---

## 三、firewall-cmd 端口转发（CentOS 7+/RHEL 8+）

```bash
# 1. 开启伪装 IP
firewall-cmd --permanent --add-masquerade

# 2. 配置转发：本机 12345 → 192.168.172.131:22
firewall-cmd --permanent \
  --add-forward-port=port=12345:proto=tcp:toaddr=192.168.172.131:toport=22

# 3. 重载生效
firewall-cmd --reload
```

---

## 四、rinetd — 轻量级 TCP 转发

```bash
# 安装
rpm -ivh rinetd-0.62-9.el7.nux.x86_64.rpm

# 配置 /etc/rinetd.conf
# 格式: 源地址 源端口 目标地址 目标端口
0.0.0.0 1234 127.0.0.1 22

# 启动
rinetd -c /etc/rinetd.conf
```

---

## 五、ncat — 应急调试

```bash
# 安装
yum install nmap-ncat -y

# 监听 9876，转发到 192.168.172.131:80
ncat --sh-exec "ncat 192.168.172.131 80" -l 9876 --keep-open
```

---

## 六、socat — 灵活首选（支持双向/复杂协议）

```bash
# 安装
yum install -y socat

# 监听 12345 → 转发到 192.168.172.131:22
socat TCP4-LISTEN:12345,reuseaddr,fork TCP4:192.168.172.131:22
```

常用选项：

- `reuseaddr`：允许端口复用
- `fork`：每个连接创建子进程处理（支持并发）
- 支持 UNIX socket、UDP、SSL、PTY 等多种类型

---

## 七、portmap (lcx) — 内网穿透

```bash
# 下载
wget http://www.vuln.cn/wp-content/uploads/2016/06/lcx_vuln.cn_.zip

# 监听 1234 → 转发到 192.168.172.131:22
./portmap -m 1 -p1 1234 -h2 192.168.172.131 -p2 22
```

---

## 八、选型建议

| 场景 | 推荐方案 |
|:-----|:---------|
| 日常调试/临时转发 | **SSH -L**（自备加密，0 额外依赖） |
| 生产环境持久转发 | **firewall-cmd**（CentOS 8+）或 **iptables**（CentOS 6/7） |
| 跨机器透明转发 | **iptables DNAT + SNAT**（内核级，性能最优） |
| 简单 TCP 转发服务 | **rinetd**（配置文件一行搞定） |
| 需要双向/协议转换 | **socat**（功能最强，类型丰富） |
| 内网穿透/跨网段 | **SSH -R** 或 **portmap**（lcx） |

---

## 关联知识

- XFS reflink/CoW 拷贝加速 — Linux 内核文件系统层优化

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- XFS reflink/CoW 拷贝加速 — 关联

### 外部资料引用

- 来源: [johng.cn 博客](https://johng.cn/notes/linux-port-forwarding-methods)

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-24 | v1.0 | 初始版本 |
