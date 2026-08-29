#!/usr/bin/env bash
# ============================================================
# bmc_net_config.sh - configure BMC (OOB mgmt plane, 10.1.x.x)
# Uses ipmitool to set static IP on the BMC LAN channel.
#
# Prereq: host-side ipmitool with a working host interface (KCS)
#   ipmitool lan print 1   # verify current channel
#
# Plane:  mgmt 10.1.<R>.<S>  mask 255.255.0.0  gw 10.1.250.1  vlan 101
# ============================================================
set -euo pipefail
. "$(cd "$(dirname "$0")" && pwd)/common.sh"

CHANNEL="${BMC_CHANNEL:-1}"          # ipmitool lan channel
MGMT_MASK="255.255.0.0"
MGMT_GW="${MGMT_GW:-10.1.250.1}"

load_identity
BMC_IP="$(ip_of_plane 1 "$RACK_ID" "$SLOT_ID")"
valid_ip "$BMC_IP" || die "bad BMC IP: $BMC_IP"

command -v ipmitool >/dev/null 2>&1 || die "ipmitool not found"

# read current config first (idempotency + audit)
CUR="$(ipmitool lan print "$CHANNEL" 2>/dev/null || true)"
CUR_IP="$(echo "$CUR" | awk '/IP Address  *: /{print $NF}')"
log "current BMC IP on ch$CHANNEL: ${CUR_IP:-none}"

if [ "$CUR_IP" = "$BMC_IP" ]; then
  log "BMC IP already $BMC_IP - skip (idempotent)"
else
  ipmitool lan set "$CHANNEL" ipsrc static >/dev/null
  ipmitool lan set "$CHANNEL" ipaddr "$BMC_IP" >/dev/null
  ipmitool lan set "$CHANNEL" netmask "$MGMT_MASK" >/dev/null
  ipmitool lan set "$CHANNEL" defgw ipaddr "$MGMT_GW" >/dev/null
  log "BMC configured: $BMC_IP/$MGMT_MASK gw $MGMT_GW"
fi

# verify
NEW="$(ipmitool lan print "$CHANNEL")"
echo "$NEW" | grep -E "IP Address|Subnet Mask|Default Gateway" || die "verify failed"
echo "$NEW" | grep -q "IP Address  *: $BMC_IP" || die "BMC IP mismatch after set"

# optional: set vlan on BMC channel (switch port must trunk 101)
if [ -n "${BMC_VLAN:-}" ]; then
  ipmitool lan set "$CHANNEL" vlan id "$BMC_VLAN" >/dev/null && \
    log "BMC vlan set to $BMC_VLAN"
fi
log "BMC OK: $BMC_IP"
