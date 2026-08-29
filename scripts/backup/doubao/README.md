# scripts/backup/doubao/ — 归档说明

> **状态**: 已归档（2026-08-10 确认）· **勿直接使用**

## 替代关系（W32 S8 评估结论）

本目录 46 个文件为**豆包（Doubao）分享链接抓取/导出脚本**的历史迭代（v1-v7 系列：
`doubao_scraper` / `doubao_selenium_export` / `doubao_auto_login` / `batch_export_doubao*` /
`analyze_doubao_md*` 等），**已被 `skills/doubao-share/` skill 完整替代**（获取→提取→归档→
kb-log-append 全流程，2026-08-03 起）。

> ⚠️ 修正：W32 质量报告 S8 称「被 wechat-fetch.py 替代」——**不准确**。
> wechat-fetch.py 是微信文章抓取（UA+chksm 反爬），与豆包无关；豆包的替代者是 doubao-share skill。

## 保留策略

- 保留于 `scripts/backup/`（已是归档区），**不删除**（永不 rm 铁律）
- 如需复用豆包抓取能力 → 使用 `skills/doubao-share/SKILL.md` 工作流
- 本目录仅作历史参考，引用前先确认内容未被替代（RULE.md 铁律 4）
