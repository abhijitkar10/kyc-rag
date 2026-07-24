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

**Read of exp0b:** recall@1 (0.61) << recall@5 (0.82) — the right chunk is usually retrieved but
often not rank-1 → a reranker (Phase 3.4) should help most. 8 misses (Q2,3,8,11,17,23,26,46) are
the Phase-3 targets: paraphrases (8,11,46), amendment footnote (17), and clause-split cases
(2,3,23,26). Separation still overlaps → refusal threshold stays a Phase-4 item, unblocked only
after retrieval improves.

Planned (Phase 3, one change at a time): BM25-alone → hybrid RRF → clause-aware chunking →
cross-encoder rerank. Phase 4 threshold work only starts once separation exists.
