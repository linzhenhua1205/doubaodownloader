#!/usr/bin/env python3
"""
关键词质量快速修复

修复关键词中的碎片词，确保每个关键词都是有意义的完整词汇
"""

import re
import os
import sys
from pathlib import Path
from datetime import datetime


def extract_frontmatter(text):
    if text.startswith('---'):
        end_pos = text.find('\n---', 3)
        if end_pos != -1:
            fm = text[3:end_pos].strip()
            body = text[end_pos+4:].strip()
            return fm, body
    return "", text


def extract_title_from_fm(fm):
    match = re.search(r'^title:\s*(.+?)\s*$', fm, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return ""


COMMON_EMOJIS = [
    '📊', '📋', '📖', '📚', '📌', '📎', '📐', '📏', '📝',
    '🔬', '🔍', '🔎', '🔭',
    '💼', '💻', '📱', '🖥️', '⌨️', '🖱️',
    '🚀', '🔥', '💪', '✨', '⭐', '🌟', '💡',
    '🎯', '🎨', '🎭', '🎪', '🎬', '🎤', '🎧',
    '🧠', '🤖', '👾', '🧬', '🔮',
    '💰', '💸', '💵', '💎', '📈', '📉',
    '🏆', '🥇', '🥈', '🥉',
    '🎓', '✏️',
    '🌐', '🌍', '🌎', '🌏',
    '⚡', '🔔', '🔕', '📢', '📣',
    '🛡️', '🔒', '🔓', '🔑',
    '⚙️', '🔧', '🔨', '🛠️', '🧰',
    '📅', '📆', '⏰', '⏱️', '⏲️',
    '👥', '👤', '🧑', '👨', '👩',
    '❓', '❔', '❗', '❕',
    '➕', '➖', '➗', '✖️',
    '⬆️', '⬇️', '⬅️', '➡️',
    '↗️', '↘️', '↙️', '↖️',
    '🔄', '🔁', '🔂',
    '▶️', '⏸️', '⏹️', '⏺️',
    '🏷️', '🏷',
    '💬', '💭', '🗨️', '🗯️',
    '🎉', '🎊', '🎁', '🎂',
    '☕', '🍵', '🍺', '🍷',
    '📷', '📹', '🎥', '📺', '📻',
    '📞', '☎️', '📟',
    '🔋', '🪫', '🔌',
    '🧪', '🧫',
    '🌱', '🌿', '🍀', '🌸',
    '🚗', '🚙', '✈️', '🚢',
    '🏠', '🏢', '🏥', '🏫', '🏪',
    '⚖️', '🗂️', '📁', '📂',
    '🧩', '🧸', '🎮',
    '🆕', '🆓', '🆒', '🆙',
    '🔴', '🟠', '🟡', '🟢', '🔵', '🟣', '⚫', '⚪',
    '🟥', '🟧', '🟨', '🟩', '🟦', '🟪', '⬛', '⬜',
    '◻️', '◼️', '🔲', '🔳',
    '✓', '✔️', '✗', '✘', '❌', '✅',
    '⚠️', '⚠',
]


def remove_emoji(text):
    result = text
    for emoji in COMMON_EMOJIS:
        result = result.replace(emoji, '')
    return result


def clean_heading(text):
    t = remove_emoji(text)
    t = t.lstrip(' -—·•')
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def extract_article_specific_content(body):
    """提取文章特有内容"""
    template_keywords = [
        '核心要点', '快速导读', '背景与意义', '背景与上下文', '深度解读',
        '主流大模型对比', '挑战与风险', '趋势与展望', '建议与行动指南',
        '企业案例与应用实践', '核心技术解析', '现状与格局',
        '关键数据', '阅读建议', '适合人群', '阅读时长', '难度等级',
        '内容评级', 'import素材融合', '知识关联',
        'AI技术路线对比',
    ]
    
    content_match = re.search(
        r'##\s*内容[^\n]*\n(.+?)(?=\n## |\Z)',
        body, re.DOTALL
    )
    
    if content_match:
        content_text = content_match.group(1)
        content_text = re.sub(r'^原文[：:].*?\n', '', content_text, flags=re.MULTILINE)
        content_text = content_text.strip()
        if len(content_text) > 100:
            return content_text
    
    all_sections = re.finditer(r'##\s+(.+?)\n(.+?)(?=\n## |\Z)', body, re.DOTALL)
    
    specific_parts = []
    for sec in all_sections:
        sec_title = clean_heading(sec.group(1))
        sec_content = sec.group(2)
        
        is_template = False
        for kw in template_keywords:
            if kw in sec_title:
                is_template = True
                break
        
        if not is_template and sec_title not in ['目录', '参考文件', 'Changelog', '参考资料']:
            specific_parts.append(sec_content)
    
    if specific_parts:
        return '\n\n'.join(specific_parts)
    
    return body


def is_valid_keyword(kw):
    """判断是否是有效关键词"""
    if not kw or len(kw) < 2:
        return False
    
    kw = kw.strip()
    
    if len(kw) < 2:
        return False
    
    if re.match(r'^\d+$', kw):
        return False
    
    if re.match(r'^(19|20)\d{2}$', kw):
        return False
    
    bad_patterns = [
        r'^与.*$',
        r'^.*与$',
        r'^的.*$',
        r'^.*的$',
        r'^.*局$',
        r'^.*析$',
        r'^.*告$',
        r'^.*南$',
        r'^.*录$',
        r'^.*设$',
        r'^.*究$',
        r'^.*台$',
        r'^.*品$',
        r'^.*术$',
        r'^.*具$',
        r'^.*用$',
        r'^.*景$',
        r'^.*案$',
        r'^.*策$',
        r'^.*式$',
        r'^.*态$',
        r'^.*面$',
        r'^.*线$',
        r'^.*期$',
        r'^.*半$',
        r'^.*全$',
        r'^.*新$',
        r'^.*报$',
        r'^.*下$',
        r'^.*上$',
        r'^.*中$',
        r'^.*内$',
        r'^.*外$',
        r'^.*前$',
        r'^.*后$',
        r'^.*大$',
        r'^.*小$',
        r'^.*多$',
        r'^.*少$',
        r'^.*高$',
        r'^.*低$',
        r'^.*快$',
        r'^.*慢$',
        r'^.*好$',
        r'^.*坏$',
        r'^.*新$',
        r'^.*旧$',
        r'^.*长$',
        r'^.*短$',
        r'^.*深$',
        r'^.*浅$',
        r'^.*广$',
        r'^.*窄$',
        r'^.*强$',
        r'^.*弱$',
        r'^.*重$',
        r'^.*轻$',
    ]
    
    for pat in bad_patterns:
        if re.match(pat, kw):
            return False
    
    stopwords = {
        '分析', '指南', '详解', '深度', '全面', '最新', '报告', '研究',
        '技术', '应用', '发展', '趋势', '实践', '案例', '综述', '概览',
        '入门', '进阶', '高级', '基础', '原理', '实战', '教程', '手册',
        '大全', '合集', '精选', '推荐', '汇总', '盘点', '揭秘', '洞察',
        '思考', '解读', '观察', '评论', '观点', '看法', '经验', '心得',
        'AI', '人工智能', '行业动态', '产品与设计',
        '编程与开发', '系统与运维', '数据库', '知识管理',
        '核心要点', '关键数据', '阅读建议',
        '全景', '深度分析', '全面解析', '最新进展',
        '行业报告', '市场分析', '技术分析',
        '什么是', '如何', '怎么', '为什么',
        '内容', '文章', '本文', '我们', '他们',
        '可以', '能够', '需要', '已经', '正在',
        '一个', '一种', '一些', '这个', '那个',
        '以及', '还有', '包括', '包含', '涉及',
        '通过', '基于', '对于', '关于', '随着',
        '因此', '所以', '但是', '然而', '而且',
        '市场', '产业', '行业', '企业', '公司',
        '产品', '服务', '用户', '客户',
        '功能', '性能', '效果', '效率',
        '问题', '挑战', '风险', '机遇',
        '未来', '当前', '目前', '现在',
        '中国', '全球', '世界', '美国',
        '大会', '峰会', '论坛', '展会',
        '发布', '推出', '上线',
        '合作', '投资', '融资', '收购',
        '增长', '下降', '提升', '降低',
        '数据', '信息', '知识', '方法',
        '系统', '平台', '工具', '框架',
        '方案', '模式', '流程', '标准',
        '架构', '设计', '开发', '测试',
        '优化', '改进', '创新', '突破',
        '优势', '特点', '特征', '属性',
        '价格', '成本', '价值', '利润',
        '规模', '数量', '质量', '速度',
        '时间', '空间', '范围', '领域',
        '方面', '角度', '层面', '维度',
        '阶段', '时期', '阶段', '周期',
        '水平', '程度', '级别', '等级',
        '类型', '种类', '类别', '分类',
        '方式', '方法', '策略', '路径',
        '结果', '效果', '成果', '成就',
        '原因', '因素', '条件', '环境',
        '情况', '状态', '形势', '局面',
        '结构', '组织', '机构', '团队',
        '人才', '人员', '用户', '客户',
        '资本', '资金', '资源', '资产',
        '业务', '工作', '任务', '项目',
        '产品', '服务', '解决方案',
        '深度解读', '深度分析', '全面解析',
        '研究报告', '分析报告', '行业报告',
        '解决方案', '最佳实践', '实战指南',
        '入门教程', '学习笔记', '技术分享',
        '案例分析', '经验总结', '心得体会',
        '趋势预测', '前景展望', '未来展望',
        '资本押注', '案例洞察', '产业趋势',
        '全面提升', '编程效率',
        '技术细节', '开源价值',
        '技术融合', '版本革新',
        '工具对比', '场景适配',
        '效能提升', '实战',
        '趋势洞察', '落地挑战',
        '年程序员', '薪资全景',
        '技术演进', '生态重构', '商业突围',
        '产品进入', '垂直场景', '深度应用', '下半场',
        '投资逻辑', '变现路径', '竞争格',
        '市场格局', '投资机',
        '大模型时', '代的数据', '安全风险',
        '夏令营作', '品全景',
        '技术突破', '产品形态',
        '产品升级', '技术突',
        '模型更新', '融资与行', '业动态',
        '算力竞赛', '与应用落', '地双轮驱',
        '驱动科研', '创新与', '系统发布',
        '技术演进', '场景落地', '与竞争格', '局深度分',
        '版本革新', '技术融合',
        '工具选型', '场景适配',
        '年程序员', '薪资全景',
        '技术演进', '生态重构', '商业突围',
        '产品进入', '垂直场景', '深度应用',
        '投资逻辑', '变现路径',
        '市场格局', '技术演进', '与投资机',
        '大模型时', '代的数据', '安全风险',
        '夏令营作', '品全景分',
        '技术突破', '产品形态',
        '产品升级', '技术突',
        '模型更新', '融资与行', '业动态',
        '算力竞赛', '与应用落', '地双轮驱',
        '驱动科研', '创新与', '系统发布',
        '定义', '未来十年', '的核心方', '向与落地',
        '下一个十', '年的场景', '驱动与新', '质引擎',
        '技术突破', '落地路径', '与市场格', '局深度分',
        '电商的落', '地突破与', '现实挑战',
        '杭州', '六小龙', '引领', '从文本走',
        '从百模大', '战到生存', '淘汰赛',
        '世界互联网大会',
        '资本押注', '案例洞察', '与产业趋',
        '全面提升', '你的编程',
        '技术细节', '性能与开',
        '活法', '定义', '算法',
        '优势', '功能与选', '择指南',
        '编程助手',
        '版本革新', '技术融合',
        '工具选型', '场景适配', '与效能提', '升实战',
        '趋势洞察', '落地挑战',
        '年程序员', '薪资全景',
        '技术演进', '生态重构', '商业突围',
        '产品进入', '垂直场景', '深度应用', '下半场',
        '投资逻辑', '变现路径', '与竞争格',
        '市场格局', '技术演进', '与投资机',
        '大模型时', '代的数据', '安全风险',
        '夏令营作', '品全景分',
        '技术突破', '产品形态',
        '产品升级', '技术突',
        '模型更新', '融资与行', '业动态',
        '算力竞赛', '与应用落', '地双轮驱',
        '驱动科研', '创新与', '系统发布',
        '阿里', '谷歌', '腾讯布局', '智能体生',
        '数据', '案例与', '影响分析',
    }
    
    if kw in stopwords:
        return False
    
    return True


def generate_good_keywords(specific_content, title, fm):
    """生成高质量关键词"""
    candidates = []
    seen = set()
    
    def add(kw, prio):
        kw = kw.strip()
        if kw and kw not in seen and is_valid_keyword(kw):
            candidates.append((kw, prio))
            seen.add(kw)
    
    title_clean = clean_heading(title)
    
    # 高优先级：从预定义的技术术语中匹配标题
    tech_terms_title = [
        ('OLMo', 'OLMo'),
        ('Zabbix', 'Zabbix'),
        ('WAIC', 'WAIC'),
        ('IDEA大会', 'IDEA大会'),
        ('T-EDGE', 'T-EDGE'),
        ('AWS', 'AWS'),
        ('re:Invent', 're:Invent'),
        ('Dify', 'Dify'),
        ('KTransformers', 'KTransformers'),
        ('LLaMA-Factory', 'LLaMA-Factory'),
        ('GPT', 'GPT'),
        ('Claude', 'Claude'),
        ('Gemini', 'Gemini'),
        ('DeepSeek', 'DeepSeek'),
        ('通义千问', '通义千问'),
        ('Qwen', '通义千问'),
        ('Llama', 'Llama'),
        ('MoE', 'MoE架构'),
        ('Transformer', 'Transformer架构'),
        ('RAG', 'RAG'),
        ('Agent', 'AI Agent'),
        ('智能体', 'AI Agent'),
        ('AIGC', 'AIGC'),
        ('生成式AI', 'AIGC'),
        ('提示词', '提示工程'),
        ('提示工程', '提示工程'),
        ('Prompt', '提示工程'),
        ('多模态', '多模态'),
        ('微调', '微调'),
        ('算力', '算力'),
        ('GPU', 'GPU'),
        ('Token', 'Token'),
        ('大模型', '大模型'),
        ('开源', '开源'),
        ('医疗AI', '医疗AI'),
        ('AI电商', 'AI电商'),
        ('AI编程', 'AI编程'),
        ('银发AI', '银发AI'),
        ('适老化', '银发AI'),
        ('端侧推理', '端侧推理'),
        ('企业级', '企业级应用'),
        ('知识图谱', '知识图谱'),
        ('具身智能', '具身智能'),
        ('自动驾驶', '自动驾驶'),
        ('自然语言处理', '自然语言处理'),
        ('NLP', '自然语言处理'),
        ('计算机视觉', '计算机视觉'),
        ('CV', '计算机视觉'),
        ('云栖大会', '云栖大会'),
        ('乌镇峰会', '乌镇峰会'),
        ('世界互联网大会', '乌镇峰会'),
        ('双11', '双11'),
        ('双十一', '双11'),
        ('京东双11', '双11'),
        ('天猫双11', '双11'),
        ('程序员薪资', '程序员薪资'),
        ('裁员', '科技裁员'),
        ('AI股票', 'AI股票'),
        ('飞书', '飞书知识库'),
        ('VSCode', 'VSCode'),
        ('PPT', 'AI生成PPT'),
        ('编程助手', 'AI编程助手'),
        ('AI日报', 'AI日报'),
        ('AI周报', 'AI周报'),
        ('AI月报', 'AI月报'),
        ('世界人工智能大会', 'WAIC'),
    ]
    
    for term, norm in tech_terms_title:
        if term and term.lower() in title_clean.lower():
            if norm:
                add(norm, 100)
    
    # 从特有内容中的高频技术词
    tech_patterns = [
        (r'OLMo', 10, 'OLMo'),
        (r'Zabbix', 10, 'Zabbix'),
        (r'WAIC|世界人工智能大会', 8, 'WAIC'),
        (r'Dify', 8, 'Dify'),
        (r'KTransformers', 10, 'KTransformers'),
        (r'LLaMA[-\s]?Factory', 8, 'LLaMA-Factory'),
        (r'GPT(?:-\d+(?:\.\d+)?)?', 6, 'GPT'),
        (r'Claude(?:\s*\d+\.?\d*)?', 6, 'Claude'),
        (r'Gemini(?:\s*\d+\.?\d*)?', 6, 'Gemini'),
        (r'DeepSeek|深度求索', 6, 'DeepSeek'),
        (r'通义千问|Qwen', 6, '通义千问'),
        (r'Llama|Llama\s*\d+', 6, 'Llama'),
        (r'MoE|混合专家', 5, 'MoE架构'),
        (r'Transformer', 5, 'Transformer架构'),
        (r'RAG|检索增强生成', 6, 'RAG'),
        (r'Agent|智能体', 5, 'AI Agent'),
        (r'AIGC|生成式AI', 5, 'AIGC'),
        (r'提示词|提示工程|Prompt', 5, '提示工程'),
        (r'多模态', 5, '多模态'),
        (r'微调|fine-tuning|LoRA|QLoRA', 5, '微调'),
        (r'算力', 4, '算力'),
        (r'GPU', 4, 'GPU'),
        (r'Token', 3, 'Token'),
        (r'大模型|大语言模型|LLM', 4, '大模型'),
        (r'开源', 4, '开源'),
        (r'医疗AI', 6, '医疗AI'),
        (r'AI电商|电商AI', 6, 'AI电商'),
        (r'AI编程|代码生成', 5, 'AI编程'),
        (r'银发AI|老年AI|适老化', 6, '银发AI'),
        (r'端侧推理', 4, '端侧推理'),
        (r'企业级|私有化部署', 4, '企业级应用'),
        (r'知识图谱', 4, '知识图谱'),
        (r'具身智能', 4, '具身智能'),
        (r'自动驾驶', 4, '自动驾驶'),
        (r'自然语言处理|NLP', 3, '自然语言处理'),
        (r'计算机视觉|CV', 3, '计算机视觉'),
        (r'云栖大会', 5, '云栖大会'),
        (r'乌镇峰会|世界互联网大会', 5, '乌镇峰会'),
        (r'双11|双十一', 5, '双11'),
        (r'程序员薪资', 5, '程序员薪资'),
        (r'裁员', 4, '科技裁员'),
        (r'AI股票', 4, 'AI股票'),
        (r'飞书', 4, '飞书知识库'),
        (r'VSCode', 5, 'VSCode'),
        (r'PPT', 4, 'AI生成PPT'),
        (r'编程助手|编码助手', 4, 'AI编程助手'),
    ]
    
    freq_scores = {}
    for pattern, weight, norm in tech_patterns:
        try:
            count = len(re.findall(pattern, specific_content, re.IGNORECASE))
            if count > 0:
                score = count * weight
                if norm in freq_scores:
                    freq_scores[norm] += score
                else:
                    freq_scores[norm] = score
        except:
            pass
    
    sorted_tech = sorted(freq_scores.items(), key=lambda x: x[1], reverse=True)
    for kw, score in sorted_tech:
        if score >= 8:
            add(kw, 50 + min(score, 30))
    
    # 确保至少3个
    final = []
    candidates.sort(key=lambda x: x[1], reverse=True)
    
    for kw, prio in candidates:
        if len(final) >= 5:
            break
        
        too_similar = False
        for existing in final:
            if kw in existing or existing in kw:
                if len(kw) <= len(existing):
                    too_similar = True
                    break
        
        if too_similar:
            continue
        
        final.append(kw)
    
    if len(final) < 3:
        backups = ['大模型', 'AI Agent', 'AIGC', 'RAG', '多模态']
        for b in backups:
            if b not in final:
                final.append(b)
                if len(final) >= 3:
                    break
    
    return " · ".join(final[:5])


def process_file(filepath):
    filename = Path(filepath).name
    
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    fm, body = extract_frontmatter(text)
    
    if not fm:
        return False
    
    title = extract_title_from_fm(fm)
    if not title:
        title = filename.replace('.md', '')
    
    specific_content = extract_article_specific_content(body)
    
    new_keywords = generate_good_keywords(specific_content, title, fm)
    
    # 替换关键词行
    new_body = re.sub(
        r'> \*\*关键词\*\*:\s*.+',
        f'> **关键词**: {new_keywords}',
        body
    )
    
    # 更新frontmatter
    new_fm = re.sub(
        r'^updated_at:\s*[\'"]?\d{4}-\d{2}-\d{2}[\'"]?',
        f"updated_at: '{datetime.now().strftime('%Y-%m-%d')}'",
        fm,
        flags=re.MULTILINE
    )
    
    final_text = f"---\n{new_fm}\n---\n\n{new_body}"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(final_text)
    
    print(f"  ✅ {filename[:45]}...")
    print(f"     关键词: {new_keywords}")
    return True


def main():
    if len(sys.argv) < 2:
        print('用法: python3 fix_keywords.py <目录路径>')
        sys.exit(1)
    
    target_dir = sys.argv[1]
    
    if not os.path.exists(target_dir):
        print(f'❌ 路径不存在: {target_dir}')
        sys.exit(1)
    
    md_files = sorted([f for f in Path(target_dir).glob('*.md') if f.name != 'index.md'])
    
    print(f'🔍 发现 {len(md_files)} 个markdown文件')
    print()
    
    success = 0
    fail = 0
    
    for fp in md_files:
        try:
            if process_file(str(fp)):
                success += 1
            else:
                fail += 1
        except Exception as e:
            print(f"  ❌ {Path(fp).name}: {e}")
            import traceback
            traceback.print_exc()
            fail += 1
    
    print()
    print('=' * 60)
    print(f'📊 关键词修复完成: {success} 成功, {fail} 失败')
    print('=' * 60)


if __name__ == '__main__':
    main()
