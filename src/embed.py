"""Step 3: chunks -> embedding vectors, saved to disk.

Uses a local open-source model (BGE-small, 384 dims). Vectors are normalized
to length 1 so cosine similarity later is just a dot product. Run from repo
root (first run downloads the model, ~130MB):

    python src/embed.py
"""

import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

CHUNKS = Path("data/processed/chunks.jsonl")
OUT = Path("data/processed/embeddings.npz")

MODEL_NAME = "BAAI/bge-small-en-v1.5"


def main() -> None:
    texts = [json.loads(line)["text"] for line in CHUNKS.open()]
    model = SentenceTransformer(MODEL_NAME)
    vecs = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
    np.savez_compressed(OUT, vectors=vecs.astype(np.float32))
    print(f"embedded {len(texts)} chunks -> {OUT} (shape {vecs.shape})")


if __name__ == "__main__":
    main()
