"""
test_retrieval.py

Test semantic retrieval.
"""

import sys

sys.stdout.reconfigure(encoding="utf-8")

from retriever import retrieve


def main():

    print("=" * 80)
    print("Semantic Retrieval Test")
    print("=" * 80)

    while True:

        query = input("\nQuestion: ").strip()

        if query.lower() in ["exit", "quit"]:
            break

        results = retrieve(query)

        print(f"\nFound {len(results)} results\n")

        for i, doc in enumerate(results, start=1):

            print("=" * 80)
            print(f"Top {i}")
            print(f"Score    : {doc['score']:.4f}")
            print(f"Title    : {doc['title']}")
            print(f"Chapter  : {doc['chapter']}")
            print(f"Article  : {doc['article']}")
            print(f"Heading1 : {doc['heading1']}")
            print(f"Heading2 : {doc['heading2']}")
            print(f"Heading3 : {doc['heading3']}")
            print(f"Source   : {doc['source']}")
            print("-" * 80)
            print(doc["text"][:700])
            print()


if __name__ == "__main__":
    main()