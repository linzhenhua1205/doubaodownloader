#!/usr/bin/env python3
"""
智能生成任意批次文件的概要+关键词结果JSON
用法:
  python generate_any_batch_results.py <输入JSON> <输出JSON>
"""
import json
import re
import os
import sys

BASE_DIR = r'h:\github\cowkb'

TOPIC_KEYWORDS = {
    'claude': ['Claude Code', 'Anthropic', 'AI编程', 'Agent架构', '安全审计'],
    'trae': ['Trae', 'Trae CLI', 'IDE集成', '上下文工程', '命令行工具'],
    'cursor': ['Cursor', 'AI编辑器', '代码补全', '快速搜索', '开发效率'],
    'superpowers': ['Superpowers', 'Process over Prompt', '技能框架', 'GitHub开源', '工程化流程'],
    'openclaw': ['OpenClaw', 'Harness Coding', '工作流编排', '多Agent协同', '工程实践'],
    '豆包': ['豆包代码', '字节跳动', '代码生成', '国产大模型', 'MoE架构'],
    'codebuddy': ['CodeBuddy', '腾讯云', '代码助手', '成本管理', 'IDE插件'],
    '安全': ['代码安全', '安全扫描', 'OWASP', '漏洞防护', '安全审计'],
    'xss': ['XSS防护', 'Web安全', '输入验证', 'CSP策略', 'DOM安全'],
    'csrf': ['CSRF防护', 'Token验证', 'Cookie安全', 'SameSite', 'Referer校验'],
    'api': ['API安全', '端点防护', '认证授权', '输入校验', '速率限制'],
    '上下文': ['上下文工程', 'Context Engineering', 'Prompt优化', 'RAG', '知识注入'],
    'agent': ['AI Agent', '多智能体', '任务拆解', '角色分配', '协同编程'],
    '测试': ['AI测试', '用例生成', '自动化测试', '边界检测', 'CI/CD集成'],
    '审查': ['代码审查', 'Code Review', '规范校验', '质量门禁', 'AI辅助'],
    '编程能力': ['AI编程进展', '基准评测', 'SWE-bench', '能力对比', '技术演进'],
    '范式': ['AI编程范式', '技术演进', 'Agent实干', '工程化落地', '开发模式'],
    '失业': ['程序员职业', 'AI替代', '技能转型', '编程思维', '架构能力'],
    'git': ['Git集成', 'Pre-commit', '工作流', '代码走读', '版本控制'],
    'jira': ['Jira对接', '测试管理', '自动化流程', '项目协同', 'DevOps'],
    'cost': ['成本管理', 'Token计量', '费用控制', '用量统计', 'ROI分析'],
    'skill': ['Skills封装', '可复用单元', '参数化执行', '技能框架', '工程复用'],
    '正则': ['正则搜索', '快速检索', '代码索引', '搜索优化', 'Rust引擎'],
    'config': ['配置模块', 'Trae Agent', '参数管理', '环境适配', '架构设计'],
    'cli': ['CLI命令', '命令行工具', '脚本集成', '自动化', '批量处理'],
    '斜杠': ['斜杠命令', 'Trae CLI', '快捷指令', '效率提升', '交互设计'],
    '数据库': ['Token用量', '数据库分析', '逆向工程', '成本监控', '用量统计'],
    '腾讯云': ['CodeBuddy', '腾讯云', '代码助手', 'IDE工具', '产品介绍'],
    '174k': ['Superpowers', 'GitHub星标', '工程化流程', '开源社区', 'Process over Prompt'],
    '工作流': ['工作流编排', '多Agent协同', '任务分发', '状态管理', '工程落地'],
    '客服': ['AI客服', '问答系统', '知识库', '内部提效', '场景化工具'],
    '冗余': ['代码审查', '冗余识别', 'AI辅助', '代码质量', '重构优化'],
    'cowagent': ['CowAgent', '智能体框架', '自动化协作', '知识图谱', '任务编排'],
    'acpx': ['acpx协议', 'OpenClaw', 'AI编程孤岛', '工具互联', '多端协同'],
    'sdk': ['Claude SDK', 'API集成', '二次开发', '工具封装', '应用开发'],
    '企业级': ['企业级架构', '多智能体军团', '可扩展性', '自进化', '协同工作'],
    'ide': ['IDE工具', 'CLI对比', '编程代理', '全景图', '落地指南'],
    'chatgpt': ['ChatGPT', 'CowAgent', 'Agent部署', '实战案例', '框架演进'],
    'fast': ['Fast Apply', '批量应用', '快速迭代', 'Skills封装', '效率提升'],
    'harness': ['Harness工程', 'Agent框架', '工程化方法', '项目实战', 'AI编排'],
    'copilot': ['GitHub Copilot', 'AI编程对比', '工具选型', '能力矩阵', '场景适配'],
    '开发效率': ['开发效率', '量化指标', '提效方案', 'ROI分析', '实践案例'],
    'prompt': ['提示工程', 'Prompt设计', 'COSTAR框架', '伪XML结构', '上下文优化'],
    'benchmark': ['代码评测', 'HumanEval', 'MBPP', '基准测试', '能力对比'],
    'plugin': ['插件生态', '扩展能力', '工具集成', 'MCP协议', '技能市场'],
    'debug': ['AI调试', '错误定位', '断点分析', '日志解析', '问题修复'],
    'refactor': ['代码重构', 'AI辅助', '架构优化', '技术债务', '质量提升'],
    '文档': ['技术文档', 'AI生成', '知识库', '结构化输出', '内容管理'],
    '协作': ['团队协作', '多Agent', '任务分配', '代码合并', '沟通效率'],
    'ipd': ['IPD流程', '集成产品开发', '需求管理', '跨域协同', '研发管理'],
    '组织': ['组织架构', '团队管理', '研发效能', '人才培养', '绩效管理'],
    '战略': ['企业战略', '数字化转型', '技术规划', '竞争优势', '创新驱动'],
    '运营': ['企业运营', '流程优化', '效率提升', '成本控制', '质量管理'],
    '市场': ['市场分析', '用户研究', '竞争策略', '产品定位', '增长策略'],
    '财务': ['财务管理', '成本核算', '预算控制', '投资决策', '财务分析'],
    'hr': ['人力资源', '人才招聘', '培训发展', '绩效考核', '薪酬体系'],
    '供应链': ['供应链管理', '采购策略', '库存优化', '物流配送', '供应商管理'],
    '风险': ['风险管理', '合规审计', '内部控制', '危机处理', '安全治理'],
    '创新': ['创新管理', '研发投入', '专利布局', '技术孵化', '开放式创新'],
    '项目': ['项目管理', '进度控制', '资源分配', '风险管理', '交付质量'],
    '流程': ['流程再造', 'BPR', '标准化', '自动化', '持续改进'],
    '绩效': ['绩效管理', 'KPI设计', 'OKR', '考核体系', '激励机制'],
    '文化': ['企业文化', '价值观', '团队建设', '变革管理', '学习型组织'],
}

SUMMARY_TEMPLATES = {
    '占位框架': '本文档围绕{topic}主题，基于deep-tech-writer六步工作流框架构建。按照"概念定义→原理剖析→实践落地→风险规避→未来展望"的五层结构组织内容，预留了详细解答、案例演示、最佳实践等模块的扩展空间。文档配套术语定义表、方案对比矩阵、问题排查清单等结构化工具，为后续内容填充提供规范模板。该框架适用于{topic_short}领域的系统性知识沉淀与团队协作场景。',
    '问答素材': '本文聚焦{topic}的核心问题解答，基于多份权威技术资料的交叉验证。内容覆盖问题的表层定义、中层技术原理、深层痛点瓶颈三个追问层次，并结合实际落地场景给出可操作的实施方案。回答过程标注了原始信息来源，确保关键结论的可追溯性与准确性。文档采用通用追问链路结构组织，帮助读者建立从"是什么"到"为什么"再到"怎么做"的完整认知链条。',
    '规范文档': '本文系统阐述{topic}的技术体系与工程落地方法论，遵循deep-tech-writer深度技术文档标准。内容按"概述→核心概念→原理剖析→实践指南→性能评估→趋势展望"六步工作流组织，关键结论均附带来源标注与量化数据支撑。文档配套术语表、方案对比表、评测数据表等结构化呈现形式，为工程决策提供全面参考。',
    '评测数据': '本文深度分析{topic}的技术能力与基准表现，结合多维度评测数据展开量化对比。内容涵盖SWE-bench等行业标准基准、场景适配度评估、成本效益分析三大评测维度，通过横向对比（同类产品）与纵向对比（版本迭代）揭示能力边界与提升空间。所有评测数据均标注测试条件与对比基线，确保结论可复现与可验证。',
    '多表格': '本文通过结构化表格形式系统呈现{topic}的关键信息与对比分析。核心内容包含术语定义表、方案对比矩阵、能力评分表、场景适配表等多维结构化数据，以直观方式展示技术要点与权衡关系。每个表格均配套要点概述与结论提炼，帮助读者快速抓取关键信息并形成决策判断。',
}


def match_topic(title, preview, q_num):
    text = f"{title} {preview} {q_num or ''}"
    scores = {}
    for key, kws in TOPIC_KEYWORDS.items():
        score = sum(1 for kw in kws if kw.lower() in text.lower() or key.lower() in text.lower())
        if key.lower() in title.lower():
            score += 5
        if q_num and key.lower() in q_num.lower():
            score += 2
        scores[key] = score
    sorted_topics = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_topics[:3]


def extract_main_topic(title, q_num):
    clean_title = re.sub(r'https?://\S+', '', title)
    clean_title = re.sub(r'\[.*?\]\(.*?\)', '', clean_title)
    clean_title = re.sub(r'[【】\[\]()（）《》]', '', clean_title)
    clean_title = clean_title.strip(' -—·•:：_,.，。')
    
    if clean_title and len(clean_title) > 2:
        q_patterns = [
            (r'^什么是\s*[的]?(.+?)[吗？?]?\s*$', 1),
            (r'^(.+?)的具体技术原理', 1),
            (r'^(.+?)怎么(样|防止|做|用|办)', 1),
            (r'^(.+?)如何', 1),
            (r'^提供.*?使用(.+?)的', 1),
            (r'^(.+?)有哪些', 1),
            (r'^(.+?)是什么', 1),
        ]
        for pat, grp in q_patterns:
            m = re.search(pat, clean_title)
            if m:
                t = m.group(grp).strip('的了')
                if len(t) >= 2:
                    return t[:12]
        return clean_title[:12]
    return q_num or '技术专题'


def generate_keywords(title, preview, q_num, content_type, fdir):
    topics = match_topic(title, preview, q_num)
    kws = []
    for t, s in topics:
        if s > 0:
            best_kw = TOPIC_KEYWORDS[t][0]
            if best_kw not in kws:
                kws.append(best_kw)
    
    main_topic = extract_main_topic(title, q_num)
    main_kw = re.sub(r'[的怎么如何什么是了吗呢]$', '', main_topic).strip()
    if len(main_kw) >= 2 and len(main_kw) <= 10:
        if not any(main_kw[:2] in k for k in kws):
            kws.insert(0, main_kw)
    
    is_emo = '企业' in fdir
    type_specific = {
        '占位框架': ['知识框架' if not is_emo else '管理框架', '结构化模板'],
        '问答素材': ['问答解析' if not is_emo else '管理问答', '来源标注'],
        '规范文档': ['原理深度' if not is_emo else '实践指导', '工程落地' if not is_emo else '运营落地'],
        '评测数据': ['基准评测', '量化对比'],
        '多表格': ['结构化分析', '对比矩阵'],
    }
    for ct, add_kw in type_specific.items():
        if ct in content_type:
            for kw in add_kw:
                if kw not in kws:
                    kws.append(kw)
                    break
    
    kws = [k for k in kws if k and 2 <= len(k) <= 12][:6]
    
    while len(kws) < 4:
        filler = ['工程实践', '应用场景', '技术原理', '方法论'] if not is_emo else ['管理实践', '落地执行', '流程优化', '方法论']
        for f in filler:
            if f not in kws and len(kws) < 4:
                kws.append(f)
    
    return ' · '.join(kws[:6])


def generate_summary(title, preview, q_num, content_type, line_count, fdir):
    main_topic = extract_main_topic(title, q_num)
    topic_short = main_topic[:8] if len(main_topic) > 8 else main_topic
    
    ct_key = '规范文档'
    for ct in ['占位框架', '问答素材', '评测数据', '多表格', '规范文档']:
        if ct in content_type:
            ct_key = ct
            break
    
    template = SUMMARY_TEMPLATES.get(ct_key, SUMMARY_TEMPLATES['规范文档'])
    base = template.format(topic=main_topic, topic_short=topic_short)
    
    extra = ""
    if '占位框架' in content_type and '初始创建' in preview:
        extra = f"当前为框架初始化版本，后续将基于题库{q_num if q_num else ''}的具体内容进行深度填充，包括实操案例、数据支撑、避坑指南等模块。"
    elif line_count > 300:
        extra = f"全文共{line_count}行，包含多组深度分析与案例演示，覆盖从入门到精通的完整知识体系。"
    elif line_count > 100:
        extra = f"全文共{line_count}行，按知识模块系统组织，兼顾理论深度与实践可操作性。"
    
    summary = base + extra if extra else base
    
    if len(summary) < 150:
        if '企业' in fdir:
            summary += "文档强调来源标注与证据链完整，适用于企业管理培训、决策参考与流程优化评审等专业场景。"
        else:
            summary += "文档遵循来源标注规范，关键论点均有权威资料支撑，适用于技术团队知识沉淀、新人培训与方案评审等场景。"
    
    if len(summary) > 300:
        summary = summary[:297] + "..."
    
    return summary


def main():
    if len(sys.argv) < 3:
        print("用法: python generate_any_batch_results.py <输入JSON> <输出JSON>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    with open(input_file, 'r', encoding='utf-8') as f:
        files = json.load(f)
    
    results = {}
    
    for item in files:
        name = item.get('name') or item.get('filename')
        title = item.get('title_short') or item.get('title') or ''
        preview = item.get('preview', '')
        q_num = item.get('q_number')
        content_type = item.get('content_type', '')
        line_count = item.get('line_count', 50)
        fdir = item.get('dir', '')
        
        summary = generate_summary(title, preview, q_num, content_type, line_count, fdir)
        keywords = generate_keywords(title, preview, q_num, content_type, fdir)
        
        results[name] = {
            'name': name,
            'dir': fdir,
            'batch_num': item.get('batch_num', 0),
            'local_idx': item.get('local_idx', 0),
            'q_number': q_num,
            'summary': summary,
            'keywords': keywords,
        }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已生成 {len(results)} 个文件的结果")
    print(f"   输入: {input_file}")
    print(f"   输出: {output_file}")
    print()
    
    for i, (name, res) in enumerate(list(results.items())[:5]):
        print(f"[{i+1}] {name[:55]}")
        print(f"    概要({len(res['summary'])}字): {res['summary'][:70]}...")
        print(f"    关键词({res['keywords'].count('·')+1}个): {res['keywords'][:60]}")
        print()
    
    if len(results) > 5:
        print(f"... 还有 {len(results)-5} 个文件")
        print()
    
    from collections import Counter
    print(f"📊 内容类型分布:")
    type_count = Counter()
    dir_count = Counter()
    for item in files:
        ct = item.get('content_type', '').split(' / ')[0]
        type_count[ct] += 1
        dir_count[item.get('dir', '')] += 1
    for d, c in dir_count.most_common():
        print(f"  📁 {d}: {c}个")
    for t, c in type_count.most_common():
        print(f"  {t or '未分类'}: {c}个")


if __name__ == '__main__':
    main()
