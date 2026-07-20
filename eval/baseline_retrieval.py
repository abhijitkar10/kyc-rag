"""Phase 1 baseline: retrieval-only scoring of the 20 eval questions.

Grades the LIBRARIAN only (no LLM needed): for each answerable question, did a
top-5 chunk come from the page named in clause_ref? For trick questions, report
the best similarity score (raw material for the Phase 4 refusal threshold).

    python eval/baseline_retrieval.py
"""

import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from search import search  # noqa: E402

QUESTIONS = Path("eval/questions.csv")


def expected_pages(clause_ref: str) -> set[int]:
    """Parse page numbers out of refs like 'Para 17(iii)-(v), p.26-27; ... p.13'."""
    pages: set[int] = set()
    for m in re.finditer(r"p\.(\d+)(?:-(\d+))?", clause_ref):
        lo = int(m.group(1))
        hi = int(m.group(2)) if m.group(2) else lo
        pages.update(range(lo, hi + 1))
    return pages


def main() -> None:
    rows = list(csv.DictReader(QUESTIONS.open()))
    hits, total = 0, 0
    trick_scores = []

    print(f"{'id':>3} {'ok':>3} {'best':>6}  question")
    for row in rows:
        results = search(row["question"], top_k=5)
        best_score = results[0][0]
        if row["answerable"] == "yes":
            total += 1
            want = expected_pages(row["clause_ref"])
            got = {c["page"] for _, c in results}
            hit = bool(want & got)
            hits += hit
            print(f"{row['id']:>3} {'✓' if hit else '✗':>3} {best_score:6.3f}  {row['question'][:70]}")
        else:
            trick_scores.append(best_score)
            print(f"{row['id']:>3} {'—':>3} {best_score:6.3f}  (trick) {row['question'][:62]}")

    print(f"\nrecall@5 = {hits}/{total} = {hits/total:.2f}")
    if trick_scores:
        print(f"trick-question best scores: {', '.join(f'{s:.3f}' for s in trick_scores)}"
              f"  (refusal threshold must sit above these)")


if __name__ == "__main__":
    main()
