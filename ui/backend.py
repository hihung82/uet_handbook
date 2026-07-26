import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from retriever.hybrid_retriever import hybrid_retrieve
from llm.generator import generate_answer
import inspect

print("=" * 80)
print("Generator:", inspect.getfile(generate_answer))
print("Signature:", inspect.signature(generate_answer))
print("=" * 80)


def ask(question, history):
    # trả về top 5
    docs = hybrid_retrieve(
        question,
        top_k=5
    )
    # gửi sang colab
    result = generate_answer(
        question=question,
        retrieved_docs=docs,
        history=history
    )

    answer = result["answer"].replace("Answer:", "").strip()

    sources = result.get("sources", [])

    return answer, sources