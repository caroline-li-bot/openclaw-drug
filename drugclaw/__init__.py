#!/usr/bin/env python3
"""
DrugClaw - AI-powered drug discovery assistant based on OpenClaw
"""

__version__ = "0.2.0"
__author__ = "DrugClaw Contributors"

from .main_system import DrugClawSystem
from .config import Config
from .rag.literature_rag import LiteratureRAG, RetrievedDocument
from .kg.graph_builder import KnowledgeGraph, Triple, Entity
