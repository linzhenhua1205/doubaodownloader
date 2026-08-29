#!/usr/bin/env bash
# =============================================================================
# 竞品信息采集辅助脚本
# 用法: bash <skill_dir>/scripts/competitor-collect.sh <竞品名称> <输出目录>
# =============================================================================
set -euo pipefail

if [ $# -lt 2 ]; then
    echo "用法: bash \$0 <竞品名称> <输出目录>"
    echo "示例: bash \$0 'Dell PowerEdge XE9680' \$SKILL_DIR/../../tmp/competitor"
    exit 1
fi

COMPETITOR="$1"
OUTDIR="$2"
SLUG=$(echo "$COMPETITOR" | tr 'A-Z ' 'a-z-')

mkdir -p "$OUTDIR/$SLUG"

# 检查各信息源的文件完整性
check_source() {
    local name="$1"
    local file="$2"
    if [ -f "$file" ]; then
        local size=$(wc -c < "$file")
        echo "  ✅ $name: $file (${size} bytes)"
    else
        echo "  ❌ $name: 未收集"
    fi
}

cat << 'EOF'
# =============================================================================
# 竞品信息采集清单
# 按以下顺序逐项采集，每项完成后勾选
#
# 采集完成后运行: bash collect-check.sh <竞品名> <输出目录>
# =============================================================================

## 一、官方信息源
EOF

cat << TABLE_EOF
| # | 信息源 | 采集内容 | 状态 |
|:-:|:-------|:---------|:----:|
| 1 | 官方产品页 | 规格参数、价格、图片 | ☐ — web_fetch 竞品官网 |
| 2 | Datasheet/白皮书 | 详细技术规格、性能数据 | ☐ — web_fetch PDF |
| 3 | 官方技术博客 | 架构设计理念、技术选型 | ☐ — web_fetch blog |
| 4 | MLPerf 提交记录 | 标准化训练/推理性能 | ☐ — mlcommons.org |
| 5 | 培训/认证信息 | 生态绑定程度 | ☐ — 官网搜索培训课程 |

## 二、第三方评测

| 6 | ServeTheHome | 拆机评测、BOM分析、实测数据 | ☐ — web_fetch STH |
| 7 | ChipsandCheese | 微架构分析 | ☐ — web_fetch C&C |
| 8 | SemiAnalysis | 商业策略分析 | ☐ — web_fetch SA |
| 9 | 用户论坛(Reddit/HPC) | 真实使用体验、故障模式 | ☐ — web_fetch subreddit |

## 三、技术验证

| 10 | GitHub Issues | 软件栈Bug/兼容性问题 | ☐ — web_fetch repo |
| 11 | 安全公告(PSIRT) | CVE、漏洞修复周期 | ☐ — web_fetch PSIRT |
| 12 | 社区问答(Stack Overflow) | 开发者真实体验 | ☐ — web_fetch SO |
TABLE_EOF

cat << 'EOF'

# =============================================================================
# 验证步骤
# =============================================================================
EOF

echo ""
echo "=== 采集检查: $COMPETITOR ==="
echo "输出目录: $OUTDIR/$SLUG/"
echo ""

echo "--- 已采集文件 ---"
check_source "官方产品摘要" "$OUTDIR/$SLUG/01-official.md"
check_source "Datasheet"    "$OUTDIR/$SLUG/02-datasheet.md"
check_source "技术评测"     "$OUTDIR/$SLUG/03-review.md"
check_source "MLPerf数据"   "$OUTDIR/$SLUG/04-mlperf.md"
check_source "用户反馈"     "$OUTDIR/$SLUG/05-community.md"
check_source "安全公告"     "$OUTDIR/$SLUG/06-security.md"

echo ""
echo "--- 完整性评估 ---"
found=$(ls "$OUTDIR/$SLUG/"*.md 2>/dev/null | wc -l)
echo "已采集 $found/6 个信息源"
if [ "$found" -ge 4 ]; then
    echo "状态: ✅ 可进行分析 (≥4个信息源)"
else
    echo "状态: ⚠️ 信息不充分，建议补充采集"
fi
