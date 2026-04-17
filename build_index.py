"""
Генерация эмбеддингов и запись в ChromaDB
"""

import time
import uuid
from pathlib import Path
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document as LangchainDocument
from sentence_transformers import SentenceTransformer
import chromadb
from tqdm import tqdm

KNOWLEDGE_BASE_DIR = Path("knowledge_base")
CHROMA_PERSIST_DIR = "chroma.db"
CHUNK_SIZE = 500                              # ~250 токенов
CHUNK_OVERLAP = 50                            # перекрытие между чанками
EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-base"
BATCH_SIZE = 32

def load_documents_from_folder(folder: Path) -> List[LangchainDocument]:
    docs = []
    for file_path in folder.glob("*.txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        if not content:
            continue
        metadata = {
            "source": str(file_path),
            "filename": file_path.stem,
            "doc_id": str(uuid.uuid4())
        }
        doc = LangchainDocument(page_content=content, metadata=metadata)
        docs.append(doc)
    print(f"Загружено документов: {len(docs)}")
    return docs

def split_documents(docs: List[LangchainDocument]) -> List[LangchainDocument]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""],
        length_function=len,
    )
    chunks = text_splitter.split_documents(docs)
    chunk_counter = {}
    for chunk in chunks:
        source = chunk.metadata["source"]
        if source not in chunk_counter:
            chunk_counter[source] = 0
        chunk_counter[source] += 1
        chunk.metadata["chunk_index"] = chunk_counter[source]
        chunk.metadata["chunk_id"] = f"{chunk.metadata['filename']}_chunk_{chunk_counter[source]}"
    for chunk in chunks:
        source = chunk.metadata["source"]
        chunk.metadata["total_chunks"] = chunk_counter[source]
    return chunks

def generate_embeddings_in_batches(texts: List[str], model: SentenceTransformer, batch_size: int = BATCH_SIZE):
    all_embeddings = []
    for i in tqdm(range(0, len(texts), batch_size), desc="Генерация эмбеддингов"):
        batch_texts = texts[i:i+batch_size]
        # Для модели e5 рекомендуется добавлять префикс "query:" или "passage:" при инференсе
        prefixed_batch = [f"passage: {t}" for t in batch_texts]
        embeddings = model.encode(prefixed_batch, show_progress_bar=False, normalize_embeddings=True)
        all_embeddings.extend(embeddings)
    return all_embeddings

def create_chroma_index(chunks: List[LangchainDocument], persist_dir: str, batch_size: int):
    client = chromadb.PersistentClient(path=persist_dir)

    existing_collections = client.list_collections()
    collection_names = [col.name for col in existing_collections]

    if "knowledge_base" in collection_names:
        client.delete_collection("knowledge_base")
        print("Старая коллекция удалена.")

    collection = client.create_collection(name="knowledge_base")

    ids = []
    documents = []
    metadatas = []
    texts_for_embedding = []

    for idx, chunk in enumerate(chunks):
        chunk_id = chunk.metadata["chunk_id"]
        ids.append(chunk_id)
        documents.append(chunk.page_content)
        metadatas.append({
            "source": chunk.metadata["source"],
            "filename": chunk.metadata["filename"],
            "chunk_index": chunk.metadata["chunk_index"],
            "total_chunks": chunk.metadata["total_chunks"],
            "doc_id": chunk.metadata.get("doc_id", "")
        })
        texts_for_embedding.append(chunk.page_content)

    print("Загрузка модели эмбеддингов...")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    print(f"Модель загружена. Размер эмбеддинга: {model.get_embedding_dimension()}")

    print("Генерация эмбеддингов...")
    all_embeddings = []
    for i in tqdm(range(0, len(texts_for_embedding), BATCH_SIZE)):
        batch_texts = texts_for_embedding[i:i+BATCH_SIZE]
        prefixed_batch = [f"passage: {t}" for t in batch_texts]
        batch_embeddings = model.encode(prefixed_batch, show_progress_bar=False, normalize_embeddings=True)
        all_embeddings.extend(batch_embeddings)

    print("Добавление в ChromaDB пакетами...")
    total = len(ids)
    for start in range(0, total, batch_size):
        end = min(start + batch_size, total)
        collection.add(
            ids=ids[start:end],
            documents=documents[start:end],
            metadatas=metadatas[start:end],
            embeddings=all_embeddings[start:end],
        )
        print(f"  Добавлено {end}/{total} чанков")

    print(f"Индекс создан. Всего чанков: {collection.count()}")

def main():
    start_time = time.time()

    print("Загрузка документов из knowledge_base/")
    docs = load_documents_from_folder(KNOWLEDGE_BASE_DIR)
    if not docs:
        print("Нет документов для индексации")
        return

    print("Разбиение на чанки")
    chunks = split_documents(docs)
    print(f"Создано чанков: {len(chunks)}")

    print("Создание индекса ChromaDB")
    create_chroma_index(chunks, CHROMA_PERSIST_DIR, 20)

    elapsed = time.time() - start_time
    print(f"\nИндексация завершена за {elapsed:.2f} секунд.")

if __name__ == "__main__":
    main()