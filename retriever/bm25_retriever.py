"""
bm25_retriever.py

Keyword retrieval using BM25.

Input:
    bm25.pkl
    metadata.jsonl

Output:
    Top-k keyword search results
"""


import json
import pickle
import re
import sys
from underthesea import word_tokenize
from pathlib import Path


# ==========================================================
# Config
# ==========================================================

sys.stdout.reconfigure(
    encoding="utf-8"
)


TOP_K = 50


BASE_DIR = Path(
    "C:/Users/DELL/Documents/RAG/data"
)


BM25_FILE = BASE_DIR / "bm25.pkl"

METADATA_FILE = BASE_DIR / "metadata.jsonl"



# ==========================================================
# Tokenizer
# ==========================================================

def tokenize(text):

    text = text.lower()

    text = re.sub(
        r"[^\w\s]",
        " ",
        text
    )

    text = word_tokenize(
        text,
        format="text"
    )

    return text.split()



# ==========================================================
# Load BM25
# ==========================================================


print("Loading BM25 index...")


with open(
    BM25_FILE,
    "rb"
) as f:

    bm25 = pickle.load(f)



print("Loading metadata...")


metadata = []


with open(
    METADATA_FILE,
    encoding="utf-8"
) as f:

    for line in f:

        metadata.append(
            json.loads(line)
        )



print(
    f"Loaded {len(metadata)} documents"
)



# ==========================================================
# BM25 Retrieval
# ==========================================================


def bm25_retrieve(
        query,
        top_k=TOP_K
):


    tokens = tokenize(query)


    scores = bm25.get_scores(
        tokens
    )


    # lấy index điểm cao nhất

    ranked_indices = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True
    )


    results = []


    rank = 1


    for idx in ranked_indices[:top_k]:


        chunk = metadata[idx]


        results.append({

            "chunk_id":
                chunk["chunk_id"],


            "document_id":
                chunk["document_id"],


            "rank":
                rank,


            "retriever":
                "bm25",


            "score":
                float(scores[idx]),


            "title":
                chunk["title"],


            "chapter":
                chunk.get("chapter"),


            "article":
                chunk.get("article"),


            "heading1":
                chunk.get("heading1"),


            "heading2":
                chunk.get("heading2"),


            "heading3":
                chunk.get("heading3"),


            "source":
                chunk.get("source"),


            "type":
                chunk.get("type"),


            "text":
                chunk["text"]

        })


        rank += 1



    return results




# ==========================================================
# Test
# ==========================================================


if __name__ == "__main__":


    while True:


        query = input(
            "\nQuestion: "
        )


        if query.lower() in [
            "exit",
            "quit"
        ]:
            break



        docs = bm25_retrieve(
            query
        )


        print()



        for i, doc in enumerate(
            docs[:5],
            start=1
        ):


            print(
                "=" * 80
            )

            print(
                f"Top {i}"
            )

            print(
                "Retriever:",
                doc["retriever"]
            )

            print(
                "Score:",
                doc["score"]
            )

            print(
                "Title:",
                doc["title"]
            )

            print(
                "-" * 80
            )

            print(
                doc["text"][:500]
            )

            print()