#!/usr/bin/env python3
"""
Build knowledge graph from downloaded ChEMBL data

Usage:
    python scripts/build_chembl_kg.py --input ./data/chembl_drugs/chembl_34_chemreps.txt --output ./data/chembl_kg.json
"""

import argparse
import pandas as pd
from pathlib import Path
from drugclaw.kg.graph_builder import KnowledgeGraph, Entity, Triple

def main():
    parser = argparse.ArgumentParser(
        description='Build knowledge graph from ChEMBL data'
    )
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Input chembl_*_chemreps.txt file'
    )
    parser.add_argument(
        '--output', '-o',
        required=True,
        help='Output JSON file for knowledge graph'
    )
    parser.add_argument(
        '--max-compounds', '-m',
        type=int,
        default=1000,
        help='Maximum number of compounds to process (for testing)'
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        print(f"Error: input file {input_path} does not exist")
        print("Hint: Run python scripts/download_public_datasets.py --dataset chembl_drugs first")
        exit(1)
    
    print(f"Reading ChEMBL data from {input_path}...")
    print(f"This may take a few minutes for the full file...")
    
    # Read ChEMBL chemrep file
    # Format: chembl_id,standard_inchi_key,canonical_smiles,standard_inchi
    df = pd.read_csv(input_path, sep='\t', nrows=args.max_compounds)
    print(f"Loaded {len(df)} compounds")
    
    kg = KnowledgeGraph()
    
    # Add compounds as entities
    for idx, row in df.iterrows():
        chembl_id = row['chembl_id']
        smiles = row['canonical_smiles']
        
        kg.add_entity(Entity(
            name=chembl_id,
            entity_type='drug',
            description=f"Compound with SMILES: {smiles[:100]}",
            identifiers={'chembl': chembl_id, 'smiles': smiles}
        ))
    
    stats = kg.stats()
    kg.export_json(output_path)
    
    print(f"✅ Knowledge graph built:")
    print(f"   Output: {output_path}")
    print(f"   Entities: {stats['total_entities']}")
    print(f"   Triples: {stats['total_triples']}")

if __name__ == '__main__':
    main()
