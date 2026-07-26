"""
build_bm25.py

Build BM25 index.

Input:
    metadata.jsonl

Output:
    bm25.pkl
"""

import json
import pickle
import re
from pathlib import Path
from underthesea import word_tokenize
from rank_bm25 import BM25Okapi


# ==========================================================
# Config
# ==========================================================

BASE_DIR = Path("C:/Users/DELL/Documents/RAG/data")

METADATA_FILE = BASE_DIR / "metadata.jsonl"

OUTPUT_FILE = BASE_DIR / "bm25.pkl"


# ==========================================================
# Tokenizer
# ==========================================================

def tokenize(text: str):

    text = text.lower()

    # bỏ dấu câu
    text = re.sub(r"[^\w\s]", " ", text)

    # tách từ tiếng Việt
    text = word_tokenize(text, format="text")

    # chuyển thành list token
    tokens = text.split()

    return tokens


# ==========================================================
# Main
# ==========================================================

def main():

    print("Loading metadata...")

    corpus = []

    with open(METADATA_FILE, encoding="utf-8") as f:

        for line in f:

            item = json.loads(line)

            corpus.append(
                tokenize(item["text"])
            )

    print(f"Documents : {len(corpus)}")

    print("Building BM25 index...")

    bm25 = BM25Okapi(corpus)

    print("Saving BM25 index...")

    with open(OUTPUT_FILE, "wb") as f:

        pickle.dump(bm25, f)

    print("\nDone!")
    print(f"Vocabulary : {len(bm25.idf)}")
    print(f"Saved      : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()