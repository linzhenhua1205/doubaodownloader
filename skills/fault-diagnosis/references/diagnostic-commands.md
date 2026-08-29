# 排障命令速查手册

## 系统层

| 目的 | 命令 | 说明 |
|:-----|:-----|:-----|
| 内核日志 | `dmesg -T \| tail -100` | 查看最近内核日志（含时间戳） |
| 系统日志 | `journalctl -xe -n 50 --no-pager` | 查看最近的系统日志 |
| 服务日志 | `journalctl -u <service> --since "5 min ago"` | 查看特定服务的日志 |
| 内存状态 | `free -h; cat /proc/meminfo \| grep -E "(MemTotal\|MemFree\|Cached)"` | 内存总量/剩余/缓存 |
| CPU 信息 | `lscpu; mpstat -P ALL 1 3` | CPU 架构 + 各核负载 |
| 磁盘 IO | `iostat -x 1 3` | 磁盘 IO 详情（await、svctm、util） |
| 网络状态 | `ss -tuln; netstat -s` | 监听端口 + 网络统计 |
| 进程树 | `ps auxf \| head -50` | 进程树结构 |
| 打开文件 | `lsof +c 15 \| head -30` | 查看进程打开的文件 |
| 系统限制 | `ulimit -a` | 用户进程限制 |
| 启动时间 | `uptime; who -b` | 系统运行时间和启动时间 |

## 存储/磁盘层

| 目的 | 命令 | 说明 |
|:-----|:-----|:-----|
| 磁盘列表 | `lsblk -o NAME,SIZE,TYPE,MOUNTPOINT,FSTYPE` | 块设备一览 |
| 分区信息 | `fdisk -l /dev/sda` | 分区表详情 |
| 磁盘使用 | `df -hT \| grep -v tmpfs` | 磁盘使用率（含文件系统类型） |
| 大目录定位 | `du -sh /* 2>/dev/null \| sort -rh \| head -10` | 找到最大目录 |
| 磁盘健康 | `smartctl -a /dev/nvme0n1 \| grep -E "(Critical\|Percentage\|Media\|Power_On\|Unsafe)"` | SMART 关键指标 |
| NVMe 详情 | `nvme list; nvme smart-log /dev/nvme0n1` | NVMe 设备 + SMART |
| IO 排队 | `iostat -x -d 1 5` | 连续 5 次 IO 监控 |
| IO 定位进程 | `iotop -o -n 1 -b` | 正在 IO 的进程 |
| 文件系统检查 | `dumpe2fs -h /dev/sda1 \| grep -E "(Block count\|Block size)"` | 文件系统参数 |

## 网络层

| 目的 | 命令 | 说明 |
|:-----|:-----|:-----|
| 网卡信息 | `ip a; ethtool <eth0>` | 网卡 IP + 速率/双工 |
| 路由表 | `ip route show` | 路由表 |
| ARP 表 | `ip neigh` | ARP 邻居表 |
| 带宽测试 | `iperf3 -c <server> -t 10` | 网络带宽测试 |
| 连通性 | `ping -c 5 <target>; mtr <target>` | 延迟+路径探测 |
| DNS 解析 | `dig +short <domain>; nslookup <domain>` | DNS 查询 |
| TCP 状态 | `ss -s; ss -tan \| awk '{print $1}' \| sort \| uniq -c` | TCP 连接状态统计 |
| 抓包 | `tcpdump -i eth0 -c 100 -nn port 80` | 抓取 100 个包 |
| 丢包统计 | `ethtool -S eth0 \| grep -E "(drop\|error\|miss\|fifo)"` | 网卡丢包/错误统计 |
| 网卡缓存 | `ethtool -g eth0` | Ring buffer 大小 |
| MTU | `ip link show eth0; ping -M do -s 1472 <target>` | MTU 探测 |

## GPU 层

| 目的 | 命令 | 说明 |
|:-----|:-----|:-----|
| GPU 状态 | `nvidia-smi` | 温度/功耗/显存/利用率 |
| GPU 进程 | `nvidia-smi pmon -c 1` | 哪个进程在用 GPU |
| GPU 详情 | `nvidia-smi -q -d TEMPERATURE,POWER,CLOCK,MEMORY` | GPU 子项详情 |
| GPU 错误 | `dmesg \| grep -i nvidia; journalctl -u nvidia-persistenced --since "1h ago"` | GPU 相关错误 |
| Xid 错误 | `grep -i xid /var/log/syslog \| tail -20` | GPU Xid 硬件错误统计 |
| NVLink 状态 | `nvidia-smi nvlink --status` | NVLink 链路状态 |
| GPU 拓扑 | `nvidia-smi topo -m` | GPU 互联拓扑（PCIe/NVLink） |

## BMC/IPMI 层

| 目的 | 命令 | 说明 |
|:-----|:-----|:-----|
| 传感器 | `ipmitool sensor \| grep -E "(Temp\|Fan\|Volt\|Power)"` | 温度/风扇/电压/功耗 |
| SEL 日志 | `ipmitool sel list -c \| tail -20` | 系统事件日志 |
| 重启原因 | `ipmitool chassis status \| grep -i "last"` | 上次重启原因 |
| 电源状态 | `ipmitool power status` | 电源开关状态 |
| FRU 信息 | `ipmitool fru print` | 硬件资产信息 |
| LAN 配置 | `ipmitool lan print 1` | BMC 网络配置 |
| SOL 连接 | `ipmitool sol activate` | 串口重定向 |

## K8s 容器层

| 目的 | 命令 | 说明 |
|:-----|:-----|:-----|
| Pod 状态 | `kubectl get pods -A \| grep -v Running` | 所有非 Running 的 Pod |
| Pod 详情 | `kubectl describe pod <name> -n <ns>` | Pod 事件 + Conditions |
| 容器日志 | `kubectl logs --tail=50 <pod> -n <ns>` | 最近 50 行日志 |
| 节点状态 | `kubectl get nodes -o wide` | 节点状态 + 内核版本 |
| 节点资源 | `kubectl top nodes; kubectl top pods -A` | 节点/Pod 资源使用 |
| 事件排序 | `kubectl get events -A --sort-by='.lastTimestamp'` | 按时间排序的集群事件 |
| 资源 YAML | `kubectl get pod <name> -n <ns> -o yaml` | Pod 完整配置 |

## 磁盘/文件系统排障专项

| 场景 | 命令序列 |
|:-----|:---------|
| IO 高但不知道哪个盘 | `iostat -x 1 3` 看哪个盘的 `%util` 高 |
| 找到了高 IO 盘 | `iotop -o -b -d 1 -n 5` 找具体进程 |
| 磁盘空间满 | `df -h` → `du -sh /tmp /var /home 2>/dev/null` → 逐层 |
| 文件删了空间没释放 | `lsof \| grep deleted` 找未释放 fd |
| 根分区满 | `du -sh /* 2>/dev/null \| sort -rh \| head -10` |

## 性能分析专项

| 方法 | 命令 | 说明 |
|:-----|:-----|:-----|
| 60 秒快速分析 | `uptime; dmesg -T \| tail; vmstat 1; mpstat -P ALL 1; pidstat 1; iostat -xz 1; free -m; sar -n DEV 1; sar -n TCP,ETCP 1; top` | USE 方法（Brendan Gregg） |
| 热点函数 | `perf top -e cycles -k 1` | 内核/用户态热点 |
| 系统调用 | `strace -c -p <pid>` | 统计系统调用分布 |
| 文件 IO | `strace -e trace=read,write,open,close -p <pid> 2>&1 \| head` | 跟踪文件操作 |
| 内存映射 | `pmap -x <pid> \| sort -k3 -nr \| head` | 进程内存分布 |
| 网络连接 | `ss -tanp \| grep <port>` | 特定端口的连接详情 |

## 参考来源

- Brendan Gregg's USE Method
- Linux Performance Observability Tools (perf, ftrace, eBPF)
- 知识库方法论：[事件墙](../knowledge/06_others/sources/2026-06-18-event-wall-root-cause-analysis.md)
- 知识库方法论：[五层诊断架构](../knowledge/reliability-testing/storage-device-diagnostic-architecture.md)
