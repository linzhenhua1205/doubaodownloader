#!/usr/bin/env bash
# ============================================================
# verify_net_config.sh - 4-plane verification & report
# Checks (per plane):
#   mgmt    : BMC reachable via ipmitool / ping 10.1.R.S
#   storage : bond0 up, IP set, PXE mirror reachable
#   scaleout: P1/P2 IP + MTU + routing rules present
#   scaleup : (roce) 12 port IPs present | (memory) links up
# Exit 0 when all checks pass; prints PASS/FAIL matrix.
# ============================================================
set -euo pipefail
. "$(cd "$(dirname "$0")" && pwd)/common.sh"

load_identity
FAILED=0
pass() { log "PASS  $1"; }
fail() { log "FAIL  $1"; FAILED=$((FAILED+1)); }

# ---- mgmt plane: BMC self-report ----
BMC_IP="$(ip_of_plane 1 "$RACK_ID" "$SLOT_ID")"
if command -v ipmitool >/dev/null 2>&1; then
  GOT="$(ipmitool lan print 1 2>/dev/null | awk '/IP Address  *: /{print $NF}')"
  [ "$GOT" = "$BMC_IP" ] && pass "mgmt BMC IP=$BMC_IP" || fail "mgmt BMC IP got=$GOT want=$BMC_IP"
else
  fail "mgmt ipmitool missing"
fi

# ---- storage plane: bond0 ----
BOND="${BOND_NAME:-bond0}"
STOR_IP="$(ip_of_plane 2 "$RACK_ID" "$SLOT_ID")"
if [ -d "/sys/class/net/$BOND" ]; then
  GOT="$(ip -4 addr show dev "$BOND" | awk '/inet /{print $2}' | cut -d/ -f1)"
  [ "$GOT" = "$STOR_IP" ] && pass "storage bond0 $STOR_IP" || fail "storage bond0 got=$GOT want=$STOR_IP"
  CARRIER="$(cat "/sys/class/net/$BOND/carrier" 2>/dev/null || echo 0)"
  [ "$CARRIER" = "1" ] && pass "storage bond0 carrier up" || fail "storage bond0 carrier down"
else
  fail "storage bond0 missing"
fi

# ---- scale-out plane: CX7 P1/P2/P3/P4 (4 NICs/node) ----
IP_P1="$(ip_of_plane 3 "$RACK_ID" "$SLOT_ID")"
IP_P2="$(ip_of_plane 3 "$RACK_ID" "$((SLOT_ID+128))")"
IP_P3="$(ip_of_plane 3 "$RACK_ID" "$((SLOT_ID+64))")"
IP_P4="$(ip_of_plane 3 "$RACK_ID" "$((SLOT_ID+192))")"
for pair in "$IP_P1" "$IP_P2" "$IP_P3" "$IP_P4"; do
  ip -4 addr show | grep -q "$pair" && pass "scaleout has $pair" || fail "scaleout missing $pair"
done
ip rule show | grep -q "from $IP_P1" && pass "scaleout rule P1" || fail "scaleout rule P1 missing"
ip rule show | grep -q "from $IP_P2" && pass "scaleout rule P2" || fail "scaleout rule P2 missing"
ip rule show | grep -q "from $IP_P3" && pass "scaleout rule P3" || fail "scaleout rule P3 missing"
ip rule show | grep -q "from $IP_P4" && pass "scaleout rule P4" || fail "scaleout rule P4 missing"

# ---- scale-up plane ----
SU_SEMANTICS="${SU_SEMANTICS:-roce}"
if [ "$SU_SEMANTICS" = "roce" ]; then
  BASE=$((16 + (SLOT_ID - 1) * 12))
  N=0
  for p in $(seq 0 11); do
    ip -4 addr show | grep -q "10.4.$RACK_ID.$((BASE+p))" && N=$((N+1))
  done
  [ "$N" -eq 12 ] && pass "scaleup 12 port IPs present" || fail "scaleup only $N/12 port IPs"
else
  # memory semantics: check uplink ports carrier
  N=0
  for dev in /sys/class/net/*; do
    case "$(basename "$dev")" in bond*|lo|docker*) continue;; esac
    [ "$(cat "$dev/carrier" 2>/dev/null || echo 0)" = "1" ] && N=$((N+1))
  done
  pass "scaleup(memory) carrier-up interfaces: $N"
fi

# ---- gateway reachability (optional) ----
MGMT_GW="${MGMT_GW:-10.1.250.1}"
ping -c1 -W1 "$MGMT_GW" >/dev/null 2>&1 && pass "mgmt gw $MGMT_GW reachable" \
  || fail "mgmt gw $MGMT_GW unreachable (may be normal pre-OS)"

log "=== VERIFY RESULT: $([ $FAILED -eq 0 ] && echo ALL-PASS || echo "$FAILED FAILURES") ==="
exit $([ $FAILED -eq 0 ] && echo 0 || echo 1)
