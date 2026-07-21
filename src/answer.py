"""Step 5: the writer — the LLM answers ONLY from retrieved chunks, with citations.

Provider is chosen automatically (Gemini free tier, else Claude) — see llm.py.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from search import search  # noqa: E402
import llm  # noqa: E402

SYSTEM = """You are a compliance assistant for the RBI KYC Master Direction.
Answer ONLY from the excerpts provided by the user. For every claim, cite the
source in the form [KYC Master Direction, p.<page>]. Do not use any outside
knowledge. If the answer is not contained in the excerpts, reply exactly:
"Not found in the provided documents." """


def answer(question: str, top_k: int = 5) -> str:
    hits = search(question, top_k=top_k)
    excerpts = "\n\n".join(
        f"[Excerpt {i+1} — KYC Master Direction, p.{c['page']}]\n{c['text']}"
        for i, (_, c) in enumerate(hits)
    )
    return llm.complete(SYSTEM, f"{excerpts}\n\nQUESTION: {question}")


if __name__ == "__main__":
    print(answer(" ".join(sys.argv[1:]) or "What is an OVD?"))
