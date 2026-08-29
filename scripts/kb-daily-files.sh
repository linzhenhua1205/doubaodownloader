#!/usr/bin/env bash
#================================================================
# kb-daily-files.sh v3 — git-based 单日 knowledge 大变更文件排查
#
# 背景：v1 使用 find -newermt（文件修改时间戳），因 git 操作
#       后 mtime 不准，且无变更量过滤，输出不准确。
#
# 用途：找出 knowledge/ 下 git commit 变更超 100 行的文件
#       （排除 01_survey/、weekly-reports/ 目录）
#
# 时间窗口：[REPORT_DATE 08:00 → (REPORT_DATE+1) 08:10]
#       参数为 REPORT_DATE（报告覆盖日期），自动推算结束时间。
#       与日报时间窗口完全对齐。
#
# 方法：git log 获取时间窗口内所有涉及 knowledge/ 的 commit →
#       git diff-tree --numstat 精确统计每文件插入/删除行数 →
#       合计单日变更总量 → 过滤 >100 行 → 降序输出
#
# 用法：
#   ./scripts/kb-daily-files.sh                    # 上一日（日报模式）
#   ./scripts/kb-daily-files.sh 2026-07-28         # 指定报告日期
#
# 输出：
#   - stdout：每行一个文件路径（供管道/脚本消费）
#   - stderr：概览信息
#   - tmp/kb-daily-files-{日期}.txt：含变更量统计的详细报表
#
# 变更日志：
#   2026-07-29 v3 时间窗口改为 [REPORT_DATE 08:00 → NEXT_DAY 08:10]
#   2026-07-28 v2 rewrite: git-based 替代 mtime-based
#      - 精确每文件插入+删除行数
#      - 过滤 >100 行变更
#      - 排除 01_survey/、weekly-reports/
#      - 降序排列
#================================================================

set -euo pipefail

WORKSPACE="$HOME/cow"
REPORT_DATE="${1:-$(date -d "yesterday" +%Y-%m-%d)}"
NEXT_DAY=$(date -d "${REPORT_DATE} +1 day" +%Y-%m-%d)
OUTPUT_FILE="${WORKSPACE}/tmp/kb-daily-files-${REPORT_DATE}.txt"
WINDOW_AFTER="${REPORT_DATE}T08:00:00"
WINDOW_BEFORE="${NEXT_DAY}T08:10:00"

cd "$WORKSPACE"

echo "📊 分析日期: ${REPORT_DATE}（时间窗口: ${WINDOW_AFTER} → ${WINDOW_BEFORE}）" >&2

#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Step 1: 获取当日所有涉及 knowledge/ 的 commits
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
commits=$(git log --after="${WINDOW_AFTER}" --before="${WINDOW_BEFORE}" \
  --format="%H" -- "knowledge/" ":^knowledge/01_survey/" 2>/dev/null)

if [ -z "$commits" ]; then
  echo "⚠️  当日无涉及 knowledge/ 的 commit" >&2
  > "$OUTPUT_FILE"
  exit 0
fi

commit_count=$(echo "$commits" | wc -l)
echo "🔍 当日 ${commit_count} 个 commit 涉及 knowledge/" >&2

#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Step 2: 遍历每个 commit，用 --numstat 累计每文件变更
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
declare -A file_add
declare -A file_del

for hash in $commits; do
  # diff-tree 比 diff $hash^..$hash 更稳健（处理首个 commit）
  while IFS=$'\t' read -r added deleted filepath; do
    # 跳过 binary 文件（numstat 中 binary 显示为 -）
    [[ "$added" == "-" ]] && continue
    # 只处理 knowledge/ 下的 markdown 文件
    [[ "$filepath" != knowledge/*.md ]] && continue
    # 排除 01_survey/
    [[ "$filepath" == knowledge/01_survey/* ]] && continue
    # 排除 weekly-reports/
    [[ "$filepath" == knowledge/weekly-reports/* ]] && continue

    file_add["$filepath"]=$(( ${file_add["$filepath"]:-0} + added ))
    file_del["$filepath"]=$(( ${file_del["$filepath"]:-0} + deleted ))
  done < <(git diff-tree --no-commit-id -r --numstat "$hash" 2>/dev/null)
done

#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Step 3: 过滤 >100 行并输出
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 3a: 详细报表 → 输出文件
{
  echo "# kb-daily-files: ${REPORT_DATE}"
  echo "# 单日变更 >100 行的 knowledge 文件（排除 01_survey / weekly-reports）"
  echo "# 来源: git log + git diff-tree --numstat"
  echo "# 排序: 变更总量（+/- 之和）降序"
  echo "#"
  printf "# %-90s %7s %7s %7s\n" "FILE" "ADD" "DEL" "TOTAL"
  printf "# %-90s %7s %7s %7s\n" "------------------------------------------------------------------------------------------" "-------" "-------" "-------"

  # 收集 >100 行的结果，先存临时数组以便排序
  results=()
  for filepath in "${!file_add[@]}"; do
    total=$(( file_add["$filepath"] + file_del["$filepath"] ))
    [ "$total" -le 100 ] && continue
    results+=("$(printf "%07d %s" "$total" "$filepath")")
  done

  # 降序排序
  IFS=$'\n' sorted=($(sort -rn <<<"${results[*]}"))
  unset IFS

  for entry in "${sorted[@]}"; do
    total="${entry:0:7}"
    total=$((10#$total))  # 去掉前导零
    filepath="${entry:8}"
    printf "%-90s %7d %7d %7d\n" "$filepath" "${file_add[$filepath]}" "${file_del[$filepath]}" "$total"
  done
} > "$OUTPUT_FILE"

# 3b: 文件路径列表 → stdout（供管道消费，兼容原有调用方）
total_files=0
for entry in "${sorted[@]}"; do
  filepath="${entry:8}"
  echo "$filepath"
  total_files=$((total_files + 1))
done

# 3c: 概览 → stderr
echo "" >&2
if [ "$total_files" -eq 0 ]; then
  echo "⚠️  当日无 knowledge 文件变更超过 100 行" >&2
else
  echo "===== >100 行变更的 knowledge 文件（排除 01_survey/weekly-reports）=====" >&2
  for entry in "${sorted[@]}"; do
    total="${entry:0:7}"
    total=$((10#$total))
    filepath="${entry:8}"
    printf "  %4d 行  %s\n" "$total" "$filepath" >&2
  done
fi
echo "" >&2
echo "✅ 已保存: ${OUTPUT_FILE}（${total_files} 个文件 >100 行）" >&2
