#!/usr/bin/env bash
# =============================================================================
# 竞品分析维度对比表生成器
# 用法: bash <skill_dir>/scripts/dimension-table.sh <数据文件> [输出文件]
#
# 数据文件格式（每行一个对比条目）:
# 维度|我们自己|竞品A|竞品B|竞品C|分析结论
# CPU型号|Xeon 6980P|EPYC 9965|Xeon 6980P|Grace|Xeon vs EPYC 各有所长
# =============================================================================
set -euo pipefail

if [ $# -lt 1 ]; then
    echo "用法: bash \$0 <数据文件> [输出文件]"
    echo "数据格式: 维度|我们自己|竞品A|竞品B|竞品C|分析结论"
    echo "若不指定输出文件，输出到 stdout"
    echo ""
    echo "示例:"
    echo "  bash \$0 comparison-data.txt"
    echo "  bash \$0 comparison-data.txt report.md"
    exit 1
fi

INFILE="$1"
OUTFILE="${2:-}"

if [ ! -f "$INFILE" ]; then
    echo "❌ 数据文件不存在: $INFILE"
    exit 1
fi

# 读取表头（第一行）
HEADER=$(head -1 "$INFILE")
echo "表头: $HEADER" >&2

# 从表头提取列名
IFS='|' read -ra COLS <<< "$HEADER"
NUM_COLS=${#COLS[@]}

if [ "$NUM_COLS" -lt 3 ]; then
    echo "❌ 数据文件至少需要 3 列: 维度|我们自己|竞品A"
    exit 1
fi

# 检查是否有结论列
HAS_CONCLUSION=false
LAST_COL="${COLS[$((NUM_COLS-1))]}"
if [ "$LAST_COL" = "分析结论" ]; then
    HAS_CONCLUSION=true
fi

# 输出函数
output() {
    if [ -n "$OUTFILE" ]; then
        echo "$1" >> "$OUTFILE"
    else
        echo "$1"
    fi
}

# ---- 开始生成 ----

# 表头
DIM_COL="${COLS[0]}"
output ""
output "### 对比表: 竞品分析"
output ""
output "| $DIM_COL"

# 从col[1]到col[end]构建表头
for ((i=1; i<NUM_COLS; i++)); do
    output -n " | ${COLS[$i]}"
done
output " |"

# 分隔线
output -n "|:"
output -n "$(printf '%*s' "${#DIM_COL}" '' | tr ' ' '-')"
output -n ":"
for ((i=1; i<NUM_COLS; i++)); do
    output -n " |:"
    output -n "$(printf '%*s' "${#COLS[$i]}" '' | tr ' ' '-')"
    output -n ":"
done
output " |"

# 数据行（从第二行开始）
TOTAL=$(wc -l < "$INFILE")
echo "总行数: $TOTAL (含表头)" >&2

LINENUM=0
while IFS='|' read -ra ROW; do
    LINENUM=$((LINENUM + 1))
    # 跳过第一行（表头）
    [ "$LINENUM" -eq 1 ] && continue
    
    # 跳过空行
    [ ${#ROW[@]} -eq 0 ] && continue
    
    # 输出数据行
    output -n "| ${ROW[0]}"
    for ((i=1; i<${#ROW[@]}; i++)); do
        val="${ROW[$i]}"
        # 给关键值加粗
        if [[ "$val" == *"✅"* ]] || [[ "$val" == *"领先"* ]] || [[ "$val" == *"优势"* ]]; then
            val="**$val**"
        elif [[ "$val" == *"❌"* ]] || [[ "$val" == *"落后"* ]] || [[ "$val" == *"弱"* ]]; then
            val="*$val*"
        fi
        output -n " | $val"
    done
    output " |"
done < "$INFILE"

output ""
output "> 📊 注: **加粗**=优势 · *斜体*=劣势 · 结论列含关键洞察"
output ""

echo "✅ 对比表已生成" >&2
if [ -n "$OUTFILE" ]; then
    echo "输出文件: $OUTFILE" >&2
fi
