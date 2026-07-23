# Experiment Table (living document)

Every retrieval/generation change gets one row, produced by `eval/run_eval.py --tag <name>`.
Full context for each run is in `LAB_NOTEBOOK.md`.

**Eval set versions:** v1 = 20 questions (17 answerable / 3 trick), v2 = 50 questions
(44 answerable / 6 trick, whole-document coverage). **Numbers across eval versions are
NOT comparable** — v2 re-baselines everything.

| tag | eval set | recall@1 | recall@5 | separation (ans-min / trick-max) | generation notes |
|---|---|---|---|---|---|
| exp0-baseline | v1 (20q) | — | 0.71 | 0.66 / 0.70 — overlap | smoke only: faithful refusal confirmed; 1 free-tier hallucination observed |
| exp0b-rebaseline | v2 (50q) | *(run pending)* | | | |

Planned (Phase 3, one change at a time): BM25-alone → hybrid RRF → clause-aware chunking →
cross-encoder rerank. Phase 4 threshold work only starts once separation exists.
