from src.core.rag_engine import get_rag_engine

def verify_rag():
    rag = get_rag_engine()
    
    queries = [
        "len na lato",
        "ile kolorów"
    ]
    
    print("--- Starting RAG Verification ---")
    
    for q in queries:
        print(f"\nSearching for: '{q}'")
        results = rag.search(q, k=1)
        
        if results:
            print("SUKCES")
            print(f"Found: {results[0]['content']}")
            print(f"Source: {results[0]['source']}")
        else:
            print("BŁĄD: Brak wyników.")

if __name__ == "__main__":
    verify_rag()
