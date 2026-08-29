#!/usr/bin/env python3
"""
Initialize pipeline state for the orchestrator.
Reads pipeline config, creates state file with checkpoint support.
Usage: python3 init_pipeline.py --config <pipeline_config.yaml>
"""

import json
import sys
import os
from datetime import datetime


DEFAULT_PROFILES = {
    "quick": {"parallel_paths": 1, "max_iterations": 2, "quality_min_level": "C"},
    "standard": {"parallel_paths": 3, "max_iterations": 5, "quality_min_level": "C", "sub_agent": True},
    "deep": {"parallel_paths": 5, "max_iterations": 8, "quality_min_level": "B", "sub_agent": True, "source_min_weight": 0.7}
}


def init_state(config):
    task_name = config.get('task', {}).get('name', 'unnamed_task')
    profile_name = config.get('pipeline', {}).get('profile', 'standard')
    profile = DEFAULT_PROFILES.get(profile_name, DEFAULT_PROFILES['standard'])

    task_id = f"{task_name.lower().replace(' ', '-')}-{datetime.now().strftime('%Y%m%d')}"

    state = {
        "task_id": task_id,
        "task_name": task_name,
        "status": "initialized",
        "created_at": datetime.now().isoformat(),
        "current_stage": 0,
        "profile": profile_name,
        "profile_config": profile,
        "stages": {
            "1_input_qa": {"status": "pending", "output": None, "checkpoint": None},
            "2_multi_path": {"status": "pending", "output": None, "checkpoint": None},
            "3_convergence": {"status": "pending", "output": None, "checkpoint": None},
            "4_verification": {"status": "pending", "output": None, "checkpoint": None},
            "5_constraint": {"status": "pending", "output": None, "checkpoint": None},
            "6_expert_gate": {"status": "pending", "output": None, "checkpoint": None}
        },
        "metrics": {
            "iterations_used": 0,
            "paths_spawned": 0,
            "conflicts_resolved": 0,
            "constraint_violations": 0
        },
        "errors": []
    }

    # Create pipeline working directory
    state_dir = f"tmp/pipeline/{task_id}"
    os.makedirs(state_dir, exist_ok=True)

    # Write state
    state_path = f"{state_dir}/state.json"
    with open(state_path, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

    print(json.dumps({"task_id": task_id, "state_file": state_path, "status": "initialized", "profile": profile_name}))
    return state


def main():
    if len(sys.argv) < 3 or sys.argv[1] != '--config':
        print(json.dumps({"error": "Usage: init_pipeline.py --config <config.json>"}))
        sys.exit(1)

    config_path = sys.argv[2]
    try:
        with open(config_path) as f:
            config = json.load(f)
    except FileNotFoundError:
        print(json.dumps({"error": f"Config file not found: {config_path}"}))
        sys.exit(1)

    init_state(config)


if __name__ == '__main__':
    main()
