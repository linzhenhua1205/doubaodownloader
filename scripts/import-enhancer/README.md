# 📦 import 目录增强系统 — 使用手册

> 本地轻量工具：对 import 目录素材做 **L0 规范化 / L1 轻增强 / L2 深增强**，32K 上下文约束，不覆盖源文件。
> 设计依据：[本地增强工具设计方案](knowledge/05_tools/knowledge-management/2026-08-13-local-import-enhancer-design.md) + [专场应用场景](knowledge/05_tools/knowledge-management/2026-08-13-local-import-enhancer-applications.md)

## 目录结构

```
scripts/import-enhancer/
├── l0_normalize.py    # L0 格式规范化（零依赖，立即可用）
├── chunk.py           # 分片器（核心组件，可独立测试）
├── enhancer.py        # 增强调度器（L1/L2 + 状态机断点续传）
├── llm_client.py      # Ollama 客户端（自动降级 3B）
├── prompts/           # 指令头模板（L1_enhance.md / L2_enhance.md）
├── config.json        # 配置（模型/阈值/优先级）
└── README.md          # 本手册
```

## 环境准备（一次性）

```bash
# 1. 安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. 拉取模型（RTX5060 8G 推荐 Q4 量化）
ollama pull qwen2.5:3b-instruct-q4_K_M    # L1 轻增强（~2G）
ollama pull qwen2.5:7b-instruct-q4_K_M    # L2 深增强（~4.7G）

# 3. 启动服务
ollama serve                               # 或 systemctl start ollama
```

## 三步流程

### Step 1: L0 全量规范化（零依赖，10 分钟跑完全库）

```bash
# 全部 import（约 19,864 文件）
python3 scripts/import-enhancer/l0_normalize.py \
    --input import --output import-enhanced

# 单目录 + 先试跑前 50 个（dry-run 只统计不写盘）
python3 scripts/import-enhancer/l0_normalize.py \
    --input import/server --output import-enhanced/server --limit 50 --dry-run
```

产物：`import-enhanced/<镜像目录>/<文件>` + `manifest.json`（编码修复/frontmatter 补全统计）。

### Step 2: L1 轻增强（小文件优先，3B 模型）

```bash
# 小文件优先 + 限 20 个试跑（dry-run 不调 LLM）
python3 scripts/import-enhancer/enhancer.py \
    --input import-enhanced --output import-enhanced/out \
    --small-first --limit 20 --dry-run

# 正式跑（夜间无人值守推荐）
nohup python3 scripts/import-enhancer/enhancer.py \
    --input import-enhanced --output import-enhanced/out \
    --small-first > /tmp/enhancer-L1.log 2>&1 &
```

### Step 3: L2 深增强（A 类精选，7B 模型）

```bash
# 只处理 server/ 目录（业务核心）
python3 scripts/import-enhancer/enhancer.py \
    --input import-enhanced/server --output import-enhanced/out \
    --level L2 --limit 5
```

## 状态与断点续传

- 状态机落盘：`<output>/state.json`（每文件 status: pending/processing/done/failed）
- **重复运行自动跳过 done**，失败文件重试 2 次后记录 failed
- 中断后重跑同一命令即可续传

## 常用参数

| 参数 | 说明 |
|:-----|:-----|
| `--input` / `--output` | 输入（L0 产物）/ 输出（增强产物，不覆盖源） |
| `--level L1\|L2` | 强制级别；默认 auto（≤5KB→L1，≥20KB→L2） |
| `--small-first` | 小文件优先（吞吐最大化） |
| `--limit N` | 仅处理前 N 个（调试） |
| `--dry-run` | 只走流程，不调 LLM、不写盘 |

## 质量保障提醒

1. **产物是素材加工品**：增强结果（`【补】`/`【规格】`标记）未经人工复核不得直接入库
2. **抽检 5%**：重点看是否有"新增事实错误"（幻觉）
3. **入库走标准流程**：审核后按知识库三件套纪律（`kb-log-append.py` + 索引脚本）写入 knowledge/

## 常见问题

| 问题 | 处理 |
|:-----|:-----|
| `Ollama 未在线` | 启动 `ollama serve`，或 `curl http://127.0.0.1:11434/api/tags` 验证 |
| 7B 显存不足（OOM） | config.json 调低 `num_ctx` 到 4096；或改用 3B（L2 降级自动发生） |
| 产物乱码 | 确认先跑 L0（编码修复），L1/L2 读 L0 产物 |
| 想清理重跑 | 删除 `<output>/state.json` 后重跑 |

## 测试

```bash
# 分片器自测（输出分片统计）
python3 scripts/import-enhancer/chunk.py 某大文件.md 12000

# LLM 连通测试
python3 scripts/import-enhancer/llm_client.py
```
