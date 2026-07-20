"""Step 5: the writer — Claude answers ONLY from retrieved chunks, with citations.

Model: claude-haiku-4-5 ($1/$5 per MTok — a query costs a fraction of a paisa).
Needs ANTHROPIC_API_KEY in the environment.
"""

import sys
from pathlib import Path

import anthropic

sys.path.insert(0, str(Path(__file__).parent))
from search import search  # noqa: E402

MODEL = "claude-haiku-4-5"

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
    client = anthropic.Anthropic()
    resp = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM,
        messages=[{"role": "user", "content": f"{excerpts}\n\nQUESTION: {question}"}],
    )
    return "".join(b.text for b in resp.content if b.type == "text")


if __name__ == "__main__":
    print(answer(" ".join(sys.argv[1:]) or "What is an OVD?"))
