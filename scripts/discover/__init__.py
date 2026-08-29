"""discover/ — AI 批量化知识加工脚本工具链

需求规格: spec/sr-005-discover-dir-req.md §3.5
设计方案: spec/design-007-skills-scripts-design.md
技能入口: skills/discover/SKILL.md

脚本列表:
  extract-questions.py          FR-22  import 问题提取
  ai-classify.py                FR-23  AI 分类
  ai-extract-keywords.py        FR-24  AI 提取关键字
  ai-batch-extract-questions.py FR-25  AI 批量提取问题
  ai-batch-gen-docs.py          FR-26  问题→文档生成
  ai-batch-enhance.py           FR-27  批量文档治理
  import-to-knowledge.py        FR-28  discover→knowledge 导入
  config.py                     共享配置
"""
