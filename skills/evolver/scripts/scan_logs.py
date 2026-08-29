#!/usr/bin/env python3
"""
Evolver Log Scanner
Scans conversation logs for error patterns and inefficiencies
"""
import os
import re
import json
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'conversation-log')
EVENTS_FILE = os.path.join(os.path.dirname(__file__), '..', 'assets', 'gep', 'events.jsonl')

ERROR_PATTERNS = [
    r'TimeoutError',
    r'ConnectionRefusedError',
    r'KeyError',
    r'IndexError',
    r'TypeError',
    r'AttributeError',
    r'UnicodeEncodeError',
    r'UnicodeDecodeError',
    r'ValueError',
    r'FileNotFoundError',
    r'PermissionError',
    r'api_timeout',
    r'request timed out',
    r'connection refused',
    r'503 Service Unavailable',
    r'service unavailable',
    r'overcomplicated',
    r'too complex',
    r'refactor',
    r'slow',
    r'performance',
    r'latency',
    r'learn',
    r'remember',
    r'update knowledge',
    r'new feature',
    r'enhance',
    r'improve',
    r'topic boundary',
    r'intent misclassification',
    r'misclassification',
    r'category imbalance',
    r'data truncation',
    r'content truncated',
    r'skill not found',
    r'failed to apply',
    r'evolution failed',
    r'validation failed',
    r'git clone error',
    r'RPC failed',
    r'Connection was reset',
    r'request was aborted',
    r'cURL error'
]

def scan_logs():
    """Scan conversation logs for error patterns (recursive)"""
    findings = []
    
    if not os.path.exists(LOG_DIR):
        print(f"[INFO] Log directory not found: {LOG_DIR}")
        return findings
    
    for root, dirs, files in os.walk(LOG_DIR):
        for filename in files:
            if filename.endswith('.md') or filename.endswith('.json') or filename.endswith('.jsonl'):
                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, LOG_DIR)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    for pattern in ERROR_PATTERNS:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            findings.append({
                                'file': rel_path,
                                'pattern': pattern,
                                'count': len(matches),
                                'sample': matches[:3]
                            })
                except Exception as e:
                    print(f"[ERROR] Error reading {rel_path}: {e}")
    
    return findings

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

def main():
    print("[Evolver] Starting log scan...")
    
    findings = scan_logs()
    
    if findings:
        print(f"[Evolver] Found {len(findings)} issues:")
        for finding in findings:
            print(f"  - {finding['pattern']} ({finding['count']} times) in {finding['file']}")
        
        for finding in findings:
            write_event(f"Pattern detected: {finding['pattern']} in {finding['file']}")
    else:
        print("[Evolver] No issues found in logs")
        write_event("Log scan completed, no issues found")
    
    print("[Evolver] Log scan complete")

if __name__ == '__main__':
    main()
