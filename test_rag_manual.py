from src.core.rag_engine import get_rag_engine

print("Inicjalizacja RAG (to chwilę potrwa)...")
rag = get_rag_engine()

questions = [
    "Co ubrać jak pada deszcz?",
    "Czy czapka jest potrzebna w zimie?"
]

for q in questions:
    print(f"\nPYTANIE: {q}")
    results = rag.search(q, k=2)
    for res in results:
        print(f" - [Źródło: {res['source']}] {res['content']}")