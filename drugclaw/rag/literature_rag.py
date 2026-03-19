#!/usr/bin/env python3
"""
Literature RAG - Private and public literature knowledge base retrieval
Supports:
- PDF ingestion and embedding
- Vector search over private literature
- Hybrid retrieval: public database + private RAG
"""

from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
import os
import re
import logging
from pathlib import Path

from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI

logger = logging.getLogger(__name__)

@dataclass
class RetrievedDocument:
    """Retrieved document from RAG"""
    content: str
    metadata: Dict[str, Any]
    score: float
    source: str  # "private" or "public"

class LiteratureRAG:
    """Literature RAG system for private and public literature"""
    
    def __init__(self, 
                 db_path: str = "./data/chroma_db",
                 embedding_model: str = "BAAI/bge-base-en-v1.5",
                 openai_api_key: Optional[str] = None,
                 openai_base_url: Optional[str] = None,
                 openai_model: str = "gpt-4o"):
        """
        Initialize Literature RAG
        
        Args:
            db_path: Path to ChromaDB persistent storage
            embedding_model: HuggingFace embedding model name
            openai_api_key: OpenAI API key for LLM
        """
        self.db_path = db_path
        self.embedding_model = embedding_model
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'}
        )
        
        # Initialize or load vector store
        if os.path.exists(db_path) and len(os.listdir(db_path)) > 0:
            self.vector_store = Chroma(
                persist_directory=db_path,
                embedding_function=self.embeddings
            )
        else:
            self.vector_store = Chroma(
                persist_directory=db_path,
                embedding_function=self.embeddings
            )
        
        # Initialize LLM if API key available
        if openai_api_key:
            self.llm = OpenAI(
                api_key=openai_api_key,
                base_url=openai_base_url,
                model_name=openai_model,
                temperature=0
            )
        else:
            self.llm = None
    
    def ingest_pdf(self, pdf_path: str, metadata: Optional[Dict] = None) -> int:
        """
        Ingest a single PDF file into RAG
        
        Args:
            pdf_path: Path to PDF file
            metadata: Additional metadata (title, authors, year, etc.)
        
        Returns:
            Number of chunks ingested
        """
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return 0
        
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        
        # Add metadata
        if metadata:
            for doc in documents:
                doc.metadata.update(metadata)
        
        doc = documents[0]
        if 'source' not in doc.metadata:
            doc.metadata['source'] = os.path.basename(pdf_path)
        doc.metadata['file_type'] = 'pdf'
        
        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_documents(documents)
        
        # Add to vector store
        self.vector_store.add_documents(chunks)
        self.vector_store.persist()
        
        logger.info(f"Ingested {len(chunks)} chunks from {pdf_path}")
        return len(chunks)
    
    def ingest_directory(self, dir_path: str, glob_pattern: str = "*.pdf") -> int:
        """
        Ingest all PDF files in a directory
        
        Args:
            dir_path: Directory containing PDF files
            glob_pattern: File pattern to match
        
        Returns:
            Total number of chunks ingested
        """
        total_chunks = 0
        dir_path = Path(dir_path)
        
        for pdf_file in dir_path.glob(glob_pattern):
            metadata = {
                'filename': pdf_file.name,
                'directory': str(dir_path)
            }
            chunks = self.ingest_pdf(str(pdf_file), metadata)
            total_chunks += chunks
        
        return total_chunks
    
    def search(self, query: str, top_k: int = 5) -> List[RetrievedDocument]:
        """
        Similarity search for documents
        
        Args:
            query: Search query
            top_k: Number of top results to return
        
        Returns:
            List of retrieved documents
        """
        if self.vector_store._collection.count() == 0:
            logger.warning("Vector store is empty, no documents to search")
            return []
        
        results = self.vector_store.similarity_search_with_score(query, k=top_k)
        
        retrieved = []
        for doc, score in results:
            retrieved.append(RetrievedDocument(
                content=doc.page_content,
                metadata=doc.metadata,
                score=score,
                source=doc.metadata.get('source', 'unknown')
            ))
        
        return retrieved
    
    def query(self, question: str, top_k: int = 5) -> Dict[str, Any]:
        """
        End-to-end question answering over RAG
        
        Args:
            question: User question
            top_k: Number of documents to retrieve
        
        Returns:
            Answer with retrieved context
        """
        if self.llm is None:
            logger.error("LLM not initialized, cannot answer question")
            return {
                'answer': "Error: LLM not configured. Please provide OpenAI API key.",
                'retrieved': self.search(question, top_k)
            }
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(search_kwargs={'k': top_k})
        )
        
        answer = qa_chain.run(question)
        retrieved = self.search(question, top_k)
        
        return {
            'answer': answer,
            'retrieved': [
                {
                    'content': r.content,
                    'metadata': r.metadata,
                    'score': r.score,
                    'source': r.source
                } for r in retrieved
            ]
        }
    
    def delete_document(self, source: str) -> bool:
        """Delete a document from vector store by source"""
        # Chroma doesn't support direct deletion by metadata easily
        # This is a simplified implementation
        try:
            self.vector_store.delete(filter={'source': source})
            self.vector_store.persist()
            logger.info(f"Deleted document: {source}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the RAG collection"""
        return {
            'total_documents': self.vector_store._collection.count(),
            'db_path': self.db_path,
            'embedding_model': self.embedding_model
        }
