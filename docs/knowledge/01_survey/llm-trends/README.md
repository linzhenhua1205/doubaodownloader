# 大模型动态

> 大语言模型演进、能力边界、发布动态

## 范围
- 主流大模型发布与迭代（GPT、Claude、Gemini、DeepSeek、Llama等）
- 模型架构演进（Dense、MoE、多模态）
- **模型原理**: Transformer 架构、注意力机制（QKV）、位置编码、归一化
- **训练方法**: 预训练、SFT、RLHF、DPO、GRPO、强化学习对齐
- **推理方法**: Chain-of-Thought、Tree-of-Thought、推理时扩展
- **评估体系**: 模型能力评测基准、多模态评估、安全性评估
- 模型能力评估与对比
- 大模型训练方法论（RLHF、DPO、SFT等）

## 标签
`LLM` `大模型` `GPT` `Claude` `DeepSeek` `模型能力` `Transformer` `RLHF`

## 关联模块
- [AI应用](../../05_tools/methodology-tools/README.md) — 模型驱动的上层应用
- [万卡集群与训推优化](../../05_tools/methodology-tools/README.md) — 模型训练的基础设施

## 📋 可回答的关键问题

**模型原理**
- Transformer 的注意力机制如何工作？QKV 的含义是什么？
- 位置编码（绝对/相对/RoPE/ALiBi）的区别与选择
- 归一化（LayerNorm/RMSNorm）对训练稳定性的影响

**训练与对齐**
- 预训练、SFT、RLHF、DPO 各解决什么问题？
- RLHF 的 Reward Model 如何训练？PPO 与 GRPO 的区别？
- 模型对齐中的幻觉问题如何缓解？

**推理优化**
- Chain-of-Thought 如何实现推理能力提升？
- Tree-of-Thought 与思维链的区别与适用场景
- 推理时扩展（Test-Time Compute）的前沿进展

> 关联工具: [豆包问题索引](../../03_AI/notes/doubao-questions-index.md) — 52个大模型相关问题
