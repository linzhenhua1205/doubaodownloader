#!/usr/bin/env python3
"""测试单个文件的重构"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from deep_refactor_database_storage_v2 import (
    extract_frontmatter,
    extract_meaningful_body,
    extract_h2_titles,
)

BASE_DIR = Path("h:/github/cowkb")
TEST_FILE = BASE_DIR / "discover" / "site" / "数据库与存储" / "MySQL 8_0查询缓存_Query Cache_功能深度解析：移除原因与替代方案.md"

def main():
    with open(TEST_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    frontmatter_full, frontmatter_content, body = extract_frontmatter(content)
    
    print(f"Frontmatter长度: {len(frontmatter_full)}")
    print(f"Body长度: {len(body)}")
    print()
    
    meaningful = extract_meaningful_body(body)
    
    if meaningful:
        print(f"提取内容长度: {len(meaningful)}")
        print()
        print("=" * 60)
        print("提取的内容:")
        print("=" * 60)
        print(meaningful[:2000])
        print("...")
        print()
        
        h2 = extract_h2_titles(meaningful)
        print(f"二级标题数量: {len(h2)}")
        for i, t in enumerate(h2):
            print(f"  {i+1}. {t}")
    else:
        print("❌ 未能提取有效内容")


if __name__ == '__main__':
    main()
