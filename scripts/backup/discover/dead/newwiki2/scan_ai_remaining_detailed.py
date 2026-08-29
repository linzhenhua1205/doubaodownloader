# -*- coding: utf-8 -*-
"""
精准扫描 AI 目录剩余文件 - 找出真正需要质量提升的文件
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


def count_chinese_chars(text):
    return len(re.findall(r'[\u4e00-\u9fff]', text))


def count_tables(body):
    table_lines = len(re.findall(r'^\|.*\|$', body, re.MULTILINE))
    return max(0, table_lines // 3)


def has_template_content(body):
    template_patterns = [
        r'方案A\s*\|\s*方案B\s*\|\s*方案C',
        r'案例一：大型互联网公司',
        r'案例二：金融企业',
        r'案例三：初创企业',
        r'入门级（1-2个月）',
        r'以下为原始内容，已整合到增强版中',
        r'\{.*?placeholder.*?\}',
        r'请补充',
        r'待补充',
        r'TODO',
    ]
    for pattern in template_patterns:
        if re.search(pattern, body, re.IGNORECASE):
            return True
    return False


def assess_real_quality(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {'error': str(e)}

    fm, body = parse_frontmatter(content)

    cn_chars = count_chinese_chars(body)
    tables = count_tables(body)
    has_template = has_template_content(body)

    # 检查 frontmatter 自评级
    fm_quality = fm.get('quality_level', '')
    fm_status = fm.get('status', '')
    fm_word_count = fm.get('word_count', '')

    # 真实质量评估（更保守）
    real_level = 'C级'
    reasons = []

    if cn_chars > 2500 and tables >= 3:
        real_level = 'S级'
    elif cn_chars > 1800 and tables >= 2:
        real_level = 'A级'
    elif cn_chars > 1000 and tables >= 1:
        real_level = 'B级'
    elif cn_chars > 500:
        real_level = 'B级'
    else:
        real_level = 'C级'
        reasons.append(f'字数不足（{cn_chars}字）')

    if has_template:
        reasons.append('含模板化内容')

    # 检查 frontmatter 是否虚高
    fm_level_num = {'S级': 4, 'S+级': 5, 'A级': 3, 'B级': 2, 'C级': 1, 'D级': 0}
    real_num = fm_level_num.get(real_level, 0)
    fm_num = fm_level_num.get(fm_quality, 0)
    is_overrated = fm_num > real_num + 1

    return {
        'filename': filepath.name,
        'title': fm.get('title', filepath.stem),
        'fm_quality': fm_quality,
        'real_quality': real_level,
        'is_overrated': is_overrated,
        'cn_chars': cn_chars,
        'tables': tables,
        'has_template': has_template,
        'reasons': reasons,
        'fm_status': fm_status,
    }


def main():
    all_files = []
    needs_enhancement = []
    quality_summary = {'S级': 0, 'A级': 0, 'B级': 0, 'C级': 0}
    template_count = 0
    overrated_count = 0

    for dir_name, files in FILES_TO_PROCESS.items():
        dir_path = BASE_DIR / dir_name

        for filename in files:
            filepath = dir_path / filename
            if filepath.exists():
                result = assess_real_quality(filepath)
                result['directory'] = dir_name
                all_files.append(result)

                quality_summary[result['real_quality']] = quality_summary.get(result['real_quality'], 0) + 1

                if result['has_template']:
                    template_count += 1

                if result['is_overrated']:
                    overrated_count += 1

                # 需要增强的：C级、含模板、虚高严重
                if result['real_quality'] in ['C级', 'D级'] or result['has_template'] or result['is_overrated']:
                    needs_enhancement.append(result)

    total = len(all_files)

    print("=" * 80)
    print("AI 目录剩余文件真实质量扫描报告")
    print("=" * 80)
    print(f"\n总文件数: {total}")
    print(f"\n真实质量分布:")
    for q in ['S级', 'A级', 'B级', 'C级', 'D级']:
        count = quality_summary.get(q, 0)
        pct = count / total * 100 if total > 0 else 0
        print(f"  {q}: {count} 个 ({pct:.1f}%)")

    print(f"\n含模板化内容: {template_count} 个")
    print(f"frontmatter 虚高: {overrated_count} 个")
    print(f"需要质量提升: {len(needs_enhancement)} 个")

    print(f"\n{'='*80}")
    print("需要质量提升的文件列表:")
    print(f"{'='*80}")

    by_dir = {}
    for f in needs_enhancement:
        d = f['directory']
        if d not in by_dir:
            by_dir[d] = []
        by_dir[d].append(f)

    for dir_name, files in by_dir.items():
        print(f"\n【{dir_name}】 ({len(files)} 个)")
        for f in sorted(files, key=lambda x: x['cn_chars']):
            flag = ''
            if f['has_template']:
                flag += ' [模板]'
            if f['is_overrated']:
                flag += ' [虚高]'
            print(f"  - {f['filename']:30s} 真实:{f['real_quality']:4s} 自评:{f['fm_quality']:4s} {f['cn_chars']:5d}字 {f['tables']}表{flag}")
            if f['reasons']:
                print(f"    原因: {', '.join(f['reasons'])}")

    # 保存详细结果
    with open(BASE_DIR / 'ai_remaining_detailed_scan.json', 'w', encoding='utf-8') as f:
        json.dump({
            'summary': {
                'total': total,
                'quality_summary': quality_summary,
                'template_count': template_count,
                'overrated_count': overrated_count,
                'needs_enhancement_count': len(needs_enhancement),
            },
            'needs_enhancement': needs_enhancement,
            'all_files': all_files,
        }, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*80}")
    print(f"详细结果已保存到 ai_remaining_detailed_scan.json")


if __name__ == '__main__':
    main()
