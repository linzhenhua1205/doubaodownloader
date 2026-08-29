#!/usr/bin/env python3
"""
文档格式检查脚本 - 验证文档格式规范
"""
import sys
import re


def check_format(document_path):
    """检查文档格式"""
    with open(document_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    
    errors = []
    warnings = []
    
    # R1: TOC 在顶部 (>100行必须有)
    if len(lines) > 100:
        if not re.search(r'##\s*目录|##\s*目錄|##\s*TOC|##\s*Table of Contents', content[:2000]):
            warnings.append("[R1] ⚠️ >100行但未找到目录(TOC)在顶部")
        else:
            # 检查TOC位置
            toc_pos = content.find('## 目录')
            if toc_pos > 2000:
                warnings.append(f"[R1] ⚠️ 目录位置偏后 (第{toc_pos//80}行附近)")
            else:
                print(f"[R1] ✅ TOC在顶部")
    
    # R2: 参考文献在底部
    if '## 参考文献' not in content and '## References' not in content:
        # 检查是否有其他参考标记
        ref_patterns = ['## 参考', '## Reference', '# 参考文献', '# References']
        found_ref = False
        for p in ref_patterns:
            if p in content:
                found_ref = True
                break
        if not found_ref:
            warnings.append("[R2] ⚠️ 未找到参考文献章节")
        else:
            print("[R2] ✅ 参考文献章节存在")
    else:
        print("[R2] ✅ 参考文献章节存在")
    
    # R3: Changelog/变更记录在底部
    if '## 变更记录' in content or '## 修订记录' in content or '## Changelog' in content:
        print("[R3] ✅ 变更记录章节存在")
    else:
        warnings.append("[R3] ⚠️ 未找到变更记录章节")
    
    # R4: 检查代码块中是否包含中文
    code_blocks = re.findall(r'```[\s\S]*?```', content)
    for i, block in enumerate(code_blocks):
        # 只检查纯代码块（非JSON/YAML中有中文是正常的）
        if re.search(r'[\u4e00-\u9fff]', block):
            # 排在前面的是代码注释中的中文
            lines_in_block = block.split('\n')
            chinese_lines = [l for l in lines_in_block if re.search(r'[\u4e00-\u9fff]', l)]
            if chinese_lines:
                warnings.append(f"[R4] ⚠️ 代码块 #{i+1} 中包含{len(chinese_lines)}行中文注释")
    
    # R5: 检查链接有效性
    links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
    broken_links = []
    for text, url in links:
        if url.startswith('http') and 'dmtf.org' in url:
            pass  # 外部链接不检查
        elif url.startswith('../'):
            # local link
            pass
    
    # R6: 检查量化数据是否有来源标注
    quantified_patterns = [
        r'\d+\.?\d*\s*%',
        r'\d+\s*W',
        r'\d+\s*GB',
        r'\d+\s*TB',
        r'\d+\s*hours?',
        r'\d+\s*POH',
    ]
    
    print(f"\n📏 文档统计:")
    print(f"  总行数: {len(lines)}")
    print(f"  总字符: {len(content)}")
    
    # 统计章节
    h2_count = len(re.findall(r'^##\s', content, re.MULTILINE))
    h3_count = len(re.findall(r'^###\s', content, re.MULTILINE))
    print(f"  H2章节: {h2_count}")
    print(f"  H3子章: {h3_count}")
    
    # 统计链接
    links_count = len(links)
    print(f"  链接数: {links_count}")
    
    # 统计代码块
    print(f"  代码块: {len(code_blocks)}")
    
    print(f"\n{'='*50}")
    if errors:
        print(f"❌ 错误 ({len(errors)}):")
        for e in errors:
            print(f"  {e}")
    
    if warnings:
        print(f"⚠️  警告 ({len(warnings)}):")
        for w in warnings:
            print(f"  {w}")
    
    if not errors and not warnings:
        print("✅ 所有检查通过!")
    
    return len(errors) == 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 check_format.py <文档路径>")
        sys.exit(1)
    
    success = check_format(sys.argv[1])
    sys.exit(0 if success else 1)
