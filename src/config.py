# src/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # Settings
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "local_stub")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # fallback na 'gemini-pro', jeśli w env nic nie ma
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-pro")
    
    # RAG Settings
    RAG_K_RETRIEVAL = int(os.getenv("RAG_K_RETRIEVAL", 3))
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    # Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    VECTOR_STORE_PATH = os.path.join(DATA_DIR, "vector_store")