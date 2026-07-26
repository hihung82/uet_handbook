import sys
import json
from pathlib import Path

from chunker import create_chunks


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(
        encoding="utf-8"
    )


DATA_FILE = Path(
    "C:/Users/DELL/Documents/RAG/data/processed/filtered_documents.jsonl"
)


total = 0


with open(
    DATA_FILE,
    encoding="utf-8"
) as f:


    for line in f:


        doc = json.loads(line)


        chunks = create_chunks(doc)


        print(
            doc["title"],
            "=>",
            len(chunks),
            "chunks"
        )


        if chunks:

            print(
                "Example:"
            )

            print(
                chunks[0]["text"][:300]
            )

            print(
                "="*50
            )


        total += len(chunks)



print(
    "TOTAL CHUNKS:",
    total
)