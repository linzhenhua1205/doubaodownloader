#!/bin/bash
# 创建增量跟踪文件 - 行业洞察持续跟踪辅助脚本
# Usage: bash <base_dir>/scripts/create_tracker.sh <topic> [--date YYYY-MM-DD]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

TOPIC="${1:-}"
DATE="${3:-$(date +%Y-%m-%d)}"

if [ -z "$TOPIC" ]; then
    echo "❌ Usage: create_tracker.sh <topic> [--date YYYY-MM-DD]"
    echo "   Example: create_tracker.sh cxl-switch --date 2026-07-15"
    exit 1
fi

TOPIC_SLUG="$(echo "$TOPIC" | tr '[:upper:]' '[:lower:]' | tr '_' '-' | tr ' ' '-' | sed 's/--*/-/g')"
# 从 SKILL_DIR(../) 上溯到 workspace 根目录推导路径
WORKSPACE_DIR="$(cd "$SKILL_DIR/../.." && pwd)"
TRACKER_DIR="$WORKSPACE_DIR/knowledge/01_survey/08_incr_ir"
TRACKER_FILE="$TRACKER_DIR/$DATE-$TOPIC_SLUG.md"

# 确保目录存在
mkdir -p "$TRACKER_DIR"

if [ -f "$TRACKER_FILE" ]; then
    echo "⚠️  文件已存在: $TRACKER_FILE"
    echo "   追加内容即可"
    exit 0
fi

cat > "$TRACKER_FILE" << EOF
# 📡 $DATE — $TOPIC 增量跟踪

> 关联专题: [专题名称](<../关联专题文件路径>)
> 跟踪频率: [每周/每日]

---

## 本期要点

- 

## 关键信息

### 1. 

### 2. 

## 数据更新

| 指标 | 上期值 | 本期值 | 变化 | 趋势 |
|:-----|:------:|:------:|:----:|:----:|
| — | — | — | —% | 🔼/🔽 |

## 判断调整

- 上期判断: 
- 本期验证: ✅ / ❌ / ⚠️ 部分验证
- 调整: 

## 引用来源

- [来源1](URL)

---

*编辑于 $DATE*
EOF

echo "✅ 增量跟踪文件已创建: $TRACKER_FILE"
echo "💡 提示: 编辑文件补充本期跟踪信息"
