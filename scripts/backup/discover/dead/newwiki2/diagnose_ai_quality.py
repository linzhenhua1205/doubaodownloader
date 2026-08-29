# -*- coding: utf-8 -*-
"""
精准识别需要质量提升的文件
识别标准：
1. 知识索引页（内容空洞，有大量笔记链接）
2. 含模板化占位内容
3. frontmatter 自评虚高
4. 真实内容质量不足
"""
import os
import re
import json
from pathlib import Path

BASE_DIR = Path(r"h:\github\cowkb\discover\newwiki2")

FILES_TO_PROCESS = {
    "AI-模型架构": [
        "auth.md", "container.md", "cpu.md", "database.md", "docker.md",
        "java.md", "linux.md", "memory.md", "model.md", "network.md",
        "nvidia.md", "paper.md", "pcie.md", "prompt.md", "python.md",
        "research.md", "security.md", "server.md", "sql.md", "storage.md"
    ],
    "AI-训练微调": [
        "container.md", "cpu.md", "java.md", "kernel.md", "linux.md",
        "memory.md", "nvidia.md", "pcie.md", "prompt.md", "rag.md", "sql.md"
    ],
    "AI-Agent": [
        "archon.md", "cloudagentv.md", "cowagent.md", "coze.md",
        "feishucozero.md", "freespirepdf.md", "gartner.md", "gpu.md",
        "hermes.md", "isc.md", "linkai.md", "nanobot.md", "nvidia.md",
        "openbmc.md", "pcie.md", "prompt.md", "python.md", "rag.md",
        "zabbixai.md", "业务.md", "扣子应用与智.md", "维保备件动态.md",
        "股市.md", "运维体系分析.md", "飞书.md", "飞书知识库与.md", "高盛.md"
    ],
    "ai-models": [
        "amd.md", "archon.md", "claude.md", "claudecode.md", "claudecodesk.md",
        "codebuddy.md", "codegraph.md", "cowagent.md", "deep.md", "deepclaude.md",
        "deepseektui.md", "deepseekv.md", "ecdc.md", "gartner.md", "github.md",
        "hermesagent.md", "https.md", "mvc.md", "nvidia.md", "omc.md", "open.md",
        "openbmc.md", "openclaw.md", "patronusai.md", "superpowers.md",
        "tinyclaw.md", "trae.md", "中国.md", "书籍问答零幻.md", "企业.md",
        "分布式一致性.md", "国产.md", "大模型.md", "大规模推理与.md",
        "显卡.md", "服务器设备制.md", "李萌.md", "架构思维在分.md",
        "生成式.md", "突破.md", "股票.md", "英伟达开源模.md",
        "赋能固件研发.md", "过去两周.md", "运营商.md", "魔搭与扣子对.md",
        "华为.md", "字节阿里腾讯.md", "开源模型本地.md", "影响.md",
        "批判性思维避.md", "提升大模型回.md", "数据训练对.md",
        "时代.md", "大模型训练平.md", "大模型架构师.md", "anthropic.md",
        "codereviewag.md", "genai.md", "mfu.md", "nlp.md", "tokens.md"
    ]
}


def parse_frontmatter(content):
    if not content.startswith('---'):
        return {}, content
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content
    fm_text = parts[1].strip()
    body = parts[2].lstrip('\n')
    fm = {}
    for line in fm_text.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            fm[key] = value
    return fm, body


def is_index_page(body):
    """判断是否是知识索引页"""
    index_markers = [
        '本卡片为知识索引页',
        '收录了相关主题的多条笔记摘要',
        '点击源文件可查看完整内容',
        'card_count',
        '收录卡片',
    ]
    for marker in index_markers:
        if marker in body:
            return True
    return False


def has_template_content(body):
    """检查是否有模板化占位内容"""
    template_patterns = [
        r'基础概念[：:]\s*.+的基础知识和核心定义',
        r'核心原理[：:]\s*.+的底层机制和工作原理',
        r'实践方法[：:]\s*.+的应用方法和实践技巧',
        r'技术持续演进，性能和效率不断提升',
        r'AI 技术融合加速，智能化水平提高',
        r'开源生态持续繁荣，工具链日益成熟',
        r'从传统场景向更多新兴领域渗透',
        r'与云计算、大数据、AI 等技术结合更紧密',
        r'相关领域经典书籍与教材',
        r'技术白皮书与官方文档',
        r'优质技术博客与专栏文章',
        r'相关领域经典教材与权威著作',
        r'技术社区高质量文章与讨论',
        r'行业研究报告与分析',
        r'前沿论文与学术研究',
        r'知识体系全景图',
        r'技术演进路线图',
    ]
    count = 0
    for pattern in template_patterns:
        if re.search(pattern, body):
            count += 1
    return count >= 3


def assess_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {'error': str(e)}

    fm, body = parse_frontmatter(content)

    is_index = is_index_page(body)
    has_template = has_template_content(body)

    # 计算实质内容字数（排除模板、链接等）
    # 先移除代码块
    clean_body = re.sub(r'```.*?```', '', body, flags=re.DOTALL)
    # 移除表格
    clean_body = re.sub(r'^\|.*\|$', '', clean_body, flags=re.MULTILINE)
    # 移除标题行
    clean_body = re.sub(r'^#.*$', '', clean_body, flags=re.MULTILINE)
    # 移除链接
    clean_body = re.sub(r'\[.*?\]\(.*?\)', '', clean_body)
    # 移除引用来源
    clean_body = re.sub(r'^>.*$', '', clean_body, flags=re.MULTILINE)

    cn_chars = len(re.findall(r'[\u4e00-\u9fff]', clean_body))

    # 真实质量评级
    real_quality = 'C级'
    if is_index:
        real_quality = 'B级'  # 索引页本身就是聚合，B级合理
    elif cn_chars > 2500 and not has_template:
        real_quality = 'S级'
    elif cn_chars > 1500 and not has_template:
        real_quality = 'A级'
    elif cn_chars > 800:
        real_quality = 'B级'
    else:
        real_quality = 'C级'

    fm_quality = fm.get('quality_level', '')
    fm_level_num = {'S级': 4, 'S+级': 5, 'A级': 3, 'B级': 2, 'C级': 1, 'D级': 0}
    real_num = fm_level_num.get(real_quality, 0)
    fm_num = fm_level_num.get(fm_quality, 0)
    is_overrated = fm_num > real_num + 1

    issues = []
    if is_index:
        issues.append('知识索引页')
    if has_template:
        issues.append('模板化内容')
    if is_overrated:
        issues.append(f'自评虚高（{fm_quality}→{real_quality}）')
    if cn_chars < 500 and not is_index:
        issues.append(f'内容单薄（{cn_chars}字）')

    return {
        'filename': filepath.name,
        'title': fm.get('title', filepath.stem),
        'directory': filepath.parent.name,
        'fm_quality': fm_quality,
        'real_quality': real_quality,
        'is_index': is_index,
        'has_template': has_template,
        'is_overrated': is_overrated,
        'cn_chars': cn_chars,
        'issues': issues,
        'needs_fix': len(issues) > 0,
    }


def main():
    all_files = []
    needs_fix = []
    index_pages = []
    template_pages = []
    overrated_pages = []

    for dir_name, files in FILES_TO_PROCESS.items():
        dir_path = BASE_DIR / dir_name

        for filename in files:
            filepath = dir_path / filename
            if filepath.exists():
                result = assess_file(filepath)
                all_files.append(result)

                if result['needs_fix']:
                    needs_fix.append(result)
                if result['is_index']:
                    index_pages.append(result)
                if result['has_template']:
                    template_pages.append(result)
                if result['is_overrated']:
                    overrated_pages.append(result)

    total = len(all_files)

    print("=" * 90)
    print("AI 目录剩余文件质量诊断报告")
    print("=" * 90)
    print(f"\n总文件数: {total}")
    print(f"需要处理: {len(needs_fix)} 个 ({len(needs_fix)/total*100:.1f}%)")
    print(f"  - 知识索引页: {len(index_pages)} 个")
    print(f"  - 含模板化内容: {len(template_pages)} 个")
    print(f"  - 自评虚高: {len(overrated_pages)} 个")

    print(f"\n{'='*90}")
    print("分类详情:")
    print(f"{'='*90}")

    # 按目录分组
    by_dir = {}
    for f in needs_fix:
        d = f['directory']
        if d not in by_dir:
            by_dir[d] = []
        by_dir[d].append(f)

    for dir_name, files in sorted(by_dir.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"\n【{dir_name}】 ({len(files)} 个需要处理)")
        for f in sorted(files, key=lambda x: x['cn_chars']):
            issues_str = ', '.join(f['issues'])
            print(f"  - {f['filename']:35s} 真实:{f['real_quality']:4s} 自评:{f['fm_quality']:4s} {f['cn_chars']:5d}字  [{issues_str}]")

    print(f"\n{'='*90}")
    print("处理优先级建议:")
    print(f"{'='*90}")
    print("""
P0（必须处理）:
  - 含模板化内容的文件 → 清理模板，补充真实内容
  - 自评虚高严重的文件 → 修正 frontmatter，提升内容

P1（建议处理）:
  - 知识索引页 → 如果该主题有价值，可转化为知识卡片；否则保持索引页定位
  - 内容单薄的 B 级文件 → 可提升到 A 级

P2（可选处理）:
  - 真实 B 级但质量尚可的文件 → 保持现状，后续按需增强
""")

    # 保存结果
    with open(BASE_DIR / 'ai_quality_diagnosis.json', 'w', encoding='utf-8') as f:
        json.dump({
            'summary': {
                'total': total,
                'needs_fix': len(needs_fix),
                'index_pages': len(index_pages),
                'template_pages': len(template_pages),
                'overrated_pages': len(overrated_pages),
            },
            'needs_fix': needs_fix,
            'index_pages': index_pages,
            'template_pages': template_pages,
            'all_files': all_files,
        }, f, ensure_ascii=False, indent=2)

    print(f"\n详细结果已保存到 ai_quality_diagnosis.json")


if __name__ == '__main__':
    main()
