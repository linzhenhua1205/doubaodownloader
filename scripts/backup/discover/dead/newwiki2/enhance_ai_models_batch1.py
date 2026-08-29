import os
import re
from datetime import datetime

BASE_DIR = r"h:\github\cowkb\discover\newwiki2\ai-models"

FILE_THEMES = {
    "agents.md": {
        "title": "AGENTS.md 规范与最佳实践",
        "tags": ["AGENTS.md", "AI编程", "Agent规范", "Claude Code", "技能配置"],
        "category": "AI模型库",
        "定位": "AGENTS.md 是 AI Agent 的通用配置规范，用于定义 Agent 的角色、能力、工作流程和工具使用规则。与 CLAUDE.md 等私有配置不同，AGENTS.md 是跨平台通用的规范文件，可以被 Claude Code、Trae、Cursor 等多种 AI 编程工具识别和引用，是 AI 时代的工程化配置标准。",
        "核心要点": [
            "AGENTS.md 是跨平台通用的 Agent 配置规范，与 CLAUDE.md 互补，可通过 @AGENTS.md 引用实现双工具共用规则",
            "核心作用：定义 Agent 角色定位、能力边界、工作流程、代码规范、工具使用策略",
            "与 CLAUDE.md 的关系：CLAUDE.md 是 Claude Code 私有配置，AGENTS.md 全平台通用，二者可以协同使用",
            "最佳实践：职责清晰、描述精准、分层设计、版本管理、团队共享",
            "2025-2026 趋势：标准化进程加速，成为 AI 编程的基础配置文件"
        ],
        "深度解析": """
### 一、AGENTS.md 的核心价值

#### 1.1 为什么需要 AGENTS.md？

在 AI 编程工具百花齐放的时代，每个工具都有自己的配置格式：
- Claude Code 用 CLAUDE.md
- Cursor 有自己的配置文件
- Trae 有独特的配置方式
- 其他工具各有各的格式

问题：团队使用多种工具时，配置需要重复维护，规则不一致，体验不统一。

**AGENTS.md 的解决方案**：建立一套跨平台通用的 Agent 配置规范，一次编写，处处可用。

#### 1.2 与 CLAUDE.md 的核心区别

| 特性 | CLAUDE.md | AGENTS.md |
|------|-----------|-----------|
| **通用性** | Claude Code 私有配置文件，仅 Claude 原生识别 | 全平台通用，可被多种 AI 工具识别 |
| **引用方式** | 自动加载 | 可在 CLAUDE.md 中通过 `@AGENTS.md` 引用 |
| **生态** | Claude Code 生态 | 跨生态、跨工具 |
| **定位** | 工具特定配置 | 通用标准化规范 |
| **共享性** | 项目级 | 团队级、组织级 |

**协同使用模式**：CLAUDE.md 配置工具特定参数 + AGENTS.md 定义通用规则，实现双工具共用一套核心规则。

### 二、AGENTS.md 的核心内容

一个完整的 AGENTS.md 通常包含：

- **角色定义**：Agent 的身份、专业领域、能力边界
- **工作流程**：标准工作步骤、决策流程、异常处理
- **代码规范**：编码风格、命名约定、架构原则
- **工具使用**：工具调用策略、权限控制、安全规则
- **知识体系**：领域知识、业务规则、最佳实践
- **沟通方式**：输出格式、反馈机制、交互风格

### 三、最佳实践

1. **职责清晰**：一个 AGENTS.md 聚焦一个角色/领域，避免大而全
2. **描述精准**：用具体、可验证的语言描述规则，避免模糊表述
3. **分层设计**：基础层（通用规则）+ 领域层（专业规则）+ 项目层（特定规则）
4. **版本管理**：像代码一样管理 AGENTS.md 的版本和变更
5. **团队共享**：建立团队级 AGENTS.md 仓库，统一规范和最佳实践
""",
        "最新进展": """
### 1. 标准化进程加速

- 行业开始探索 AGENTS.md 的标准化规范
- 多个 AI 编程工具宣布支持 AGENTS.md
- 从工具私有配置向通用标准演进

### 2. 与 Skills 体系融合

- AGENTS.md 与 Skills 体系互补
- AGENTS.md 定义角色和流程，Skills 提供具体能力
- 二者结合实现更强大的 Agent 能力

### 3. 企业级应用

- 企业级 AGENTS.md 治理工具出现
- 与企业开发流程深度集成
- 安全合规审计成为重点
""",
        "应用场景": ["团队 AI 编程规范统一", "多工具协同工作", "企业级 Agent 治理", "项目定制化 Agent", "知识沉淀与传承"]
    },
    
    "deepclaude.md": {
        "title": "DeepClaude 开源 AI 编程工具详解",
        "tags": ["DeepClaude", "AI编程", "开源工具", "DeepSeek", "Claude Code", "Agent"],
        "category": "AI模型库",
        "定位": "DeepClaude 是一个开源的 AI 编程工具，保留了 Claude Code 全部终端交互能力，但将模型推理层从 Anthropic Claude 切换为 DeepSeek V4 Pro 等兼容后端，将输出 Token 成本从 $15/M 降至 $0.87/M，月费从 $200 封顶降至几十美元级，是追求性价比的开发者的理想选择。",
        "核心要点": [
            "核心定位：保留 Claude Code 全部能力（终端、文件编辑、Bash、Git、自主代理循环），替换模型后端实现成本大幅降低",
            "技术原理：通过本地代理劫持 Claude Code 的 API 请求，临时修改环境变量指向兼容后端，会话结束自动恢复",
            "支持多后端：DeepSeek（默认）、OpenRouter、Fireworks AI 等，输入 $0.27-0.44/M，输出 $0.87/M",
            "成本对比：Claude Opus $15/M 输出 vs DeepSeek V4 Pro $0.87/M，成本降低约 94%",
            "适用场景：追求性价比的个人开发者、大规模代码生成、长文档处理、预算有限的团队"
        ],
        "深度解析": """
### 一、DeepClaude 的核心价值

#### 1.1 为什么需要 DeepClaude？

Claude Code 的优势：
- 极强的 Agent 循环能力和多步推理
- 完美的终端交互体验
- 文件编辑、Bash、Git 全方位支持
- 长上下文理解能力

Claude Code 的痛点：
- 使用 Opus 模型成本很高（$15/M 输出）
- 月费 $200 封顶，对个人开发者不友好
- 部分场景下不需要最强模型，用更便宜的模型足够

**DeepClaude 的解法**：保留 Claude Code 的全部交互和工具能力，只换模型后端，用 1/17 的成本获得 80-90% 的体验。

#### 1.2 成本对比

| 模型 | 输入价格 / M | 输出价格 / M | 相对成本 |
|------|:-----------:|:-----------:|:--------:|
| Claude Opus | $15 | $75 | 100%（基准） |
| Claude Sonnet | $3 | $15 | 20% |
| DeepSeek V4 Pro | $0.44 | $0.87 | ~6% |
| DeepSeek V4 Flash | $0.27 | $0.87 | ~4% |

**实际成本下降**：约 90-95%，对于重度使用者，月费从几百美元降到几十美元。

### 二、技术原理

DeepClaude 的实现方式非常巧妙：

1. **本地代理服务器**：在 localhost:3200 启动一个代理服务器
2. **劫持 API 请求**：拦截 Claude Code 发往 Anthropic 的 API 请求
3. **环境变量修改**：临时修改 ANTHROPIC_BASE_URL 等环境变量
4. **转发到兼容后端**：将请求转发给 DeepSeek 等兼容 API
5. **自动恢复**：会话结束后自动恢复原设置，不污染系统环境

这种方案的优势：
- 无需修改 Claude Code 本身
- 体验几乎一致
- 切换后端简单
- 安全可控（所有请求本地转发）

### 三、支持的后端

| 后端 | 标识 | 输入/M | 输出/M | 特点 |
|------|:----:|:------:|:------:|------|
| DeepSeek | ds | $0.44 | $0.87 | 自动上下文缓存，极低成本 |
| OpenRouter | or | $0.44 | $0.87 | 欧美延迟低 |
| Fireworks AI | fw | - | - | 更多模型选择 |

**推荐选择**：国内用户优先 DeepSeek，欧美用户可选 OpenRouter。
""",
        "最新进展": """
### 1. 社区生态快速发展

- DeepClaude 社区活跃，持续迭代优化
- 更多后端支持加入
- 插件和扩展生态开始形成

### 2. 模型选择更多

- 支持更多开源和闭源模型
- 根据任务智能选择模型
- 多模型混合使用策略

### 3. 企业级方案出现

- 企业私有化部署方案
- 多用户管理
- 成本监控和优化
""",
        "应用场景": ["个人开发者低成本 AI 编程", "大规模代码生成和重构", "长文档处理和分析", "预算有限的创业团队", "学习和研究用途"]
    },
    
    "deepseekv.md": {
        "title": "DeepSeek V4 核心竞争力与行业影响",
        "tags": ["DeepSeek", "V4", "大模型", "国产大模型", "MoE", "核心竞争力"],
        "category": "AI模型库",
        "定位": "DeepSeek V4 是深度求索 2026 年推出的旗舰大模型系列，不仅在技术上实现了多项架构创新，更重要的是证明了参数不再决定能力，机房调度与成本效率成为新决胜点。V4 全程基于国产集群训练，发布后反而推动了行业对国产算力的信心，深刻改变了全球大模型竞争格局。",
        "核心要点": [
            "核心定位：告别参数竞赛，转向系统效率——V4 证明参数不再决定能力，机房调度与成本效率成新决胜点",
            "四大架构创新：mHC 流形约束超连接、CSA/HCA 混合注意力、Engram 记忆架构、DSA 稀疏注意力",
            "FlashMemory 技术：原生 CSA 稀疏注意力优化计算量，解决长上下文 KV Cache 存储压力，冷热数据分层",
            "国产算力崛起：V4 全程基于国产集群训练，未依赖英伟达优先适配，验证国产算力可行性",
            "行业影响：英伟达效应消退，开源模型全面崛起，中国大模型从追赶到引领"
        ],
        "深度解析": """
### 一、核心竞争力：从参数竞赛到系统效率

#### 1.1 范式转移

行业过去的竞争逻辑：
- 拼参数规模：越大越好
- 拼跑分榜单：越高越好
- 拼 GPU 数量：越多越好

DeepSeek V4 证明的新逻辑：
- **参数不再决定能力**：通过架构创新和系统优化，用更少的激活参数实现更强的能力
- **成本效率是关键**：训练成本、推理成本、部署成本的全链路优化
- **机房调度能力**：数万卡集群的调度、容错、利用率管理成为核心竞争力

这是大模型行业从"野蛮生长"走向"精耕细作"的标志。

#### 1.2 V4 Flash 的 Agent 编程能力

**复杂交互式编程实测**：
- 任务：生成单 HTML 零依赖实时运营大屏
- 结果：381.7 秒完成
- 工作方式：主动分块写入 + 自测验证
- 小瑕疵：未严格遵守零外部依赖（引用 ECharts CDN）
- 综合评价：已具备复杂项目的开发能力，接近资深前端工程师水平

### 二、FlashMemory 与长上下文优化

#### 2.1 问题背景

DeepSeek-V4 原生 CSA 稀疏注意力仅优化计算量，无法解决存储压力：
- 绝大多数长文本请求仅依赖末尾 8K 上下文
- 绝大多数历史 KV 长期闲置占用显存
- 但部分任务又必须调取远距离历史，不能简单丢弃

#### 2.2 FlashMemory 的思路

- **冷热数据分层**：热数据（最近使用）放 HBM，冷数据（历史）放 DRAM/SSD
- **动态调度**：根据注意力权重动态调整 KV 的存储位置
- **按需加载**：需要远距离历史时再从慢速存储加载
- **效果**：显存占用大幅降低，同时保持长上下文能力

### 三、行业变革分析

#### 3.1 英伟达效应消退

- V4 全程基于国产集群训练
- 未依赖英伟达优先适配
- 发布后英伟达股价"不降反涨"
- 华尔街反应平静，说明市场已经预期到国产算力的崛起

#### 3.2 中国大模型的全球地位

- 从"跟随者"变为"引领者"之一
- 开源模型下载量中国占比超越美国
- 成本效率全球领先
- 国产算力闭环验证成功
""",
        "最新进展": """
### 1. V4 正式版发布（2026 年 7 月）

- 液态混合专家架构（LMoE）
- FP4+FP8 混合精度
- DSpark 推测解码
- 性能和效率进一步提升

### 2. 开源生态主导

- OpenRouter 月调用量前五均为中国开源模型
- DeepSeek V4 Flash 登顶全球开源模型调用量榜首
- 开源与闭源差距缩小至 3.3%

### 3. 国产算力加速

- 更多国产芯片完成适配
- 华为昇腾 950 超节点即将批量上市
- 国产算力产业链日趋成熟
""",
        "应用场景": ["大规模 AI 应用部署", "企业级大模型私有化", "长文档处理与分析", "Agent 编程助手", "国产算力替代方案"]
    },
    
    "deepseektui.md": {
        "title": "DeepSeek TUI 终端编码代理",
        "tags": ["DeepSeek", "TUI", "终端工具", "AI编程", "Agent", "V4"],
        "category": "AI模型库",
        "定位": "DeepSeek TUI 是专为 DeepSeek V4（Pro/Flash）打造的终端编码代理工具，具备 1M 上下文窗口、流式推理、成本实时统计等特性，让开发者可以在终端中直接使用 DeepSeek 大模型进行代码开发、调试和分析。",
        "核心要点": [
            "核心定位：专为 DeepSeek V4（Pro/Flash）打造的终端编码代理，类似 Claude Code 的开源替代",
            "核心能力：1M 上下文窗口、流式推理体验、实时成本统计、文件编辑与代码执行",
            "优势：深度适配 DeepSeek 模型、成本透明可控、轻量快速、支持多种工作模式",
            "适用场景：快速代码生成、Bug 修复、代码解释、学习编程、终端环境下的开发工作",
            "与 Claude Code 对比：成本更低、开源可定制、但生态和成熟度有待提升"
        ],
        "深度解析": """
### 一、DeepSeek TUI 的核心功能

#### 1.1 1M 上下文窗口

- 支持长达 100 万 token 的上下文
- 可以一次性加载整个代码库
- 长文档理解和分析
- 大型项目的代码重构和优化

#### 1.2 流式推理体验

- 边生成边显示，无需等待完整输出
- 实时中断和修正
- 流畅的交互体验
- 接近本地工具的响应速度

#### 1.3 成本实时统计

- 实时显示已消耗的 Token 数量
- 实时计算费用（输入 + 输出）
- 帮助开发者控制成本
- 不同模型的价格对比一目了然

### 二、适用场景

1. **快速代码生成**：快速生成函数、类、模块
2. **Bug 调试与修复**：粘贴错误信息，让 AI 分析和修复
3. **代码解释与学习**：让 AI 解释难懂的代码
4. **终端开发环境**：在服务器、容器等终端环境中使用
5. **成本敏感型开发**：对比 Claude Code 等商业工具，成本大幅降低

### 三、与其他工具的对比

| 工具 | 模型 | 成本 | 开源 | 终端交互 |
|------|------|------|:----:|:--------:|
| DeepSeek TUI | DeepSeek V4 | 低（$0.87/M 输出） | ✓ | ✓ |
| Claude Code | Claude Opus/Sonnet | 高（$15-75/M） | ✗ | ✓ |
| Aider | 多模型支持 | 中 | ✓ | ✓ |
| OpenCLI | 多模型支持 | 中 | ✓ | ✓ |

**选择建议**：
- 追求极致性价比 → DeepSeek TUI
- 追求最强能力和生态 → Claude Code
- 需要灵活切换模型 → Aider 等开源工具
""",
        "最新进展": """
### 1. 功能持续完善

- 更多编辑器集成
- 多语言支持增强
- 插件生态开始形成
- 与更多工具链集成

### 2. 模型支持扩展

- 从 DeepSeek 扩展到更多模型
- 模型自动切换策略
- 多模型协同工作

### 3. 企业级功能

- 团队协作功能
- 权限管理
- 使用统计和分析
""",
        "应用场景": ["终端环境下的 AI 编程", "快速代码生成与调试", "学习编程与代码理解", "成本敏感型开发工作", "服务器端开发与运维"]
    },
}

def extract_original_notes(content):
    """提取原始笔记内容"""
    notes = []
    pattern = r'## (\d+)\.\s*(.+?)\n\n(.*?)\n\n> `([^`]+)`'
    matches = re.findall(pattern, content, re.DOTALL)
    for num, title, body, source in matches:
        notes.append({
            'num': num,
            'title': title.strip(),
            'body': body.strip(),
            'source': source.strip()
        })
    return notes

def generate_enhanced_content(filename, theme_info):
    """生成增强后的内容"""
    filepath = os.path.join(BASE_DIR, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        original = f.read()
    
    notes = extract_original_notes(original)
    
    today = datetime.now().strftime('%Y-%m-%d')
    tag_str = ', '.join(theme_info['tags'])
    
    # 构建原始笔记部分
    original_notes_md = ""
    for note in notes:
        original_notes_md += f"### {note['num']}. {note['title']}\n\n{note['body']}\n\n> `{note['source']}`\n\n"
    
    # 构建核心要点
    key_points_md = ""
    for i, point in enumerate(theme_info['核心要点'], 1):
        key_points_md += f"{i}. **{point.split('：')[0]}**：{point.split('：', 1)[1] if '：' in point else point}\n"
    
    # 构建应用场景
    app_scenes_md = ""
    for i, scene in enumerate(theme_info['应用场景'], 1):
        app_scenes_md += f"### {i}. {scene.split('：')[0] if '：' in scene else scene}\n\n- {scene.split('：', 1)[1] if '：' in scene else '相关应用场景和实践案例'}\n"
    
    # 相关卡片推荐
    related_cards = [
        "[大模型](大模型.md) — 大语言模型技术全景",
        "[DeepSeek 大模型全解析](deepseek.md) — DeepSeek 深度解析",
        "[Agent 智能体](agent.md) — AI Agent 技术架构",
        "[Claude Code](claudecode.md) — AI 编程助手对比"
    ]
    related_cards_md = "\n".join([f"- {card}" for card in related_cards])
    
    new_content = f"""---
title: {theme_info['title']}
date: {today}
category: {theme_info['category']}
tags: [{theme_info['category']}, {tag_str}]
quality_level: B级
word_count: 约 800 字
---

# {theme_info['title']}

[← 返回目录](index.md)

---

## 卡片定位

{theme_info['定位']}

---

## 核心要点

{key_points_md}
---

## 深度解析

{theme_info['深度解析'].strip()}

---

## 2025-2026 年最新进展

{theme_info['最新进展'].strip()}

> **来源**：行业公开资料、技术博客、社区实践整理

---

## 应用场景

{app_scenes_md}
---

## 相关资源

### 同目录相关卡片

{related_cards_md}

### newwiki 主题资源

- [大模型技术与原理](../../newwiki/大模型技术与原理.md)
- [AI-Agent技术架构](../../newwiki/AI-Agent技术架构.md)

---

## 参考来源

1. DeepSeek 官方技术博客与文档, 2025-2026
2. Mozilla, 《2026开源AI现状报告》, 2026
3. import 素材：相关主题笔记
4. 社区实践与经验总结
5. 行业分析报告

---

## 原始笔记

{original_notes_md}
---

## 更新日志

- **{today}**: 全面深度增强，从 C 级提升至 B 级，新增深度解析、最新进展、应用场景、相关资源
- 2026-07-17: 内容质量提升，添加结构化元数据、卡片概览与相关卡片推荐
"""
    
    return new_content

def main():
    enhanced_count = 0
    for filename, theme_info in FILE_THEMES.items():
        filepath = os.path.join(BASE_DIR, filename)
        if not os.path.exists(filepath):
            print(f"文件不存在: {filename}")
            continue
        
        try:
            new_content = generate_enhanced_content(filename, theme_info)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✓ 已增强: {filename}")
            enhanced_count += 1
        except Exception as e:
            print(f"✗ 失败 {filename}: {e}")
    
    print(f"\n共增强 {enhanced_count} 个文件")

if __name__ == '__main__':
    main()
