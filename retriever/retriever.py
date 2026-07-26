import json
import sys
from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer


sys.stdout.reconfigure(encoding="utf-8")

MODEL_PATH = r"C:/Users/DELL/.cache/huggingface/hub/models--BAAI--bge-m3/snapshots/5617a9f61b028005a4858fdac845db406aefb181"

TOP_K = 20

BASE_DIR = Path("C:/Users/DELL/Documents/RAG/data")

INDEX_FILE = BASE_DIR / "index.faiss"
METADATA_FILE = BASE_DIR / "metadata.jsonl"


print("Loading embedding model...")

model = SentenceTransformer(
    MODEL_PATH,
    device="cpu"
)

print("Embedding model loaded!")

print("Loading FAISS index...")

index = faiss.read_index(str(INDEX_FILE))

print("Loading metadata...")

metadata = []

with open(METADATA_FILE, encoding="utf-8") as f:
    for line in f:
        metadata.append(json.loads(line))

print(f"Loaded {index.ntotal} vectors")


def semantic_retrieve(query, top_k=TOP_K):
    # encode câu hỏi
    query_embedding = model.encode(
        query,
        normalize_embeddings=True,
        convert_to_numpy=True
    ).astype("float32")

    scores, indices = index.search(
        query_embedding.reshape(1, -1),
        top_k
    )

    results = []

    for rank, (score, idx) in enumerate(
            zip(scores[0], indices[0]),
            start=1):

        if idx == -1:
            continue

        chunk = metadata[idx]

        results.append({

            "chunk_id": chunk["chunk_id"],

            "document_id": chunk["document_id"],

            "rank": rank, # thêm

            "retriever": "semantic",

            "score": float(score), # thêm

            "title": chunk["title"],

            "chapter": chunk.get("chapter"),

            "article": chunk.get("article"),

            "heading1": chunk.get("heading1"),

            "heading2": chunk.get("heading2"),

            "heading3": chunk.get("heading3"),

            "source": chunk.get("source"),

            "type": chunk.get("type"),

            "text": chunk["text"]

        })

    return results


# test

if __name__ == "__main__":

    while True:

        query = input("\nQuestion: ")

        if query.lower() in ["exit", "quit"]:
            break

        docs = semantic_retrieve(query)

        if not docs:
            print("\nKhông tìm thấy tài liệu phù hợp.\n")
            continue

        print()

        for i, doc in enumerate(docs[:5], start=1):

            print("=" * 80)
            print(f"Top {i}")
            print(f"Retriever : {doc['retriever']}")
            print(f"Rank      : {doc['rank']}")
            print(f"Score     : {doc['score']:.4f}")
            print(f"Title     : {doc['title']}")
            print(f"Chapter   : {doc['chapter']}")
            print(f"Article   : {doc['article']}")
            print(f"Heading1  : {doc['heading1']}")
            print(f"Heading2  : {doc['heading2']}")
            print(f"Heading3  : {doc['heading3']}")
            print(f"Source    : {doc['source']}")
            print("-" * 80)
            print(doc["text"][:700])
            print()