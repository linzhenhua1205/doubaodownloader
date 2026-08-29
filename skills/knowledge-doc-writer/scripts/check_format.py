#!/usr/bin/env python3
"""
文档格式检查脚本 - 检查知识库文档的格式规范

检查规则:
  R1 - TOC 在顶部 (>100行必须有)
  R2 - 参考文献章节存在
  R3 - 变更记录在底部
  R4 - 代码块纯 ASCII（中文说明在外）
  R5 - 内部链接有效性检查
  R6 - 量化数据来源标注检查
  R7 - 章节/链接/代码块统计
"""
import sys
import re
import os


def color(text, code):
    """终端颜色"""
    return f"\033[{code}m{text}\033[0m"


def green(text):
    return color(text, "32")


def yellow(text):
    return color(text, "33")


def red(text):
    return color(text, "31")


def cyan(text):
    return color(text, "36")


def check_format(document_path):
    """检查文档格式"""
    if not os.path.exists(document_path):
        print(red(f"❌ 文件不存在: {document_path}"))
        return False

    with open(document_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')

    filename = os.path.basename(document_path)
    errors = []
    warnings = []
    stats = {}

    print(f"\n{'='*60}")
    print(f"📄 格式检查: {filename}")
    print(f"   路径: {document_path}")
    print(f"{'='*60}\n")

    # ── R1: TOC 在顶部 ──
    stats['r1'] = "⚠️  未检查"
    if len(lines) > 100:
        first_2000 = content[:2000]
        toc_patterns = [
            r'##\s*目录',
            r'##\s*目錄',
            r'##\s*TOC',
            r'##\s*Table of Contents',
            r'##\s*Contents',
            r'\[TOC\]',
            r'<!-- TOC -->',
        ]
        has_toc = False
        for pat in toc_patterns:
            if re.search(pat, first_2000):
                has_toc = True
                break

        if not has_toc:
            warnings.append(("[R1]", f">100行但未找到TOC在顶部 (前2000字符)"))
            stats['r1'] = red("✗ 未找到")
        else:
            # 找到具体的TOC位置
            for pat in toc_patterns:
                m = re.search(pat, first_2000)
                if m:
                    line_no = content[:m.start()].count('\n') + 1
                    if line_no > 15:
                        warnings.append(("[R1]", f"TOC位置偏后 (第{line_no}行)"))
                        stats['r1'] = yellow(f"⚠ 偏后 (L{line_no})")
                    else:
                        stats['r1'] = green(f"✓ 顶部 (L{line_no})")
                    break
    else:
        stats['r1'] = green("✓ ≤100行, 无需TOC")

    # ── R2: 参考文献章节 ──
    stats['r2'] = "⚠️  未检查"
    ref_patterns = [
        '## 参考文献', '## 参考', '# 参考文献',
        '## References', '# References',
        '## 参考资料', '## 参考资料',
    ]
    has_ref = False
    for pat in ref_patterns:
        if pat in content:
            has_ref = True
            break
    if not has_ref:
        warnings.append(("[R2]", "未找到参考文献章节"))
        stats['r2'] = red("✗ 未找到")
    else:
        stats['r2'] = green("✓ 存在")

    # ── R3: 变更记录在底部 ──
    stats['r3'] = "⚠️  未检查"
    changelog_patterns = [
        '## 变更记录', '## 修订记录', '## Changelog',
        '## 更新历史', '## 版本记录',
    ]
    has_cl = False
    cl_pos = -1
    for pat in changelog_patterns:
        pos = content.find(pat)
        if pos >= 0:
            has_cl = True
            cl_pos = pos
            break
    if not has_cl:
        warnings.append(("[R3]", "未找到变更记录章节"))
        stats['r3'] = red("✗ 未找到")
    else:
        # 检查是否在文件末尾1/3处
        cl_line = content[:cl_pos].count('\n') + 1
        total_lines = len(lines)
        if cl_line > total_lines * 2 / 3:
            stats['r3'] = green(f"✓ 底部 (L{cl_line}/{total_lines})")
        else:
            warnings.append(("[R3]", f"变更记录位置偏上 (L{cl_line}/{total_lines})"))
            stats['r3'] = yellow(f"⚠ 偏上 (L{cl_line}/{total_lines})")

    # ── R4: 代码块纯ASCII ──
    stats['r4'] = "⚠️  未检查"
    code_blocks = re.findall(r'```[\s\S]*?```', content)
    chinese_in_code = 0
    for i, block in enumerate(code_blocks):
        # 判断是否是代码块（非数据表格）
        first_line = block.split('\n')[0]
        lang = first_line.replace('```', '').strip().lower()

        # JSON/YAML/Markdown/Mermaid/Diagram 等可以有中文注释
        chinese_allowed = ['json', 'yaml', 'yml', 'mermaid', 'diagram', 'text',
                          'markdown', 'md', 'html', 'xml', 'json5', 'toml']

        if lang in chinese_allowed:
            continue

        # 检查代码块中文行（注释中的中文）
        lines_in_block = block.split('\n')[1:-1]  # 去掉首尾 ```
        for j, cl in enumerate(lines_in_block):
            if re.search(r'[\u4e00-\u9fff]', cl):
                # 注释中的中文可以接受
                if not re.match(r'^\s*[/#;].*', cl) and not re.match(r'^\s*//.*', cl):
                    chinese_in_code += 1

    if chinese_in_code > 0:
        warnings.append(("[R4]", f"代码块中包含 {chinese_in_code} 行非注释中文"))
        stats['r4'] = yellow(f"⚠ {chinese_in_code}行中文")
    else:
        stats['r4'] = green("✓ 纯ASCII")

    # ── R5: 内部链接检查 ──
    stats['r5'] = "⚠️  未检查"
    # 只检查相对路径链接 (../ 开头的)
    internal_links = re.findall(r'\[([^\]]+)\]\(\.\./([^)]+)\)', content)
    broken_count = 0
    doc_dir = os.path.dirname(os.path.abspath(document_path))
    for text, url in internal_links:
        # 跳过外部 URL
        if url.startswith('http'):
            continue
        # 解析相对路径
        link_path = os.path.normpath(os.path.join(doc_dir, '..', url))
        if not os.path.exists(link_path):
            broken_count += 1

    if broken_count > 0:
        warnings.append(("[R5]", f"{broken_count} 个内部链接可能断开"))
        stats['r5'] = yellow(f"⚠ {broken_count}断开")
    else:
        stats['r5'] = green(f"✓ {len(internal_links)}个链接")

    # ── R6: 量化数据来源标注 ──
    stats['r6'] = "⚠️  未检查"
    # 搜索常见的量化模式
    quant_patterns = [
        (r'\d+\.?\d*\s*%', '百分比'),
        (r'\d+\s*(?:W|mW|kW)', '功耗'),
        (r'\d+\s*(?:GB|TB|MB|PB)', '容量'),
        (r'\d+\s*(?:ns|us|ms|μs|ps)', '延迟'),
        (r'\d+\s*(?:GHz|MHz|kHz|Hz)', '频率'),
        (r'\d+\s*(?:GT/s|GB/s|Gbps|Tbps)', '带宽'),
        (r'\d+\s*(?:mm|cm|nm|μm)', '尺寸'),
        (r'\d+\.?\d*\s*x\s*[A-Z]', '倍数'),
    ]

    quant_count = 0
    sourced_count = 0
    for pat, label in quant_patterns:
        matches = re.finditer(pat, content)
        for m in matches:
            quant_count += 1
            # 检查匹配位置前后各200字符是否有来源标记
            start = max(0, m.start() - 200)
            end = min(len(content), m.end() + 200)
            context = content[start:end]
            # 检查是否包含来源标记
            source_indicators = [
                r'\[来源:', r'\[Source:', r'\[\d+\]', r'\[注',
                r'数据来源', r'data from', r'ref\.', r'Ref\.',
                r'source:', r'Source:',
            ]
            for si in source_indicators:
                if re.search(si, context, re.IGNORECASE):
                    sourced_count += 1
                    break

    if quant_count > 0:
        sourced_pct = (sourced_count / quant_count) * 100
        if sourced_pct < 50:
            stats['r6'] = yellow(f"⚠ {quant_count}处量化数据, 仅{sourced_pct:.0f}%有来源标注")
            warnings.append(("[R6]", f"量化数据来源标注率偏低 ({sourced_pct:.0f}%)"))
        else:
            stats['r6'] = green(f"✓ {quant_count}处量化数据, {sourced_pct:.0f}%有来源标注")
    else:
        stats['r6'] = green("✓ 无需检查（无量化数据）")

    # ── R7: 章节/链接/代码块统计 ──
    h1_count = len(re.findall(r'^#\s', content, re.MULTILINE))
    h2_count = len(re.findall(r'^##\s', content, re.MULTILINE))
    h3_count = len(re.findall(r'^###\s', content, re.MULTILINE))
    h4_count = len(re.findall(r'^####\s', content, re.MULTILINE))
    all_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
    ext_links = [(t, u) for t, u in all_links if u.startswith('http')]
    local_links = [(t, u) for t, u in all_links if not u.startswith('http')]
    table_count = len(re.findall(r'^\|.+\|$', content, re.MULTILINE))

    # ── 输出结果 ──
    print(f"{'检查项':<20} {'状态':<20} {'详情'}")
    print(f"{'-'*60}")
    for rule_id in ['r1', 'r2', 'r3', 'r4', 'r5', 'r6']:
        label = {'r1': 'R1 TOC位置', 'r2': 'R2 参考文献',
                 'r3': 'R3 变更记录', 'r4': 'R4 代码块ASCII',
                 'r5': 'R5 内部链接', 'r6': 'R6 量化标注'}[rule_id]
        status = stats.get(rule_id, '⚠️  未检查')
        print(f"  {label:<18} {status}")

    print(f"\n{'='*60}")
    print(f"📊 文档统计:")
    print(f"  总行数: {len(lines)} | 总字符: {len(content):,}")
    print(f"  H1/H2/H3/H4: {h1_count}/{h2_count}/{h3_count}/{h4_count}")
    print(f"  外部链接: {len(ext_links)} | 内部链接: {len(local_links)}")
    print(f"  代码块: {len(code_blocks)} | 表格行: {table_count}")

    if errors or warnings:
        print(f"\n{'='*60}")
    if errors:
        print(f"\n{red('❌ 错误')} ({len(errors)}):")
        for rule, msg in errors:
            print(f"  {rule} {msg}")

    if warnings:
        print(f"\n{yellow('⚠️  警告')} ({len(warnings)}):")
        for rule, msg in warnings:
            print(f"  {rule} {msg}")

    if not errors and not warnings:
        print(f"\n{green('✅')} 所有检查通过!")

    print()
    return len(errors) == 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"用法: python3 {sys.argv[0]} <文档路径>")
        print(f"示例: python3 {sys.argv[0]} knowledge/02_rd/07_reports/my-report.md")
        sys.exit(1)

    success = check_format(sys.argv[1])
    sys.exit(0 if success else 1)
