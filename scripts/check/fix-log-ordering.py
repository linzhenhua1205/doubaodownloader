#!/usr/bin/env python3
"""
Reformat knowledge/log.md into a clean changelog:
- Remove redundant top table (entries merged into changelog section below)
- Remove duplicate headers and "历史存档" separators
- Ensure time-descending order
- Convert table rows to proper changelog format with file links
"""

from pathlib import Path
from scripts.shared.workspace import WORKSPACE_ROOT

LOG = WORKSPACE_ROOT / "log.md"

content = LOG.read_text(encoding='utf-8')
lines = content.split('\n')

# Find key section markers
hist_start = None
changelog_header = None
changelog_start = None
table_end = None

for i, line in enumerate(lines):
    if '📜 历史存档' in line:
        hist_start = i
    if line.startswith('# 📝 知识操作日志 · 按时间倒序排列'):
        changelog_header = i
    if changelog_start is None and changelog_header is not None and line.startswith('## 2026-06-23'):
        changelog_start = i
    if table_end is None and line.strip() == '' and i > 0 and '|:' in lines[i-1]:
        table_end = i

# Extract table rows (between header and blank line after table)
table_rows = []
in_table = False
for i, line in enumerate(lines):
    if line.startswith('| 2026-06-23 ') and not line.startswith('|:'):
        table_rows.append(line)
        in_table = True
    elif in_table and line.startswith('| 2026-06-23 '):
        table_rows.append(line)
    elif in_table and not line.startswith('|'):
        break

print(f"Found {len(table_rows)} table rows to integrate")

# Convert table rows to changelog entries
converted = []
for row in table_rows:
    parts = [p.strip() for p in row.split('|')]
    if len(parts) >= 5:
        time = parts[1]
        op = parts[2]
        filepath = parts[3]
        desc = parts[4]
        
        # Extract just the hour:min
        time_short = time.split(' ')[-1] if ' ' in time else time
        
        # Create file link
        filepath_clean = filepath.replace('knowledge/', '')
        
        # Build entry
        emoji = '📝'
        if op == 'add':
            emoji = '➕'
        elif op == 'update':
            emoji = '✏️'
        elif op == 'ingest':
            emoji = '📥'
        
        entry = f'- **{op}** {emoji} [`{filepath_clean}`]({filepath_clean}) — {desc} (@{time_short})'
        converted.append(entry)

print("Converted entries:")
for e in converted:
    print(f"  {e}")

# Now build the new log file
# Remove everything before the changelog section, except the header
new_lines = []
new_lines.append('# 📝 知识库操作日志')
new_lines.append('')
new_lines.append('> 自动记录 · 按时间倒序排列（最新在上）。格式：`操作 · 文件 — 说明摘要`')
new_lines.append('')

# Insert converted entries at the beginning of the changelog
# They all belong to 2026-06-23, newest first
# Sort by time descending
def extract_time(entry):
    # Extract @(HH:MM) from end
    if '(@' in entry:
        t = entry.split('(@')[1].rstrip(')')
        h, m = t.split(':')
        return int(h) * 60 + int(m)
    return 0

converted.sort(key=extract_time, reverse=True)

# Find the start of actual changelog content
# Copy all from changelog section onwards, but remove the duplicate header
changelog_section = []
copying = False
for i, line in enumerate(lines):
    if changelog_header is not None and i == changelog_header + 1:
        # Skip the old header line, we already have our own
        continue
    if changelog_start is not None and i == changelog_start:
        copying = True
        # This is the first ## 2026-06-23 line
        changelog_section.append(line)
        continue
    if copying:
        changelog_section.append(line)

# The changelog_section now has the full changelog (starting from ## 2026-06-23)
# We need to insert converted entries right after ## 2026-06-23

# Find where to insert (right after the ## 2026-06-23 header line)
insert_idx = None
for i, line in enumerate(changelog_section):
    if line.startswith('## 2026-06-23') and i <= 3:
        # Find the first blank line or first entry after the header
        for j in range(i+1, min(i+5, len(changelog_section))):
            if changelog_section[j].startswith('- ') or changelog_section[j].strip() == '':
                insert_idx = j
                break
        break

if insert_idx is not None:
    # Insert converted entries
    for entry in reversed(converted):
        changelog_section.insert(insert_idx, entry)

# Build final content
final_lines = new_lines + changelog_section
final_content = '\n'.join(final_lines)

# Write
LOG.write_text(final_content, encoding='utf-8')
print(f"\n✅ Rewrote {LOG}")
print(f"   {len(final_lines)} lines (was {len(lines)} lines)")

# Verify no duplicate headers
dup_count = final_content.count('# 📝 知识操作日志')
print(f"   Header count: {dup_count} (should be 1)")
