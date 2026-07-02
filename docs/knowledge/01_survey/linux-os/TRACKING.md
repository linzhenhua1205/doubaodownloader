# 🐧 操作系统（Linux） — 行业跟踪框架

## 核心跟踪问题
- Linux 内核新特性（调度器/CXL 支持/IO_uring）
- K8s 新版本发布/关键特性
- 容器运行时（containerd/CRI-O）更新
- 安全漏洞/供应链攻击事件
- 操作系统性能优化（内存/网络/存储子系统）

## 搜索关键词
- `Linux kernel new feature` `kernel 6.x` `CXL Linux`
- `Kubernetes new release` `k8s 1.x` `KEP`
- `容器安全` `container runtime` `containerd`
- `Linux security vulnerability` `supply chain attack`
- `CXL Linux support` `IO_uring` `perf optimization`

## 来源优先级

| 优先级 | 来源 | 说明 |
|:-----:|:-----|:-----|
| 🥇 Tier 1 | **Kernel.org / LWN.net** | 内核邮件列表精选 |
| 🥇 Tier 1 | **Kubernetes 官方 changelog / KEPs** | 版本特性 |
| 🥇 Tier 1 | **RedHat / Ubuntu 发布说明** | 企业版更新 |
| 🥈 Tier 2 | **Phoronix** | 性能 benchmark |
| 🥈 Tier 2 | **CVE 数据库 / NIST NVD** | 安全漏洞 |
| 🥉 Tier 3 | **The Register / ZDNet** | 行业新闻 |

## 质量门槛
- ✅ **值得记录**：新内核特性/性能提升数据/K8s 新 API GA/安全漏洞 CVE
- ❌ **跳过**：二次转载/无基准测试的版本发布新闻

## 输出路径
- `knowledge/01_survey/linux-os/YYYY-MM-DD.md`

## 交叉引用
- CXL 支持 ↔ `components-storage/` (CXL 内存池)
- K8s 调度 ↔ `distributed-os/` (拓扑感知)
