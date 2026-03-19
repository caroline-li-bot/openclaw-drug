#!/usr/bin/env python3
"""
ChEMBL Skill - Drug-Target Interaction retrieval from ChEMBL
"""

from typing import List, Dict, Optional
from chembl_webresource_client.new_client import new_client

def retrieve(entities: List[str]) -> str:
    """Retrieve information for a list of entities"""
    output_lines = []
    compound_client = new_client.molecule
    
    for entity in entities:
        output_lines.append(f"## ChEMBL Results for: {entity}")
        
        molecules = list(compound_client.filter(pref_name__icontains=entity))
        
        if not molecules:
            output_lines.append(f"No compounds found matching '{entity}'")
            output_lines.append("")
            continue
        
        for mol in molecules[:5]:
            mol_id = mol['molecule_chembl_id']
            mol_name = mol.get('pref_name', 'Unknown')
            smiles = mol.get('canonical_smiles', 'Not available')
            
            output_lines.append(f"### {mol_name} [{mol_id}]")
            output_lines.append(f"**SMILES**: `{smiles[:100]}{'...' if len(smiles) > 100 else ''}`")
            
            activities = list(new_client.activity.filter(molecule_chembl_id=mol_id).only(
                ['target_chembl_id', 'target_pref_name', 'pchembl_value', 'standard_type']))
            
            if activities:
                output_lines.append(f"")
                output_lines.append(f"Found **{len(activities)}** activities. Top targets:")
                seen_targets = set()
                count = 0
                for act in activities:
                    target_name = act.get('target_pref_name', 'Unknown')
                    if target_name not in seen_targets and count < 15:
                        seen_targets.add(target_name)
                        pchembl = act.get('pchembl_value', 'N/A')
                        stype = act.get('standard_type', 'N/A')
                        output_lines.append(f"- {target_name}: pChEMBL = {pchembl} ({stype})")
                        count += 1
            
            output_lines.append("")
    
    return "\n".join(output_lines)
