"""Step 1: PDF -> plain text, one record per page.

Keeps the printed page number with each page's text so chunks (and later,
citations and eval grading) can point back to a page. Run from repo root:

    python src/extract.py
"""

import json
from pathlib import Path

from pypdf import PdfReader

RAW = Path("data/raw/kyc-master-direction-2025-08-14.pdf")
OUT = Path("data/processed/pages.jsonl")


def main() -> None:
    reader = PdfReader(RAW)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    n_chars = 0
    with OUT.open("w") as f:
        for i, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            text = " ".join(text.split())  # collapse whitespace/newlines
            n_chars += len(text)
            f.write(json.dumps({"page": i, "text": text}) + "\n")
    print(f"extracted {len(reader.pages)} pages, {n_chars:,} chars -> {OUT}")


if __name__ == "__main__":
    main()
