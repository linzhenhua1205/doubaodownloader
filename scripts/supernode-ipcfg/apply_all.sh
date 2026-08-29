#!/usr/bin/env bash
# ============================================================
# apply_all.sh - one-shot loader: run all four plane configs
# in dependency order, then verify.
#
#   bash apply_all.sh            # run everything on this node
#   bash apply_all.sh --bmc-only # only BMC plane
#   bash apply_all.sh --dry-run  # print actions, no change
# ============================================================
set -euo pipefail
. "$(cd "$(dirname "$0")" && pwd)/common.sh"

DRY=0
ONLY=""
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY=1 ;;
    --bmc-only) ONLY=bmc ;;
    --storage-only) ONLY=storage ;;
    --scaleout-only) ONLY=scaleout ;;
    --scaleup-only) ONLY=scaleup ;;
    *) die "unknown arg: $arg" ;;
  esac
done

run() {
  local name="$1"; shift
  log ">>> [$name] $*"
  if [ "$DRY" -eq 1 ]; then
    log "    (dry-run, skipped)"
    return 0
  fi
  bash "$IPCFG_DIR/$name" "$@" || die "$name failed"
}

load_identity

if [ -z "$ONLY" ] || [ "$ONLY" = "bmc" ]; then
  run bmc_net_config.sh
fi
if [ -z "$ONLY" ] || [ "$ONLY" = "storage" ]; then
  run storage_net_config.sh
fi
if [ -z "$ONLY" ] || [ "$ONLY" = "scaleout" ]; then
  run scaleout_net_config.sh
fi
if [ -z "$ONLY" ] || [ "$ONLY" = "scaleup" ]; then
  run scaleup_net_config.sh
fi

log "=== apply_all done (dry=$DRY only=${ONLY:-all}) ==="
if [ "$DRY" -eq 0 ]; then
  bash "$IPCFG_DIR/verify_net_config.sh" || die "VERIFY FAILED"
fi
