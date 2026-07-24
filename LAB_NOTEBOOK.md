# Lab Notebook

One entry per work session / experiment. Template:

```
## YYYY-MM-DD — <what>
Changed: <one thing>
Expected: <prediction before running>
Result: <numbers / what happened>
Lesson: <one sentence>
```

---

## 2026-07-20 — Project start (Phase 0)
Changed: created repo, folder structure, venv (Python 3.13).
Expected: —
Result: scaffolding in place; next: download corpus + read + write 20 Q&A pairs.
Lesson: —

## 2026-07-20 — Corpus acquired + reading materials built
Changed: downloaded consolidated KYC Master Direction (updated Aug 14, 2025; 107pp) from rbi.org.in; verified Sections 16/17/18 locations; extracted amendment-circular links from the PDF's own footnote hyperlinks; wrote READING_GUIDE.md + eval/QUESTION_GUIDE.md.
Expected: —
Result: data/raw/ has the authoritative corpus. Separate amendment PDFs blocked by RBI's bot-protection (F5/TSPD JS challenge) — manual browser download deferred to Phase 4; links recorded in READING_GUIDE.md.
Lesson: real-world data acquisition has friction (bot walls, mirrors serving HTML); the consolidated doc + footnotes already contain the full amendment history.

## 2026-07-20 — Build timeline + question worksheet
Changed: added BUILD_TIMELINE.md (milestone history, honest AI-attribution note) and eval/QUESTION_WORKSHEET.md (20 designed question stems with exact page/section pointers; final phrasing + own-words answers to be completed against the PDF).
Expected: worksheet reduces question-writing from ~3 evenings of open reading to ~2 focused hours of targeted clause reading.
Result: Phase 0 remaining work = complete questions.csv from the worksheet.
Lesson: keep eval ground truth human-verified even when AI designs the question stems.

## 2026-07-20 — Eval set v1 complete (20 questions)
Changed: filled questions.csv with all 20 rows (6 direct, 6 paraphrased, 3 numeric, 2 amendment-aware, 3 trick). Answers verified against PDF pages 7-14, 24-27, 38-52 during writing.
Expected: paraphrased rows (7-12) should be the hardest for keyword-only retrieval; trick rows (18-20) should tempt a naive system.
Result: v1 ground truth in place. Independent verification pass = onboarding Step 2.
Lesson: retention rules have TWO different clocks (transaction date vs relationship end) — exactly the subtlety that makes a good eval question.

## 2026-07-20 — Phase 1: walking skeleton + BASELINE
Changed: built the full pipeline (extract 107pp -> 431 naive 800-char chunks -> bge-small-en-v1.5 embeddings -> hand-written cosine top-5 -> Haiku answer w/ strict cite-or-refuse prompt). Ran retrieval-only baseline over all 20 eval questions.
Expected: mediocre recall; paraphrase questions worst.
Result: **recall@5 = 12/17 = 0.71 (BASELINE, exp 0)**. Misses: Q2 (Para 16 reqs), Q3 (V-CIP scope), Q8 (driving licence paraphrase), Q11 (DigiLocker paraphrase), Q17 (amendment footnote). Trick best-scores 0.573/0.702/0.677 vs answerable best-scores 0.655–0.835 → ranges OVERLAP, so a naive refusal threshold can't cleanly separate yet (threshold 0.71 would wrongly refuse Q7 & Q11).
Lesson: 2 of 5 misses are paraphrase rows as predicted; and cosine scores from bge-small are bunched (0.57–0.84) — separating real from trick questions needs better retrieval (Phase 3) before a threshold (Phase 4) can work.
Note: answer.py/ask.py written but untested — no ANTHROPIC_API_KEY on this machine yet.

## 2026-07-20 — Provider-flexible LLM (Gemini free tier, Claude fallback)
Changed: added src/llm.py — one complete(system,user) interface that auto-selects Gemini (GEMINI_API_KEY, free tier) or Claude (ANTHROPIC_API_KEY), plus a dependency-free .env loader. Rewired answer.py through it. Added eval/generation_smoke.py (checks answerable->cites a page, trick->refuses). Installed google-genai.
Expected: switching provider changes nothing upstream (retrieval untouched) — the generator is a commodity behind an interface.
Result: imports + no-key error path verified. Generation NOT yet run end-to-end — waiting on a free Gemini key in .env (key creation needs a Google login, done by the project owner).
Lesson: making the generator vendor-swappable is a clean architecture point AND unblocks a free provider for a student — cost and design win at once.

## 2026-07-20 — First end-to-end generation run (Gemini 2.5-flash free tier)
Changed: ran the full pipeline (retrieval -> Gemini) on 4 representative questions; investigated every non-pass instead of accepting the labels.
Expected: answerable -> cited answer; trick -> refuse.
Result: after fixing a smoke-test bug, **3/4 behavioural checks pass**. Findings:
  1. Generation works on the free tier; citations render in the exact required format [KYC Master Direction, p.N].
  2. FAITHFULNESS CONFIRMED under adversarial retrieval: for the 3-limits question, the retrieved context contained tempting-but-WRONG "one lakh" figures (Small Accounts p.32; another account type p.34) but NOT the OTP e-KYC balance cap (para 17iii, p.26). The model gave the 2 supported limits with citations and honestly said the 3rd was "not found" — it refused to grab the wrong number. The strict-grounding prompt works.
  3. NON-DETERMINISM: an earlier run hallucinated that 3rd limit with a fabricated "p.26" cite; later runs (deterministic 3x) correctly refused it. Gemini free tier isn't fully deterministic even at temperature=0 -> motivates a Phase 4 citation-verification post-check (assert cited page is in the retrieved set).
  4. RECURRING STRUCTURAL ISSUE: right PAGE retrieved != answer-bearing CHUNK retrieved (seen on both the video-call Q and the balance-cap Q). Naive 800-char chunking splits a clause (e.g. para 18 heading) from its body -> Phase 3 clause-aware chunking + hybrid. Also means page-level recall@5 is OPTIMISTIC; chunk/phrase-level grading would be stricter.
  5. Video-call question fails end-to-end: retrieval returns V-CIP *conditions* (p.30/33) not the "V-CIP may be used for onboarding" opening (para 18, p.27) -> correct refusal, real recall gap.
Fixed: smoke-test refusal detector was a substring match (flagged partial answers containing the phrase mid-text as full refusals); changed to startswith so a leading refusal counts, a mid-answer "not found for sub-point" does not.
Lesson: separating retrieval-eval from generation-eval paid off immediately — it let me tell "retrieval missed" apart from "generator refused" apart from "generator hallucinated," three different fixes. The most reassuring result is the model declining a plausible wrong number.

## 2026-07-23 — Phase 2: eval harness + 50-question set (v2)
Changed: expanded eval to 50 questions (44 answerable / 6 trick) with whole-document coverage — added Q21-47 across Customer Acceptance (Ch III), Risk Mgmt (Ch IV), CIP (Ch V), Small Accounts (para 23), sole-prop/company/partnership/trust CDD (paras 27-33), V-CIP infra/procedure (para 18a-c), periodic-updation mechanics (para 38) — plus 3 new trick questions (mutual funds/SEBI-KRA, crypto/VDA, min-balance). All answers verified against PDF pages 15-37 read this session. Built eval/run_eval.py: one command, unified scorecard (recall@1, recall@5, separation, + optional --gen behavioural checks: cited/grounded/false-refusal/trick-refusal) writing per-question outputs to eval/results/<tag>.jsonl for manual faithfulness spot-checks. Created EXPERIMENTS.md (living table).
Expected: aggregate recall shifts (different set); the many well-posed direct questions should mostly hit.
Result: **v2 retrieval re-baseline: recall@1 = 0.61, recall@5 = 0.82** (36/44). Misses Q2,3,8,11,17,23,26,46. Separation still OVERLAP (ans-min 0.655 / trick-max 0.751). NOTE: v1 (0.71) and v2 (0.82) are NOT comparable — v2 is the real baseline going forward.
Key read: recall@1 (0.61) << recall@5 (0.82) → answer chunk usually retrieved but rarely rank-1 → a cross-encoder reranker (Phase 3.4) is the highest-leverage fix. The 8 misses cluster into paraphrase / amendment-footnote / clause-split — exactly the Phase-3 targets.
Also: hardened run_eval.py against free-tier 429s (retry w/ exponential backoff 10/20/40s; per-answer flush so a crash keeps progress; --resume to continue) — the first background gen run had died on a transient 429 after 1 question and lost everything.
Lesson: a bigger eval set changes the numbers but not the diagnosis; and an eval harness that talks to a rate-limited free API must be crash-resilient and resumable, or you lose an 8-minute run to one blip.

## 2026-07-23 — Free-tier daily quota exhausted (generation eval deferred)
Changed: ran the hardened 50-question generation eval; investigated the outcome.
Expected: full cited/grounded/refusal numbers on all 50.
Result: all 50 returned 429 RESOURCE_EXHAUSTED ("exceeded your current quota"). A fresh single call also 429s, and gemini-2.0-flash-lite 429s too -> the free-tier daily quota is PROJECT-LEVEL and exhausted for today (a day of testing: smoke x3 + diagnostics + a crashed run + 50x up-to-4 retries). Resets in ~24h. The hardening WORKED: the run completed cleanly and wrote all 50 records (each errored) instead of crashing and losing progress.
Fixed: --resume now keeps only SUCCESSFUL prior answers and re-attempts errored/missing rows, rewriting the file in question order (no duplicate ids). So after reset: `python eval/run_eval.py --gen --tag exp0b-gen --resume` finishes just the failures.
Not blocked: retrieval eval needs NO LLM and is exactly what Phase 3 optimizes (recall@k via BM25/hybrid/chunking/rerank). Generation grounding numbers are a periodic nice-to-have; faithfulness was already demonstrated on the Phase-1 smoke run.
Lesson: budget free-tier request-per-day quota like a scarce resource — don't spend it on iterative debugging you can do with retrieval-only eval. Design the harness so a full quota-blocked run is recoverable (it is now).

## 2026-07-23 — Exp 3.1: BM25 from scratch (alone)
Changed: wrote src/bm25.py (Okapi BM25 from scratch — inverted index, IDF, k1=1.5/b=0.75, no library) + src/retrievers.py (swappable retriever seam) + run_eval.py --retriever flag. Dense regression re-checked = 0.82 (unchanged).
Expected: BM25 strong on exact-keyword Qs (circular numbers, "DigiLocker"), weak on pure-semantic Qs (video↔V-CIP).
Result: **recall@1 0.59, recall@5 0.84** (37/44). BM25 misses {3,7,23,26,27,46,47}; dense misses {2,3,8,11,17,23,26,46}. COMPLEMENTARY: BM25 catches dense's 2/8/11/17 (exact keywords incl. amendment circular #s), dense catches BM25's 7/27/47 (7 = "video call" vs text "V-CIP", pure semantic). Both miss only {3,23,26,46} → union ceiling = 40/44 = 0.91.
Lesson: my Phase-1 guess that paraphrase Qs (8 driving-licence, 11 DigiLocker) were "semantic" was half wrong — they contain the exact keyword too, so BM25 nails them. The genuinely semantic-only miss is Q7. This complementarity is the empirical case FOR hybrid (3.2).

## 2026-07-23 — Exp 3.2: Hybrid (dense + BM25 via RRF)
Changed: added hybrid retriever to retrievers.py — Reciprocal Rank Fusion, k=60, pool=30 from each retriever, fuse on chunk id. Uses rank position only (cosine 0-1 and BM25 0-15 scales never mixed).
Expected: approach the 0.91 union ceiling from 3.1.
Result: **recall@1 0.73, recall@5 0.91** (40/44) — biggest single jump so far (dense 0.82→0.91, recall@1 0.61→0.73). Misses {3,7,17,23}, NOT the naive union {3,23,26,46}. Nuance: RRF RECOVERED both-miss {26,46} (each present in both top-30 lists → fusion lifted them into top-5) but DROPPED {7,17} which were single-retriever-STRONG (Q7 dense-only rank-high, Q17 BM25-only rank-high) — consensus reward diluted them below top-5.
Lesson: RRF trades single-retriever peaks for cross-retriever consensus. Net win (+ recall@1 especially), but it can drop items only ONE retriever finds well — those {7,17} are prime targets for a cross-encoder reranker (3.4) that reads query+chunk jointly. Standard k=60/pool=30 left untuned (one change at a time).

## 2026-07-23 — Exp 3.3: Clause-aware chunking (NEGATIVE RESULT, reverted)
Changed: wrote src/chunk_clause.py — split on top-level paragraph markers ("16.", "46A."), prefix chunks with [Para N], pack long clauses into <=1000c line-packed windows (page = first line's page). Re-chunked (431→539) + re-embedded, evaluated dense and hybrid.
Expected: keeping clause heading with body fixes "right page wrong chunk" → recall UP.
Result: recall@5 DOWN — dense 0.82→0.77, hybrid 0.91→0.82. (dense recall@1 UP 0.61→0.68: focused chunks rank better WHEN found.) New hybrid misses {2,8,12,42,46} all live inside the LONGEST clauses (para 3 definitions, 16, 18 V-CIP, 38). Cause: my chunker windows long clauses with NO overlap and an identical "[Para N]" prefix, so those windows embed similarly and the answer-bearing window gets diluted/out-ranked. Short clauses were unaffected.
Decision: REVERTED to naive 800/200 chunks (re-ran chunk.py + embed.py); confirmed hybrid back at 0.91. chunk_clause.py kept in repo as a documented experiment.
Lesson: naive fixed-size chunks have TWO hidden advantages I under-valued — the 200-char OVERLAP gives answer-bearing text two chances to be retrieved, and uniform size avoids the long-clause dilution. Structure-aware chunking only wins if it ALSO keeps overlap and splits long clauses at sub-clause ((a)/(i)) boundaries rather than blind windows. Measuring caught a change a tutorial would have shipped as an "obvious" improvement.

## 2026-07-23 — Exp 3.4a: Cross-encoder rerank, ms-marco-MiniLM (NEGATIVE)
Changed: added "rerank" retriever — hybrid top-20 pool re-scored by cross-encoder/ms-marco-MiniLM-L-6-v2 (joint query+chunk scoring), keep top-5.
Expected: recover the single-retriever-strong misses {7,17} → beat hybrid 0.91.
Result: REGRESSED — recall@1 0.73→0.66, recall@5 0.91→0.84. Misses grew to {3,7,8,12,17,23,26}. The CE gave several answerable questions strongly negative scores (min -5.76). Likely cause: naive 800-char chunks start/end mid-sentence, so the CE (trained on clean MS-MARCO web passages) sees fragmented, out-of-distribution text and ranks erratically; it also fully REPLACES the good hybrid ordering, so a noisy CE actively hurts.
Next: try a stronger, domain-robust reranker (BAAI/bge-reranker-base) before concluding reranking doesn't help here (exp 3.4b, running).
Lesson: a reranker is only as good as (a) its domain fit and (b) the cleanliness of the chunks it reads. Fragmented chunks + web-trained CE = worse than no rerank. Reranking and chunking are coupled.

## 2026-07-23 — Exp 3.4b: BGE reranker (WINNER) + wire-up
Changed: ran rerank with RERANK_MODEL=BAAI/bge-reranker-base (hybrid top-20 → CE re-score → top-5). Then made it the default rerank model; wired answer.py/ask.py to get_retriever(RETRIEVER env, default "hybrid").
Expected: a stronger reranker overcomes the fragmented-chunk problem that sank ms-marco.
Result: **recall@1 0.77, recall@5 0.93 — best config.** Recovered Q17 (the amendment Q that RRF had diluted); misses now {3,7,23}. Same rerank pipeline as ms-marco but +0.09 vs -0.07 → the MODEL was the whole difference. Separation still overlaps: BGE gives some tricks high relevance (max 0.851) while some answerable score 0.020 — the reranker score alone can't gate refusal (Phase 4 must combine signals).
Decision: pipeline default retriever = hybrid (0.91, fast, no 1.1GB model — good for the friend's laptop); RETRIEVER=rerank for peak 0.93 (demo/eval). Both wired and documented.
Lesson: "add a reranker" is not a monolith — ms-marco HURT, BGE HELPED, same code. The component choice within a technique matters as much as the technique. And a reranker's relevance score is NOT a refusal signal (tricks can score high). Phase 3 overall: 0.82→0.93 recall@5, 0.61→0.77 recall@1, with two honest negative results.
