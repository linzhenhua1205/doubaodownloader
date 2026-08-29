#!/usr/bin/env python3
"""
Analyze a system/process/tool using the Function-Life framework.

Usage:
    python3 analyze_system_function.py --name "System Name" \
        --input "input1, input2" \
        --output "output1, output2" \
        --complexity low|medium|high \
        --decision-cost small|medium|large \
        [--context "extra context info"]
"""

import argparse


def analyze_system(name, inputs, outputs, complexity, decision_cost, context=""):
    print(f"\n{'='*60}")
    print(f"  System Analysis: {name}")
    print(f"{'='*60}\n")

    # Part 1: Input Mapping
    print("📥 [Input Layer]")
    input_list = [s.strip() for s in inputs.split(",") if s.strip()]
    print(f"  Sources ({len(input_list)}):")
    for i, inp in enumerate(input_list, 1):
        print(f"    {i}. {inp}")
    print()

    # Part 2: State Assessment
    print("⚙️  [Function Layer]")
    complexity_map = {
        "low": ("Simple linear function", "Direct input→output mapping, no branching"),
        "medium": ("Multi-branch decision tree", "Has if-else flows, context-dependent paths"),
        "high": ("Complex coupled system", "Multi-constraint, multi-branch, multi-objective, interfering mechanisms"),
    }
    func_type, desc = complexity_map.get(complexity, complexity_map["medium"])
    print(f"  Type: {func_type}")
    print(f"  Description: {desc}")
    print()

    # Part 3: Output Mapping
    print("📤 [Output Layer]")
    output_list = [s.strip() for s in outputs.split(",") if s.strip()]
    print(f"  Outputs ({len(output_list)}):")
    for i, out in enumerate(output_list, 1):
        print(f"    {i}. {out}")
    print()

    # Part 4: Decision Rigor
    print("💰 [Decision Cost Calibration]")
    cost_map = {
        "small": ("Low cost (¥5-level)", "Quick intuition-based decision", "Minimal"),
        "medium": ("Medium cost", "Partial analysis + some verification", "Moderate"),
        "large": ("High cost (¥5M-level)", "Full dimensional analysis + expert support", "Heavy"),
    }
    cost_label, approach, effort = cost_map.get(decision_cost, cost_map["medium"])
    print(f"  Investment: {cost_label}")
    print(f"  Approach: {approach}")
    print(f"  Effort: {effort}")
    print()

    # Part 5: Summary
    print(f"{'='*60}")
    print(f"  📋 Summary")
    print(f"{'='*60}")
    print(f"  System: {name}")
    print(f"  Alive? ✅ YES — has input({len(input_list)}) → process → output({len(output_list)})")
    print(f"  Complexity: {complexity.upper()}")
    print(f"  Recommended decision approach: {approach}")
    print()

    if context:
        print(f"  Extra Context: {context}")
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze system using Function-Life framework")
    parser.add_argument("--name", required=True, help="System name")
    parser.add_argument("--input", required=True, help="Input sources (comma separated)")
    parser.add_argument("--output", required=True, help="Output targets (comma separated)")
    parser.add_argument("--complexity", choices=["low", "medium", "high"], default="medium")
    parser.add_argument("--decision-cost", choices=["small", "medium", "large"], default="medium")
    parser.add_argument("--context", default="", help="Extra context")
    args = parser.parse_args()

    analyze_system(
        args.name, args.input, args.output,
        args.complexity, args.decision_cost, args.context
    )
