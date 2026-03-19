#!/usr/bin/env python3
"""
Graph Reasoner - Reason over knowledge graph to find connections
"""

from typing import List, Dict, Optional, Any, Tuple
import logging
from collections import defaultdict

from .graph_builder import KnowledgeGraph, Triple, Entity

logger = logging.getLogger(__name__)

class GraphReasoner:
    """Reason over drug discovery knowledge graph"""
    
    def __init__(self, kg: KnowledgeGraph):
        self.kg = kg
    
    def find_second_order_connections(self, drug: str) -> Dict[str, Any]:
        """
        Find drug -> target -> pathway connections
        """
        result = {
            'drug': drug,
            'direct_targets': [],
            'pathways': [],
            'downstream_effects': []
        }
        
        # Get direct targets
        targets = self.kg.find_targets_of_drug(drug)
        for target_triple in targets:
            target_name = target_triple.object
            target_entity = self.kg.get_entity(target_name)
            result['direct_targets'].append({
                'target': target_name,
                'predicate': target_triple.predicate,
                'confidence': target_triple.confidence,
                'source': target_triple.source,
                'description': target_entity.description if target_entity else None
            })
            
            # Find pathways connected to this target
            pathway_triples = self.kg.get_outgoing(target_name)
            for pathway_triple in pathway_triples:
                if pathway_triple.predicate in ['participates_in', 'activates', 'inhibits']:
                    result['pathways'].append({
                        'from_target': target_name,
                        'pathway': pathway_triple.object,
                        'predicate': pathway_triple.predicate
                    })
        
        return result
    
    def find_repurposing_opportunities(self, disease: str, max_distance: int = 3) -> List[Dict[str, Any]]:
        """
        Find approved drugs that can potentially be repurposed for a disease
        by looking for paths drug -> target -> ... -> disease
        """
        opportunities = []
        
        # Find all drugs in the graph
        drugs = [e for e in self.kg.entities.values() if e.entity_type == 'drug']
        
        for drug in drugs:
            paths = self.kg.find_path(drug.name, disease, max_length=max_distance)
            if paths:
                # Score paths by average confidence
                total_conf = sum(t.confidence for path in paths for t in path)
                avg_conf = total_conf / sum(len(path) for path in paths)
                
                opportunities.append({
                    'drug': drug.name,
                    'drug_description': drug.description,
                    'number_of_paths': len(paths),
                    'average_confidence': avg_conf,
                    'paths': [
                        [(t.subject, t.predicate, t.object) for t in path]
                        for path in paths
                    ]
                })
        
        # Sort by confidence
        opportunities.sort(key=lambda x: x['average_confidence'], reverse=True)
        return opportunities
    
    def find_interactions(self, drug1: str, drug2: str) -> Dict[str, Any]:
        """
        Find potential interactions between two drugs via shared targets or pathways
        """
        result = {
            'has_interaction': False,
            'direct_ddi': None,
            'shared_targets': [],
            'shared_pathways': [],
            'confidence': 0.0
        }
        
        # Check for direct DDI
        outgoing1 = self.kg.get_outgoing(drug1)
        for triple in outgoing1:
            if triple.predicate == 'interacts_with' and triple.object == drug2:
                result['has_interaction'] = True
                result['direct_ddi'] = {
                    'description': triple.metadata.get('description') if triple.metadata else None,
                    'severity': triple.metadata.get('severity') if triple.metadata else 'unknown',
                    'source': triple.source
                }
                result['confidence'] = triple.confidence
                return result
        
        # Check shared targets
        targets1 = set(t.object for t in self.kg.find_targets_of_drug(drug1))
        targets2 = set(t.object for t in self.kg.find_targets_of_drug(drug2))
        shared_targets = targets1.intersection(targets2)
        
        for target in shared_targets:
            target_entity = self.kg.get_entity(target)
            result['shared_targets'].append({
                'target': target,
                'description': target_entity.description if target_entity else None
            })
        
        # Check shared pathways
        pathways1 = set()
        for target in targets1:
            for triple in self.kg.get_outgoing(target):
                if triple.predicate in ['participates_in', 'activates']:
                    pathways1.add(triple.object)
        
        pathways2 = set()
        for target in targets2:
            for triple in self.kg.get_outgoing(target):
                if triple.predicate in ['participates_in', 'activates']:
                    pathways2.add(triple.object)
        
        shared_pathways = pathways1.intersection(pathways2)
        for pathway in shared_pathways:
            result['shared_pathways'].append(pathway)
        
        if result['shared_targets'] or result['shared_pathways']:
            result['has_interaction'] = True
            # Lower confidence than direct DDI
            result['confidence'] = 0.5 if result['shared_targets'] else 0.3
        
        return result
    
    def summarize_entity(self, name: str) -> Dict[str, Any]:
        """
        Generate a comprehensive summary of an entity from the graph
        """
        entity = self.kg.get_entity(name)
        if not entity:
            return {'found': False}
        
        summary = {
            'found': True,
            'name': name,
            'entity_type': entity.entity_type,
            'description': entity.description,
            'identifiers': entity.identifiers,
            'outgoing_relations': defaultdict(list),
            'incoming_relations': defaultdict(list)
        }
        
        # Group outgoing relations by predicate
        for triple in self.kg.get_outgoing(name):
            summary['outgoing_relations'][triple.predicate].append({
                'object': triple.object,
                'confidence': triple.confidence,
                'source': triple.source
            })
        
        # Group incoming relations by predicate
        for triple in self.kg.get_incoming(name):
            summary['incoming_relations'][triple.predicate].append({
                'subject': triple.subject,
                'confidence': triple.confidence,
                'source': triple.source
            })
        
        return summary
    
    def rank_centrality(self, entity_type: str = 'drug') -> List[Tuple[str, int]]:
        """
        Rank entities by degree centrality (number of connections)
        """
        degrees = []
        for entity in self.kg.entities.values():
            if entity.entity_type == entity_type:
                degree = len(self.kg.get_outgoing(entity.name)) + len(self.kg.get_incoming(entity.name))
                degrees.append((entity.name, degree))
        
        degrees.sort(key=lambda x: x[1], reverse=True)
        return degrees
