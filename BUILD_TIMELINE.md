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
