import os
import re
import json

dir_path = r'h:\github\cowkb\discover\newwiki2\programming'
output_dir = r'h:\github\cowkb\discover\newwiki2\original_contents'

os.makedirs(output_dir, exist_ok=True)

template_files = [
    '01-ai-pair-programming.md',
    '02-software-architecture-patterns.md',
    '03-lachat-architecture.md',
    'aidc.md',
    'ipd.md',
    'paperclip.md',
    'rise.md',
    'sherwood.md',
    'ubuntutoucho.md',
    'windows.md',
    '三体阅读心境.md',
    '业智方舟.md',
    '产品力量理论.md',
    '企业周均工时.md',
    '企业系统演化.md',
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
    '服务器软件趋.md',
    '生产标物料转.md',
    '知乎文章无法.md',
    '股权.md',
    '螺旋模型优化.md',
    '行人路权受侵.md',
    '解构思维解决.md',
    '认知托付框架.md',
    '讯飞星辰.md',
    '超智能与未来.md',
    '链接解析失败.md',
    '阿里云光模块.md',
    '阿里云王坚.md',
    '附件链接失效.md',
]

results = {}

for filename in template_files:
    filepath = os.path.join(dir_path, filename)
    if not os.path.exists(filepath):
        print(f"文件不存在: {filename}")
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取 frontmatter
    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    frontmatter = {}
    if fm_match:
        fm_content = fm_match.group(1)
        for line in fm_content.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()
    
    # 提取原始内容归档部分
    # 找到 "## 8. 原始内容归档" 或类似标题，然后从下一个 ## 开始到文件末尾
    original_content = ''
    
    # 方法1: 找到"原始内容归档"章节，然后提取该章节之后的所有内容
    pattern = r'## .*原始内容.*?\n(.*)'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        section_content = match.group(1).strip()
        # 去掉开头的引用标记和空行
        lines = section_content.split('\n')
        # 跳过前面的引用行和空行
        start_idx = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not stripped.startswith('>') and stripped != '---':
                start_idx = i
                break
        
        original_content = '\n'.join(lines[start_idx:]).strip()
    
    results[filename] = {
        'frontmatter': frontmatter,
        'original_content': original_content,
        'original_length': len(original_content),
        'has_original': bool(original_content) and len(original_content) > 200
    }
    
    # 保存原始内容到单独文件
    if original_content and len(original_content) > 200:
        out_file = os.path.join(output_dir, filename)
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(original_content)

# 统计
has_original = sum(1 for r in results.values() if r['has_original'])
no_original = sum(1 for r in results.values() if not r['has_original'])

print(f"模板化文件总数: {len(template_files)}")
print(f"有原始内容的文件: {has_original}")
print(f"无/少原始内容的文件: {no_original}")

print("\n有原始内容的文件（按字数排序）:")
sorted_files = sorted(results.items(), key=lambda x: x[1]['original_length'], reverse=True)
for filename, data in sorted_files:
    if data['has_original']:
        print(f"  {filename:<30} {data['original_length']:>5} 字")

print("\n无/少原始内容的文件列表:")
for filename, data in sorted_files:
    if not data['has_original']:
        print(f"  {filename:<30} {data['original_length']:>5} 字")

# 保存详细结果
with open(os.path.join(output_dir, '_summary.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n原始内容已保存到: {output_dir}")
