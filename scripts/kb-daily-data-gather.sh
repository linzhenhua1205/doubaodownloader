#!/usr/bin/env bash
#================================================================
# kb-daily-data-gather.sh v3 — 日报数据统一采集器
#
# 用途：单入口收集日报所需全部原始数据，输出规范化供日报生成消费。
#       保证 kb-daily-files.sh（深度文档）和 kb-daily-survey-scan.sh
#       （跟踪文件）总是先于日报生成被调用。
#
# 时间窗口：[REPORT_DATE 08:00 → TODAY 08:10]
#   - REPORT_DATE = 上一日（日报覆盖的日期）
#   - TODAY       = 当前日期（执行日报生成的日期）
#   例如 2026-07-29 09:42 → report=2026-07-28, window=07-28 08:00~07-29 08:10
#
# 数据源：
#   1. kb-daily-files.sh        → 深度文档（git knowledge/ 排除 01_survey）
#   2. kb-daily-survey-scan.sh  → 调研跟踪文件（01_survey/ 下日期匹配）
#   3. git log                  → 当日提交（只关注 knowledge/ 排除 01_survey）
#   4. memory/<report_date>.md  → 记忆文件中的操作要点
#   5. skills/ scripts/ 变更    → 工具本身更新
#
# 用法：
#   ./scripts/kb-daily-data-gather.sh                    # 上一日（日报）
#   ./scripts/kb-daily-data-gather.sh 2026-07-28         # 指定报告日期
#
# 输出：
#   tmp/kb-daily-data-{REPORT_DATE}/                   — 数据目录
#     ├── metadata.json                                 — 元数据摘要
#     ├── 00-commits.txt                                — 按时间窗口的 git commit
#     ├── 01-depth-files.txt                            — kb-daily-files.sh 输出
#     ├── 02-survey-files.txt                           — kb-daily-survey-scan.sh 输出
#     ├── 03-file-stats-all.txt                         — 知识库文件变更统计（不含 survey）
#     ├── 04-memory-stats.txt                           — 记忆文件状态与操作要点
#     ├── 05-scripts-skills-changes.txt                 — scripts/skills 变更
#     └── 06-git-log-detailed.txt                       — 详细 git log（含 commit body）
#
# 变更日志：
#   2026-07-29 v2 时间窗口改为 [REPORT_DATE 08:00 → TODAY 08:10]
#     - git 只关注 knowledge/ 目录，排除 01_survey/
#     - memory 关注 report_date 文件中的操作要点
#     - 自动计算上一日为默认报告日期
#   2026-07-29 v1 created
#================================================================

set -euo pipefail

WORKSPACE="$HOME/cow"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 日期计算：REPORT_DATE = 上一日（默认）
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REPORT_DATE="${1:-}"
if [ -z "$REPORT_DATE" ]; then
  # 默认取上一日（[上一日 08:00 → 今日 08:10] 窗口的"上一日"）
  REPORT_DATE=$(date -d "yesterday" +%Y-%m-%d)
fi

# TODAY = REPORT_DATE + 1 天（窗口结束日）
TODAY=$(date -d "${REPORT_DATE} +1 day" +%Y-%m-%d)

DATA_DIR="${WORKSPACE}/tmp/kb-daily-data-${REPORT_DATE}"

mkdir -p "$DATA_DIR"
cd "$WORKSPACE"

echo "📊 kb-daily-data-gather v3 — 日报数据采集" >&2
echo "   报告日期: ${REPORT_DATE} (时间窗口: ${REPORT_DATE} 08:00 → ${TODAY} 08:10)" >&2
echo "   输出目录: ${DATA_DIR}" >&2
# ⚠️ 日报文件名 = TODAY（生成当日），勿用 REPORT_DATE 命名（08-11 教训：曾险些覆盖已存在日报）
REPORT_FILE="${WORKSPACE}/knowledge/weekly-reports/00_daily/${TODAY}.md"
echo "   ⚠️ 日报文件名: ${REPORT_FILE} —— 按生成当日 TODAY 命名，脚本输出目录按 REPORT_DATE（昨日）命名，两者不同" >&2
echo "   （若该文件已存在，先核对内容与生成时间确定窗口归属，避免覆盖）" >&2
printf '%s\n' "${REPORT_FILE}" > "${DATA_DIR}/REPORT_FILENAME.txt"
echo "" >&2

#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Step 1: Git 提交信息（时间窗口内，仅 knowledge/ 下，排除 01_survey/）
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "▶ Step 1/7: Git 提交信息（knowledge/，排除 01_survey/）..." >&2

window_after="${REPORT_DATE}T08:00:00"
window_before="${TODAY}T08:10:00"

echo "   时间窗口: ${window_after} → ${window_before}" >&2

# 1a: 简要列表（只关注 knowledge/ 下的提交，排除 01_survey/）
git log --after="${window_after}" --before="${window_before}" \
  --format="%H %s" -- "knowledge/" ":^knowledge/01_survey/" \
  -- > "${DATA_DIR}/00-commits.txt" 2>/dev/null || true

commit_count=$(wc -l < "${DATA_DIR}/00-commits.txt" 2>/dev/null || echo 0)
echo "  → ${commit_count} 个 knowledge/ commit（排除 01_survey/）" >&2

# 1b: 详细 log（含 body）
git log --after="${window_after}" --before="${window_before}" \
  --format="COMMIT %H%nAuthor: %an <%ae>%nDate: %ai%nSubject: %s%n%n%b%n---" \
  -- "knowledge/" ":^knowledge/01_survey/" \
  -- > "${DATA_DIR}/06-git-log-detailed.txt" 2>/dev/null || true

# 1c: 提取 commit hashes 供后续统计使用
commits=$(git log --after="${window_after}" --before="${window_before}" \
  --format="%H" -- "knowledge/" ":^knowledge/01_survey/" \
  -- 2>/dev/null || true)

#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Step 2: 调研跟踪文件扫描（01_survey/ 下日期匹配）
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "▶ Step 2/7: 调研跟踪文件扫描（${REPORT_DATE}）..." >&2

if [ -x "${SCRIPT_DIR}/kb-daily-survey-scan.sh" ]; then
  bash "${SCRIPT_DIR}/kb-daily-survey-scan.sh" "${REPORT_DATE}" > "${DATA_DIR}/02-survey-files.txt" 2>/dev/null
  survey_count=$(wc -l < "${DATA_DIR}/02-survey-files.txt" 2>/dev/null || echo 0)
  # 同时读取详细报表中的总行数
  survey_lines=$(grep "^# 总计" "${WORKSPACE}/tmp/kb-daily-survey-${REPORT_DATE}.txt" 2>/dev/null | grep -oP '\d+(?= 行)' || echo 0)
  echo "  → ${survey_count} 个跟踪文件" >&2
else
  echo "  ⚠️  kb-daily-survey-scan.sh 不可执行，跳过" >&2
  survey_count=0
  survey_lines=0
fi

#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Step 3: 深度文档扫描（git knowledge/ 排除 01_survey/ 和 weekly-reports/）
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "▶ Step 3/7: 深度文档扫描（>100行，排除 survey/weekly）..." >&2

if [ -x "${SCRIPT_DIR}/kb-daily-files.sh" ]; then
  bash "${SCRIPT_DIR}/kb-daily-files.sh" "${REPORT_DATE}" > "${DATA_DIR}/01-depth-files.txt" 2>/dev/null
  depth_count=$(wc -l < "${DATA_DIR}/01-depth-files.txt" 2>/dev/null || echo 0)
  echo "  → ${depth_count} 个深度文档" >&2
else
  echo "  ⚠️  kb-daily-files.sh 不可执行，跳过" >&2
  depth_count=0
fi

#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Step 4: 知识库文件变更统计（按时间窗口，仅 knowledge/，排除 01_survey/）
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "▶ Step 4/7: 全知识库文件变更统计（排除 01_survey）..." >&2

{
  echo "# 单日知识库文件按目录分组变更统计（时间窗口: ${window_after} → ${window_before}）"
  echo "# 仅 knowledge/，排除 01_survey/"
  echo "#"
  printf "# %-50s %7s %7s %7s\n" "FILE" "ADD" "DEL" "TOTAL"
  printf "# %-50s %7s %7s %7s\n" "--------------------------------------------------" "-------" "-------" "-------"

  if [ -n "$commits" ]; then
    declare -A f_add f_del
    for hash in $commits; do
      while IFS=$'\t' read -r added deleted filepath; do
        [[ "$added" == "-" ]] && continue
        [[ "$filepath" != knowledge/*.md ]] && continue
        [[ "$filepath" == knowledge/01_survey/* ]] && continue
        f_add["$filepath"]=$(( ${f_add["$filepath"]:-0} + added ))
        f_del["$filepath"]=$(( ${f_del["$filepath"]:-0} + deleted ))
      done < <(git diff-tree --no-commit-id -r --numstat "$hash" 2>/dev/null)
    done

    results=()
    for filepath in "${!f_add[@]}"; do
      total=$(( f_add["$filepath"] + f_del["$filepath"] ))
      results+=("$(printf "%07d %s" "$total" "$filepath")")
    done

    IFS=$'\n' sorted=($(sort -rn <<<"${results[*]}")); unset IFS

    added_total=0; deleted_total=0; total_total=0
    for entry in "${sorted[@]}"; do
      tot="${entry:0:7}"; tot=$((10#$tot))
      fp="${entry:8}"
      printf "%-50s %7d %7d %7d\n" "${fp:0:50}" "${f_add[$fp]}" "${f_del[$fp]}" "$tot"
      added_total=$((added_total + f_add[$fp]))
      deleted_total=$((deleted_total + f_del[$fp]))
      total_total=$((total_total + tot))
    done
    echo "#"
    echo "# 合计: +${added_total} / -${deleted_total} / ${total_total} 总变更行"
  else
    echo "# 时间窗口内无知识库 commit"
  fi
} > "${DATA_DIR}/03-file-stats-all.txt"

# 提取按目录分组的统计（knowledge/ 下一级子目录）
declare -A dir_add dir_del
if [ -n "$commits" ]; then
  for hash in $commits; do
    while IFS=$'\t' read -r added deleted filepath; do
      [[ "$added" == "-" ]] && continue
      [[ "$filepath" != knowledge/*.md ]] && continue
      [[ "$filepath" == knowledge/01_survey/* ]] && continue
      # 取 knowledge/ 下的一级目录
      dir="${filepath#knowledge/}"; dir="${dir%%/*}"
      dir_add["$dir"]=$(( ${dir_add["$dir"]:-0} + added ))
      dir_del["$dir"]=$(( ${dir_del["$dir"]:-0} + deleted ))
    done < <(git diff-tree --no-commit-id -r --numstat "$hash" 2>/dev/null)
  done
fi

echo "  → $(wc -l < "${DATA_DIR}/03-file-stats-all.txt") 行统计输出" >&2

#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Step 5: 记忆文件检查（关注 REPORT_DATE 的记忆文件）
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "▶ Step 5/7: 记忆文件检查（${REPORT_DATE}）..." >&2

{
  echo "# 记忆文件状态（报告日期: ${REPORT_DATE}，时间窗口: ${window_after} → ${window_before}）"
  echo "#"
  echo "## 报告日记忆文件"
  echo "#"

  mem_file="memory/${REPORT_DATE}.md"
  if [ -f "$mem_file" ]; then
    mem_lines=$(wc -l < "$mem_file")
    mem_size=$(wc -c < "$mem_file" | awk '{if($1>1048576) printf "%.1fM",$1/1048576; else if($1>1024) printf "%.1fK",$1/1024; else print $1"B"}')
    echo "memory/${REPORT_DATE}.md  |  ${mem_lines} lines | ${mem_size}"

    # 提取操作要点 — 任务完成标记或"→"符号的行
    echo "#"
    echo "## 操作要点摘要"
    echo "#"
    grep -n '✅\|✔️\|→\|##' "$mem_file" 2>/dev/null | head -80 || echo "# （无要点标记）"
  else
    echo "memory/${REPORT_DATE}.md  |  NOT FOUND"
  fi

  # MEMORY.md 变更检查（在当前时间窗口内）
  echo "#"
  echo "## MEMORY.md 变更"
  echo "#"
  mem_md_modified=$(git log --after="${window_after}" --before="${window_before}" \
    --oneline -- "MEMORY.md" 2>/dev/null | wc -l || echo 0)
  if [ "$mem_md_modified" -gt 0 ]; then
    git log --after="${window_after}" --before="${window_before}" \
      --oneline -- "MEMORY.md" 2>/dev/null | while IFS= read -r line; do
      echo "  $line"
    done
  else
    echo "  无变更"
  fi

  # 当日 memory 文件（TODAY）— 可能包含日报生成过程的记录
  echo "#"
  echo "## 当日（${TODAY}）记忆文件 — 仅检查是否存在"
  echo "#"
  today_mem="memory/${TODAY}.md"
  if [ -f "$today_mem" ]; then
    today_lines=$(wc -l < "$today_mem")
    echo "memory/${TODAY}.md  |  ${today_lines} lines（存在，可能含日报生成记录）"
  else
    echo "memory/${TODAY}.md  |  NOT FOUND"
  fi

} > "${DATA_DIR}/04-memory-stats.txt"

cat "${DATA_DIR}/04-memory-stats.txt" >&2

#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Step 6: scripts/ skills/ 变更统计（时间窗口内）
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "▶ Step 6/7: scripts/skills 变更统计..." >&2

{
  echo "# scripts/skills 变更（时间窗口: ${window_after} → ${window_before}）"
  echo "#"

  for dir in scripts skills; do
    count=$(git log --after="${window_after}" --before="${window_before}" \
      --oneline -- "${dir}/" 2>/dev/null | wc -l || echo 0)
    echo "${dir}/: ${count} 个 commit 涉及"

    if [ "$count" -gt 0 ]; then
      git log --after="${window_after}" --before="${window_before}" \
        --name-only --format="" -- "${dir}/" 2>/dev/null | sort -u | while IFS= read -r f; do
        if [ -n "$f" ]; then
          echo "  - $f"
        fi
      done
    fi
  done
} > "${DATA_DIR}/05-scripts-skills-changes.txt"

cat "${DATA_DIR}/05-scripts-skills-changes.txt" >&2

#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Step 6b: 新增三个分析脚本（Git 综合分析 / 记忆会话分析 / 调研覆盖检查）
#          输出直接落盘 tmp/kb-daily-*-{REPORT_DATE}.md，供日报消费
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "▶ Step 6b/7: 三个增强分析脚本（git/memory/coverage）..." >&2

for script in kb-daily-git-analysis.py kb-daily-memory-analysis.py kb-daily-survey-coverage.py kb-token-context-stats.py; do
  if [ -x "${SCRIPT_DIR}/${script}" ] || [ -f "${SCRIPT_DIR}/${script}" ]; then
    echo "  → ${script}" >&2
    python3 "${SCRIPT_DIR}/${script}" "${REPORT_DATE}" > /dev/null 2>&1 \
      && echo "    ✅ 完成" >&2 \
      || echo "    ⚠️ 失败（日报可手动降级）" >&2
  else
    echo "  ⚠️  ${script} 不存在，跳过" >&2
  fi
done

#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Step 7: 生成 metadata JSON
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "▶ 生成元数据..." >&2

# 计算覆盖模块数
module_count=0
for dir in "${!dir_add[@]}"; do
  module_count=$((module_count + 1))
done

modules_json=""
sep=""
for dir in $(printf "%s\n" "${!dir_add[@]}" | sort); do
  modules_json="${modules_json}${sep}\"${dir}\""
  sep=", "
done

# 提取 commit hashes 列表
commit_hashes=$(git log --after="${window_after}" --before="${window_before}" \
  --format="\"%h\"" -- "knowledge/" ":^knowledge/01_survey/" -- 2>/dev/null | paste -sd "," || echo "")

# 统计
survey_file_count=$(cat "${DATA_DIR}/02-survey-files.txt" 2>/dev/null | wc -l || echo 0)
depth_file_count=$(cat "${DATA_DIR}/01-depth-files.txt" 2>/dev/null | wc -l || echo 0)

# MEMORY.md 变更数
mem_md_modified=$(git log --after="${window_after}" --before="${window_before}" \
  --oneline -- "MEMORY.md" 2>/dev/null | wc -l || echo 0)

cat > "${DATA_DIR}/metadata.json" <<METADATA
{
  "date": "${REPORT_DATE}",
  "window": {
    "start": "${window_after}",
    "end": "${window_before}"
  },
  "today": "${TODAY}",
  "pillars": {
    "pillar1_insights": {
      "label": "每日洞察技术要点",
      "source": "01_survey/ tracking files (${REPORT_DATE}* + ${TODAY}* 早间)",
      "file_list": "02-survey-files.txt",
      "count": ${survey_file_count},
      "total_lines": ${survey_lines}
    },
    "pillar2_deep_docs": {
      "label": "深度分析文档摘要",
      "source": "git knowledge/ excluding 01_survey (>100 lines)",
      "file_list": "01-depth-files.txt",
      "count": ${depth_file_count}
    },
    "pillar3_engineering": {
      "label": "工程Git/Memory变更",
      "source": "git knowledge/ (excl survey) + memory/${REPORT_DATE}.md + scripts/skills",
      "commits_file": "00-commits.txt",
      "memory_file": "04-memory-stats.txt",
      "scripts_file": "05-scripts-skills-changes.txt"
    }
  },
  "commits": {
    "count": ${commit_count},
    "hashes": [${commit_hashes}]
  },
  "survey": {
    "count": ${survey_count},
    "total_lines": ${survey_lines}
  },
  "depth_docs": {
    "count": ${depth_count}
  },
  "modules_covered": ${module_count},
  "modules": [${modules_json}],
  "memory": {
    "report_date_file": "memory/${REPORT_DATE}.md",
    "report_date_exists": $( [ -f "memory/${REPORT_DATE}.md" ] && echo "true" || echo "false" ),
    "mem_md_commits": ${mem_md_modified}
  },
  "data_dir": "tmp/kb-daily-data-${REPORT_DATE}"
}
METADATA

#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 输出 JSON summary（stdout）
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "=============================================="
echo "  kb-daily-data-gather v2 完成: ${REPORT_DATE}"
echo "  时间窗口: ${REPORT_DATE} 08:00 → ${TODAY} 08:10"
echo "=============================================="
echo "  Pillar 1 (洞察技术要点): ${survey_count} 调研文件 / ${survey_lines} 行"
echo "  Pillar 2 (深度文档摘要): ${depth_count} 深度文档"
echo "  Pillar 3 (工程变更):     ${commit_count} commits"
echo "  ── modules: ${module_count} (${modules_json})"
echo "  data dir:   ${DATA_DIR}"

cat "${DATA_DIR}/metadata.json"
