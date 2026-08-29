---
name: github-activity-report
description: 每日 GitHub 开源活动日报生成器。聚合 AI/部件/项目管理/Agent/算力平台/运维/云计算/操作系统 8 领域的热点项目最新进展，覆盖最新亮点项目（star 飙升/新发布）与成熟项目关键提交（commits/releases）。Use when generating daily GitHub activity reports, tracking open-source project progress, or surveying trending repos. | github日报, 开源项目追踪, 热点仓库, 关键提交, trending, open source activity
license: MIT
metadata:
  author: lzh
  version: "1.0"
  tags:
    - github
    - daily
    - opensource
    - tracking
---

# GitHub 开源活动日报 Skill

每日 06:50 定时任务专用。聚合 8 领域热点仓库的最新进展，输出结构化日报到 `knowledge/01_survey/github/YYYY-MM-DD.md`。

## 适用场景

- 每日 GitHub 开源活动报告（定时任务）
- 用户询问某领域开源项目最新进展
- 追踪成熟项目（vLLM/K8s/Linux 等）的关键提交与发布

## 8 领域仓库清单（SSOT）

> 清单按领域维护，可按需增删。`★` 为核心仓库（每领域必查提交）；其余为亮点候选（按当日搜索/趋势结果动态补充）。

### 1️⃣ AI（推理/训练框架）
- ★ `vllm-project/vllm` — LLM 推理引擎（核心）
- ★ `pytorch/pytorch` — 深度学习框架（核心）
- `NVIDIA/TensorRT-LLM` — NVIDIA 推理栈
- `huggingface/transformers` — 模型生态
- `deepseek-ai/DeepSeek-V3` — 国产开源模型
- `hpcaitech/ColossalAI` — 大模型训练系统
- `Dao-AILab/flash-attention` — 注意力加速
- `ollama/ollama` — 本地推理工具

### 2️⃣ 部件（硬件/固件/存储）
- ★ `tianocore/edk2` — UEFI 固件（核心）
- ★ `ceph/ceph` — 分布式存储（核心）
- `coreboot/coreboot` — 开源固件
- `openzfs/zfs` — ZFS 文件系统
- `linux-nvme/nvme-cli` — NVMe 工具
- `opencomputeproject/OCP` — 开放计算（如可访问）

### 3️⃣ 项目管理（研发效能/协作）
- ★ `toeverything/AFFiNE` — 知识协作（核心）
- ★ `AppFlowy-IO/AppFlowy` — 开源 Notion（核心）
- `logseq/logseq` — 大纲知识库
- `frappe/frappe` — 低代码业务框架
- `mermaid-js/mermaid` — 文档图表

### 4️⃣ Agent（智能体框架）
- ★ `langchain-ai/langgraph` — Agent 编排（核心）
- ★ `openai/openai-agents-python` — OpenAI Agents SDK（核心）
- `langchain-ai/langchain` — LLM 应用框架
- `microsoft/autogen` — 多 Agent 框架
- `crewAIInc/crewAI` — 角色协作框架
- `run-llama/llama_index` — 数据框架

### 5️⃣ 算力平台（调度/分布式训练/集合通信）
- ★ `ray-project/ray` — 分布式计算（核心）
- ★ `NVIDIA/nccl` — 集合通信（核心）
- `volcano-sh/volcano` — K8s 批调度
- `kubernetes-sigs/kueue` — 队列调度
- `NVIDIA/Megatron-LM` — 大模型训练
- `hpcaitech/ColossalAI` — 训练系统

### 6️⃣ 运维（可观测/监控/GitOps）
- ★ `grafana/grafana` — 可观测平台（核心）
- ★ `prometheus/prometheus` — 监控（核心）
- `open-telemetry/opentelemetry-collector` — 遥测采集
- `argoproj/argo-cd` — GitOps
- `VictoriaMetrics/VictoriaMetrics` — 时序库
- `Thanos-io/thanos` — 高可用 Prometheus

### 7️⃣ 云计算（K8s/容器/网络）
- ★ `kubernetes/kubernetes` — 容器编排（核心）
- ★ `containerd/containerd` — 容器运行时（核心）
- `cilium/cilium` — eBPF 网络
- `istio/istio` — 服务网格
- `envoyproxy/envoy` — 数据面代理
- `k3s-io/k3s` — 轻量 K8s
- `crossplane/crossplane` — 云资源编排

### 8️⃣ 操作系统（内核/系统组件）
- ★ `torvalds/linux` — Linux 内核（核心）
- ★ `systemd/systemd` — 系统管理（核心）
- `rust-lang/rust` — 系统语言
- `freebsd/freebsd-src` — FreeBSD 源码
- `moby/moby` — 容器引擎

## 数据获取策略（按优先级）

> ⚠️ 当前环境网络搜索（web_search）常不可用，**优先直连 GitHub API/网页**。

### 方案 A：GitHub REST API（首选，免认证 60 req/h）
```bash
# 单仓库元数据（star/最近更新/描述）
curl -s https://api.github.com/repos/{owner}/{repo}

# 最近 N 条提交（since 过滤）
curl -s "https://api.github.com/repos/{owner}/{repo}/commits?per_page=10&since=YYYY-MM-DDTHH:MM:SSZ"

# 最近发布
curl -s "https://api.github.com/repos/{owner}/{repo}/releases?per_page=5"

# 某日新仓库（亮点候选）
curl -s "https://api.github.com/search/repositories?q=created:>YYYY-MM-DD&sort=stars&order=desc&per_page=20"

# 亮点 star 批量获取（单次请求拿全部亮点 star，勿逐仓库 curl）
curl -s "https://api.github.com/search/repositories?q=repo:a/b+repo:c/d&per_page=20"
```
**预算控制**：8 核心仓库 commits（8 req）+ 亮点搜索（2-3 req）+ 异常重试 → 单日 < 30 req，安全。
**教训（2026-08-08）**：亮点 star 一律用 search API 单次批量（`q=repo:a/b+repo:c/d`），逐仓库 curl 会把免认证配额烧爆（曾 59 req/日）；改批量后 core 请求 59→32，全程 ≤35 req。

### 方案 B：web_fetch 直连 GitHub 页面（API 限流时）
```bash
# 趋势页（按日）
https://github.com/trending?since=daily
# 单仓库提交页
https://github.com/{owner}/{repo}/commits
# 单仓库 Release 页
https://github.com/{owner}/{repo}/releases
```

### 方案 C：镜像/聚合站（B 也失败时）
- `https://github-trending-api.vercel.app/repositories?since=daily`（Trending API 镜像）
- 用 `curl -sL -A "Mozilla/5.0" <url>` 规避简单 UA 拦截

## 报告模板（输出到 `knowledge/01_survey/github/YYYY-MM-DD.md`）

```markdown
# GitHub 开源活动日报（YYYY-MM-DD）

> 生成时间: YYYY-MM-DD HH:MM | 数据源: GitHub API/趋势页 | 覆盖 8 领域

## 📌 今日头条（TOP 3）
1. **<仓库>** — <一句话亮点>（star +N / 关键提交 / 新发布）
2. ...

## 🆕 最新亮点项目
| 领域 | 仓库 | 说明 | star |
|:-----|:-----|:-----|:----:|
| ... | ... | ... | ... |

## 🔑 成熟项目关键提交/发布
### 1️⃣ AI
- **vllm-project/vllm** — 最近提交: <commit msg>（<sha 前7位>）· <日期>
- **pytorch/pytorch** — 发布: <tag>（<日期>）
### 2️⃣ 部件
...
### 8️⃣ 操作系统
- **torvalds/linux** — 最近提交: <msg>

## 💡 交叉洞察（与知识库联动）
- <新信号与 knowledge/ 已有跟踪主题的关联，如 MoE→硬件 / 超节点 / Agent 编排>

---
**统计**: 覆盖 X 仓库 · Y 条关键提交 · Z 个亮点项目
```

## 后处理（必做）

1. **只生成日期文件**：输出固定为 `knowledge/01_survey/github/YYYY-MM-DD.md`；**不更新** `index.md` / `log.md`（降 token：01_survey 调研日报只写日期文件，索引由脚本批量维护，AI 不手工编辑）
2. **交叉信号**：若发现与已有专题（MoE→硬件 / 超节点 / 分布式 OS / Agent 编排）强相关的提交，在当日 `memory/YYYY-MM-DD.md` 标注，供深度分析任务接力
3. **质量自检**：数据须带来源（API/页面）+ 日期；star 数值须标注抓取时间；提交信息须带 sha 前缀

## 注意事项

- **诚实标注**: API 限流/网络失败时，在报告头部标注"数据源降级: 仅覆盖 X 领域"，绝不编造提交/star 数据
- **预算控制**: 单次运行 API 调用 ≤ 35 次（免认证限额 60/h 的安全余量）
- **时区**: 提交日期均为 UTC，报告内统一转为 UTC+8 标注
