#!/usr/bin/env python3
"""
knowledge-special-reports-updater.py — 知识库专项报告自动更新脚本
功能：自动运行各项分析，更新 knowledge/weekly-reports/ 中的 4 个专项报告
运行：python3 scripts/knowledge-special-reports-updater.py

使用说明：
  完整更新: python3 scripts/knowledge-special-reports-updater.py
  仅采集:   python3 scripts/knowledge-special-reports-updater.py --collect-only
  仅报告:   python3 scripts/knowledge-special-reports-updater.py --report-only
  定时:     配合 cron 每周日 15:00 自动执行
"""

import os, sys, json, subprocess, datetime
from pathlib import Path

WORKSPACE = os.path.expanduser("~/cow")
KNOWLEDGE = os.path.join(WORKSPACE, "knowledge")
SCRIPTS_DIR = os.path.join(WORKSPACE, "scripts")
REPORTS_DIR = os.path.join(KNOWLEDGE, "weekly-reports", "07_kb_stat")
TODAY = datetime.date.today().isoformat()

FLAG_COLLECT = "--collect-only" not in sys.argv
FLAG_REPORT = "--report-only" not in sys.argv

def run_cmd(cmd, cwd=WORKSPACE):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd, timeout=120)
    if result.returncode != 0:
        print(f"⚠️ CMD Error: {cmd[:80]}... → {result.stderr[:200]}")
    return result.stdout.strip()

def step(num, desc):
    print(f"\n{'='*60}")
    print(f" [{num}/6] {desc}")
    print(f"{'='*60}")

def main():
    print(f"📊 知识库专项报告自动更新 - {TODAY}")
    
    # Step 1: 采集数据
    step(1, "采集统计数据")
    collector = os.path.join(SCRIPTS_DIR, "knowledge-stats-collector.py")
    if os.path.exists(collector):
        run_cmd(f"python3 {collector}")
        print("✅ 数据采集完成")
    else:
        print("⚠️ 采集脚本不存在，跳过")
    
    # --collect-only: 仅采集数据，不生成索引/报告（2026-08-19 起无 index.md，产物登记走全局 log.md）
    if not FLAG_COLLECT:
        print("\n⏭️ --collect-only 模式：仅采集数据，跳过索引更新与报告生成")
        return
    if not FLAG_REPORT:
        print("\n⏭️ --report-only 模式：跳过报告生成")
        return
    
    # Step 2: 更新 index
    step(2, "生成报告索引")
    reports = sorted([f for f in os.listdir(REPORTS_DIR) if f.endswith(".md")])
    
    index_content = f"""# 📚 weekly-reports 专项报告目录（参考索引，2026-08-19 起仅生成到 tmp，不再写入 knowledge/）

> **更新日期**: {TODAY}
> **报告数**: {len(reports)}

| # | 报告 | 类型 | 说明 |
|:--:|:-----|:----|:------|

"""
    for i, f in enumerate(reports, 1):
        # 从文件名推断类型
        if "directory-evolution" in f or "目录" in f:
            topic = "📁 目录变迁"
        elif "commit" in f or "提交" in f:
            topic = "📊 代码提交"
        elif "domain" in f or "focus" in f or "关注" in f:
            topic = "🎯 领域变迁"
        elif "dimension" in f or "completeness" in f or "完备" in f:
            topic = "📐 维度完备"
        else:
            topic = "📋 其他"
        
        index_content += f"| {i} | [{f}]({f}) | {topic} | {_get_desc(f)} |\n"
    
    # 2026-08-19 起 07_kb_stat/index.md 已移除（全库统一根 index/log）；参考索引仅生成到 tmp；
    # 自动生成的简化索引输出到 tmp/ 供人工参考
    tmp_index = os.path.join(WORKSPACE, "tmp", f"kb-special-reports-index-{TODAY}.md")
    with open(tmp_index, "w", encoding="utf-8") as f:
        f.write(index_content)
    print(f"✅ 参考索引已生成: {tmp_index}（07_kb_stat 不再维护 index.md，2026-08-19 起）")
    
    # Step 3: CLI 报告生成摘要
    step(3, "报告状态检查")
    for f in reports:
        size = os.path.getsize(os.path.join(REPORTS_DIR, f))
        print(f"  {'✅' if size > 2000 else '⚠️'}  {f}  ({size//1000}KB)")
    
    print(f"\n{'='*60}")
    print(f"✅ 全部完成！{len(reports)} 个专项报告已就绪")
    print(f"📂 {REPORTS_DIR}/")
    print(f"{'='*60}")

def _get_desc(filename):
    descs = {
        "01-knowledge-directory-evolution.md": "知识库目录结构演变全景",
        "02-code-commit-analysis.md": "Git提交统计与频率分析",
        "03-domain-focus-shift.md": "关注领域漂移与阶段特征",
        "04-dimension-completeness.md": "各维度完备程度评估",
    }
    # 从文件名匹配
    for key, val in descs.items():
        if key in filename or filename.startswith(key[:15]):
            return val
    return "自动生成的专项报告"

if __name__ == "__main__":
    main()
