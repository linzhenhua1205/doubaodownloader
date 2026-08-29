#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
newwiki2 知识库质量提升脚本
功能：
1. 增强 README.md
2. 为每个子目录创建 index.md
3. 为所有内容文件添加头部元数据
"""

import os
import re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(r"h:\github\cowkb\discover\newwiki2")

# 子目录信息配置
DIR_INFO = {
    "AI-Agent": {
        "cn_name": "AI智能体",
        "description": "AI Agent 相关知识卡片，涵盖智能体架构、框架应用、行业案例等",
        "category": "AI 人工智能",
        "related_dirs": ["AI-模型架构", "AI-训练微调", "ai-models", "programming"],
    },
    "AI-模型架构": {
        "cn_name": "AI模型架构",
        "description": "大模型架构设计、Transformer、MoE、注意力机制等核心技术",
        "category": "AI 人工智能",
        "related_dirs": ["AI-训练微调", "ai-models", "算法优化", "系统底层"],
    },
    "AI-训练微调": {
        "cn_name": "AI训练微调",
        "description": "模型训练、微调技术、训练框架、优化方法等",
        "category": "AI 人工智能",
        "related_dirs": ["AI-模型架构", "ai-models", "算法优化", "数据工程"],
    },
    "ai-models": {
        "cn_name": "AI模型库",
        "description": "各类 AI 模型介绍、对比、评测、行业报告等",
        "category": "AI 人工智能",
        "related_dirs": ["AI-模型架构", "AI-训练微调", "AI-Agent", "研究与论文"],
    },
    "cloud-infra": {
        "cn_name": "云基础设施(英)",
        "description": "云原生、容器化、DevOps 等云基础设施技术",
        "category": "基础设施",
        "related_dirs": ["云基础设施", "linux-system", "server-hardware", "数据工程"],
    },
    "data-analysis": {
        "cn_name": "数据分析",
        "description": "数据工程、数据库系统、数据分析方法等",
        "category": "数据科学",
        "related_dirs": ["数据工程", "programming", "general"],
    },
    "general": {
        "cn_name": "综合其他",
        "description": "跨领域知识、思维方法、历史人文、行业观察等综合内容",
        "category": "综合类",
        "related_dirs": ["programming", "project-mgmt", "research", "product-reports"],
    },
    "linux-system": {
        "cn_name": "Linux系统",
        "description": "Linux 操作系统、性能优化、系统管理等",
        "category": "基础设施",
        "related_dirs": ["系统底层", "云基础设施", "security", "programming"],
    },
    "networking": {
        "cn_name": "网络技术(英)",
        "description": "网络协议、网络架构、网络安全等",
        "category": "基础设施",
        "related_dirs": ["网络", "security", "cloud-infra", "server-hardware"],
    },
    "papers-research": {
        "cn_name": "论文研究(英)",
        "description": "AI 系统研究论文、学术进展等",
        "category": "研究学术",
        "related_dirs": ["研究与论文", "research", "AI-模型架构", "ai-models"],
    },
    "product-reports": {
        "cn_name": "产品报告",
        "description": "行业报告、产品分析、市场研究等",
        "category": "产品商业",
        "related_dirs": ["project-mgmt", "general", "research"],
    },
    "programming": {
        "cn_name": "编程开发(英)",
        "description": "编程语言、软件开发、架构设计、工程实践等",
        "category": "软件开发",
        "related_dirs": ["编程语言", "软件架构", "project-mgmt", "AI-Agent"],
    },
    "project-mgmt": {
        "cn_name": "项目管理",
        "description": "项目管理方法论、产品管理、团队协作、商业策略等",
        "category": "产品商业",
        "related_dirs": ["product-reports", "programming", "general", "research"],
    },
    "research": {
        "cn_name": "研究(英)",
        "description": "各类研究主题、前沿探索、技术趋势等",
        "category": "研究学术",
        "related_dirs": ["研究与论文", "papers-research", "ai-models", "general"],
    },
    "security": {
        "cn_name": "安全(英)",
        "description": "网络安全、系统安全、数据安全、安全最佳实践等",
        "category": "安全领域",
        "related_dirs": ["安全", "networking", "linux-system", "云基础设施"],
    },
    "server-hardware": {
        "cn_name": "服务器硬件(英)",
        "description": "服务器硬件架构、GPU 服务器、存储网络、算力平台等",
        "category": "基础设施",
        "related_dirs": ["服务器硬件", "cloud-infra", "AI-训练微调", "系统底层"],
    },
    "云基础设施": {
        "cn_name": "云基础设施(中)",
        "description": "容器、K8s、微服务、云原生架构等",
        "category": "基础设施",
        "related_dirs": ["cloud-infra", "linux-system", "数据工程", "软件架构"],
    },
    "安全": {
        "cn_name": "安全(中)",
        "description": "认证授权、安全架构、信息安全等",
        "category": "安全领域",
        "related_dirs": ["security", "networking", "云基础设施", "系统底层"],
    },
    "数据工程": {
        "cn_name": "数据工程",
        "description": "数据架构、数据库、大数据处理、数据存储等",
        "category": "数据科学",
        "related_dirs": ["data-analysis", "云基础设施", "programming", "server-hardware"],
    },
    "服务器硬件": {
        "cn_name": "服务器硬件(中)",
        "description": "服务器架构、CPU/GPU、存储、散热、硬件管理等",
        "category": "基础设施",
        "related_dirs": ["server-hardware", "系统底层", "云基础设施", "数据工程"],
    },
    "研究与论文": {
        "cn_name": "研究与论文(中)",
        "description": "学术论文、研究方法、前沿技术追踪等",
        "category": "研究学术",
        "related_dirs": ["papers-research", "research", "ai-models", "AI-模型架构"],
    },
    "算法优化": {
        "cn_name": "算法优化",
        "description": "算法设计、网络优化、性能优化等",
        "category": "软件开发",
        "related_dirs": ["AI-模型架构", "AI-训练微调", "programming", "系统底层"],
    },
    "系统底层": {
        "cn_name": "系统底层",
        "description": "操作系统内核、内存管理、CPU 架构、底层优化等",
        "category": "基础设施",
        "related_dirs": ["linux-system", "服务器硬件", "算法优化", "security"],
    },
    "综合其他": {
        "cn_name": "综合其他(中)",
        "description": "通用知识、跨领域内容等",
        "category": "综合类",
        "related_dirs": ["general", "research", "product-reports"],
    },
    "编程语言": {
        "cn_name": "编程语言",
        "description": "Go、Java、Python、Rust 等编程语言学习",
        "category": "软件开发",
        "related_dirs": ["programming", "软件架构", "数据工程", "云基础设施"],
    },
    "网络": {
        "cn_name": "网络技术(中)",
        "description": "网络架构、网络协议等",
        "category": "基础设施",
        "related_dirs": ["networking", "security", "云基础设施", "server-hardware"],
    },
    "软件架构": {
        "cn_name": "软件架构",
        "description": "软件架构设计、架构模式、分布式系统等",
        "category": "软件开发",
        "related_dirs": ["programming", "云基础设施", "数据工程", "project-mgmt"],
    },
}

# 按主题领域分类
CATEGORY_GROUPS = {
    "AI 人工智能": ["AI-Agent", "AI-模型架构", "AI-训练微调", "ai-models"],
    "基础设施": ["cloud-infra", "linux-system", "networking", "server-hardware", "云基础设施", "服务器硬件", "网络", "系统底层"],
    "软件开发": ["programming", "算法优化", "编程语言", "软件架构"],
    "数据科学": ["data-analysis", "数据工程"],
    "安全领域": ["security", "安全"],
    "研究学术": ["papers-research", "research", "研究与论文"],
    "产品商业": ["product-reports", "project-mgmt"],
    "综合类": ["general", "综合其他"],
}


def get_file_size(filepath):
    """获取文件大小，返回可读格式"""
    size = os.path.getsize(filepath)
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size/1024:.1f} KB"
    else:
        return f"{size/(1024*1024):.1f} MB"


def extract_title(filepath):
    """从文件中提取标题（H1）"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("# "):
                    return line[2:].strip()
    except Exception:
        pass
    return filepath.stem


def extract_summary(filepath, max_len=80):
    """提取文件内容摘要"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        # 去掉标题
        content = re.sub(r"^# .*?\n", "", content, flags=re.MULTILINE)
        # 去掉引用块
        content = re.sub(r"^>.*?\n", "", content, flags=re.MULTILINE)
        # 去掉分隔线
        content = content.replace("---", "")
        # 去掉多余空白
        content = re.sub(r"\s+", " ", content).strip()
        if len(content) > max_len:
            return content[:max_len] + "..."
        return content if content else "—"
    except Exception:
        return "—"


def has_metadata(filepath):
    """检查文件是否已有元数据头部"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return "**来源**: newwiki2 知识卡片" in content
    except Exception:
        return False


def add_metadata(filepath, category_name):
    """为文件添加头部元数据，返回是否成功添加"""
    if has_metadata(filepath):
        return False
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 找到第一个 H1 标题的位置
        match = re.search(r"^# .+?\n", content, re.MULTILINE)
        if not match:
            return False
        
        h1_end = match.end()
        
        metadata = f"""> **来源**: newwiki2 知识卡片
> **主题分类**: {category_name}
> **素材等级**: ⭐⭐（待提炼整理）

"""
        
        new_content = content[:h1_end] + "\n" + metadata + content[h1_end:]
        
        with open(filepath, "r+", encoding="utf-8") as f:
            # 检查是否已经有空行
            rest = content[h1_end:]
            if rest.startswith("\n"):
                rest = rest[1:]
            new_content = content[:h1_end] + "\n" + metadata + rest
            f.seek(0)
            f.write(new_content)
            f.truncate()
        
        return True
    except Exception as e:
        print(f"  处理失败 {filepath}: {e}")
        return False


def generate_readme():
    """生成增强版 README.md"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 统计各目录文件数
    dir_stats = {}
    total_files = 0
    for dir_name in sorted(os.listdir(BASE_DIR)):
        dir_path = BASE_DIR / dir_name
        if dir_path.is_dir() and not dir_name.startswith("."):
            md_files = list(dir_path.glob("*.md"))
            # 排除 index.md
            content_files = [f for f in md_files if f.name != "index.md"]
            dir_stats[dir_name] = len(content_files)
            total_files += len(content_files)
    
    # 生成按主题分类的表格
    category_tables = ""
    for category, dirs in CATEGORY_GROUPS.items():
        category_tables += f"### {category}\n\n"
        category_tables += "| 目录名 | 中文说明 | 文件数 | 简介 |\n"
        category_tables += "|--------|----------|--------|------|\n"
        for d in dirs:
            if d in DIR_INFO and d in dir_stats:
                info = DIR_INFO[d]
                category_tables += f"| [{d}]({d}/) | {info['cn_name']} | {dir_stats[d]} | {info['description']} |\n"
        category_tables += "\n"
    
    # 全部目录列表
    all_dirs_table = "## 完整目录列表\n\n"
    all_dirs_table += "| 序号 | 目录名 | 中文名称 | 主题分类 | 文件数 |\n"
    all_dirs_table += "|------|--------|----------|----------|--------|\n"
    
    idx = 1
    for category, dirs in CATEGORY_GROUPS.items():
        for d in dirs:
            if d in DIR_INFO and d in dir_stats:
                info = DIR_INFO[d]
                all_dirs_table += f"| {idx} | [{d}]({d}/) | {info['cn_name']} | {category} | {dir_stats[d]} |\n"
                idx += 1
    
    content = f"""# newwiki2 知识库

> **定位**: AI 生成的知识卡片素材库
> **规模**: {len(dir_stats)} 个子目录 · {total_files} 个知识卡片
> **最近更新**: {today}
> **素材等级**: ⭐⭐（原始素材，待提炼整理）

---

## 📋 目录说明

newwiki2 是一个由 AI 生成的知识卡片集合，涵盖人工智能、基础设施、软件开发、数据科学等多个技术领域。每个文件是一个独立主题的知识卡片，包含相关主题的核心内容摘要。

### 特点

- **素材级别**: 内容为 AI 生成的原始素材，需要进一步提炼整理
- **主题丰富**: 覆盖 8 大领域，{len(dir_stats)} 个细分方向
- **中英文混合**: 目录名包含中英文，便于不同使用习惯
- **持续更新**: 知识卡片会随着学习和探索持续补充

---

## 🗂️ 主题分类导航

{category_tables}
---

{all_dirs_table}
---

## 📖 阅读指南

### 如何使用本知识库

1. **按主题浏览**: 通过上方分类表找到感兴趣的领域，进入对应子目录
2. **使用目录索引**: 每个子目录都有 `index.md`，提供该目录下所有文件的清单和摘要
3. **快速筛选**: 通过文件名大致了解内容主题，配合 index.md 的摘要快速定位

### 素材等级说明

| 等级 | 标识 | 说明 |
|------|------|------|
| ⭐⭐ | 待提炼整理 | 原始素材，内容较散乱，需进一步提炼 |
| ⭐⭐⭐ | 已初步整理 | 经过基本整理，结构较清晰 |
| ⭐⭐⭐⭐ | 高质量笔记 | 经过深度加工，可作为学习资料 |

> 当前 newwiki2 整体为 ⭐⭐ 素材等级

---

## 🔗 与其他知识库的关系

| 知识库 | 定位 | 关系 |
|--------|------|------|
| [knowledge/](../../knowledge/) | 正式知识体系 | 经过深度整理的结构化知识，是 newwiki2 的目标形态 |
| [newwiki/](../newwiki/) | 前一代知识卡片 | 早期版本的知识卡片，newwiki2 是其升级重构版 |
| **newwiki2/** | 素材库 | 原始素材积累，待提炼后进入 knowledge/ |

### 流转关系

```
newwiki2 (素材积累) → 提炼整理 → knowledge (正式知识)
     ↑
  AI 生成 / 收集
```

---

## 📝 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|----------|
| {today} | v2.0 | 大规模质量提升：增强 README、新增子目录 index.md、统一文件元数据 |
| 2026-06-25 | v1.0 | 初始版本，AI 生成 3049 条知识卡片 |

---

*本知识库由 AI 辅助生成，内容仅供参考学习使用*
"""
    
    with open(BASE_DIR / "README.md", "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"✓ 已生成 README.md")
    return len(dir_stats), total_files


def generate_index_md():
    """为每个子目录生成 index.md，返回创建数量"""
    count = 0
    today = datetime.now().strftime("%Y-%m-%d")
    
    for dir_name in sorted(os.listdir(BASE_DIR)):
        dir_path = BASE_DIR / dir_name
        if not dir_path.is_dir() or dir_name.startswith("."):
            continue
        
        info = DIR_INFO.get(dir_name, {
            "cn_name": dir_name,
            "description": "知识卡片集合",
            "category": "未分类",
            "related_dirs": [],
        })
        
        # 获取所有 md 文件（排除 index.md）
        md_files = sorted([f for f in dir_path.glob("*.md") if f.name != "index.md"])
        
        # 生成文件清单表格
        file_table = "| 序号 | 文件名 | 内容标题 | 文件大小 |\n"
        file_table += "|------|--------|----------|----------|\n"
        
        for i, f in enumerate(md_files, 1):
            title = extract_title(f)
            size = get_file_size(f)
            file_table += f"| {i} | [{f.name}]({f.name}) | {title} | {size} |\n"
        
        # 核心主题速览 - 从文件名提取关键词
        keywords = set()
        for f in md_files[:20]:
            name = f.stem
            # 提取有意义的关键词
            parts = re.split(r'[-_\s]', name)
            for p in parts:
                if len(p) >= 2 and len(p) <= 15:
                    keywords.add(p)
        keywords_str = "、".join(list(keywords)[:15]) if keywords else "—"
        
        # 关联目录
        related_links = []
        for rd in info.get("related_dirs", []):
            if (BASE_DIR / rd).exists():
                rd_info = DIR_INFO.get(rd, {"cn_name": rd})
                related_links.append(f"[{rd}（{rd_info['cn_name']}）](../{rd}/)")
        related_str = "、".join(related_links) if related_links else "—"
        
        content = f"""# {dir_name} — {info['cn_name']}

> **定位**: {info['description']}
> **主题分类**: {info['category']}
> **文件数量**: {len(md_files)} 个知识卡片
> **更新日期**: {today}
> **素材等级**: ⭐⭐（待提炼整理）

[← 返回上层目录](../README.md)

---

## 📑 文件清单

{file_table}
---

## 🔍 核心主题速览

{keywords_str}

---

## 🔗 关联目录

{related_str}

---

## 📝 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|----------|
| {today} | v1.0 | 初始化目录索引，创建文件清单 |

---

*本目录知识卡片由 AI 生成，内容仅供参考学习使用*
"""
        
        with open(dir_path / "index.md", "w", encoding="utf-8") as f:
            f.write(content)
        
        count += 1
        print(f"✓ 已生成 {dir_name}/index.md ({len(md_files)} 个文件)")
    
    return count


def add_metadata_to_all_files():
    """为所有内容文件添加头部元数据，返回处理数量"""
    count = 0
    skip_count = 0
    
    for dir_name in sorted(os.listdir(BASE_DIR)):
        dir_path = BASE_DIR / dir_name
        if not dir_path.is_dir() or dir_name.startswith("."):
            continue
        
        info = DIR_INFO.get(dir_name, {"cn_name": dir_name})
        category_name = f"{dir_name}（{info['cn_name']}）"
        
        md_files = [f for f in dir_path.glob("*.md") 
                    if f.name not in ("index.md", "README.md")]
        
        for f in md_files:
            if add_metadata(f, category_name):
                count += 1
            else:
                skip_count += 1
        
        print(f"✓ {dir_name}: 处理 {len(md_files)} 个文件")
    
    print(f"\n总计: 新增元数据 {count} 个文件，跳过 {skip_count} 个已存在的文件")
    return count


def main():
    print("=" * 60)
    print("newwiki2 知识库质量提升脚本")
    print("=" * 60)
    
    # 1. 增强 README.md
    print("\n📖 步骤 1: 生成增强版 README.md")
    print("-" * 40)
    dir_count, total_files = generate_readme()
    
    # 2. 生成子目录 index.md
    print(f"\n📂 步骤 2: 为 {dir_count} 个子目录创建 index.md")
    print("-" * 40)
    index_count = generate_index_md()
    
    # 3. 添加文件头部元数据
    print(f"\n📝 步骤 3: 为所有内容文件添加头部元数据")
    print("-" * 40)
    meta_count = add_metadata_to_all_files()
    
    # 统计
    print("\n" + "=" * 60)
    print("✅ 完成！统计信息：")
    print("=" * 60)
    print(f"  子目录数量: {dir_count}")
    print(f"  知识卡片总数: {total_files}")
    print(f"  新建 index.md: {index_count} 个")
    print(f"  新增元数据文件: {meta_count} 个")
    print("=" * 60)


if __name__ == "__main__":
    main()
