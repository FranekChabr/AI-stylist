import warnings
import logging
import src.tools.definitions

# --- BLOKOWANIE WARNINGÓW ---
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", module="google.auth")
# -----------------------------

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.core.llm_engine import LLMEngine
from src.utils.logger import logger
from src.config import Config
from src.core.llm_engine import LLMEngine, LocalLLMStub

app = FastAPI(
    title="AI Stylist API",
    description="Agent doradzający ubiór z RAG i Function Calling (Gemini)",
    version="1.0.0"
)

# Konfiguracja CORS - pozwól na zapytania z frontendu
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # W produkcji zmień na konkretny adres frontendu
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model zapytania
class AskRequest(BaseModel):
    query: str

# Inicjalizacja silnika (Lazy loading)
llm_engine = None

@app.on_event("startup")
async def startup_event():
    global llm_engine
    logger.info("Starting up API...")
    try:
        if Config.LLM_PROVIDER == "local_stub":
            logger.info("Using LOCAL STUB Engine (Offline mode)")
            llm_engine = LocalLLMStub()
        else:
            logger.info(f"Using Google Gemini Engine (Model: {Config.GEMINI_MODEL})")
            llm_engine = LLMEngine()
            
        logger.info("LLM Engine initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize LLM Engine: {e}")

@app.post("/ask")
async def ask_endpoint(request: AskRequest):
    """
    Główny endpoint do rozmowy z agentem.
    """
    if not llm_engine:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        response_text = llm_engine.process_query(request.query)
        return {
            "query": request.query,
            "response": response_text,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Instrukcja uruchomienia (jeśli plik jest uruchamiany bezpośrednio)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)