"""Step 5: the writer — the LLM answers ONLY from retrieved chunks, with citations.

Provider is chosen automatically (Gemini free tier, else Claude) — see llm.py.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from retrievers import get_retriever  # noqa: E402
import llm  # noqa: E402
import verify  # noqa: E402

# Default to rerank: the best measured config (recall@5 0.93, recall@1 0.77). It loads
# a ~1.1GB cross-encoder on first use, then caches. Set RETRIEVER=hybrid for a lighter,
# slightly weaker setup (0.91) with no extra model download.
_search = get_retriever(os.environ.get("RETRIEVER", "rerank"))

SYSTEM = """You are a compliance assistant for the RBI KYC Master Direction.
Answer ONLY from the excerpts provided by the user. For every claim, cite the
source in the form [KYC Master Direction, p.<page>]. Do not use any outside
knowledge. If the answer is not contained in the excerpts, reply exactly:
"Not found in the provided documents." """


def answer(question: str, top_k: int = 5, retriever=None) -> str:
    # `retriever` lets the eval harness pass the SAME retriever it grades with,
    # so the grounding check compares against exactly what the LLM saw.
    hits = (retriever or _search)(question, top_k=top_k)
    retrieved_pages = {c["page"] for _, c in hits}
    excerpts = "\n\n".join(
        f"[Excerpt {i+1} — KYC Master Direction, p.{c['page']}]\n{c['text']}"
        for i, (_, c) in enumerate(hits)
    )
    raw = llm.complete(SYSTEM, f"{excerpts}\n\nQUESTION: {question}")
    # Phase 4 guardrail: flag any citation to a page we didn't actually retrieve.
    checked, _verdict = verify.enforce(raw, retrieved_pages)
    return checked


if __name__ == "__main__":
    print(answer(" ".join(sys.argv[1:]) or "What is an OVD?"))
