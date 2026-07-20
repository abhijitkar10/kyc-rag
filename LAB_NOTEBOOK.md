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
