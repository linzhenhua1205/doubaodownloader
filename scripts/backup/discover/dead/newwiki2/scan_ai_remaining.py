# -*- coding: utf-8 -*-
"""
扫描 AI 目录剩余文件的质量状态
"""
import os
import re
import json
from pathlib import Path

BASE_DIR = Path(r"h:\github\cowkb\discover\newwiki2")

# 需要处理的文件列表（按目录分类）
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


def estimate_word_count(body):
    cn_chars = len(re.findall(r'[\u4e00-\u9fff]', body))
    en_words = len(re.findall(r'[a-zA-Z]+', body))
    return cn_chars + en_words // 2


def count_tables(body):
    return len(re.findall(r'^\|.*\|$', body, re.MULTILINE)) // 2


def has_templated_content(body):
    template_markers = [
        "方案A | 方案B | 方案C",
        "案例一：大型互联网公司",
        "入门级（1-2个月）",
        "（以下为原始内容，已整合到增强版中）",
        "主流方案对比\n\n| 维度 | 方案A | 方案B | 方案C",
    ]
    for marker in template_markers:
        if marker in body:
            return True
    return False


def scan_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {'error': str(e)}

    fm, body = parse_frontmatter(content)

    word_count = estimate_word_count(body)
    tables = count_tables(body)
    templated = has_templated_content(body)

    quality = fm.get('quality_level', '')
    if not quality:
        if word_count > 2000:
            quality = "S级"
        elif word_count > 1000:
            quality = "A级"
        elif word_count > 400:
            quality = "B级"
        else:
            quality = "C级"

    return {
        'filename': filepath.name,
        'title': fm.get('title', filepath.stem),
        'quality': quality,
        'word_count': word_count,
        'tables': tables,
        'has_templated': templated,
        'status': fm.get('status', ''),
    }


def main():
    results = {}
    total_files = 0
    quality_counts = {"S级": 0, "A级": 0, "B级": 0, "C级": 0, "D级": 0}
    templated_count = 0

    for dir_name, files in FILES_TO_PROCESS.items():
        dir_path = BASE_DIR / dir_name
        dir_results = []

        for filename in files:
            filepath = dir_path / filename
            if filepath.exists():
                result = scan_file(filepath)
                result['directory'] = dir_name
                dir_results.append(result)
                total_files += 1

                q = result['quality']
                if q in quality_counts:
                    quality_counts[q] += 1
                else:
                    quality_counts[q] = 1

                if result['has_templated']:
                    templated_count += 1
            else:
                dir_results.append({
                    'filename': filename,
                    'directory': dir_name,
                    'error': 'file_not_found'
                })

        results[dir_name] = dir_results

    print("=" * 70)
    print("AI 目录剩余文件质量扫描报告")
    print("=" * 70)
    print(f"\n总文件数: {total_files}")
    print(f"\n质量分布:")
    for q in ["S级", "A级", "B级", "C级", "D级"]:
        count = quality_counts.get(q, 0)
        pct = count / total_files * 100 if total_files > 0 else 0
        print(f"  {q}: {count} 个 ({pct:.1f}%)")
    print(f"\n含模板化内容: {templated_count} 个")

    print(f"\n{'='*70}")
    print("各目录详情:")
    print(f"{'='*70}")

    for dir_name, files in results.items():
        existing = [f for f in files if 'error' not in f]
        not_found = [f for f in files if 'error' in f]
        print(f"\n【{dir_name}】 ({len(existing)} 个文件)")

        c_levels = {}
        for f in existing:
            q = f['quality']
            c_levels[q] = c_levels.get(q, 0) + 1

        levels_str = ", ".join(f"{q}:{c}" for q, c in sorted(c_levels.items()))
        print(f"  质量分布: {levels_str}")

        templated = [f for f in existing if f['has_templated']]
        if templated:
            print(f"  模板化文件: {len(templated)} 个")
            for f in templated[:5]:
                print(f"    - {f['filename']} ({f['quality']}, {f['word_count']}字)")

        c_files = [f for f in existing if f['quality'] in ['C级', 'D级']]
        if c_files:
            print(f"  C/D级文件 ({len(c_files)} 个):")
            for f in sorted(c_files, key=lambda x: x['word_count']):
                print(f"    - {f['filename']}: {f['quality']}, {f['word_count']}字, {f['tables']}表")

        if not_found:
            print(f"  未找到文件: {len(not_found)} 个")
            for f in not_found:
                print(f"    - {f['filename']}")

    with open(BASE_DIR / 'ai_remaining_scan_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*70}")
    print(f"详细结果已保存到 ai_remaining_scan_results.json")


if __name__ == '__main__':
    main()
