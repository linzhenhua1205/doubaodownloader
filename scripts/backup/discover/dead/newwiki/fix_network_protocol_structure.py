import os
import re

wiki_dir = r"h:\github\cowkb\discover\newwiki"
filename = '其他_网络协议.md'
filepath = os.path.join(wiki_dir, filename)

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
new_lines = []
in_first_section = False
first_section_title_found = False

for line in lines:
    if line.startswith('## 🌐 深度增强：'):
        in_first_section = True
        continue
    
    if in_first_section and line.startswith('### 一、'):
        first_section_title_found = True
        new_lines.append('## 一、知识体系全景图')
        continue
    
    if in_first_section and line.startswith('### 二、'):
        new_lines.append('## 二、核心知识深度解析')
        continue
    
    if in_first_section and line.startswith('### 三、'):
        new_lines.append('## 三、丰富对比表格')
        continue
    
    if in_first_section and line.startswith('### 四、'):
        new_lines.append('## 四、选型决策框架')
        continue
    
    if in_first_section and line.startswith('### 五、'):
        new_lines.append('## 五、2025-2026 最新进展')
        continue
    
    if in_first_section and line.startswith('### 六、'):
        new_lines.append('## 六、企业级案例与最佳实践')
        continue
    
    if in_first_section and line.startswith('### 七、'):
        new_lines.append('## 七、学习路径与成长路线')
        continue
    
    if line.startswith('## 八、'):
        in_first_section = False
    
    new_lines.append(line)

new_content = '\n'.join(new_lines)

char_count = len(new_content)
fm_lines = new_content.split('\n')
in_fm = False
fm_end = -1
for i, line in enumerate(fm_lines):
    if line.startswith('---'):
        if not in_fm:
            in_fm = True
        else:
            fm_end = i
            break

if fm_end > 0:
    for i in range(1, fm_end):
        if fm_lines[i].startswith('word_count:'):
            fm_lines[i] = f'word_count: 约{char_count:,}字'
            break

new_content = '\n'.join(fm_lines)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)

h2_count = len(re.findall(r'^## .+$', new_content, re.MULTILINE))
print(f"修正完成")
print(f"二级章节数: {h2_count}")
print(f"总字数: {char_count:,}")
