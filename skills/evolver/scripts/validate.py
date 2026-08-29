#!/usr/bin/env python3
"""
Evolver Validator
Validates proposed changes before application
"""
import os
import subprocess
import json

EVENTS_FILE = os.path.join(os.path.dirname(__file__), '..', 'assets', 'gep', 'events.jsonl')

def run_validation_command(command):
    """Run a validation command"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'stdout': '',
            'stderr': 'Command timed out',
            'returncode': -1
        }
    except Exception as e:
        return {
            'success': False,
            'stdout': '',
            'stderr': str(e),
            'returncode': -2
        }

def validate_gene(gene):
    """Validate a gene's proposed changes"""
    validation_command = gene.get('validation_command', '')
    
    if not validation_command:
        print(f"[Evolver] No validation command for gene: {gene['name']}")
        return {
            'valid': True,
            'message': 'No validation required',
            'details': {}
        }
    
    print(f"[Evolver] Validating gene: {gene['name']}")
    print(f"[Evolver] Command: {validation_command}")
    
    result = run_validation_command(validation_command)
    
    if result['success']:
        print(f"[Evolver] Validation PASSED")
        return {
            'valid': True,
            'message': 'Validation passed',
            'details': result
        }
    else:
        print(f"[Evolver] Validation FAILED: {result['stderr']}")
        return {
            'valid': False,
            'message': f'Validation failed: {result["stderr"]}',
            'details': result
        }

def validate_gene_syntax(gene):
    """Validate gene JSON syntax"""
    required_fields = ['gene_id', 'name', 'trigger_pattern', 'modification']
    
    missing_fields = [f for f in required_fields if f not in gene]
    
    if missing_fields:
        return {
            'valid': False,
            'message': f'Missing required fields: {", ".join(missing_fields)}'
        }
    
    if not isinstance(gene.get('confidence', 0), (int, float)):
        return {
            'valid': False,
            'message': 'Confidence must be a number'
        }
    
    if gene.get('confidence', 0) < 0 or gene.get('confidence', 0) > 1:
        return {
            'valid': False,
            'message': 'Confidence must be between 0 and 1'
        }
    
    return {
        'valid': True,
        'message': 'Gene syntax valid'
    }

def validate_capsule(capsule):
    """Validate capsule JSON syntax"""
    required_fields = ['capsule_id', 'name', 'genes']
    
    missing_fields = [f for f in required_fields if f not in capsule]
    
    if missing_fields:
        return {
            'valid': False,
            'message': f'Missing required fields: {", ".join(missing_fields)}'
        }
    
    if not isinstance(capsule.get('genes', []), list):
        return {
            'valid': False,
            'message': 'Genes must be a list'
        }
    
    return {
        'valid': True,
        'message': 'Capsule syntax valid'
    }

def validate_genes_file(filepath):
    """Validate genes.json file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            genes = json.load(f)
        
        if not isinstance(genes, list):
            return {
                'valid': False,
                'message': 'genes.json must be a list'
            }
        
        for gene in genes:
            result = validate_gene_syntax(gene)
            if not result['valid']:
                return {
                    'valid': False,
                    'message': f'Invalid gene: {gene.get("gene_id", "unknown")} - {result["message"]}'
                }
        
        return {
            'valid': True,
            'message': f'All {len(genes)} genes valid'
        }
    except json.JSONDecodeError as e:
        return {
            'valid': False,
            'message': f'JSON parse error: {e}'
        }
    except Exception as e:
        return {
            'valid': False,
            'message': f'Error reading file: {e}'
        }

def main():
    print("[Evolver] Starting validation...")
    
    genes_file = os.path.join(os.path.dirname(__file__), '..', 'assets', 'gep', 'genes.json')
    capsules_file = os.path.join(os.path.dirname(__file__), '..', 'assets', 'gep', 'capsules.json')
    
    # Validate genes file
    genes_result = validate_genes_file(genes_file)
    print(f"[Evolver] Genes file: {genes_result['message']}")
    
    # Validate capsules file
    try:
        with open(capsules_file, 'r', encoding='utf-8') as f:
            capsules = json.load(f)
        
        for capsule in capsules:
            result = validate_capsule(capsule)
            print(f"[Evolver] Capsule {capsule['capsule_id']}: {result['message']}")
    except Exception as e:
        print(f"[Evolver] Error validating capsules: {e}")
    
    print("[Evolver] Validation complete")

if __name__ == '__main__':
    main()
