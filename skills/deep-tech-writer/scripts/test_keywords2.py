import re
import sys
sys.path.insert(0, r'h:\github\cowkb\skills\deep-tech-writer\scripts')

from deep_refactor_knowledge_mgmt_v2 import generate_keywords

test_cases = [
    ('OKR管理体系全景指南（2026）：从目标管理到AI驱动的组织效能提升', ''),
    ('企业知识库搭建工具深度解析（11款主流工具选型指南）', ''),
    ('AI时代程序员效能提升全景指南（2026）：从10x工程师到100x工程师的能力进化路径', ''),
    ('OneNote深度研究：从信息碎片到知识系统', ''),
]

for title, content in test_cases:
    print('Title:', title)
    print('Keywords:', generate_keywords(title, content))
    print()
