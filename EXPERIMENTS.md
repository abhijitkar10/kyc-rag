# Experiment Table (living document)

Every retrieval/generation change gets one row, produced by `eval/run_eval.py --tag <name>`.
Full context for each run is in `LAB_NOTEBOOK.md`.

**Eval set versions:** v1 = 20 questions (17 answerable / 3 trick), v2 = 50 questions
(44 answerable / 6 trick, whole-document coverage). **Numbers across eval versions are
NOT comparable** — v2 re-baselines everything.

| tag | eval set | recall@1 | recall@5 | separation (ans-min / trick-max) | generation notes |
|---|---|---|---|---|---|
| exp0-baseline | v1 (20q) | — | 0.71 | 0.66 / 0.70 — overlap | smoke only: faithful refusal confirmed; 1 free-tier hallucination observed |
| **exp0b-rebaseline** | **v2 (50q)** | **0.61** | **0.82** | **0.655 / 0.751 — overlap** | dense baseline. gen 50-q run blocked: Gemini free-tier **daily** quota (429); `--resume` after reset. |
| exp1-bm25 | v2 (50q) | 0.59 | **0.84** | 11.2 / 14.1 — overlap | BM25 from scratch, ALONE. Misses {3,7,23,26,27,46,47} vs dense {2,3,8,11,17,23,26,46}: complementary — BM25 wins exact-keyword Qs (DigiLocker, circular #s), dense wins semantic Q7 (video↔V-CIP). Both miss only {3,23,26,46} → **hybrid ceiling 0.91**. |
| exp2-hybrid | v2 (50q) | **0.73** | **0.91** | 0.029 / 0.032 — overlap | dense+BM25 via RRF (k=60, pool=30). Hit the 0.91 ceiling; recall@1 jumped 0.61→0.73. Misses {3,7,17,23}: RRF's consensus-reward RECOVERED both-miss {26,46} but DROPPED single-retriever-strong {7,17} (Q7 dense-only, Q17 BM25-only) — rerank (3.4) should recover these. |
| exp3-clause-dense | v2 (50q) | 0.68 | 0.77 ↓ | 0.62 / 0.75 — overlap | clause-aware chunks (539, avg 436c). **NEGATIVE** — recall@5 down from 0.82. recall@1 up (focused chunks rank better *when found*). |
| exp3-clause-hybrid | v2 (50q) | 0.64 | 0.82 ↓ | overlap | **NEGATIVE, REVERTED.** Hybrid dropped 0.91→0.82. New misses all in LONG clauses (para 3/16/18/38): my chunker windows long clauses with NO overlap + identical `[Para X]` prefix → windows embed alike, answer-bearing one diluted. Kept naive chunks. Future work: overlap + sub-clause ((a)/(i)) splitting. |
| exp4-rerank (ms-marco) | v2 (50q) | 0.66 ↓ | 0.84 ↓ | -5.76 / 3.64 — overlap | **NEGATIVE.** cross-encoder/ms-marco-MiniLM-L-6-v2 over hybrid top-20. Regressed below hybrid 0.91. Naive chunks start/end mid-sentence (fragmented, out-of-distribution for a web-passage-trained reranker); some answerable Qs scored -5.8. |
| **exp4b-rerank (BGE)** ⭐ | v2 (50q) | **0.77** | **0.93** | 0.02 / 0.85 — overlap | **WINNER.** BAAI/bge-reranker-base over hybrid top-20. Best on both metrics; recovered Q17. Same technique as ms-marco, but a stronger domain-fit model → +0.09 instead of -0.07. Misses {3,7,23}. Trick scores still overlap (a trick can look "relevant" to the reranker) → Phase-4 threshold must not rely on rerank score alone. |

**Phase 3 result: recall@5 0.82 → 0.93, recall@1 0.61 → 0.77.** Pipeline default = `hybrid` (fast, 0.91, no 1.1GB model); `RETRIEVER=rerank` for the peak 0.93. Two negative results (clause chunking, ms-marco rerank) documented. Remaining hard misses {3,7,23} and the still-overlapping trick separation carry into Phase 4.

## Phase 4 — safety layer

Code complete + unit-tested (retrieval-graded, quota-free):
- **Citation guardrail** (`src/verify.py`, 7/7 tests): flags cited pages not in the retrieved set.
- **Versioning** (`src/amendments.py`): 14-circular amendment timeline from footnotes.
- **Refusal by design**: no score threshold (measured overlap on every retriever); enforced at generation + citation check.

Generation behavioural numbers (cited / grounded / false-refusal / trick-refusal on the 50-q set)
are **deferred** — the free-tier daily quota only covers ~20 clean calls/day. Complete with:
`python eval/run_eval.py --gen --retriever hybrid --tag exp5-safety --resume` across days, or a paid key.
Harness bug fixed en route: generation + grounding now use the SAME retriever.

**Read of exp0b:** recall@1 (0.61) << recall@5 (0.82) — the right chunk is usually retrieved but
often not rank-1 → a reranker (Phase 3.4) should help most. 8 misses (Q2,3,8,11,17,23,26,46) are
the Phase-3 targets: paraphrases (8,11,46), amendment footnote (17), and clause-split cases
(2,3,23,26). Separation still overlaps → refusal threshold stays a Phase-4 item, unblocked only
after retrieval improves.

Planned (Phase 3, one change at a time): BM25-alone → hybrid RRF → clause-aware chunking →
cross-encoder rerank. Phase 4 threshold work only starts once separation exists.

## Phase 4 results — generation & safety (exp6, hybrid retriever, 2026-08-26)

Free-tier daily quota (~20 calls/day) capped the run at **21/50 clean answers** (18 answerable,
3 trick). Complete the rest with `./run.sh eval-gen --resume`. What the 21 show:

| Metric | Result |
|---|---|
| Citations grounded (cited page ∈ retrieved pages) | **14 / 14 — zero hallucinated citations** |
| Answerable questions answered with a citation | 14 / 18 |
| Out-of-corpus (trick) questions refused | **3 / 3** (Q48–50 not yet reached) |
| False refusals | 4 / 18 — **3 of which were retrieval misses (correct behaviour)** |

**Key finding — the system fails safe.** 3 of the 4 false refusals (Q3, Q7, Q17) happened because
retrieval never surfaced the right page, so the model refused instead of inventing an answer. Only
Q16 was a true false refusal (right page retrieved, model still refused — it's the footnote-based
amendment question). Refusing on a retrieval miss is the desired failure mode in compliance.
