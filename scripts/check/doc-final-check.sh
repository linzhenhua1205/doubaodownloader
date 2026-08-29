#!/usr/bin/env bash
# =============================================================================
# doc-final-check.sh — 知识库文档产出门禁「快速通道」 v1.1
#
# 目的：把多个 skill 要求的 4+ 个串行 check 合一，默认只输出 FAIL 摘要 +
#       通过计数，避免全量输出回读污染上下文。
#
# 用法：
#   doc-final-check.sh <目标路径>              # 快速模式（默认）：必错项 2 项
#   doc-final-check.sh <目标路径> --full       # 完整模式：深度文档全量 4 项
#   doc-final-check.sh <目标路径> --fix        # 自动修复 R1 后重查
#   doc-final-check.sh <目标路径> --skip-links # 跳过链接检查
#
# 退出码：0=全部通过；1=有 FAIL；2=用法错误
# 设计原则：轻量优先、容忍弹性——fast 只拦「必错项」，full 才是发布门禁。
# =============================================================================
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$WORKSPACE_ROOT"
export PYTHONPATH="$WORKSPACE_ROOT${PYTHONPATH:+:$PYTHONPATH}"

TARGET="${1:-}"; MODE="fast"; DO_FIX=0; SKIP_LINKS=0
for arg in "${@:2}"; do
  case "$arg" in
    --full) MODE="full" ;;
    --fix)  DO_FIX=1 ;;
    --skip-links) SKIP_LINKS=1 ;;
    *) echo "⚠️ 未知参数: $arg" >&2 ;;
  esac
done

if [[ -z "$TARGET" ]]; then
  echo "用法: doc-final-check.sh <目标路径> [--full|--fix|--skip-links]"
  exit 2
fi
[[ -e "$TARGET" ]] || { echo "❌ 目标不存在: $TARGET"; exit 2; }

if [[ -t 1 ]]; then
  RED=$'\033[31m'; GREEN=$'\033[32m'; YELLOW=$'\033[33m'; NC=$'\033[0m'
else RED=""; GREEN=""; YELLOW=""; NC=""; fi

pass=0; fail=0

# run_check <name> <判定表达式> <命令...>
# 判定表达式用变量 $out $rc：返回 0=通过，1=FAIL
run_check() {
  local name="$1"; local judge="$2"; shift 2
  local out rc verdict
  out="$("$@" 2>&1)"; rc=$?
  if eval "$judge"; then
    pass=$((pass+1)); echo "  ${GREEN}✅${NC} $name"
  else
    fail=$((fail+1)); echo "  ${RED}❌${NC} $name (exit=$rc)"
    echo "$out" | grep -E '✗|❌|FAIL|Error|error' | grep -vE 'Missing\s*0|missing\s*0|Truly Missing\s*0' \
      | sed 's/\x1b\[[0-9;]*m//g' | head -12 | sed 's/^/      /'
  fi
}

echo "════════════════════════════════════════════════════════"
echo "📋 doc-final-check ($MODE) — $TARGET"
echo "════════════════════════════════════════════════════════"

if [[ "$MODE" == "fast" ]]; then
  # ── fast：只拦必错项（2 项，<3s） ──
  FIX_FLAG=""; [[ $DO_FIX -eq 1 ]] && FIX_FLAG="--fix"
  run_check "格式必错项 (check_md_format R1)" \
    'r1=$(echo "$out" | grep -oE "R1 \(must-fix\):\s*[0-9]+" | grep -oE "[0-9]+$"); [[ -z "$r1" || "$r1" -eq 0 ]]' \
    python3 scripts/check_md_format.py "$TARGET" $FIX_FLAG
  if [[ $SKIP_LINKS -eq 0 && -f "$TARGET" && "$TARGET" == knowledge/*.md ]]; then
    run_check "链接有效性 (link-validator)" \
      'miss=$(echo "$out" | grep -oE "Truly Missing\s*[0-9]+" | grep -oE "[0-9]+$"); [[ -z "$miss" || "$miss" -eq 0 ]]' \
      python3 scripts/check/link-validator.py --file "${TARGET#knowledge/}" --no-external
  else
    echo "  ${YELLOW}⏭️${NC} 链接校验跳过"
  fi
else
  # ── full：深度文档发布门禁（4 项） ──
  FIX_FLAG=""; [[ $DO_FIX -eq 1 ]] && FIX_FLAG="--fix"
  run_check "格式 R1-R6 (check_format)" \
    'f=$(echo "$out" | grep -E "✗|❌" | grep -vE "0个链接|Missing 0"); [[ -z "$f" ]]' \
    python3 skills/knowledge-doc-writer/scripts/check_format.py "$TARGET" $FIX_FLAG
  if [[ -f "$TARGET" && "$TARGET" == knowledge/* ]]; then
    run_check "策略合规 (strategy-compliance)" \
      '! echo "$out" | grep -qiE "FAIL|不通过|✗"' \
      python3 scripts/check/strategy-compliance.py "${TARGET#knowledge/}"
    run_check "T4 格式 (format-validator)" \
      '! echo "$out" | grep -qiE "FAIL|不通过|✗"' \
      python3 scripts/check/format-validator.py "${TARGET#knowledge/}"
    run_check "链接有效性 (link-validator)" \
      'miss=$(echo "$out" | grep -oE "Truly Missing\s*[0-9]+" | grep -oE "[0-9]+$"); [[ -z "$miss" || "$miss" -eq 0 ]]' \
      python3 scripts/check/link-validator.py --file "${TARGET#knowledge/}" --no-external
  fi
fi

echo "────────────────────────────────────────────────────────"
if [[ $fail -eq 0 ]]; then
  echo "  ${GREEN}✅ 全部通过 ($pass 项)${NC}"; exit 0
else
  echo "  ${RED}⚠️ 通过 $pass / FAIL $fail${NC}"
  echo "  💡 --skip-links 跳过链接；--fix 自动修复；--full 完整门禁"
  exit 1
fi
