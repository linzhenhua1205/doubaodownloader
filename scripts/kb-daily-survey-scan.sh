#!/usr/bin/env bash
#================================================================
# kb-daily-survey-scan.sh v3 — 扫描 01_survey/ 下日报时间窗口内的跟踪文件
#
# 用途：找出 knowledge/01_survey/ 下匹配日报时间窗口的跟踪文件
#       用于日报 Pillar 1（每日洞察技术要点），从调研跟踪文件中提取技术发现。
#
# 时间窗口：[REPORT_DATE 08:00 → REPORT_DATE+1 08:10]
# 匹配策略：匹配 REPORT_DATE* 和 REPORT_DATE+1* 两类文件名
#           （因为 00:00~08:10 的文件以次日日期命名）
#
# 用法：
#   ./scripts/kb-daily-survey-scan.sh                    # 上一日
#   ./scripts/kb-daily-survey-scan.sh 2026-07-28         # 指定日期
#
# 输出：
#   - stdout：每行一个文件路径（供管道/脚本消费）
#   - stderr：带统计的概览信息
#   - tmp/kb-daily-survey-{REPORT_DATE}.txt：详细报表
#
# 变更日志：
#   2026-07-29 v3 匹配两日模式（REPORT_DATE 和 REPORT_DATE+1）以覆盖 00:00~08:10
#   2026-07-29 v2 注释更新为日报时间窗口语义，功能不变
#   2026-07-29 v1 created
#================================================================

set -euo pipefail

WORKSPACE="$HOME/cow"
REPORT_DATE="${1:-$(date +%Y-%m-%d)}"
OUTPUT_FILE="${WORKSPACE}/tmp/kb-daily-survey-${REPORT_DATE}.txt"

# 计算次日（REPORT_DATE+1），匹配 00:00~08:10 的文件
NEXT_DATE=$(date -d "${REPORT_DATE} + 1 day" +%Y-%m-%d 2>/dev/null || echo "")

cd "$WORKSPACE"

echo ">>> 调研跟踪扫描: ${REPORT_DATE}（窗口 ${REPORT_DATE} 08:00 -> ${NEXT_DATE} 08:10）" >&2

# Step 1: 扫描 01_survey/ 下所有子目录的日期匹配文件
declare -A survey_files
declare -A survey_lines

total_files=0
total_lines=0

for dir in knowledge/01_survey/*/; do
  dirname=$(basename "$dir")

  while IFS= read -r -d '' file; do
    fname=$(basename "$file")

    matched=false
    if [[ "$fname" =~ ^(${REPORT_DATE})(-.*)?\.md$ ]]; then
      matched=true
    elif [[ -n "$NEXT_DATE" && "$fname" =~ ^(${NEXT_DATE})(-.*)?\.md$ ]]; then
      matched=true
    fi

    if $matched; then
      lines=$(wc -l < "$file")
      survey_files["$file"]="${dirname}"
      survey_lines["$file"]=$lines
      total_files=$((total_files + 1))
      total_lines=$((total_lines + lines))
    fi
  done < <(find "$dir" -maxdepth 1 -name "*.md" -print0 2>/dev/null)
done

# Step 2: 输出详细报表
{
  echo "# kb-daily-survey-scan: ${REPORT_DATE}"
  echo "# 窗口: ${REPORT_DATE} 08:00 -> ${NEXT_DATE} 08:10"
  echo "# 匹配模式: ${REPORT_DATE}* + ${NEXT_DATE}*"
  echo "#"
  printf "# %-12s %-50s %7s\n" "DIR" "FILE" "LINES"
  printf "# %-12s %-50s %7s\n" "------------" "-------------------------------------------------" "-------"

  for file in $(echo "${!survey_files[@]}" | tr ' ' '\n' | sort); do
    dirname="${survey_files[$file]}"
    lines="${survey_lines[$file]}"
    fname=$(basename "$file")
    printf "  %-12s %-50s %7d\n" "$dirname" "$fname" "$lines"
  done
  echo "#"
  echo "# 总计: ${total_files} 个文件, ${total_lines} 行"
} > "$OUTPUT_FILE"

# Step 3: stdout 输出文件列表
for file in $(echo "${!survey_files[@]}" | tr ' ' '\n' | sort); do
  echo "$file"
done

# Step 4: stderr 输出概览
echo "" >&2
echo "===== ${REPORT_DATE} 调研跟踪文件 =====" >&2
for file in $(echo "${!survey_files[@]}" | tr ' ' '\n' | sort); do
  dirname="${survey_files[$file]}"
  lines="${survey_lines[$file]}"
  fname=$(basename "$file")
  printf "  [%-12s] %-50s %5d 行\n" "$dirname" "$fname" "$lines" >&2
done
echo "" >&2
echo ">>> 总计: ${total_files} 个文件, ${total_lines} 行" >&2
echo ">>> 已保存: ${OUTPUT_FILE}" >&2
