#!/usr/bin/env python3
"""
Input quality check script for Stage 1.
Reads task input JSON, validates against QA checklist, returns structured verdict.
Usage: python3 quality_check.py <input.json>
"""

import json
import sys
from pathlib import Path


SOURCE_LEVELS = {'S': 1.0, 'A': 0.9, 'B': 0.7, 'C': 0.4, 'D': 0.1}


def check_completeness(task):
    """Check if task has clear objective, sufficient background, complete materials."""
    issues = []
    if not task.get('objective'):
        issues.append({"type": "missing_objective", "severity": "critical"})
    if not task.get('background'):
        issues.append({"type": "missing_background", "severity": "major"})
    if not task.get('materials') and not task.get('sources'):
        issues.append({"type": "missing_materials", "severity": "major"})
    return issues


def check_credibility(sources):
    """Grade each source and check minimum credibility level."""
    issues = []
    grades = []
    for src in sources:
        level = src.get('credibility_level', 'D')
        weight = SOURCE_LEVELS.get(level, 0.1)
        grades.append({"source": src.get('name', 'unknown'), "level": level, "weight": weight})
        if level == 'D':
            issues.append({
                "type": "low_credibility",
                "detail": f"Source '{src.get('name', 'unknown')}' is unverified (D)"
            })
    return grades, issues


def check_consistency(materials):
    """Basic consistency check — placeholder for advanced NLP-based detection."""
    # Future: implement contradiction detection across materials
    return []


def check_feasibility(task):
    """Check if task is doable within current constraints."""
    issues = []
    estimated_tokens = task.get('estimated_tokens', 0)
    if estimated_tokens > 32000:
        issues.append({"type": "token_budget_warning", "severity": "warning"})
    return issues


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: quality_check.py <input.json>"}))
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(json.dumps({"error": f"File not found: {input_path}"}))
        sys.exit(1)

    with open(input_path) as f:
        task = json.load(f)

    all_issues = []
    all_issues.extend(check_completeness(task))
    sources = task.get('sources', [])
    source_grades, cred_issues = check_credibility(sources)
    all_issues.extend(cred_issues)
    all_issues.extend(check_consistency(task.get('materials', [])))
    all_issues.extend(check_feasibility(task))

    critical_issues = [i for i in all_issues if i.get('severity') == 'critical']
    major_issues = [i for i in all_issues if i.get('severity') == 'major']
    warnings = [i for i in all_issues if i.get('severity') == 'warning']

    if critical_issues:
        verdict = "reject"
    elif major_issues:
        verdict = "conditional_pass"
    else:
        verdict = "pass"

    result = {
        "verdict": verdict,
        "source_grades": source_grades,
        "issues": all_issues,
        "enhancement_log": [],
        "summary": {
            "critical": len(critical_issues),
            "major": len(major_issues),
            "warnings": len(warnings)
        }
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
