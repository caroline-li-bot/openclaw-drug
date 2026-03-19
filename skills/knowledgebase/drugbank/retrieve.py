#!/usr/bin/env python3
"""
Deterministic retrieval from DrugBank local database
Usage: python retrieve.py drug-name [drug-name ...]
"""

import sys
import json
import os

def retrieve_entities(entities, resources_metadata_path="resources_metadata/drugbank/"):
    """Retrieve information for a list of entities"""
    for entity in entities:
        print(f"\n=== DrugBank Information for: {entity}")
        
        # Check for cached JSON
        json_path = os.path.join(resources_metadata_path, f"{entity.lower()}.json")
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                data = json.load(f)
            print_drug_info(data)
        else:
            print(f"No cached DrugBank entry found for '{entity}'")
            print("You can download the full DrugBank database from https://go.drugbank.com/")

def print_drug_info(data):
    """Print formatted drug information"""
    print(f"**DrugBank ID**: {data.get('drugbank_id', 'N/A')}")
    print(f"**Name**: {data.get('name', 'N/A')}")
    print()
    print(f"**Description**: {data.get('description', 'N/A')[:500]}...")
    print()
    if data.get('mechanisms_of_action'):
        print("**Mechanism of Action**:")
        for moa in data.get('mechanisms_of_action', [])[:5]:
            print(f"  - {moa}")
        print()
    if data.get('targets'):
        print("**Targets**:")
        for target in data.get('targets', [])[:10]:
            name = target.get('name', 'Unknown')
            action = target.get('action', 'N/A')
            print(f"  - {name} ({action})")
        print()
    if data.get('drug_interactions'):
        print(f"**Known Drug Interactions**: {len(data.get('drug_interactions', []))} found")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python retrieve.py <drug-name> [...]")
        sys.exit(1)
    
    entities = sys.argv[1:]
    retrieve_entities(entities)
