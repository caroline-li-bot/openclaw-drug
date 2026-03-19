#!/usr/bin/env python3
"""
Example: Retrieve drug-target interactions from ChEMBL
"""

from chembl_webresource_client.new_client import new_client

# Initialize clients
target_client = new_client.target
compound_client = new_client.molecule

def find_targets_by_drug(drug_name):
    """Find all targets for a given drug name"""
    # Search for compound
    molecules = compound_client.filter(pref_name__icontains=drug_name)
    results = []
    
    for mol in molecules[:10]:
        mol_id = mol['molecule_chembl_id']
        # Get activities for this molecule
        activities = new_client.activity.filter(molecule_chembl_id=mol_id)\
            .only(['target_chembl_id', 'pchembl_value', 'standard_type', 
                   'standard_value', 'target_pref_name'])
        
        for act in activities:
            results.append({
                'drug_chembl_id': mol_id,
                'drug_name': drug_name,
                'target_chembl_id': act['target_chembl_id'],
                'target_name': act.get('target_pref_name', 'Unknown'),
                'pchembl_value': act.get('pchembl_value'),
                'standard_type': act.get('standard_type'),
                'standard_value': act.get('standard_value')
            })
    
    return results

def find_compounds_by_target(target_name):
    """Find all compounds that interact with a given target"""
    # Search for target
    targets = target_client.filter(pref_name__icontains=target_name)
    results = []
    
    for target in targets[:5]:
        target_id = target['target_chembl_id']
        activities = new_client.activity.filter(target_chembl_id=target_id)\
            .filter(standard_type__icontains="IC50")\
            .only(['molecule_chembl_id', 'canonical_smiles', 'pchembl_value', 
                   'standard_value', 'molecule_pref_name'])
        
        for act in activities[:50]:
            results.append({
                'target_chembl_id': target_id,
                'target_name': target_name,
                'compound_chembl_id': act.get('molecule_chembl_id'),
                'compound_name': act.get('molecule_pref_name'),
                'smiles': act.get('canonical_smiles'),
                'pchembl_value': act.get('pchembl_value'),
                'IC50_value': act.get('standard_value')
            })
    
    return results

if __name__ == "__main__":
    # Example: get targets for imatinib
    print("=== Targets for imatinib ===")
    targets = find_targets_by_drug("imatinib")
    for t in targets[:20]:
        print(f"- {t['target_name']} ({t['target_chembl_id']}): pKi = {t['pchembl_value']}")
    
    print(f"\nTotal: {len(targets)} interactions found")
