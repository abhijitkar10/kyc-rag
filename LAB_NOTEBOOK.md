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
