# 🖥️ 运维运营系统 — 行业跟踪框架

## 核心跟踪问题
- 监控系统（Prometheus/Grafana/OpenTelemetry）新版本/新功能
- CMDB/资源管理系统进展
- AIOps / 智能运维新方案
- K8s 运维工具更新（KEDA/Kuberhealthy/Cluster API）
- 数据中心运维自动化/AI 工厂运维

## 搜索关键词
- `OpenTelemetry latest` `Prometheus new release`
- `AIOps 2026` `intelligent operations AI`
- `Kubernetes operations` `KEDA` `cluster autoscaler`
- `AI factory operations` `data center automation`
- `运维自动化` `智能运维`

## 来源优先级

| 优先级 | 来源 | 说明 |
|:-----:|:-----|:-----|
| 🥇 Tier 1 | **CNCF 官方博客/发布** | Prometheus/OpenTelemetry 等毕业项目 |
| 🥇 Tier 1 | **GitHub Release Notes** (kube-prometheus/OTel/KEDA) | 直接看 changelog |
| 🥈 Tier 2 | **NVIDIA DSX / DCGM** 官方文档 | GPU 运维方案 |
| 🥈 Tier 2 | **Google / Meta SRE Blogs** | 大规模运维实践 |
| 🥉 Tier 3 | **The New Stack / InfoQ** | 运维工具综述 |

## 质量门槛
- ✅ **值得记录**：新版本发布/新开源项目/性能提升数据
- ✅ **深度追踪**：对整个运维体系有影响的架构变化
- ❌ **跳过**：产品宣传稿/无具体版本的新闻

## 输出模板

```markdown
# 🖥️ 运维运营系统 — 当日动态 YYYY-MM-DD

...

## 📊 趋势判断
```

## 输出路径
- `knowledge/01_survey/ops-system/YYYY-MM-DD.md`

## 交叉引用
- GPU 运维 ↔ `cluster-training/` (Dynamo/DCGM)
- K8s 管理 ↔ `linux-os/` (容器运行时/K8s 版本)
