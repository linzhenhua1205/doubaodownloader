#!/usr/bin/env python3
"""
修复重构后的文档问题：
1. 移除重复的参考文件和Changelog章节（只保留最后一份）
2. 清理空的二级标题
3. 优化标题层级
"""

import os
import re
import sys
from pathlib import Path

BASE_DIR = Path("h:/github/cowkb")
TARGET_DIR = BASE_DIR / "discover" / "site" / "数据库与存储"


def clean_document(filepath):
    """清理单个文档"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        new_lines = []
        in_code_block = False
        
        # 找出所有二级标题的位置
        h2_positions = []
        for i, line in enumerate(lines):
            if line.startswith('```'):
                in_code_block = not in_code_block
            if not in_code_block and line.startswith('## ') and not line.startswith('### '):
                h2_positions.append((i, line[3:].strip()))
        
        # 找出最后一个"参考文件"和"Changelog"的位置
        last_ref_idx = -1
        last_changelog_idx = -1
        
        for idx, (pos, title) in enumerate(h2_positions):
            clean_title = re.sub(r'[\U0001F300-\U0001F9FF\U00002600-\U000027BF]', '', title).strip()
            if clean_title == '参考文件':
                last_ref_idx = idx
            if clean_title == 'Changelog':
                last_changelog_idx = idx
        
        # 如果有多个参考文件或Changelog，移除前面的
        if last_ref_idx >= 0 or last_changelog_idx >= 0:
            # 找出需要保留的起始位置
            keep_from = len(h2_positions)
            if last_ref_idx >= 0:
                keep_from = min(keep_from, last_ref_idx)
            if last_changelog_idx >= 0:
                keep_from = min(keep_from, last_changelog_idx)
            
            # 标记需要删除的章节
            sections_to_remove = set()
            for idx in range(keep_from):
                pos, title = h2_positions[idx]
                clean_title = re.sub(r'[\U0001F300-\U0001F9FF\U00002600-\U000027BF]', '', title).strip()
                if clean_title in ['参考文件', 'Changelog', '变更日志', '版本记录']:
                    sections_to_remove.add(idx)
            
            if sections_to_remove:
                # 重建内容，跳过要删除的章节
                result_lines = []
                skip_until_next_h2 = False
                
                in_code_block2 = False
                for i, line in enumerate(lines):
                    if line.startswith('```'):
                        in_code_block2 = not in_code_block2
                    
                    if not in_code_block2 and line.startswith('## ') and not line.startswith('### '):
                        # 检查这是不是要删除的章节
                        title = line[3:].strip()
                        clean_title = re.sub(r'[\U0001F300-\U0001F9FF\U00002600-\U000027BF]', '', title).strip()
                        if clean_title in ['参考文件', 'Changelog', '变更日志', '版本记录']:
                            # 判断是不是最后一个
                            is_last_ref = (clean_title == '参考文件' and i == h2_positions[last_ref_idx][0])
                            is_last_cl = (clean_title == 'Changelog' and last_changelog_idx >= 0 and i == h2_positions[last_changelog_idx][0])
                            
                            if not is_last_ref and not is_last_cl:
                                skip_until_next_h2 = True
                                continue
                            else:
                                skip_until_next_h2 = False
                        else:
                            skip_until_next_h2 = False
                    
                    if not skip_until_next_h2:
                        result_lines.append(line)
                
                lines = result_lines
        
        # 清理空的二级标题（标题下面没有内容）
        final_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            if stripped.startswith('## ') and not stripped.startswith('### '):
                # 检查后面是否有内容
                has_content = False
                for j in range(i + 1, min(i + 10, len(lines))):
                    next_stripped = lines[j].strip()
                    if next_stripped.startswith('## '):
                        break
                    if next_stripped and not next_stripped.startswith('---'):
                        has_content = True
                        break
                
                if has_content:
                    final_lines.append(line)
                i += 1
                continue
            
            final_lines.append(line)
            i += 1
        
        # 清理过多的分隔线
        cleaned_lines = []
        prev_was_divider = False
        for line in final_lines:
            stripped = line.strip()
            if stripped == '---':
                if not prev_was_divider:
                    cleaned_lines.append(line)
                prev_was_divider = True
            else:
                prev_was_divider = False
                cleaned_lines.append(line)
        
        # 清理过多空行
        new_content = '\n'.join(cleaned_lines)
        new_content = re.sub(r'\n{4,}', '\n\n\n', new_content)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, None
        
    except Exception as e:
        import traceback
        return False, f'{str(e)}\n{traceback.format_exc()[:200]}'


def main():
    print("=" * 70)
    print("修复重构后的文档问题")
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
        print(f"[{i:2d}/{len(md_files)}] 🔧 修复中: {filepath.name}")
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
    print("📊 修复完成统计")
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
