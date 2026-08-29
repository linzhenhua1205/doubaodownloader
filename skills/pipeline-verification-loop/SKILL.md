---
name: pipeline-verification-loop
description: "Ralph循环验证引擎——AI生产流水线的心脏，阶段4 of 6。通过Plan→Do→Check→Act四步循环，让AI自主迭代直到满足客观验证标准。核心组件：明确的完成条件（check gate列表）、Stop Hook拦截（AI尝试退出时自动触发验证）、最大迭代次数（防止无限循环）。Use when: (1) 需要自动迭代验证产出质量，(2) 要求'循环验证'/'Ralph循环'/'loop until达标'，(3) 需要验证：事实准确性/逻辑一致性/结构完整性/格式规范性/来源可追溯/数据可验证，(4) part of pipeline-orchestrator pipeline execution。不用于：单次review、主观质量判断。"
metadata:
  requires:
    bins: ["python3"]
---
# Verification Loop (Ralph Engine)

**Pipeline Stage 4**: The "heart" of the production pipeline. Automated Plan→Do→Check→Act iteration until objective completion criteria are met.

## Core Architecture

```
     ┌─────────┐     ┌─────────┐     ┌─────────┐
     │ Plan    │────▶│ Do      │────▶│ Check   │
     └─────────┘     └─────────┘     └────┬─────┘
          ▲                                │
          │                                │ Fail
          │    ┌─────────┐                 │
          └────│ Act     │◀────────────────┘
               └─────────┘
                     │ Pass
                     ▼
                ┌──────────┐
                │ Output   │
                └──────────┘
```

### Three Core Components

#### 1. Explicit Completion Criteria

Must be **objectively measurable**:

```
✅ Good criteria:
  - "All 5 check gates pass"
  - "Document contains required 4 sections: Overview/Method/Results/Conclusion"
  - "Table rows ≥ 10, columns = 5"
  - "Every assertion has source citation"

❌ Bad criteria:
  - "Looks good enough"
  - "Quality is satisfactory"
  - "Reader can understand"
```

#### 2. Stop Hook Interception

Automatically trigger verification when AI attempts to exit:
- Inject verification instructions into system prompt
- Check results after each tool call
- Force verification before final output

#### 3. Max Iterations

Hard-coded upper limit (default: 5). Timeout → suspend for human intervention.

## Verification Dimensions

Check Stage 4 output against ALL applicable dimensions:

| Dimension | What to Verify | Method | Pass Criteria |
|:----------|:---------------|:-------|:--------------|
| **Fact accuracy** | Data/claims are correct | Cross-reference + source trace | Every claim has S/A source support |
| **Logic consistency** | No internal contradictions | Auto-scan conflicting claims | Zero logic conflicts |
| **Structure completeness** | Contains all required parts | Template/format check | 100% required elements present |
| **Format compliance** | Meets target format | Lint + pattern match | Zero format violations |
| **Source traceability** | Every claim has citation | Citation count + cross-check | No uncited claims |
| **Data verifiability** | Values + units + baseline + conditions | Pattern matching | No bare assertions |
| **Innovation** | Incremental vs existing work | Comparison with reference | Clear delta identified |
| **Ethical compliance** | No exaggeration/false/infringement | Ethics checklist scan | No red-line violations |

## Verification Independence（验证独立性，v1.1 新增）

> 依据：自评 = 闭合反馈回路（信息论零信息增益）；独立验证 = 打破回路（条件独立性）。
> 详见 [`2026-08-17-loop-verification-independence-economy-deep-analysis.md`](../../../knowledge/03_AI/agent-engineering/2026-08-17-loop-verification-independence-economy-deep-analysis.md)

### 独立性四条件（验证可信度检查清单）

| # | 条件 | 含义 | 违反后果 |
|:-:|:-----|:-----|:---------|
| ① | **上下文隔离** | 验证时上下文不含生成过程记忆（看不到"我刚刚写了什么"） | 退化为自评（确认偏差） |
| ② | **证据锚定** | 结论必须对照真实文件/测试结果（E 为锚），非产出表面连贯性 | 流利度替代正确性 |
| ③ | **证伪激励** | 验证角色是"找错"（fail-finding），非"确认"（pass-approving） | 模型倾向 PASS 一切 |
| ④ | **无利益关联** | 验证者不被激励维护产出 | 维护面子 → 放过错误 |

### 执行规则（三条军规）

```yaml
# 1. 验证轮与生成轮上下文隔离（最低成本近似独立）
#    - 新开一轮，只注入：产出 + 外部证据（文件路径/测试结果）
#    - 不注入：生成过程记忆、中间草稿、思考链
# 2. 验证 prompt 必须用证伪式（不是确认式）
❌ 确认式: "请检查你的产出有没有问题"          → 闭路自评（PASS 一切）
✅ 证伪式: "逐项核对：产出第 N 条 ↔ 文件实际内容 ↔ 测试实际结果，列出每项 PASS/FAIL"
          "找不到 FAIL 也要给出证据链"        → 强制证据接入（判断权交给证据）
# 3. 高价值产出加独立上下文第二意见
#    - 关键文档/代码：第二个独立上下文子 agent 复核（Ralph 背压谱系最强端）
#    - 成本约束：仅对关键产出启用（token 穷人原则：验证用脚本不用子 agent）
```

### 与 8 维验证的关系

8 维（事实/逻辑/结构/格式/来源/数据/创新/伦理）是**验证什么**；独立性四条件是**谁验证、怎么验才可信**。**两者正交：8 维定义检查项，四条件保证检查结果可信。** 缺少独立性时，8 维检查全部退化为"模型自评"——正是 Ralph 五要素"背压验证"失效的主因。

## Pass Criteria Levels

| Level | Meaning | Condition | Next Step |
|:-----:|:--------|:----------|:----------|
| **🟢 Auto pass** | All auto-verification satisfied | All check gates pass | Forward to next stage |
| **🟡 Conditional pass** | Minor non-core issues | ≥80% check gates pass, minor issues tagged | Forward + issue list |
| **🔴 Fail** | Serious issues need rework | Core check gates fail | Return to Stage 2/3 |

## Ralph Loop Execution

```yaml
verification_result:
  iterations:
    - round: 1
      verdict: "fail"
      issues:
        - dimension: "fact_accuracy"
          detail: "Data unit error: GB/s vs GT/s"
      action: "Correct unit, recalculate values"
    - round: 2
      verdict: "conditional_pass"
      issues:
        - dimension: "format_compliance"
          detail: "TOC missing (auto-fixed)"
          severity: "minor"
    - round: 3
      verdict: "pass"
      iterations_used: 3
      max_iterations: 5
      pass_level: "auto_pass"
```

## Script

Scripts are in `<base_dir>/scripts/`.

```bash
python3 <base_dir>/scripts/ralph_loop.py \  # ⚠️ 设计承诺（Ralph 循环引擎（语义判断），当前由 LLM 按循环规则执行）
  --input <merged_result.json> \
  --criteria verification_criteria.yaml \
  --max-iterations 5
```

## References

See full methodology: `knowledge/05_tools/ai-production-pipeline/ai-production-pipeline-methodology.md` (§6)
