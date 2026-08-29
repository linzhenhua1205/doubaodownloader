#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
import 素材大规模深度嵌入 - 第三批 分布式与数据库类
处理 general/分布式系列 + 数据工程/ + newwiki/数据库与大数据技术.md
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
    print("第三批：分布式与数据库类内容整合")
    print("="*60)
    
    general_dir = os.path.join(discover_root, 'newwiki2', 'general')
    data_eng = os.path.join(discover_root, 'newwiki2', '数据工程')
    data_eng2 = os.path.join(discover_root, 'newwiki2', 'data-analysis')
    newwiki_dir = os.path.join(discover_root, 'newwiki')
    
    work_jinghua = os.path.join(import_root, 'work', '精华')
    cnblogs_dir = os.path.join(import_root, 'cnblogs')
    qianwen_dir = os.path.join(import_root, '千问')
    
    integration_map = []
    
    # ========== general/ 分布式系列卡片 ==========
    if os.path.exists(general_dir):
        general_files = [f for f in os.listdir(general_dir) if f.endswith('.md') and f != 'index.md']
        
        for fname in general_files:
            fpath = os.path.join(general_dir, fname)
            sources = []
            name_lower = fname.lower()
            
            if 'distribut' in name_lower or '分布式' in fname or 'cap' in name_lower:
                sources.extend([
                    {
                        'source': os.path.join(work_jinghua, '分布式原理介绍.md'),
                        'section': '技术详解',
                        'title': '分布式系统核心原理',
                        'keywords': ['分布式', 'CAP', '一致性', '协议'],
                        'max_chars': 800
                    },
                ])
            elif 'raft' in name_lower or 'paxos' in name_lower:
                sources.extend([
                    {
                        'source': os.path.join(work_jinghua, '分布式原理介绍.md'),
                        'section': '技术详解',
                        'title': '分布式一致性协议',
                        'keywords': ['Raft', 'Paxos', '一致性', '协议'],
                        'max_chars': 700
                    },
                ])
            elif 'database' in name_lower or 'sql' in name_lower or '数据库' in fname:
                sources.extend([
                    {
                        'source': os.path.join(qianwen_dir, '数据库与大数据技术.md'),
                        'section': '技术详解',
                        'title': '数据库技术原理',
                        'keywords': ['数据库', 'SQL', '事务', '索引'],
                        'max_chars': 600
                    },
                ])
            else:
                sources.extend([
                    {
                        'source': os.path.join(work_jinghua, '分布式原理介绍.md'),
                        'section': '技术详解',
                        'title': '分布式系统基础',
                        'keywords': ['分布式', '系统', '架构', '技术'],
                        'max_chars': 500
                    },
                ])
            
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
                    'source': os.path.join(qianwen_dir, '数据库与大数据技术.md'),
                    'section': '技术详解',
                    'title': '大数据与数据工程技术',
                    'keywords': ['大数据', '数据工程', '存储', '处理'],
                    'max_chars': 600
                },
                {
                    'source': os.path.join(qianwen_dir, '数据与存储技术.md'),
                    'section': '技术详解',
                    'title': '数据存储与管理',
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
                    'source': os.path.join(qianwen_dir, '数据库与大数据技术.md'),
                    'section': '技术详解',
                    'title': '数据分析与大数据',
                    'keywords': ['数据', '分析', '大数据', '技术'],
                    'max_chars': 500
                },
            ]
            
            integration_map.append({
                'target': fpath,
                'sources': sources
            })
    
    # ========== newwiki/数据库与大数据技术.md ==========
    newwiki_db = os.path.join(newwiki_dir, '数据库与大数据技术.md')
    if os.path.exists(newwiki_db):
        integration_map.append({
            'target': newwiki_db,
            'sources': [
                {
                    'source': os.path.join(work_jinghua, '分布式原理介绍.md'),
                    'section': '## 核心概念',
                    'title': '分布式数据库原理补充',
                    'keywords': ['分布式', '数据库', '一致性', 'CAP'],
                    'max_chars': 800
                },
                {
                    'source': os.path.join(work_jinghua, 'RAID.md'),
                    'section': '## 核心概念',
                    'title': '存储与RAID技术',
                    'keywords': ['RAID', '存储', '磁盘', '冗余'],
                    'max_chars': 600
                },
            ]
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
                    'source': os.path.join(qianwen_dir, '数据与存储技术.md'),
                    'section': '## 核心概念',
                    'title': '数据存储技术全景',
                    'keywords': ['数据', '存储', '技术', '架构'],
                    'max_chars': 800
                },
            ]
        })
    
    # 执行批量整合
    integrator.batch_integrate(integration_map)
    
    # 打印统计
    integrator.print_stats()
    
    print("\n第三批 分布式与数据库类整合完成！")


if __name__ == '__main__':
    main()
