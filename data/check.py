import faiss
import numpy as np
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path("C:/Users/DELL/Documents/RAG/data")

INDEX_FILE = BASE_DIR / "index.faiss"

print("Loading index...")

index = faiss.read_index(str(INDEX_FILE))

print("=" * 60)
print("Vectors in index:", index.ntotal)
print("Dimension:", index.d)
print("=" * 60)

# Lấy 5 vector đầu
vectors = np.zeros((5, index.d), dtype="float32")

for i in range(5):
    index.reconstruct(i, vectors[i])

for i in range(5):
    print(f"\nVECTOR {i}")
    print("-" * 40)
    print(vectors[i][:10])      # 10 giá trị đầu
    print("Dimension:", vectors[i].shape)
    print("L2 Norm:", np.linalg.norm(vectors[i]))