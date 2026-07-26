import sys

sys.stdout.reconfigure(
    encoding="utf-8"
)

from retriever.retriever import semantic_retrieve
from retriever.bm25_retriever import bm25_retrieve


TOP_K = 20

RRF_K = 60



def min_max_normalize(score_dict):

    values = list(score_dict.values())

    if not values:
        return {}


    min_score = min(values)
    max_score = max(values)


    # tránh chia cho 0
    if max_score == min_score:

        return {
            k: 1.0
            for k in score_dict
        }


    normalized = {}

    for k, v in score_dict.items():

        normalized[k] = (
            (v - min_score)
            /
            (max_score - min_score)
        )

    return normalized




def weighted_reciprocal_rank_fusion(
        semantic_docs,
        bm25_docs
):

    scores = {}

    documents = {}


    semantic_scores = {}

    for doc in semantic_docs:

        semantic_scores[
            doc["chunk_id"]
        ] = doc["score"]


    semantic_confidence = min_max_normalize(
        semantic_scores
    )



    bm25_scores = {}

    for doc in bm25_docs:

        # tránh score âm của BM25
        bm25_scores[
            doc["chunk_id"]
        ] = max(doc["score"], 0)



    bm25_confidence = min_max_normalize(
        bm25_scores
    )




    for doc in semantic_docs:

        cid = doc["chunk_id"]

        rank = doc["rank"]

        confidence = semantic_confidence[cid]


        scores[cid] = scores.get(cid, 0) + (
            confidence /
            (RRF_K + rank)
        )


        documents[cid] = doc


    for doc in bm25_docs:

        cid = doc["chunk_id"]

        rank = doc["rank"]

        confidence = bm25_confidence[cid]


        scores[cid] = scores.get(cid, 0) + (
            confidence /
            (RRF_K + rank)
        )


        if cid not in documents:

            documents[cid] = doc




    ranked = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )



    results = []


    for cid, score in ranked:

        doc = documents[cid].copy()

        doc["retriever"] = "hybrid"

        doc["wrrf_score"] = score


        results.append(doc)



    return results




def hybrid_retrieve(
        query,
        top_k=TOP_K
):

    semantic_docs = semantic_retrieve(
        query,
        top_k=50
    )


    bm25_docs = bm25_retrieve(
        query,
        top_k=50
    )


    fused_docs = weighted_reciprocal_rank_fusion(
        semantic_docs,
        bm25_docs
    )


    return fused_docs[:top_k]





# test
if __name__ == "__main__":

    while True:

        query = input("\nQuestion: ")


        if query.lower() in [
            "exit",
            "quit"
        ]:
            break



        docs = hybrid_retrieve(query)


        print()


        for i, doc in enumerate(
            docs,
            start=1
        ):

            print("=" * 80)

            print(f"Top {i}")

            print(
                f"WRRF Score : {doc['wrrf_score']:.6f}"
            )

            print(
                f"Title      : {doc['title']}"
            )

            print(
                f"Article    : {doc['article']}"
            )

            print("-" * 80)

            print(
                doc["text"][:700]
            )

            print()