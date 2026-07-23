"""The unified eval harness — one command, one scorecard. (Supersedes
baseline_retrieval.py, kept for history.)

    python eval/run_eval.py                      # retrieval-only (fast loop for Phase 3)
    python eval/run_eval.py --gen                # + generation behaviour (needs LLM key)
    python eval/run_eval.py --tag exp1-bm25      # label the run

Retrieval metrics (page-level, graded against clause_ref):
  recall@1 / recall@5  - did a top-k chunk come from the right page?
  separation           - min best-score over answerable vs max over tricks
                         (a refusal threshold is only possible if these separate)

Generation metrics (--gen; behavioural, rate-limited for the free tier):
  cited     - answerable question answered with >=1 [.., p.N] citation
  grounded  - every cited page is among the retrieved pages (no invented cites)
  false_ref - answerable question wrongly lead-refused
  refused   - trick question correctly lead-refused

Per-question generation outputs are saved to eval/results/<tag>.jsonl for
manual faithfulness spot-checks (a human step - see FRIEND_ONBOARDING.md).
"""

import argparse
import csv
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from search import search  # noqa: E402

QUESTIONS = Path("eval/questions.csv")
RESULTS_DIR = Path("eval/results")
REFUSAL = "Not found in the provided documents."
CITE = re.compile(r"\[KYC Master Direction, p\.(\d+)\]")
GEN_SLEEP_S = 6.5  # Gemini free tier: 10 requests/minute


def expected_pages(clause_ref: str) -> set[int]:
    pages: set[int] = set()
    for m in re.finditer(r"p\.(\d+)(?:-(\d+))?", clause_ref):
        lo = int(m.group(1))
        hi = int(m.group(2)) if m.group(2) else lo
        pages.update(range(lo, hi + 1))
    return pages


def answer_with_retry(answer_fn, question: str, top_k: int, tries: int = 4) -> str:
    """The Gemini free tier throws transient 429s. One shouldn't kill an 8-min
    run, so retry with exponential backoff; on final failure return a sentinel
    the caller records but doesn't score."""
    for attempt in range(tries):
        try:
            return answer_fn(question, top_k=top_k).strip()
        except Exception as e:  # noqa: BLE001 - free-tier errors are opaque
            if attempt == tries - 1:
                return f"__ERROR__ {type(e).__name__}: {e}"
            time.sleep(10 * (2 ** attempt))  # 10s, 20s, 40s
    return "__ERROR__ unreachable"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen", action="store_true", help="also run generation checks")
    ap.add_argument("--top-k", type=int, default=5)
    ap.add_argument("--tag", default="run")
    ap.add_argument("--resume", action="store_true",
                    help="skip questions already in eval/results/<tag>.jsonl")
    args = ap.parse_args()

    rows = list(csv.DictReader(QUESTIONS.open()))
    answerable = [r for r in rows if r["answerable"] == "yes"]
    tricks = [r for r in rows if r["answerable"] == "no"]

    # ---------- retrieval ----------
    r1 = r5 = 0
    ans_best, trick_best = [], []
    retrieved: dict[str, list] = {}
    misses = []
    for row in rows:
        hits = search(row["question"], top_k=args.top_k)
        retrieved[row["id"]] = hits
        best = hits[0][0]
        if row["answerable"] == "yes":
            want = expected_pages(row["clause_ref"])
            got = [c["page"] for _, c in hits]
            r1 += bool(want & set(got[:1]))
            hit5 = bool(want & set(got))
            r5 += hit5
            ans_best.append(best)
            if not hit5:
                misses.append(row["id"])
        else:
            trick_best.append(best)

    n = len(answerable)
    print(f"== retrieval (top-{args.top_k}, {len(rows)} questions, tag={args.tag}) ==")
    print(f"recall@1 = {r1}/{n} = {r1/n:.2f}")
    print(f"recall@5 = {r5}/{n} = {r5/n:.2f}   misses: {', '.join(misses) or '-'}")
    print(f"separation: answerable best-scores min={min(ans_best):.3f}  "
          f"trick best-scores max={max(trick_best):.3f}  "
          f"({'SEPARATED' if min(ans_best) > max(trick_best) else 'OVERLAP - no clean threshold'})")

    md_row = (f"| {args.tag} | recall@1 {r1/n:.2f} | recall@5 {r5/n:.2f} | "
              f"sep {min(ans_best):.2f}/{max(trick_best):.2f} |")

    # ---------- generation (optional) ----------
    if args.gen:
        import llm  # noqa: E402  (deferred: needs a key)
        from answer import answer  # noqa: E402

        name, model = llm.provider()
        print(f"\n== generation ({name} {model}, {GEN_SLEEP_S}s pacing) ==")
        RESULTS_DIR.mkdir(exist_ok=True)
        out_path = RESULTS_DIR / f"{args.tag}.jsonl"

        done_ids: set[str] = set()
        if args.resume and out_path.exists():
            done_ids = {json.loads(l)["id"] for l in out_path.open()}
            print(f"resuming: {len(done_ids)} already done, skipping them")

        todo = [r for r in rows if r["id"] not in done_ids]
        mode = "a" if args.resume else "w"
        with out_path.open(mode) as f:
            for i, row in enumerate(todo):
                out = answer_with_retry(answer, row["question"], args.top_k)
                errored = out.startswith("__ERROR__")
                lead_refusal = (not errored) and out.lower().startswith(REFUSAL.lower())
                cite_pages = set() if errored else {int(p) for p in CITE.findall(out)}
                got_pages = {c["page"] for _, c in retrieved[row["id"]]}
                rec = {"id": row["id"], "question": row["question"], "answer": out,
                       "errored": errored, "lead_refusal": lead_refusal,
                       "cited_pages": sorted(cite_pages), "retrieved_pages": sorted(got_pages)}
                f.write(json.dumps(rec) + "\n")
                f.flush()  # survive a crash: keep every completed answer on disk
                if i < len(todo) - 1:
                    time.sleep(GEN_SLEEP_S)

        # Aggregate from the file so --resume runs score the full set.
        allrecs = {json.loads(l)["id"]: json.loads(l) for l in out_path.open()}
        cited = grounded = false_ref = refused = errored_n = 0
        for row in rows:
            r = allrecs.get(row["id"])
            if r is None:
                continue
            if r.get("errored"):
                errored_n += 1
                continue
            cp, gp = set(r["cited_pages"]), set(r["retrieved_pages"])
            if row["answerable"] == "yes":
                if r["lead_refusal"]:
                    false_ref += 1
                else:
                    cited += bool(cp)
                    grounded += bool(cp) and cp <= gp
            else:
                refused += r["lead_refusal"]

        print(f"answerable ({n}): cited={cited}  grounded={grounded}  false-refusals={false_ref}")
        print(f"tricks ({len(tricks)}): correctly refused={refused}/{len(tricks)}")
        if errored_n:
            print(f"ERRORED (free-tier, not scored): {errored_n} — re-run with --resume")
        print(f"per-question outputs -> {out_path}")
        md_row = md_row[:-1] + (f" cited {cited}/{n} | grounded {grounded}/{n} | "
                                f"false-ref {false_ref} | trick-refuse {refused}/{len(tricks)} |")

    print("\nEXPERIMENTS.md row:")
    print(md_row)


if __name__ == "__main__":
    main()
