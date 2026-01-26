# src/core/rag_engine.py
import os
import pickle
from typing import List, Dict
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from src.config import Config
from src.utils.logger import logger

class RagEngine:
    def __init__(self):
        # Ładowanie modelu embeddingów
        logger.info("Loading embedding model...")
        self.model = SentenceTransformer(Config.EMBEDDING_MODEL)
        
        # Wymiar wektora dla all-MiniLM-L6-v2 to 384
        self.dimension = 384 
        self.index = faiss.IndexFlatL2(self.dimension)
        
        self.documents: List[Dict] = []
        self._load_knowledge_base()

    def _load_knowledge_base(self):
        """Ładuje indeks FAISS i metadane z folderu data/vector_store."""
        index_path = os.path.join(Config.VECTOR_STORE_PATH, "index.faiss")
        meta_path = os.path.join(Config.VECTOR_STORE_PATH, "index.pkl")

        if not os.path.exists(index_path) or not os.path.exists(meta_path):
             logger.warning(f"RAG Index not found at {Config.VECTOR_STORE_PATH}. Initializing empty index.")
             return

        try:
            self.index = faiss.read_index(index_path)
            with open(meta_path, "rb") as f:
                self.documents = pickle.load(f)
            logger.info(f"Loaded RAG index with {self.index.ntotal} vectors.")
        except Exception as e:
             logger.error(f"Failed to load RAG index: {e}")

    def search(self, query: str, k: int = 3) -> List[Dict]:
        """
        Wyszukuje k najbardziej podobnych fragmentów.
        """
        if self.index.ntotal == 0:
            return []

        query_vector = self.model.encode([query]).astype('float32')
        distances, indices = self.index.search(query_vector, k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx == -1: continue
            
            doc = self.documents[idx]
            results.append({
                "content": doc["content"],
                "source": doc["source"],
                "score": float(distances[0][i])
            })
            
        return results

rag_engine = None

def get_rag_engine():
    global rag_engine
    if rag_engine is None:
        rag_engine = RagEngine()
    return rag_engine