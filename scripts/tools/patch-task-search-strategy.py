#!/usr/bin/env python3
"""
定时任务搜索策略加固脚本

修复内容:
1. 所有调研模块任务 → 追加"零产出占位文件"规则（解决静默空跑）
2. 所有调研模块任务 → 追加"缺失自愈"机制（连续3天空跑自动升级）
3. 所有调研模块任务 → 追加"搜索策略增强"（多源+重试+轮换）
4. 日报生成任务 → 追加"完整性检查"（静默>3天模块自动告警）

用法: python3 scripts/patch-task-search-strategy.py
已在 2026-07-27 对 29 个任务执行加固，此脚本保留供后续新增任务加固使用。
"""

import json
import re

TASKS_PATH = "scheduler/tasks.json"

FULL_TEMPLATE = """
产出零记录规则（强制执行）:
- 即使没有有效发现，也必须创建占位文件记录搜索摘要。
  文件名: knowledge/01_survey/{module}/YYYY-MM-DD.md
  内容格式:
  ```
  ## 📋 搜索摘要（无新增内容）
  - **执行时间**: YYYY-MM-DD HH:MM
  - **搜索源**: [源1: 状态码] [源2: 状态码] [源3: 状态码]
  - **搜索词**: xxx
  - **结论**: 未发现值得归档的有效信息
  - **上次有产出日**: YYYY-MM-DD
  ```
- 此占位文件会参与日报统计，确保审计可见。
- 连续 3 天零产出 → 任务下次运行时自动升级搜索策略（见下方缺失自愈）。

缺失自愈（强制执行）:
- 执行前检查: ls -t knowledge/01_survey/{module}/*.md | head -1   # 01_survey 已无 index/log（2026-08-19 起）
- 如果最新产出日期距今天 >=3 天，说明有产出缺口，自动升级策略:
  - 搜索源增至 5 个（追加 2 个常规搜索引擎兜底）
  - 关键词扩展为更宽泛的变体（至少准备 2 组词）
  - 每个源失败后可换词重试 1 次
- 缺口 >=7 天 → 额外追加 arXiv/Bing 宽泛搜索

搜索策略增强:
- 每个源最多尝试 2 次（首次失败后换近似关键词重试）
- 关键词提供至少 2 组变体
- 备用搜索源 +1
"""

DAILY_STALENESS_CHECK = """
## 完整性检查（强制执行）

生成日报正文之后、写入文件之前，执行以下完整性检查:

1. 遍历 knowledge/01_survey/*/ 所有子目录
2. 对每个子目录，找出最新的 YYYY-MM-DD 日期文件（排除 index.md 和 log.md）
3. 计算该日期距今天的天数
4. 如果 >=3 天（即模块静默超过3天），在日报末尾追加:

```
---

## ⚠️ 模块产出静默告警

以下模块已超过 3 天无新产出，请关注:

| 模块 | 最后产出日 | 静默天数 | 最后产出文件 |
|:-----|:----------:|:--------:|:-------------|
| xxx | YYYY-MM-DD | N 天 | filename.md |
```
"""


def patch_all(data):
    """Patch all survey module tasks and daily report task."""
    patched_modules = 0
    patched_daily = False
    
    for tid, task in data["tasks"].items():
        action = task.get("action", {})
        desc = action.get("task_description", "")
        if not desc:
            continue
        
        # Survey module tasks
        m = re.search(r"knowledge/01_survey/([^/\s]+)/", desc)
        if m:
            module = m.group(1)
            
            # Skip if already patched
            if "即使没有有效发现" in desc:
                continue
            
            # Replace silent-skip rule
            old = "没有有效信息 → 直接结束，不创建文件"
            new = "没有有效信息 → 创建占位文件（规则见下方）"
            desc = desc.replace(old, new)
            
            old = "没有有效信息就不需要创建文件，不消耗额外 token"
            new = "没有有效信息 → 创建占位文件（规则见下方）"
            desc = desc.replace(old, new)
            
            desc = desc.replace("无有效信息就不需要创建文件，不消耗额外 token", new)
            desc = desc.replace("无有效信息 → 直接结束，不创建文件", new)
            desc = desc.replace("没有任何发现就直接结束", "")
            desc = desc.replace("没有有效信息就不需要创建文件", new)
            
            # Append full template
            template = FULL_TEMPLATE.format(module=module)
            action["task_description"] = desc.rstrip() + "\n" + template
            task["updated_at"] = "2026-07-27T10:30:00"
            patched_modules += 1
        
        # Daily report task (by ID)
        if tid == "443f5e47":
            if "完整性检查" not in desc:
                action["task_description"] = desc.rstrip() + "\n" + DAILY_STALENESS_CHECK
                task["updated_at"] = "2026-07-27T10:30:00"
                patched_daily = True
    
    return patched_modules, patched_daily


if __name__ == "__main__":
    with open(TASKS_PATH, "r") as f:
        data = json.load(f)
    
    mod_count, daily_ok = patch_all(data)
    data["updated_at"] = "2026-07-27T10:30:00"
    
    with open(TASKS_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"模块任务修复: {mod_count} 个")
    print(f"日报完整性检查: {'已接入' if daily_ok else '无需更新'}")
