#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_ip_plan.py - Generate full-cluster IP ledger from plan.yaml.

Addressing model (v1.2 edge-fixed, derived from 08-25 four-plane design):
  10.<M>.<R>.<S>   M=plane(1..4) R=rack(1..8) S=slot(1..16)
  mgmt    : 10.1.<R>.<S>          BMC (MAC reserved)
  storage : 10.2.<R>.<S>          BF3 bond0 (option82 / static)
  scaleout: 10.3.<R>.<S> / +64 / +128 / +192   CX7 P1..P4 (static, 4 NIC/node)
  scaleup : 10.4.<R>.<16+(S-1)*12+P>  node port P; FSW 208+n; interrack 220+n

Edge fixes vs 08-25 v1.1:
  * 1-based R/S -> no 10.M.0.0 network-address collision
  * scale-up node ports offset +16 -> no overlap with FSW 208+n

Outputs:
  ip_plan.csv   - one row per (plane, device, rack, slot, ip, mask, gw, vlan)
  ip_plan.json  - machine-readable copy for scripts

Usage:
  python3 gen_ip_plan.py [--plan plan.yaml] [--outdir .]
  python3 gen_ip_plan.py --check   # validate: overlaps, range, count
"""
import argparse
import csv
import ipaddress
import json
import os
import sys

import yaml


def a(s):
    """str -> IPv4Address, assert valid private address"""
    addr = ipaddress.IPv4Address(s)
    assert addr.is_private, f"NOT PRIVATE: {s}"
    return addr


def build(plan):
    racks = plan["cluster"]["racks"]          # 8, 1-based
    slots = plan["cluster"]["slots_per_rack"]  # 16, 1-based
    P = plan["planes"]
    rows, seen = [], {}

    def add(plane, dev, rack, slot, ip, mask, gw, vlan, note=""):
        x = a(ip)
        if x in seen:
            raise SystemExit(f"OVERLAP: {ip} used by {seen[x]} and {plane}:{dev}")
        seen[x] = f"{plane}:{dev}"
        rows.append([plane, dev, rack, slot, str(x), mask, gw, vlan, note])

    for r in range(1, racks + 1):
        for s in range(1, slots + 1):
            add("mgmt", "bmc", r, s, f"10.1.{r}.{s}", P["mgmt"]["mask"],
                P["mgmt"]["gw"], P["mgmt"]["vlan"])
            add("storage", "bf3_bond0", r, s, f"10.2.{r}.{s}", P["storage"]["mask"],
                P["storage"]["gw"], P["storage"]["vlan"])
            add("scaleout", "cx7_p1", r, s, f"10.3.{r}.{s}", P["scaleout"]["mask"],
                P["scaleout"]["gw"], P["scaleout"]["vlan"])
            add("scaleout", "cx7_p2", r, s, f"10.3.{r}.{s+128}", P["scaleout"]["mask"],
                P["scaleout"]["gw"], P["scaleout"]["vlan"])
            add("scaleout", "cx7_p3", r, s, f"10.3.{r}.{s+64}", P["scaleout"]["mask"],
                P["scaleout"]["gw"], P["scaleout"]["vlan"])
            add("scaleout", "cx7_p4", r, s, f"10.3.{r}.{s+192}", P["scaleout"]["mask"],
                P["scaleout"]["gw"], P["scaleout"]["vlan"])
            for p in range(12):
                add("scaleup", f"node_port{p}", r, s, f"10.4.{r}.{16 + (s-1)*12 + p}",
                    P["scaleup"]["mask"], P["scaleup"]["gw"], P["scaleup"]["vlan"])
        for n in range(12):
            add("mgmt", f"fsw{n}", r, None, f"10.1.{r}.{160+n}", P["mgmt"]["mask"],
                P["mgmt"]["gw"], P["mgmt"]["vlan"])
            add("scaleup", f"fsw{n}", r, None, f"10.4.{r}.{208+n}", P["scaleup"]["mask"],
                P["scaleup"]["gw"], P["scaleup"]["vlan"])
            add("scaleup", f"interrack{n}", r, None, f"10.4.{r}.{220+n}",
                P["scaleup"]["mask"], P["scaleup"]["gw"], P["scaleup"]["vlan"])
        add("mgmt", "oob_acc", r, None, f"10.1.{r}.200", P["mgmt"]["mask"],
            P["mgmt"]["gw"], P["mgmt"]["vlan"])

    infra = [
        ("mgmt", "oob_core", "10.1.250.1"), ("mgmt", "oob_agg1", "10.1.250.2"),
        ("mgmt", "oob_agg2", "10.1.250.3"), ("mgmt", "mgmt_srv_dhcp", "10.1.250.10"),
        ("mgmt", "mgmt_srv_dns", "10.1.250.11"), ("mgmt", "mgmt_srv_ntp", "10.1.250.12"),
        ("storage", "tor01", "10.2.250.2"), ("storage", "tor02", "10.2.250.3"),
        ("storage", "mirror", "10.2.241.1"),
        # 存储服务器 x3 (G3.5x2 + G4x1, 08-25 拍板) -- C6 一致性整改 2026-08-26
        # (原 9 台 10.2.240.1~9 为旧规划残留; 台账计数 131 -> 134 已同步)
        ("storage", "storage_srv1", "10.2.240.1"),
        ("storage", "storage_srv2", "10.2.240.2"),
        ("storage", "storage_srv3", "10.2.240.3"),
    ]
    for plane, dev, ip in infra:
        m = P[plane]["mask"]
        add(plane, dev, None, None, ip, m, P[plane]["gw"], P[plane]["vlan"])
    return rows, seen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", default="plan.yaml")
    ap.add_argument("--outdir", default=".")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    with open(args.plan, "r", encoding="utf-8") as f:
        plan = yaml.safe_load(f)
    rows, seen = build(plan)

    if args.check:
        by_plane = {}
        for r in rows:
            by_plane[r[0]] = by_plane.get(r[0], 0) + 1
        print(f"LEDGER OK: {len(rows)} entries, {len(seen)} unique IPs, 0 overlaps")
        for k in sorted(by_plane):
            print(f"  {k:9s}: {by_plane[k]}")
        return 0

    os.makedirs(args.outdir, exist_ok=True)
    csv_path = os.path.join(args.outdir, "ip_plan.csv")
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["plane", "device", "rack", "slot", "ip", "mask", "gw", "vlan"])
        w.writerows(rows)
    json_path = os.path.join(args.outdir, "ip_plan.json")
    with open(json_path, "w") as f:
        json.dump({"plan": plan, "entries": rows}, f, indent=2)
    print(f"WROTE {csv_path} ({len(rows)} rows)")
    print(f"WROTE {json_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
