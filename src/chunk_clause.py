"""Step 2 (better): clause-aware chunking. Overwrites chunks.jsonl.

Naive 800-char windows split a clause's heading from its body ("para 18 —
V-CIP may be used for..." landed in a different chunk than its conditions),
which caused the "right page, wrong chunk" misses. This splits on the
document's own top-level paragraph markers ("16.", "17.", "46A.", ...) so a
clause stays together, prefixes each chunk with its clause number, and packs
long clauses line-by-line into <=MAX_CHARS windows — each window keeps the
page of its first line so page-level grading stays honest.

    python src/chunk_clause.py     # then re-run src/embed.py

(The naive chunker src/chunk.py is kept for comparison; git history has the
naive chunks.jsonl.)
"""

import json
import re
from pathlib import Path

from pypdf import PdfReader

RAW = Path("data/raw/kyc-master-direction-2025-08-14.pdf")
OUT = Path("data/processed/chunks.jsonl")

MAX_CHARS = 1000
CLAUSE_START = re.compile(r"^(\d+[A-Z]?)\.\s")   # "16. ", "46A. " — not roman/letter sub-items
PAGE_NUM = re.compile(r"^\d+$")


def flush(label: str | None, seg: list[tuple[str, int]], chunks: list[dict]) -> None:
    """Pack a clause's lines into <=MAX_CHARS windows, page = first line's page."""
    if not seg:
        return
    prefix = f"[Para {label}] " if label else ""
    cur: list[str] = []
    cur_len = 0
    cur_page: int | None = None

    def emit() -> None:
        if not cur:
            return
        text = re.sub(r"\s+", " ", " ".join(cur)).strip()
        if text:
            chunks.append({"page": cur_page, "clause": label, "text": prefix + text})

    for line, page in seg:
        if cur_page is None:
            cur_page = page
        if cur and cur_len + len(line) > MAX_CHARS:
            emit()
            cur, cur_len, cur_page = [], 0, page
        cur.append(line)
        cur_len += len(line) + 1
    emit()


def main() -> None:
    reader = PdfReader(RAW)
    chunks: list[dict] = []
    label: str | None = None
    seg: list[tuple[str, int]] = []

    for page_no, page in enumerate(reader.pages, start=1):
        for line in (page.extract_text() or "").split("\n"):
            line = line.strip()
            if not line or PAGE_NUM.fullmatch(line):
                continue
            m = CLAUSE_START.match(line)
            if m:
                flush(label, seg, chunks)
                label = m.group(1)
                seg = [(line, page_no)]
            else:
                seg.append((line, page_no))
    flush(label, seg, chunks)

    for i, c in enumerate(chunks):
        c["id"] = i
    with OUT.open("w") as f:
        for c in chunks:
            f.write(json.dumps(c) + "\n")

    sizes = [len(c["text"]) for c in chunks]
    print(f"{len(chunks)} clause-aware chunks -> {OUT} "
          f"(avg {sum(sizes)//len(sizes)} chars, max {max(sizes)})")


if __name__ == "__main__":
    main()
