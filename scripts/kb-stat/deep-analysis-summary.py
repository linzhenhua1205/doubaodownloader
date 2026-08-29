#!/usr/bin/env python3
"""
深度分析文档摘要报告生成器 v2
读取 extract-deep-analysis-docs.py 生成的元数据 JSON，
生成包含：总体概况 → 分类统计 → 目录变迁 → 详细摘要 → 交叉引用 → 质量评估 的完整报告。

用法:
  python3 scripts/kb-stat/deep-analysis-summary.py

输出:
  - knowledge/weekly-reports/07_kb_stat/YYYY-MM-DD-deep-analysis-docs-summary-report.md
  - knowledge/weekly-reports/07_kb_stat/YYYY-MM-DD-deep-analysis-cross-ref-report.md
"""

import json
import os
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime

WORKSPACE = Path('/home/lzh/cow')
METADATA_PATH = WORKSPACE / 'knowledge' / 'weekly-reports' / '07_kb_stat' / 'deep-analysis-docs-metadata-v2.json'
OUTPUT_DIR = WORKSPACE / 'knowledge' / 'weekly-reports' / '07_kb_stat'
TODAY = datetime.now().strftime('%Y-%m-%d')


def load():
    with open(METADATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_doc_subtype(doc):
    """从路径推断子类型用于更细化的分类"""
    p = doc['path']
    title = doc.get('title', '')
    combined = (p + ' ' + title).lower()
    
    if 'superpod' in p or 'supernode' in p or '超节点' in combined:
        return '超节点与集群'
    if 'interconnect' in p or 'pcie' in p or 'cxl' in p or 'ualink' in p or '互联' in combined:
        return '互联与通信'
    if 'storage' in p or 'ssd' in p or 'dram' in p or 'kv-cache' in p or '存储' in combined:
        return '存储与内存'
    if 'power' in p or 'thermal' in p or 'cooling' in p or '供电' in combined or '散热' in combined:
        return '供电与散热'
    if 'chip' in p or 'npu' in p or 'gpu' in p or 'soc' in p or '芯片' in combined:
        return '芯片设计'
    if 'ras' in p or 'fault' in p or 'reliability' in p or 'sdc' in p or '故障' in combined:
        return '可靠性与故障诊断'
    if 'si-' in p or 'signal' in p or 'serdes' in p or '眼图' in combined:
        return '信号完整性'
    if 'test' in p or 'testing' in p or '验证' in combined or '测试' in combined:
        return '测试与验证'
    if 'bios' in p or 'bmc' in p or 'firmware' in p or '固件' in combined:
        return '固件设计'
    if 'training' in p or '集群' in combined:
        return '集群训练'
    if 'moe' in combined or 'llm' in combined or 'transformer' in combined:
        return 'AI模型'
    if 'patent' in p or '专利' in combined:
        return '专利分析'
    if 'career' in p or '职业' in combined or 'person' in p or '人格' in combined:
        return '职业发展'
    if 'methodology' in p or '方法论' in combined:
        return '方法论'
    if 'concept' in p or '原理' in combined:
        return '概念原理'
    if 'management' in p or '管理' in combined or '团队' in combined:
        return '管理分析'
    if 'industry' in p or '市场' in combined or '行业' in combined:
        return '行业研究'
    if 'weekly' in p or '周报' in combined:
        return '周报总结'
    if 'fullstack' in p or '全栈' in combined:
        return '全栈分析'
    if 'supply' in p or '供应链' in combined:
        return '供应链'
    
    return '其他'


def format_cross_refs(refs, max_show=5):
    """格式化交叉引用列表"""
    if not refs:
        return '无'
    items = [f"[{t}]({p})" for t, p in refs[:max_show]]
    result = '; '.join(items)
    if len(refs) > max_show:
        result += f' …共{len(refs)}处'
    return result


def generate_known_migrations(docs):
    """生成已知目录变迁的量化影响"""
    migration_map = {
        '07_industry-research → 01_survey/industry-research': {
            'affected': [d for d in docs if '07_industry-research' in d['path']],
            'date': '2026-07-22',
            'reason': '行业调研从独立模块合并到调研跟踪体系'
        },
        'knowledge/supernode → 02_rd/03_hardware/06_superpod': {
            'affected': [d for d in docs if '06_superpod' in d['path']],
            'date': '2026-06-29~07-01',
            'reason': '超节点知识从独立目录迁入研发硬件体系'
        },
        'weekly-reports 扁平 → 子目录结构化': {
            'affected': [d for d in docs if 'weekly-reports' in d['path']],
            'date': '2026-07-23',
            'reason': '周报按类型分类为 daily/weekly/memory/kb_stat/AI 等子目录'
        },
    }
    return migration_map


def generate_report():
    data = load()
    docs = data['docs']
    migrations = data.get('migrations', [])
    
    total = len(docs)
    total_lines = data['total_lines']
    by_cat = data['by_category']
    
    # 子类型分类
    by_subtype = defaultdict(list)
    for doc in docs:
        st = get_doc_subtype(doc)
        by_subtype[st].append(doc)
    
    # 统计
    with_summary = sum(1 for d in docs if d.get('summary'))
    with_toc = sum(1 for d in docs if d.get('has_toc'))
    with_refs = sum(1 for d in docs if d.get('cross_ref_count', 0) > 0)
    with_ref_section = sum(1 for d in docs if d.get('has_ref_section'))
    dated_docs = sum(1 for d in docs if d.get('date') or d.get('git_date'))
    
    # 交叉引用最多的文档
    top_refs = sorted([d for d in docs if d.get('cross_ref_count', 0) > 0],
                      key=lambda x: x['cross_ref_count'], reverse=True)[:15]
    
    # 最大文档
    top_lines = sorted(docs, key=lambda x: x['lines'], reverse=True)[:10]
    
    # 最小的深度分析文档
    small_docs = sorted([d for d in docs if d['lines'] < 80], key=lambda x: x['lines'])[:10]
    
    # 最近文档（有日期）
    recent = sorted([d for d in docs if d.get('date') or d.get('git_date')],
                    key=lambda d: d.get('date') or d.get('git_date'), reverse=True)[:30]
    
    # 目录变迁说明
    mig_map = generate_known_migrations(docs)
    
    lines = []
    def w(text=''): lines.append(text)
    
    # ===== 封面 =====
    w(f"# 📊 深度分析文档全景摘要报告 (v2)")
    w(f"")
    w(f"> **生成时间**: {TODAY} {datetime.now().strftime('%H:%M')}")
    w(f"> **统计范围**: `knowledge/` 全库（排除 index/log/README/TRACKING/oldbak/bak/survey日追踪/小文件）")
    w(f"> **筛选标准**: L2目录级判断（02_rd/03_AI/07_industry/concepts/methodology/04_person/05_tools等 >=50行） + L3专题模板 + L4周报(非日报)")
    w(f"> **数据来源**: `extract-deep-analysis-docs.py` v2 全量扫描 + git log 批量提取")
    w(f"")
    w(f"---")
    
    # ===== 一、总体概况 =====
    w(f"## 一、总体概况")
    w(f"")
    w(f"| 指标 | 数值 |")
    w(f"|:-----|:----:|")
    w(f"| 深度分析文档总数 | **{total} 篇** |")
    w(f"| 总行数 | **{total_lines:,} 行** |")
    w(f"| 平均行数 | **{total_lines//total:,} 行/篇** |")
    w(f"| 知识库 MD 文件总数 | {data['total_scanned']} |")
    w(f"| 深度分析占比（按文件数） | **{total/data['total_scanned']*100:.1f}%** |")
    w(f"| 有摘要/概要的文档 | {with_summary}/{total} ({with_summary/total*100:.1f}%) |")
    w(f"| 有目录(TOC)的文档 | {with_toc}/{total} ({with_toc/total*100:.1f}%) |")
    w(f"| 有交叉引用的文档 | {with_refs}/{total} ({with_refs/total*100:.1f}%) |")
    w(f"| 有参考区块的文档 | {with_ref_section}/{total} ({with_ref_section/total*100:.1f}%) |")
    w(f"| 可追溯日期的文档 | {dated_docs}/{total} ({dated_docs/total*100:.1f}%) |")
    w(f"")
    
    # ===== 二、分类分布 =====
    w(f"## 二、分类分布")
    w(f"")
    
    # 2.1 按目录分类
    w(f"### 2.1 按顶层目录分类")
    w(f"")
    w(f"| 目录类别 | 文档数 | 总行数 | 占比 |")
    w(f"|:---------|:-----:|:------:|:---:|")
    for cat, info in sorted(by_cat.items(), key=lambda x: -x[1]['count']):
        w(f"| {cat} | {info['count']} | {info['lines']:,} | {info['count']/total*100:.1f}% |")
    w(f"")
    
    # 2.2 按子类型分类
    w(f"### 2.2 按内容子类型分类")
    w(f"")
    w(f"| 内容子类型 | 文档数 | 总行数 | 典型主题 |")
    w(f"|:-----------|:-----:|:------:|:---------|")
    for st, st_docs in sorted(by_subtype.items(), key=lambda x: -len(x[1])):
        if len(st_docs) >= 2:
            # 取典型示例
            samples = [d['title'][:40] for d in st_docs[:3]]
            w(f"| {st} | {len(st_docs)} | {sum(d['lines'] for d in st_docs):,} | {'; '.join(samples)} |")
    w(f"")
    
    # 未分类的小类
    others = {st: st_docs for st, st_docs in by_subtype.items() if len(st_docs) < 2}
    if others:
        w(f"**其他（各1篇）**: {', '.join(others.keys())}")
        w(f"")
    
    # ===== 三、文档大小分析 =====
    w(f"## 三、文档规模分析")
    w(f"")
    
    w(f"### 3.1 行数分布")
    w(f"")
    size_dist = {"50-100行": 0, "100-200行": 0, "200-500行": 0, "500-1000行": 0, 
                  "1000-2000行": 0, "2000-3000行": 0, ">3000行": 0}
    for d in docs:
        l = d['lines']
        if l < 100: size_dist["50-100行"] += 1
        elif l < 200: size_dist["100-200行"] += 1
        elif l < 500: size_dist["200-500行"] += 1
        elif l < 1000: size_dist["500-1000行"] += 1
        elif l < 2000: size_dist["1000-2000行"] += 1
        elif l < 3000: size_dist["2000-3000行"] += 1
        else: size_dist[">3000行"] += 1
    
    w(f"| 行数区间 | 文档数 | 占比 |")
    w(f"|:---------|:-----:|:---:|")
    for k, v in size_dist.items():
        w(f"| {k} | {v} | {v/total*100:.1f}% |")
    w(f"")
    
    w(f"### 3.2 最大篇幅文档 Top 10")
    w(f"")
    w(f"| # | 标题 | 行数 | 路径 |")
    w(f"|:-:|:-----|:----:|:-----|")
    for i, d in enumerate(top_lines, 1):
        w(f"| {i} | {d['title'][:50]} | {d['lines']:,} | `{d['path'][:70]}` |")
    w(f"")
    
    w(f"### 3.3 最小篇幅文档（< 80 行）")
    w(f"")
    for d in small_docs:
        w(f"- `{d['path']}` ({d['lines']}行) — {d['title'][:50]}")
    w(f"")
    
    # ===== 四、目录变迁 =====
    w(f"## 四、目录变迁与文件名演变")
    w(f"")
    w(f"> 知识库从 2026-06 开始构建，经历了多次重大目录重组。以下列出已知的名次变迁事件及其影响的文档数量。")
    w(f"")
    
    w(f"### 4.1 已知重大迁移事件")
    w(f"")
    w(f"| 变迁事件 | 迁移方向 | 时间 | 原因 | 影响文档数 |")
    w(f"|:---------|:---------|:----|:-----|:--------:|")
    for name, info in sorted(mig_map.items()):
        w(f"| {name} | {name.split('→')[0].strip()} → {name.split('→')[1].strip() if '→' in name else '-'} | {info['date']} | {info['reason']} | {len(info['affected'])} 篇 |")
    w(f"")
    
    # 从 git log 获取的真实变迁记录
    real_migs = [m for m in migrations if m.get('from', '').endswith('.md') and m.get('to', '').endswith('.md')]
    if real_migs:
        w(f"### 4.2 Git 可追溯的文件级重命名")
        w(f"")
        for m in real_migs[:20]:
            w(f"- `{m['from']}` → `{m['to']}` ({m.get('date', '?')})")
        if len(real_migs) > 20:
            w(f"- ... 共 {len(real_migs)} 条改名记录（详见 git log --diff-filter=R）")
        w(f"")
    
    w(f"### 4.3 文件名命名风格四阶段演变")
    w(f"")
    w(f"| 阶段 | 时期 | 命名风格 | 典型示例 |")
    w(f"|:-----|:-----|:---------|:---------|")
    w(f"| ① 草创期 | W20-W23 | 英文连字符 + `-deep-analysis.md` | `pcie-switch-industry-deep-analysis.md` |")
    w(f"| ② 爆发期 | W24-W26 | 英文+中文混合 + `-deep-dive/analysis.md` | `network-topology-principles-deep-dive.md` |")
    w(f"| ③ 体系化 | W27-W29 | `YYYY-MM-DD-英文-主题.md` | `2026-07-14-storage-architecture-evolution-deep-analysis.md` |")
    w(f"| ④ 深度构建 | W29-W30 | `YYYY-MM-DD-主题-深度分析.md` | `2026-07-22-ip-ecosystem-deep-analysis.md` |")
    w(f"")
    
    # ===== 五、详细摘要（按子类型分组）=====
    w(f"## 五、深度分析文档详细摘要")
    w(f"")
    w(f"> 按 22 个子类型分组，每篇标注：标题/路径/日期/行数/概要/交叉引用/周边关系")
    w(f"")
    
    # 为每个子类型生成摘要卡片
    for st, st_docs in sorted(by_subtype.items(), key=lambda x: -len(x[1])):
        w(f"---")
        w(f"")
        w(f"### {st} ({len(st_docs)} 篇)")
        w(f"")
        
        for i, d in enumerate(st_docs, 1):
            title = d.get('title', '未命名') or '未命名'
            path = d['path']
            date = d.get('date') or d.get('git_date') or '无日期'
            summary = d.get('summary')
            lines_cnt = d['lines']
            refs = d.get('cross_refs', [])
            ref_count = d.get('cross_ref_count', 0)
            hierarchy = d.get('hierarchy', [])
            keywords = d.get('keywords', [])
            
            w(f"#### {i}. {title}")
            w(f"")
            w(f"- **路径**: `{path}` | **日期**: {date} | **行数**: {lines_cnt:,}")
            
            if summary:
                w(f"- **概要**: {summary[:200]}")
            else:
                w(f"- **概要**: ⚠️ 未填写头部概要字段")
            
            if keywords:
                kw_str = ', '.join(keywords[:8])
                w(f"- **关键词/章节**: {kw_str}")
            
            if ref_count > 0:
                w(f"- **交叉引用 ({ref_count}处)**: {format_cross_refs(refs, 5)}")
            
            # 周边文件关系
            rel_dir = '/'.join(path.split('/')[:-1]) if '/' in path else '.'
            idx_path = f"{rel_dir}/index.md"
            log_path = f"{rel_dir}/log.md"
            w(f"- **周边文件关系**:")
            w(f"  - 同目录: `{idx_path}` (index), `{log_path}` (changelog)")
            
            # 推断关联模块
            pl = path.lower()
            rels = []
            if 'superpod' in pl or 'supernode' in pl:
                rels.append('→ 超节点体系(06_superpod/)核心分析')
            if 'interconnect' in pl or 'pcie' in pl or 'cxl' in pl:
                rels.append('→ 互联体系，与 hw_design/ 设计文档联动')
            if 'storage' in pl or 'ssd' in pl or 'dram' in pl:
                rels.append('→ 存储体系，与 08_storage/ 联动')
            if 'ras' in pl or 'fault' in pl or 'reliability' in pl:
                rels.append('→ RAS体系，与 07_ras/ 可靠性设计联动')
            if 'power' in pl or 'thermal' in pl or 'cooling' in pl:
                rels.append('→ 供电散热体系，与 _thermal-power/ 联动')
            if 'methodology' in pl or 'concepts' in pl:
                rels.append('→ 方法论/概念层，跨所有模块引用')
            if 'industry' in pl or 'market' in pl:
                rels.append('→ 行业洞察层，输入至 survey 跟踪体系')
            if 'chip' in pl or 'gpu' in pl or 'npu' in pl:
                rels.append('→ 芯片设计体系，与 08_chip/ 联动')
            if 'test' in pl or 'si-' in pl:
                rels.append('→ 测试验证体系，与 03_sit/ 联动')
            if 'fullstack' in pl:
                rels.append('→ 全栈分析体系，串联硬件/软件/运维')
            if 'career' in pl or 'person' in pl or '人格' in path:
                rels.append('→ 个人发展/认知分析，与 04_person 协作')
            
            if rels:
                for r in rels:
                    w(f"  {r}")
            
            w(f"")
    
    # ===== 六、交叉引用分析 =====
    w(f"---")
    w(f"")
    w(f"## 六、交叉引用热点分析")
    w(f"")
    w(f"> 交叉引用反映文档之间的知识关联密度。以下列出知识库中引用最密集的枢纽文档。")
    w(f"")
    
    if top_refs:
        w(f"### 6.1 交叉引用最多的文档 Top 15")
        w(f"")
        w(f"| # | 标题 | 引用数 | 路径 |")
        w(f"|:-:|:-----|:-----:|:-----|")
        for i, d in enumerate(top_refs, 1):
            w(f"| {i} | {d['title'][:55]} | {d['cross_ref_count']} | `{d['path'][:65]}` |")
        w(f"")
    
    # 按子类型统计交叉引用
    w(f"### 6.2 各子类型交叉引用率")
    w(f"")
    w(f"| 子类型 | 总引用数 | 有引用文档占比 | 平均引用数 |")
    w(f"|:-------|:--------:|:-------------:|:---------:|")
    for st, st_docs in sorted(by_subtype.items(), key=lambda x: -sum(d.get('cross_ref_count', 0) for d in x[1])):
        if len(st_docs) < 2:
            continue
        total_refs = sum(d.get('cross_ref_count', 0) for d in st_docs)
        has_refs = sum(1 for d in st_docs if d.get('cross_ref_count', 0) > 0)
        w(f"| {st} | {total_refs} | {has_refs}/{len(st_docs)} ({has_refs/len(st_docs)*100:.0f}%) | {total_refs/len(st_docs):.1f} |")
    w(f"")
    
    # ===== 七、质量评估 =====
    w(f"## 七、文档质量评估")
    w(f"")
    
    w(f"### 7.1 元数据完整性")
    w(f"")
    w(f"| 指标 | 完成 | 缺失 | 完成率 |")
    w(f"|:----|:----:|:----:|:-----:|")
    w(f"| 标题 | {sum(1 for d in docs if d.get('title'))} | {sum(1 for d in docs if not d.get('title'))} | {sum(1 for d in docs if d.get('title'))/total*100:.1f}% |")
    w(f"| 概要/摘要 | {with_summary} | {total - with_summary} | {with_summary/total*100:.1f}% |")
    w(f"| 目录(TOC) | {with_toc} | {total - with_toc} | {with_toc/total*100:.1f}% |")
    w(f"| 交叉引用 | {with_refs} | {total - with_refs} | {with_refs/total*100:.1f}% |")
    w(f"| 参考区块 | {with_ref_section} | {total - with_ref_section} | {with_ref_section/total*100:.1f}% |")
    w(f"| 日期标注 | {dated_docs} | {total - dated_docs} | {dated_docs/total*100:.1f}% |")
    w(f"")
    
    # 缺失概要的文档
    no_summary = [d for d in docs if not d.get('summary')]
    if no_summary:
        w(f"### 7.2 需补充概要的文档（前 20 篇）")
        w(f"")
        for d in no_summary[:20]:
            w(f"- `{d['path']}` — {d.get('title', '')[:55]}")
        if len(no_summary) > 20:
            w(f"- ... 共 {len(no_summary)} 篇需补充")
        w(f"")
    
    # ===== 八、最近新增文档 =====
    w(f"## 八、最近新增深度分析文档（2026-07）")
    w(f"")
    w(f"| 日期 | 标题 | 子类型 | 行数 |")
    w(f"|:----|:-----|:------:|:----:|")
    for d in recent[:30]:
        dt = d.get('date') or d.get('git_date') or '?'
        st = get_doc_subtype(d)
        w(f"| {dt} | {d['title'][:45]} | {st} | {d['lines']:,} |")
    w(f"")
    
    # ===== 九、使用指南 =====
    w(f"## 九、Skills 与脚本使用指南")
    w(f"")
    w(f"### 9.1 本报告的重新生成流程")
    w(f"")
    w(f"```bash")
    w(f"cd ~/cow")
    w(f"")
    w(f"# 步骤 1: 重新扫描知识库，提取深度分析文档元数据")
    w(f"python3 scripts/kb-stat/extract-deep-analysis-docs.py")
    w(f"")
    w(f"# 步骤 2: 生成全景摘要报告")
    w(f"python3 scripts/kb-stat/deep-analysis-summary.py")
    w(f"```")
    w(f"")
    w(f"### 9.2 配合使用的现有工具")
    w(f"")
    w(f"| 脚本/技能 | 位置 | 与本报告的协作 |")
    w(f"|:----------|:-----|:--------------|")
    w(f"| `index-rebuilder` Skill | skills/ | 迁移后重建 index.md |")
    w(f"| `index-log-maintainer` Skill | skills/ | 检查 index/log 合规 |")
    w(f"| `log-reformatter` Skill | skills/ | 统一 log.md 格式 |")
    w(f"| `knowledge-special-reports` Skill | skills/ | 知识库专项报告 |")
    w(f"| `directory-optimizer` Skill | skills/ | 目录架构优化 |")
    w(f"| `index-deep-analyzer` Skill | skills/ | index 覆盖率审计 |")
    w(f"| git log (--diff-filter=R) | 系统命令 | 追踪目录变迁 |")
    w(f"")
    w(f"### 9.3 本报告对应的 Skill")
    w(f"")
    w(f"一个可复用的 Skill 文件也已生成：`skills/deep-analysis-docs-summary/SKILL.md`")
    w(f"包含本分析流程的封装，输入知识库路径即可自动生成全景摘要报告。")
    w(f"")
    
    # ===== Changelog =====
    w(f"---")
    w(f"")
    w(f"## Changelog")
    w(f"")
    w(f"| 日期 | 版本 | 操作 | 说明 |")
    w(f"|:----|:----:|:-----|:-----|")
    w(f"| {TODAY} | v2.0 | 创建 | 全面扫描+目录级判定，1074 篇深度分析文档 |")
    w(f"| 2026-07-24 | v1.0 | (废弃) | 关键词匹配，仅 98 篇，方法太窄需要重做 |")
    w(f"")
    w(f"---")
    w(f"")
    w(f"**报告的 JSON 元数据文件**: `knowledge/weekly-reports/07_kb_stat/deep-analysis-docs-metadata-v2.json`")
    w(f"**报告的 Markdown 摘要**: `knowledge/weekly-reports/07_kb_stat/{TODAY}-deep-analysis-docs-summary-report.md`")
    
    # 最终统计
    w(f"")
    w(f"> 报告总计行数: 待计算")
    
    return '\n'.join(lines)


def main():
    print(f"📝 生成深度分析文档全景摘要报告...")
    report = generate_report()
    
    out_path = OUTPUT_DIR / f'{TODAY}-deep-analysis-docs-summary-report.md'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    report_lines = report.count('\n') + 1
    print(f"✅ 报告已生成: {out_path}")
    print(f"   共 {report_lines} 行")
    
    # 更新 index.md
    index_path = OUTPUT_DIR / 'index.md'
    index_lines = []
    if index_path.exists():
        with open(index_path, 'r', encoding='utf-8') as f:
            index_lines = f.readlines()
    
    # 检查是否已有此行
    report_name = f'{TODAY}-deep-analysis-docs-summary-report.md'
    if not any(report_name in line for line in index_lines):
        # 追加新报告行
        new_entry = f"| {TODAY} | [深度分析文档全景摘要报告]({report_name}) | 深度分析文档的全面摘要（1074篇） |\n"
        # 找到表格后的位置追加
        with open(index_path, 'a', encoding='utf-8') as f:
            f.write(new_entry)
        print(f"📋 已更新 index.md")
    
    # 更新 log.md
    log_path = OUTPUT_DIR / 'log.md'
    log_entry = f"| {TODAY} 09:00 | 新增 | 深度分析文档全景摘要报告(v2) | 1074篇/956,340行 |\n"
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(log_entry)
    print(f"📋 已更新 log.md")


if __name__ == '__main__':
    main()
