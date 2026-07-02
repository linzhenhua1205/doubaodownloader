# ⚡ 万卡集群与训推优化 — 行业跟踪框架

## 核心跟踪问题
- 分布式训练优化（3D并行/序列并行/专家并行）进展？
- 推理优化（PD分离/continuous batching/speculative decoding）
- 万卡集群部署案例（规模/拓扑/网络架构）
- 集群利用率/GPU利用率提升方案
- 推理引擎新发布（vLLM/SGLang/RTP-LLM/TensorRT-LLM）

## 搜索关键词
- `speculative decoding 2026` `PD-disaggregation deployment`
- `distributed training optimization` `large scale training cluster 10K GPU`
- `GPU utilization optimization` `training efficiency`
- `万卡集群` `训推一体化` `推理优化 2026`
- `arXiv:2606` (最新6月论文，结合 spec decode / MoE / training 等关键词)

## 来源优先级

| 优先级 | 来源 | 说明 |
|:-----:|:-----|:-----|
| 🥇 Tier 1 | **arXiv.org** | 学术前沿，按 cs.CL/cs.LG/ cs.DC 分类浏览最新3天 |
| 🥇 Tier 1 | **NVIDIA Technical Blog** | 工业级方案发布 |
| 🥈 Tier 2 | **Hugging Face Daily Papers** | 精选论文汇总 |
| 🥈 Tier 2 | **Meta / Google / Microsoft Research Blogs** | 大厂工程实践 |
| 🥉 Tier 3 | **OCP / ODCC 技术论坛** | 开放标准进展 |
| 🥉 Tier 3 | **TechCrunch / The Verge** | 行业新闻 |

## 质量门槛
- ✅ **值得记录**：有新论文/新发布/新案例（提供 arXiv ID/URL）
- ✅ **深度追踪**：该领域标志性工作（多篇对比/趋势判断）
- ❌ **跳过**：二手转载/无具体数据的新闻报道/营销内容
- 每发现需标注来源 URL 或 arXiv ID

## 输出模板

```markdown
# ⚡ 万卡集群与训推优化 — 当日动态 YYYY-MM-DD

> 采集时间: YYYY-MM-DD HH:MM | 来源: {来源列表}

---

## {分类标题}

### {条目标题} ({来源}, {日期})
- {关键发现}
- {数据/指标}
- 📌 【深度跟踪】{判断/洞察}

---
## 📊 趋势判断

| 方向 | 热度 | 关键信号 |
|:-----|:----|:---------|
| {方向} | {🔥评级} | {信号} |
```

## 输出路径
- `knowledge/01_survey/cluster-training/YYYY-MM-DD.md`

## 交叉引用
- 推理优化 ↔ `distributed-os/` (KV Cache 管理/集合通信)
- 训练效率 ↔ `reliability-testing/` (慢节点检测/容错)
- 训练集群 ↔ `data-center/` (供电散热)
