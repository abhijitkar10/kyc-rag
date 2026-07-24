"""Swappable retrievers. Every retriever is a callable

    retriever(question: str, top_k: int) -> [(score, chunk), ...]

so the eval harness can A/B them with one flag. This is the seam Phase 3 turns.
"""

import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

RRF_K = 60   # standard Reciprocal Rank Fusion constant
POOL = 30    # candidates pulled from each retriever before fusing


def get_retriever(name: str):
    if name == "dense":
        from search import search
        return search

    if name == "bm25":
        from bm25 import BM25Index
        idx = BM25Index()
        return lambda q, top_k=5: idx.search(q, top_k)

    if name == "hybrid":
        from search import search as dense
        from bm25 import BM25Index
        bm = BM25Index()

        def hybrid(q: str, top_k: int = 5):
            # Reciprocal Rank Fusion: each list contributes 1/(RRF_K + rank).
            # Uses rank position only, so cosine and BM25 score scales never mix.
            fused: dict[int, float] = defaultdict(float)
            chunk_by_id: dict[int, dict] = {}
            for hits in (dense(q, top_k=POOL), bm.search(q, top_k=POOL)):
                for rank, (_, c) in enumerate(hits):
                    fused[c["id"]] += 1.0 / (RRF_K + rank + 1)  # rank is 1-indexed
                    chunk_by_id[c["id"]] = c
            ranked = sorted(fused.items(), key=lambda kv: kv[1], reverse=True)[:top_k]
            return [(score, chunk_by_id[i]) for i, score in ranked]

        return hybrid

    if name == "rerank":
        import os
        from sentence_transformers import CrossEncoder
        hybrid = get_retriever("hybrid")
        # Default: small MS-MARCO cross-encoder. Override with RERANK_MODEL,
        # e.g. BAAI/bge-reranker-base (stronger, pairs with the BGE embedder).
        ce = CrossEncoder(os.environ.get("RERANK_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2"))

        def rerank(q: str, top_k: int = 5, pool: int = 20):
            cands = hybrid(q, top_k=pool)              # fast stage: fused candidates
            if not cands:
                return []
            scores = ce.predict([(q, c["text"]) for _, c in cands])  # joint scoring
            order = sorted(range(len(cands)), key=lambda i: scores[i], reverse=True)
            return [(float(scores[i]), cands[i][1]) for i in order[:top_k]]

        return rerank

    raise ValueError(f"unknown retriever: {name}")
