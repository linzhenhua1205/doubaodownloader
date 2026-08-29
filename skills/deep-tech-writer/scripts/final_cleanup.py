#!/usr/bin/env python3
"""
最终清理：
1. 移除多余的分隔线
2. 清理不相关的外部资料引用
3. 优化空行
"""

import os
import re
import sys
from pathlib import Path

BASE_DIR = Path("h:/github/cowkb")
TARGET_DIR = BASE_DIR / "discover" / "site" / "数据库与存储"


def clean_document(filepath):
    """最终清理单个文档"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        result_lines = []
        
        in_external_refs = False
        external_ref_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # 检测"外部资料引用"章节开始
            if stripped == '### 外部资料引用':
                in_external_refs = True
                external_ref_lines = [line]
                i += 1
                continue
            
            if in_external_refs:
                # 检测下一个二级或三级标题（章节结束）
                if stripped.startswith('## ') or (stripped.startswith('### ') and stripped != '### 外部资料引用'):
                    # 处理收集到的外部引用
                    result_lines.extend(filter_external_refs(external_ref_lines, filepath.name))
                    result_lines.append(line)
                    in_external_refs = False
                    i += 1
                    continue
                else:
                    external_ref_lines.append(line)
                    i += 1
                    continue
            
            # 跳过连续的分隔线
            if stripped == '---':
                # 检查前面是不是已经有分隔线或空行+分隔线
                if result_lines:
                    # 往前找非空行
                    j = len(result_lines) - 1
                    while j >= 0 and result_lines[j].strip() == '':
                        j -= 1
                    if j >= 0 and result_lines[j].strip() == '---':
                        # 连续的分隔线，跳过
                        i += 1
                        continue
            
            result_lines.append(line)
            i += 1
        
        # 如果文件以外部引用结束，也要处理
        if in_external_refs:
            result_lines.extend(filter_external_refs(external_ref_lines, filepath.name))
        
        # 清理过多空行
        new_content = '\n'.join(result_lines)
        new_content = re.sub(r'\n{4,}', '\n\n\n', new_content)
        
        # 清理结尾多余的空行
        new_content = new_content.rstrip() + '\n'
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, None
        
    except Exception as e:
        import traceback
        return False, f'{str(e)}\n{traceback.format_exc()[:200]}'


def filter_external_refs(lines, filename):
    """过滤不相关的外部资料引用"""
    result = []
    in_list = False
    
    for line in lines:
        stripped = line.strip()
        result.append(line)
        
        if stripped.startswith('- [') and '](' in stripped:
            # 检查这个链接是否相关
            if not is_relevant_ref(stripped, filename):
                result.pop()  # 移除刚才添加的
    
    return result


def is_relevant_ref(ref_line, filename):
    """判断引用是否相关"""
    filename_lower = filename.lower()
    
    # 提取链接标题
    match = re.match(r'-\s*\[(.+?)\]\(', ref_line)
    if not match:
        return True
    
    title = match.group(1)
    title_lower = title.lower()
    
    # 根据文件名判断哪些引用是相关的
    if 'postgresql' in filename_lower or 'pgsql' in filename_lower:
        if 'PostgreSQL' in title:
            return True
        if 'MySQL' in title and ('对比' in filename or 'mysql' in filename_lower):
            return True
        if '原文链接' in title:
            return True
        return False
    
    if 'mysql' in filename_lower:
        if 'MySQL' in title:
            return True
        if 'PostgreSQL' in title and ('对比' in filename or 'postgresql' in filename_lower):
            return True
        if '原文链接' in title:
            return True
        return False
    
    if 'sqlite' in filename_lower or 'db4s' in filename_lower:
        if 'SQLite' in title or 'sqlite' in title_lower:
            return True
        if '原文链接' in title:
            return True
        return False
    
    if 'minio' in filename_lower:
        if 'MinIO' in title or 'minio' in title_lower:
            return True
        if '原文链接' in title:
            return True
        return False
    
    if 'dify' in filename_lower:
        if 'Dify' in title or 'dify' in title_lower:
            return True
        if 'MySQL' in title and 'mysql' in filename_lower:
            return True
        if '原文链接' in title:
            return True
        return False
    
    if 'nvme' in filename_lower:
        if 'NVM Express' in title or 'NVMe' in title or 'nvme' in title_lower:
            return True
        if '原文链接' in title:
            return True
        return False
    
    if 'rag' in filename_lower or 'graphrag' in filename_lower:
        if '原文链接' in title:
            return True
        # RAG相关的都可以保留
        return True
    
    # 默认保留
    return True


def main():
    print("=" * 70)
    print("最终清理优化")
    print("=" * 70)
    print()
    
    if not TARGET_DIR.exists():
        print(f"❌ 目录不存在: {TARGET_DIR}")
        sys.exit(1)
    
    md_files = sorted(TARGET_DIR.glob('*.md'))
    md_files = [f for f in md_files if f.name != 'index.md']
    
    print(f"📁 目标目录: {TARGET_DIR}")
    print(f"📄 发现 {len(md_files)} 个markdown文件")
    print()
    
    success_count = 0
    fail_count = 0
    errors = []
    
    for i, filepath in enumerate(md_files, 1):
        print(f"[{i:2d}/{len(md_files)}] 🧹 清理中: {filepath.name}")
        success, error = clean_document(filepath)
        if success:
            success_count += 1
            print(f"         ✅ 完成")
        else:
            fail_count += 1
            errors.append((filepath.name, error))
            print(f"         ❌ 失败: {error[:80]}")
    
    print()
    print("=" * 70)
    print("📊 清理完成统计")
    print("=" * 70)
    print(f"✅ 成功: {success_count}")
    print(f"❌ 失败: {fail_count}")
    print(f"📈 成功率: {success_count/len(md_files)*100:.1f}%")
    
    if errors:
        print()
        print("⚠️  错误详情:")
        for name, error in errors:
            print(f"   - {name}: {error[:100]}")
    
    return 0 if fail_count == 0 else 1


if __name__ == '__main__':
    exit(main())
