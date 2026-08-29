#!/usr/bin/env python3
"""
Fix URL-encoded Chinese filenames in index.md links.
The actual files use literal Chinese characters, but index.md links 
sometimes use URL-encoded versions (%E3%80%90 for 【, etc.)
"""

import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote

from scripts.shared.workspace import WORKSPACE_ROOT, KNOWLEDGE_ROOT

BASE = WORKSPACE_ROOT
INDEX = BASE / "index.md"

# Read current content
content = INDEX.read_text(encoding='utf-8')
original = content

# Pattern: any markdown link with URL-encoded characters
link_pattern = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')

def decode_link(match):
    text = match.group(1)
    path = match.group(2)
    
    # Skip external URLs
    if path.startswith('http://') or path.startswith('https://'):
        return match.group(0)
    
    # Decode URL-encoded characters in local paths
    decoded = unquote(path)
    
    if decoded != path:
        return f'[{text}]({decoded})'
    return match.group(0)

content = link_pattern.sub(decode_link, content)

if content != original:
    INDEX.write_text(content, encoding='utf-8')
    print(f"✅ Fixed URL-encoded links in {INDEX}")
else:
    print("No URL-encoded links found")

# Now also fix: replace 'enterprise-mgmt/sources/' with correct relative paths
# since sources was consolidated under 06_others/sources/
content2 = INDEX.read_text(encoding='utf-8')
original2 = content2

# Fix paths that reference sources/ subdirectories incorrectly
# Check if these files exist
fixes = [
    ('enterprise-mgmt/sources/', 'notes/'),
]
for old_prefix, new_prefix in fixes:
    count = content2.count(f'({old_prefix}')
    if count > 0:
        content2 = content2.replace(f'({old_prefix}', f'({new_prefix}')
        print(f"  🔧 Replaced {count}x `{old_prefix}` → `{new_prefix}`")

if content2 != original2:
    INDEX.write_text(content2, encoding='utf-8')
    print(f"✅ Fixed prefix paths in index.md")
