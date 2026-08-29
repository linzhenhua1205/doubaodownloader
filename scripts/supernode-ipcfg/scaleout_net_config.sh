#!/usr/bin/env bash
# ============================================================
# scaleout_net_config.sh - configure CX7 scale-out plane (10.3.x.x)
#   4 NICs/node (2026-08-26 frozen):
#     P1 (rail A ): 10.3.<R>.<S>        (1..16)
#     P2 (rail B ): 10.3.<R>.<S+128>    (129..144)
#     P3 (rail A2): 10.3.<R>.<S+64>     (65..80)
#     P4 (rail B2): 10.3.<R>.<S+192>    (193..208)
#   NCCL/RoCE plane: NO default gw, per-port routing tables,
#   policy rules "origin-in origin-out" to avoid asymmetric routing.
#
# Plane:  scaleout 10.3.0.0/16  vlan 103  mtu 9000
# ============================================================
set -euo pipefail
. "$(cd "$(dirname "$0")" && pwd)/common.sh"

SO_MASK="255.255.0.0"
SO_MTU="${SO_MTU:-9000}"
# rt_tables: 31..34 = so-p1..so-p4
SO_TBL_P1=31
SO_TBL_P2=32
SO_TBL_P3=33
SO_TBL_P4=34

CX7_P1="${CX7_P1:-}"   # auto-detect by PCI/VPD or pass env
CX7_P2="${CX7_P2:-}"
CX7_P3="${CX7_P3:-}"
CX7_P4="${CX7_P4:-}"

detect_cx7_ports() {
  # ConnectX-7 exposes 2 phys per PCI function; 4 NICs -> 4 devs.
  # typical names: ens4f0np0 / ens4f1np1 / ... Detect via ethtool:
  for dev in /sys/class/net/*; do
    local name drv
    name=$(basename "$dev")
    case "$name" in bond*|lo|docker*|virbr*) continue;; esac
    drv=$(basename "$(readlink -f "$dev/device/driver" 2>/dev/null || true)" 2>/dev/null || true)
    if [ "$drv" = "mlx5_core" ]; then
      [ -z "$CX7_P1" ] && CX7_P1="$name" && continue
      [ -z "$CX7_P2" ] && CX7_P2="$name" && continue
      [ -z "$CX7_P3" ] && CX7_P3="$name" && continue
      [ -z "$CX7_P4" ] && CX7_P4="$name" && break
    fi
  done
}

load_identity
detect_cx7_ports
[ -z "$CX7_P1" ] && die "CX7 P1 not found (mlx5_core driver missing?)"
[ -z "$CX7_P2" ] && die "CX7 P2 not found"
[ -z "$CX7_P3" ] && die "CX7 P3 not found (4 NICs expected)"
[ -z "$CX7_P4" ] && die "CX7 P4 not found (4 NICs expected)"
log "CX7 ports: P1=$CX7_P1 P2=$CX7_P2 P3=$CX7_P3 P4=$CX7_P4"

IP_P1="$(ip_of_plane 3 "$RACK_ID" "$SLOT_ID")"
IP_P2="$(ip_of_plane 3 "$RACK_ID" "$((SLOT_ID+128))")"
IP_P3="$(ip_of_plane 3 "$RACK_ID" "$((SLOT_ID+64))")"
IP_P4="$(ip_of_plane 3 "$RACK_ID" "$((SLOT_ID+192))")"
for ip in "$IP_P1" "$IP_P2" "$IP_P3" "$IP_P4"; do
  valid_ip "$ip" || die "bad scaleout IP: $ip"
done

# ---- 1) static IPs (no default gw on RoCE plane) ----
for pair in "$CX7_P1:$IP_P1" "$CX7_P2:$IP_P2" "$CX7_P3:$IP_P3" "$CX7_P4:$IP_P4"; do
  iface="${pair%%:*}"; ip="${pair##*:}"
  ip addr flush dev "$iface" 2>/dev/null || true
  ip addr add "$ip/$SO_MASK" dev "$iface" 2>/dev/null || true
  ip link set "$iface" mtu "$SO_MTU" up 2>/dev/null || true
done

# ---- 2) per-port routing tables (origin-in origin-out) ----
# rt_tables: 31 so-p1 / 32 so-p2 / 33 so-p3 / 34 so-p4
grep -q "^$SO_TBL_P1 " /etc/iproute2/rt_tables 2>/dev/null || \
  echo -e "$SO_TBL_P1\tso-p1\n$SO_TBL_P2\tso-p2\n$SO_TBL_P3\tso-p3\n$SO_TBL_P4\tso-p4" >> /etc/iproute2/rt_tables

for t in $SO_TBL_P1 $SO_TBL_P2 $SO_TBL_P3 $SO_TBL_P4; do
  ip route flush table $t 2>/dev/null || true
done
ip route add 10.3.0.0/16 dev "$CX7_P1" src "$IP_P1" table $SO_TBL_P1
ip route add 10.3.0.0/16 dev "$CX7_P2" src "$IP_P2" table $SO_TBL_P2
ip route add 10.3.0.0/16 dev "$CX7_P3" src "$IP_P3" table $SO_TBL_P3
ip route add 10.3.0.0/16 dev "$CX7_P4" src "$IP_P4" table $SO_TBL_P4

ip rule del from "$IP_P1" table $SO_TBL_P1 2>/dev/null || true
ip rule del from "$IP_P2" table $SO_TBL_P2 2>/dev/null || true
ip rule del from "$IP_P3" table $SO_TBL_P3 2>/dev/null || true
ip rule del from "$IP_P4" table $SO_TBL_P4 2>/dev/null || true
ip rule add from "$IP_P1" table $SO_TBL_P1 prio 100
ip rule add from "$IP_P2" table $SO_TBL_P2 prio 100
ip rule add from "$IP_P3" table $SO_TBL_P3 prio 100
ip rule add from "$IP_P4" table $SO_TBL_P4 prio 100

# ---- 3) persist: systemd unit re-applies rules at boot ----
UNIT=/etc/systemd/system/supernode-scaleout-rules.service
cat > "$UNIT" <<EOF
[Unit]
Description=Supernode scale-out per-port routing rules
After=network.target
[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/sbin/ip route replace 10.3.0.0/16 dev $CX7_P1 src $IP_P1 table $SO_TBL_P1
ExecStart=/usr/sbin/ip route replace 10.3.0.0/16 dev $CX7_P2 src $IP_P2 table $SO_TBL_P2
ExecStart=/usr/sbin/ip route replace 10.3.0.0/16 dev $CX7_P3 src $IP_P3 table $SO_TBL_P3
ExecStart=/usr/sbin/ip route replace 10.3.0.0/16 dev $CX7_P4 src $IP_P4 table $SO_TBL_P4
ExecStart=/usr/sbin/ip rule add from $IP_P1 table $SO_TBL_P1 prio 100
ExecStart=/usr/sbin/ip rule add from $IP_P2 table $SO_TBL_P2 prio 100
ExecStart=/usr/sbin/ip rule add from $IP_P3 table $SO_TBL_P3 prio 100
ExecStart=/usr/sbin/ip rule add from $IP_P4 table $SO_TBL_P4 prio 100
[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable supernode-scaleout-rules.service >/dev/null 2>&1 || true

# ---- 4) persist IPs via NetworkManager ----
if command -v nmcli >/dev/null 2>&1; then
  nm_apply_static "$CX7_P1" "$IP_P1" "$SO_MASK" "-" "$SO_MTU"
  nm_apply_static "$CX7_P2" "$IP_P2" "$SO_MASK" "-" "$SO_MTU"
  nm_apply_static "$CX7_P3" "$IP_P3" "$SO_MASK" "-" "$SO_MTU"
  nm_apply_static "$CX7_P4" "$IP_P4" "$SO_MASK" "-" "$SO_MTU"
fi

log "SCALEOUT OK: P1=$CX7_P1 $IP_P1  P2=$CX7_P2 $IP_P2  P3=$CX7_P3 $IP_P3  P4=$CX7_P4 $IP_P4 (no default gw)"
