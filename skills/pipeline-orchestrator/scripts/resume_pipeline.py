#!/usr/bin/env python3
"""
Resume pipeline from checkpoint.
Usage: python3 resume_pipeline.py --checkpoint <checkpoint.json>
"""

import json
import sys
from pathlib import Path
from datetime import datetime


STAGE_ORDER = ["1_input_qa", "2_multi_path", "3_convergence", "4_verification", "5_constraint", "6_expert_gate"]


def resume(checkpoint_path):
    with open(checkpoint_path) as f:
        state = json.load(f)

    current = None
    for i, stage_name in enumerate(STAGE_ORDER):
        if state['stages'][stage_name]['status'] == 'in_progress':
            current = stage_name
            state['current_stage'] = i + 1
            break
        elif state['stages'][stage_name]['status'] == 'pending':
            state['current_stage'] = i + 1
            current = stage_name
            break

    if current is None:
        state['status'] = 'completed'
        print(json.dumps({"status": "completed", "task_id": state['task_id']}))
        return state

    state['status'] = 'resumed'
    state['resumed_at'] = datetime.now().isoformat()

    # Write updated state
    state_path = Path(checkpoint_path).parent / 'state.json'
    with open(state_path, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

    print(json.dumps({
        "status": "resumed",
        "task_id": state['task_id'],
        "resume_stage": current,
        "stage_number": state['current_stage'],
        "completed_stages": [s for s in STAGE_ORDER if state['stages'][s]['status'] == 'passed']
    }))

    return state


def main():
    if len(sys.argv) < 3 or sys.argv[1] != '--checkpoint':
        print(json.dumps({"error": "Usage: resume_pipeline.py --checkpoint <checkpoint.json>"}))
        sys.exit(1)

    checkpoint_path = Path(sys.argv[2])
    if not checkpoint_path.exists():
        print(json.dumps({"error": f"Checkpoint not found: {checkpoint_path}"}))
        sys.exit(1)

    resume(checkpoint_path)


if __name__ == '__main__':
    main()
