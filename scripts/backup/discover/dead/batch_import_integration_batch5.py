#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
import 素材大规模深度嵌入 - 第四批 管理与方法论类
处理 project-mgmt/ + newwiki/企业管理与运营.md + 方法论与工具.md
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
    print("第四批：管理与方法论类内容整合")
    print("="*60)
    
    proj_mgmt = os.path.join(discover_root, 'newwiki2', 'project-mgmt')
    newwiki_dir = os.path.join(discover_root, 'newwiki')
    general_dir = os.path.join(discover_root, 'newwiki2', 'general')
    
    qianwen_dir = os.path.join(import_root, '千问')
    doubao_dir = os.path.join(import_root, 'doubao')
    
    integration_map = []
    
    # ========== project-mgmt/ 目录 ==========
    if os.path.exists(proj_mgmt):
        mgmt_files = [f for f in os.listdir(proj_mgmt) if f.endswith('.md') and f != 'index.md']
        
        for fname in mgmt_files:
            fpath = os.path.join(proj_mgmt, fname)
            sources = [
                {
                    'source': os.path.join(qianwen_dir, '企业管理与运营.md'),
                    'section': '技术详解',
                    'title': '企业管理与运营实践',
                    'keywords': ['管理', '运营', '项目', '团队'],
                    'max_chars': 500
                },
                {
                    'source': os.path.join(qianwen_dir, '方法论与工具.md'),
                    'section': '技术详解',
                    'title': '方法论与工具集',
                    'keywords': ['方法论', '工具', '方法', '框架'],
                    'max_chars': 500
                },
            ]
            
            integration_map.append({
                'target': fpath,
                'sources': sources
            })
    
    # ========== newwiki/企业管理与运营.md ==========
    newwiki_mgmt = os.path.join(newwiki_dir, '企业管理与运营.md')
    if os.path.exists(newwiki_mgmt):
        integration_map.append({
            'target': newwiki_mgmt,
            'sources': [
                {
                    'source': os.path.join(doubao_dir, '企业业务分析.md'),
                    'section': '概述',
                    'title': '企业业务分析深度补充',
                    'keywords': ['企业', '业务', '分析', '管理'],
                    'max_chars': 800
                },
                {
                    'source': os.path.join(qianwen_dir, '企业管理与运营.md'),
                    'section': '概述',
                    'title': '企业管理与运营方法论',
                    'keywords': ['管理', '运营', '企业', '方法'],
                    'max_chars': 700
                },
            ]
        })
    
    # ========== newwiki/方法论与工具.md ==========
    newwiki_method = os.path.join(newwiki_dir, '方法论与工具.md')
    if os.path.exists(newwiki_method):
        integration_map.append({
            'target': newwiki_method,
            'sources': [
                {
                    'source': os.path.join(qianwen_dir, '方法论与工具.md'),
                    'section': '概述',
                    'title': '方法论体系与工具体系',
                    'keywords': ['方法论', '工具', '框架', '方法'],
                    'max_chars': 800
                },
                {
                    'source': os.path.join(qianwen_dir, 'AI技能与职业发展.md'),
                    'section': '概述',
                    'title': 'AI时代的技能与职业发展',
                    'keywords': ['AI', '技能', '职业', '发展'],
                    'max_chars': 600
                },
            ]
        })
    
    # ========== newwiki/项目管理与协作.md ==========
    newwiki_proj = os.path.join(newwiki_dir, '项目管理与协作.md')
    if os.path.exists(newwiki_proj):
        integration_map.append({
            'target': newwiki_proj,
            'sources': [
                {
                    'source': os.path.join(qianwen_dir, '企业管理与运营.md'),
                    'section': '概述',
                    'title': '项目管理与团队协作',
                    'keywords': ['项目管理', '协作', '团队', '管理'],
                    'max_chars': 700
                },
            ]
        })
    
    # ========== newwiki/行业趋势与洞察.md ==========
    newwiki_trend = os.path.join(newwiki_dir, '行业趋势与洞察.md')
    if os.path.exists(newwiki_trend):
        integration_map.append({
            'target': newwiki_trend,
            'sources': [
                {
                    'source': os.path.join(qianwen_dir, '行业趋势与洞察.md'),
                    'section': '概述',
                    'title': '行业趋势深度洞察',
                    'keywords': ['趋势', '行业', '洞察', '发展'],
                    'max_chars': 700
                },
            ]
        })
    
    # ========== general/ 中管理方法论相关文件 ==========
    mgmt_general_files = [
        '企业经营以客.md',
        '系统论在企业.md',
        '飞轮效应平台.md',
        '工作流定义与.md',
        '高质量信息输.md',
        '独立观点构建.md',
        '深度分析抓本.md',
        '软件与团队组.md',
        '研发行业低毛.md',
        '支撑岗增多反.md',
    ]
    
    for fname in mgmt_general_files:
        fpath = os.path.join(general_dir, fname)
        if not os.path.exists(fpath):
            continue
        
        sources = [
            {
                'source': os.path.join(qianwen_dir, '企业管理与运营.md'),
                'section': '技术详解',
                'title': '企业管理与运营视角',
                'keywords': ['管理', '运营', '企业', '方法'],
                'max_chars': 400
            },
        ]
        
        integration_map.append({
            'target': fpath,
            'sources': sources
        })
    
    # 执行批量整合
    integrator.batch_integrate(integration_map)
    
    # 打印统计
    integrator.print_stats()
    
    print("\n第四批 管理与方法论类整合完成！")


if __name__ == '__main__':
    main()
