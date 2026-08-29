#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复批量增强后的文件问题
- 修复错误的标题
- 清理索引页元数据
- 优化内容结构
"""

import re
import os

def fix_file(filepath):
    """修复单个文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取文件名作为备用标题
    filename = os.path.basename(filepath).replace('.md', '')
    
    # 1. 修复frontmatter中的title
    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if fm_match:
        fm_content = fm_match.group(1)
        title_match = re.search(r'title:\s*(.+)', fm_content)
        if title_match:
            old_title = title_match.group(1).strip()
            # 如果标题包含markdown链接、括号、URL等异常内容，用文件名
            if re.search(r'\[.*\]\(.*\)', old_title) or 'http' in old_title or len(old_title) > 50:
                new_title = filename
                fm_content = fm_content.replace(f'title: {old_title}', f'title: {new_title}')
                content = content[:fm_match.start()] + '---\n' + fm_content + '\n---' + content[fm_match.end():]
    
    # 2. 修复正文中的一级标题
    h1_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    if h1_match:
        old_h1 = h1_match.group(1).strip()
        if re.search(r'\[.*\]\(.*\)', old_h1) or 'http' in old_h1 or len(old_h1) > 50:
            # 从frontmatter获取正确的标题
            fm_title_match = re.search(r'title:\s*(.+)', fm_content if 'fm_content' in dir() else '')
            new_h1 = fm_title_match.group(1).strip() if fm_title_match else filename
            content = content[:h1_match.start()] + f'# {new_h1}' + content[h1_match.end():]
    
    # 3. 清理核心概念部分的索引页元数据
    # 匹配 "## 2. 核心概念与基础" 后面的索引元数据
    pattern = r'(## 2\. 核心概念与基础\n\n)(.*?)(### 核心维度对比)'
    replacement = r'\1' + _generate_core_concepts(filename) + r'\n\n\3'
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # 4. 修复核心洞察中的错误标题引用
    content = re.sub(
        r'> \*\*核心洞察\*\*：.*?不是孤立的知识点',
        f'> **核心洞察**：{filename}相关知识不是孤立的知识点',
        content
    )
    
    # 5. 修复全景图中的错误标题
    content = re.sub(
        r'### .*知识体系全景图',
        f'### {filename}知识体系全景图',
        content
    )
    
    # 6. 清理方法框架部分的低质量内容
    method_pattern = r'(## 3\. 方法框架与实践\n\n### 核心方法论\n\n)(.*?)(### 不同方法对比)'
    method_replacement = r'\1' + _generate_methodology(filename) + r'\n\n\3'
    content = re.sub(method_pattern, method_replacement, content, flags=re.DOTALL)
    
    # 重新估算字数
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
    english_words = len(re.findall(r'[a-zA-Z]+', content))
    total_words = chinese_chars + english_words
    
    # 更新frontmatter中的字数
    content = re.sub(
        r'word_count: 约 \d+ 字',
        f'word_count: 约 {total_words} 字',
        content
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True, f'修复完成，约{total_words}字'

def _generate_core_concepts(topic):
    """生成核心概念内容"""
    concepts = {
        '股权': '股权是指股东因出资而对公司享有的人身和财产权益的一种综合性权利。股权的核心是所有权和收益权，具体包括表决权、分红权、知情权、转让权等。在创业公司中，股权分配是一个至关重要的问题，直接影响公司的治理结构和创始人的控制权。\n\n**股权的核心要素：**\n- **表决权**：参与公司重大决策的权利\n- **分红权**：获得公司利润分配的权利\n- **知情权**：了解公司经营状况的权利\n- **转让权**：依法转让股权的权利\n- **优先认购权**：公司增发时优先认购的权利',
        '大学生就业趋': '大学生就业趋势是社会经济发展的风向标，反映了产业结构变迁、人才供需变化和技术革新的影响。近年来，受经济周期、技术变革、政策调整等多重因素影响，大学生就业市场呈现出新的特点和趋势。\n\n**核心观察维度：**\n- **供需关系**：毕业生人数增长 vs 岗位需求变化\n- **行业结构**：新兴行业崛起 vs 传统行业转型\n- **地域分布**：一线城市聚集 vs 新一线城市崛起\n- **能力要求**：学历导向 vs 能力导向\n- **就业形态**：全职就业 vs 灵活就业',
        '数学证明解析': '数学证明是数学的核心，是从已知条件出发，通过逻辑推理得出结论的过程。理解和掌握数学证明，不仅是学习数学的关键，也是培养逻辑思维能力的重要途径。\n\n**数学证明的基本要素：**\n- **已知条件**：证明的起点和基础\n- **公理/定理**：推理的依据和规则\n- **逻辑推导**：一步步的推理过程\n- **最终结论**：要证明的目标\n- **严谨性**：每一步都要有理有据',
    }
    
    # 默认模板
    default = f'{topic}是一个值得深入了解的知识领域。理解它需要从基础概念入手，逐步建立完整的认知框架。\n\n**核心要点：**\n- **基础概念**：理解核心定义和基本原理\n- **方法体系**：掌握主要的分析方法和工具\n- **实践应用**：在实际场景中运用所学知识\n- **持续学习**：关注领域最新发展动态'
    
    return concepts.get(topic, default)

def _generate_methodology(topic):
    """生成方法论内容"""
    methods = {
        '股权': '**1. 股权分配原则**\n   - 公平原则：贡献与股权匹配\n   - 效率原则：决策效率优先\n   - 稳定原则：避免频繁变动\n   - 预留原则：为未来人才留出期权池\n\n**2. 股权架构设计方法**\n   - 直接持股 vs 间接持股\n   - 有限合伙架构的运用\n   - 表决权委托与一致行动人\n   - AB股双层股权结构\n\n**3. 股权激励要点**\n   - 激励对象选择\n   - 授予数量与节奏\n   - 行权条件与考核\n   - 退出机制设计',
        '大学生就业趋': '**1. 职业规划方法**\n   - 自我认知：了解自己的兴趣、能力、价值观\n   - 行业研究：了解各行业的发展前景\n   - 目标设定：短期和长期职业目标\n   - 路径规划：实现目标的具体步骤\n\n**2. 求职准备策略**\n   - 技能提升：补齐短板，强化优势\n   - 简历优化：突出亮点，匹配岗位\n   - 面试准备：常见问题，模拟演练\n   - 信息搜集：目标公司，行业动态\n\n**3. 职业发展路径**\n   - 技术路线：深度专精，成为专家\n   - 管理路线：带团队，做管理\n   - 创业路线：自己干，闯一番\n   - 跨界路线：结合多领域优势',
        '数学证明解析': '**1. 基础拆解法**\n   - 拆分三段式：已知条件、中间推导、最终结论\n   - 划清边界：明确什么是已知，什么是要证的\n   - 梳理逻辑链：理清证明的主线和分支\n\n**2. 正向推导法**\n   - 从已知条件出发\n   - 一步步向前推导\n   - 每一步都要有依据\n   - 最终得出结论\n\n**3. 反向分析法**\n   - 从结论往回看\n   - 思考要得到这个结论需要什么条件\n   - 一步步倒推到已知条件\n   - 然后再正向写出来\n\n**4. 反证法**\n   - 假设结论不成立\n   - 从这个假设出发推导\n   - 推出矛盾\n   - 从而证明原结论正确',
    }
    
    default = f'**1. 入门路径**\n   - 从基础概念开始，建立基本认知\n   - 通过具体案例加深理解\n   - 边学边练，在实践中巩固\n\n**2. 进阶方法**\n   - 系统学习完整知识体系\n   - 深入钻研核心原理和方法\n   - 参与实际项目和案例分析\n\n**3. 持续精进**\n   - 关注领域最新动态\n   - 与同行交流学习\n   - 持续输出，教学相长'
    
    return methods.get(topic, default)

def batch_fix(dir_path, files):
    """批量修复文件"""
    results = []
    for filename in files:
        filepath = os.path.join(dir_path, filename)
        if not os.path.exists(filepath):
            results.append((filename, '跳过', '文件不存在'))
            continue
        
        success, msg = fix_file(filepath)
        status = '成功' if success else '失败'
        results.append((filename, status, msg))
        print(f'{filename:40s} {status:4s} {msg}')
    
    return results

if __name__ == '__main__':
    dir_path = 'programming'
    
    # 需要修复的文件（批量增强的文件）
    files_to_fix = [
        '02-software-architecture-patterns.md',
        '03-lachat-architecture.md',
        'paperclip.md',
        'rise.md',
        'sherwood.md',
        'ubuntutoucho.md',
        '三体阅读心境.md',
        '企业周均工时.md',
        '叙事六要素.md',
        '古文讲解与原.md',
        '备件快速响应.md',
        '大学生就业趋.md',
        '审计步骤核心.md',
        '属性辨析.md',
        '市场份额对.md',
        '开发代码版本.md',
        '归纳过程可视.md',
        '快速理解开源.md',
        '支持度与置信.md',
        '数学证明解析.md',
        '生产标物料转.md',
        '知乎文章无法.md',
        '股权.md',
        '螺旋模型优化.md',
        '行人路权受侵.md',
        '解构思维解决.md',
        '认知托付框架.md',
        '链接解析失败.md',
        '阿里云光模块.md',
        '阿里云王坚.md',
        '附件链接失效.md',
    ]
    
    print('='*80)
    print(f'开始批量修复 {len(files_to_fix)} 个文件')
    print('='*80)
    
    results = batch_fix(dir_path, files_to_fix)
    
    print()
    print('='*80)
    print(f'批量修复完成！成功：{sum(1 for r in results if r[1]=="成功")}，失败：{sum(1 for r in results if r[1]=="失败")}')
    print('='*80)
