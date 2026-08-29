#!/usr/bin/env python3
"""
Check whether past experience can be safely reused in a new scenario.
Uses the Four Scenario Variables framework.

Usage:
    python3 check_experience_reuse.py
    Interactive Q&A mode.
"""


def ask_question(question, options=None):
    """Ask a question and get a simple rating (1-5)."""
    print(f"\n{question}")
    if options:
        for k, v in options.items():
            print(f"  {k}: {v}")
    while True:
        try:
            val = int(input("  Your rating (1-5, 1=completely different, 5=identical): "))
            if 1 <= val <= 5:
                return val
        except ValueError:
            pass
        print("  Please enter a number 1-5.")


def assess_reuse():
    print(f"\n{'='*60}")
    print(f"  🔄 Experience Reuse Assessment")
    print(f"{'='*60}")
    print(f"\n  For each variable, rate how similar the NEW scenario is")
    print(f"  to the OLD scenario where you have experience.")
    print(f"  1 = Completely different   5 = Identical")
    print(f"{'-'*60}")

    scores = {}

    # Variable 1: Context Baseline
    print(f"\n{'='*40}")
    print(f"  📋 Variable 1: Context Baseline")
    print(f"{'='*40}")
    scores["context"] = ask_question(
        "Industry environment (regulations, market conditions, competitors)?")
    scores["business_goal"] = ask_question(
        "Business goals and objectives?")
    scores["constraints"] = ask_question(
        "Constraints (timeline, quality standards, compliance)?")
    scores["process"] = ask_question(
        "Process and workflow norms?")

    # Variable 2: Resource Boundary
    print(f"\n{'='*40}")
    print(f"  💰 Variable 2: Resource Boundary")
    print(f"{'='*40}")
    scores["people"] = ask_question(
        "Team size, skills, availability?")
    scores["budget"] = ask_question(
        "Budget and funding?")
    scores["tools"] = ask_question(
        "Tools, systems, data access?")
    scores["external"] = ask_question(
        "External support and partnerships?")

    # Variable 3: Relationship Inversion (most critical)
    print(f"\n{'='*40}")
    print(f"  ⚠️  Variable 3: Relationship Inversion (CRITICAL)")
    print(f"{'='*40}")
    scores["leadership"] = ask_question(
        "Leadership support level (old scenario: were they supportive?)")
    scores["peer"] = ask_question(
        "Peer/team cooperation level?")
    scores["stakeholder"] = ask_question(
        "Stakeholder buy-in and alignment?")

    # Variable 4: Hidden Constraints
    print(f"\n{'='*40}")
    print(f"  🔒 Variable 4: Hidden Constraints")
    print(f"{'='*40}")
    scores["risk"] = ask_question(
        "Risk tolerance level?")
    scores["kpi"] = ask_question(
        "KPI/performance metrics?")
    scores["compliance"] = ask_question(
        "Compliance and regulatory requirements?")

    # Calculate results
    total = sum(scores.values())
    max_score = len(scores) * 5
    avg = total / max_score

    print(f"\n{'='*60}")
    print(f"  📊 Assessment Result")
    print(f"{'='*60}")
    print(f"  Overall Similarity: {avg:.0%} ({total}/{max_score})")
    print()

    # Breakdown
    categories = {
        "Context Baseline": ["context", "business_goal", "constraints", "process"],
        "Resource Boundary": ["people", "budget", "tools", "external"],
        "Relationship Inversion": ["leadership", "peer", "stakeholder"],
        "Hidden Constraints": ["risk", "kpi", "compliance"],
    }

    for cat, keys in categories.items():
        cat_total = sum(scores[k] for k in keys)
        cat_max = len(keys) * 5
        cat_pct = cat_total / cat_max
        warning = " ⚠️" if cat_pct < 0.5 else ""
        print(f"  {cat}: {cat_pct:.0%} ({cat_total}/{cat_max}){warning}")

    print()

    # Conclusion
    print(f"{'='*60}")
    print(f"  🎯 Conclusion")
    print(f"{'='*60}")

    if avg >= 0.8:
        print(f"  ✅ HIGH confidence — Experience is likely reusable with minor adjustments.")
    elif avg >= 0.6:
        print(f"  ⚠️  MEDIUM confidence — Experience can be a reference, but significant")
        print(f"      adjustments needed. Re-analyze all constraints carefully.")
    elif avg >= 0.4:
        print(f"  🚧 LOW confidence — High risk of failure if directly reused.")
        print(f"      Rebuild the approach from first principles using the new scenario.")
    else:
        print(f"  ❌ VERY LOW confidence — Past experience is likely misleading.")
        print(f"      Do NOT reuse. Start from scratch.")

    # Identify specific risk areas
    print(f"\n  🔍 Risk Areas:")
    risks = [(k, v) for k, v in scores.items() if v <= 2]
    if risks:
        risk_names = {
            "context": "Industry context",
            "business_goal": "Business goals",
            "constraints": "Constraints",
            "process": "Process norms",
            "people": "People resources",
            "budget": "Budget",
            "tools": "Tools/Data access",
            "external": "External support",
            "leadership": "Leadership support",
            "peer": "Peer cooperation",
            "stakeholder": "Stakeholder alignment",
            "risk": "Risk tolerance",
            "kpi": "KPI/Metrics",
            "compliance": "Compliance",
        }
        for k, v in risks:
            print(f"    - {risk_names.get(k, k)} (score: {v}/5)")
    else:
        print(f"    No critical risk areas identified.")
    print()


if __name__ == "__main__":
    assess_reuse()
