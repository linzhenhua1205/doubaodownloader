#!/usr/bin/env python3
"""
check-sr-ar-trace.py — AR 映射一致性检查 (Level 1)

sr-001 为历史参考文档，ar-001 为活跃需求文档。
本脚本聚焦 **ar-001 内部三方一致性**：

  §2 AR 清单 ←→ §3 SR→AR 正向映射 ←→ §4 AR→SR 逆向映射

检查项：
  - 轮空：§2 有、§4 无的 AR（不完整的反向条目）
  - 孤儿：§4 有、§2 无的 AR（§2 清单遗漏）
  - 状态漂移：同一 AR 在 §2 和 §4 的状态不同
  - §3 引用漂移：§3 正向表中引用的 AR 在 §2 中不存在
  - 编号有效性：所有引用的 AR 编号格式正确

输出格式：JSON
"""
import re
import json
import sys
from pathlib import Path

WORKSPACE = Path("/home/lzh/cow")
SPEC_DIR = WORKSPACE / "spec"

def read_file(path):
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""

def parse_ar_list_v2(text):
    """从 ar-001 §2 AR 清单提取：编号 → {描述, 阶段, SR引用, 状态, 优先级}"""
    ar_map = {}
    # | AR-P1-001 | Import 目录扫描与自动发现 | Phase 1 | SR-001, SR-005 | ✅ | P0 |
    pattern = r"\|[ \t]*(AR-\w+-\d+)[ \t]*\|[ \t]*(.*?)[ \t]*\|[ \t]*(.*?)[ \t]*\|[ \t]*(.*?)[ \t]*\|[ \t]*([✅🚧📋])[ \t]*\|[ \t]*(P[012])[ \t]*\|"
    for m in re.finditer(pattern, text):
        ar_id = m.group(1)
        desc = m.group(2).strip()
        phase = m.group(3).strip()
        sr_ref = m.group(4).strip()
        status = m.group(5)
        priority = m.group(6)
        ar_map[ar_id] = {"desc": desc, "phase": phase, "sr_ref": sr_ref, "status": status, "priority": priority}
    return ar_map

def parse_reverse_map_v2(text):
    """从 ar-001 §4 逆向映射表提取：编号 → {SR引用, 状态}"""
    reverse = {}
    # | AR-P1-001 | Import 目录扫描... | Phase 1 | SR-001, SR-005 | ✅ | P0 |
    # SR 引用列支持：SR-xxx / SR-C5(全局质量) / 全局(全局质量门禁)
    pattern = r"\|[ \t]*(AR-\w+-\d+)[ \t]*\|[ \t]*(.*?)[ \t]*\|[ \t]*(.*?)[ \t]*\|[ \t]*(SR-[\w, -]+|全局)[ \t]*\|[ \t]*([✅🚧📋])[ \t]*\|[ \t]*(P[012])[ \t]*\|"
    for m in re.finditer(pattern, text):
        ar_id = m.group(1)
        sr_ref = m.group(4).strip()
        status = m.group(5)
        reverse[ar_id] = {"sr_ref": sr_ref, "status": status}
    return reverse

def parse_forward_map_v2(text):
    """从 ar-001 §3 正向映射表提取：SR → [AR列表]"""
    forward = {}  # SR -> [AR列表]
    # | SR-001 | 本地 Markdown 批量导入 | AR-P1-001, AR-P1-002 | 2 |
    pattern = r"\|[ \t]*(SR-\d+)[ \t]*\|[ \t]*(.*?)[ \t]*\|[ \t]*(.*?)[ \t]*\|[ \t]*(\d+)[ \t]*\|"
    for m in re.finditer(pattern, text):
        sr_id = m.group(1)
        ar_list_str = m.group(3).strip()
        ar_ids = re.findall(r"(AR-\w+-\d+)", ar_list_str)
        if ar_ids:
            forward[sr_id] = ar_ids
    return forward

def check_list_reverse_gap(ar_map, reverse_map):
    """Check 1: §2 有但 §4 无的 AR（反向条目缺失）"""
    issues = []
    for ar_id in ar_map:
        if ar_id not in reverse_map:
            issues.append({
                "type": "AR_MISSING_IN_REVERSE",
                "severity": "ERROR",
                "item": ar_id,
                "detail": f"AR {ar_id} 在 §2 AR 清单中存在，但 §4 逆向映射表中无对应行",
                "fix": f"在 ar-001 §4 中为 {ar_id} 添加逆向映射行（复制 §2 行或补全新行）"
            })
    return issues

def check_orphan_ar_v2(ar_map, reverse_map):
    """Check 2: §4 有但 §2 无的 AR（孤儿）"""
    issues = []
    orphans = set(reverse_map.keys()) - set(ar_map.keys())
    for ar_id in sorted(orphans):
        issues.append({
            "type": "ORPHAN_AR_IN_REVERSE",
            "severity": "ERROR",
            "item": ar_id,
            "detail": f"AR {ar_id} 在 §4 逆向映射表存在但 §2 AR 清单中无此条目",
            "fix": f"在 §2 AR 清单中添加 {ar_id} 条目，或从 §4 中删除"
        })
    return issues

def check_status_drift(ar_map, reverse_map):
    """Check 3: §2 和 §4 中同一 AR 的状态不一致"""
    issues = []
    for ar_id, info in ar_map.items():
        if ar_id in reverse_map:
            s2_status = info["status"]
            s4_status = reverse_map[ar_id]["status"]
            if s2_status != s4_status:
                issues.append({
                    "type": "AR_STATUS_DRIFT",
                    "severity": "WARNING",
                    "item": ar_id,
                    "detail": f"状态不一致：§2={s2_status}, §4={s4_status}",
                    "fix": f"将 §2 或 §4 中 {ar_id} 的状态统一为 {s2_status} 或 {s4_status}"
                })
    return issues

def check_forward_ar_refs(ar_map, forward_map):
    """Check 4: §3 正向表中引用的 AR 在 §2 中不存在"""
    issues = []
    all_ars_in_forward = set()
    for sr_id, ar_ids in forward_map.items():
        for ar_id in ar_ids:
            all_ars_in_forward.add(ar_id)
            if ar_id not in ar_map:
                issues.append({
                    "type": "FORWARD_REF_MISSING_IN_LIST",
                    "severity": "ERROR",
                    "item": f"{sr_id} → {ar_id}",
                    "detail": f"§3 正向表 {sr_id} 引用 {ar_id}，但 §2 AR 清单中无此条目",
                    "fix": f"在 §2 中添加 {ar_id} 条目，或修正 §3 中 {sr_id} 的引用"
                })
    return issues

def check_ar_numbering(ar_map, reverse_map, forward_map):
    """Check 5: AR 编号格式规范检查"""
    issues = []
    valid_prefixes = {"AR-P1", "AR-P2", "AR-P3", "AR-P4", "AR-SYS", "AR-FUT", "AR-ASM", "AR-QSV"}
    
    all_ars = set(ar_map.keys()) | set(reverse_map.keys())
    for ar_id in sorted(all_ars):
        prefix = ar_id.rsplit("-", 1)[0]
        if prefix not in valid_prefixes:
            issues.append({
                "type": "INVALID_AR_PREFIX",
                "severity": "WARNING",
                "item": ar_id,
                "detail": f"AR 编号前缀 '{prefix}' 不在规范范围内：{', '.join(sorted(valid_prefixes))}",
                "fix": "检查 AR 编号是否使用已注册的前缀"
            })
    return issues

def main():
    ar_text = read_file(SPEC_DIR / "ar-001-sr-ar-mapping.md")
    if not ar_text:
        print(json.dumps({
            "status": "ERROR",
            "summary": "无法读取 ar-001（活跃需求文档）",
            "details": []
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    ar_map = parse_ar_list_v2(ar_text)
    reverse_map = parse_reverse_map_v2(ar_text)
    forward_map = parse_forward_map_v2(ar_text)

    all_issues = []
    all_issues.extend(check_list_reverse_gap(ar_map, reverse_map))
    all_issues.extend(check_orphan_ar_v2(ar_map, reverse_map))
    all_issues.extend(check_status_drift(ar_map, reverse_map))
    all_issues.extend(check_forward_ar_refs(ar_map, forward_map))
    all_issues.extend(check_ar_numbering(ar_map, reverse_map, forward_map))

    errors = [i for i in all_issues if i["severity"] == "ERROR"]
    warnings = [i for i in all_issues if i["severity"] == "WARNING"]

    list_count = len(ar_map)
    rev_count = len(reverse_map)
    fwd_srs = len(forward_map)
    
    # Stats
    list_only = set(ar_map.keys()) - set(reverse_map.keys())
    rev_only = set(reverse_map.keys()) - set(ar_map.keys())
    both = set(ar_map.keys()) & set(reverse_map.keys())
    matched = len(both)

    result = {
        "status": "PASS" if len(errors) == 0 else "FAIL",
        "check_name": "AR Mapping Consistency (Level 1)",
        "summary": f"§2={list_count} | §3(SR)={fwd_srs} | §4={rev_count} | 对齐={matched}/{list_count} | Issues={len(errors)}E/{len(warnings)}W",
        "ar_list_count": list_count,
        "ar_reverse_count": rev_count,
        "sr_mapped_count": fwd_srs,
        "matched_count": matched,
        "list_only_count": len(list_only),
        "reverse_only_count": len(rev_only),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "issues": all_issues,
        "details": {
            "list_only": sorted(list_only),
            "reverse_only": sorted(rev_only),
            "status_drift_count": len([i for i in all_issues if i["type"] == "AR_STATUS_DRIFT"])
        }
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
