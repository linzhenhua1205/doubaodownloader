import os
import re
import json
from collections import defaultdict
from datetime import datetime

MARKDOWN_DIR = "h:/github/md/doubao_batch_export/markdown"
OUTPUT_DIR = "h:/github/md/analysis_results_v4"

def clean_content(content):
    lines = content.split('\n')
    cleaned_lines = []
    
    nav_patterns = [
        '^New Chat$', '^Chat History$', '^存储设备参数信息提供$',
        '^Chat2File 工具介绍$', '^组织内能力差异化$', '^服务器L1-L12分级体系介绍$',
        '^复杂系统理论补充还原论不足$', '^服务器行业深度分析$', '^逻辑分析在复杂问题中的应用方法$',
        '^刀箱服务器硬件框架介绍$', '^根据附件扩写内容$', '^服务器竞争力及 ROI 评估$',
        '^CNCF项目及应用场景$', '^服务器整机研发规划$', '^多元知识问答与资讯解读$',
        '^用数据指标衡量市场预期变化$', '^Mobile Chats$', '^认知科学解释短期与长期记忆差异$',
        '^人工智能对软件开发流程的变革$', '^华为韬定律技术路线解读$', '^STAR法则描述创新点教程$',
        '^NLP推动LLM发展$', '^HAMi vGPU虚拟化调度系统介绍$', '^用辩证法分析复杂问题的方法$',
        '^个人对话画像生成$', '^逻辑漏洞对决策质量的影响$', '^SQLite数据库管理工具推荐$',
        '^开源项目吸引贡献者的方法$', '^游戏科技树经典设计模式$', '^代码审核优化代码质量方法$',
        '^事件驱动架构与观察者模式的联系$', '^人类信息存储的古今演变$', '^Python 库和模块的区别$',
        '^flashnet$', '^Deep Research$', '^Generate Slides$', '^Help Me Write$',
        '^\\d+ sources?$'
    ]
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        is_nav = False
        for pattern in nav_patterns:
            if re.match(pattern, line):
                is_nav = True
                break
        
        if not is_nav:
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def extract_title_and_content(content):
    lines = content.split('\n')
    title = ""
    body_lines = []
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('# ') and not title:
            title = line[2:].strip()
            continue
        
        if line.startswith('来源链接:'):
            continue
        
        body_lines.append(line)
    
    body = '\n'.join(body_lines).strip()
    
    if not title:
        title = "未命名"
    
    return title, body

def categorize_content(title, body):
    full_text = (title + ' ' + body).lower()
    
    categories = [
        {
            'name': '人文社科',
            'keywords': [
                '哲学', '历史', '社会', '文化', '伦理', '道德', '政治',
                '经济', '心理', '教育', '文学', '艺术', '思想', '价值',
                '意义', '人性', '社会变革', '文明', '文化传承', '辩证',
                '批判', '思维', '逻辑', '认知', '知识', '智慧', '信仰',
                '传统', '现代', '后现代', '存在', '自由', '平等', '正义',
                '权力', '阶级', '阶层', '民族', '国家', '国际', '全球化'
            ],
            'required_count': 1
        },
        {
            'name': '人工智能',
            'keywords': [
                'ai', '机器学习', '深度学习', '神经网络', '大模型', 'gpt',
                'chatgpt', 'llm', '自然语言', 'nlp', '计算机视觉', '强化学习',
                '模型训练', '推理', '微调', 'prompt', '智能体', 'agent', 'rag',
                'embedding', '向量数据库', '生成式', '多模态', 'prompt',
                'token', 'transformer', 'bert', 'diffusion', 'stable diffusion',
                'midjourney', 'claude', 'gemini', 'doubao', '文心一言', '通义千问'
            ],
            'required_count': 1
        },
        {
            'name': '服务器研发',
            'keywords': [
                'bmc', '固件', '主板', '芯片', '板卡', '机箱', '电源',
                '散热', '液冷', 'bios', 'uefi', '固件开发', '硬件开发',
                '服务器研发', '刀箱', '节点', '集群', '算力', '智算',
                '数据中心', 'gpu服务器', 'ai服务器', 'inspur', '浪潮',
                'huawei', '华为', 'intel', 'amd', 'nvidia', 'gpu', 'cpu',
                'pcie', 'nvme', 'ssd', '内存', 'ddr', '存储', 'raid'
            ],
            'required_count': 2
        },
        {
            'name': '编程开发',
            'keywords': [
                '编程', '代码', 'python', 'java', 'javascript', '前端', '后端',
                '算法', '数据结构', 'api', '接口', '框架', 'github', 'git',
                'npm', 'docker', 'kubernetes', 'linux', 'shell', '脚本',
                '编译器', '调试', 'bug', '代码审查', '测试', '开发',
                '数据库', 'sql', 'redis', 'mongodb', 'mysql', 'postgresql',
                'react', 'vue', 'angular', 'spring', 'django', 'flask',
                'rust', 'go', 'typescript', 'node', 'webpack', 'vite'
            ],
            'required_count': 2
        },
        {
            'name': '系统运维',
            'keywords': [
                '运维', '部署', '配置', '监控', '日志', '性能', '优化',
                '网络', '服务器管理', '自动化', '监控系统', '告警',
                '故障排查', '灾备', '备份', '恢复', 'kubernetes', 'docker',
                'prometheus', 'grafana', 'elk', 'jenkins', 'ci/cd', 'devops'
            ],
            'required_count': 2
        },
        {
            'name': '商业管理',
            'keywords': [
                '企业', '商业', '管理', '运营', '市场', '营销', '产品',
                '战略', '财务', '投资', '创业', '职场', '团队', '效率',
                '领导力', '管理方法', '商业模式', '竞争', '战略规划',
                'gtm', 'sales', 'marketing', 'product', 'ceo', 'cio', 'cto'
            ],
            'required_count': 2
        },
        {
            'name': '数据分析',
            'keywords': [
                '数据分析', '数据挖掘', 'sql', 'excel', '数据可视化', '图表',
                '数据仓库', 'etl', 'bi', '报表', '大数据', 'hadoop', 'spark',
                '统计', '建模', '预测', '洞察', '数据治理', 'python数据分析',
                'pandas', 'numpy', 'matplotlib', 'seaborn', 'tableau', 'powerbi'
            ],
            'required_count': 2
        },
        {
            'name': '网络安全',
            'keywords': [
                '安全', '加密', '漏洞', '渗透', '防护', '黑客', '攻击',
                '防火墙', '认证', '授权', '隐私', '合规', '风险', '威胁',
                'cyber', 'security', 'pentest', 'ctf', 'waf', 'ids', 'ips',
                'vpn', 'ssl', 'tls', '零信任'
            ],
            'required_count': 2
        },
        {
            'name': '科技资讯',
            'keywords': [
                '发布', '新品', '技术', '趋势', '会议', '峰会', '财报',
                '市场', '分析', '评测', '行业动态', '技术进展', '新闻',
                '发布时间', '来源', '报告', '研究', '调查', '白皮书',
                'ces', 'mwc', 'computex', 'wwdc', 'google i/o'
            ],
            'required_count': 2
        },
        {
            'name': '办公效率',
            'keywords': [
                'excel', 'word', 'ppt', '效率', '快捷键', '自动化', '文档',
                '报告', '会议', '项目管理', '飞书', '钉钉', '协作', '工具',
                'notion', 'obsidian', 'slack', 'trello', 'jira', 'confluence'
            ],
            'required_count': 2
        },
        {
            'name': '生活问题',
            'keywords': [
                '生活', '健康', '饮食', '旅游', '购物', '情感', '日常',
                '家庭', '兴趣', '爱好', '休闲', '美食', '运动', '健身',
                '读书', '电影', '音乐', '旅行', '摄影', '手工', '宠物'
            ],
            'required_count': 2
        }
    ]
    
    scores = []
    for cat in categories:
        count = sum(1 for kw in cat['keywords'] if kw in full_text)
        if count >= cat['required_count']:
            scores.append((cat['name'], count))
    
    if not scores:
        return '其他'
    
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[0][0]

def analyze_files():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    md_files = [f for f in os.listdir(MARKDOWN_DIR) if f.endswith('.md')]
    total_files = len(md_files)
    
    print(f"📁 发现 {total_files} 个markdown文件")
    
    all_records = []
    category_stats = defaultdict(int)
    misclassified = []
    
    save_interval = 50
    batch_count = 0
    
    for idx, filename in enumerate(md_files, 1):
        if idx % 50 == 0:
            print(f"⏳ 正在处理第 {idx}/{total_files} 个文件: {filename}")
        
        file_path = os.path.join(MARKDOWN_DIR, filename)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            title, body = extract_title_and_content(content)
            cleaned_body = clean_content(body)
            
            if not cleaned_body:
                continue
            
            category = categorize_content(title, cleaned_body)
            category_stats[category] += 1
            
            record = {
                'filename': filename,
                'title': title,
                'category': category,
                'content': cleaned_body[:3000]
            }
            
            all_records.append(record)
            
            if category == '服务器研发' and '服务器' not in title.lower():
                misclassified.append({
                    'filename': filename,
                    'title': title,
                    'content_preview': cleaned_body[:100]
                })
            
            if idx % save_interval == 0:
                batch_count += 1
                print(f"📥 保存第 {batch_count} 批中间结果...")
                
                batch_data = {
                    'batch': batch_count,
                    'processed_files': idx,
                    'total_files': total_files,
                    'records': all_records[-save_interval*10:],
                    'stats': dict(category_stats)
                }
                
                with open(os.path.join(OUTPUT_DIR, f"batch_{batch_count}.json"), 'w', encoding='utf-8') as f:
                    json.dump(batch_data, f, ensure_ascii=False, indent=2)
        
        except Exception as e:
            print(f"❌ 处理 {filename} 失败: {e}")
    
    print(f"\n📊 统计结果:")
    total = sum(category_stats.values())
    for category, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
        percentage = f"{(count / total * 100):.1f}"
        print(f"  {category}: {count} 条 ({percentage}%)")
    
    print(f"\n⚠️ 可能误分类为服务器研发的文件（标题不含服务器）: {len(misclassified)} 个")
    
    with open(os.path.join(OUTPUT_DIR, "all_records.json"), 'w', encoding='utf-8') as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(OUTPUT_DIR, "category_stats.json"), 'w', encoding='utf-8') as f:
        json.dump(dict(category_stats), f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(OUTPUT_DIR, "misclassified.json"), 'w', encoding='utf-8') as f:
        json.dump(misclassified, f, ensure_ascii=False, indent=2)
    
    generate_summary(all_records, category_stats)
    generate_category_reports(all_records)
    
    print(f"\n🎉 分析完成！结果已保存到 {OUTPUT_DIR}")

def generate_summary(all_records, category_stats):
    summary = f"# 豆包聊天记录分析汇总\n\n"
    summary += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    summary += f"总记录数: {len(all_records)}\n"
    summary += f"分类数量: {len(category_stats)}\n\n"
    
    summary += "## 分类统计\n\n"
    summary += "| 分类 | 数量 | 占比 |\n"
    summary += "|------|------|------|\n"
    total = sum(category_stats.values())
    for category, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
        percentage = f"{(count / total * 100):.1f}"
        summary += f"| {category} | {count} | {percentage}% |\n"
    
    summary += "\n## 各分类内容示例\n\n"
    for category in sorted(category_stats.keys()):
        category_records = [r for r in all_records if r['category'] == category]
        summary += f"### {category}\n\n"
        
        for i, record in enumerate(category_records[:3], 1):
            title = record['title'][:60] + '...' if len(record['title']) > 60 else record['title']
            content = record['content'][:200] + '...' if len(record['content']) > 200 else record['content']
            summary += f"**{i}. {title}**\n\n"
            summary += f"{content}\n\n"
    
    with open(os.path.join(OUTPUT_DIR, "汇总报告.md"), 'w', encoding='utf-8') as f:
        f.write(summary)

def generate_category_reports(all_records):
    categories = defaultdict(list)
    
    for record in all_records:
        categories[record['category']].append(record)
    
    for category, records in categories.items():
        report = f"# {category}\n\n"
        report += f"记录数量: {len(records)}\n\n"
        
        for i, record in enumerate(records, 1):
            report += f"## {i}. {record['title']}\n\n"
            report += f"**来源文件:** {record['filename']}\n\n"
            report += f"**内容:**\n\n{record['content']}\n\n"
            report += "---\n\n"
        
        safe_category = re.sub(r'[\\/:*?"<>|]', '_', category)
        with open(os.path.join(OUTPUT_DIR, f"分类_{safe_category}.md"), 'w', encoding='utf-8') as f:
            f.write(report)

if __name__ == "__main__":
    analyze_files()