#!/usr/bin/env python3
"""
Configuration handling for DrugClaw
"""

import os
import json
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class Config:
    """DrugClaw configuration"""
    api_key: str
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4o"
    max_tokens: int = 20000
    timeout: int = 60
    temperature: float = 0.7
    
    @classmethod
    def from_file(cls, key_file: str) -> 'Config':
        """Load configuration from JSON file"""
        with open(key_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls(
            api_key=data.get('api_key'),
            base_url=data.get('base_url', 'https://api.openai.com/v1'),
            model=data.get('model', 'gpt-4o'),
            max_tokens=data.get('max_tokens', 20000),
            timeout=data.get('timeout', 60),
            temperature=data.get('temperature', 0.7)
        )
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Load configuration from environment variables"""
        return cls(
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url=os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1'),
            model=os.getenv('OPENAI_MODEL', 'gpt-4o'),
            max_tokens=int(os.getenv('OPENAI_MAX_TOKENS', '20000')),
            timeout=int(os.getenv('OPENAI_TIMEOUT', '60')),
            temperature=float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
        )
    
    def is_valid(self) -> bool:
        """Check if configuration is valid"""
        return self.api_key is not None and len(self.api_key) > 0
