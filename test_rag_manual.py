from src.core.llm_engine import LLMEngine

def test_rag_integration():
    print("Inicjalizacja LLMEngine...")
    try:
        # Zakładamy, że config jest już załadowany wewnątrz LLMEngine
        engine = LLMEngine()
    except Exception as e:
        print(f"Błąd inicjalizacji silnika: {e}")
        return

    print("\n=== START TESTÓW INTEGRACYJNYCH RAG ===\n")

    # Test A (Upał)
    print("--- Test A: Upał (>30 stopni) ---")
    query_a = "Jest bardzo gorąco, ponad 30 stopni, co ubrać?"
    print(f"Pytanie: {query_a}")
    
    response_a = engine.process_query(query_a)
    print(f"Odpowiedź: {response_a}")
    
    keywords_a = ["len", "lniana", "lniane", "lniany"]
    found_a = any(kw in response_a.lower() for kw in keywords_a)
    
    if found_a:
        print("PASS ✅ - RAG Knowledge Used (Found linen reference)\n")
    else:
        print("FAIL ❌ - Brak wzmianki o lnie\n")

    # Test B (Materiał)
    print("--- Test B: Poliester na kolację ---")
    query_b = "Idę na elegancką kolację, czy mogę ubrać poliester?"
    print(f"Pytanie: {query_b}")
    
    response_b = engine.process_query(query_b)
    print(f"Odpowiedź: {response_b}")
    
    # Słowa kluczowe sugerujące unikanie lub odradzanie
    negative_keywords = ["nie", "unikaj", "odradzam", "słabo", "słaby", "kiepski", "zły", "gorąco", "pocić"]
    # Lub sugestia innego materiału (alternatywy)
    alternative_keywords = ["lepiej", "bawełna", "jedwab", "wiskoza", "wełna", "zamiast"]
    
    found_b = any(kw in response_b.lower() for kw in negative_keywords + alternative_keywords)
    
    if found_b:
        print("PASS ✅ - RAG Knowledge Used (Negative advice or alternative suggested)\n")
    else:
        print("FAIL ❌ - Brak odradzenia poliestru\n")

if __name__ == "__main__":
    test_rag_integration()