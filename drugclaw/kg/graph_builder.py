#!/usr/bin/env python3
"""
Knowledge Graph Builder - Build and query drug-target-disease knowledge graph
"""

from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
import json
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class Triple:
    """Subject-Predicate-Object triple for knowledge graph"""
    subject: str
    predicate: str
    object: str
    confidence: float
    source: str
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class Entity:
    """Entity in knowledge graph"""
    name: str
    entity_type: str  # drug, target, disease, pathway, side_effect
    description: Optional[str] = None
    identifiers: Optional[Dict[str, str]] = None  # {"chembl": "CHEMBL123", "drugbank": "DB0000"}

class KnowledgeGraph:
    """Simple in-memory knowledge graph for drug discovery"""
    
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.triples: List[Triple] = []
        # Index for faster queries
        self._outgoing: Dict[str, List[Tuple[str, Triple]]] = defaultdict(list)
        self._incoming: Dict[str, List[Tuple[str, Triple]]] = defaultdict(list)
    
    def add_entity(self, entity: Entity) -> None:
        """Add an entity to the graph"""
        self.entities[entity.name] = entity
    
    def add_triple(self, triple: Triple) -> None:
        """Add a triple to the graph"""
        self.triples.append(triple)
        self._outgoing[triple.subject].append((triple.predicate, triple))
        self._incoming[triple.object].append((triple.predicate, triple))
    
    def get_entity(self, name: str) -> Optional[Entity]:
        """Get entity by name"""
        return self.entities.get(name)
    
    def get_outgoing(self, subject: str) -> List[Triple]:
        """Get all outgoing triples from a subject"""
        if subject not in self._outgoing:
            return []
        return [t for (p, t) in self._outgoing[subject]]
    
    def get_incoming(self, object: str) -> List[Triple]:
        """Get all incoming triples to an object"""
        if object not in self._incoming:
            return []
        return [t for (p, t) in self._incoming[object]]
    
    def find_path(self, start: str, end: str, max_length: int = 3) -> List[List[Triple]]:
        """Find all paths between two entities up to max_length"""
        paths = []
        visited = set()
        
        def dfs(current: str, path: List[Triple], length: int):
            if length > max_length:
                return
            if current == end:
                paths.append(path.copy())
                return
            for (pred, triple) in self._outgoing.get(current, []):
                if triple.object not in visited:
                    visited.add(triple.object)
                    path.append(triple)
                    dfs(triple.object, path, length + 1)
                    path.pop()
                    visited.remove(triple.object)
        
        visited.add(start)
        dfs(start, [], 0)
        return paths
    
    def find_connected_drugs(self, target: str) -> List[Triple]:
        """Find all drugs that target a given target"""
        return [t for t in self.get_incoming(target) 
                if t.predicate in ['targets', 'inhibits', 'binds'] 
                and t.subject in self.entities 
                and self.entities[t.subject].entity_type == 'drug']
    
    def find_targets_of_drug(self, drug: str) -> List[Triple]:
        """Find all targets of a given drug"""
        return [t for t in self.get_outgoing(drug) 
                if t.predicate in ['targets', 'inhibits', 'binds'] 
                and t.object in self.entities 
                and self.entities[t.object].entity_type == 'target']
    
    def export_json(self, path: str) -> None:
        """Export graph to JSON"""
        data = {
            'entities': [e.__dict__ for e in self.entities.values()],
            'triples': [t.__dict__ for t in self.triples]
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @classmethod
    def from_json(cls, path: str) -> 'KnowledgeGraph':
        """Load graph from JSON"""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        kg = cls()
        for entity_data in data['entities']:
            entity = Entity(**entity_data)
            kg.add_entity(entity)
        for triple_data in data['triples']:
            triple = Triple(**triple_data)
            kg.add_triple(triple)
        
        return kg
    
    def stats(self) -> Dict[str, int]:
        """Get graph statistics"""
        entity_types = defaultdict(int)
        for entity in self.entities.values():
            entity_types[entity.entity_type] += 1
        
        return {
            'total_entities': len(self.entities),
            'total_triples': len(self.triples),
            'entity_types': dict(entity_types)
        }
