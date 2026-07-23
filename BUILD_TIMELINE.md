# Build Timeline

Milestone-level history of how this project was built, in order. (Experiment-level detail
lives in `LAB_NOTEBOOK.md`.) Maintained every session — this is the "story of the build"
for the README and interviews.

> Working style, stated honestly: built with an AI mentor (Claude) as pair-programmer and
> teacher. Design decisions, document reading, clause verification, and eval ground truth
> are mine; scaffolding, boilerplate, and concept explanations were AI-assisted.
> This is the accurate narration and the interview-safe one.

---

## 2026-07-20 — Day 1: plan → repo → corpus → reading materials

1. **Chose the project** after comparing alternatives (mini search engine, reconciliation
   engine, fraud detection). Rationale: fintech-relevant domain, free public data,
   hard parts with business justification (citations, refusal, versioning).
2. **Wrote the master plan** (Karpathy-style: walking skeleton first, eval before
   improvements, one change at a time, BM25 from scratch, no LangChain).
   Lives in the vault: `05 Career/RAG Project — Master Plan.md`.
3. **Scaffolded the repo**: folder structure, Python 3.13 venv, git, lab notebook,
   eval CSV template. First commit.
4. **Acquired the corpus**: consolidated RBI KYC Master Direction (updated Aug 14 2025,
   107 pages) from rbi.org.in. Verified key sections by reading pages 1–6 and 24–27
   (Sec 16 = CDD documents, Sec 17 = OTP e-KYC limits, Sec 18 = V-CIP).
   Discovered the amendment footnotes — each changed clause names its amending circular →
   this becomes the Phase 4 versioning mechanism.
5. **Hit a real-world wall**: RBI's document server (rbidocs) bot-blocks scripted
   downloads (F5/TSPD JS challenge); third-party mirrors served HTML block pages.
   Resolution: consolidated PDF already contains all amendments; separate circular PDFs
   deferred to Phase 4 as a manual browser download (links extracted from the PDF's own
   footnote hyperlinks).
6. **Built reading materials**: `READING_GUIDE.md` (chapter-by-chapter priority map with
   verified page numbers) and `eval/QUESTION_GUIDE.md` (recipe for the 20-question eval set).
7. **Built the question worksheet**: `eval/QUESTION_WORKSHEET.md` — 20 designed question
   stems, each pointing at an exact page/section; final phrasing + own-words answers to be
   completed against the PDF (keeps eval ground truth human-verified).

**Next milestone:** complete `questions.csv` from the worksheet → Phase 0 done → Phase 1
(walking skeleton: extract → chunk → embed → search → answer).

## 2026-07-20 — Day 1 (continued): eval set completed, project handoff clarified

8. **Clarified who this is for**: the project is being built for a friend (the interview
   candidate). Division of labor updated — AI/user complete the build; the friend follows
   `FRIEND_ONBOARDING.md` to verify, internalize, and own it.
9. **Completed the 20-question eval set** (`eval/questions.csv`): every answer written
   against the PDF after reading the relevant pages (definitions p.7–14, CDD p.24–27,
   ongoing DD/EDD/records/reporting p.38–52). All clause refs carry page numbers.
   Verification pass by the project owner is Step 2 of onboarding — that re-establishes
   human-verified ground truth and doubles as the domain reading.
10. **Wrote `FRIEND_ONBOARDING.md`**: the make-it-yours path — understand, verify, self-test,
   run all experiments personally, rehearse with mock questions.

**Phase 0: complete.** Next: Phase 1 walking skeleton (extract → chunk → embed → search → answer).

## 2026-07-20 — Day 1 (continued): Phase 1 walking skeleton + baseline

11. **Built the six-script pipeline** (`src/`): extract.py (pypdf, page-tagged text),
    chunk.py (naive 800/200 windows, 431 chunks), embed.py (bge-small, 384-dim, ~6s),
    search.py (hand-written cosine: one dot product + argsort), answer.py (Haiku 4.5,
    cite-or-refuse system prompt), ask.py (CLI). Plus eval/baseline_retrieval.py
    (page-match grading against questions.csv).
12. **Baseline established: recall@5 = 0.71** (12/17 answerable). Misses concentrated in
    paraphrase questions and the amendment-footnote question — the exact weaknesses
    Phase 3 experiments (BM25, hybrid, clause chunking, rerank) are designed to attack.
    Key finding: trick-question scores overlap answerable scores → no clean refusal
    threshold exists yet at baseline.

**Phase 1: complete** (generation path pending an ANTHROPIC_API_KEY for live test).
Next: Phase 2 (formalize eval harness) then Phase 3 experiments.

## 2026-07-20 — Day 1 (continued): LLM made provider-flexible (Gemini free tier)

13. **Switched the generator to Gemini's free tier** (Claude kept as fallback) to avoid
    needing a payment card. Refactored the generator into `src/llm.py` — a single
    `complete()` interface that auto-selects provider by which API key is present, with a
    dependency-free `.env` loader. `answer.py` now calls it; retrieval is untouched.
    Added `eval/generation_smoke.py` (answerable -> must cite a page; trick -> must refuse).
    Phase 5's model comparison is now Gemini-vs-Claude.
    Blocked on generation testing only by key creation (Google login = owner's step).

## 2026-07-20 — Day 1 (continued): first end-to-end generation run (Gemini free tier)

14. **Ran the full pipeline live on Gemini 2.5-flash (free tier)** and investigated every
    non-pass rather than trusting the labels. Confirmed the generator is faithful — under a
    question where the retrieved context held tempting-but-wrong "one lakh" figures (Small
    Accounts, other account types) it declined to use them and honestly flagged the one
    unsupported sub-point. Also observed free-tier non-determinism (one earlier run
    hallucinated a fabricated page cite) — motivating a Phase 4 citation-verification check.
    Surfaced the recurring "right page, wrong chunk" weakness of naive chunking (Phase 3
    target) and fixed a real bug in the smoke test's refusal detector. 3/4 behavioural
    checks pass; the one fail is a genuine retrieval miss.
