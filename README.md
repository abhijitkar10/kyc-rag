# KYC Compliance RAG Assistant

A retrieval-augmented question-answering system over the RBI Master Direction on KYC —
with clause-level citations, refusal on weak retrieval, and amendment-aware versioning.

**Master plan:** see `RAG Project — Master Plan.md` in the vault (05 Career).
**Every experiment is logged in** `LAB_NOTEBOOK.md`.

## Status

- Phase 0 — foundations & data immersion: **in progress**

## Layout

```
data/raw/         downloaded RBI PDFs (dated filenames)
data/processed/   extracted text, chunks
src/              pipeline code (built in Phase 1)
eval/             questions.csv + scoring script
LAB_NOTEBOOK.md   experiment log
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# LLM key for the answer step (retrieval works without it).
# Free Gemini key: https://aistudio.google.com/apikey
echo 'GEMINI_API_KEY=your-key-here' > .env    # .env is gitignored
```

The generator picks Gemini if a Gemini key is present, else Claude — see `src/llm.py`.

