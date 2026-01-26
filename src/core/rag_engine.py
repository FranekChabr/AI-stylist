# src/core/rag_engine.py
import os
import glob
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
        """Ładuje pliki tekstowe z folderu data/knowledge_base."""
        txt_files = glob.glob(os.path.join(Config.DATA_DIR, "knowledge_base", "*.txt"))
        
        doc_id_counter = 0
        all_sentences = []
        
        for file_path in txt_files:
            filename = os.path.basename(file_path)
            # UTF-8 encoding dla polskich znaków
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
                
                for line in lines:
                    self.documents.append({
                        "id": doc_id_counter,
                        "content": line,
                        "source": filename
                    })
                    all_sentences.append(line)
                    doc_id_counter += 1
        
        if not all_sentences:
            logger.warning("Knowledge base is empty!")
            return

        logger.info(f"Indexing {len(all_sentences)} text chunks...")
        embeddings = self.model.encode(all_sentences)
        
        # Konwersja do float32 (wymagane przez FAISS)
        embeddings = np.array(embeddings).astype('float32')
        self.index.add(embeddings)
        logger.info("RAG Index created successfully.")

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