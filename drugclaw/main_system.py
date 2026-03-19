#!/usr/bin/env python3
"""
DrugClaw main system - Entry point for queries
"""

from typing import List, Dict, Optional, Any, Tuple
import json
import logging
import os
from openai import OpenAI

from .agent.planner import PlannerAgent, QueryAnalysis
from .agent.code_agent import CodeAgent
from .agent.responder import Responder, Evidence, SynthesizedAnswer
from .config import Config

logger = logging.getLogger(__name__)

class DrugClawSystem:
    """Main DrugClaw system"""
    
    def __init__(self, config: Config, skills_root: str = "skills"):
        self.config = config
        self.planner = PlannerAgent()
        self.code_agent = CodeAgent(skills_root=skills_root)
        self.responder = Responder()
        self.skills_root = skills_root
        
        # Initialize OpenAI client
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=config.timeout
        )
    
    def get_available_skills(self) -> Dict[str, List[str]]:
        """Get all available skills organized by category"""
        skills = {}
        
        for category in os.listdir(self.skills_root):
            category_path = os.path.join(self.skills_root, category)
            if os.path.isdir(category_path) and not category.startswith('__'):
                category_skills = []
                for skill in os.listdir(category_path):
                    skill_path = os.path.join(category_path, skill)
                    if os.path.isdir(skill_path):
                        category_skills.append(skill)
                if category_skills:
                    skills[category] = category_skills
        
        return skills
    
    def query(self, query_text: str, 
              thinking_mode: str = None, 
              resource_filter: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Main entrypoint for queries
        
        Args:
            query_text: User query
            thinking_mode: 'simple', 'graph', or 'web_only' (auto-detected if None)
            resource_filter: Optional list of specific resources to use
        
        Returns:
            Dict with answer and metadata
        """
        # Step 1: Plan the query
        analysis = self.planner.analyze(query_text)
        
        # Override thinking mode if specified
        if thinking_mode is not None:
            analysis.thinking_mode = thinking_mode
        
        logger.info(f"Query analyzed: mode={analysis.thinking_mode}, categories={analysis.selected_categories}")
        
        # Step 2: Get all available skills and filter
        available_skills = self.get_available_skills()
        selected_skills = []
        
        for category in analysis.selected_categories:
            if category in available_skills:
                for skill in available_skills[category]:
                    if resource_filter is None or skill in resource_filter or category in resource_filter:
                        selected_skills.append((category, skill))
        
        analysis.selected_skills = selected_skills
        logger.info(f"Selected {len(selected_skills)} skills")
        
        # Step 3: Retrieve evidence from each selected skill
        evidences = self._retrieve_evidences(analysis, selected_skills)
        
        # Step 4: Synthesize answer
        if analysis.thinking_mode == 'graph':
            result = self.responder.synthesize_graph(query_text, evidences)
        else:
            result = self.responder.synthesize_simple(query_text, evidences)
        
        # Step 5: Handle web search if needed
        if analysis.requires_web_search and analysis.thinking_mode != 'web_only':
            # TODO: Add web search fallback
            pass
        
        return {
            'answer': result.answer,
            'evidence_count': result.evidence_count,
            'sources': result.sources,
            'claims': result.claims,
            'analysis': {
                'entities': analysis.entities,
                'entity_types': analysis.entity_types,
                'selected_categories': analysis.selected_categories,
                'thinking_mode': analysis.thinking_mode
            }
        }
    
    def _retrieve_evidences(self, analysis: QueryAnalysis, 
                          selected_skills: List[Tuple[str, str]]) -> List[Evidence]:
        """Retrieve evidence from all selected skills"""
        evidences = []
        
        for category, skill in selected_skills:
            evidence = self._retrieve_from_skill(category, skill, analysis.entities)
            if evidence:
                evidences.append(evidence)
        
        return evidences
    
    def _retrieve_from_skill(self, category: str, skill: str, 
                           entities: List[str]) -> Optional[Evidence]:
        """Retrieve evidence from a single skill with fallback"""
        
        # First try: deterministic retrieve.py
        if self.code_agent.has_retrieve_script(category, skill):
            content = self.code_agent.execute_retrieve_script(category, skill, entities)
            if content is not None and content.strip():
                claims = self.responder.extract_claims(content, f"{category}/{skill}")
                return Evidence(
                    source=f"{category}/{skill}",
                    content=content.strip(),
                    confidence=0.9,  # Deterministic script has high confidence
                    entities=entities,
                    claims=claims
                )
        
        # Second try: code generation via LLM (vibe coding)
        docs, example = self.code_agent.read_skill_docs(category, skill)
        
        if docs or example:
            prompt = self._build_code_generation_prompt(
                category, skill, docs, example, entities
            )
            
            try:
                response = self.client.chat.completions.create(
                    model=self.config.model,
                    messages=[
                        {"role": "system", "content": "You are a code generation assistant for DrugClaw. Write a Python script to retrieve the requested information from this data source. Follow the example exactly. Only output the complete runnable Python code."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens
                )
                
                code = response.choices[0].message.content
                # Clean up markdown code blocks
                code = code.replace('```python', '').replace('```', '').strip()
                
                content, error = self.code_agent.execute_generated_code(code)
                if content is not None and content.strip():
                    claims = self.responder.extract_claims(content, f"{category}/{skill}")
                    return Evidence(
                        source=f"{category}/{skill} (generated)",
                        content=content.strip(),
                        confidence=0.7,  # Generated code has lower confidence
                        entities=entities,
                        claims=claims
                    )
                else:
                    logger.warning(f"Generated code failed: {error}")
            except Exception as e:
                logger.error(f"LLM code generation failed: {str(e)}")
        
        # Third try: load skill module and use skill.retrieve()
        module = self.code_agent.load_skill_module(category, skill)
        if module and hasattr(module, 'retrieve'):
            try:
                content = module.retrieve(entities)
                if content:
                    claims = self.responder.extract_claims(str(content), f"{category}/{skill}")
                    return Evidence(
                        source=f"{category}/{skill}",
                        content=str(content),
                        confidence=0.8,
                        entities=entities,
                        claims=claims
                    )
            except Exception as e:
                logger.error(f"Skill module retrieve failed: {str(e)}")
        
        logger.warning(f"No evidence retrieved from {category}/{skill}")
        return None
    
    def _build_code_generation_prompt(self, category: str, skill: str, 
                                     docs: str, example: str, 
                                     entities: List[str]) -> str:
        """Build prompt for code generation"""
        prompt = f"""Category: {category}
Skill: {skill}

Documentation:
{docs[:2000]}  # Truncate to avoid token overflow

Example code:
{example}

Retrieve information for these entities: {', '.join(entities)}

Write a complete Python script that retrieves and prints the information. Follow the example pattern exactly. Print the output in human-readable format.
"""
        return prompt
