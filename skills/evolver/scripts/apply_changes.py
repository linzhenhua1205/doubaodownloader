#!/usr/bin/env python3
"""
Evolver Change Applier
Applies evolution changes to skills, rules, and memory
"""
import os
import json
from datetime import datetime

RULE_FILE = os.path.join(os.path.dirname(__file__), '..', '..', '..', '.trae', 'rules', 'RULE.md')
MEMORY_FILE = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'MEMORY.md')
EVENTS_FILE = os.path.join(os.path.dirname(__file__), '..', 'assets', 'gep', 'events.jsonl')

def update_rule_md(content):
    """Update RULE.md with new guidelines"""
    if not os.path.exists(RULE_FILE):
        print(f"[WARN] RULE.md not found: {RULE_FILE}")
        return False
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_section = f"\n\n## Evolution Update ({timestamp})\n\n{content}\n"
    
    with open(RULE_FILE, 'a', encoding='utf-8') as f:
        f.write(new_section)
    
    print(f"[Evolver] Updated RULE.md")
    return True

def update_memory_md(content):
    """Update MEMORY.md with new insights"""
    if not os.path.exists(MEMORY_FILE):
        print(f"[WARN] MEMORY.md not found: {MEMORY_FILE}")
        return False
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_entry = f"\n\n### [{timestamp}] Evolution Update\n\n{content}\n"
    
    with open(MEMORY_FILE, 'a', encoding='utf-8') as f:
        f.write(new_entry)
    
    print(f"[Evolver] Updated MEMORY.md")
    return True

def update_skill(skill_name, content):
    """Update a specific skill"""
    skill_path = os.path.join(os.path.dirname(__file__), '..', '..', skill_name)
    
    if not os.path.exists(skill_path):
        print(f"[WARN] Skill not found: {skill_name}")
        return False
    
    skill_file = os.path.join(skill_path, 'SKILL.md')
    
    if not os.path.exists(skill_file):
        print(f"[WARN] SKILL.md not found for {skill_name}")
        return False
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_section = f"\n\n## Evolution Update ({timestamp})\n\n{content}\n"
    
    with open(skill_file, 'a', encoding='utf-8') as f:
        f.write(new_section)
    
    print(f"[Evolver] Updated skill: {skill_name}")
    return True

def write_event(trigger, gene_selected=None, validation_result='N/A', applied=False):
    """Write evolution event to log"""
    event = {
        'event_id': f"event_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        'timestamp': datetime.now().isoformat(),
        'trigger': trigger,
        'gene_selected': gene_selected,
        'validation_result': validation_result,
        'applied': applied,
        'strategy': os.environ.get('EVOLVE_STRATEGY', 'balanced')
    }
    
    with open(EVENTS_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(event, ensure_ascii=False) + '\n')
    
    return event

def apply_change(gene, review=False):
    """Apply a gene's modification"""
    print(f"[Evolver] Applying gene: {gene['name']}")
    
    modification = gene.get('modification', '')
    category = gene.get('category', '')
    
    if review:
        print(f"[Evolver] Review mode - modification: {modification}")
        print(f"[Evolver] Would apply changes to appropriate files...")
        write_event(f"Review mode: {gene['name']}", gene_selected=gene['gene_id'], validation_result='REVIEW', applied=False)
        return True
    
    success = False
    
    if category == 'memory':
        success = update_rule_md(modification) or update_memory_md(modification)
    elif category == 'optimization':
        success = update_rule_md(f"Optimization Guideline: {modification}")
    elif category == 'reliability':
        success = update_rule_md(f"Reliability Enhancement: {modification}")
    else:
        success = update_rule_md(f"Evolution Update: {modification}")
    
    if success:
        write_event(f"Applied gene: {gene['name']}", gene_selected=gene['gene_id'], validation_result='PASS', applied=True)
        print(f"[Evolver] Successfully applied {gene['name']}")
    else:
        write_event(f"Failed to apply: {gene['name']}", gene_selected=gene['gene_id'], validation_result='FAIL', applied=False)
        print(f"[Evolver] Failed to apply {gene['name']}")
    
    return success

def main():
    print("[Evolver] Change Applier - This script is designed to be called by evolve.py")
    print("[Evolver] Usage: python evolve.py [--review]")
    print("[Evolver] Do not run this script directly.")

if __name__ == '__main__':
    main()
