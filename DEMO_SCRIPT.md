# Live Demo — exact commands, in order

Tested 2026-08-26. Every command below was verified to work.

## ⚠️ Before the interview (do this the night before)

1. **Pre-warm the reranker** — the shipped default retriever downloads a ~1.1GB model on its
   FIRST run. Never let that happen live. Run `./run.sh ask "test"` once beforehand.
2. **Check your LLM quota** — the free Gemini tier allows ~20 calls/day. If you've been
   testing, you may be out. Steps 5–8 need NO key and always work.
3. **Open two terminal tabs** — one in the repo, one spare for the web server.

---

## Step 0 — Navigate

```bash
cd ~/Documents/life/kyc-rag
```

## Step 1 — The money demo: a cited answer

```bash
./run.sh ask "Which documents count as Officially Valid Documents for KYC?"
```

Expect: the full OVD list ending with **[KYC Master Direction, p.8]**.
Say: *"Every claim carries the page it came from, so a compliance officer can verify it."*

## Step 2 — The refusal demo (the one that impresses)

```bash
./run.sh ask "What are the tax benefits under Section 80C?"
```

Expect: **"Not found in the provided documents."**
Say: *"That's income-tax law, not in my corpus. A wrong compliance answer is worse than
no answer, so refusing is a feature, not a limitation."*

## Step 3 — Show the machinery (retrieval under the hood)

```bash
./run.sh ask "How long must banks keep KYC records?" --show-chunks
```

Expect: the 5 retrieved chunks with scores and page numbers, then the answer.
Say: *"This is how I debug — if the right chunk isn't in this list it's a retrieval problem,
if it is and the answer's wrong it's a generation problem."*

## Step 4 — The V-CIP question

```bash
./run.sh ask "Can I open a bank account over a video call?"
```

Expect: a cited answer about **V-CIP** (p.13). ✅ Works on the default config.
Say: *"The document never says 'video call' — it says V-CIP. That's the embedding search
matching on meaning rather than words."*

*(If you want to show the speed/accuracy trade-off, run the same question with
`RETRIEVER=hybrid ./run.sh ask "..."` — 37× faster, slightly lower recall.)*

## Step 5 — The scorecard (NO API KEY NEEDED)

```bash
./run.sh eval
```

Expect: recall@1, recall@5, misses, separation line.
Say: *"This is the number that matters — 50 hand-verified questions, graded on retrieval alone."*

## Step 6 — The tests (NO KEY NEEDED)

```bash
./run.sh test
```

Expect: **7/7 tests passed** — the citation guardrail.

## Step 7 — The versioning story (NO KEY NEEDED)

```bash
./run.sh amendments
```

Expect: a 14-circular timeline, newest first.
Say: *"RBI amends this document constantly. Every amended clause names its circular in a
footnote — I parse those into this timeline."*

## Step 8 — The web UI

```bash
./run.sh web
```

Then open **http://127.0.0.1:8000** — type a question, click Ask. Citations render green,
warnings red. `Ctrl-C` to stop.

---

## If the API quota dies mid-demo

Stay calm and pivot — steps **5, 6, 7** and `--show-chunks` all work with **no key**:

```bash
./run.sh eval && ./run.sh test && ./run.sh amendments
```

Say: *"I'm on a free API tier with a daily cap — but the retrieval layer, which is where the
real engineering is, needs no API at all. Here's the scorecard."*

That recovery reads as competence, not failure.

---

## One-command everything (if they say "just show me")

```bash
./run.sh all
```

Runs the tests, the scorecard, the amendment timeline, and a sample answer, in one go.
