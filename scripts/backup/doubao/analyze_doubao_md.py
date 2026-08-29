import os
import re
import json
from collections import defaultdict
from datetime import datetime

MARKDOWN_DIR = "h:/github/md/doubao_batch_export/markdown"
OUTPUT_DIR = "h:/github/md/analysis_results"

def extract_qa_pairs(content):
    """从markdown内容中提取问题和回答"""
    lines = content.split('\n')
    qa_pairs = []
    
    current_question = []
    current_answer = []
    in_question = True
    
    for line in lines:
        line = line.strip()
        
        if not line:
            continue
        
        if line.startswith('#'):
            continue
        
        if line.startswith('来源链接:'):
            continue
        
        if line.startswith('##'):
            if current_question or current_answer:
                qa_pairs.append({
                    'question': '\n'.join(current_question).strip(),
                    'answer': '\n'.join(current_answer).strip()
                })
            current_question = []
            current_answer = []
            in_question = True
            continue
        
        if len(line) < 8:
            continue
        
        nav_keywords = ['新对话', 'Ctrl K', 'AI', '创作', '云盘', '更多', '历史对话', '搜索',
                       '消息', '通知', '设置', '帮助', '退出', '登录', '注册', '会员',
                       'Export', '导出', '下载', 'PDF', 'JSON', 'Word', '复制', '分享',
                       '由 AI 生成，请仔细甄别', '豆包', '输入消息', '输入框']
        
        is_noise = False
        for keyword in nav_keywords:
            if keyword in line:
                is_noise = True
                break
        
        if is_noise:
            continue
        
        if in_question:
            current_question.append(line)
            if len(current_question) > 3 or len('\n'.join(current_question)) > 500:
                in_question = False
        else:
            current_answer.append(line)
    
    if current_question or current_answer:
        qa_pairs.append({
            'question': '\n'.join(current_question).strip(),
            'answer': '\n'.join(current_answer).strip()
        })
    
    return qa_pairs

def categorize_question(question):
    """对问题进行分类"""
    categories = {
        '编程开发': ['编程', '代码', 'Python', 'Java', 'JavaScript', '前端', '后端', '算法', '数据结构', 'API', '接口', '框架'],
        '人工智能': ['AI', '机器学习', '深度学习', '神经网络', '大模型', 'GPT', '豆包', 'ChatGPT'],
        '数据分析': ['数据分析', '数据挖掘', 'SQL', 'Excel', '数据可视化', '图表'],
        '系统运维': ['Linux', '服务器', 'Docker', 'Kubernetes', '运维', '部署', '配置'],
        '网络安全': ['安全', '加密', '漏洞', '渗透', '防护'],
        '办公效率': ['Excel', 'Word', 'PPT', '效率', '快捷键', '自动化'],
        '教育学习': ['学习', '课程', '考试', '考研', '高考', '知识'],
        '生活问题': ['生活', '健康', '饮食', '旅游', '购物', '情感'],
        '技术咨询': ['技术', '问题', '如何', '怎么', '什么', '为什么'],
        '其他': []
    }
    
    for category, keywords in categories.items():
        if category == '其他':
            continue
        for keyword in keywords:
            if keyword.lower() in question.lower():
                return category
    
    return '其他'

def analyze_files():
    """遍历所有markdown文件进行分析"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    md_files = [f for f in os.listdir(MARKDOWN_DIR) if f.endswith('.md')]
    total_files = len(md_files)
    
    print(f"📁 发现 {total_files} 个markdown文件")
    
    all_qa_pairs = []
    category_stats = defaultdict(int)
    file_results = []
    
    save_interval = 50
    batch_count = 0
    
    for idx, filename in enumerate(md_files, 1):
        if idx % 10 == 0:
            print(f"⏳ 正在处理第 {idx}/{total_files} 个文件: {filename}")
        
        file_path = os.path.join(MARKDOWN_DIR, filename)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            qa_pairs = extract_qa_pairs(content)
            
            for pair in qa_pairs:
                if not pair['question'] and not pair['answer']:
                    continue
                
                category = categorize_question(pair['question'])
                category_stats[category] += 1
                
                all_qa_pairs.append({
                    'filename': filename,
                    'category': category,
                    'question': pair['question'],
                    'answer': pair['answer']
                })
            
            file_results.append({
                'filename': filename,
                'qa_count': len(qa_pairs),
                'categories': list(set([categorize_question(p['question']) for p in qa_pairs]))
            })
            
            if idx % save_interval == 0:
                batch_count += 1
                print(f"📥 保存第 {batch_count} 批中间结果...")
                
                batch_data = {
                    'batch': batch_count,
                    'processed_files': idx,
                    'total_files': total_files,
                    'qa_pairs': all_qa_pairs[-save_interval*10:],
                    'stats': dict(category_stats)
                }
                
                with open(os.path.join(OUTPUT_DIR, f"batch_{batch_count}.json"), 'w', encoding='utf-8') as f:
                    json.dump(batch_data, f, ensure_ascii=False, indent=2)
        
        except Exception as e:
            print(f"❌ 处理 {filename} 失败: {e}")
    
    print(f"\n📊 统计结果:")
    for category, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {category}: {count} 条")
    
    with open(os.path.join(OUTPUT_DIR, "all_qa_pairs.json"), 'w', encoding='utf-8') as f:
        json.dump(all_qa_pairs, f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(OUTPUT_DIR, "file_results.json"), 'w', encoding='utf-8') as f:
        json.dump(file_results, f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(OUTPUT_DIR, "category_stats.json"), 'w', encoding='utf-8') as f:
        json.dump(dict(category_stats), f, ensure_ascii=False, indent=2)
    
    generate_summary(all_qa_pairs, category_stats)
    
    print(f"\n🎉 分析完成！结果已保存到 {OUTPUT_DIR}")

def generate_summary(all_qa_pairs, category_stats):
    """生成汇总报告"""
    summary = f"# 豆包聊天记录分析汇总\n\n"
    summary += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    summary += f"总问答对数: {len(all_qa_pairs)}\n"
    summary += f"分类数量: {len(category_stats)}\n\n"
    
    summary += "## 分类统计\n\n"
    summary += "| 分类 | 数量 | 占比 |\n"
    summary += "|------|------|------|\n"
    total = sum(category_stats.values())
    for category, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
        percentage = f"{(count / total * 100):.1f}"
        summary += f"| {category} | {count} | {percentage}% |\n"
    
    summary += "\n## 各分类问题示例\n\n"
    for category in sorted(category_stats.keys()):
        category_pairs = [p for p in all_qa_pairs if p['category'] == category]
        summary += f"### {category}\n\n"
        
        for i, pair in enumerate(category_pairs[:3], 1):
            question = pair['question'][:100] + '...' if len(pair['question']) > 100 else pair['question']
            answer = pair['answer'][:150] + '...' if len(pair['answer']) > 150 else pair['answer']
            summary += f"**Q{i}:** {question}\n\n"
            summary += f"**A{i}:** {answer}\n\n"
    
    with open(os.path.join(OUTPUT_DIR, "汇总报告.md"), 'w', encoding='utf-8') as f:
        f.write(summary)

def generate_category_reports(all_qa_pairs):
    """按分类生成详细报告"""
    categories = defaultdict(list)
    
    for pair in all_qa_pairs:
        categories[pair['category']].append(pair)
    
    for category, pairs in categories.items():
        report = f"# {category}\n\n"
        report += f"问答数量: {len(pairs)}\n\n"
        
        for i, pair in enumerate(pairs, 1):
            report += f"## {i}. {pair['filename']}\n\n"
            report += f"**问题:** {pair['question']}\n\n"
            report += f"**回答:**\n\n{pair['answer']}\n\n"
            report += "---\n\n"
        
        safe_category = re.sub(r'[\\/:*?"<>|]', '_', category)
        with open(os.path.join(OUTPUT_DIR, f"分类_{safe_category}.md"), 'w', encoding='utf-8') as f:
            f.write(report)

if __name__ == "__main__":
    analyze_files()
    
    with open(os.path.join(OUTPUT_DIR, "all_qa_pairs.json"), 'r', encoding='utf-8') as f:
        all_qa_pairs = json.load(f)
    
    generate_category_reports(all_qa_pairs)
    
    print("📋 分类报告已生成！")