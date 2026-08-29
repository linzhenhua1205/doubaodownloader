#!/usr/bin/env bash
# ============================================================
# import-repo.sh — 通用 GitHub 仓库 submodule 导入脚本
# ============================================================
# 功能:
#   1. 解析仓库 URL (owner/name/branch)
#   2. 多镜像通道自动探测(直连 → ghproxy.net → ghfast.top → gh-proxy.com → gitclone.com)
#   3. clone 到目标路径 (默认 import/<repo-name>)
#   4. 注册为 git submodule (.gitmodules 保留官方 URL, 他人可正常拉取)
#   5. 版本固定 + 元信息归档 (<target>.info/ 目录: README/版本/通道/时间)
#   6. 生成导入索引并给出提交建议
#
# 用法:
#   ./import-repo.sh https://github.com/bojieli/ai-agent-book
#   ./import-repo.sh https://github.com/bojieli/ai-agent-book import/ai-agent-book --branch main
#   ./import-repo.sh <url> --depth 1 --shallow      # 浅克隆(默认)
#   ./import-repo.sh <url> --dry-run                # 只探测通道与仓库信息
#   ./import-repo.sh <url> --force                  # 已存在时重新导入
# ============================================================
set -euo pipefail

# ---------- 配置 ----------
MIRRORS=(
  ""                                   # 直连
  "https://ghproxy.net/https://github.com"
  "https://ghfast.top/https://github.com"
  "https://gh-proxy.com/https://github.com"
  "https://gitclone.com/github.com"
)
TIMEOUT=90
DEPTH=1                                # 浅克隆(素材导入足够; 需要历史时 --depth 0)
WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# ---------- 工具函数 ----------
log()  { echo -e "\033[1;32m[import]\033[0m $*"; }
warn() { echo -e "\033[1;33m[import!]\033[0m $*"; }
die()  { echo -e "\033[1;31m[import✗]\033[0m $*" >&2; exit 1; }

parse_repo() {  # <url> → 输出 owner name 到全局变量
  local url="$1"
  REPO_OWNER=$(echo "$url" | sed -E 's#https?://[^/]+/([^/]+)/([^/.]+)(\.git)?#\1#')
  REPO_NAME=$(echo "$url" | sed -E 's#https?://[^/]+/([^/]+)/([^/.]+)(\.git)?#\2#')
  if [ -z "$REPO_OWNER" ] || [ -z "$REPO_NAME" ]; then
    die "无法解析仓库: $url (支持 https://github.com/owner/name)"
  fi
}

probe_mirror() {  # <mirror> → 0 可达 / 1 不可达 (用 git ls-remote 实测, 比 curl 更真实)
  local mirror="$1" url
  url="${mirror:+$mirror/}bojieli/ai-agent-book"
  timeout 15 git ls-remote --heads "$url" >/dev/null 2>&1
}

get_default_branch() {  # <mirror> → 输出默认分支名
  local mirror="$1" url
  url="${mirror:+$mirror/}$REPO_OWNER/$REPO_NAME"
  timeout 20 git ls-remote --symref "$url" HEAD 2>/dev/null | head -1 \
    | sed -E 's#ref: refs/heads/([^ \t]+).*#\1#'
}

# ---------- 主流程 ----------
DRY_RUN=0; FORCE=0; BRANCH=""; SHALLOW=1
POS_ARGS=()

while [ $# -gt 0 ]; do
  case "$1" in
    --branch) BRANCH="$2"; shift 2 ;;
    --depth)  DEPTH="$2"; shift 2 ;;
    --no-shallow) SHALLOW=0; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    --force)   FORCE=1; shift ;;
    *) POS_ARGS+=("$1"); shift ;;
  esac
done

REPO_URL="${POS_ARGS[0]:?用法: import-repo.sh <repo-url> [target-path] [--branch main]}"
parse_repo "$REPO_URL"
TARGET="${POS_ARGS[1]:-import/$REPO_NAME}"

log "仓库: $REPO_OWNER/$REPO_NAME → $TARGET"
[ "$DRY_RUN" = 1 ] && log "[dry-run] 仅探测通道, 不克隆不注册"

# ---------- 1. 通道探测 ----------
log "探测镜像通道..."
SELECTED="" 
for m in "${MIRRORS[@]}"; do
  if probe_mirror "$m"; then
    SELECTED="$m"
    log "  可用通道: ${m:-直连 github.com}"
    break
  fi
done
[ -z "$SELECTED" ] && die "所有通道不可达。请检查网络或稍后重试 (可用: ghproxy.net/ghfast.top 等镜像)"

# ---------- 2. 默认分支探测 ----------
if [ -z "$BRANCH" ]; then
  BRANCH=$(get_default_branch "$SELECTED")
  BRANCH="${BRANCH:-main}"
  log "默认分支: $BRANCH"
fi

if [ "$DRY_RUN" = 1 ]; then
  log "[dry-run] 完成。通道=$SELECTED 分支=$BRANCH 目标=$TARGET"
  exit 0
fi

# ---------- 3. 前置检查 ----------
[ -e "$TARGET" ] && [ "$FORCE" = 0 ] && die "目标已存在: $TARGET (加 --force 覆盖)"
[ -e "$TARGET" ] && [ "$FORCE" = 1 ] && { rm -rf "$TARGET"; warn "已删除旧目标(force)"; }

# ---------- 4. 克隆(走选定通道) ----------
CLONE_URL="${SELECTED:+$SELECTED/}$REPO_OWNER/$REPO_NAME"
ARGS=(clone)
[ "$SHALLOW" = 1 ] && ARGS+=(--depth "$DEPTH")
ARGS+=(-b "$BRANCH" --single-branch "$CLONE_URL" "$TARGET")

log "克隆: $CLONE_URL (branch=$BRANCH depth=$DEPTH)"
if ! timeout $((TIMEOUT * 3)) git "${ARGS[@]}" 2>&1 | tail -3; then
  # 失败自动切换下一通道重试
  for m in "${MIRRORS[@]}"; do
    [ "$m" = "$SELECTED" ] && continue
    [ -z "$m" ] && continue
    warn "通道失败, 尝试: $m"
    CLONE_URL="$m/$REPO_OWNER/$REPO_NAME"
    if timeout $((TIMEOUT * 3)) git clone --depth "$DEPTH" -b "$BRANCH" --single-branch \
        "$CLONE_URL" "$TARGET" 2>&1 | tail -2; then
      SELECTED="$m"; break
    fi
  done
fi
[ -d "$TARGET/.git" ] || [ -f "$TARGET/.git" ] || die "克隆失败: 所有通道均未成功"

# ---------- 5. 注册 submodule (官方 URL 保留) ----------
git -C "$WORKSPACE_ROOT" config -f .gitmodules "submodule.$TARGET.path" "$TARGET"
git -C "$WORKSPACE_ROOT" config -f .gitmodules "submodule.$TARGET.url" "$REPO_URL"
git -C "$WORKSPACE_ROOT" config "submodule.$TARGET.active" true
git -C "$WORKSPACE_ROOT" add .gitmodules "$TARGET"

# ---------- 6. 版本固定 + 元信息归档 ----------
COMMIT=$(git -C "$TARGET" rev-parse HEAD)
INFO_DIR="$TARGET.info"
mkdir -p "$INFO_DIR"
{
  echo "# 📦 Submodule: $REPO_NAME"
  echo
  echo "| 项 | 值 |"
  echo "|:---|:---|"
  echo "| 仓库 | [$REPO_OWNER/$REPO_NAME]($REPO_URL) |"
  echo "| 分支 | $BRANCH |"
  echo "| 固定版本 | \`$COMMIT\` |"
  echo "| 导入时间 | $(date '+%Y-%m-%d %H:%M') |"
  echo "| 通道 | ${SELECTED:-直连} |"
  echo "| 深度 | ${DEPTH} (浅克隆) |"
  echo
  echo "## 仓库简介"
  echo
  if [ -f "$TARGET/README.md" ]; then
    head -20 "$TARGET/README.md"
  else
    echo "(README 未找到)"
  fi
  echo
  echo "## 更新方式"
  echo '```bash'
  echo "# 进入 submodule 拉取最新"
  echo "git -C $TARGET fetch origin && git -C $TARGET pull origin $BRANCH"
  echo "# 提交版本更新"
  echo "git add $TARGET && git commit -m \"chore: update $REPO_NAME\""
  echo '```'
} > "$INFO_DIR/README.md"
git -C "$WORKSPACE_ROOT" add "$INFO_DIR" 2>/dev/null || true

log "✅ 导入完成"
log "  路径: $TARGET | 版本: $COMMIT | 元信息: $INFO_DIR/README.md"
log "  提交建议: git commit -m \"chore: import $REPO_OWNER/$REPO_NAME as submodule\""
