#!/usr/bin/env python3
"""
Evolver - Main Entry Point
Agent Self-Evolution Engine
Usage: python evolve.py [--review] [--loop]
"""
import os
import sys
import time
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from scan_logs import scan_logs, write_event
from match_genes import select_best_gene
from apply_changes import apply_change
from validate import validate_gene, validate_genes_file

def run_evolution_cycle(review=False):
    """Run one evolution cycle"""
    print(f"\n{'='*60}")
    print(f"[Evolver] Evolution Cycle - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    strategy = os.environ.get('EVOLVE_STRATEGY', 'balanced')
    print(f"[Evolver] Strategy: {strategy}")
    print(f"[Evolver] Review Mode: {'ON' if review else 'OFF'}")
    
    # Step 1: Scan logs
    print("\n[Evolver] Step 1: Scanning conversation logs...")
    findings = scan_logs()
    
    if not findings:
        print("[Evolver] No issues found. Evolution cycle complete.")
        write_event("Evolution cycle completed, no issues found")
        return True
    
    print(f"[Evolver] Found {len(findings)} issues")
    
    # Step 2: Validate gene library
    print("\n[Evolver] Step 2: Validating gene library...")
    genes_file = os.path.join(os.path.dirname(__file__), '..', 'assets', 'gep', 'genes.json')
    genes_result = validate_genes_file(genes_file)
    print(f"[Evolver] Gene library: {genes_result['message']}")
    
    if not genes_result['valid']:
        print("[Evolver] Gene library validation failed. Aborting evolution.")
        write_event("Gene library validation failed")
        return False
    
    # Step 3: Match genes
    print("\n[Evolver] Step 3: Matching genes to issues...")
    applied_count = 0
    skipped_count = 0
    
    for finding in findings:
        pattern = finding['pattern']
        print(f"\n[Evolver] Processing pattern: {pattern}")
        
        gene = select_best_gene(pattern, strategy)
        
        if not gene:
            print(f"[Evolver] No matching gene found for: {pattern}")
            write_event(f"No gene matched: {pattern}")
            skipped_count += 1
            continue
        
        print(f"[Evolver] Selected gene: {gene['name']} (confidence: {gene['confidence']})")
        
        # Step 4: Validate gene
        print(f"[Evolver] Validating gene...")
        validation = validate_gene(gene)
        
        if not validation['valid']:
            print(f"[Evolver] Gene validation failed: {validation['message']}")
            write_event(f"Gene validation failed: {gene['name']}", gene_selected=gene['gene_id'], validation_result='FAIL', applied=False)
            skipped_count += 1
            continue
        
        # Step 5: Apply changes
        print(f"[Evolver] Applying changes...")
        success = apply_change(gene, review=review)
        
        if success:
            applied_count += 1
            print(f"[Evolver] Successfully applied: {gene['name']}")
        else:
            skipped_count += 1
            print(f"[Evolver] Failed to apply: {gene['name']}")
    
    # Step 6: Summary
    print(f"\n{'='*60}")
    print(f"[Evolver] Evolution Cycle Complete")
    print(f"{'='*60}")
    print(f"[Evolver] Total issues found: {len(findings)}")
    print(f"[Evolver] Genes applied: {applied_count}")
    print(f"[Evolver] Issues skipped: {skipped_count}")
    print(f"[Evolver] Strategy: {strategy}")
    
    write_event(f"Evolution cycle complete: {applied_count} applied, {skipped_count} skipped")
    
    return applied_count > 0

def main():
    """Main entry point"""
    review = '--review' in sys.argv
    loop = '--loop' in sys.argv
    
    print("[Evolver] Agent Self-Evolution Engine")
    print("[Evolver] ==============================")
    
    if loop:
        print("[Evolver] Running in continuous loop mode")
        print("[Evolver] Press Ctrl+C to stop")
        
        try:
            cycle = 0
            while True:
                cycle += 1
                print(f"\n[Evolver] === Cycle {cycle} ===")
                run_evolution_cycle(review=review)
                print(f"[Evolver] Waiting 60 seconds for next cycle...")
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n[Evolver] Evolution stopped by user")
    else:
        run_evolution_cycle(review=review)
    
    print("\n[Evolver] Done")

if __name__ == '__main__':
    main()
