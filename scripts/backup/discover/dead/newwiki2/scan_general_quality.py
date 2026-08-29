import os
import re
import json
from pathlib import Path

BASE_DIR = Path(r"h:\github\cowkb\discover\newwiki2\general")

def count_chinese_chars(text):
    return len(re.findall(r'[\u4e00-\u9fff]', text))

def count_words(text):
    chinese = count_chinese_chars(text)
    english = len(re.findall(r'[a-zA-Z]+', text))
    return chinese + english

def count_tables(text):
    lines = text.split('\n')
    table_count = 0
    in_table = False
    for line in lines:
        if '|' in line and re.match(r'^\s*\|.*\|\s*$', line):
            if not in_table:
                in_table = True
                table_count += 1
        else:
            in_table = False
    return table_count

def count_code_blocks(text):
    return len(re.findall(r'```[\s\S]*?```', text))

def extract_quality_level(text):
    match = re.search(r'quality_level:\s*(\S+)', text)
    if match:
        return match.group(1)
    return '未知'

def extract_frontmatter(text):
    if text.startswith('---'):
        end = text.find('---', 3)
        if end != -1:
            fm = text[3:end]
            result = {}
            for line in fm.split('\n'):
                line = line.strip()
                if ':' in line:
                    key, val = line.split(':', 1)
                    result[key.strip()] = val.strip()
            return result
    return {}

def classify_topic(filename, tags_str):
    tags = tags_str.lower() if tags_str else ''
    name = filename.lower()
    
    tech_keywords = ['cap', 'ssd', 'uefi', 'swiglu', 'mapreduce', '分布式', '数据中心', 
                     '自动驾驶', '图像识别', 'nbd', 'html', 'mermaid', 'ppt', 'cmu',
                     'github', 'harness', 'meta', '消息队列', '机器人', '智能运维',
                     '数据分析', '产生式规则', '低功耗', '铠侠', '阿里云', '讯飞',
                     '超智能']
    
    mgmt_keywords = ['企业经营', '系统论', '飞轮效应', '开源组件', '快速读懂', 
                     '高质量信息', '深度分析', '独立观点', '辩证法', '递归',
                     '解构思维', '历史思维', '工作流', '角色适应', '软件与团队',
                     '达人管理', '多设备数据']
    
    history_law_keywords = ['商君书', '松锦之战', '新中国主权', '洞穴奇案', '电车难题',
                            '未成年打工', '法律知识', '中美治理', '哈勃张力']
    
    life_keywords = ['上海到南京', '杭州至上海', '杭州苏州', '拼多多', '知乎',
                     '政策', '普查数据', '生态整合', '精确率', '认知托付',
                     '社会进步', '股研发', '研发行业', '支撑岗', '人生管道',
                     '从无所事事', '模糊数学', '架空历史', '附件链接', '链接解析',
                     '动态适配']
    
    for kw in tech_keywords:
        if kw in filename or kw in tags:
            return '技术类'
    
    for kw in mgmt_keywords:
        if kw in filename or kw in tags:
            return '管理/方法论类'
    
    for kw in history_law_keywords:
        if kw in filename or kw in tags:
            return '历史/法律/社会类'
    
    for kw in life_keywords:
        if kw in filename or kw in tags:
            return '生活/笔记类'
    
    return '其他'

def assess_quality(word_count, table_count, has_architecture, sections_count):
    if word_count >= 2500 and table_count >= 2 and sections_count >= 5:
        return 'A级'
    elif word_count >= 1500 and table_count >= 1 and sections_count >= 3:
        return 'B级'
    elif word_count >= 800:
        return 'C级'
    else:
        return 'D级'

def count_sections(text):
    return len(re.findall(r'^##\s+', text, re.MULTILINE))

def has_architecture_diagram(text):
    return '```mermaid' in text or '┌───' in text or '├───' in text or 'graph ' in text

def main():
    files_data = []
    
    for md_file in sorted(BASE_DIR.glob('*.md')):
        if md_file.name == 'index.md':
            continue
            
        try:
            text = md_file.read_text(encoding='utf-8')
        except Exception as e:
            print(f"读取失败: {md_file.name}, {e}")
            continue
        
        fm = extract_frontmatter(text)
        wc = count_words(text)
        tc = count_tables(text)
        cb = count_code_blocks(text)
        secs = count_sections(text)
        has_arch = has_architecture_diagram(text)
        topic = classify_topic(md_file.stem, fm.get('tags', ''))
        fm_quality = extract_quality_level(text)
        calc_quality = assess_quality(wc, tc, has_arch, secs)
        
        files_data.append({
            'filename': md_file.name,
            'title': fm.get('title', md_file.stem),
            'word_count': wc,
            'table_count': tc,
            'code_blocks': cb,
            'sections': secs,
            'has_architecture': has_arch,
            'topic': topic,
            'fm_quality': fm_quality,
            'calc_quality': calc_quality,
            'tags': fm.get('tags', '')
        })
    
    print(f"共扫描 {len(files_data)} 个文件\n")
    
    by_topic = {}
    for f in files_data:
        t = f['topic']
        if t not in by_topic:
            by_topic[t] = []
        by_topic[t].append(f)
    
    print("=== 按主题分类 ===")
    for topic, files in sorted(by_topic.items()):
        print(f"{topic}: {len(files)} 个")
    print()
    
    by_quality = {}
    for f in files_data:
        q = f['calc_quality']
        if q not in by_quality:
            by_quality[q] = []
        by_quality[q].append(f)
    
    print("=== 按质量分级（计算值） ===")
    for q in ['A级', 'B级', 'C级', 'D级']:
        if q in by_quality:
            avg_wc = sum(f['word_count'] for f in by_quality[q]) / len(by_quality[q])
            print(f"{q}: {len(by_quality[q])} 个，平均字数 {avg_wc:.0f}")
    print()
    
    total_wc = sum(f['word_count'] for f in files_data)
    total_tc = sum(f['table_count'] for f in files_data)
    total_arch = sum(1 for f in files_data if f['has_architecture'])
    
    print(f"总字数: {total_wc}")
    print(f"总表格数: {total_tc}")
    print(f"有架构图的文件数: {total_arch}")
    print()
    
    print("=== 各质量等级文件列表 ===")
    for q in ['D级', 'C级', 'B级', 'A级']:
        if q in by_quality:
            print(f"\n{q} ({len(by_quality[q])}个):")
            for f in sorted(by_quality[q], key=lambda x: x['word_count']):
                print(f"  {f['filename']:30s} {f['word_count']:5d}字 {f['table_count']}表 {f['topic']}")
    
    with open(BASE_DIR.parent / 'general_quality_scan.json', 'w', encoding='utf-8') as f:
        json.dump(files_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n详细数据已保存到 general_quality_scan.json")

if __name__ == '__main__':
    main()
