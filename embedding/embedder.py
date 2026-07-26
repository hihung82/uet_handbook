import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_PATH = r"C:/Users/DELL/.cache/huggingface/hub/models--BAAI--bge-m3/snapshots/5617a9f61b028005a4858fdac845db406aefb181"

BATCH_SIZE = 4          # CPU nên để nhỏ

INPUT_FILE = Path("C:/Users/DELL/Documents/RAG/data/processed/chunks.jsonl")

OUTPUT_EMBEDDING = Path("C:/Users/DELL/Documents/RAG/data/embeddings.npy")

OUTPUT_METADATA = Path("C:/Users/DELL/Documents/RAG/data/metadata.jsonl")


def load_chunks():

    chunks = []

    with open(INPUT_FILE, encoding="utf-8") as f:

        for line in f:

            chunks.append(json.loads(line))

    return chunks


def main():

    print("Loading model...")

    model = SentenceTransformer(
        MODEL_PATH,
        device="cpu"
    )

    print("Model loaded!")

    print("Loading chunks...")

    chunks = load_chunks()

    texts = [chunk["text"] for chunk in chunks]

    print(f"{len(texts)} chunks")

    print("Embedding...")

    embeddings = model.encode(

        texts,

        batch_size=BATCH_SIZE,

        normalize_embeddings=True,

        convert_to_numpy=True,

        show_progress_bar=True

    )

    np.save(OUTPUT_EMBEDDING, embeddings)

    with open(OUTPUT_METADATA, "w", encoding="utf-8") as f:

        for chunk in chunks:

            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    print("\nDone!")

    print("Embedding shape:", embeddings.shape)

    print("Saved:", OUTPUT_EMBEDDING)

    print("Saved:", OUTPUT_METADATA)


if __name__ == "__main__":

    main()