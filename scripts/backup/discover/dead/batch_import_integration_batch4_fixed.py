#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
import 素材大规模深度嵌入 - 第三批（修正版） 分布式与数据库类
只处理真正相关的文件
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
    print("第三批（修正版）：分布式与数据库类内容整合")
    print("="*60)
    
    general_dir = os.path.join(discover_root, 'newwiki2', 'general')
    data_eng = os.path.join(discover_root, 'newwiki2', '数据工程')
    data_eng2 = os.path.join(discover_root, 'newwiki2', 'data-analysis')
    newwiki_dir = os.path.join(discover_root, 'newwiki')
    
    work_jinghua = os.path.join(import_root, 'work', '精华')
    cnblogs_dir = os.path.join(import_root, 'cnblogs')
    qianwen_dir = os.path.join(import_root, '千问')
    
    integration_map = []
    
    # ========== general/ 分布式相关文件（精准筛选） ==========
    dist_files = [
        'cap.md',
        'mapreduce.md', 
        '分布式事务实.md',
        '分布式存储数.md',
        '分布式架构挑.md',
        '分布式系统计.md',
        '分布式计算效.md',
        '消息队列保障.md',
        '数据中心技术.md',
        '数据中心逻辑.md',
        '开源组件评估.md',
    ]
    
    for fname in dist_files:
        fpath = os.path.join(general_dir, fname)
        if not os.path.exists(fpath):
            print(f"  跳过不存在的文件: {fname}")
            continue
        
        sources = [
            {
                'source': os.path.join(work_jinghua, '分布式原理介绍.md'),
                'section': '技术详解',
                'title': '分布式系统核心原理',
                'keywords': ['分布式', 'CAP', '一致性', '协议', '系统'],
                'max_chars': 700
            },
        ]
        
        integration_map.append({
            'target': fpath,
            'sources': sources
        })
    
    # ========== 数据工程/ 目录 ==========
    if os.path.exists(data_eng):
        data_files = [f for f in os.listdir(data_eng) if f.endswith('.md') and f != 'index.md']
        
        for fname in data_files:
            fpath = os.path.join(data_eng, fname)
            sources = [
                {
                    'source': os.path.join(qianwen_dir, '数据与存储技术.md'),
                    'section': '技术详解',
                    'title': '数据存储与管理技术',
                    'keywords': ['数据', '存储', '管理', '架构'],
                    'max_chars': 500
                },
            ]
            
            integration_map.append({
                'target': fpath,
                'sources': sources
            })
    
    # ========== data-analysis/ 目录 ==========
    if os.path.exists(data_eng2):
        data2_files = [f for f in os.listdir(data_eng2) if f.endswith('.md') and f != 'index.md']
        
        for fname in data2_files:
            fpath = os.path.join(data_eng2, fname)
            sources = [
                {
                    'source': os.path.join(qianwen_dir, '数据与存储技术.md'),
                    'section': '技术详解',
                    'title': '数据技术基础',
                    'keywords': ['数据', '技术', '分析', '存储'],
                    'max_chars': 400
                },
            ]
            
            integration_map.append({
                'target': fpath,
                'sources': sources
            })
    
    # ========== newwiki/数据与存储技术.md ==========
    newwiki_data = os.path.join(newwiki_dir, '数据与存储技术.md')
    if os.path.exists(newwiki_data):
        integration_map.append({
            'target': newwiki_data,
            'sources': [
                {
                    'source': os.path.join(work_jinghua, 'RAID.md'),
                    'section': '## 核心概念',
                    'title': 'RAID存储技术详解',
                    'keywords': ['RAID', '存储', '磁盘阵列', '技术'],
                    'max_chars': 700
                },
                {
                    'source': os.path.join(work_jinghua, '分布式原理介绍.md'),
                    'section': '## 核心概念',
                    'title': '分布式存储原理',
                    'keywords': ['分布式', '存储', '数据', '系统'],
                    'max_chars': 600
                },
            ]
        })
    
    # ========== newwiki/操作系统与底层技术.md ==========
    newwiki_os = os.path.join(newwiki_dir, '操作系统与底层技术.md')
    if os.path.exists(newwiki_os):
        integration_map.append({
            'target': newwiki_os,
            'sources': [
                {
                    'source': os.path.join(work_jinghua, '操作系统原理.md'),
                    'section': '## 核心概念',
                    'title': '操作系统核心原理',
                    'keywords': ['操作系统', '进程', '内存', '文件系统'],
                    'max_chars': 800
                },
            ]
        })
    
    # 执行批量整合
    integrator.batch_integrate(integration_map)
    
    # 打印统计
    integrator.print_stats()
    
    print("\n第三批（修正版） 分布式与数据库类整合完成！")


if __name__ == '__main__':
    main()
