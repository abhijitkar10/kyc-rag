"""Phase 4: citation verification — the guardrail against hallucinated citations.

The generator is told to cite [KYC Master Direction, p.N] for every claim. But
LLMs occasionally invent a plausible page that was NOT in the retrieved context
(we observed exactly this: one run fabricated a 'p.26' citation). A citation we
can't trace back to a retrieved chunk is worthless in compliance.

This deterministic post-check parses the cited pages and compares them to the
pages actually retrieved. It runs with no LLM, so it's cheap and testable.
"""

import re

CITE = re.compile(r"\[KYC Master Direction, p\.(\d+)\]")
REFUSAL = "Not found in the provided documents."


def cited_pages(text: str) -> set[int]:
    return {int(p) for p in CITE.findall(text)}


def verify(answer_text: str, retrieved_pages) -> tuple[str, set[int]]:
    """Classify an answer's citation health.

    Returns (verdict, ungrounded_pages) where verdict is one of:
      refusal   - the answer is a leading refusal (nothing to check)
      uncited   - answered but cited no page (suspect: unsupported claim)
      grounded  - every cited page was in the retrieved set
      ungrounded- at least one cited page was NOT retrieved (hallucinated cite)
    """
    if answer_text.strip().lower().startswith(REFUSAL.lower()):
        return "refusal", set()
    cites = cited_pages(answer_text)
    if not cites:
        return "uncited", set()
    ungrounded = cites - set(retrieved_pages)
    return ("grounded" if not ungrounded else "ungrounded"), ungrounded


def enforce(answer_text: str, retrieved_pages) -> tuple[str, str]:
    """Append a visible warning when the citation check fails. Returns
    (possibly-annotated text, verdict). We annotate rather than silently delete
    so a reviewer sees exactly what the model did — auditability over tidiness."""
    verdict, ungrounded = verify(answer_text, retrieved_pages)
    if verdict == "ungrounded":
        return (answer_text + f"\n\n[⚠ citation check: page(s) {sorted(ungrounded)} were "
                f"cited but are not in the retrieved context — treat those claims as "
                f"UNVERIFIED.]"), verdict
    if verdict == "uncited":
        return answer_text + "\n\n[⚠ citation check: no source citation found.]", verdict
    return answer_text, verdict


if __name__ == "__main__":
    # quick self-checks (no LLM needed)
    assert verify("X is true [KYC Master Direction, p.16].", [16, 17])[0] == "grounded"
    assert verify("X is true [KYC Master Direction, p.99].", [16, 17]) == ("ungrounded", {99})
    assert verify("Not found in the provided documents.", [])[0] == "refusal"
    assert verify("Some unsupported claim.", [16])[0] == "uncited"
    print("verify.py self-checks passed")
