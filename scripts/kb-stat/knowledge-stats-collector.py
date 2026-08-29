#!/usr/bin/env python3
"""
knowledge-stats-collector.py — 知识库统计数据采集脚本
功能：自动收集知识库目录变迁、Git提交统计、各模块规模等数据
用途：供 weekly-report 专项报告使用
运行：python3 scripts/knowledge-stats-collector.py
输出：tmp/knowledge-stats-{日期}.json
"""

import os, json, subprocess, datetime
from pathlib import Path

WORKSPACE = os.path.expanduser("~/cow")
KNOWLEDGE = os.path.join(WORKSPACE, "knowledge")
OUTPUT_DIR = os.path.join(WORKSPACE, "tmp")
os.makedirs(OUTPUT_DIR, exist_ok=True)

TODAY = datetime.date.today().isoformat()

def run_cmd(cmd, cwd=WORKSPACE):
    """Run shell command and return stdout"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd, timeout=60)
    return result.stdout.strip()

def collect_git_stats():
    """Git 提交统计"""
    stats = {}
    
    # 总提交数
    stats["total_commits"] = int(run_cmd("git log --oneline --all | wc -l") or 0)
    
    # 日期范围
    first_commit = run_cmd("git log --reverse --all --format='%ai' | head -1")
    last_commit = run_cmd("git log --all --format='%ai' | head -1")
    stats["first_commit"] = first_commit
    stats["last_commit"] = last_commit
    
    # 作者统计
    author_output = run_cmd("git shortlog -sn --all")
    authors = {}
    for line in author_output.split("\n"):
        parts = line.strip().split("\t")
        if len(parts) == 2:
            count, name = parts
            authors[name] = int(count.strip())
    stats["authors"] = authors
    
    # 按日提交
    daily = run_cmd("git log --all --format='%ai' | cut -d' ' -f1 | sort | uniq -c | sort -rn")
    day_stats = {}
    for line in daily.split("\n"):
        parts = line.strip().split()
        if len(parts) == 2:
            count, date = parts
            day_stats[date] = int(count)
    stats["daily_commits"] = day_stats
    
    # 按月提交
    monthly = run_cmd(r"git log --all --format='%ai' | awk '{split($1,d,\"-\"); ym=d[1]\"-\"d[2]; cnt[ym]++} END{for(k in cnt) print k, cnt[k]}' | sort")
    month_stats = {}
    for line in monthly.split("\n"):
        parts = line.strip().split()
        if len(parts) == 2:
            ym, count = parts
            month_stats[ym] = int(count)
    stats["monthly_commits"] = month_stats
    
    # 按知识库模块提交
    modules = {}
    for mod in ["01_survey", "02_rd", "03_AI", "04_person", "05_tools", "06_others", "07_industry-research", "concepts", "methodology", "weekly-reports"]:
        mod_path = f"knowledge/{mod}/"
        mod_count = int(run_cmd(f"git log --all --oneline -- '{mod_path}' | wc -l") or 0)
        modules[mod] = mod_count
    stats["module_commits"] = modules
    
    return stats


def collect_knowledge_stats():
    """知识库文件统计"""
    stats = {}
    
    # 总文件
    all_md = int(run_cmd(f"find {KNOWLEDGE} -type f -name '*.md' | wc -l") or 0)
    all_files = int(run_cmd(f"find {KNOWLEDGE} -type f | wc -l") or 0)
    total_size = run_cmd(f"du -sh {KNOWLEDGE} | cut -f1")
    total_dirs = int(run_cmd(f"find {KNOWLEDGE} -type d | wc -l") or 0)
    
    stats["total_md_files"] = all_md
    stats["total_files"] = all_files
    stats["total_size"] = total_size
    stats["total_dirs"] = total_dirs
    
    # 顶层模块统计
    modules = {}
    top_dirs = ["01_survey", "02_rd", "03_AI", "04_person", "05_tools", "06_others", 
                "07_industry-research", "concepts", "methodology", "weekly-reports", "bak"]
    
    for mod in top_dirs:
        mod_path = os.path.join(KNOWLEDGE, mod)
        if os.path.isdir(mod_path):
            md_count = int(run_cmd(f"find {mod_path} -type f -name '*.md' | wc -l") or 0)
            size = run_cmd(f"du -sh {mod_path} | cut -f1")
            dir_count = int(run_cmd(f"find {mod_path} -type d | wc -l") or 0)
            modules[mod] = {
                "md_files": md_count,
                "size": size,
                "dirs": dir_count
            }
    
    stats["modules"] = modules
    
    # 最大深度
    max_depth = run_cmd(f"find {KNOWLEDGE} -type d | awk -F/ '{{print NF-1}}' | sort -rn | head -1")
    stats["max_depth"] = int(max_depth or 4)
    
    return stats


def collect_memory_stats():
    """记忆文件统计"""
    memory_dir = os.path.join(WORKSPACE, "memory")
    stats = {}
    
    if os.path.isdir(memory_dir):
        files = sorted([f for f in os.listdir(memory_dir) if f.endswith(".md") and f != "README.md"])
        stats["memory_files"] = len(files)
        
        # 最早的记忆文件
        dream_dir = os.path.join(memory_dir, "dreams")
        if os.path.isdir(dream_dir):
            dream_files = [f for f in os.listdir(dream_dir) if f.endswith(".md")]
            stats["dream_files"] = len(dream_files)
        else:
            stats["dream_files"] = 0
    else:
        stats["memory_files"] = 0
        stats["dream_files"] = 0
    
    return stats


def main():
    print(f"📊 知识库统计数据采集 - {TODAY}")
    print("="*50)
    
    print("1/3 采集 Git 统计...")
    git_stats = collect_git_stats()
    print(f"   ✓ 总提交: {git_stats['total_commits']}")
    
    print("2/3 采集知识库统计...")
    kb_stats = collect_knowledge_stats()
    print(f"   ✓ 总文件: {kb_stats['total_files']} ({kb_stats['total_size']})")
    
    print("3/3 采集记忆文件统计...")
    mem_stats = collect_memory_stats()
    print(f"   ✓ 记忆文件: {mem_stats['memory_files']}")
    
    # 合并输出
    output = {
        "date": TODAY,
        "git": git_stats,
        "knowledge": kb_stats,
        "memory": mem_stats
    }
    
    output_path = os.path.join(OUTPUT_DIR, f"knowledge-stats-{TODAY}.json")
    with open(output_path, "w") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 数据已保存: {output_path}")
    
    # 打印摘要
    print(f"\n📋 摘要")
    print(f"  Commits: {git_stats['total_commits']}")
    print(f"  文件: {kb_stats['total_md_files']} md / {kb_stats['total_files']} 总")
    print(f"  目录: {kb_stats['total_dirs']}")
    print(f"  大小: {kb_stats['total_size']}")
    
    print(f"\n📦 模块分布")
    for mod, data in sorted(kb_stats.get("modules", {}).items()):
        print(f"  {mod}: {data['md_files']} files, {data['size']}")
    
    return output


if __name__ == "__main__":
    main()
