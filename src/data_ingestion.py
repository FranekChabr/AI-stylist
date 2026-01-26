import os
import glob
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from src.config import Config
from src.utils.logger import logger

def main():
    # 1. Przeskanuj folder data/knowledge_base
    kb_path = os.path.join(Config.DATA_DIR, "knowledge_base")
    txt_files = glob.glob(os.path.join(kb_path, "*.txt"))

    if not txt_files:
        print(f"No .txt files found in {kb_path}")
        return

    print(f"Found {len(txt_files)} files to process.")

    documents = []
    all_sentences = []
    
    # 2. & 3. Wczytaj treść i podziel na fragmenty
    for file_path in txt_files:
        filename = os.path.basename(file_path)
        print(f"Processing: {filename}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
                
                for line in lines:
                    documents.append({
                        "content": line,
                        "source": filename
                    })
                    all_sentences.append(line)
        except Exception as e:
            print(f"Error reading {filename}: {e}")

    if not all_sentences:
        print("No content to index.")
        return

    # 4. Stwórz embeddingi
    print(f"Generating embeddings for {len(all_sentences)} chunks...")
    model = SentenceTransformer(Config.EMBEDDING_MODEL)
    embeddings = model.encode(all_sentences)
    embeddings = np.array(embeddings).astype('float32')

    # 5. Zapisz/Zaktualizuj indeks FAISS
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    # Ensure vector store directory exists
    os.makedirs(Config.VECTOR_STORE_PATH, exist_ok=True)
    
    index_path = os.path.join(Config.VECTOR_STORE_PATH, "index.faiss")
    meta_path = os.path.join(Config.VECTOR_STORE_PATH, "index.pkl")
    
    faiss.write_index(index, index_path)
    with open(meta_path, "wb") as f:
        pickle.dump(documents, f)

    # 6. Wyświetl raport
    print("\n--- Ingestion Report ---")
    print(f"Files processed: {len(txt_files)}")
    print(f"Chunks indexed: {len(all_sentences)}")
    print(f"Index saved to: {index_path}")
    print(f"Metadata saved to: {meta_path}")

if __name__ == "__main__":
    main()
