"""Step 4: the search engine — hand-written cosine similarity.

The entire "vector search" is search(): one matrix-vector dot product over
normalized vectors, then a sort. No vector database, no framework. Run from
repo root to try it:

    python src/search.py "Can I open an account over a video call?"
"""

import json
import sys
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

CHUNKS = Path("data/processed/chunks.jsonl")
VECTORS = Path("data/processed/embeddings.npz")

MODEL_NAME = "BAAI/bge-small-en-v1.5"
# BGE models are trained to see queries with this prefix (model card requirement
# for retrieval); passages are embedded without it.
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "

_model = None
_chunks = None
_vecs = None


def _load():
    global _model, _chunks, _vecs
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
        _chunks = [json.loads(line) for line in CHUNKS.open()]
        _vecs = np.load(VECTORS)["vectors"]


def search(question: str, top_k: int = 5):
    """Return the top_k most similar chunks as (score, chunk) pairs."""
    _load()
    q = _model.encode([QUERY_PREFIX + question], normalize_embeddings=True)[0]
    scores = _vecs @ q                       # every dot product at once
    best = np.argsort(scores)[::-1][:top_k]  # indices, highest first
    return [(float(scores[i]), _chunks[i]) for i in best]


if __name__ == "__main__":
    for score, chunk in search(" ".join(sys.argv[1:]) or "What is an OVD?"):
        print(f"[{score:.3f}] p.{chunk['page']}  {chunk['text'][:100]}...")
