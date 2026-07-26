from pathlib import Path

import faiss
import numpy as np


BASE_DIR = Path("C:/Users/DELL/Documents/RAG/data")

EMBEDDING_FILE = BASE_DIR / "embeddings.npy"

INDEX_FILE = BASE_DIR / "index.faiss"


def main():

    print("Loading embeddings...")

    embeddings = np.load(
        EMBEDDING_FILE
    ).astype("float32")

    print("Shape:", embeddings.shape)

    dim = embeddings.shape[1]

    print("Creating FAISS index...")

    # cosine similarity
    index = faiss.IndexFlatIP(dim)

    index.add(embeddings)

    print("Vectors:", index.ntotal)

    faiss.write_index(
        index,
        str(INDEX_FILE)
    )

    print("Saved:", INDEX_FILE)


if __name__ == "__main__":
    main()