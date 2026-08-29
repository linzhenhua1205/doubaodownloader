#!/usr/bin/env bash
# ============================================================
# common.sh - shared functions for supernode IP config scripts
# 4-plane model: 10.<M>.<R>.<S>  M=1..4
# Source this file:  . "$(dirname "$0")/common.sh"
# ============================================================

# ---- strict mode (caller also sets -euo pipefail) ----------
[ -n "${SUPERNODE_IPCFG_LOADED:-}" ] && return 0
SUPERNODE_IPCFG_LOADED=1

IPCFG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IDENT_FILE="${NODE_IDENTITY_FILE:-/etc/node-identity}"
LOG_TAG="[ipcfg]"

log() { echo "$LOG_TAG $(date '+%F %T') $*"; }
die()  { log "FATAL: $*"; exit 1; }

# ---- identity: rack_id / slot_id / node_role ---------------
# sources (priority): env > identity file > SMBIOS OEM string
load_identity() {
  RACK_ID="${RACK_ID:-}"
  SLOT_ID="${SLOT_ID:-}"
  NODE_ROLE="${NODE_ROLE:-compute}"

  if [ -f "$IDENT_FILE" ]; then
    while IFS='=' read -r k v; do
      case "$k" in
        rack_id)  RACK_ID="$v" ;;
        slot_id)  SLOT_ID="$v" ;;
        node_role) NODE_ROLE="$v" ;;
      esac
    done < "$IDENT_FILE"
  fi

  if [ -z "$RACK_ID" ] || [ -z "$SLOT_ID" ]; then
    # SMBIOS Type 11 OEM strings injected by BMC at POST
    #   dmidecode -t 11 -> "rack_id=3" "slot_id=11"
    if command -v dmidecode >/dev/null 2>&1; then
      local oem
      oem="$(dmidecode -t 11 2>/dev/null | grep -oE '(rack_id|slot_id|node_role)=[0-9a-zA-Z_-]+')"
      [ -z "$RACK_ID" ] && RACK_ID="$(echo "$oem" | grep -oE 'rack_id=[0-9]+' | cut -d= -f2)"
      [ -z "$SLOT_ID" ] && SLOT_ID="$(echo "$oem" | grep -oE 'slot_id=[0-9]+' | cut -d= -f2)"
    fi
  fi

  [ -z "$RACK_ID" ] && die "rack_id unknown (check $IDENT_FILE / SMBIOS)"
  [ -z "$SLOT_ID" ] && die "slot_id unknown (check $IDENT_FILE / SMBIOS)"
  # 0-based internal ids (physical rack-1 / slot-1), validate
  RACK_ID=$((RACK_ID)); SLOT_ID=$((SLOT_ID))
  [ "$RACK_ID" -lt 0 ] && die "rack_id < 0"
  [ "$SLOT_ID" -lt 0 ] && die "slot_id < 0"
  log "identity: rack=$RACK_ID slot=$SLOT_ID role=$NODE_ROLE"
}

# ---- pure ip helpers ----------------------------------------
# ip_of_plane <M> <R> <S> -> echo 10.M.R.S
ip_of_plane() { echo "10.$1.$2.$3"; }

# validate ipv4 dotted quad
valid_ip() { [[ "$1" =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]] \
             && local IFS='.' && set -- $1 && \
             [ $1 -le 255 ] && [ $2 -le 255 ] && [ $3 -le 255 ] && [ $4 -le 255 ]; }

# ---- idempotent apply helpers --------------------------------
# apply_ifcfg <iface> <ip> <mask> <gw|-> <mtu|->  via NetworkManager
nm_apply_static() {
  local iface="$1" ip="$2" mask="$3" gw="$4" mtu="${5:-}"
  command -v nmcli >/dev/null 2>&1 || die "nmcli not found"
  nmcli con delete "id-$iface" >/dev/null 2>&1 || true
  nmcli con add type ethernet con-name "id-$iface" ifname "$iface" \
      ipv4.method manual ipv4.addresses "$ip/$mask" >/dev/null
  [ -n "$gw" ] && [ "$gw" != "-" ] && \
      nmcli con modify "id-$iface" ipv4.gateway "$gw"
  [ -n "$mtu" ] && [ "$mtu" != "-" ] && \
      nmcli con modify "id-$iface" 802-3ethernet.mtu "$mtu"
  nmcli con up "id-$iface" >/dev/null 2>&1 || true
  log "applied static $ip on $iface (mask $mask gw ${gw:--})"
}

# nm_apply_dhcp <iface> <hostname|->  via NetworkManager (PXE/post-install)
nm_apply_dhcp() {
  local iface="$1" hostname="${2:-}"
  command -v nmcli >/dev/null 2>&1 || die "nmcli not found"
  nmcli con delete "id-$iface" >/dev/null 2>&1 || true
  nmcli con add type ethernet con-name "id-$iface" ifname "$iface" \
      ipv4.method auto >/dev/null
  [ -n "$hostname" ] && [ "$hostname" != "-" ] && \
      nmcli con modify "id-$iface" ipv4.dhcp-hostname "$hostname"
  nmcli con up "id-$iface" >/dev/null 2>&1 || true
  log "applied dhcp on $iface"
}
