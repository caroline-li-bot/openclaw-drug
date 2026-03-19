#!/usr/bin/env python3
"""
Deterministic retrieval from ChEMBL - can be used as fallback
Usage: python retrieve.py entity [entity2 ...]
"""

import sys
from chembl_webresource_client.new_client import new_client

def retrieve_entities(entities):
    """Retrieve information for a list of entities"""
    results = []
    compound_client = new_client.molecule
    
    for entity in entities:
        print(f"\n=== Searching ChEMBL for: {entity}")
        
        # Try as drug/compound name first
        molecules = list(compound_client.filter(pref_name__icontains=entity))
        
        if not molecules:
            print(f"No compounds found for '{entity}'")
            continue
        
        for mol in molecules[:5]:
            mol_id = mol['molecule_chembl_id']
            mol_name = mol.get('pref_name', 'Unknown')
            smiles = mol.get('canonical_smiles', 'Not available')
            
            print(f"\nCompound: {mol_name} [{mol_id}]")
            print(f"SMILES: {smiles[:100]}{'...' if len(smiles) > 100 else ''}")
            
            # Get activities
            activities = list(new_client.activity.filter(molecule_chembl_id=mol_id).only(
                ['target_chembl_id', 'target_pref_name', 'pchembl_value', 'standard_type']))
            
            if activities:
                print(f"Found {len(activities)} activities. Top 10 targets:")
                seen_targets = set()
                count = 0
                for act in activities:
                    target_name = act.get('target_pref_name', 'Unknown')
                    if target_name not in seen_targets and count < 10:
                        seen_targets.add(target_name)
                        pchembl = act.get('pchembl_value', 'N/A')
                        stype = act.get('standard_type', 'N/A')
                        print(f"  - {target_name}: pChEMBL = {pchembl} ({stype})")
                        count += 1
            results.append({
                'entity': entity,
                'compound_chembl_id': mol_id,
                'compound_name': mol_name,
                'target_count': len(activities)
            })
    
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python retrieve.py <drug-name-or-chembl-id> [...]")
        sys.exit(1)
    
    entities = sys.argv[1:]
    retrieve_entities(entities)
