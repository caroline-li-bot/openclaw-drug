#!/usr/bin/env python3
"""
Import PDF files from a directory into DrugClaw Literature RAG

Usage:
    python scripts/import_pdfs_to_rag.py --input-dir ./pdfs --db-path ./data/chroma_db
"""

import argparse
import os
from pathlib import Path
from typing import Optional

from drugclaw.rag.literature_rag import LiteratureRAG
from drugclaw.config import Config

def main():
    parser = argparse.ArgumentParser(
        description='Import PDF files into DrugClaw Literature RAG'
    )
    parser.add_argument(
        '--input-dir', '-i',
        required=True,
        help='Directory containing PDF files to import'
    )
    parser.add_argument(
        '--db-path', '-d',
        default='./data/chroma_db',
        help='Path to ChromaDB persistent storage'
    )
    parser.add_argument(
        '--embedding-model', '-m',
        default='BAAI/bge-base-en-v1.5',
        help='HuggingFace embedding model name'
    )
    
    args = parser.parse_args()
    
    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        print(f"Error: directory {input_dir} does not exist")
        exit(1)
    
    print(f"Initializing RAG with embedding model: {args.embedding_model}")
    rag = LiteratureRAG(
        db_path=args.db_path,
        embedding_model=args.embedding_model
    )
    
    print(f"Ingesting PDFs from {input_dir}")
    total_chunks = rag.ingest_directory(input_dir, "*.pdf")
    
    print(f"✅ Done! Ingested {total_chunks} chunks")
    stats = rag.get_statistics()
    print(f"Total documents in RAG: {stats['total_documents']}")

if __name__ == '__main__':
    main()
