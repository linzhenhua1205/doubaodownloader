#!/usr/bin/env bash
# ============================================================
# update-submodules.sh — 批量更新所有 submodule（走镜像通道）
# ============================================================
# 用法:
#   ./update-submodules.sh            # 更新全部
#   ./update-submodules.sh ai-agent-book   # 只更新指定名称
#   ./update-submodules.sh --dry-run   # 只显示将更新项
# ============================================================
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.."

MIRROR="${MIRROR:-https://ghproxy.net/https://github.com}"
TIMEOUT=120
ONLY="${2:-}"; DRY=0
[ "${1:-}" = "--dry-run" ] && DRY=1
[ $# -ge 1 ] && [ "${1:-}" != "--dry-run" ] && ONLY="$1"

log() { echo -e "\033[1;32m[update]\033[0m $*"; }
warn() { echo -e "\033[1;33m[update!]\033[0m $*"; }

# 读取 .gitmodules 中所有 submodule
grep -E "^\s*path = " .gitmodules | sed -E 's/^\s*path = //' | while read -r path; do
  name="$(basename "$path")"
  if [ -n "$ONLY" ] && [ "$name" != "$ONLY" ]; then continue; fi
  if [ ! -d "$path/.git" ] && [ ! -f "$path/.git" ]; then
    warn "跳过(未初始化): $path"
    continue
  fi
  log "检查: $path"
  [ "$DRY" = 1 ] && { echo "   [dry-run] 将更新 $path"; continue; }

  # 取上游 url 构造镜像地址
  url="$(git config -f .gitmodules "submodule.$path.url" 2>/dev/null || true)"
  [ -z "$url" ] && url="$(git -C "$path" remote get-url origin 2>/dev/null || true)"
  mirror_url="${url/https:\/\/github.com\//$MIRROR/}"

  before="$(git -C "$path" rev-parse --short HEAD 2>/dev/null || echo '?')"
  if timeout $TIMEOUT git -C "$path" fetch origin 2>/dev/null; then
    branch="$(git -C "$path" symbolic-ref --short HEAD 2>/dev/null || echo main)"
    if git -C "$path" rev-parse --verify "origin/$branch" >/dev/null 2>&1; then
      git -C "$path" merge --ff-only "origin/$branch" >/dev/null 2>&1 \
        && git -C "$path" pull --ff-only origin "$branch" >/dev/null 2>&1 || true
    fi
  fi
  after="$(git -C "$path" rev-parse --short HEAD 2>/dev/null || echo '?')"
  if [ "$before" != "$after" ]; then
    log "  ✅ $name: $before → $after"
    git add "$path" 2>/dev/null || true
  else
    log "  已是最新: $name ($after)"
  fi
done

log "完成。如有更新: git commit -m \"chore: update submodules\""
