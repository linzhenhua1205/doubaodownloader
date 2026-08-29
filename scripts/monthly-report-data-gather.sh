#!/usr/bin/env bash
# ============================================================
# monthly-report-data-gather.sh — 知识库月度报告数据采集脚本
# 功能：采集当月知识库变更/规模/领域/质量/洞察/待办六大类数据，
#       供 monthly-report-generator 技能生成月度报告（5 大维度）
# 运行：
#   ./scripts/monthly-report-data-gather.sh            # 采集当月（默认）
#   ./scripts/monthly-report-data-gather.sh 2026-07    # 指定月份 YYYY-MM
#   ./scripts/monthly-report-data-gather.sh --check    # 仅校验是否当月最后一天
# 输出：tmp/kb-monthly-data-{YYYY-MM}/
#   ├── metadata.json          → 元数据（月份/时间范围/校验结果）
#   ├── 00-commits.txt         → 当月 git 提交列表（全库 + knowledge/）
#   ├── 01-numstat.txt         → 当月增/删/改行数统计
#   ├── 02-module-dist.txt     → 当月按模块提交分布 + 新增文件分布
#   ├── 03-new-files.txt       → 当月新增文件清单
#   ├── 04-size-stats.txt      → 规模变化（文件数/行数/字节，当月 vs 上月末）
#   ├── 05-quality-snapshot.txt→ 质量快照（当月新增/修改文档格式检查通过率）
#   ├── 06-insights-sources.txt→ 洞察素材来源（当月 01_survey/memory 文件清单）
#   └── 07-todo-sources.txt    → 待办素材（当月 memory 中的 TODO/待办/下一步）
# 定时：cron "20 23 28-31 * *" + 脚本内最后一天校验（非最后一天自动退出）
# ============================================================
set -euo pipefail

WORKSPACE="${HOME}/cow"
KNOWLEDGE="${WORKSPACE}/knowledge"
cd "${WORKSPACE}"

# ---------- 参数解析 ----------
CHECK_ONLY=false
REPORT_MONTH=""
if [[ "$#" -ge 1 ]]; then
  case "$1" in
    --check) CHECK_ONLY=true ;;
    *) REPORT_MONTH="$1" ;;
  esac
fi

# ---------- 月份计算 ----------
if [[ -z "${REPORT_MONTH}" ]]; then
  TODAY=$(date +%Y-%m-%d)
  REPORT_MONTH=$(date +%Y-%m)
else
  TODAY=$(date +%Y-%m-%d)
fi

YM="${REPORT_MONTH}"
MONTH_START="${YM}-01"
# 当月最后一天（下月1号减1天）
NEXT_MONTH_START=$(date -d "${MONTH_START} +1 month" +%Y-%m-%d)
MONTH_END=$(date -d "${NEXT_MONTH_START} -1 day" +%Y-%m-%d)
MONTH_START_DATETIME="${MONTH_START} 00:00:00"
MONTH_END_DATETIME="${MONTH_END} 23:59:59"

# ---------- 最后一天校验（定时任务用）----------
TOMORROW_MONTH=$(date -d "tomorrow" +%Y-%m)
if [[ "${TOMORROW_MONTH}" != "$(date +%Y-%m)" ]]; then
  IS_LAST_DAY="true"
else
  IS_LAST_DAY="false"
fi

if [[ "${CHECK_ONLY}" == "true" ]]; then
  echo "{\"month\":\"${YM}\",\"is_last_day\":${IS_LAST_DAY},\"month_end\":\"${MONTH_END}\"}"
  exit 0
fi

# 指定月份但非当月最后一天时仍执行（支持回溯补采）；定时任务默认当月最后一天
# 若未指定月份且今天不是当月最后一天 → 提示但继续（便于手动测试）
if [[ -z "${1:-}" && "${IS_LAST_DAY}" != "true" ]]; then
  echo "⚠️  今天 $(date +%Y-%m-%d) 不是 ${YM} 的最后一天（${MONTH_END}），跳过采集（定时任务模式）。"
  echo "   手动指定月份可强制采集：./scripts/monthly-report-data-gather.sh ${YM}"
  exit 0
fi

# ---------- 输出目录 ----------
OUT_DIR="${WORKSPACE}/tmp/kb-monthly-data-${YM}"
mkdir -p "${OUT_DIR}"

echo "📊 知识库月度报告数据采集 — ${YM} (${MONTH_START} ~ ${MONTH_END})"
echo "  输出目录: ${OUT_DIR}"

# ---------- 1. 提交列表 ----------
{
  echo "# 当月 Git 提交列表（${YM}）"
  echo "## 全库提交（含 scripts/skills/spec 等）"
  git log --since="${MONTH_START_DATETIME}" --until="${MONTH_END_DATETIME}" \
    --pretty="%h | %ad | %s" --date=format:"%Y-%m-%d %H:%M" --all | head -2000
  echo ""
  echo "## knowledge/ 提交（仅知识库）"
  git log --since="${MONTH_START_DATETIME}" --until="${MONTH_END_DATETIME}" \
    --pretty="%h | %ad | %s" --date=format:"%Y-%m-%d %H:%M" --all -- knowledge/ | head -2000
} > "${OUT_DIR}/00-commits.txt"

# ---------- 2. 增删改统计 ----------
{
  echo "# 当月变更行数统计（${YM}）"
  echo "## 全库增删改"
  git log --since="${MONTH_START_DATETIME}" --until="${MONTH_END_DATETIME}" \
    --numstat --pretty="%H" --all \
    | awk '/^[0-9]/{add+=$1; del+=$2; files++} END{printf "增加行数: %d\n删除行数: %d\n变更文件数: %d\n", add, del, files}'
  echo ""
  echo "## knowledge/ 增删改"
  git log --since="${MONTH_START_DATETIME}" --until="${MONTH_END_DATETIME}" \
    --numstat --pretty="%H" --all -- knowledge/ \
    | awk '/^[0-9]/{add+=$1; del+=$2; files++} END{printf "增加行数: %d\n删除行数: %d\n变更文件数: %d\n", add, del, files}'
  echo ""
  echo "## 当月提交总数"
  echo "全库: $(git log --since="${MONTH_START_DATETIME}" --until="${MONTH_END_DATETIME}" --oneline --all | wc -l)"
  echo "knowledge/: $(git log --since="${MONTH_START_DATETIME}" --until="${MONTH_END_DATETIME}" --oneline --all -- knowledge/ | wc -l)"
  echo "scripts/: $(git log --since="${MONTH_START_DATETIME}" --until="${MONTH_END_DATETIME}" --oneline --all -- scripts/ | wc -l)"
  echo "skills/: $(git log --since="${MONTH_START_DATETIME}" --until="${MONTH_END_DATETIME}" --oneline --all -- skills/ | wc -l)"
  echo ""
  echo "## 新增/删除/重命名文件（knowledge/）"
  echo "新增: $(git log --since="${MONTH_START_DATETIME}" --until="${MONTH_END_DATETIME}" --diff-filter=A --name-only --pretty="" --all -- knowledge/ | grep -v '^$' | wc -l)"
  echo "删除: $(git log --since="${MONTH_START_DATETIME}" --until="${MONTH_END_DATETIME}" --diff-filter=D --name-only --pretty="" --all -- knowledge/ | grep -v '^$' | wc -l)"
  echo "重命名: $(git log --since="${MONTH_START_DATETIME}" --until="${MONTH_END_DATETIME}" --diff-filter=R --name-status --pretty="" --all -- knowledge/ | grep -v '^$' | wc -l)"
} > "${OUT_DIR}/01-numstat.txt"

# ---------- 3. 模块分布（领域侧重） ----------
{
  echo "# 当月领域分布（${YM}）"
  echo "## 按 knowledge/ 顶层模块提交数"
  git log --since="${MONTH_START_DATETIME}" --until="${MONTH_END_DATETIME}" \
    --oneline --name-only --pretty="" --all -- knowledge/ \
    | grep -v '^$' | grep -oE "^knowledge/[^/]+" | sort | uniq -c | sort -rn
  echo ""
  echo "## 按 knowledge/ 顶层模块新增文件数"
  git log --since="${MONTH_START_DATETIME}" --until="${MONTH_END_DATETIME}" \
    --diff-filter=A --name-only --pretty="" --all -- knowledge/ \
    | grep -v '^$' | grep -oE "^knowledge/[^/]+" | sort | uniq -c | sort -rn
  echo ""
  echo "## 当月新增 md 文件（knowledge/，最新优先）"
  git log --since="${MONTH_START_DATETIME}" --until="${MONTH_END_DATETIME}" \
    --diff-filter=A --name-only --pretty="" --all -- knowledge/ \
    | grep -E "\.md$" | sort -u | tail -100
} > "${OUT_DIR}/02-module-dist.txt"

# ---------- 4. 新增文件清单 ----------
git log --since="${MONTH_START_DATETIME}" --until="${MONTH_END_DATETIME}" \
  --diff-filter=A --name-only --pretty="" --all -- knowledge/ \
  | grep -v '^$' | sort -u > "${OUT_DIR}/03-new-files.txt"

# ---------- 5. 规模变化 ----------
{
  echo "# 知识库规模变化（${YM} 末 vs 上月末）"
  # 当月最后一天的工作树快照（用 git archive 或直接统计当前目录）
  echo "## 当前规模（${TODAY} 实测）"
  echo "md 文件数: $(find "${KNOWLEDGE}" -name '*.md' -type f | wc -l)"
  echo "md 总行数: $(find "${KNOWLEDGE}" -name '*.md' -type f -exec cat {} + | wc -l)"
  echo "总文件数: $(find "${KNOWLEDGE}" -type f | wc -l)"
  echo "顶层子目录数: $(find "${KNOWLEDGE}" -mindepth 1 -maxdepth 1 -type d | wc -l)"
  echo ""
  echo "## 各顶层模块 md 文件数"
  for mod in $(find "${KNOWLEDGE}" -mindepth 1 -maxdepth 1 -type d | sort); do
    name=$(basename "${mod}")
    cnt=$(find "${mod}" -name '*.md' -type f | wc -l)
    echo "  ${name}: ${cnt}"
  done
  echo ""
  echo "## 当月新增文件 TOP 目录（知识库）"
  git log --since="${MONTH_START_DATETIME}" --until="${MONTH_END_DATETIME}" \
    --diff-filter=A --name-only --pretty="" --all -- knowledge/ \
    | grep -v '^$' | sed 's|/[^/]*$||' | sort | uniq -c | sort -rn | head -20
} > "${OUT_DIR}/04-size-stats.txt"

# ---------- 6. 质量快照 ----------
{
  echo "# 知识库质量快照（${YM} 当月新增/修改文档）"
  echo "## 格式检查（check_md_format.py，抽样当月新增 md 文件）"
  # 取当月新增的 md 文件（最多 15 个），运行格式检查
  NEW_MD=$(git log --since="${MONTH_START_DATETIME}" --until="${MONTH_END_DATETIME}" \
    --diff-filter=A --name-only --pretty="" --all -- knowledge/ \
    | grep -E "\.md$" | grep -v "weekly-reports" | sort -u | tail -15 || true)
  PASS=0; FAIL=0; FAIL_LIST=""
  if [[ -n "${NEW_MD}" ]]; then
    while IFS= read -r f; do
      if [[ -f "${WORKSPACE}/${f}" ]]; then
        if python3 "${WORKSPACE}/scripts/check_md_format.py" "${WORKSPACE}/${f}" >/dev/null 2>&1; then
          PASS=$((PASS+1))
        else
          FAIL=$((FAIL+1)); FAIL_LIST="${FAIL_LIST}  ${f}\n"
        fi
      fi
    done <<< "${NEW_MD}"
  fi
  echo "抽样文件数: $((PASS+FAIL))"
  echo "通过: ${PASS} | 未通过: ${FAIL}"
  [[ -n "${FAIL_LIST}" ]] && printf "未通过列表:\n${FAIL_LIST}"
  echo ""
  echo "## 质量深度检查（check_tech_doc_quality.py，抽样当月新增大文档）"
  BIG_MD=$(git log --since="${MONTH_START_DATETIME}" --until="${MONTH_END_DATETIME}" \
    --diff-filter=A --name-only --pretty="" --all -- knowledge/ \
    | grep -E "\.md$" | grep -v "weekly-reports" | sort -u | tail -5 || true)
  if [[ -n "${BIG_MD}" ]]; then
    while IFS= read -r f; do
      if [[ -f "${WORKSPACE}/${f}" ]]; then
        echo "### ${f}"
        python3 "${WORKSPACE}/scripts/check_tech_doc_quality.py" "${WORKSPACE}/${f}" 2>&1 | grep -E "综合|通过|问题" | head -3 || true
      fi
    done <<< "${BIG_MD}"
  fi
} > "${OUT_DIR}/05-quality-snapshot.txt"

# ---------- 7. 洞察素材 ----------
{
  echo "# 月度行业洞察素材来源（${YM}）"
  echo "## 当月调研跟踪文件（01_survey 下 ${YM} 前缀）"
  find "${KNOWLEDGE}/01_survey" -name "${YM}-*.md" -type f 2>/dev/null | sort | head -80
  echo ""
  echo "## 当月记忆文件"
  find "${WORKSPACE}/memory" -name "${YM}-*.md" -type f 2>/dev/null | sort
  echo ""
  echo "## 当月周报"
  find "${KNOWLEDGE}/weekly-reports/01_weekly" -name "*-${YM}*" -type f 2>/dev/null | sort
  echo ""
  echo "## 当月行业研究（07_industry-research 下 ${YM} 前缀）"
  find "${KNOWLEDGE}/07_industry-research" -name "${YM}-*.md" -type f 2>/dev/null | sort | head -60
} > "${OUT_DIR}/06-insights-sources.txt"

# ---------- 8. 待办素材 ----------
{
  echo "# 月度待办素材（${YM} 记忆文件中的待办/下一步/风险）"
  for f in $(find "${WORKSPACE}/memory" -name "${YM}-*.md" -type f 2>/dev/null | sort); do
    echo "### ${f}"
    grep -nE "待办|TODO|下一步|后续|行动计划|未完成|风险|遗留" "${f}" | head -20 || true
  done
  echo ""
  echo "## MEMORY.md 中的行动项"
  grep -nE "待办|TODO|下一步|行动|计划" "${WORKSPACE}/MEMORY.md" 2>/dev/null | head -20 || true
} > "${OUT_DIR}/07-todo-sources.txt"

# ---------- 元数据 ----------
cat > "${OUT_DIR}/metadata.json" << EOF
{
  "month": "${YM}",
  "period": "${MONTH_START} ~ ${MONTH_END}",
  "collected_at": "$(date '+%Y-%m-%d %H:%M:%S')",
  "is_last_day": ${IS_LAST_DAY},
  "total_commits": $(git log --since="${MONTH_START_DATETIME}" --until="${MONTH_END_DATETIME}" --oneline --all | wc -l),
  "kb_commits": $(git log --since="${MONTH_START_DATETIME}" --until="${MONTH_END_DATETIME}" --oneline --all -- knowledge/ | wc -l),
  "new_md_files": $(git log --since="${MONTH_START_DATETIME}" --until="${MONTH_END_DATETIME}" --diff-filter=A --name-only --pretty="" --all -- knowledge/ | grep -E "\.md$" | wc -l),
  "output_dir": "tmp/kb-monthly-data-${YM}"
}
EOF

echo ""
echo "✅ 采集完成 → ${OUT_DIR}"
echo "   metadata.json: $(cat "${OUT_DIR}/metadata.json")"
