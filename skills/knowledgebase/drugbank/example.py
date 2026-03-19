#!/usr/bin/env python3
"""
Example: Get drug information from DrugBank
"""

import json
import os

def get_drug_info(drug_name, drugbank_xml_path=None):
    """
    Get drug information from DrugBank
    
    Note: Full DrugBank requires download from https://go.drugbank.com/
    This example shows the expected output structure.
    """
    # In a real implementation, you'd parse the DrugBank XML
    # For demonstration, return structure
    return {
        'drugbank_id': 'DB00619',
        'name': 'Imatinib',
        'description': 'Imatinib is a tyrosine kinase inhibitor used for the treatment of multiple cancers...',
        'mechanism': 'Imatinib acts by inhibiting the BCR-ABL tyrosine kinase...',
        'targets': [
            {
                'id': 'P00519',
                'name': 'Abelson tyrosine-protein kinase 1',
                'gene_name': 'ABL1',
                'action': 'inhibitor'
            }
        ],
        'interactions': [
            {
                'drug_id': 'DB01051',
                'name': 'Warfarin',
                'description': 'Increased bleeding risk'
            }
        ]
    }

if __name__ == "__main__":
    info = get_drug_info("imatinib")
    print(json.dumps(info, indent=2))
