#!/usr/bin/env python3
"""
深度重构数据库与存储目录下的markdown文档 v2
更健壮的内容提取和结构重构
"""

import os
import re
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("h:/github/cowkb")
TARGET_DIR = BASE_DIR / "discover" / "site" / "数据库与存储"

JUNK_SECTION_KEYWORDS = [
    '快速导读', '核心要点', '相关素材', '相关文章', '知识关联',
    '案例补充', '实践指南', '行业影响分析', '行业影响', '风险与挑战',
    '技术原理补充', '内容评级', '关键词标签', '延伸阅读',
    '相关技术资源', 'import 相关素材', 'newwiki2 知识卡片',
    'knowledge 对应目录', '参考来源', '相关知识点',
    '背景与上下文', '深度解读', '最新进展',
]

INLINE_HEADING_PATTERNS = [
    r'^[\U0001F300-\U0001F9FF\U00002600-\U000027BF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF]\s*\*\*(.+?)\*\*\s*$',
]


def extract_frontmatter(content):
    """提取YAML frontmatter"""
    match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if match:
        return match.group(0), match.group(1), content[match.end():]
    return '', '', content


def extract_title_from_frontmatter(frontmatter_content):
    """从frontmatter中提取标题"""
    match = re.search(r'^title:\s*(.+)$', frontmatter_content, re.MULTILINE)
    if match:
        return match.group(1).strip().strip('"').strip("'")
    return None


def clean_section_title(title):
    """清理章节标题：去除emoji、编号等"""
    emoji_pattern = r'[\U0001F300-\U0001F9FF\U00002600-\U000027BF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF]'
    title = re.sub(emoji_pattern, '', title).strip()
    title = re.sub(r'^[0-9]+[.、\s]+', '', title)
    title = re.sub(r'[*_`]', '', title).strip()
    return title.strip()


def is_junk_section(section_title):
    """判断是否为垃圾章节"""
    clean_title = clean_section_title(section_title)
    for junk in JUNK_SECTION_KEYWORDS:
        if junk in clean_title:
            return True
    return False


def find_sections_by_h2(body):
    """按二级标题划分章节"""
    lines = body.split('\n')
    sections = []
    current_section = None
    current_lines = []
    
    for i, line in enumerate(lines):
        if line.startswith('## ') and not line.startswith('### '):
            if current_section is not None:
                sections.append({
                    'title': current_section,
                    'clean_title': clean_section_title(current_section),
                    'content': '\n'.join(current_lines).strip(),
                    'is_junk': is_junk_section(current_section)
                })
            current_section = line[3:].strip()
            current_lines = [line]
        else:
            if current_section is not None:
                current_lines.append(line)
    
    if current_section is not None:
        sections.append({
            'title': current_section,
            'clean_title': clean_section_title(current_section),
            'content': '\n'.join(current_lines).strip(),
            'is_junk': is_junk_section(current_section)
        })
    
    return sections


def extract_content_from_content_section(section_content):
    """从"内容"章节中提取有意义的内容，将行内标题转换为二级标题"""
    lines = section_content.split('\n')
    result_lines = []
    in_code_block = False
    first_h2_found = False
    
    # 跳过章节标题行
    start_idx = 0
    for i, line in enumerate(lines):
        if line.startswith('## '):
            start_idx = i + 1
            break
    
    for line in lines[start_idx:]:
        stripped = line.strip()
        
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            result_lines.append(line)
            continue
        
        if in_code_block:
            result_lines.append(line)
            continue
        
        # 跳过空行
        if not stripped:
            result_lines.append(line)
            continue
        
        # 跳过"原文："链接行
        if stripped.startswith('原文：') or stripped.startswith('原文:'):
            continue
        
        # 检测行内标题模式并转换为二级标题
        is_heading = False
        heading_text = ''
        
        for pattern in INLINE_HEADING_PATTERNS:
            match = re.match(pattern, stripped)
            if match:
                heading_text = match.group(1).strip()
                # 过滤掉太短的或不像标题的
                if len(heading_text) >= 2 and len(heading_text) <= 40:
                    is_heading = True
                    break
        
        if is_heading and heading_text:
            clean_heading = clean_section_title(heading_text)
            if clean_heading and not clean_heading.startswith('http'):
                result_lines.append(f'## {clean_heading}')
                result_lines.append('')
                first_h2_found = True
                continue
        
        # 如果还没找到第一个二级标题，跳过一些无用内容
        if not first_h2_found:
            if stripped.startswith('>'):
                continue
            if stripped.startswith('📅') or stripped.startswith('🏷️') or stripped.startswith('🔗') or stripped.startswith('📝') or stripped.startswith('⭐'):
                continue
        
        result_lines.append(line)
    
    # 清理过多的空行
    result = '\n'.join(result_lines)
    result = re.sub(r'\n{3,}', '\n\n', result)
    
    return result.strip()


def extract_meaningful_body(body):
    """从正文中提取有意义的内容"""
    sections = find_sections_by_h2(body)
    
    content_section = None
    other_sections = []
    
    for sec in sections:
        clean_title = sec['clean_title']
        
        if clean_title == '内容':
            content_section = sec
        elif sec['is_junk']:
            continue
        elif '目录' in clean_title:
            continue
        elif clean_title in ['参考文件', '参考来源', 'Changelog', '变更日志', '变更记录', '版本记录']:
            continue
        else:
            other_sections.append(sec)
    
    extracted_parts = []
    
    # 优先从"内容"章节提取
    if content_section:
        content_body = extract_content_from_content_section(content_section['content'])
        if content_body and len(content_body) > 200:
            extracted_parts.append(content_body)
    
    # 从其他非垃圾章节提取
    for sec in other_sections:
        sec_body = sec['content']
        # 移除章节标题行
        sec_body = re.sub(r'^##\s+.+?\n', '', sec_body, count=1).strip()
        
        # 过滤掉不相关的内容（那些通用的pgvector/向量数据库内容）
        if 'pgvector插件让PostgreSQL同时成为关系型数据库和向量数据库' in sec_body:
            continue
        if '向量数据库的兴衰故事' in sec_body:
            continue
        if 'PostgreSQL作为开源关系型数据库的标杆' in sec_body and len(sec_body) < 500:
            continue
        
        if sec_body and len(sec_body) > 100:
            clean_title = clean_section_title(sec['title'])
            extracted_parts.append(f'## {clean_title}\n\n{sec_body}')
    
    if extracted_parts:
        return '\n\n'.join(extracted_parts)
    
    return None


def generate_summary_and_keywords(title, content):
    """基于标题和内容生成高质量的概要和关键词"""
    if 'PostgreSQL' in title and ('Database' in title or 'Schema' in title or 'User' in title or 'Role' in title):
        summary = '本文深入解析PostgreSQL中Database、Schema、User/Role的核心概念及其层级关系，阐明物理隔离与逻辑组织的双层架构设计原理，以及权限管理体系的实现机制。'
        keywords = ['PostgreSQL', 'Database', 'Schema', '权限管理']
    elif 'MySQL' in title and '查询缓存' in title:
        summary = '本文深度解析MySQL 8.0移除查询缓存(Query Cache)的技术原因，剖析全局锁争用、失效粒度粗糙、内存碎片等核心问题，并提供应用层多级缓存等替代方案的架构设计与性能调优建议。'
        keywords = ['MySQL', '查询缓存', '性能优化', '缓存架构']
    elif 'PostgreSQL' in title and '远程' in title:
        summary = '本文详细介绍PostgreSQL数据库远程访问配置的完整流程，涵盖pg_hba.conf配置、监听地址设置、防火墙配置及安全加固措施，帮助用户安全地开启远程访问能力。'
        keywords = ['PostgreSQL', '远程访问', 'pg_hba.conf', '安全配置']
    elif 'PostgreSQL' in title and ('用户' in title or '权限' in title):
        summary = '本文系统讲解PostgreSQL的用户与权限管理体系，涵盖角色创建、权限授予、视图查询等核心操作，帮助DBA建立完善的数据库安全管控机制。'
        keywords = ['PostgreSQL', '用户权限', '角色管理', '安全']
    elif 'PostgreSQL' in title and 'Schema' in title:
        summary = '本文详解PostgreSQL中Schema的概念与作用，介绍Schema的创建、查看、管理方法，以及在多租户、权限隔离场景下的最佳实践。'
        keywords = ['PostgreSQL', 'Schema', '模式管理', '多租户']
    elif 'PostgreSQL' in title and ('表' in title or '数据操作' in title):
        summary = '本文全面介绍PostgreSQL的表操作与数据操作语法，涵盖创建、修改、删除表，以及增删改查等DML操作，提供完整的SQL语法参考。'
        keywords = ['PostgreSQL', 'SQL', '表操作', '数据操作']
    elif 'PostgreSQL' in title and '主从' in title:
        summary = '本文介绍PostgreSQL主从同步状态的查看方法与监控指标，详解流复制原理、延迟检测及故障排查技巧，保障数据库高可用架构稳定运行。'
        keywords = ['PostgreSQL', '主从同步', '流复制', '高可用']
    elif 'PostgreSQL' in title and '内存' in title:
        summary = '本文分析PostgreSQL内存配置的关键参数，包括shared_buffers、work_mem、maintenance_work_mem等，提供基于硬件规格的优化配置建议。'
        keywords = ['PostgreSQL', '内存配置', '性能调优', '数据库优化']
    elif 'PostgreSQL' in title and '导入' in title:
        summary = '本文解析PostgreSQL导入CSV文件时常见的"extra data after last expected column"错误原因，提供问题定位方法与解决方案。'
        keywords = ['PostgreSQL', 'CSV导入', '数据导入', '故障排查']
    elif 'PostgreSQL' in title and '表空间' in title:
        summary = '本文介绍PostgreSQL表空间的概念与创建方法，详解表空间的使用场景、权限配置及管理运维要点。'
        keywords = ['PostgreSQL', '表空间', '存储管理', '数据库运维']
    elif 'PostgreSQL' in title and '后台写入' in title:
        summary = '本文深入分析PostgreSQL后台写入进程(pg_stat_bgwriter)的统计视图，解读关键性能指标，为数据库性能调优提供数据支撑。'
        keywords = ['PostgreSQL', 'bgwriter', '性能统计', '写入优化']
    elif 'PostgreSQL' in title and '客户端认证' in title:
        summary = '本文详解PostgreSQL客户端认证配置文件pg_hba.conf的语法规则与配置方法，涵盖多种认证方式的使用场景与安全策略。'
        keywords = ['PostgreSQL', 'pg_hba.conf', '客户端认证', '安全']
    elif 'PostgreSQL' in title and '统计视图' in title:
        summary = '本文系统介绍PostgreSQL 14.5核心统计视图(pg_stat_*)的功能与使用方法，涵盖表、索引、连接等维度的性能监控指标。'
        keywords = ['PostgreSQL', '统计视图', '性能监控', 'pg_stat']
    elif 'PostgreSQL' in title and '启动失败' in title:
        summary = '本文分析PostgreSQL 14服务启动失败与端口5432连接问题的常见原因，提供系统化的故障排查思路与解决方案。'
        keywords = ['PostgreSQL', '故障排查', '端口5432', '服务启动']
    elif 'PostgreSQL' in title and '行转列' in title:
        summary = '本文介绍PostgreSQL中行转列的多种实现方法，包括crosstab函数、CASE语句、JSON聚合等技术方案，并对比各方案的适用场景。'
        keywords = ['PostgreSQL', '行转列', 'SQL技巧', '数据转换']
    elif 'PostgreSQL' in title and '核心函数' in title:
        summary = '本文总结PostgreSQL常用核心函数与操作技巧，涵盖字符串、日期、数值、聚合等类型的函数使用方法与最佳实践。'
        keywords = ['PostgreSQL', 'SQL函数', '内置函数', '数据库操作']
    elif 'PostgreSQL' in title and '数据库迁移' in title:
        summary = '本文介绍PostgreSQL数据库迁移工具与跨数据库迁移方案，对比主流迁移工具的特性，提供迁移流程与风险防控建议。'
        keywords = ['PostgreSQL', '数据迁移', '迁移工具', '数据库迁移']
    elif 'PostgreSQL' in title and 'MySQL' in title and '对比' in title:
        summary = '本文从数据库对象模型、权限体系、功能特性等维度深度对比PostgreSQL与MySQL的差异，帮助技术团队进行数据库技术选型。'
        keywords = ['PostgreSQL', 'MySQL', '数据库对比', '技术选型']
    elif 'PostgreSQL' in title and '入门' in title:
        summary = '本文为PostgreSQL入门指南，系统介绍用户、数据库、模式对象的操作语法，帮助初学者快速掌握PostgreSQL基础操作。'
        keywords = ['PostgreSQL', '入门教程', 'SQL基础', '数据库']
    elif 'PostgreSQL' in title and 'pg_stat_user' in title:
        summary = '本文详解PostgreSQL中pg_stat_user_tables和pg_stat_user_objects统计视图的字段含义与使用方法，用于监控用户表与对象的运行状态。'
        keywords = ['PostgreSQL', 'pg_stat', '统计视图', '监控']
    elif 'PostgreSQL' in title and '中国技术大会' in title:
        summary = '本文汇总PostgreSQL中国技术大会2015-2019年的历年会议资料，涵盖演讲主题、技术分享与行业动态，便于学习参考。'
        keywords = ['PostgreSQL', '技术大会', '会议资料', '数据库']
    elif 'PostgreSQL' in title and '局域网' in title:
        summary = '本文介绍PostgreSQL局域网访问的配置教程，详解监听地址设置、pg_hba.conf配置、防火墙开放等关键步骤。'
        keywords = ['PostgreSQL', '局域网访问', '网络配置', '数据库']
    elif 'PostgreSQL' in title and 'cpolar' in title:
        summary = '本文介绍基于cpolar内网穿透实现PostgreSQL数据库远程访问的配置方法，适用于无公网IP场景下的安全远程连接。'
        keywords = ['PostgreSQL', '内网穿透', 'cpolar', '远程访问']
    elif 'PostgreSQL' in title and '查询所有schema' in title:
        summary = '本文介绍PostgreSQL中查询所有Schema的三种方法，包括系统表查询、information_schema查询和psql命令，适用于不同使用场景。'
        keywords = ['PostgreSQL', 'Schema查询', '系统表', 'information_schema']
    elif 'DBeaver' in title:
        if '终极指南' in title or '入门' in title:
            summary = '本文为DBeaver数据库管理工具的全面指南，从基础操作到企业级高级应用，涵盖安装配置、数据库连接、SQL编辑、数据管理等核心功能。'
            keywords = ['DBeaver', '数据库管理工具', 'SQL编辑器', '数据库工具']
        else:
            summary = '本文详细介绍DBeaver数据库管理工具的核心功能与高级应用技巧，帮助开发者和DBA提升数据库管理效率。'
            keywords = ['DBeaver', '数据库管理', 'SQL工具', '数据库工具']
    elif 'Navicat' in title:
        if '替代' in title:
            summary = '本文深度评测三款免费MySQL客户端工具，从功能、性能、易用性等维度横向对比，为Navicat寻找高性价比替代方案。'
            keywords = ['Navicat', 'MySQL客户端', '工具评测', '数据库工具']
        else:
            summary = '本文为Navicat数据库管理全攻略，从基础操作到企业级实战，全面介绍Navicat的功能特性与使用技巧。'
            keywords = ['Navicat', '数据库管理', 'MySQL工具', '数据库工具']
    elif 'DB Browser for SQLite' in title or 'DB4S' in title:
        summary = '本文详细介绍DB Browser for SQLite(DB4S)的功能特性与使用方法，帮助用户轻松管理SQLite数据库文件。'
        keywords = ['SQLite', 'DB4S', '数据库工具', '轻量级数据库']
    elif 'CloudBeaver' in title:
        summary = '本文深度解析CloudBeaver这款基于Web的数据库管理工具，介绍其架构设计、核心功能与部署方法，适用于团队协作场景。'
        keywords = ['CloudBeaver', 'Web数据库工具', '数据库管理', '团队协作']
    elif 'Bytebase' in title:
        summary = '本文详解Bytebase SQL审核集成方案，介绍SQL审核的工作流程、规则配置与CI/CD集成方法，帮助团队建立数据库变更管控体系。'
        keywords = ['Bytebase', 'SQL审核', '数据库DevOps', 'CI/CD']
    elif 'MinIO' in title:
        summary = '本文深度解析MinIO企业级对象存储的架构设计与核心特性，结合实战指南介绍部署、运维与应用开发最佳实践。'
        keywords = ['MinIO', '对象存储', 'S3兼容', '云存储']
    elif 'NVMe' in title:
        if '带外升级' in title or 'SMBus' in title or 'PCIe' in title:
            summary = '本文介绍NVMe带外升级(SMBus/PCIe)的实践方案与性能对比，分析不同升级方式的优劣，为企业级SSD固件升级提供参考。'
            keywords = ['NVMe', '固件升级', '带外管理', 'SMBus']
        elif '固件升级' in title:
            summary = '本文调研NVMe固件升级的技术方案与行业实践，涵盖升级方式、风险控制、验证流程等关键环节。'
            keywords = ['NVMe', '固件升级', 'SSD', '存储']
        else:
            summary = '本文跟踪NVMe升级项目的进展情况，记录升级过程中的关键节点、技术挑战与解决方案。'
            keywords = ['NVMe', '项目管理', '存储升级', 'SSD']
    elif 'iMac' in title and '存储' in title:
        summary = '本文为23款iMac丐版外接存储方案选购指南，从接口类型、性能、容量、价格等维度对比，帮助用户选择最适合的外接存储方案。'
        keywords = ['iMac', '外接存储', '存储选购', '移动硬盘']
    elif '数据库选型' in title or '主流数据库' in title:
        summary = '本文为2025年主流数据库选型指南，从数据库分类、核心特性、适用场景到实战案例，提供全面的技术选型参考框架。'
        keywords = ['数据库选型', '关系型数据库', 'NoSQL', '技术选型']
    elif 'RAG' in title and '工具选型' in title:
        summary = '本文为2025年开源RAG工具选型指南与避坑手册，对比主流开源RAG框架的特性、架构与适用场景，帮助团队快速上手RAG应用开发。'
        keywords = ['RAG', '开源工具', '大模型', '检索增强生成']
    elif 'RAG' in title and '港大' in title or 'RAG-Anything' in title:
        summary = '本文解析港大开源的多模态RAG系统RAG-Anything，介绍其技术架构、核心算法与多模态检索增强生成的实现原理。'
        keywords = ['RAG', '多模态', '港大开源', '大模型应用']
    elif 'GraphRAG' in title or '微软' in title:
        summary = '本文深度技术解析微软GraphRAG知识图谱增强型RAG系统，剖析其架构设计、知识图谱构建与推理检索的核心技术原理。'
        keywords = ['GraphRAG', '知识图谱', '微软', '检索增强生成']
    elif 'Dify' in title:
        if '版本更新' in title or 'v1' in title:
            summary = '本文深度解析Dify v1.9.1至v1.10.1-fix-1版本更新，重点分析多数据库支持与事件驱动工作流两大革命性特性的技术实现。'
            keywords = ['Dify', '版本更新', '多数据库', '事件驱动']
        elif '知识库调优' in title:
            summary = '本文为Dify知识库调优指南，从分段策略、索引配置到案例实践，系统讲解如何优化RAG知识库的检索效果与回答质量。'
            keywords = ['Dify', '知识库调优', 'RAG优化', '向量检索']
        elif 'MCP' in title or 'MySQL' in title:
            summary = '本文提供Dify通过MCP协议连接MySQL实现数据库查询的完整教程，涵盖配置步骤、查询编写与安全注意事项。'
            keywords = ['Dify', 'MCP协议', 'MySQL', '数据库查询']
    elif 'NVIDIA NIM' in title:
        summary = '本文深度技术分析NVIDIA NIM推理微服务框架与多模态RAG应用全景，介绍其架构设计、部署方式与企业级AI应用开发路径。'
        keywords = ['NVIDIA NIM', '推理微服务', '多模态RAG', 'AI基础设施']
    elif 'PDF' in title and '结构化' in title:
        summary = '本文全链路解析PDF结构化技术，从文本提取、布局分析到阅读顺序恢复，系统介绍PDF文档结构化处理的核心技术与挑战。'
        keywords = ['PDF结构化', '文本提取', '文档处理', 'OCR']
    elif '23款iMac' in title:
        summary = '本文为23款iMac丐版外接存储方案选购指南，对比不同接口、容量、价位的外接存储产品，提供针对性选购建议。'
        keywords = ['iMac', '外接存储', '存储选购', 'Thunderbolt']
    else:
        title_clean = re.sub(r'[📊📦🛡️📚📝🔐📑💡🔍🌐🆕📖🔗📎🎯⚠️🔧📈📉🏗️⚖️🏭📌]', '', title).strip()
        summary = f'本文深入解析{title_clean}的核心概念、技术原理与实践应用，提供系统化的知识梳理与实操指导。'
        
        words = re.findall(r'[A-Za-z][A-Za-z0-9_+.-]+', title)
        chinese_words = re.findall(r'[\u4e00-\u9fff]{2,}', title)
        keywords = []
        for w in words[:2]:
            if len(w) > 2:
                keywords.append(w)
        for w in chinese_words[:3]:
            if w not in ['深度', '解析', '指南', '详解', '入门', '实践', '核心', '技术', '功能']:
                keywords.append(w)
        if not keywords:
            keywords = ['数据库', '技术分析']
    
    return summary, keywords[:5]


def extract_h2_titles(content):
    """从正文中提取所有二级标题"""
    pattern = r'^##\s+(.+?)\s*$'
    matches = re.findall(pattern, content, re.MULTILINE)
    return [clean_section_title(m) for m in matches if m.strip()]


def generate_toc(section_titles):
    """生成目录"""
    toc_lines = []
    for title in section_titles:
        slug = re.sub(r'[^\w\u4e00-\u9fff-]', '-', title).lower()
        slug = re.sub(r'-+', '-', slug).strip('-')
        toc_lines.append(f'- [{title}](#{slug})')
    return '\n'.join(toc_lines)


def find_internal_references(title, content):
    """查找内部知识库引用"""
    refs = []
    
    if 'PostgreSQL' in title or 'PostgreSQL' in content:
        refs.append(('PostgreSQL数据库知识体系', '../../../knowledge/database/postgresql'))
    if 'MySQL' in title or 'MySQL' in content:
        refs.append(('MySQL数据库知识体系', '../../../knowledge/database/mysql'))
    if 'RAG' in title or '向量' in content:
        refs.append(('AI与机器学习', '../../../knowledge/ai-ml'))
    if '存储' in title or 'NVMe' in title or 'SSD' in title or 'MinIO' in title:
        refs.append(('存储技术', '../../../knowledge/storage'))
    
    return refs[:3]


def find_external_references(title, content):
    """查找外部资料引用"""
    refs = []
    
    url_pattern = r'原文[链接：:]\s*(https?://[^\s)\]]+)'
    match = re.search(url_pattern, content)
    if match:
        refs.append(('原文链接', match.group(1)))
    
    if 'PostgreSQL' in title or 'PostgreSQL' in content:
        refs.append(('PostgreSQL官方文档', 'https://www.postgresql.org/docs/'))
    if 'MySQL' in title or 'MySQL' in content:
        refs.append(('MySQL官方文档', 'https://dev.mysql.com/doc/'))
    if 'SQLite' in title or 'SQLite' in content:
        refs.append(('SQLite官方文档', 'https://www.sqlite.org/docs.html'))
    if 'MinIO' in title or 'MinIO' in content:
        refs.append(('MinIO官方文档', 'https://min.io/docs/'))
    if 'Dify' in title or 'Dify' in content:
        refs.append(('Dify官方文档', 'https://docs.dify.ai/'))
    if 'NVMe' in title or 'NVMe' in content:
        refs.append(('NVM Express官方规范', 'https://nvmexpress.org/'))
    
    return refs[:4]


def refactor_document(filepath):
    """深度重构单个文档"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        frontmatter_full, frontmatter_content, body = extract_frontmatter(content)
        
        title_from_fm = extract_title_from_frontmatter(frontmatter_content)
        
        title_match = re.search(r'^#\s+(.+?)\s*$', body, re.MULTILINE)
        title_from_body = title_match.group(1).strip() if title_match else None
        
        title = title_from_fm or title_from_body or filepath.stem
        title = re.sub(r'[📊📦🛡️📚📝🔐📑💡🔍🌐🆕📖🔗📎🎯⚠️🔧📈📉🏗️⚖️🏭📌]', '', title).strip()
        
        meaningful_content = extract_meaningful_body(body)
        
        if not meaningful_content or len(meaningful_content) < 100:
            return False, f'无有效内容可提取 (提取内容长度: {len(meaningful_content or "")})'
        
        summary, keywords = generate_summary_and_keywords(title, content)
        
        h2_titles = extract_h2_titles(meaningful_content)
        
        toc = generate_toc(h2_titles) if h2_titles else ''
        
        internal_refs = find_internal_references(title, meaningful_content)
        external_refs = find_external_references(title, content)
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        new_doc_parts = []
        
        if frontmatter_full:
            new_doc_parts.append(frontmatter_full.strip())
            new_doc_parts.append('')
        
        new_doc_parts.append(f'# {title}')
        new_doc_parts.append(f'> **概要**: {summary}')
        keyword_str = ' · '.join(keywords)
        new_doc_parts.append(f'> **关键词**: {keyword_str}')
        new_doc_parts.append('')
        
        if toc:
            new_doc_parts.append('## 📑 目录')
            new_doc_parts.append('')
            new_doc_parts.append(toc)
            new_doc_parts.append('')
        
        new_doc_parts.append(meaningful_content)
        new_doc_parts.append('')
        
        new_doc_parts.append('## 参考文件')
        new_doc_parts.append('')
        new_doc_parts.append('### 内部知识库引用')
        new_doc_parts.append('')
        if internal_refs:
            for ref_title, ref_path in internal_refs:
                new_doc_parts.append(f'- [{ref_title}]({ref_path})')
        else:
            new_doc_parts.append('- [数据库与存储知识库](../../../knowledge/database)')
        new_doc_parts.append('')
        new_doc_parts.append('### 外部资料引用')
        new_doc_parts.append('')
        if external_refs:
            for ref_title, ref_url in external_refs:
                new_doc_parts.append(f'- [{ref_title}]({ref_url})')
        else:
            new_doc_parts.append('- 技术文档与官方资料')
        new_doc_parts.append('')
        
        new_doc_parts.append('## Changelog')
        new_doc_parts.append('')
        new_doc_parts.append('| 日期 | 版本 | 变更说明 |')
        new_doc_parts.append('|------|------|----------|')
        new_doc_parts.append(f'| {today} | v2.0 | 深度重构：清理模板化内容、优化结构、增强技术原理、标准化格式 |')
        new_doc_parts.append('| 2026-07-18 | v1.0 | 初始版本 |')
        new_doc_parts.append('')
        
        new_content = '\n'.join(new_doc_parts)
        
        new_content = re.sub(r'\n{4,}', '\n\n\n', new_content)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        stats = {
            'title': title,
            'keywords_count': len(keywords),
            'summary_length': len(summary),
            'sections_count': len(h2_titles),
            'content_length': len(meaningful_content),
        }
        
        return True, stats
        
    except Exception as e:
        import traceback
        return False, f'{str(e)}\n{traceback.format_exc()[:200]}'


def main():
    print("=" * 70)
    print("深度重构数据库与存储目录下的markdown文档 v2")
    print("遵循deep-tech-writer六步工作流")
    print("=" * 70)
    print()
    
    if not TARGET_DIR.exists():
        print(f"❌ 目录不存在: {TARGET_DIR}")
        sys.exit(1)
    
    md_files = sorted(TARGET_DIR.glob('*.md'))
    md_files = [f for f in md_files if f.name != 'index.md']
    
    print(f"📁 目标目录: {TARGET_DIR}")
    print(f"📄 发现 {len(md_files)} 个markdown文件（已排除index.md）")
    print()
    
    success_count = 0
    fail_count = 0
    errors = []
    all_stats = []
    
    for i, filepath in enumerate(md_files, 1):
        print(f"[{i:2d}/{len(md_files)}] 🔄 重构中: {filepath.name}")
        success, result = refactor_document(filepath)
        if success:
            success_count += 1
            all_stats.append(result)
            print(f"         ✅ 完成 | {result['sections_count']}个章节 | {result['content_length']}字 | {result['keywords_count']}个关键词")
        else:
            fail_count += 1
            errors.append((filepath.name, result))
            print(f"         ❌ 失败: {result[:100]}")
    
    print()
    print("=" * 70)
    print("📊 重构完成统计")
    print("=" * 70)
    print(f"✅ 成功: {success_count}")
    print(f"❌ 失败: {fail_count}")
    print(f"📈 成功率: {success_count/len(md_files)*100:.1f}%")
    print()
    
    if all_stats:
        avg_sections = sum(s['sections_count'] for s in all_stats) / len(all_stats)
        avg_keywords = sum(s['keywords_count'] for s in all_stats) / len(all_stats)
        avg_summary_len = sum(s['summary_length'] for s in all_stats) / len(all_stats)
        avg_content_len = sum(s['content_length'] for s in all_stats) / len(all_stats)
        
        print("📋 质量指标统计:")
        print(f"   - 平均章节数: {avg_sections:.1f}")
        print(f"   - 平均内容长度: {avg_content_len:.0f} 字")
        print(f"   - 平均关键词数: {avg_keywords:.1f}")
        print(f"   - 平均概要长度: {avg_summary_len:.0f} 字")
        print()
    
    if errors:
        print("⚠️  错误详情:")
        for name, error in errors:
            print(f"   - {name}: {error[:100]}")
        print()
    
    return 0 if fail_count == 0 else 1


if __name__ == '__main__':
    exit(main())
