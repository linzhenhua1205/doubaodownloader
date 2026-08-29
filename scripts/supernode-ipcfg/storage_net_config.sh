#!/usr/bin/env bash
# ============================================================
# storage_net_config.sh - configure BF3 storage plane (10.2.x.x)
#   bond0 = {P1, P2} active-backup, single IP 10.2.<R>.<S>
#   P1 -> TOR-01 (option82 -> 10.2.R.S), P2 -> TOR-02 backup
#   Runtime IP == PXE-time IP (no drift, per 08-24 design)
#
# Interfaces (per 08-24 node config):
#   BF3-P1 = enpXs0f0np0  (pci addr varies -> auto-detect by MAC plan)
#   BF3-P2 = enpXs0f1np1
# ============================================================
set -euo pipefail
. "$(cd "$(dirname "$0")" && pwd)/common.sh"

STOR_MASK="255.255.0.0"
STOR_GW="${STOR_GW:--}"               # storage plane usually no default gw
STOR_MTU="${STOR_MTU:-9000}"          # RoCE storage: jumbo frames

# discover BF3 uplink ports by MAC plan (OUI + rack + slot)
#   MAC = OUI:00:0R:0S  (08-13 MAC plan; adapt OUI to your NIC)
BF3_OUI="${BF3_OUI:-00:1a:2b}"
BF3_P1="${BF3_P1:-}"                  # override if auto-detect fails
BF3_P2="${BF3_P2:-}"

detect_bf3_ports() {
  local want1 want2
  want1=$(printf '%s:00:%02x:%02x' "$BF3_OUI" "$RACK_ID" "$SLOT_ID")
  want2=$(printf '%s:00:%02x:%02x' "$BF3_OUI" "$RACK_ID" "$((SLOT_ID))")
  # find interfaces whose permaddr matches either slot-encoded MAC
  for dev in /sys/class/net/*; do
    local name mac
    name=$(basename "$dev")
    mac=$(cat "$dev/address" 2>/dev/null || true)
    case "$name" in bond*|lo|docker*) continue;; esac
    [ -z "$BF3_P1" ] && [ "$mac" = "$want1" ] && BF3_P1="$name"
    [ -z "$BF3_P2" ] && [ "$mac" = "$want2" ] && BF3_P2="$name"
  done
}

load_identity
detect_bf3_ports
[ -z "$BF3_P1" ] && die "BF3 P1 port not found (MAC plan mismatch?)"
[ -z "$BF3_P2" ] && die "BF3 P2 port not found (MAC plan mismatch?)"
log "BF3 ports: P1=$BF3_P1 P2=$BF3_P2"

BOND_NAME="${BOND_NAME:-bond0}"
STOR_IP="$(ip_of_plane 2 "$RACK_ID" "$SLOT_ID")"
valid_ip "$STOR_IP" || die "bad storage IP: $STOR_IP"

# ---- create bond (active-backup, miimon=100) ----
if [ ! -d "/sys/class/net/$BOND_NAME" ]; then
  ip link add "$BOND_NAME" type bond mode active-backup miimon 100 2>/dev/null \
    || die "cannot create bond $BOND_NAME"
fi
ip link set "$BF3_P1" down 2>/dev/null || true
ip link set "$BF3_P2" down 2>/dev/null || true
ip link set "$BF3_P1" master "$BOND_NAME" 2>/dev/null || true
ip link set "$BF3_P2" master "$BOND_NAME" 2>/dev/null || true
ip link set "$BOND_NAME" mtu "$STOR_MTU" 2>/dev/null || true
ip link set "$BOND_NAME" up
ip link set "$BF3_P1" up
ip link set "$BF3_P2" up

# ---- single IP on bond (runtime == PXE-time) ----
ip addr flush dev "$BOND_NAME" 2>/dev/null || true
ip addr add "$STOR_IP/$STOR_MASK" dev "$BOND_NAME" 2>/dev/null || \
  log "WARN: addr add failed (may already exist)"
[ "$STOR_GW" != "-" ] && ip route replace default via "$STOR_GW" dev "$BOND_NAME" || true

# ---- persist via NetworkManager connection profile ----
if command -v nmcli >/dev/null 2>&1; then
  nmcli con delete "id-$BOND_NAME" >/dev/null 2>&1 || true
  nmcli con add type bond con-name "id-$BOND_NAME" ifname "$BOND_NAME" \
      mode active-backup miimon 100 >/dev/null
  nmcli con add type ethernet con-name "id-$BF3_P1" ifname "$BF3_P1" \
      master "id-$BOND_NAME" >/dev/null 2>&1 || true
  nmcli con add type ethernet con-name "id-$BF3_P2" ifname "$BF3_P2" \
      master "id-$BOND_NAME" >/dev/null 2>&1 || true
  nmcli con modify "id-$BOND_NAME" \
      ipv4.method manual ipv4.addresses "$STOR_IP/16" \
      802-3ethernet.mtu "$STOR_MTU" >/dev/null
  [ "$STOR_GW" != "-" ] && nmcli con modify "id-$BOND_NAME" ipv4.gateway "$STOR_GW"
  nmcli con up "id-$BOND_NAME" >/dev/null 2>&1 || true
fi

log "STORAGE OK: $BOND_NAME $STOR_IP (P1=$BF3_P1 P2=$BF3_P2)"
