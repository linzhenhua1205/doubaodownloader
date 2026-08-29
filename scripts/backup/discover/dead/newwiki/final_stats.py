# -*- coding: utf-8 -*-
import os
import re
import json

def analyze_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    name = os.path.basename(filepath)
    
    # 中文字符数（去掉markdown标记）
    # 简单估算：总字符数的70-80%左右是实际内容
    total_chars = len(content)
    
    # 统计表格数
    table_pattern = r'^\|.*\|\s*\n\|[-\s|:]+\|\s*\n'
    tables = re.findall(table_pattern, content, re.MULTILINE)
    table_count = len(tables)
    
    # 统计代码块数
    code_blocks = re.findall(r'```', content)
    code_block_count = len(code_blocks) // 2
    
    # 统计ASCII架构图（包含框线字符的代码块）
    ascii_art = len(re.findall(r'```[a-zA-Z]*\s*\n.*?[┌┐└┘├┤│─].*?```', content, re.DOTALL))
    
    # 统计mermaid图
    mermaid = len(re.findall(r'```mermaid', content))
    
    total_diagrams = ascii_art + mermaid
    
    # 检查7大模块是否存在
    modules = {
        '知识体系全景图': bool(re.search(r'(知识体系|全景图|架构图|知识图谱)', content)),
        '核心技术深度解析': bool(re.search(r'(深度解析|技术原理|核心技术|技术深度)', content)),
        '对比分析表格': table_count >= 3,
        '选型决策框架': bool(re.search(r'(选型|决策框架|评估矩阵|怎么选|如何选择)', content)),
        '2025-2026最新进展': bool(re.search(r'202[56]', content)),
        '企业级案例': bool(re.search(r'(案例|Case Study|企业案例|落地案例|最佳实践)', content)),
        '学习路径': bool(re.search(r'(学习路径|学习路线|成长路径|怎么学|如何学习|推荐.*书)', content)),
    }
    
    modules_completed = sum(modules.values())
    
    # import素材引用
    import_refs = len(re.findall(r'(import/|素材来源|引用素材|整合素材|素材.*整合)', content))
    
    # 判断质量等级
    # 基于：字数、表格数、架构图数、模块完成度
    score = 0
    
    # 字数（30分）
    if total_chars > 150000:
        score += 30
    elif total_chars > 100000:
        score += 25
    elif total_chars > 60000:
        score += 20
    elif total_chars > 30000:
        score += 15
    else:
        score += 10
    
    # 表格数（20分）
    if table_count >= 15:
        score += 20
    elif table_count >= 10:
        score += 17
    elif table_count >= 6:
        score += 14
    elif table_count >= 3:
        score += 10
    else:
        score += 5
    
    # 架构图（15分）
    if total_diagrams >= 5:
        score += 15
    elif total_diagrams >= 3:
        score += 12
    elif total_diagrams >= 2:
        score += 9
    elif total_diagrams >= 1:
        score += 6
    else:
        score += 0
    
    # 模块完成度（25分）
    score += modules_completed * (25 / 7)
    
    # import素材（10分）
    if import_refs >= 8:
        score += 10
    elif import_refs >= 5:
        score += 8
    elif import_refs >= 3:
        score += 6
    elif import_refs >= 1:
        score += 4
    else:
        score += 0
    
    # 等级
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
        'total_chars': total_chars,
        'table_count': table_count,
        'ascii_art': ascii_art,
        'mermaid': mermaid,
        'total_diagrams': total_diagrams,
        'code_blocks': code_block_count,
        'modules': modules,
        'modules_completed': modules_completed,
        'import_refs': import_refs,
        'score': round(score, 1),
        'grade': grade
    }

def main():
    wiki_dir = r'h:\github\cowkb\discover\newwiki'
    
    exclude = {'index.md', 'task_plan.md', 'progress.md', 'findings.md', 
               'enhance_wiki.py', 'quality_assessment.py', 'final_stats.py',
               'quality_assessment_results.json'}
    
    results = []
    
    for fname in sorted(os.listdir(wiki_dir)):
        if not fname.endswith('.md') or fname in exclude:
            continue
        fpath = os.path.join(wiki_dir, fname)
        r = analyze_file(fpath)
        results.append(r)
    
    # 按分数排序
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # 打印
    print("=" * 120)
    print(f"{'文件名':<30} {'字数':>8} {'表格':>4} {'架构图':>4} {'ASCII':>4} {'Mermaid':>6} {'模块':>4}/7 {'import':>5} {'得分':>5} {'等级':>4}")
    print("=" * 120)
    
    for r in results:
        print(f"{r['name']:<28} {r['total_chars']:>8} {r['table_count']:>4} {r['total_diagrams']:>4} "
              f"{r['ascii_art']:>4} {r['mermaid']:>6} {r['modules_completed']:>4}/7 {r['import_refs']:>5} "
              f"{r['score']:>5} {r['grade']:>4}")
    
    print("=" * 120)
    
    # 等级分布
    grade_count = {}
    for r in results:
        grade_count[r['grade']] = grade_count.get(r['grade'], 0) + 1
    
    print(f"\n📊 质量等级分布：")
    for g in ['S+', 'S', 'A', 'B', 'C']:
        if g in grade_count:
            print(f"  {g}: {grade_count[g]} 个")
    
    print(f"\n📈 总体统计：")
    print(f"  主题文件总数：{len(results)} 个")
    print(f"  平均分数：{sum(r['score'] for r in results)/len(results):.1f}")
    print(f"  平均字数：{sum(r['total_chars'] for r in results)/len(results):.0f}")
    print(f"  总表格数：{sum(r['table_count'] for r in results)}")
    print(f"  总架构图数：{sum(r['total_diagrams'] for r in results)}")
    print(f"  平均表格数/文件：{sum(r['table_count'] for r in results)/len(results):.1f}")
    print(f"  平均架构图数/文件：{sum(r['total_diagrams'] for r in results)/len(results):.1f}")
    print(f"  7大模块全部完成的文件：{sum(1 for r in results if r['modules_completed']==7)} 个")
    
    # 7大模块完成情况
    print(f"\n📋 7大模块覆盖率：")
    module_names = ['知识体系全景图', '核心技术深度解析', '对比分析表格', '选型决策框架', 
                    '2025-2026最新进展', '企业级案例', '学习路径']
    for m in module_names:
        count = sum(1 for r in results if r['modules'][m])
        print(f"  {m}: {count}/{len(results)} ({count*100/len(results):.0f}%)")
    
    # 保存JSON
    with open(os.path.join(wiki_dir, 'final_enhancement_report.json'), 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 详细数据已保存到 final_enhancement_report.json")

if __name__ == '__main__':
    main()
