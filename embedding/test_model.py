from transformers import AutoTokenizer, AutoModel

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(
    "BAAI/bge-m3",
    local_files_only=True
)
print("Tokenizer OK")

print("Loading model...")
model = AutoModel.from_pretrained(
    "BAAI/bge-m3",
    local_files_only=True
)
print("Model OK")