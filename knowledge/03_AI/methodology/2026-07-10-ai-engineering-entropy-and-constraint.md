# 🛡️ AI 工程熵增与约束验证体系

> **概要**: AI 工程熵增根因与 Harness Engineering 四层约束验证体系
>
> **关键词**: 熵增 · 约束验证 · Harness · 上下文工程 · 质量门禁

---

## 📑 目录

- [📋 目录](#目录)
- [1. 问题本质：AI 工程熵增的根因分析](#1-问题本质ai-工程熵增的根因分析)
  - [1.1 熵增的根本机制](#11-熵增的根本机制)
  - [1.2 四大根因](#12-四大根因)
  - [1.3 熵增的加速曲线](#13-熵增的加速曲线)
- [2. 约束失效的典型模式](#2-约束失效的典型模式)
  - [2.1 按约束类型分类](#21-按约束类型分类)
  - [2.2 企业落地真实案例](#22-企业落地真实案例)
- [3. Harness Engineering 的四层约束体系](#3-harness-engineering-的四层约束体系)
  - [3.1 整体架构](#31-整体架构)
  - [3.2 护栏一：上下文工程（AGENTS.md）](#32-护栏一上下文工程agentsmd)
  - [3.3 护栏二：架构约束（刚性边界）](#33-护栏二架构约束刚性边界)
  - [3.4 护栏三：反馈循环（智能体审智能体）](#34-护栏三反馈循环智能体审智能体)
- [4. 架构约束：刚性边界工程化](#4-架构约束刚性边界工程化)
  - [4.1 文件管理约束（P0 级）](#41-文件管理约束p0-级)
  - [4.2 代码风格约束（P1 级）](#42-代码风格约束p1-级)
  - [4.3 依赖管理约束（P0 级）](#43-依赖管理约束p0-级)
  - [4.4 复用偏好约束（P0 级）🆕](#44-复用偏好约束p0-级)
    - [4.4.1 根因分析](#441-根因分析)
    - [4.4.2 组件清单机制](#442-组件清单机制)
- [📦 工具函数 (utils/)](#工具函数-utils)
- [🧩 通用组件 (components/)](#通用组件-components)
- [🔧 已有工具类 (lib/)](#已有工具类-lib)
- [🛡️ 已有 Config/常量 (config/)](#已有-config常量-config)
  - [4.4.3 提示词约束模板](#443-提示词约束模板)
  - [4.4.4 自动复用检测机制](#444-自动复用检测机制)
  - [4.4.5 自检清单中的复用检查项](#445-自检清单中的复用检查项)
  - [4.4.6 工程化落地策略](#446-工程化落地策略)
- [5. 熵管理：自动化对抗技术债](#5-熵管理自动化对抗技术债)
  - [5.1 自动化垃圾回收机制](#51-自动化垃圾回收机制)
  - [5.2 持续小额偿还策略](#52-持续小额偿还策略)
  - [5.3 文档园丁机制](#53-文档园丁机制)
- [6. 验证增强：验证前置与质量控制](#6-验证增强验证前置与质量控制)
  - [6.1 验证前置原则](#61-验证前置原则)
  - [6.2 质量门禁（Quality Gate）](#62-质量门禁quality-gate)
  - [6.3 CI 阻断策略](#63-ci-阻断策略)
- [7. 工程化实施方案](#7-工程化实施方案)
  - [7.1 实施路线图](#71-实施路线图)
  - [7.2 文件结构布局](#72-文件结构布局)
  - [7.3 .agignore — AI 生成忽略规则](#73-agignore-ai-生成忽略规则)
- [8. 工具链与最佳实践](#8-工具链与最佳实践)
  - [8.1 推荐工具链](#81-推荐工具链)
  - [8.2 约束验证自检清单](#82-约束验证自检清单)
  - [8.3 量化度量指标](#83-量化度量指标)
- [9. 量化效果](#9-量化效果)
  - [9.1 OpenAI 内部数据](#91-openai-内部数据)
  - [9.2 熵管理预期效果](#92-熵管理预期效果)
- [10. 局限与注意事项](#10-局限与注意事项)
  - [10.1 已知局限](#101-已知局限)
  - [10.2 反模式提醒](#102-反模式提醒)
  - [10.3 关键原则](#103-关键原则)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

---

## 📋 目录

- [1. 问题本质：AI 工程熵增的根因分析](#1-问题本质ai-工程熵增的根因分析)
- [2. 约束失效的典型模式](#2-约束失效的典型模式)
- [3. Harness Engineering 的四层约束体系](#3-harness-engineering-的四层约束体系)
- [4. 架构约束：刚性边界工程化](#4-架构约束刚性边界工程化)
- [5. 熵管理：自动化对抗技术债](#5-熵管理自动化对抗技术债)
- [6. 验证增强：验证前置与质量控制](#6-验证增强验证前置与质量控制)
- [7. 工程化实施方案](#7-工程化实施方案)
- [8. 工具链与最佳实践](#8-工具链与最佳实践)
- [9. 量化效果](#9-量化效果)
- [10. 局限与注意事项](#10-局限与注意事项)
- [参考来源](#参考来源)

---

## 1. 问题本质：AI 工程熵增的根因分析

### 1.1 熵增的根本机制

AI 生成代码的特性，天然导致工程熵增加速：

```text
传统开发（人工）          AI 辅助开发
    |                         |
    +- 写代码慢，但自维护   +- 生成代码极快，但无维护意识
    +- 中间文件手动清理     +- 中间文件从不清理（"下次还用"）
    +- 代码模式收敛         +- 代码模式不收敛（"每次风格略有不同"）
    +- 技术债匀速增长       +- 技术债指数级增长
    +- 架构漂移慢速进行     +- 架构漂移快速蔓延
```

**关键数据**: OpenAI 早期实验显示，若不进行干预，AI 生成的代码库在 **3 个月内的技术债规模会是传统人工代码库的 5-8 倍**。这是因为 AI 会复制仓库中已有的模式（包括坏模式），且文档往往无法同步更新。

### 1.2 四大根因

| 根因 | 本质 | 表现 | 后果 |
|:-----|:-----|:-----|:-----|
| **无维护成本意识** | AI 没有「长期维护」的概念 | 生成文件后从不删除、从不清理中间产物 | 文件爆炸式增长，目录结构混乱 |
| **模式复制无收敛** | AI 倾向复制现有模式，包括坏模式 | 坏模式被反复复制放大 | 架构漂移加速，一致性丧失 |
| **缺乏自省机制** | AI 不会主动检查自己的输出质量 | 不验证代码是否引入无用文件/依赖 | 无用依赖堆积，构建变慢 |
| **🆕 复用偏好不足** | AI 的「优化目标」是「最快完成任务」，不是「最少引入新依赖」 | 倾向于自己重写已有组件/引入新库，而非查找并使用项目中已有实现 | 组件碎片化、依赖膨胀、实现风格不统一并行存在 |

> **复用偏好不足的深层原因**：
>
> - **认知成本不对称**：翻遍项目找已有组件并理解其用法，对 AI 来说远比自己重写一个「够用」的实现要耗 token
> - **「够用优先」而非「最佳实践」**：AI 的评分函数偏向快速交付可运行结果，而不是最小化对项目的影响
> - **不感知「已有」**：AI 缺乏对「项目已经有什么」的全局认知，除非显式注入到上下文
> - **对自己能力过度自信**：AI 倾向于相信自己新写的代码比项目中已有的更「好」/「更干净」
> - **项目上下文窗口限制**：当项目过大时，AI 无法一次性读取全部已有组件，只能「没找到就自己写」

### 1.3 熵增的加速曲线

```text
工程熵值
    ^
    |                            ╱  无约束 -> 技术债指数增长
    |                       ╱
    |                  ╱
    |             ╱
    |        ╱
    |   ╱
    |--╱-------------------------> 基线（传统开发，熵值缓慢增长）
    |
    +-------------------------------> 时间
        1月    2月    3月    4月
```

**OpenAI 实测**:

- 第 1 个月：AI 代码库技术债 ≈ 人工 2 倍（尚可接受）
- 第 2 个月：AI 代码库技术债 ≈ 人工 4 倍（开始失控）
- 第 3 个月：AI 代码库技术债 ≈ 人工 5-8 倍（必须干预）
- 无干预到第 6 个月：代码库混乱程度达到**需要重写**的程度

---

## 2. 约束失效的典型模式

### 2.1 按约束类型分类

| 类别 | 典型失效模式 | 具体表现 | 危害等级 |
|:-----|:-------------|:---------|:--------:|
| **🅰 文件管理约束** | 随意添加文件 | 生成中间文件、调试文件、备份文件到项目目录 | 🔴 P0 |
| | 文件不删除 | 完成任务后遗留无用文件（如 `temp_*.py`、`test_*.bak`） | 🔴 P0 |
| | 目录混乱 | 文件放错位置、随意创建新目录 | 🟡 P1 |
| **🅱 代码风格约束** | 命名不规范 | 同一项目出现多种命名范式（camelCase/snake_case/混合） | 🟡 P1 |
| | 模式不收敛 | 不同次生成的同类逻辑实现方式不同 | 🟡 P1 |
| | 格式漂移 | 缩进、换行、括号风格不一致 | 🟢 P2 |
| **🅲 架构约束** | 跨层依赖 | UI 层直接调用数据层、跳过 Service 层 | 🔴 P0 |
| | 循环依赖 | 模块间相互引用，打乱依赖方向 | 🔴 P0 |
| | 过度抽象 | 为简单功能引入不必要的接口/抽象类 | 🟡 P1 |
| **🅳 依赖约束** | 随意引入依赖 | 为一个小功能引入新库，不考虑复用 | 🔴 P0 |
| | 版本不一致 | 不同模块使用同一库的不同版本 | 🟡 P1 |
| | 无用依赖残留 | 功能重构后旧依赖未移除 | 🟡 P1 |
| **🅴 文档约束** | 文档不同步 | 代码改了但 AGENTS.md/README.md 未更新 | 🟡 P1 |
| | 注释过时 | 函数注释与实际实现不一致 | 🟢 P2 |
| **🅵 验证约束** | 跳过测试 | 生成代码但不生成测试用例 | 🔴 P0 |
| | 无效测试 | 测试用例不覆盖真实场景（为覆盖率而写） | 🟡 P1 |
| **🅶 复用约束** 🆕 | 不查已有组件直接重写 | 项目已有工具函数/组件，AI 不知道/不查，自己另写一份 | 🔴 P0 |
| | 引入重复依赖 | 已有 `pydantic` 做校验，又引入 `marshmallow` | 🔴 P0 |
| | 重造轮子 | 项目已有 `format_date()` 工具函数，AI 又写了一个 `date_to_string()` | 🟡 P1 |
| | 忽略已有模式 | 项目统一用 `@dataclass`，AI 用 `TypedDict` | 🟡 P1 |
| | 不查 API 直接硬编码 | 已有封装好的 API 客户端，AI 直接从 `requests.get(url)` 开始写 | 🟡 P1 |

### 2.2 企业落地真实案例

**案例 1：中间文件污染**

- 某 AI 辅助项目运行 2 个月后，发现项目中散布了 200+ 个 `temp_*.py`、`backup_*.json`、`test_output_*.csv` 等中间文件
- 原因是 AI 在每次调试过程中都会生成临时文件用于验证，但完成后从不清理
- 影响：目录 `ls` 需要 3 秒，CI 扫描多出 200+ 无用文件

**案例 2：依赖膨胀**

- AI 每次实现功能倾向于引入新依赖（因为「最保险」）
- 3 个月内项目从 12 个依赖膨胀到 47 个
- 最终发现 40% 的依赖只有少量文件在使用，可安全移除

**案例 3：架构漂移**

- 项目初期定义严格的分层架构（UI → Service → Repo → Domain）
- AI 在多次迭代后，开始生成「捷径代码」——UI 直接调用 Repo 层
- 到第 3 个月，60% 的新代码违反分层规则
- 后果：后续维护成本增加 3 倍

**案例 4（新增）：重复造轮子**

- 项目已有 `utils/date_helpers.py` 提供了 `format_date()`、`parse_date_range()` 等 6 个日期处理函数
- AI 在实现「统计报表」功能时，没有引用已有工具函数，而是写了一个全新的 `DateFormatter` 类
- 结果：项目中同时存在两套日期处理实现，功能重叠但接口不同
- 后续开发者需要维护两套实现，且不确定该用哪个

**案例 5（新增）：引入重复依赖**

- 项目使用 `httpx` 作为 HTTP 客户端，已在多处使用并封装了重试/超时逻辑
- AI 在实现「调用外部 API」功能时，直接 `import requests` 并自行处理重试
- 结果：项目中同时存在 `httpx` 和 `requests` 两套 HTTP 客户端
- 影响：`requirements.txt` 膨胀、CI 安装时间增加、安全扫描需覆盖两套库

**案例 6（新增）：忽略已有 API 封装**

- 项目已封装 `api_client.py` 统一处理认证/签名/错误码
- AI 在实现新接口时，直接 `httpx.post(url, json=data)` 绕过封装
- 结果：新接口的认证/签名逻辑缺失，产生线上 Bug
- 影响：排查 2 天才发现是「没走统一 API 客户端」导致

**案例 4（旧）：无效测试堆积**

- AI 每次生成代码都附带测试用例，但大部分只是为了覆盖而写
- 某项目 3000 个测试用例中，35% 是无效测试（变异测试无法发现注入 Bug）
- 影响：CI 运行时间增加 40%，但实际质量保障效果有限

---

## 3. Harness Engineering 的四层约束体系

### 3.1 整体架构

Harness Engineering 的核心哲学是 **「约束换自主」**——要让 AI 更可靠地完成复杂任务，人类需要放弃对模型输出的直接干预，转而通过严格的环境设计，将「不可控的自主」转化为「可控的自主」。

```text
                    Harness Engineering 四层约束体系
                    +------------------------------+
                    |  ④ 熵管理（长期健康层）        |
                    |  自动化对抗技术债              |
                    +------------------------------+
                    +------------------------------+
                    |  ③ 反馈循环（自我修正层）      |
                    |  智能体审智能体 + 变异测试     |
                    +------------------------------+
                    +------------------------------+
                    |  ② 架构约束（刚性边界层）      |
                    |  单向依赖 Linter + CI 阻断    |
                    +------------------------------+
                    +------------------------------+
                    |  ① 上下文工程（信息供给层）    |
                    |  AGENTS.md + 活文档机制        |
                    +------------------------------+
```

### 3.2 护栏一：上下文工程（AGENTS.md）

**核心作用**: 给 AI 提供「边界认知」——告诉 AI 哪些目录可以动、哪些不能动、代码风格是什么、架构约束有哪些。

**实现机制**:

```text
AGENTS.md（面向 AI 的标准化操作手册）
+-- 项目规则（编码规范、测试命令、PR 流程）
+-- 目录边界（哪些目录只读、哪些可写）
+-- 架构约束（分层依赖规则、禁止反模式）
+-- 历史教训（失败案例驱动的规则迭代）
+-- 工具指南（可用工具链及其使用方式）
```

**关键原则**:

- **稳定入口 + 按需检索**：AGENTS.md 仅保留最核心规则，详细文档通过链接指向
- **失败案例驱动**：每一条规则都对应一次真实错误，形成「活反馈循环」
- **定期重载**：迭代优化，保持具体性和高效性

**代码示例**:

```yaml
# .claude/settings.yml — AGENTS.md 的配套约束配置
allowed_directories:
  - src/          # 只允许修改 src/ 下的文件
  - tests/        # 允许生成测试文件
  - docs/         # 允许更新文档

readonly_directories:
  - .git/         # Git 元数据禁止修改
  - node_modules/ # 依赖目录禁止修改
  - config/       # 配置文件禁止修改（除非明确需求）
  - .github/      # CI 配置禁止修改

disallowed_patterns:
  - "temp_*"      # 禁止创建临时文件
  - "backup_*"    # 禁止创建备份文件
  - "*.bak"       # 禁止创建备份
  - "*.tmp"       # 禁止创建临时文件
  - "test_output/"
```

### 3.3 护栏二：架构约束（刚性边界）

> **核心逻辑**: 约束越严格，AI 的效率越高。OpenAI 内部数据：引入分层依赖模型后，代码评审通过率从 40% → 85%，架构漂移降低 90%。

**单向依赖模型**（OpenAI 六层架构）:

```text
+------------------------------------------+
|  UI Layer (页面/组件)                     | <- 只能依赖 Runtime
+------------------------------------------+
|  Runtime Layer (运行时/状态管理)          | <- 只能依赖 Service
+------------------------------------------+
|  Service Layer (服务/用例编排)            | <- 只能依赖 Repo
+------------------------------------------+
|  Repo Layer (数据访问/存储)               | <- 只能依赖 Domain
+------------------------------------------+
|  Domain Layer (领域模型/业务规则)         | <- 零依赖（纯逻辑）
+------------------------------------------+
|  Cross-cutting (日志/权限/监控)           | <- Providers 注入
+------------------------------------------+
```

**自定义 Linter 规则实现**:

```python
# scripts/lint-arch.py — 架构约束自动化检查
import ast
import sys
from pathlib import Path

LAYER_MAP = {
    "ui": ["ui_layer", "pages", "components"],
    "runtime": ["runtime", "state", "middleware"],
    "service": ["services", "usecases"],
    "repo": ["repositories", "data_access"],
    "domain": ["domain", "models", "entities"],
}

# 允许的依赖方向（key 可以依赖 value 中的层）
ALLOWED_DEPENDENCIES = {
    "ui": ["runtime"],
    "runtime": ["service"],
    "service": ["repo"],
    "repo": ["domain"],
    "domain": [],       # domain 层零依赖
}

def check_layer_violation(filepath: str, imports: list) -> list:
    """检查文件是否存在跨层依赖违规"""
    file_layer = detect_layer(filepath)
    violations = []

    for imported_module in imports:
        imported_layer = detect_layer(imported_module)
        if imported_layer and imported_layer not in ALLOWED_DEPENDENCIES.get(file_layer, []):
            violations.append({
                "file": filepath,
                "file_layer": file_layer,
                "imported_module": imported_module,
                "imported_layer": imported_layer,
                "rule": f"{file_layer} 层不能依赖 {imported_layer} 层",
                "fix": get_fix_suggestion(file_layer, imported_layer, imported_module)
            })

    return violations

def get_fix_suggestion(src_layer, dst_layer, module):
    """生成包含修复指引的错误信息"""
    suggestions = {
        ("service", "ui"): f"Service 层不应直接引用 UI 组件。将 UI 相关逻辑下沉到 Service 层，或通过回调接口解耦。",
        ("domain", "infrastructure"): f"Domain 层不应引用基础设施。使用依赖注入将 {module} 的调用移到外层。",
    }
    return suggestions.get((src_layer, dst_layer),
                          f"请通过 {dst_layer} 层的公共接口访问，避免跨层直接引用。")


# CI 集成：检查通过输出 exit 0，否则输出违规详情并 exit 1
if __name__ == "__main__":
    all_violations = scan_all_files()
    if all_violations:
        for v in all_violations:
            print(f"[架构违规] {v['file']}: {v['rule']}")
            print(f"  → 修复建议: {v['fix']}")
        sys.exit(1)
    else:
        print("✅ 架构约束检查通过")
        sys.exit(0)
```

### 3.4 护栏三：反馈循环（智能体审智能体）

**PR 自动化审查流程**:

```text
编码 Agent A ---> 生成代码 + 单元测试
      |
      v
评审 Agent B ---> 架构合规性审查
      |             代码风格审查
      |             逻辑正确性审查
      |             测试有效性审查
      |
      v (需修改)
修复循环 ---> A 修改 -> B 再审 -> 通过
      |
      v
测试 Agent C ---> 端到端测试
                   变异测试（注入 Bug 验证测试有效性）
                   性能测试
      |
      v
    CI 验证 ---> 静态工具检查（SonarQube / ESLint / Pylint）
                  构建验证
                  安全扫描
      |
      v
  Merge 到主分支
```

**变异测试（Mutation Testing）核心机制**:

```python
# scripts/mutation_test.py — 变异测试验证测试有效性
import random
import subprocess
from typing import List

MUTATION_TYPES = [
    ("change_operator", lambda code: code.replace("==", "!=")),
    ("change_operator", lambda code: code.replace(">", "<")),
    ("remove_condition", lambda code: code.replace("if x:", "if True:")),
    ("change_return", lambda code: code.replace("return True", "return False")),
    ("change_constant", lambda code: code.replace("0", "1")),
]

def run_mutation_test(source_file: str, test_file: str) -> dict:
    """
    在源码中注入微小 Bug，验证测试是否能捕获

    返回: {"mutants_created": N, "mutants_killed": M, "score": X%}
    """
    killed = 0
    total = 0

    for mut_type, mutator in MUTATION_TYPES:
        original = read_file(source_file)
        mutated = mutator(original)

        if mutated == original:
            continue  # 突变未生效，跳过

        total += 1
        write_file(source_file, mutated)

        # 运行测试
        result = subprocess.run(
            ["pytest", test_file, "-x", "--tb=short"],
            capture_output=True, text=True
        )

        if result.returncode != 0:
            killed += 1  # 测试发现 Bug → 有效测试
        else:
            print(f"⚠️ 变异未被捕获: {mut_type} in {source_file}")

        write_file(source_file, original)  # 恢复源码

    score = (killed / total * 100) if total > 0 else 100
    return {
        "mutants_created": total,
        "mutants_killed": killed,
        "score": score
    }
```

---

## 4. 架构约束：刚性边界工程化

### 4.1 文件管理约束（P0 级）

**策略**: 通过目录白名单 + 文件模式黑名单 + 自动清理三管齐下。

```yaml
# .ai-constraints/file-policy.yaml — 文件管理约束策略
version: 1.0

file_creation_policy:
  allowed_root_dirs:
    - src/
    - tests/
    - docs/
    - scripts/

  disallowed_root_dirs:
    - node_modules/
    - __pycache__/
    - .git/
    - dist/
    - build/

  # 禁止创建的文件模式
  forbidden_patterns:
    - "temp_*"
    - "*.bak"
    - "*.tmp"
    - "*_backup.*"
    - "*_copy.*"
    - "test_output/"
    - "debug_*.*"

  # 允许的临时文件位置（受控区域）
  temp_directory: ".ai_temp/"
  temp_file_ttl: "1h"  # 临时文件超过 1 小时自动清理

auto_cleanup:
  enabled: true
  schedule: "hourly"  # 每小时清理

  # 自动清理规则
  rules:
    - pattern: ".ai_temp/*"
      max_age: "1h"
      action: "delete"

    - pattern: "__pycache__/*"
      max_age: "0"
      action: "delete"

    - pattern: ".mypy_cache/*"
      max_age: "24h"
      action: "delete"

    - pattern: "*.pyc"
      action: "delete"

    - pattern: ".coverage"
      action: "keep"  # 重要报告保留
```

**Git 集成——.gitignore 动态管理**:

```bash
# .gitignore 模板（AI 项目专用）
# 自动生成的忽略规则
.ai_temp/
temp_*
*.bak
*.tmp
*_backup.*
*_copy.*
test_output/
debug_*

# 标准忽略
__pycache__/
*.py[cod]
*$py.class
*.so
.env
.venv
```

### 4.2 代码风格约束（P1 级）

**策略**: 通过格式化工具 + Linter + 统一配置实现。

```yaml
# .ai-constraints/code-style.yaml — 代码风格约束配置
version: 1.0

formatter:
  python: "ruff format"
  javascript: "prettier --write"
  go: "gofmt -w"

# AI 生成代码时需遵守的命名规范
naming_conventions:
  python:
    variables: "snake_case"
    functions: "snake_case"
    classes: "PascalCase"
    constants: "UPPER_CASE"
    private: "_prefix_underscore"

  typescript:
    variables: "camelCase"
    functions: "camelCase"
    classes: "PascalCase"
    interfaces: "I_Prefix"
    types: "T_Prefix"

# 每个文件的行数上限（防止 AI 生成超大文件）
max_lines_per_file:
  python: 500
  typescript: 400
  go: 800

# 每个函数行数上限
max_lines_per_function:
  python: 50
  typescript: 60
  go: 80
```

### 4.3 依赖管理约束（P0 级）

```yaml
# .ai-constraints/dependency-policy.yaml — 依赖管理策略
version: 1.0

dependency_import_rules:
  # 禁止引入的依赖（已有替代方案）
  banned_packages:
    python:
      - "requests"      # 已使用 httpx
      - "numpy"         # 项目不使用
      - "pandas"        # 项目不使用
      - "flask"         # 已使用 fastapi
    javascript:
      - "axios"         # 已使用 fetch
      - "moment"        # 已使用 dayjs
      - "lodash"        # 鼓励原生实现

  # 新依赖引入需满足的条件
  new_dependency_policy:
    min_usage_count: 3      # 至少 3 处使用才考虑引入
    min_stars: 100          # GitHub stars 最低要求
    must_be_maintained: true  # 最近 6 月有更新
    require_review: true    # 需要人工审查

# 依赖清理规则
dependency_cleanup:
  auto_detect_unused: true
  cleanup_frequency: "weekly"
  exception_list:
    - "pytest"        # 测试框架，经常隐式使用
    - "ruff"          # 格式化工具，CLI 模式
```

### 4.4 复用偏好约束（P0 级）🆕

> **核心问题**: AI 的「优化目标」是「最快完成任务」，不是「最小化对项目的影响」。对她来说，自己写一个 `format_date()` 比翻遍项目找 `utils/date_helpers.py` 然后理解它的参数签名更「省事」。
>
> **解决思路**: 不能指望 AI「自觉去查」，必须显式地将「项目已有组件清单」注入到提示词/上下文中，并在验证环节强制检查「是否该用已有组件而没用的」。

#### 4.4.1 根因分析

| 维度 | AI 的默认行为 | 期望行为 | 根因 |
|:-----|:-------------|:---------|:-----|
| **认知成本** | 自己写一个新函数 | 翻遍项目找到已有函数并理解用法 | AI 没有「人类工程师对项目的记忆」，每次都要从头扫描文件树，耗 token |
| **风险偏好** | 自己写是「确定的」（写完就通） | 用已有组件是「不确定的」（需验证接口/行为是否匹配） | AI 倾向于选择确定路径，避免需要「推理+验证」的路径 |
| **评价标准** | 「代码是否通过测试」 | 「代码是否与项目已有模式一致」 | 人类的「一致性」标准很难量化成 AI 的 loss function |
| **上下文局限** | 只看了当前文件/附近文件 | 需要了解整个项目的工具函数/组件清单 | 项目越大，AI 越倾向「局部最优解」而非「全局最优解」 |

#### 4.4.2 组件清单机制

**核心方案**: 维护一份项目级「组件清单」(`component-inventory.md`)，让 AI 在生成代码前先查清单。

```markdown
# .ai-constraints/component-inventory.md — 项目组件清单

> 此文件供 AI 在生成代码前优先查参。
> 规则：任何新增功能，必须先查此清单；清单中有能直接或稍作适配后使用的组件，**禁止另造轮子**。

---

## 📦 工具函数 (utils/)

| 文件 | 暴露接口 | 用途 | 替代惩罚 |
|:-----|:---------|:-----|:---------|
| `utils/date_helpers.py` | `format_date(dt, fmt)`、`parse_date_range(start, end)`、`get_weekday(dt)`、`is_holiday(dt)` | 日期格式化/范围解析/工作日判断 | ❌ 禁止另写日期处理函数 |
| `utils/string_helpers.py` | `slugify(text)`、`truncate(text, max_len)`、`camel_to_snake(name)` | 字符串处理 | ❌ 禁止另写字符串处理 |
| `utils/http_client.py` | `get(url, params, headers)`、`post(url, json)`、`put(url, json)`、`delete(url)` | 统一 HTTP 请求（含重试/超时/签名） | ❌ 禁止直接 `import httpx` |
| `utils/retry.py` | `retry(max_attempts=3, delay=1, backoff=2)` 装饰器 | 函数重试 | ❌ 禁止自行实现重试逻辑 |
| `utils/logging.py` | `get_logger(name)`、`log_with_context(logger, msg, **ctx)` | 结构化日志 | ❌ 禁止使用 `print()` 或自建 logger |

## 🧩 通用组件 (components/)

| 文件 | 暴露接口 | 用途 | 替代惩罚 |
|:-----|:---------|:-----|:---------|
| `components/table.py` | `DataTable(data, columns, sortable, filterable, pagination)` | 数据表格组件 | ❌ 禁止另写表格 |
| `components/modal.py` | `Modal(title, content, size, confirm_text, cancel_text)` | 模态框 | ❌ 禁止另写模态框 |
| `components/form.py` | `Form(fields, layout, validation)` | 表单组件 | ❌ 禁止另写表单 |
| `components/chart.py` | `Chart(type, data, options)` | 图表组件（基于 ECharts） | ❌ 禁止直接操作 ECharts API |

## 🔧 已有工具类 (lib/)

| 文件 | 暴露接口 | 用途 | 替代惩罚 |
|:-----|:---------|:-----|:---------|
| `lib/cache.py` | `cache.get(key)`、`cache.set(key, val, ttl)`、`cache.delete(key)` | 缓存（Redis 封装） | ❌ 禁止直接 `import redis` |
| `lib/auth.py` | `auth.verify_token(token)`、`auth.get_current_user()` | 认证/鉴权 | ❌ 禁止自行实现认证逻辑 |
| `lib/validator.py` | `validate(schema, data)` -> `Errors` | 数据校验（基于 Pydantic） | ❌ 禁止引入新校验库 |
| `lib/excel.py` | `export_to_excel(data, filename)`、`import_from_excel(filename)` | Excel 导入导出 | ❌ 禁止直接 `import openpyxl` |

## 🛡️ 已有 Config/常量 (config/)

| 文件 | 暴露接口 | 用途 | 替代惩罚 |
|:-----|:---------|:-----|:---------|
| `config/constants.py` | `MAX_RETRIES`, `TIMEOUT_SEC`, `PAGE_SIZE`, `DATE_FORMAT` | 全局常量 | ❌ 禁止硬编码常量值 |
| `config/settings.py` | `settings.DATABASE_URL`, `settings.REDIS_URL`, `settings.LOG_LEVEL` | 配置项 | ❌ 禁止硬编码配置 |
```

**使用方式**: 将 `component-inventory.md` 注入到 AI 的初始化上下文中，加在 AGENTS.md 末尾作为强制查阅清单。

#### 4.4.3 提示词约束模板

在提示词（Prompt）中显式约束 AI 优先使用已有组件：

```yaml
# .ai-constraints/reuse-prompt-template.yaml — 复用偏好提示词约束
version: 1.0

reuse_constraints_in_prompt: |
  ## 🚨 强制约束：优先使用项目已有组件

  在开始写任何新代码之前，请严格执行以下步骤：

  ### Step 1: 查阅组件清单
  打开 `.ai-constraints/component-inventory.md`，找到与你当前任务相关的已有组件/工具函数。

  ### Step 2: 优先复用规则
  按以下优先级选择实现方案（从高到低）：
  - 🥇 **直接复用**: 已有组件完全满足需求 → 直接调用，不允许自行实现
  - 🥈 **适配复用**: 已有组件功能接近需微调 → 封装一层适配器调用，不允许重写
  - 🥉 **扩展复用**: 已有组件需扩展功能 → 在现有组件基础上扩展，不允许新建文件
  - ❌ **禁止重写**: 除非经过以下验证，否则禁止自行重写已有功能：
      a) 已有组件存在性能瓶颈且无法通过配置优化
      b) 已有组件的接口设计无法适配新场景
      c) 你已确认以上两条并记录理由到代码注释中

  ### Step 3: 引入新依赖的审批流程
  如果你认为需要引入一个新库/新依赖：
  1. 先证明「项目中已有组件均无法满足需求」
  2. 检查 `banned_packages` 列表，确认新库不在其中
  3. 说明为什么不能用已有库的替代功能
  4. 添加注释 `# NEW_DEPENDENCY: <库名> - <理由>` 标记待审查

  ### Step 4: 新增文件限制
  - 优先在现有文件中新增函数/类，而非新建文件
  - 如果确实需要新建文件，需说明理由并添加注释 `# NEW_FILE: <路径> - <理由>`
  - 避免创建仅有一个函数的单方法文件

reuse_rules_in_prompt: |
  ## 复用检查清单（自动执行）
  完成代码后，请逐一检查：
  - [ ] 我是否查阅了组件清单？
  - [ ] 我是否有直接复用而非自己实现的机会但错过了？
  - [ ] 我引入的新依赖是否真有必要？
  - [ ] 我新建的文件是否可以合并到现有文件中？
  - [ ] 我的实现风格是否与项目中已有的同类实现一致？
```

#### 4.4.4 自动复用检测机制

在 CI 中增加「复用合规性」检测：

```python
# scripts/check_reuse_compliance.py — 复用合规性检测
"""
检测 AI 生成的代码是否：
1. 重复实现了已有组件/工具函数的功能
2. 引入了项目中已有替代的依赖
3. 绕过了已有的 API 封装层
"""
import ast
import sys
from pathlib import Path

class ReuseComplianceChecker:
    def __init__(self, inventory_path: str = ".ai-constraints/component-inventory.md"):
        self.inventory = self._parse_inventory(inventory_path)
        self.violations = []

    def _parse_inventory(self, path):
        """解析组件清单，提取 API 签名"""
        inventory = {}
        # 简化的 YAML/表格解析逻辑
        current_section = None
        with open(path) as f:
            for line in f:
                if line.startswith("## "):
                    current_section = line.strip()
                elif "`" in line and "|" in line:
                    # 解析表格行: | file.py | func_name() | 用途 | 惩罚 |
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) >= 4:
                        file_path = parts[1].strip("`")
                        api_name = parts[2].split("(")[0].strip("`")
                        inventory[api_name] = {
                            "file": file_path,
                            "section": current_section
                        }
        return inventory

    def check_file(self, filepath: str):
        """检查单文件是否存在「重复造轮子」"""
        with open(filepath) as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError:
                return []

        violations = []

        for node in ast.walk(tree):
            # 检查函数定义是否与已有 API 功能重叠
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                if func_name in self.inventory:
                    violations.append({
                        "file": filepath,
                        "line": node.lineno,
                        "type": "duplicate_func",
                        "detail": f"函数 `{func_name}()` 与已有组件 `{self.inventory[func_name]['file']}` 重名/功能重叠",
                        "suggestion": f"请使用已有组件 `{self.inventory[func_name]['file']}` 中的 `{func_name}()`，不要重新实现"
                    })

            # 检查 import 是否引入了被禁止的依赖
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    pkg_name = alias.name.split(".")[0]
                    if pkg_name in self._get_banned_packages():
                        violations.append({
                            "file": filepath,
                            "line": node.lineno,
                            "type": "banned_dependency",
                            "detail": f"引入了被禁止的依赖 `{pkg_name}`",
                            "suggestion": f"{self._get_banned_reason(pkg_name)}"
                        })

        return violations

    def _get_banned_packages(self):
        """获取禁止引入的包列表（从 dependency-policy.yaml 读取）"""
        # 实际实现应读取 YAML 配置
        return {"requests", "numpy", "pandas", "flask", "axios", "moment", "lodash"}

    def _get_banned_reason(self, pkg):
        reasons = {
            "requests": "项目中已使用 httpx 作为统一 HTTP 客户端，且封装了重试/超时/签名逻辑",
            "numpy": "本项目不使用 numpy，纯 Python 实现即可",
            "pandas": "本项目数据量不足以需要 pandas，使用原生 dict/list 操作",
            "flask": "项目已使用 fastapi 作为 Web 框架",
            "axios": "前端已使用 fetch API，无需引入 axios",
            "moment": "前端已使用 dayjs，功能完全覆盖 moment",
            "lodash": "鼓励使用原生 ES6+ 实现，避免引入 lodash",
        }
        return reasons.get(pkg, "项目已有替代方案")

    def check_all(self, changed_files: list) -> list:
        """检查所有变更文件"""
        all_violations = []
        for f in changed_files:
            if f.endswith(".py"):
                all_violations.extend(self.check_file(f))
        return all_violations

if __name__ == "__main__":
    checker = ReuseComplianceChecker()
    changes = sys.argv[1:] if len(sys.argv) > 1 else ["."]
    violations = checker.check_all(changes)

    if violations:
        print("❌ 复用合规性检测未通过:")
        for v in violations:
            print(f"  [{v['type']}] {v['file']}:{v['line']}")
            print(f"    问题: {v['detail']}")
            print(f"    建议: {v['suggestion']}")
        sys.exit(1)
    else:
        print("✅ 复用合规性检测通过")
        sys.exit(0)
```

#### 4.4.5 自检清单中的复用检查项

在 AI 的产出自检清单中增加复用条目：

```yaml
self_check:
  reuse_compliance:
    - "我在开始写代码前查阅了 `component-inventory.md`"
    - "我没有重复实现任何已有组件的功能"
    - "我没有引入项目中已有替代方案的依赖"
    - "我没有绕过已有的 API 封装层"
    - "我新增的函数/类是否需要合并到现有文件中？"
    - "我的实现模式与项目已有风格是否一致？"
```

#### 4.4.6 工程化落地策略

| 策略 | 难度 | 效果 | 实施方式 |
|:-----|:----:|:----:|:---------|
| **组件清单注入** | 🟢 低 | 🟡 中 | 在 AGENTS.md 末尾追加 `component-inventory.md` 链接，AI 每次启动时自动读取 |
| **提示词硬约束** | 🟢 低 | 🟡 中 | 在 system prompt 中嵌入「优先复用」规则，要求 AI 自我检查 |
| **函数名去重检测** | 🟡 中 | 🔴 高 | CI 中运行 `check_reuse_compliance.py`，检测与新功能重名的函数 |
| **依赖引入审计** | 🟡 中 | 🔴 高 | CI 中对比 `requirements.txt` 变更，标记新增依赖并要求审查 |
| **使用模式分析** | 🔴 高 | 🟢 极高 | 定期分析代码库中「同类功能」的多种实现方式，建议合并 |

---

## 5. 熵管理：自动化对抗技术债

### 5.1 自动化垃圾回收机制

Harness Engineering 的第四道护栏——**熵管理**——是保障长期系统健康的核心机制。

```python
# agents/entropy-manager.py — 熵管理 Agent
"""
自动化对抗 AI 工程熵增的巡检 Agent
运行周期: 每日/每周
职责:
  1. 清理死代码和冗余文件
  2. 纠正命名规范漂移
  3. 优化冗余依赖
  4. 同步文档与代码
  5. 修复架构违规
"""
import os
import re
from datetime import datetime, timedelta
from pathlib import Path

class EntropyManager:
    def __init__(self, project_root: str):
        self.root = Path(project_root)
        self.report = {
            "orphan_files": [],
            "dead_imports": [],
            "stale_temp": [],
            "doc_gaps": [],
            "arch_violations": [],
        }

    def run_full_scan(self) -> dict:
        """执行全量熵检"""
        self._find_orphan_files()
        self._find_stale_temp_files()
        self._check_doc_consistency()
        self._detect_arch_drift()
        return self.report

    def _find_orphan_files(self):
        """检测孤立文件（未被任何文件引用的模块）"""
        all_py_files = list(self.root.rglob("*.py"))
        source_files = [f for f in all_py_files
                       if "test_" not in f.name and not f.name.startswith("_")]

        # 构建 import 索引
        imports_index = set()
        for f in all_py_files:
            content = f.read_text()
            matches = re.findall(r'(?:from|import)\s+([\w.]+)', content)
            imports_index.update(matches)

        # 检测未被引用的模块
        for f in source_files:
            module_name = f.stem
            if module_name not in imports_index and module_name != "__init__":
                # 检查是否被其他文件间接引用
                if not self._is_indirectly_referenced(f):
                    self.report["orphan_files"].append(str(f))

    def _find_stale_temp_files(self):
        """检测过期临时文件和中间产物"""
        stale_patterns = ["temp_*", "*.bak", "*.tmp", "*_copy.*", "*_backup.*"]
        for pattern in stale_patterns:
            for f in self.root.glob(f"**/{pattern}"):
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                if datetime.now() - mtime > timedelta(hours=1):
                    self.report["stale_temp"].append(str(f))

    def _check_doc_consistency(self):
        """检测文档与代码一致性"""
        # 扫描 API 函数的 docstring 与实际签名是否一致
        for f in self.root.rglob("*.py"):
            if "test_" in f.name:
                continue
            content = f.read_text()
            functions = re.findall(r'def (\w+)\(([^)]*)\)', content)
            docstrings = re.findall(r'"""([^"]*)"""', content)

            # 简单检查：函数有定义但无 docstring → 标记
            if len(functions) > 0 and len(docstrings) == 0:
                self.report["doc_gaps"].append({
                    "file": str(f),
                    "issue": "functions_without_docstring",
                    "count": len(functions)
                })

    def _detect_arch_drift(self):
        """检测架构漂移（违反分层依赖规则）"""
        # 调用架构约束 Linter
        from scripts.lint_arch import check_layer_violation
        violations = check_layer_violation(self.root)
        self.report["arch_violations"] = violations

    def apply_fixes(self, dry_run=True):
        """执行自动修复（dry_run=True 仅报告不执行）"""
        actions = []

        # 清理孤立文件（移到 .archive/ 目录）
        for f in self.report["orphan_files"]:
            actions.append(f"mv {f} .archive/{f.replace('/', '_')}")

        # 清理过期临时文件
        for f in self.report["stale_temp"]:
            actions.append(f"rm {f}")

        # 自动修复架构违规（提交修复 PR）
        for v in self.report["arch_violations"]:
            actions.append(f"自动修复: {v['rule']} - {v['fix']}")

        if dry_run:
            return actions

        # 执行修复逻辑
        for action in actions:
            if action.startswith("rm"):
                os.remove(action.split()[-1])
            elif action.startswith("mv"):
                # 移到废弃目录而非直接删除
                parts = action.split()
                os.rename(parts[1], parts[2])

        return actions
```

### 5.2 持续小额偿还策略

与传统的「集中式重构」不同，熵管理采用 **「持续小额偿还」** 策略——AI 在每次生成代码时，自动清理少量技术债。

```yaml
# .ai-constraints/debt-policy.yaml — 技术债管理策略
version: 1.0

debt_strategy:
  # 持续小额偿还 vs 集中式重构
  mode: "continuous"  # continuous | periodic | manual

  # 每次代码生成时附带的技术债清理
  per_change_cleanup:
    enabled: true
    max_extra_files: 3    # 每次最多额外清理 3 个文件
    max_extra_lines: 50   # 每次最多额外清理 50 行

  # 定期巡检
  periodic_audit:
    schedule: "weekly"
    agent: "entropy-manager"
    max_pr_size: 20       # 每次自动修复 PR 最多 20 个文件变更

  # 自动修复策略
  auto_fix:
    orphan_files: "move_to_archive"     # 孤立文件 → 归档
    stale_temp: "delete"                 # 临时文件 → 删除
    unused_imports: "auto_remove"        # 无用导入 → 自动删除
    naming_drift: "auto_fix"             # 命名漂移 → 自动修正
    doc_gap: "auto_generate"             # 文档缺失 → 自动生成
    arch_violation: "create_fix_pr"      # 架构违规 → 提交修复 PR
```

### 5.3 文档园丁机制

```python
# agents/doc-gardener.py — 文档同步 Agent
"""
职责：扫描文档与代码的差异，自动提交修复 PR
执行频率：每日
"""
class DocGardener:
    def scan_doc_code_gaps(self):
        """
        检测以下不匹配：
        1. API 文档中的参数与实际代码不一致
        2. README 中描述的功能已不存在
        3. AGENTS.md 中的规则已被新实践替代
        4. 新增模块缺少对应文档
        """
        gaps = []

        # 检查 API 文档与代码签名的一致性
        doc_files = list(Path("docs").rglob("*.md"))
        for doc in doc_files:
            # 提取文档中描述的 API 签名
            doc_apis = extract_api_from_doc(doc)
            # 与实际代码对比
            for api in doc_apis:
                if not api_exists_in_code(api):
                    gaps.append({
                        "type": "stale_api_doc",
                        "file": str(doc),
                        "api": api["name"],
                        "action": "update_or_remove"
                    })

        # 检查新增模块是否缺少文档
        modules = find_new_modules()  # 最近 7 天内新增的模块
        for mod in modules:
            if not has_corresponding_doc(mod):
                gaps.append({
                    "type": "missing_doc",
                    "module": mod,
                    "action": "generate_doc"
                })

        return gaps
```

---

## 6. 验证增强：验证前置与质量控制

### 6.1 验证前置原则

AI 工程的核心理念之一：**验证不应在产生结果之后，而应嵌入在生成过程中**。

```yaml
# .ai-constraints/validation-policy.yaml — 验证策略
version: 1.0

validation_shifts:
  # 传统：生成 → 审查 → 修复 → 验证（后置验证）
  # AI：约束 → 生成 → 立即验证 → 修复 → 提交（验证前置）

  generation_validation:
    # 代码生成时的即时检查
    inline_checks:
      - "syntax_check"       # 语法正确性
      - "import_check"       # 导入是否存在
      - "type_check"         # 类型正确性
      - "style_check"        # 风格一致性
      - "size_check"         # 文件大小上限

    # 生成完成后的验证
    post_generation:
      - "unit_tests"         # 单元测试
      - "lint_check"         # Linter 检查
      - "arch_check"         # 架构约束检查
      - "file_policy_check"  # 文件管理策略检查

  quality_gates:
    # 质量控制门槛（低于门槛则要求重新生成）
    lint_score_min: 9.0      # Pylint/ESLint 评分 ≥ 9/10
    test_coverage_min: 80    # 测试覆盖率 ≥ 80%
    mutation_score_min: 85   # 变异测试分数 ≥ 85%
    arch_compliance: 100     # 架构合规率 = 100%（零容忍）
```

### 6.2 质量门禁（Quality Gate）

```python
# scripts/quality_gate.py — AI 生成代码的质量门禁
class QualityGate:
    def __init__(self):
        self.gates = [
            ("🚪 文件门禁", self.check_file_policy),
            ("🚪 风格门禁", self.check_code_style),
            ("🚪 架构门禁", self.check_architecture),
            ("🚪 测试门禁", self.check_tests),
            ("🚪 依赖门禁", self.check_dependencies),
            ("🚪 文档门禁", self.check_documentation),
        ]

    def evaluate(self, changes: dict) -> dict:
        """评估 AI 生成的变更是否通过所有门禁"""
        results = {}
        all_passed = True

        for gate_name, gate_fn in self.gates:
            result = gate_fn(changes)
            results[gate_name] = result
            if not result["passed"]:
                all_passed = False
                # 失败时输出详细的修复指引
                print(f"\n❌ {gate_name} 未通过")
                print(f"   问题: {result['reason']}")
                print(f"   修复指引: {result['fix_guide']}")

        return {"all_passed": all_passed, "details": results}

    def check_file_policy(self, changes):
        """检查是否有违反文件管理策略的行为"""
        violations = []

        # 检查是否有在禁止目录中创建文件
        for file in changes.get("created_files", []):
            for forbidden in [".git/", "node_modules/", "__pycache__/"]:
                if forbidden in file:
                    violations.append(f"在禁止目录 {forbidden} 中创建了文件: {file}")

        # 检查是否有创建了禁止模式的文件
        for file in changes.get("created_files", []):
            for pattern in ["temp_", ".bak", ".tmp", "_copy."]:
                if pattern in file:
                    violations.append(f"创建了禁止模式文件: {file}（模式: {pattern}）")

        if violations:
            return {
                "passed": False,
                "reason": "; ".join(violations),
                "fix_guide": "请删除违规文件，并遵守 .ai-constraints/file-policy.yaml 中的文件创建规则"
            }
        return {"passed": True}

    def check_architecture(self, changes):
        """检查架构合规性"""
        from scripts.lint_arch import check_layer_violation

        modified_files = changes.get("modified_files", [])
        for f in modified_files:
            violations = check_layer_violation(f, get_imports(f))
            if violations:
                return {
                    "passed": False,
                    "reason": f"文件 {f} 存在架构违规",
                    "fix_guide": violations[0]["fix"]
                }
        return {"passed": True}

    def check_tests(self, changes):
        """检查测试有效性"""
        from scripts.mutation_test import run_mutation_test

        test_files = changes.get("test_files", [])
        source_files = changes.get("source_files", [])

        # 必须为每个新增/修改的源码文件生成对应测试
        for src in source_files:
            corr_test = src.replace("src/", "tests/").replace(".py", "_test.py")
            if corr_test not in test_files:
                return {
                    "passed": False,
                    "reason": f"源码 {src} 缺少对应测试文件 {corr_test}",
                    "fix_guide": f"请为 {src} 创建测试文件 {corr_test}"
                }

        # 变异测试验证测试有效性
        for src in source_files:
            corr_test = src.replace("src/", "tests/").replace(".py", "_test.py")
            result = run_mutation_test(src, corr_test)
            if result["score"] < 85:
                return {
                    "passed": False,
                    "reason": f"测试 {corr_test} 变异测试得分 {result['score']:.1f}% < 85%",
                    "fix_guide": f"请增强测试用例，当前 {result['mutants_created']} 个变异中仅捕获 {result['mutants_killed']} 个"
                }

        return {"passed": True}
```

### 6.3 CI 阻断策略

```yaml
# .github/workflows/ai-quality-gate.yaml — AI 代码质量门禁 CI
name: AI Quality Gate

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  quality-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: 🚪 文件门禁
        run: |
          python scripts/quality_gate.py check-file-policy
          # 禁止创建禁用模式文件

      - name: 🚪 架构门禁
        run: |
          python scripts/lint-arch.py
          # 架构违规 → 直接阻断

      - name: 🚪 静态工具检查
        run: |
          ruff check . --output-format github
          # Pylint/ESLint 评分 ≥ 9.0

      - name: 🚪 单元测试
        run: |
          pytest --cov=src --cov-fail-under=80
          # 覆盖率 ≥ 80%

      - name: 🚪 变异测试
        run: |
          python scripts/mutation_test.py src/
          # 变异测试分数 ≥ 85%

      - name: 🚪 依赖审计
        run: |
          pip-audit
          # 依赖安全审计
```

---

## 7. 工程化实施方案

### 7.1 实施路线图

```text
Phase 1（基础约束 + 快速见效）— 第 1-2 周
+-- 部署文件管理策略（禁止模式 + 目录边界）
+-- 配置代码格式化工具（Prettier / Ruff / gofmt）
+-- 启用 Linter 基本规则
+-- 配置 .gitignore 动态管理
+-- 设置简单 CI 阻断（文件模式 + 风格检查）

Phase 2（架构约束 + 质量门禁）— 第 3-4 周
+-- 部署单向依赖 Linter（自定义规则）
+-- 配置架构约束 CI 阻断
+-- 部署质量门禁（Quality Gate 脚本）
+-- 引入覆盖率门槛（≥ 80%）
+-- 配置依赖管理策略

Phase 3（自动化自愈）— 第 5-8 周
+-- 部署熵管理 Agent（每周巡检）
+-- 部署文档园丁 Agent（每日同步）
+-- 配置自动修复 PR 流程
+-- 引入变异测试
+-- 配置持续小额偿还机制

Phase 4（智能体自治）— 第 9-12 周
+-- 建立 AGENTS.md 活文档机制
+-- 部署智能体审智能体链路
+-- 配置全自动 PR 评审流水线
+-- 建立技术债度量仪表盘
+-- 持续迭代约束规则（失败案例驱动）
```

### 7.2 文件结构布局

```text
.ai-constraints/                      # AI 约束配置目录（约束即代码）
+-- file-policy.yaml                  # 文件管理策略
+-- code-style.yaml                   # 代码风格约束
+-- dependency-policy.yaml            # 依赖管理策略
+-- validation-policy.yaml            # 验证策略配置
+-- debt-policy.yaml                  # 技术债管理策略

scripts/                              # 约束验证脚本
+-- lint-arch.py                      # 架构约束 Linter
+-- quality_gate.py                   # 质量门禁
+-- mutation_test.py                  # 变异测试
+-- entropy-check.sh                  # 熵检脚本

agents/                               # 自动化 Agent
+-- entropy-manager.py                # 熵管理 Agent
+-- doc-gardener.py                   # 文档园丁 Agent

.github/workflows/
+-- ai-quality-gate.yaml              # AI 质量门禁 CI

.agignore                             # AI 生成忽略规则（类比 .gitignore）
.gitignore                            # Git 忽略 + AI 生成产物忽略
```

### 7.3 .agignore — AI 生成忽略规则

```bash
# .agignore — AI 生成忽略规则（类比 .gitignore 但面向 AI）
# 当 AI 检测到以下模式时，应当自我约束不生成对应文件

# 禁止 AI 创建的目录
.ai_temp/
temp/
debug_output/

# 禁止 AI 创建的文件模式
temp_*
*.bak
*.tmp
*_backup.*
*_copy.*
*_draft.*
test_output/
debug_*

# AI 不应修改的目录
.vscode/
.idea/
.git/
node_modules/
__pycache__/
dist/
build/
*.egg-info/
```

---

## 8. 工具链与最佳实践

### 8.1 推荐工具链

| 工具 | 用途 | 等级 | 说明 |
|:-----|:-----|:----:|:-----|
| **lint-arch** | 架构约束检查 | 🔴 P0 | 自定义实现，检查单向依赖 |
| **ruff** | Python 语法+风格 | 🔴 P0 | 替代 flake8+isort+black，统一入口 |
| **prettier** | 前端代码格式化 | 🔴 P0 | 多语言统一格式化 |
| **gofmt** | Go 代码格式化 | 🔴 P0 | Go 官方格式工具 |
| **pytest-cov** | 测试覆盖率 | 🔴 P0 | 覆盖率 ≥ 80% |
| **mutmut / mutpy** | 变异测试 | 🟡 P1 | 验证测试用例有效性 |
| **pip-audit** | 依赖安全检查 | 🟡 P1 | 扫描已知漏洞 |
| **vulture** | 死代码检测 | 🟡 P1 | 发现未使用的代码 |
| **deptry** | 无用依赖检测 | 🟡 P1 | 发现项目中未使用的依赖 |
| **SonarQube** | 全量代码质量 | 🟢 P2 | 技术债可视化仪表盘 |

### 8.2 约束验证自检清单

**AI 每次提交前自检（必须通过）**:

```yaml
# .ai-constraints/self-check.yaml — AI 自检清单
version: 1.0

self_check:
  file_policy:
    - "我没有在禁止目录创建文件"
    - "我没有创建禁止模式的文件（temp_* / *.bak / *.tmp）"
    - "我没有遗留任何中间产物"
    - "所有新增文件都在合理的位置"

  code_style:
    - "代码通过格式化工具检查（ruff / prettier）"
    - "命名规范符合项目约定"
    - "没有重复代码（DRY 原则）"

  architecture:
    - "我没有创建跨层依赖"
    - "我没有引入循环依赖"
    - "我没有过度抽象（YAGNI 原则）"

  dependencies:
    - "我没有引入不必要的依赖"
    - "我没有遗留旧的依赖声明"
    - "已有依赖中没有未使用的"

  testing:
    - "我为新增/修改的代码生成了测试用例"
    - "测试用例覆盖了正常路径和边界条件"
    - "变异测试分数 ≥ 85%"

  documentation:
    - "文档与代码保持同步"
    - "公共 API 有 docstring 说明"
    - "README 更新的内容未过时"

  entropy:
    - "我检查了是否遗留了临时文件"
    - "我清理了调试用代码/注释"
    - "我检查了是否引入了冗余代码"
```

### 8.3 量化度量指标

```yaml
# .ai-constraints/metrics.yaml — 熵增度量体系
version: 1.0

metrics:
  # 文件熵指标
  file_entropy:
    - name: "file_count"                    # 总文件数
      threshold: "监控趋势（增长率不应超过人工 2x）"
    - name: "temp_file_ratio"               # 临时文件占比
      threshold: "< 1%"
    - name: "file_per_directory"            # 每目录文件数（不含子目录）
      threshold: "≤ 20"
    - name: "orphan_file_ratio"             # 孤立文件占比
      threshold: "< 5%"

  # 架构熵指标
  arch_entropy:
    - name: "layer_violation_count"         # 跨层违规数
      threshold: "0（零容忍）"
    - name: "circular_dependency_count"     # 循环依赖数
      threshold: "0（零容忍）"
    - name: "module_coupling"               # 模块耦合度
      threshold: "监控趋势"

  # 依赖熵指标
  dependency_entropy:
    - name: "total_dependencies"            # 总依赖数
      threshold: "监控趋势"
    - name: "unused_dependency_ratio"       # 无用依赖占比
      threshold: "< 5%"
    - name: "duplicate_dependency_count"    # 重复依赖数
      threshold: "0"

  # 代码质量指标
  quality_metrics:
    - name: "lint_score"                    # Linter 评分
      threshold: "≥ 9.0/10"
    - name: "test_coverage"                 # 测试覆盖率
      threshold: "≥ 80%"
    - name: "mutation_score"                # 变异测试得分
      threshold: "≥ 85%"
    - name: "duplication_ratio"             # 重复代码率
      threshold: "< 5%"
```

---

## 9. 量化效果

### 9.1 OpenAI 内部数据

| 指标 | 无约束 | 有约束（Harness Engineering） | 提升 |
|:-----|:------:|:-----------------------------:|:----:|
| 代码评审通过率 | 40% | 85% | +45pp |
| 架构漂移发生率 | 每 3 月 >60% | 每 3 月 <6% | -90% |
| 技术债累积速度 | 人工的 5-8 倍 | 人工的 1.2 倍 | -80% |
| 文档与代码一致性 | 60% | 95%+ | +35pp |
| 无效测试占比 | 35% | <5% | -30pp |
| 人工审查工作量 | 基线 | -80% | 80% 自动化 |
| 代码缺陷率 | 基线 | -60% | 质量翻倍 |

### 9.2 熵管理预期效果

| 措施 | 预期效果 | 时间 |
|:-----|:---------|:----:|
| 文件管理策略 | 消除中间文件污染，<1% 临时文件 | 即时 |
| 架构约束 Linter | 架构违规零容忍，漂移降低 90% | 1-2 周 |
| 质量门禁 | 代码评分 ≥ 9/10，覆盖率 ≥ 80% | 2-4 周 |
| 熵管理 Agent | 技术债降低 70%，自动清理死代码 | 4-8 周 |
| 文档园丁 | 文档一致性从 60% → 95%+ | 4-8 周 |
| 变异测试 | 无效测试从 35% → <5% | 6-12 周 |

---

## 10. 局限与注意事项

### 10.1 已知局限

1. **约束本身需要维护**：约束规则不是「一劳永逸」的，需要随项目演进迭代
2. **过度约束可能降低效率**：过于严格的约束可能导致 AI 频繁生成失败，反复重试
3. **变异测试计算成本高**：每次运行变异测试需要多次执行测试套件，CI 时间增加
4. **文档园丁可能生成冗余文档**：自动生成的文档可能不够精准，需人工审核
5. **熵管理 Agent 本身也由 AI 驱动**：存在 Agent 自我检视的递归问题

### 10.2 反模式提醒

| 反模式 | 问题 | 正确做法 |
|:-------|:-----|:---------|
| 「约束越多越好」 | 过度约束导致 AI 无法完成任务 | 按 P0→P1→P2 优先级渐进式部署 |
| 「一次配完就完事」 | 约束规则不随项目演进，逐渐过时 | 持续迭代，失败案例驱动规则更新 |
| 「人工审查可有可无」 | 完全依赖自动化导致系统漏洞 | 自动化 + 关键节点人工审查 |
| 「只约束不度量」 | 无法评估约束效果 | 建立量化指标，用数据驱动优化 |
| 「所有项目用一套约束」 | 不同项目约束需求不同 | 项目级定制约束配置 |

### 10.3 关键原则

> **Mitchell Hashimoto（Harness Engineering 提出者）的核心观点**:
>
> 「harness engineering is the idea that anytime you find an agent makes a mistake, you take the time to engineer a solution such that the agent will not make that mistake again in the future.」
>
> （每当智能体犯错，就花时间设计一个方案，让它永远不会再犯同样的错误。）

这意味着：

- ❌ 不要期望 AI「自觉遵守」规则
- ✅ 把规则编码化，让 AI **不得不**遵守
- ❌ 不要每次手动纠正 AI 的错误
- ✅ 将纠正过程自动化，确保同类错误不复发
- ❌ 不要相信「下次会注意」
- ✅ 相信「不可逾越的工程壁垒」

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- (无)

### 外部资料引用

- 来源: --

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-10 | v1.0 | 创建，AI 工程熵增与约束验证体系 |
| 2026-07-14 | v1.1 | 📦 从 `02_rd/05_software/17-ai-engineering/` 迁至 `03_AI/methodology/`（AI 方法论文档统一管理） |
