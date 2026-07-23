"""Generation smoke test: does the full pipeline answer, cite, and refuse?

Runs a few representative questions end-to-end (retrieval + LLM) and checks the
two behaviours that matter at Phase 1: answerable questions get a page citation;
trick questions get refused. Needs an LLM key (see src/llm.py).

    python eval/generation_smoke.py
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
import llm  # noqa: E402
from answer import answer  # noqa: E402

# (question, should_refuse)
CASES = [
    ("Which documents count as Officially Valid Documents for KYC?", False),  # direct
    ("Can I finish opening my bank account over a video call?", False),       # paraphrase
    ("What are the three monetary limits on Aadhaar OTP e-KYC accounts?", False),  # numeric
    ("What are the best tax-saving options under Section 80C?", True),        # trick -> refuse
]

REFUSAL = "Not found in the provided documents."
CITE = re.compile(r"\[KYC Master Direction, p\.\d+\]")


def main() -> None:
    name, model = llm.provider()
    print(f"provider: {name} ({model})\n")
    passed = 0
    for q, should_refuse in CASES:
        out = answer(q).strip()
        # A refusal is a LEADING refusal line. The phrase can also appear mid-answer
        # when the model honestly flags one unsupported sub-point of an otherwise
        # answered question — that is a partial answer, not a refusal.
        refused = out.lower().startswith(REFUSAL.lower())
        cited = bool(CITE.search(out))
        ok = refused if should_refuse else (cited and not refused)
        passed += ok
        tag = "REFUSE" if should_refuse else "ANSWER"
        print(f"[{'PASS' if ok else 'FAIL'}] ({tag}) {q}")
        print(f"        {out[:160].replace(chr(10), ' ')}\n")
    print(f"{passed}/{len(CASES)} behavioural checks passed")


if __name__ == "__main__":
    main()
