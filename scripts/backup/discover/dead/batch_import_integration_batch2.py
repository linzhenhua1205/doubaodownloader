#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
import 素材大规模深度嵌入 - 第一批第二批 AI 技术类
处理 AI-模型架构剩余文件 + ai-models 技术卡片 + newwiki 大模型技术与原理
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from batch_import_integration import ImportIntegration


def main():
    discover_root = r'h:\github\cowkb\discover'
    import_root = r'h:\github\cowkb\import'
    
    integrator = ImportIntegration(discover_root, import_root)
    
    print("="*60)
    print("第一批（续）：AI 技术类内容整合 - 剩余文件")
    print("="*60)
    
    ai_model_arch = os.path.join(discover_root, 'newwiki2', 'AI-模型架构')
    ai_models = os.path.join(discover_root, 'newwiki2', 'ai-models')
    newwiki_dir = os.path.join(discover_root, 'newwiki')
    doubao_dir = os.path.join(import_root, 'doubao')
    qianwen_dir = os.path.join(import_root, '千问')
    cnblogs_dir = os.path.join(import_root, 'cnblogs')
    
    integration_map = []
    
    # ========== AI-模型架构 剩余文件 ==========
    ai_arch_rest = [
        'agent.md', 'container.md', 'cpu.md', 'database.md', 'docker.md',
        'index.md', 'java.md', 'linux.md', 'network.md', 'nvidia.md',
        'paper.md', 'pcie.md', 'prompt.md', 'python.md', 'research.md',
        'security.md', 'server.md', 'sql.md', 'storage.md', 'auth.md'
    ]
    
    for fname in ai_arch_rest:
        fpath = os.path.join(ai_model_arch, fname)
        if not os.path.exists(fpath):
            continue
        
        sources = []
        
        # 根据文件名匹配素材
        name_lower = fname.lower()
        
        if 'agent' in name_lower:
            sources.append({
                'source': os.path.join(qianwen_dir, 'AI-Agent技术架构.md'),
                'section': '技术详解',
                'title': 'AI Agent技术架构综述',
                'keywords': ['Agent', '智能体', '架构', '协作'],
                'max_chars': 600
            })
        elif 'prompt' in name_lower:
            sources.append({
                'source': os.path.join(qianwen_dir, '大模型技术与原理.md'),
                'section': '技术详解',
                'title': '提示词工程与模型交互',
                'keywords': ['prompt', '提示词', '指令', '上下文'],
                'max_chars': 500
            })
        elif 'research' in name_lower or 'paper' in name_lower:
            sources.append({
                'source': os.path.join(doubao_dir, '深入研究 (1).md'),
                'section': '技术详解',
                'title': 'AI前沿研究动态',
                'keywords': ['研究', '论文', '前沿', '进展'],
                'max_chars': 500
            })
        elif 'security' in name_lower:
            sources.append({
                'source': os.path.join(qianwen_dir, 'AI伦理与安全.md'),
                'section': '技术详解',
                'title': 'AI安全与伦理考量',
                'keywords': ['安全', '伦理', '风险', '对齐'],
                'max_chars': 500
            })
        elif 'container' in name_lower or 'docker' in name_lower:
            sources.append({
                'source': os.path.join(qianwen_dir, '大模型技术与原理.md'),
                'section': '技术详解',
                'title': 'AI模型部署与容器化',
                'keywords': ['部署', '容器', 'docker', '推理'],
                'max_chars': 400
            })
        elif 'cpu' in name_lower or 'gpu' in name_lower or 'nvidia' in name_lower or 'pcie' in name_lower:
            sources.append({
                'source': os.path.join(qianwen_dir, '服务器与硬件架构.md'),
                'section': '技术详解',
                'title': 'AI算力硬件基础',
                'keywords': ['CPU', 'GPU', '硬件', '算力', '加速'],
                'max_chars': 500
            })
        elif 'database' in name_lower or 'sql' in name_lower or 'storage' in name_lower:
            sources.append({
                'source': os.path.join(qianwen_dir, '数据与存储技术.md'),
                'section': '技术详解',
                'title': 'AI数据存储与管理',
                'keywords': ['数据库', '存储', '数据', '管理'],
                'max_chars': 500
            })
        elif 'linux' in name_lower or 'server' in name_lower:
            sources.append({
                'source': os.path.join(qianwen_dir, '服务器与硬件架构.md'),
                'section': '技术详解',
                'title': 'AI服务器与系统环境',
                'keywords': ['服务器', 'Linux', '系统', '运维'],
                'max_chars': 500
            })
        elif 'python' in name_lower or 'java' in name_lower:
            sources.append({
                'source': os.path.join(qianwen_dir, '大模型技术与原理.md'),
                'section': '技术详解',
                'title': 'AI编程语言与框架',
                'keywords': ['Python', '编程', '框架', '开发'],
                'max_chars': 400
            })
        elif 'network' in name_lower:
            sources.append({
                'source': os.path.join(qianwen_dir, '服务器与硬件架构.md'),
                'section': '技术详解',
                'title': 'AI网络与通信基础',
                'keywords': ['网络', '通信', '互联', '带宽'],
                'max_chars': 400
            })
        else:
            # 默认添加通用大模型素材
            sources.append({
                'source': os.path.join(qianwen_dir, '大模型技术与原理.md'),
                'section': '技术详解',
                'title': '大模型技术基础',
                'keywords': ['大模型', 'AI', '技术', '原理'],
                'max_chars': 500
            })
        
        integration_map.append({
            'target': fpath,
            'sources': sources
        })
    
    # ========== ai-models 技术概念卡片（精选20张） ==========
    ai_models_files = [
        'llm.md', '大模型.md', '大模型架构师.md', '分布式一致性.md',
        'kvcache.md', 'mfu.md', 'nlp.md', 'mcp.md',
        'sglang.md', 'tokens.md', '开源模型本地.md',
        '数据训练对.md', '影响.md', '生成式.md', '突破.md',
        '大规模推理与.md', '大模型训练平.md', '提升大模型回.md',
        '架构思维在分.md', '赋能固件研发.md'
    ]
    
    for fname in ai_models_files:
        fpath = os.path.join(ai_models, fname)
        if not os.path.exists(fpath):
            continue
        
        sources = []
        name_lower = fname.lower()
        
        if 'llm' in name_lower or '大模型' in name_lower:
            sources.append({
                'source': os.path.join(qianwen_dir, '大模型技术与原理.md'),
                'section': '技术详解',
                'title': '大语言模型技术全景',
                'keywords': ['大模型', 'LLM', '语言模型', '技术'],
                'max_chars': 600
            })
        elif 'kvcache' in name_lower or 'cache' in name_lower:
            sources.append({
                'source': os.path.join(qianwen_dir, '大模型技术与原理.md'),
                'section': '技术详解',
                'title': 'KV Cache与推理优化',
                'keywords': ['KV Cache', '推理', '缓存', '优化'],
                'max_chars': 500
            })
        elif '分布式' in name_lower:
            sources.append({
                'source': os.path.join(import_root, 'work', '精华', '分布式原理介绍.md'),
                'section': '技术详解',
                'title': '分布式系统基础原理',
                'keywords': ['分布式', '一致性', '协议', '系统'],
                'max_chars': 600
            })
        elif '训练' in name_lower:
            sources.append({
                'source': os.path.join(doubao_dir, '机器学习基础.md'),
                'section': '技术详解',
                'title': '模型训练基础原理',
                'keywords': ['训练', '学习', '梯度', '优化'],
                'max_chars': 500
            })
        elif '推理' in name_lower:
            sources.append({
                'source': os.path.join(qianwen_dir, '大模型技术与原理.md'),
                'section': '技术详解',
                'title': '大模型推理技术',
                'keywords': ['推理', 'inference', '加速', '优化'],
                'max_chars': 500
            })
        elif '架构' in name_lower:
            sources.append({
                'source': os.path.join(qianwen_dir, '大模型技术与原理.md'),
                'section': '技术详解',
                'title': '大模型架构设计思想',
                'keywords': ['架构', '设计', '模型', 'Transformer'],
                'max_chars': 500
            })
        elif 'nlp' in name_lower:
            sources.append({
                'source': os.path.join(doubao_dir, '机器学习基础.md'),
                'section': '技术详解',
                'title': '自然语言处理基础',
                'keywords': ['NLP', '自然语言', '文本', '语言'],
                'max_chars': 500
            })
        else:
            sources.append({
                'source': os.path.join(qianwen_dir, '大模型技术与原理.md'),
                'section': '技术详解',
                'title': 'AI大模型技术基础',
                'keywords': ['AI', '模型', '技术', '大模型'],
                'max_chars': 500
            })
        
        integration_map.append({
            'target': fpath,
            'sources': sources
        })
    
    # ========== newwiki/大模型技术与原理.md ==========
    newwiki_llm = os.path.join(newwiki_dir, '大模型技术与原理.md')
    if os.path.exists(newwiki_llm):
        integration_map.append({
            'target': newwiki_llm,
            'sources': [
                {
                    'source': os.path.join(doubao_dir, '机器学习基础.md'),
                    'section': '## 核心概念',
                    'title': '机器学习基础理论补充',
                    'keywords': ['机器学习', '监督学习', '无监督学习', '算法'],
                    'max_chars': 800
                },
                {
                    'source': os.path.join(doubao_dir, '深入研究.md'),
                    'section': '## 核心概念',
                    'title': 'AI前沿研究深度解析',
                    'keywords': ['研究', '前沿', '模型', '技术'],
                    'max_chars': 700
                },
                {
                    'source': os.path.join(doubao_dir, '注意力机制通俗解析.md'),
                    'section': '## 核心概念',
                    'title': '注意力机制通俗讲解',
                    'keywords': ['注意力', 'Transformer', '机制', '原理'],
                    'max_chars': 600
                },
            ]
        })
    
    # ========== newwiki/AI-Agent技术架构.md ==========
    newwiki_agent = os.path.join(newwiki_dir, 'AI-Agent技术架构.md')
    if os.path.exists(newwiki_agent):
        integration_map.append({
            'target': newwiki_agent,
            'sources': [
                {
                    'source': os.path.join(qianwen_dir, 'AI-Agent技术架构.md'),
                    'section': '概述',
                    'title': 'AI Agent技术体系补充',
                    'keywords': ['Agent', '智能体', '架构', '系统'],
                    'max_chars': 800
                },
                {
                    'source': os.path.join(doubao_dir, '深入研究 (2).md'),
                    'section': '概述',
                    'title': 'Agent前沿研究动态',
                    'keywords': ['Agent', '智能体', '研究', '进展'],
                    'max_chars': 600
                },
            ]
        })
    
    # 执行批量整合
    integrator.batch_integrate(integration_map)
    
    # 打印统计
    integrator.print_stats()
    
    print("\n第一批（续）AI 技术类整合完成！")


if __name__ == '__main__':
    main()
