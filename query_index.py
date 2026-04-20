"""
Тестовые запросы к созданному индексу ChromaDB
"""

import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_PERSIST_DIR = "chroma.db"
EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-base"

def query_index(query_text: str, top_k: int = 3):
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    collection = client.get_collection("knowledge_base")

    # Генерируем эмбеддинг для запроса с префиксом "query: "
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    query_embedding = model.encode(f"query: {query_text}", normalize_embeddings=True)

    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    return results

def run_tests():
    test_queries = [
        "Кто такой Xarn Velgor и какая у него роль?",
        "Что такое Void Core и для чего он использовался?",
        "Опиши планету Dusthal и её особенности."
    ]

    for q in test_queries:
        print("\n" + "="*60)
        print(f"Запрос: {q}")
        print("="*60)
        results = query_index(q, top_k=2)
        if results['documents'] and results['documents'][0]:
            for i, (doc, meta, dist) in enumerate(zip(results['documents'][0], results['metadatas'][0], results['distances'][0])):
                print(f"\n--- Результат {i+1} (расстояние = {dist:.4f}) ---")
                print(f"Источник: {meta['filename']}, чанк {meta['chunk_index']}/{meta['total_chunks']}")
                print(f"Текст:\n{doc[:500]}...")
        else:
            print("Ничего не найдено.")

if __name__ == "__main__":
    run_tests()