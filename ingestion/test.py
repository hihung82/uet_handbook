import sys
import json


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(
        encoding="utf-8"
    )
with open(
    "C:/Users/DELL/Documents/RAG/data/processed/filtered_documents.jsonl",
    encoding="utf-8"
) as f:

    for line in f:
        doc = json.loads(line)

        if doc["title"] == "Học phí - Chế độ chính sách":
            print(doc["text"][:1000])
            break