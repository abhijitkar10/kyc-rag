"""Swappable retrievers. Every retriever is a callable

    retriever(question: str, top_k: int) -> [(score, chunk), ...]

so the eval harness can A/B them with one flag. This is the seam Phase 3 turns.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def get_retriever(name: str):
    if name == "dense":
        from search import search
        return search

    if name == "bm25":
        from bm25 import BM25Index
        idx = BM25Index()
        return lambda q, top_k=5: idx.search(q, top_k)

    raise ValueError(f"unknown retriever: {name}")
