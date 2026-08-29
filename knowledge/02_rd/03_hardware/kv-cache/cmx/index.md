# NVIDIA CMX (Context Memory X) 专题

> **专题**: KV Cache 共享存储 · G3.5 层 · DPU 全卸载 · 解耦推理
> **父专题**: [KV Cache 专题](../index.md)
> **文件数**: 3 | **创建日期**: 2026-06-30

| 文件 | 主题 | 行数 | 来源 |
|:----|:-----|:----|:-----|
| [`nvidia-cmx-platform.md`](nvidia-cmx-platform.md) | CMX 硬件平台 — BF4 DPU · 存储架构 · Tray 设计 | 264 | NVIDIA 官方白皮书 |
| [`2026-06-29-nvidia-cmx-deep-architecture-analysis.md`](2026-06-29-nvidia-cmx-deep-architecture-analysis.md) | CMX 深度架构分析 — 算力·调度·存储三维拆解 · 非 NVIDIA 等价实现 | 407 | 行业调研 + 豆包对话 |
| [`2026-06-29-nvidia-cmx-software-architecture.md`](2026-06-29-nvidia-cmx-software-architecture.md) | CMX 软件架构深度分析与适配指南 — KV Cache 传输引擎对比 · 256GPU 部署 | 457 | 豆包对话源扩展 |

## 🔗 交叉引用

| 文件 | 关联方式 |
|:----|:---------|
| [`../g35-kv-cache-storage-network-analysis.md`](../g35-kv-cache-storage-network-analysis.md) | CMX 所属 G3.5 层的带宽逐层计算（本目录） |
| [`../../06_superpod/supernode-performance-evaluation-framework.md`](../../06_superpod/supernode-performance-evaluation-framework.md) | §4.3 CMX 特化评估, §6.4 CMX 性能基线 |
| [`../../06_superpod/supernode-ai-performance-metrics-handbook.md`](../../06_superpod/supernode-ai-performance-metrics-handbook.md) | §KV Cache 共享存储评估方案, CMX G3.5 性能数据表 |
| [`../../06_superpod/standards/odcc-2026-summer-deep-analysis.md`](../../06_superpod/standards/odcc-2026-summer-deep-analysis.md) | §5.4 ODS vs CMX 深度对标 |
| [`../../../05_software/ai-technology-evolution-annual-summary.md`](../../../05_software/ai-technology-evolution-annual-summary.md) | AI 年度技术演进记录中引用 CMX 定位 |
| [`../../../../03_AI/nvidia-archives/nvidia-vera-rubin-pod.md`](../../../../03_AI/nvidia-archives/nvidia-vera-rubin-pod.md) | Vera Rubin POD 中 CMX 作为存储组件 |
| [`../../../../03_AI/llm-techniques-principles/README.md`](../../../../03_AI/llm-techniques-principles/README.md) | LLM 推理技术体系中 CMX 的 KV Cache 优化背景 |

## 📅 更新日志

- **2026-06-30**: CMX 随 KV Cache 专题迁移至 `02_rd/03_hardware/kv-cache/cmx/`
- **2026-06-30**: 从 `03_AI/` 迁移至 `06_superpod/cmx/`，建立 CMX 专题目录
