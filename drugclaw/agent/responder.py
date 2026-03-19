#!/usr/bin/env python3
"""
Responder - Synthesizes retrieved evidence into final answer
"""

from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class Evidence:
    """A piece of evidence from a skill"""
    source: str
    content: str
    confidence: float
    entities: List[str]
    claims: List[Dict[str, str]]

@dataclass
class SynthesizedAnswer:
    """Final synthesized answer"""
    answer: str
    evidence_count: int
    sources: List[str]
    claims: List[Dict[str, Any]]
    requires_followup: bool

class Responder:
    """Synthesizes multiple evidence pieces into coherent answer"""
    
    def __init__(self):
        pass
    
    def synthesize_simple(self, query: str, evidences: List[Evidence]) -> SynthesizedAnswer:
        """Simple mode: direct answer from retrieved evidence"""
        
        sources = []
        all_claims = []
        content_blocks = []
        
        for evidence in evidences:
            sources.append(evidence.source)
            content_blocks.append(f"--- From {evidence.source} ---\n{evidence.content}")
            all_claims.extend(evidence.claims)
        
        # In simple mode, we just combine the evidence
        combined_content = "\n\n".join(content_blocks)
        
        answer = f"# Answer: {query}\n\n{combined_content}\n\n*Found {len(evidences)} evidence pieces from {len(sources)} sources.*"
        
        return SynthesizedAnswer(
            answer=answer,
            evidence_count=len(evidences),
            sources=sources,
            claims=all_claims,
            requires_followup=False
        )
    
    def synthesize_graph(self, query: str, evidences: List[Evidence], 
                       graph_builder_output: Optional[Dict] = None) -> SynthesizedAnswer:
        """Graph mode: build a knowledge graph from evidence and synthesize answer"""
        
        sources = []
        all_claims = []
        triples = []
        
        for evidence in evidences:
            sources.append(evidence.source)
            all_claims.extend(evidence.claims)
            
            if graph_builder_output and 'triples' in graph_builder_output:
                triples.extend(graph_builder_output['triples'])
        
        # Build structured answer
        answer_parts = [f"# {query}"]
        
        # Add summary of findings
        if triples:
            answer_parts.append("\n## Key Relationships")
            for triple in triples:
                s, p, o = triple.get('subject', ''), triple.get('predicate', ''), triple.get('object', '')
                answer_parts.append(f"- **{s}** {p} **{o}**")
        
        # Add detailed evidence
        answer_parts.append("\n## Detailed Evidence")
        for evidence in evidences:
            answer_parts.append(f"\n### {evidence.source}")
            answer_parts.append(evidence.content.strip())
        
        answer_parts.append(f"\n\n*Total: {len(evidences)} evidence pieces, {len(triples)} relationships extracted.*")
        
        return SynthesizedAnswer(
            answer="\n".join(answer_parts),
            evidence_count=len(evidences),
            sources=sources,
            claims=all_claims,
            requires_followup=len(all_claims) == 0
        )
    
    def extract_claims(self, evidence_text: str, source: str) -> List[Dict[str, Any]]:
        """Extract structured claims from evidence text"""
        # This is simplified - in a full implementation, you'd use LLM
        # to extract (subject, predicate, object) triples
        claims = []
        
        lines = evidence_text.split('\n')
        for line in lines:
            line = line.strip()
            if line and (':' in line or ' - ' in line):
                claims.append({
                    'source': source,
                    'content': line
                })
        
        return claims
