import json
from pathlib import Path

from chunker import create_chunks
import sys

sys.stdout.reconfigure(encoding="utf-8")
import re


def load_markdown(md_file):

    text = md_file.read_text(encoding="utf-8")

    # Chuẩn hóa
    text = text.lstrip("\ufeff")
    text = text.replace("\r\n", "\n")

    title = md_file.stem
    url = ""
    doc_type = "markdown"

    # Đọc front matter
    if text.startswith("---"):
        parts = text.split("---", 2)

        if len(parts) == 3:
            header = parts[1]
            text = parts[2].lstrip()

            for line in header.splitlines():
                line = line.strip()

                if ":" not in line:
                    continue

                key, value = line.split(":", 1)

                key = key.strip().lower()
                value = value.strip()

                if key == "title":
                    title = value
                elif key == "url":
                    url = value
                elif key == "type":
                    doc_type = value

    # Xóa ảnh markdown
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)

    return {
        "id": md_file.stem,
        "title": title,
        "source": str(md_file),
        "url": url,
        "type": doc_type,
        "text": text.strip()
    }

INPUT_DIR = Path("C:/Users/DELL/Documents/RAG/data/raw/markdown")
OUTPUT_FILE = Path("data/processed/chunks.jsonl")

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

total_docs = 0
total_chunks = 0

with open(OUTPUT_FILE, "w", encoding="utf-8") as fout:

    for md_file in sorted(INPUT_DIR.glob("*.md")):

        document = load_markdown(md_file)

        chunks = create_chunks(document)

        total_docs += 1
        total_chunks += len(chunks)

        for chunk in chunks:
            fout.write(json.dumps(chunk, ensure_ascii=False) + "\n")

print(f"Documents: {total_docs}")
print(f"Chunks: {total_chunks}")
print(f"Saved: {OUTPUT_FILE}")