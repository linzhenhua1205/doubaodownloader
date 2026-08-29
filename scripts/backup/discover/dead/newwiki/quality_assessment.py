# -*- coding: utf-8 -*-
import os
import re
import json

def assess_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    name = os.path.basename(filepath)
    char_count = len(content)
    word_count_est = char_count  # 中文字符数近似字数
    
    # 统计对比表格数（markdown表格，至少有表头+分隔行+数据行）
    table_pattern = r'^\|.*\|\s*\n\|[-\s|:]+\|\s*\n\|.*\|'
    tables = re.findall(table_pattern, content, re.MULTILINE)
    table_count = len(tables)
    
    # 统计代码块/架构图数量
    code_blocks = re.findall(r'```', content)
    code_block_count = len(code_blocks) // 2
    
    # 统计ASCII图（包含┌┐└┘等字符的代码块）
    ascii_art_count = len(re.findall(r'```[a-zA-Z]*\s*\n[┌┐└┘├┤│─]', content))
    
    # 统计mermaid图
    mermaid_count = len(re.findall(r'```mermaid', content))
    
    # 检查是否有决策框架/选型指南
    has_decision_framework = bool(re.search(r'(选型|决策框架|评估矩阵|怎么选|如何选择|选哪个|对比选择|决策指南)', content))
    
    # 检查是否有2025-2026最新数据
    has_2025_2026 = bool(re.search(r'202[56]', content))
    
    # 检查是否有企业案例
    has_case_study = bool(re.search(r'(案例|Case Study|企业案例|落地案例|最佳实践|某企业|客户案例)', content))
    
    # 检查是否有学习路径
    has_learning_path = bool(re.search(r'(学习路径|学习路线|成长路径|怎么学|如何学习|入门到精通|推荐.*书|课程推荐)', content))
    
    # 检查是否有知识体系全景图
    has_knowledge_map = bool(re.search(r'(知识体系|全景图|架构图|知识图谱|体系结构|技术栈)', content))
    
    # 检查是否有核心技术深度解析
    has_deep_analysis = bool(re.search(r'(深度解析|技术原理|原理解析|核心技术|技术深度|深入理解)', content))
    
    # 估算import素材引用数
    import_refs = len(re.findall(r'(import/|素材来源|引用素材|整合素材)', content))
    
    # 综合质量评分（0-100）
    score = 0
    
    # 字数评分（40分）
    if char_count > 80000:
        score += 40
    elif char_count > 50000:
        score += 30
    elif char_count > 30000:
        score += 20
    elif char_count > 15000:
        score += 10
    else:
        score += 5
    
    # 表格评分（20分）
    if table_count >= 10:
        score += 20
    elif table_count >= 6:
        score += 15
    elif table_count >= 3:
        score += 10
    elif table_count >= 1:
        score += 5
    
    # 架构图评分（10分）
    diagram_count = ascii_art_count + mermaid_count
    if diagram_count >= 3:
        score += 10
    elif diagram_count >= 2:
        score += 8
    elif diagram_count >= 1:
        score += 5
    else:
        score += 0
    
    # 决策框架（5分）
    score += 5 if has_decision_framework else 0
    
    # 最新数据（5分）
    score += 5 if has_2025_2026 else 0
    
    # 企业案例（5分）
    score += 5 if has_case_study else 0
    
    # 学习路径（5分）
    score += 5 if has_learning_path else 0
    
    # 知识体系图（5分）
    score += 5 if has_knowledge_map else 0
    
    # 深度解析（5分）
    score += 5 if has_deep_analysis else 0
    
    # 质量等级
    if score >= 85:
        grade = 'S+'
    elif score >= 70:
        grade = 'S'
    elif score >= 55:
        grade = 'A'
    elif score >= 40:
        grade = 'B'
    else:
        grade = 'C'
    
    return {
        'name': name,
        'char_count': char_count,
        'word_count_est': word_count_est,
        'table_count': table_count,
        'code_block_count': code_block_count,
        'ascii_art_count': ascii_art_count,
        'mermaid_count': mermaid_count,
        'diagram_count': diagram_count,
        'has_decision_framework': has_decision_framework,
        'has_2025_2026': has_2025_2026,
        'has_case_study': has_case_study,
        'has_learning_path': has_learning_path,
        'has_knowledge_map': has_knowledge_map,
        'has_deep_analysis': has_deep_analysis,
        'import_refs': import_refs,
        'score': score,
        'grade': grade
    }

def main():
    wiki_dir = r'h:\github\cowkb\discover\newwiki'
    
    exclude_files = {'index.md', 'task_plan.md', 'progress.md', 'findings.md', 
                     'enhance_wiki.py', 'quality_assessment.py'}
    
    results = []
    
    for fname in sorted(os.listdir(wiki_dir)):
        if not fname.endswith('.md'):
            continue
        if fname in exclude_files:
            continue
        filepath = os.path.join(wiki_dir, fname)
        result = assess_file(filepath)
        results.append(result)
    
    # 按分数排序
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # 打印结果
    print("=" * 100)
    print(f"{'文件名':<30} {'字数':>8} {'表格':>4} {'架构图':>4} {'决策':>4} {'最新':>4} {'案例':>4} {'学习':>4} {'体系':>4} {'深度':>4} {'得分':>4} {'等级':>4}")
    print("=" * 100)
    
    for r in results:
        print(f"{r['name']:<28} {r['char_count']:>8} {r['table_count']:>4} {r['diagram_count']:>4} "
              f"{'✓' if r['has_decision_framework'] else '✗':>4} {'✓' if r['has_2025_2026'] else '✗':>4} "
              f"{'✓' if r['has_case_study'] else '✗':>4} {'✓' if r['has_learning_path'] else '✗':>4} "
              f"{'✓' if r['has_knowledge_map'] else '✗':>4} {'✓' if r['has_deep_analysis'] else '✗':>4} "
              f"{r['score']:>4} {r['grade']:>4}")
    
    print("=" * 100)
    
    # 统计
    grade_count = {}
    for r in results:
        grade_count[r['grade']] = grade_count.get(r['grade'], 0) + 1
    
    print(f"\n质量等级分布：")
    for grade in ['S+', 'S', 'A', 'B', 'C']:
        if grade in grade_count:
            print(f"  {grade}: {grade_count[grade]} 个")
    
    print(f"\n总计: {len(results)} 个主题文件")
    print(f"平均分数: {sum(r['score'] for r in results) / len(results):.1f}")
    print(f"平均字数: {sum(r['char_count'] for r in results) / len(results):.0f}")
    print(f"总表格数: {sum(r['table_count'] for r in results)}")
    print(f"总架构图数: {sum(r['diagram_count'] for r in results)}")
    
    # 保存为JSON
    with open(os.path.join(wiki_dir, 'quality_assessment_results.json'), 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n详细结果已保存到 quality_assessment_results.json")

if __name__ == '__main__':
    main()
