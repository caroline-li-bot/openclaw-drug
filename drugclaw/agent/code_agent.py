#!/usr/bin/env python3
"""
Code Agent - Reads skill documentation, writes and executes query code
"""

from typing import List, Dict, Optional, Any, Tuple
import os
import sys
import subprocess
import tempfile
import logging
import importlib.util

logger = logging.getLogger(__name__)

class CodeAgent:
    """Code generation agent that executes resource-specific retrieval"""
    
    def __init__(self, skills_root: str = "skills"):
        self.skills_root = skills_root
    
    def get_skill_path(self, category: str, skill_name: str) -> str:
        """Get path to skill directory"""
        return os.path.join(self.skills_root, category, skill_name)
    
    def read_skill_docs(self, category: str, skill_name: str) -> Tuple[str, str]:
        """Read SKILL.md and example.py from a skill"""
        skill_path = self.get_skill_path(category, skill_name)
        
        skill_md = os.path.join(skill_path, "SKILL.md")
        example_py = os.path.join(skill_path, "example.py")
        
        docs = ""
        example = ""
        
        if os.path.exists(skill_md):
            with open(skill_md, 'r', encoding='utf-8') as f:
                docs = f.read()
        
        if os.path.exists(example_py):
            with open(example_py, 'r', encoding='utf-8') as f:
                example = f.read()
        
        return docs, example
    
    def has_retrieve_script(self, category: str, skill_name: str) -> bool:
        """Check if deterministic retrieve.py exists"""
        retrieve_path = os.path.join(self.skills_root, category, skill_name, "retrieve.py")
        return os.path.exists(retrieve_path)
    
    def execute_retrieve_script(self, category: str, skill_name: str, entities: List[str]) -> Optional[str]:
        """Execute pre-written deterministic retrieve.py"""
        retrieve_path = os.path.join(self.skills_root, category, skill_name, "retrieve.py")
        
        if not os.path.exists(retrieve_path):
            return None
        
        try:
            cmd = [sys.executable, retrieve_path] + entities
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                return result.stdout
            else:
                logger.warning(f"retrieve.py failed: {result.stderr}")
                return None
        except Exception as e:
            logger.error(f"Exception running retrieve.py: {str(e)}")
            return None
    
    def generate_and_execute(self, category: str, skill_name: str, entities: List[str], query: str) -> Optional[str]:
        """Generate custom code using LLM and execute it
        
        Note: This requires an LLM to be available. The calling code should handle
        the actual prompt completion. Here we just manage the file and execution.
        """
        # This method is called by the main system after the LLM generates the code
        # It handles writing the temp file and executing
        skill_path = self.get_skill_path(category, skill_name)
        docs, example = self.read_skill_docs(category, skill_name)
        
        # The actual code generation happens in the main system
        # This just provides the context for the LLM prompt
        
        return None
    
    def execute_generated_code(self, code: str) -> Tuple[Optional[str], Optional[str]]:
        """Execute generated code in a temporary file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name
        
        try:
            result = subprocess.run([sys.executable, temp_path], 
                                  capture_output=True, text=True, timeout=180)
            os.unlink(temp_path)
            
            if result.returncode == 0:
                return result.stdout, None
            else:
                return None, result.stderr
        except Exception as e:
            os.unlink(temp_path)
            return None, str(e)
    
    def load_skill_module(self, category: str, skill_name: str):
        """Dynamically load a skill module"""
        skill_path = self.get_skill_path(category, skill_name)
        module_path = os.path.join(skill_path, f"{skill_name}_skill.py")
        
        if not os.path.exists(module_path):
            return None
        
        try:
            spec = importlib.util.spec_from_file_location(
                f"{category}_{skill_name}_skill", module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            logger.error(f"Failed to load skill module: {str(e)}")
            return None
