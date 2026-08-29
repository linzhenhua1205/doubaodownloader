import os
import re
import json

def analyze_file(filepath):
    """分析单个文件的质量状态"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    result = {
        'filename': os.path.basename(filepath),
        'filepath': filepath,
        'frontmatter': {},
        'word_count': 0,
        'is_template': False,
        'template_indicators': [],
        'real_tables': 0,
        'has_real_content': False
    }
    
    # 提取 frontmatter
    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if fm_match:
        fm_content = fm_match.group(1)
        for line in fm_content.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                result['frontmatter'][key.strip()] = value.strip()
    
    # 计算正文字数（去掉frontmatter）
    body = content
    if fm_match:
        body = content[fm_match.end():]
    
    # 去掉代码块
    body_no_code = re.sub(r'```.*?```', '', body, flags=re.DOTALL)
    # 去掉markdown标记
    body_clean = re.sub(r'[#*|\-\[\]()>_`]', '', body_no_code)
    # 统计中文字数
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', body_clean)
    result['word_count'] = len(chinese_chars)
    
    # 检测模板化内容
    template_patterns = [
        ('方案A|方案B|方案C|方案D', '通用方案占位符'),
        ('基础概念.*?核心原理.*?技术实践.*?前沿发展', '四象限模板'),
        ('定义分类.*?发展历程.*?工作机制.*?关键技术.*?应用场景.*?最佳实践.*?最新趋势.*?未来展望', '通用模板结构'),
        ('是一个重要的技术/管理领域', '模板化描述'),
        ('体系化思维.*?实践指导.*?效率提升.*?持续进化', '模板化价值点'),
        ('入门级、简单场景|主流场景、平衡选择|高性能、大规模场景|快速验证、原型开发', '模板化场景描述'),
        ('选型决策框架', '有选型框架但可能是模板'),
        ('原始内容归档', '有原始内容归档标记'),
        ('7大模块', '7大模块标记'),
        ('深度增强完成', '状态标记'),
    ]
    
    for pattern, indicator in template_patterns:
        if re.search(pattern, body, re.DOTALL):
            result['template_indicators'].append(indicator)
    
    # 检测真实表格数量（排除模板表格）
    table_count = len(re.findall(r'\n\|.*?\|.*?\|\n\|[-:| ]+\|\n', body))
    # 检测模板表格
    template_table_count = len(re.findall(r'方案A.*?方案B.*?方案C', body))
    result['real_tables'] = max(0, table_count - template_table_count)
    
    # 判断是否为模板化文件
    if len(result['template_indicators']) >= 4 or '方案A|方案B|方案C|方案D' in result['template_indicators']:
        result['is_template'] = True
    
    # 判断是否有真实内容（根据关键词密度和实际内容）
    # 检查是否有具体的技术术语、产品名等
    real_content_indicators = [
        r'Kotlin|Java|Jetpack|Compose',  # Android具体技术
        r'Python|GIL|JIT|CPython',  # Python具体技术
        r'丰田|亚马逊|苹果|Shein|JIT|精益|六西格玛',  # 供应链具体内容
        r'React|Vue|Angular|Svelte|Solid',  # 前端框架
        r'特斯拉|Waymo|百度|小鹏|华为|L\d',  # 自动驾驶
    ]
    
    for pattern in real_content_indicators:
        if re.search(pattern, body, re.IGNORECASE):
            result['has_real_content'] = True
            break
    
    # 如果字数少且有多个模板指标，视为模板
    if result['word_count'] < 800 and len(result['template_indicators']) >= 3:
        result['is_template'] = True
    
    return result

def main():
    dir_path = r'h:\github\cowkb\discover\newwiki2\programming'
    files = [f for f in os.listdir(dir_path) if f.endswith('.md') and f != 'index.md']
    
    results = []
    for filename in sorted(files):
        filepath = os.path.join(dir_path, filename)
        result = analyze_file(filepath)
        results.append(result)
    
    # 分类
    template_files = [r for r in results if r['is_template']]
    real_files = [r for r in results if not r['is_template'] and r['has_real_content']]
    unknown_files = [r for r in results if not r['is_template'] and not r['has_real_content']]
    
    print("=" * 80)
    print(f"文件总数: {len(results)}")
    print(f"模板化文件: {len(template_files)}")
    print(f"真实增强文件: {len(real_files)}")
    print(f"待确认文件: {len(unknown_files)}")
    print("=" * 80)
    
    print("\n📋 模板化文件列表（需要增强）:")
    print("-" * 80)
    for r in sorted(template_files, key=lambda x: x['filename']):
        quality = r['frontmatter'].get('quality_level', 'N/A')
        wc = r['frontmatter'].get('word_count', 'N/A')
        print(f"  {r['filename']:<30} 自评:{quality:<3} 声称字数:{wc:<10} 实际:{r['word_count']}字 指标:{len(r['template_indicators'])}个")
    
    print("\n✅ 真实增强文件列表:")
    print("-" * 80)
    for r in sorted(real_files, key=lambda x: x['filename']):
        quality = r['frontmatter'].get('quality_level', 'N/A')
        wc = r['frontmatter'].get('word_count', 'N/A')
        print(f"  {r['filename']:<30} 自评:{quality:<3} 声称字数:{wc:<10} 实际:{r['word_count']}字")
    
    print("\n❓ 待确认文件列表:")
    print("-" * 80)
    for r in sorted(unknown_files, key=lambda x: x['filename']):
        quality = r['frontmatter'].get('quality_level', 'N/A')
        wc = r['frontmatter'].get('word_count', 'N/A')
        print(f"  {r['filename']:<30} 自评:{quality:<3} 声称字数:{wc:<10} 实际:{r['word_count']}字")
    
    # 保存详细结果
    with open(r'h:\github\cowkb\discover\newwiki2\file_analysis.json', 'w', encoding='utf-8') as f:
        json.dump({
            'summary': {
                'total': len(results),
                'template': len(template_files),
                'real': len(real_files),
                'unknown': len(unknown_files)
            },
            'template_files': [r['filename'] for r in template_files],
            'real_files': [r['filename'] for r in real_files],
            'unknown_files': [r['filename'] for r in unknown_files],
            'details': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n详细分析结果已保存到: file_analysis.json")

if __name__ == '__main__':
    main()
