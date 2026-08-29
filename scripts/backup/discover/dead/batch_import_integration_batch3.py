#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
import 素材大规模深度嵌入 - 第二批 硬件与系统类
处理 server-hardware/ + linux-system/ + 系统底层/ + newwiki/服务器与硬件架构.md
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
    print("第二批：硬件与系统类内容整合")
    print("="*60)
    
    server_hw = os.path.join(discover_root, 'newwiki2', 'server-hardware')
    linux_sys = os.path.join(discover_root, 'newwiki2', 'linux-system')
    sys_bottom = os.path.join(discover_root, 'newwiki2', '系统底层')
    server_hw2 = os.path.join(discover_root, 'newwiki2', '服务器硬件')
    newwiki_dir = os.path.join(discover_root, 'newwiki')
    
    work_jinghua = os.path.join(import_root, 'work', '精华')
    work_ras = os.path.join(import_root, 'work', 'ras')
    work_os = os.path.join(import_root, 'work', 'OS')
    doubao_dir = os.path.join(import_root, 'doubao')
    qianwen_dir = os.path.join(import_root, '千问')
    cnblogs_dir = os.path.join(import_root, 'cnblogs')
    
    integration_map = []
    
    # ========== server-hardware 目录 ==========
    if os.path.exists(server_hw):
        hw_files = [f for f in os.listdir(server_hw) if f.endswith('.md') and f != 'index.md']
        
        for fname in hw_files:
            fpath = os.path.join(server_hw, fname)
            sources = []
            name_lower = fname.lower()
            
            if 'cpu' in name_lower:
                sources.extend([
                    {
                        'source': os.path.join(work_jinghua, '操作系统原理.md'),
                        'section': '技术详解',
                        'title': 'CPU与操作系统交互原理',
                        'keywords': ['CPU', '进程', '调度', '操作系统'],
                        'max_chars': 500
                    },
                    {
                        'source': os.path.join(qianwen_dir, '服务器与硬件架构.md'),
                        'section': '技术详解',
                        'title': '服务器CPU架构演进',
                        'keywords': ['CPU', '处理器', '架构', '服务器'],
                        'max_chars': 600
                    },
                ])
            elif 'memory' in name_lower or '内存' in fname:
                sources.extend([
                    {
                        'source': os.path.join(work_ras, 'dramop.md'),
                        'section': '技术详解',
                        'title': 'DRAM内存操作与优化',
                        'keywords': ['DRAM', '内存', '存储', 'RAM'],
                        'max_chars': 600
                    },
                    {
                        'source': os.path.join(work_jinghua, '操作系统原理.md'),
                        'section': '技术详解',
                        'title': '内存管理与虚拟内存',
                        'keywords': ['内存', '虚拟内存', '分页', '管理'],
                        'max_chars': 500
                    },
                ])
            elif 'storage' in name_lower or '存储' in fname or 'raid' in name_lower:
                sources.extend([
                    {
                        'source': os.path.join(work_jinghua, 'RAID.md'),
                        'section': '技术详解',
                        'title': 'RAID存储技术详解',
                        'keywords': ['RAID', '磁盘阵列', '存储', '冗余'],
                        'max_chars': 700
                    },
                    {
                        'source': os.path.join(qianwen_dir, '数据与存储技术.md'),
                        'section': '技术详解',
                        'title': '存储系统架构',
                        'keywords': ['存储', '数据', '架构', '系统'],
                        'max_chars': 500
                    },
                ])
            elif 'bmc' in name_lower or 'bios' in name_lower:
                sources.extend([
                    {
                        'source': os.path.join(doubao_dir, '服务器固件框架.md'),
                        'section': '技术详解',
                        'title': '服务器固件技术框架',
                        'keywords': ['固件', 'BMC', 'BIOS', '服务器'],
                        'max_chars': 600
                    },
                    {
                        'source': os.path.join(qianwen_dir, '服务器与硬件架构.md'),
                        'section': '技术详解',
                        'title': '服务器管理固件',
                        'keywords': ['BMC', 'BIOS', '固件', '管理'],
                        'max_chars': 500
                    },
                ])
            elif 'pcie' in name_lower or 'pci' in name_lower:
                sources.extend([
                    {
                        'source': os.path.join(qianwen_dir, '服务器与硬件架构.md'),
                        'section': '技术详解',
                        'title': 'PCIe总线与高速互联',
                        'keywords': ['PCIe', '总线', '互联', '高速'],
                        'max_chars': 500
                    },
                ])
            elif 'gpu' in name_lower or 'nvidia' in name_lower or 'amd' in name_lower:
                sources.extend([
                    {
                        'source': os.path.join(qianwen_dir, '服务器与硬件架构.md'),
                        'section': '技术详解',
                        'title': 'GPU加速与异构计算',
                        'keywords': ['GPU', '加速', '异构计算', 'AI'],
                        'max_chars': 500
                    },
                ])
            elif 'ras' in name_lower or '可靠性' in fname:
                sources.extend([
                    {
                        'source': os.path.join(work_ras, 'RAS.md'),
                        'section': '技术详解',
                        'title': 'RAS可靠性技术',
                        'keywords': ['RAS', '可靠性', '可用性', '可维护性'],
                        'max_chars': 600
                    },
                ])
            else:
                sources.extend([
                    {
                        'source': os.path.join(qianwen_dir, '服务器与硬件架构.md'),
                        'section': '技术详解',
                        'title': '服务器硬件技术基础',
                        'keywords': ['服务器', '硬件', '架构', '技术'],
                        'max_chars': 500
                    },
                ])
            
            integration_map.append({
                'target': fpath,
                'sources': sources
            })
    
    # ========== linux-system 目录 ==========
    if os.path.exists(linux_sys):
        linux_files = [f for f in os.listdir(linux_sys) if f.endswith('.md') and f != 'index.md']
        
        for fname in linux_files:
            fpath = os.path.join(linux_sys, fname)
            sources = [
                {
                    'source': os.path.join(work_jinghua, '操作系统原理.md'),
                    'section': '技术详解',
                    'title': '操作系统核心原理',
                    'keywords': ['操作系统', '进程', '内存', '文件系统'],
                    'max_chars': 700
                },
                {
                    'source': os.path.join(qianwen_dir, '服务器与硬件架构.md'),
                    'section': '技术详解',
                    'title': 'Linux服务器系统运维',
                    'keywords': ['Linux', '服务器', '运维', '系统'],
                    'max_chars': 500
                },
            ]
            
            integration_map.append({
                'target': fpath,
                'sources': sources
            })
    
    # ========== 系统底层 目录 ==========
    if os.path.exists(sys_bottom):
        sys_files = [f for f in os.listdir(sys_bottom) if f.endswith('.md') and f != 'index.md']
        
        for fname in sys_files:
            fpath = os.path.join(sys_bottom, fname)
            sources = []
            name_lower = fname.lower()
            
            if 'kernel' in name_lower:
                sources.extend([
                    {
                        'source': os.path.join(work_jinghua, '操作系统原理.md'),
                        'section': '技术详解',
                        'title': '操作系统内核原理',
                        'keywords': ['内核', '系统调用', '进程管理', '内核'],
                        'max_chars': 600
                    },
                ])
            elif 'memory' in name_lower:
                sources.extend([
                    {
                        'source': os.path.join(work_ras, 'dramop.md'),
                        'section': '技术详解',
                        'title': '内存底层工作原理',
                        'keywords': ['内存', 'DRAM', '存储', '底层'],
                        'max_chars': 500
                    },
                ])
            else:
                sources.extend([
                    {
                        'source': os.path.join(work_jinghua, '操作系统原理.md'),
                        'section': '技术详解',
                        'title': '系统底层技术原理',
                        'keywords': ['系统', '底层', '硬件', '软件'],
                        'max_chars': 500
                    },
                ])
            
            integration_map.append({
                'target': fpath,
                'sources': sources
            })
    
    # ========== 服务器硬件 目录 ==========
    if os.path.exists(server_hw2):
        hw2_files = [f for f in os.listdir(server_hw2) if f.endswith('.md') and f != 'index.md']
        
        for fname in hw2_files:
            fpath = os.path.join(server_hw2, fname)
            sources = [
                {
                    'source': os.path.join(qianwen_dir, '服务器与硬件架构.md'),
                    'section': '技术详解',
                    'title': '服务器硬件架构',
                    'keywords': ['服务器', '硬件', '架构', '技术'],
                    'max_chars': 600
                },
            ]
            
            integration_map.append({
                'target': fpath,
                'sources': sources
            })
    
    # ========== newwiki/服务器与硬件架构.md ==========
    newwiki_server = os.path.join(newwiki_dir, '服务器与硬件架构.md')
    if os.path.exists(newwiki_server):
        integration_map.append({
            'target': newwiki_server,
            'sources': [
                {
                    'source': os.path.join(work_jinghua, '操作系统原理.md'),
                    'section': '## 核心概念',
                    'title': '操作系统原理深度补充',
                    'keywords': ['操作系统', '原理', '进程', '内存'],
                    'max_chars': 800
                },
                {
                    'source': os.path.join(work_jinghua, 'RAID.md'),
                    'section': '## 核心概念',
                    'title': 'RAID存储技术详解',
                    'keywords': ['RAID', '存储', '磁盘', '冗余'],
                    'max_chars': 700
                },
                {
                    'source': os.path.join(work_ras, 'RAS.md'),
                    'section': '## 核心概念',
                    'title': 'RAS可靠性技术',
                    'keywords': ['RAS', '可靠性', '可用性', '服务器'],
                    'max_chars': 600
                },
                {
                    'source': os.path.join(doubao_dir, '服务器固件框架.md'),
                    'section': '## 核心概念',
                    'title': '服务器固件技术框架',
                    'keywords': ['固件', 'BMC', 'BIOS', '服务器'],
                    'max_chars': 700
                },
            ]
        })
    
    # 执行批量整合
    integrator.batch_integrate(integration_map)
    
    # 打印统计
    integrator.print_stats()
    
    print("\n第二批 硬件与系统类整合完成！")


if __name__ == '__main__':
    main()
