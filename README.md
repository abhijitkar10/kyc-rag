# RBI KYC Compliance Assistant

A retrieval-augmented question-answering system over the **RBI Master Direction on KYC**
(2025 consolidated, 107 pages). It answers compliance questions with **clause-level
citations**, **refuses when the answer isn't in the corpus**, and knows the document's
**amendment history** — the three things a real compliance tool needs and a demo bot doesn't.

Built as a from-scratch systems project: **no LangChain/LlamaIndex**, BM25 and vector search
implemented by hand, every improvement measured against a held-out eval set.

---

## Quick start (one command)

Everything runs through `run.sh` — it creates the virtualenv, installs deps, and builds the
index automatically the first time.

```bash
./run.sh setup            # one-time: venv + deps + build index
./run.sh all              # tests + retrieval scorecard + amendments + a sample answer

./run.sh ask "How long must banks keep KYC records?"   # CLI
./run.sh web              # web UI at http://127.0.0.1:8000
./run.sh eval             # retrieval scorecard (no API key needed)
./run.sh test             # citation-guardrail unit tests
./run.sh                  # list all commands
```

Answering needs a **free** key (retrieval/eval/tests don't): get one at
https://aistudio.google.com/apikey, then `cp .env.example .env` and paste it in.

---

## Why this problem

Every RBI-regulated entity (banks, NBFCs, payment companies) must follow the KYC Master
Direction; getting it wrong means fines or onboarding bans. The rulebook is long, dense, and
amended constantly. "Which ID documents are valid?" or "can we open an account over video?"
means digging through 100+ pages — work compliance teams pay real money for. A wrong answer is
worse than none, so citations and honest refusals are the product, not decoration.

## What it does

```
$ python src/ask.py "Can I open a bank account over a video call?"
Yes — through the Video-based Customer Identification Process (V-CIP), a live,
informed-consent audio-visual interaction with an authorised official of the RE,
treated on par with face-to-face verification [KYC Master Direction, p.27].

$ python src/ask.py "What are the tax benefits under Section 80C?"
Not found in the provided documents.
```

## Architecture

```
question ─▶ RETRIEVAL (the hard part)                        ─▶ GENERATION ─▶ GUARDRAIL
            ├─ dense: BGE-small embeddings + hand-written        LLM answers    citation
            │         cosine top-k                               ONLY from      check:
            ├─ BM25:  from scratch (inverted index, IDF)         retrieved      every cited
            └─ hybrid: Reciprocal Rank Fusion                    chunks, must   page must be
               (+ optional BGE cross-encoder rerank)             cite [p.N]     in retrieved set
```

The generator is a **swappable commodity** behind a one-function interface (`src/llm.py`):
Gemini free tier by default, Claude as a drop-in fallback. All the engineering is in retrieval.

## Results — retrieval, measured one change at a time

Held-out eval set of **50 questions** (44 answerable across the whole document + 6 out-of-corpus
"trick" questions), every answer verified against the PDF by hand. Metric: **recall@5** (did a
top-5 chunk come from the clause's page?).

| Retriever | recall@1 | recall@5 | note |
|---|---|---|---|
| dense (baseline) | 0.61 | 0.82 | BGE-small embeddings + cosine |
| BM25 from scratch | 0.59 | 0.84 | complementary to dense |
| **hybrid (RRF)** | 0.73 | **0.91** | biggest single win |
| + clause-aware chunking | 0.64 | 0.82 | ❌ **negative result, reverted** |
| + ms-marco reranker | 0.66 | 0.84 | ❌ negative (fragmented chunks OOD) |
| **+ BGE reranker** ⭐ | **0.77** | **0.93** | winner; same technique, stronger model |

**recall@5: 0.82 → 0.93. recall@1: 0.61 → 0.77.** Full experiment log in `EXPERIMENTS.md` and
`LAB_NOTEBOOK.md`. The two negative results are kept on purpose — measuring caught two changes
that *looked* obviously good and weren't.

## Safety layer

- **Mandatory citations** — every claim cites `[KYC Master Direction, p.N]`; a post-check
  (`src/verify.py`, 7 unit tests) flags any cited page **not** in the retrieved set, catching
  hallucinated citations.
- **Refusal by evidence, not by threshold** — we *measured* that answerable and out-of-corpus
  retrieval scores overlap on every retriever, so a score cutoff can't separate them. Refusal is
  enforced at generation (strict-grounding prompt) and validated by the citation check.
- **Versioning** — `src/amendments.py` parses the document's footnotes into a **14-circular
  amendment timeline**; the system knows which circular changed what, and when.

## Numbers

- **Retrieval latency** (local, 50 queries): **rerank (shipped default) p50 ≈ 408 ms**; **hybrid (`RETRIEVER=hybrid`) p50 ≈ 11 ms**. The cross-encoder buys +0.02 recall@5 for ~37× latency — worth it here (a wrong compliance answer costs more than 0.4 s), and one env var away if you need speed.
- **Cost/query**: ₹0 on the Gemini free tier. Token-based estimate on paid tiers: ~1.2K input +
  ~300 output tokens ≈ **₹0.09/query on Gemini 2.5 Flash, ₹0.23 on Claude Haiku 4.5**.

## Add your API key (the one thing you must do)

The answer step needs a language model. Get a **free Gemini key** (no credit card) at
**https://aistudio.google.com/apikey**, then:

```bash
cp .env.example .env      # then open .env and paste your key after GEMINI_API_KEY=
```

`.env` is gitignored, so your key never leaves your machine. Retrieval and the eval scorecard
work without a key; only the generated answers need it. (Prefer Claude? Put `ANTHROPIC_API_KEY`
in `.env` instead — the pipeline auto-detects which one is present.)

## Run it

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python src/extract.py && python src/chunk.py && python src/embed.py   # build the index (once)
python src/ask.py "How long must banks keep KYC records?"            # CLI
uvicorn app:app --app-dir src                                        # web UI at :8000

python eval/run_eval.py                       # retrieval scorecard (no key needed)
python eval/run_eval.py --gen --retriever hybrid   # + generation behaviour (needs key)
python eval/test_verify.py                    # citation-guardrail unit tests
python src/amendments.py                      # amendment timeline
```

Default retriever is `rerank` — the best measured config (recall@5 **0.93**, recall@1 **0.77**).
It loads a ~1.1GB BGE cross-encoder on first use, then caches. Set `RETRIEVER=hybrid` for a
lighter, ~37× faster setup at 0.91.

## What I'd do next

- Chunk-level (not page-level) recall grading — page-level is slightly optimistic.
- Complete the 50-question generation-behaviour eval (blocked only by the free-tier daily quota;
  harness is `--resume`-able).
- Ingest the individual amendment circulars for true old-vs-new text diffing (RBI's doc server
  bot-blocks scripted downloads).

## Notes

Built with AI assistance (pair-programming and review). Every number in this README is
reproducible with `./run.sh eval`; the full experiment history, including the two changes that
made things worse, is in `EXPERIMENTS.md` and `LAB_NOTEBOOK.md`.
