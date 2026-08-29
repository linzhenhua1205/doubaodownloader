#!/usr/bin/env bash
# ============================================================
# run_all.sh — 会话意图分析一键执行
# 集成: ①导出近期会话 → ②提炼用户问题CSV → ③生成意图分析报告模板
# 用法:
#   ./run_all.sh                 # 全部(导出+CSV+报告模板)
#   ./run_all.sh --since 2026-08-07  # 指定起始日期
#   ./run_all.sh --no-export     # 跳过会话导出
#   ./run_all.sh --report-only   # 仅生成报告模板(用已有CSV)
# ============================================================
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.."

SINCE=""
DO_EXPORT=1
DO_CSV=1
DO_REPORT=1

while [ $# -gt 0 ]; do
  case "$1" in
    --since) SINCE="$2"; shift 2 ;;
    --no-export) DO_EXPORT=0; shift ;;
    --report-only) DO_EXPORT=0; DO_CSV=0; shift ;;
    *) echo "未知参数: $1"; exit 1 ;;
  esac
done

TODAY=$(date +%Y-%m-%d)
OUT_DIR="knowledge/weekly-reports/07_kb_stat/06_conversation"
CSV_FILE="$OUT_DIR/user-questions-$TODAY.csv"
REPORT_FILE="$OUT_DIR/conversation-intent-analysis-$TODAY.md"

log() { echo -e "\033[1;32m[intent]\033[0m $*"; }

# ---------- ① 导出近期会话 ----------
if [ "$DO_EXPORT" = 1 ]; then
  log "① 导出会话 → conversation-log/db-sessions/"
  python3 conversation-log/export_db_sessions.py
fi

# ---------- ② 提炼用户问题 CSV ----------
if [ "$DO_CSV" = 1 ]; then
  log "② 提炼用户问题 → $CSV_FILE"
  ARGS=()
  [ -n "$SINCE" ] && ARGS+=(--since "$SINCE")
  python3 scripts/intent_analysis/export_user_questions_csv.py "${ARGS[@]}"
fi

# ---------- ③ 生成意图分析报告(模板+数据摘要) ----------
if [ "$DO_REPORT" = 1 ]; then
  log "③ 生成意图分析报告 → $REPORT_FILE"
  python3 scripts/intent_analysis/gen_intent_report.py --csv "$CSV_FILE" --out "$REPORT_FILE"
fi

log "✅ 全部完成"
log "   CSV:   $CSV_FILE"
log "   报告:  $REPORT_FILE"
log "   下一步: 由 Agent 基于 CSV 执行 LLM 深度解析, 补全报告章节"
