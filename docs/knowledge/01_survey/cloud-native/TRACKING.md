# ☸️ 云原生 — 行业跟踪框架

## 核心跟踪问题
- Kubernetes 新版本发布/关键特性（调度/网络/存储/安全）
- CNCF 项目毕业/孵化/废弃动态
- 容器运行时（containerd/cri-o）和容器引擎更新
- 服务网格（Istio/Linkerd/Envoy）架构演进
- eBPF/Cilium 在云原生领域的应用突破
- Serverless 和 FaaS 平台发展
- 云原生安全（供应链安全/运行时安全/策略引擎）
- GitOps 和平台工程（Platform Engineering）趋势

## 搜索关键词
- `Kubernetes new release` `k8s 1.x` `KEP` `sig-node` `sig-network`
- `CNCF graduated project` `CNCF incubating` `TOC vote`
- `containerd` `cri-o` `WASM container` `podman`
- `Cilium` `eBPF cloud native` `service mesh`
- `Istio ambient mesh` `Linkerd` `Envoy proxy`
- `platform engineering` `Backstage` `IDP`
- `cloud native security` `supply chain` `OPA/Gatekeeper`
- `Knative` `serverless kubernetes`
- `ArgoCD` `GitOps` `Tekton` `Flux`

## 来源优先级

| 优先级 | 来源 | 说明 |
|:-----:|:-----|:-----|
| 🥇 Tier 1 | **Kubernetes 官方 changelog / KEPs / CNCF Blog** | 一手特性 + 项目动态 |
| 🥇 Tier 1 | **Istio / Cilium / containerd 官方发布说明** | 核心组件更新 |
| 🥇 Tier 1 | **CNCF TOC 会议 / KubeCon 议程** | 战略方向 |
| 🥈 Tier 2 | **The New Stack / InfoQ** | 深度技术分析 |
| 🥈 Tier 2 | **RedHat / VMware / AWS 云原生博客** | 企业实践 |
| 🥉 Tier 3 | **GitHub Release Notes / Stack Overflow** | 社区动态 |

## 质量门槛
- ✅ **值得记录**：K8s 新 API GA/CNCF 毕业项目/CVE 严重漏洞/架构级变更
- ❌ **跳过**：纯发布通告无技术细节/重复转载/非核心项目次要更新

## 输出路径
- `knowledge/01_survey/cloud-native/YYYY-MM-DD.md`

## 交叉引用
- K8s 调度 ↔ `cluster-training/` (AI 工作负载编排)
- eBPF ↔ `linux-os/` (内核 eBPF 能力)
- 监控/Prometheus ↔ `ops-system/` (AIOps 运维)
- 容器存储 ↔ `components-storage/` (CSI/Ceph/Rook)
