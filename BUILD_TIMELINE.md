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

## 2026-07-23 — Day 2: Phase 2 eval harness + 50-question set

15. **Expanded the eval set 20 -> 50 questions** (44 answerable / 6 trick) for whole-document
    coverage — read PDF pages 15-37 to write and verify Q21-47 across Customer Acceptance,
    Risk Management, CIP, Small Accounts, entity CDD (sole-prop/company/partnership/trust),
    V-CIP infrastructure/procedure, and periodic-updation mechanics; 3 new trick questions.
16. **Built the unified eval harness** `eval/run_eval.py` — one command → one scorecard
    (recall@1, recall@5, answerable/trick score separation; `--gen` adds behavioural checks:
    cited / grounded / false-refusal / trick-refusal). Per-question outputs saved for manual
    faithfulness spot-checks. Added `EXPERIMENTS.md` living table.
17. **Retrieval re-baseline on v2: recall@1 = 0.61, recall@5 = 0.82** (36/44). Key read:
    recall@1 << recall@5 → the answer chunk is usually retrieved but rarely rank-1, so a
    reranker is the highest-leverage Phase-3 fix. Separation still overlaps.
18. **Hardened the harness against free-tier rate limits** — the first background generation
    run died on a transient 429 after one question and lost all progress; added retry with
    exponential backoff, per-answer flush-to-disk, and `--resume`.

## 2026-07-23 — Day 2 (continued): Phase 3 retrieval experiments (the heart)

19. **Built a swappable-retriever seam** (`src/retrievers.py`, `run_eval.py --retriever`) so
    every retrieval idea is a one-flag A/B, graded with NO LLM (quota-independent).
20. **3.1 BM25 from scratch** (`src/bm25.py`, no library): recall@5 0.84. Found it
    COMPLEMENTARY to dense (each catches the other's misses) → union ceiling 0.91.
21. **3.2 Hybrid via RRF**: recall@5 **0.91**, recall@1 0.61→0.73 — biggest win. Documented
    RRF's consensus trade-off (recovered both-miss items, dropped single-retriever-strong ones).
22. **3.3 Clause-aware chunking: NEGATIVE, reverted** — regressed to 0.82 because long clauses
    were windowed without overlap + identical prefixes → within-clause dilution. Measured, reverted.
23. **3.4a ms-marco reranker: NEGATIVE** — regressed to 0.84 (fragmented chunks are OOD for a
    web-trained CE). **3.4b BGE reranker: WINNER** — recall@5 **0.93**, recall@1 **0.77**. Same
    pipeline, stronger model → +0.09 vs -0.07. Wired answer/ask to a configurable retriever
    (default hybrid for speed; RETRIEVER=rerank for peak).

**Phase 3: complete. recall@5 0.82 → 0.93, recall@1 0.61 → 0.77, plus two documented negative results.**
Next: Phase 4 (mandatory citations, refusal threshold — separation still overlaps —, versioning).

## 2026-07-23 — Day 2 (continued): Phase 4 safety layer

24. **Citation guardrail** (`src/verify.py`, wired into `answer()`, 7/7 unit tests): flags any
    cited page not in the retrieved set — catches the hallucinated-citation failure from Phase 1.
25. **Versioning** (`src/amendments.py`): parses footnotes into a 14-circular amendment timeline —
    provenance without the bot-blocked circular PDFs.
26. **Refusal by design, not by threshold**: since answerable/trick retrieval scores were measured
    to overlap on every retriever, refusal is enforced at generation (strict grounding) + validated
    by the citation check — an evidence-driven choice.
27. **Fixed an eval-harness bug**: grounding was graded against dense pages while answers were
    generated from hybrid; the harness now generates and grades with the same retriever.

**Phase 4: safety CODE complete + unit-tested.** Generation behavioural numbers deferred — free-tier
daily quota (~20 clean calls/day) needs a multi-day `--resume` or a paid key; faithfulness already
shown by the smoke test. Next: Phase 5 (thin API + web UI, cost/latency, README, interview pack).
