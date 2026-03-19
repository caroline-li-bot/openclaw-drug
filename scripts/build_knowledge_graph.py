#!/usr/bin/env python3
"""
Build knowledge graph from CSV/TSV drug-target interaction data

Usage:
    python scripts/build_knowledge_graph.py --input dti.csv --output kg.json
"""

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, List, Optional

from drugclaw.kg.graph_builder import KnowledgeGraph, Entity, Triple

def guess_entity_type(name: str) -> str:
    """Heuristically guess entity type based on context"""
    # This is simplified - in a full pipeline you'd use NER
    if name.lower() in ['inhibitor', 'activator', 'antagonist', 'agonist']:
        return 'predicate'
    if any(suffix in name.lower() for suffix in ['kinase', 'receptor', 'protein', 'gene']):
        return 'target'
    if any(suffix in name.lower() for suffix in ['cancer', 'disease', 'syndrome', 'disorder']):
        return 'disease'
    return 'drug'

def main():
    parser = argparse.ArgumentParser(
        description='Build knowledge graph from DTI CSV'
    )
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Input CSV file with columns: drug, predicate, target[, confidence]'
    )
    parser.add_argument(
        '--output', '-o',
        required=True,
        help='Output JSON file for knowledge graph'
    )
    parser.add_argument(
        '--header',
        action='store_true',
        help='Input CSV has header'
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        print(f"Error: input file {input_path} does not exist")
        exit(1)
    
    kg = KnowledgeGraph()
    entity_count = 0
    triple_count = 0
    
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
        
        if args.header and len(rows) > 0:
            rows = rows[1:]
        
        for row in rows:
            if len(row) < 3:
                continue
            
            drug = row[0].strip()
            predicate = row[1].strip()
            target = row[2].strip()
            confidence = float(row[3]) if len(row) >= 4 else 0.8
            
            # Add entities
            if not kg.get_entity(drug):
                etype = guess_entity_type(drug)
                kg.add_entity(Entity(name=drug, entity_type=etype))
                entity_count += 1
            
            if not kg.get_entity(target):
                etype = guess_entity_type(target)
                kg.add_entity(Entity(name=target, entity_type=etype))
                entity_count += 1
            
            # Add triple
            kg.add_triple(Triple(
                subject=drug,
                predicate=predicate,
                object=target,
                confidence=confidence,
                source=input_path.name
            ))
            triple_count += 1
    
    kg.export_json(output_path)
    stats = kg.stats()
    
    print(f"✅ Knowledge graph built and saved to {output_path}")
    print(f"   Entities: {stats['total_entities']}")
    print(f"   Triples: {stats['total_triples']}")
    print(f"   Entity types: {stats['entity_types']}")

if __name__ == '__main__':
    main()
