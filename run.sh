#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# KYC-RAG — one script to run everything.
#
#   First time:   ./run.sh setup        (then optionally: cp .env.example .env)
#   Then:         ./run.sh all
#
# It creates the virtualenv, installs deps, and builds the search index
# automatically the first time — you don't have to remember any of that.
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail
cd "$(dirname "$0")"                 # always run from the repo root

VENV=.venv
PY="$VENV/bin/python"

# ── helpers ──────────────────────────────────────────────────────────────────
ensure_venv() {
  if [ ! -x "$PY" ]; then
    echo "==> creating virtualenv (.venv)…"
    python3 -m venv "$VENV"
  fi
  # (re)install deps only if a core package is missing — keeps re-runs instant
  if ! "$PY" -c "import sentence_transformers, google.genai, fastapi" >/dev/null 2>&1; then
    echo "==> installing dependencies (one-time, ~1-2 min)…"
    "$PY" -m pip install -q --upgrade pip
    "$PY" -m pip install -q -r requirements.txt
  fi
}

ensure_index() {
  if [ ! -f data/processed/embeddings.npz ]; then
    echo "==> building the search index (extract → chunk → embed)…"
    "$PY" src/extract.py
    "$PY" src/chunk.py
    "$PY" src/embed.py
  fi
}

key_hint() {
  if [ ! -f .env ] && [ -z "${GEMINI_API_KEY:-}" ] && [ -z "${ANTHROPIC_API_KEY:-}" ]; then
    echo
    echo "!! No API key found — answering needs one (retrieval, eval and tests don't)."
    echo "   Free Gemini key (no card): https://aistudio.google.com/apikey"
    echo "   Then:  cp .env.example .env   and paste it after GEMINI_API_KEY="
    echo
  fi
}

# ── commands ─────────────────────────────────────────────────────────────────
cmd="${1:-help}"
case "$cmd" in
  setup)
    ensure_venv; ensure_index; echo "✓ ready — try:  ./run.sh all" ;;

  index)                                    # force a rebuild of the index
    ensure_venv
    rm -f data/processed/*.jsonl data/processed/*.npz
    ensure_index; echo "✓ index rebuilt" ;;

  ask)                                      # ./run.sh ask "your question"
    ensure_venv; ensure_index; key_hint
    shift || true
    "$PY" src/ask.py "${*:-How long must banks keep KYC records?}" ;;

  web)                                      # web UI at http://127.0.0.1:8000
    ensure_venv; ensure_index; key_hint
    echo "==> http://127.0.0.1:8000   (Ctrl-C to stop)"
    "$VENV/bin/uvicorn" app:app --app-dir src ;;

  eval)                                     # retrieval scorecard (no key needed)
    ensure_venv; ensure_index
    "$PY" eval/run_eval.py "${@:2}" ;;      # extra flags pass through, e.g. --retriever hybrid

  eval-gen)                                 # + generation behaviour (needs a key)
    ensure_venv; ensure_index; key_hint
    "$PY" eval/run_eval.py --gen --retriever hybrid "${@:2}" ;;

  test)                                     # citation-guardrail unit tests
    ensure_venv
    "$PY" eval/test_verify.py ;;

  amendments)                               # the versioning timeline
    ensure_venv
    "$PY" src/amendments.py ;;

  all)                                      # full smoke run end-to-end
    ensure_venv; ensure_index
    echo; echo "── unit tests ──";        "$PY" eval/test_verify.py
    echo; echo "── retrieval scorecard ──"; "$PY" eval/run_eval.py
    echo; echo "── amendment timeline ──";  "$PY" src/amendments.py
    echo; echo "── sample answer ──";      key_hint
    "$PY" src/ask.py "How long must banks keep KYC records?" ;;

  *)
    cat <<'EOF'
KYC-RAG runner — one file to run everything.

  ./run.sh setup         create venv + install deps + build index (one-time)
  ./run.sh all           tests + retrieval scorecard + amendments + a sample answer
  ./run.sh ask "..."     ask a question (CLI)
  ./run.sh web           launch the web UI at http://127.0.0.1:8000
  ./run.sh eval          retrieval scorecard  (no API key needed)
  ./run.sh eval-gen      + generation behaviour  (needs a key; pass --resume to continue)
  ./run.sh test          citation-guardrail unit tests
  ./run.sh amendments    print the 14-circular amendment timeline
  ./run.sh index         force-rebuild the search index

Answering needs a free key:  https://aistudio.google.com/apikey
  →  cp .env.example .env   and paste it after GEMINI_API_KEY=
(Retrieval, eval, and tests all work with no key.)
EOF
    ;;
esac
