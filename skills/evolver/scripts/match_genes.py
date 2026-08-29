#!/usr/bin/env python3
"""
Evolver Gene Matcher
Matches identified issues against gene library
"""
import os
import json
import re

GENES_FILE = os.path.join(os.path.dirname(__file__), '..', 'assets', 'gep', 'genes.json')
CAPSULES_FILE = os.path.join(os.path.dirname(__file__), '..', 'assets', 'gep', 'capsules.json')

def load_genes():
    """Load genes from genes.json"""
    with open(GENES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_capsules():
    """Load capsules from capsules.json"""
    with open(CAPSULES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def match_gene(pattern, genes):
    """Match a pattern against genes"""
    matches = []
    
    for gene in genes:
        trigger_pattern = gene.get('trigger_pattern', '')
        confidence = gene.get('confidence', 0)
        
        if re.search(trigger_pattern, pattern, re.IGNORECASE):
            matches.append({
                'gene': gene,
                'confidence': confidence,
                'match_score': calculate_match_score(pattern, trigger_pattern)
            })
    
    # Sort by match score and confidence
    matches.sort(key=lambda x: (x['match_score'], x['confidence']), reverse=True)
    
    return matches

def calculate_match_score(pattern, trigger_pattern):
    """Calculate match score between pattern and trigger"""
    pattern_lower = pattern.lower()
    trigger_lower = trigger_pattern.lower()
    
    if trigger_lower in pattern_lower:
        return 1.0
    elif any(p in pattern_lower for p in trigger_lower.split('|')):
        return 0.7
    else:
        return 0.0

def match_capsule(gene_ids, capsules):
    """Match genes to capsules"""
    matched_capsules = []
    
    for capsule in capsules:
        capsule_genes = capsule.get('genes', [])
        matching_genes = set(gene_ids) & set(capsule_genes)
        
        if matching_genes:
            matched_capsules.append({
                'capsule': capsule,
                'matching_genes': list(matching_genes),
                'match_ratio': len(matching_genes) / len(capsule_genes)
            })
    
    matched_capsules.sort(key=lambda x: x['match_ratio'], reverse=True)
    
    return matched_capsules

def select_best_gene(pattern, strategy='balanced'):
    """Select the best gene based on pattern and strategy"""
    genes = load_genes()
    matches = match_gene(pattern, genes)
    
    if not matches:
        return None
    
    # Apply strategy weighting
    if strategy == 'repair-only':
        matches = [m for m in matches if m['gene']['category'] == 'reliability']
    elif strategy == 'innovate':
        matches = [m for m in matches if m['gene']['category'] == 'innovation']
    elif strategy == 'harden':
        reliability_matches = [m for m in matches if m['gene']['category'] == 'reliability']
        if reliability_matches:
            matches = reliability_matches
    
    return matches[0]['gene'] if matches else None

def main():
    print("[Evolver] Loading gene library...")
    
    genes = load_genes()
    capsules = load_capsules()
    
    print(f"[Evolver] Loaded {len(genes)} genes and {len(capsules)} capsules")
    
    # Test matching
    test_patterns = ['TimeoutError', 'KeyError', 'performance issue']
    
    for pattern in test_patterns:
        best_gene = select_best_gene(pattern)
        if best_gene:
            print(f"[Evolver] Pattern '{pattern}' -> Gene: {best_gene['name']} (confidence: {best_gene['confidence']})")
        else:
            print(f"[Evolver] Pattern '{pattern}' -> No matching gene found")
    
    print("[Evolver] Gene matching complete")

if __name__ == '__main__':
    main()
