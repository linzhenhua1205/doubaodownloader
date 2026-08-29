# 🚀 部署与执行方案（Ollama + Qwen2.5）

> 版本: v1.0 | 日期: 2026-08-13 | 状态: 待部署
> 适用硬件: 16G 内存 / 20 核 CPU / RTX5060 8G / 512G NVMe
> 设计依据: [设计方案](knowledge/05_tools/knowledge-management/2026-08-13-local-import-enhancer-design.md) · [应用场景](knowledge/05_tools/knowledge-management/2026-08-13-local-import-enhancer-applications.md)

---

## 0. 部署总览

```
┌────────────────────────────────────────────────────────────┐
│ 目标系统: 本地 PC (16G RAM / 20核 / RTX5060 8G / 512G NVMe)  │
├────────────────────────────────────────────────────────────┤
│ 软件栈:  Python3 + Ollama + qwen2.5:3b + qwen2.5:7b (Q4)    │
├────────────────────────────────────────────────────────────┤
│ 工具:    scripts/import-enhancer/ (8 文件, 884 行, 零依赖)    │
├────────────────────────────────────────────────────────────┤
│ 流程:    Day0 环境 → Day1 L0全量(10min) → L1小文件(3天夜间)    │
│          → L2精选(6-7天后台) → 每周抽检审核入库                │
└────────────────────────────────────────────────────────────┘
```

**执行前提**（用户已确认）：
- ✅ 模型选型: Ollama + qwen2.5 系列（3B 轻增强 / 7B 深增强）
- ✅ 暂不执行，本方案供部署时对照执行

---

## 1. 前置检查（Day 0 第一步，10 分钟）

```bash
# 1.1 硬件确认
free -h                          # 内存 ≥16G
nproc                            # 核心数 ≥8
nvidia-smi                       # 显存 ≥8G, 驱动正常
df -h /                         # 磁盘剩余 ≥30G (模型~8G + 产物~2G)

# 1.2 Python 版本
python3 --version                # 需 ≥3.8 (标准库即可, 零第三方依赖)

# 1.3 端口占用检查 (Ollama 默认 11434)
ss -tlnp | grep 11434 || echo "端口空闲 ✅"
```

**通过标准**: 五项全部满足；nvidia-smi 显示 RTX5060 8G。

---

## 2. 环境安装（Day 0，30-60 分钟）

### 2.1 安装 Ollama（Linux）

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama --version
```

> Windows: 下载安装包 https://ollama.com/download/windows ；macOS: https://ollama.com/download/mac

### 2.2 拉取模型（Q4 量化，匹配 8G 显存）

```bash
# L1 轻增强模型 (~2.0G)
ollama pull qwen2.5:3b-instruct-q4_K_M

# L2 深增强模型 (~4.7G)
ollama pull qwen2.5:7b-instruct-q4_K_M

# 验证已拉取
ollama list
```

### 2.3 启动服务并验证

```bash
# 前台启动(调试) 或 systemd(生产)
ollama serve &
# 或: systemctl start ollama

# 连通性验证
curl -s http://127.0.0.1:11434/api/tags | head -c 300
# 预期: {"models":[{"name":"qwen2.5:3b-instruct-q4_K_M",...}]}

# 冒烟测试(7B 最快路径)
curl -s http://127.0.0.1:11434/api/generate \
  -d '{"model":"qwen2.5:7b-instruct-q4_K_M","prompt":"回复:OK","stream":false}' \
  | python3 -c "import json,sys; print(json.load(sys.stdin).get('response','FAIL'))"
# 预期输出: OK
```

**通过标准**: `ollama list` 显示 2 个模型；冒烟测试返回 OK。

---

## 3. 参数调优（RTX5060 8G 专用）

> 8G 显存跑 7B Q4（4.7G 权重）：KV cache 与运行开销需严格控制。

```bash
# 查看默认端口服务日志, 确认加载无 OOM
journalctl -u ollama -f   # systemd 方式

# 若出现 CUDA OOM 或显存不足:
# 方案A: 降低上下文(推荐, 与 32K 设计一致)
#   config.json 中 num_ctx: 8192 → 4096
# 方案B: 限制 GPU 层数, 部分 offload CPU
#   OLLAMA_GPU_LAYERS=20 ollama serve
# 方案C: 7B 任务降级 3B (llm_client 已内置自动降级)
```

**推荐配置**（已写入 config.json）：
```json
{
  "ollama": {
    "num_ctx": 8192,
    "models": {
      "L1": "qwen2.5:3b-instruct-q4_K_M",
      "L2": "qwen2.5:7b-instruct-q4_K_M"
    }
  }
}
```

---

## 4. 文件准备（拷贝工具到目标机）

```bash
# 从开发机同步工具目录(任选其一)
rsync -av scripts/import-enhancer/ 目标机:/path/to/import-enhancer/
# 或: scp -r scripts/import-enhancer 目标机:/path/to/
# 或: 走 git 仓库

# 目标机验证
cd /path/to/import-enhancer
python3 -m py_compile *.py && echo "语法 OK ✅"
```

> import/ 素材目录与工具放同一磁盘分区（读快）；产物目录建议同盘（`import-enhanced/`）。

---

## 5. 执行流程（三步，可随时中断续传）

### Step 1: L0 全量规范化（零依赖，10 分钟）

```bash
cd /path/to/import-enhancer

# 1a. 先 dry-run 全库统计(不写盘)
python3 l0_normalize.py --input import --output import-enhanced --dry-run
# 预期: ok≈文本文件数, binary_skip≈非文本数

# 1b. 正式执行
python3 l0_normalize.py --input import --output import-enhanced

# 1c. 查看 manifest 摘要
python3 -c "
import json
m = json.load(open('import-enhanced/manifest.json'))
print('counts:', m['counts'])
print('编码修复数:', sum(1 for f in m['files'] if f.get('encoding_fixed')))
print('frontmatter补全数:', sum(1 for f in m['files'] if f.get('frontmatter_added')))
"
```

**产出**: `import-enhanced/`（镜像结构）+ `manifest.json`（文件清单/状态）。
**验收**: 编码修复与 frontmatter 补全数量合理（无全量报错）。

### Step 2: L1 轻增强（小文件优先，3B，夜间跑）

```bash
# 2a. 试跑 20 个 (dry-run 走全流程, 不调 LLM 不写盘)
python3 enhancer.py --input import-enhanced --output import-enhanced/out \
    --small-first --limit 20 --dry-run

# 2b. 真实跑 5 个验证 LLM 链路
python3 enhancer.py --input import-enhanced --output import-enhanced/out \
    --small-first --limit 5

# 2c. 检查产物质量(抽 1 个)
cat import-enhanced/out/$(python3 -c "
import json,os
s=json.load(open('import-enhanced/out/state.json'))
print([k for k,v in s.items() if v['status']=='done'][0])")

# 2d. 正式全量(后台, 断点可续)
nohup python3 enhancer.py --input import-enhanced --output import-enhanced/out \
    --small-first > /tmp/enhancer-L1.log 2>&1 &
tail -f /tmp/enhancer-L1.log
```

**产出**: `import-enhanced/out/<镜像路径>`（含 frontmatter+摘要+标签）+ `state.json`。
**验收**: 日志无连续失败；抽样产物格式正确、无新增事实。

### Step 3: L2 深增强（A 类精选，7B，后台）

```bash
# 3a. 先处理业务核心 server/ (限 5 个验证)
python3 enhancer.py --input import-enhanced/server \
    --output import-enhanced/out --level L2 --limit 5

# 3b. 全量 A 类(按优先级目录分批)
nohup python3 enhancer.py --input import-enhanced/server \
    --output import-enhanced/out --level L2 > /tmp/enhancer-L2-server.log 2>&1 &
# 完成后依次: md/ → work/ (work 大文件多, 最后跑)
```

**产出**: 技术卡片（结构+信息点+逻辑链标记）。
**验收**: 抽检 5%：信息点标注准确、无幻觉新增。

---

## 6. 调度与自动化（长期运行策略）

| 时段 | 任务 | 方式 |
|:-----|:-----|:-----|
| 白天间隙 | L2 精选（交互可抽查） | 前台小批量 |
| 夜间 22:00-08:00 | L1 批量（3B 吞吐优先） | nohup 后台 |
| 周末 | L0 刷新 + L2 大文件 | 长任务窗口 |
| 每周日 | 抽检 5% + 审核产物 | 人工 |

**并行建议**（20 核）：
```bash
# 同时跑 2 个 3B 实例(不同目录), 7B 只开 1 个
# 通过 --input 指定不同子目录即可并行
```

---

## 7. 质量检查与验收标准

### 7.1 每批抽检清单（5% 样本）
- [ ] frontmatter: title/date/tags 合理（无 unknown 滥用）
- [ ] 摘要: 基于原文压缩，无新增事实
- [ ] 信息点: 【规格】【论断】等标记准确（分类不误）
- [ ] 原文未被改写/删除（diff 可对比）
- [ ] 无幻觉: 无外部数据混入

### 7.2 量化验收标准

| 指标 | 目标 |
|:-----|:-----|
| L0 完成率 | 100% 文本文件（fail=0） |
| L1 小文件处理 | 4,158 个 ≤5KB 全部完成 |
| L2 A 类完成 | server/ 优先，目标 ≥200 个 |
| 抽样通过率 | ≥90%（5% 样本） |
| 断点续传 | 中断重跑无重复处理 |

### 7.3 diff 快速审查
```bash
# 对比原文与增强产物(抽检)
diff <(sed '1,8d' import-enhanced/out/<file>) <(head -100 import/<同路径文件>) | head -20
```

---

## 8. 问题排查（FAQ）

| 症状 | 原因 | 处理 |
|:-----|:-----|:-----|
| `Ollama 未在线` | 服务未启动 | `ollama serve` 或 systemctl start |
| 冒烟测试超时 | 首次加载 7B 慢(冷启动) | 预热: 先跑 1 个 L2 任务 |
| CUDA OOM | KV cache 超显存 | num_ctx 8192→4096, 或 OLLAMA_GPU_LAYERS 降低 |
| 产物全 fail | 模型名错误 | `ollama list` 核对 config.json 模型名 |
| 中文乱码 | 未先跑 L0 | 确认输入是 L0 产物(import-enhanced/) |
| 处理极慢 | 7B 全量 | 用 --small-first / --limit 分批; 夜间跑 |
| 想重跑某文件 | state.json 已 done | 删除 state.json 中该条目后重跑 |

---

## 9. 回滚与清理

```bash
# 停止后台任务
pkill -f enhancer.py

# 清理产物(保留源文件不动)
rm -rf import-enhanced/out      # 仅增强产物
rm -rf import-enhanced          # 连同 L0 产物(可随时重建)

# 状态重置
rm -f import-enhanced/out/state.json
```

**安全设计**: 所有步骤不修改 import/ 源文件（只读 + 镜像输出），回滚零风险。

---

## 10. 执行检查单（部署时逐项勾选）

- [ ] 1. 硬件检查通过（16G/20核/8G/512G）
- [ ] 2. Ollama 安装并启动
- [ ] 3. qwen2.5:3b 与 7b Q4 已拉取
- [ ] 4. 冒烟测试返回 OK
- [ ] 5. 工具文件已同步、语法检查通过
- [ ] 6. L0 dry-run → 正式执行 → manifest 检查
- [ ] 7. L1 试跑 5 个 → 质量抽查 → 正式后台跑
- [ ] 8. L2 server/ 试跑 5 个 → 质量抽查 → 正式后台跑
- [ ] 9. 抽检 ≥90% 通过
- [ ] 10. 审核后产物按知识库三件套纪律入库

---

## 附: 本方案与既有文档关系

| 文档 | 作用 |
|:-----|:-----|
| [设计方案](knowledge/05_tools/knowledge-management/2026-08-13-local-import-enhancer-design.md) | 技术原理（32K 预算/分片/分级） |
| [应用场景](knowledge/05_tools/knowledge-management/2026-08-13-local-import-enhancer-applications.md) | 7 大专场（提炼/补齐/技术文档/纪要/索引） |
| [README](README.md) | 工具参数速查 |
| **本文件 (DEPLOYMENT.md)** | 部署执行手册（当前） |
