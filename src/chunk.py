"""Step 2: pages -> fixed-size chunks (deliberately naive baseline).

800-character windows with 200-character overlap, cut within each page so
every chunk keeps an exact page number. Clause-aware chunking is a Phase 3
experiment; this version exists to be beaten. Run from repo root:

    python src/chunk.py
"""

import json
from pathlib import Path

PAGES = Path("data/processed/pages.jsonl")
OUT = Path("data/processed/chunks.jsonl")

CHUNK_SIZE = 800
OVERLAP = 200


def main() -> None:
    chunks = []
    for line in PAGES.open():
        rec = json.loads(line)
        text, page = rec["text"], rec["page"]
        start = 0
        while start < len(text):
            piece = text[start : start + CHUNK_SIZE]
            if piece.strip():
                chunks.append({"id": len(chunks), "page": page, "text": piece})
            start += CHUNK_SIZE - OVERLAP
    with OUT.open("w") as f:
        for c in chunks:
            f.write(json.dumps(c) + "\n")
    print(f"{len(chunks)} chunks (size={CHUNK_SIZE}, overlap={OVERLAP}) -> {OUT}")


if __name__ == "__main__":
    main()
