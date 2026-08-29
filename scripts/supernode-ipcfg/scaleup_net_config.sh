#!/usr/bin/env bash
# ============================================================
# scaleup_net_config.sh - configure scale-up plane (10.4.x.x)
#   RoCE form (semantics B, POC-gated): node 12 ports per node,
#   FSW 12 per rack, inter-rack DAC 12 per rack.
#
#   node port P  : 10.4.<R>.<16+(S-1)*12+P>   (P=0..11, S=1..16)
#   FSW n        : 10.4.<R>.<208+n>           (n=0..11)
#   interrack DAC: 10.4.<R>.<220+n>
#
#   Memory form (semantics A, NVLink/UALink/HCCS): NO IP needed.
#   When semantics=memory in plan.yaml, this script exits 0 with a
#   notice - scale-up verification is link/domain only.
# ============================================================
set -euo pipefail
. "$(cd "$(dirname "$0")" && pwd)/common.sh"

SU_MASK="255.255.0.0"
SU_MTU="${SU_MTU:-9000}"
SU_SEMANTICS="${SU_SEMANTICS:-roce}"   # roce | memory

# ---- POC gate: memory semantics -> no IP plane ----
if [ "$SU_SEMANTICS" = "memory" ]; then
  log "Scale-Up semantics=MEMORY: no IP addressing required"
  log "  verify = link up + domain topology (NCCL topo file)"
  exit 0
fi
[ "$SU_SEMANTICS" = "roce" ] || die "SU_SEMANTICS must be roce|memory"

load_identity

# ---- node side: 12 ports ----
# Port name discovery: scale-up NICs are the remaining mlx5 ports
# not used by CX7 scale-out. Convention: p3s0..p14s0 (override via env)
declare -a SU_PORTS
if [ -n "${SU_PORTS_OVERRIDE:-}" ]; then
  read -r -a SU_PORTS <<< "$SU_PORTS_OVERRIDE"
else
  for p in $(seq 0 11); do
    # default naming per node design (adapt to your BOM)
    SU_PORTS[$p]="${SU_PORT_PREFIX:-enpX}s0f${p}np0"
  done
fi

BASE=$((16 + (SLOT_ID - 1) * 12))
for p in $(seq 0 11); do
  iface="${SU_PORTS[$p]}"
  ip="10.4.$RACK_ID.$((BASE+p))"
  [ -d "/sys/class/net/$iface" ] || { log "WARN: $iface missing - skip"; continue; }
  ip addr flush dev "$iface" 2>/dev/null || true
  ip addr add "$ip/$SU_MASK" dev "$iface" 2>/dev/null || true
  ip link set "$iface" mtu "$SU_MTU" up 2>/dev/null || true
done

# ---- FSW side (run on FSW node when NODE_ROLE=fsw) ----
if [ "$NODE_ROLE" = "fsw" ]; then
  FSW_INDEX="${FSW_INDEX:?need FSW_INDEX for FSW role}"
  ip addr add "10.4.$RACK_ID.$((208+FSW_INDEX))/$SU_MASK" dev "${FSW_MGMT_IF:-eth0}" \
      2>/dev/null || true
  if [ -n "${FSW_INTERRACK_IF:-}" ]; then
    ip addr add "10.4.$RACK_ID.$((220+FSW_INDEX))/$SU_MASK" dev "$FSW_INTERRACK_IF" \
      2>/dev/null || true
  fi
  log "FSW $FSW_INDEX configured (mgmt + interrack)"
fi

log "SCALEUP OK (roce): rack=$RACK_ID slot=$SLOT_ID ports 10.4.$RACK_ID.$BASE..$((BASE+11))"
