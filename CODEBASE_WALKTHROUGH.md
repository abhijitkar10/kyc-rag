# Codebase Walkthrough — file by file, function by function

A guided tour of the whole system, in the order data flows through it. Written to be spoken
aloud in an interview: for each file you get its **one-line job**, a **function-by-function
breakdown**, the **key lines explained**, and **"what they'll probe"** — the questions an
interviewer asks at that exact spot, with the answer.

> Mental model to state up front: **the system has two halves — retrieval (the hard part) and
> generation (a swappable commodity).** Indexing is done once, offline. Then every question runs:
> `retrieve → build prompt → LLM answers only from the excerpts → citation guardrail`.

**Walk order (data flow):**
1. Indexing — `extract.py` → `chunk.py` (+ `chunk_clause.py`) → `embed.py`
2. Retrieval — `search.py` → `bm25.py` → `retrievers.py`
3. Generation — `llm.py` → `answer.py` → `ask.py`
4. Safety — `verify.py` → `amendments.py`
5. Serving — `app.py`
6. Evaluation — `questions.csv` → `run_eval.py` → `test_verify.py` → `perf.py`
7. Trace one question end-to-end (the money section)

Files & sizes to know: **107-page PDF → 431 chunks → 384-dim vectors.** Corpus = the RBI Master
Direction on KYC (2025 consolidated).

---

# PART 1 — INDEXING (run once, offline)

Produces three files under `data/processed/`: `pages.jsonl`, `chunks.jsonl`, `embeddings.npz`.
Everything here is deterministic and needs no API key.

## `src/extract.py` — PDF → page-tagged plain text

**Job:** turn the PDF into one JSON record per page, keeping the printed page number so citations
can point back to it later.

- **`main()`**
  - `reader = PdfReader(RAW)` — opens the 107-page PDF with `pypdf`.
  - Loops `for i, page in enumerate(reader.pages, start=1)` — `i` is the page number (1-indexed).
  - `text = page.extract_text() or ""` — pypdf reverse-engineers the PDF's draw instructions back
    into text. The `or ""` guards against pages that yield `None`.
  - `text = " ".join(text.split())` — collapses all whitespace/newlines into single spaces. PDFs
    litter text with layout newlines; this normalises it so downstream chunking/tokenising is clean.
  - Writes `{"page": i, "text": text}` per line to `pages.jsonl` (JSON Lines — one JSON object per
    line, streamable, appendable).
  - Prints a count (107 pages, ~230K chars).

**What they'll probe:**
- *"Why keep the page number?"* — it's the unit of citation and the unit of eval grading. Every
  chunk inherits its page; the answer cites `[p.N]`; the eval checks "did a top-5 chunk come from
  the right page?".
- *"Extraction is imperfect — how do you know?"* — I opened `pages.jsonl` and read it. Footnotes,
  two-column headers, and tables can garble. For this doc the body text is clean; the footnotes
  (which I later parse for versioning) survived intact. Real-world data is dirty — inspecting the
  extracted text is step one.

## `src/chunk.py` — pages → fixed-size chunks (the deliberately naive baseline)

**Job:** slice each page into overlapping ~800-character windows. Naive **on purpose** — it exists
to be beaten in Phase 3.

- **Constants:** `CHUNK_SIZE = 800`, `OVERLAP = 200`.
- **`main()`**
  - For each page record, slides a window: `piece = text[start : start + 800]`, then
    `start += CHUNK_SIZE - OVERLAP` (i.e. +600), so consecutive chunks share 200 chars.
  - Skips empty pieces (`if piece.strip()`), assigns each an incrementing `id`, keeps its `page`.
  - Writes 431 chunks to `chunks.jsonl`.

**Why two design choices matter:**
- **Overlap (200):** a rule sitting exactly on a cut boundary would be split — half in one chunk,
  half in the next, findable in neither. Overlap means every ~600-char stride still shares context
  with its neighbour, so boundary sentences aren't orphaned.
- **Why start naive?** So that in Phase 3, when I tried a smarter chunker, the score *change*
  proves whether chunking matters. (Spoiler: the smarter one lost — see next file.)

**What they'll probe:**
- *"Why 800 chars?"* — a balance: big enough to hold a whole short clause, small enough that a
  chunk is about one thing (so it matches precisely). It's a knob I later tested against.
- *"Character-based, not token-based?"* — simpler and deterministic; the embedder truncates
  anyway. Token-aware chunking is a refinement I noted as future work.

## `src/chunk_clause.py` — the smarter chunker that LOST (a kept negative result)

**Job:** split on the document's own clause numbers ("16.", "17.", "46A.") instead of blind
800-char windows, so a clause's heading stays with its body. Regressed recall@5 0.91 → 0.82;
**kept in the repo on purpose** as a documented negative result.

- **`CLAUSE_START = re.compile(r"^(\d+[A-Z]?)\.\s")`** — matches top-level paragraph markers like
  `16. ` or `46A. `, but NOT roman/letter sub-items (`(a)`, `iii)`), so we split on whole clauses.
- **`flush(label, seg, chunks)`** — takes a collected clause (`seg` = list of `(line, page)`) and
  packs its lines into `<=MAX_CHARS` (1000) windows via the inner `emit()`. Each window is prefixed
  `[Para 16] …` and keeps the page of its **first** line (so page-level grading stays honest).
- **`main()`** — streams every line of every page; when a line matches `CLAUSE_START`, it `flush`es
  the previous clause and starts a new one; otherwise appends the line to the current clause.

**Why it lost (this is the interesting part to tell):** long clauses (V-CIP's para 18 runs pages)
got packed into multiple windows that all share the identical `[Para 18] …` prefix and cover
overlapping sub-topics — so a query's signal got **diluted** across near-duplicate chunks, and the
right one no longer ranked top-5. Naive fixed windows, by cutting mid-clause, accidentally kept
each chunk more topically distinct. **Measured, understood, reverted.**

**What they'll probe:**
- *"Isn't clause-aware obviously better?"* — that's exactly why it's a great story: it *looks*
  obviously better and the eval said otherwise. Structure-aware chunking helps when clauses are
  short; here many are pages long, and windowing them without overlap diluted the signal. The
  lesson is to measure, not assume.

## `src/embed.py` — chunks → embedding vectors

**Job:** turn each chunk into a 384-number vector capturing its meaning; save to `embeddings.npz`.

- **`MODEL_NAME = "BAAI/bge-small-en-v1.5"`** — a small, free, local sentence-transformer.
- **`main()`**
  - Loads the chunk texts.
  - `model.encode(texts, normalize_embeddings=True)` — runs the neural net; **normalises to unit
    length** so that later a dot product == cosine similarity (no separate division needed).
  - `np.savez_compressed(OUT, vectors=vecs.astype(np.float32))` — saves a (431, 384) matrix.

**What they'll probe:**
- *"What is an embedding, really?"* — the model places each text as a point in 384-dimensional
  space such that texts with similar *meaning* sit close together. "ID proof" and "Officially Valid
  Document" share no words but land near each other. The 384 numbers are that point's coordinates.
- *"Why normalise?"* — cosine similarity is the angle between two vectors; if both are unit-length,
  the angle's cosine is just their dot product. Normalising once here makes search a single matrix
  multiply.
- *"Why this model?"* — free, runs on a laptop, and (bonus) it pairs with the BGE reranker I use
  later. I'm not training anything — I download a frozen skill and run it.

---

# PART 2 — RETRIEVAL (the hard part; this is where the interview lives)

## `src/search.py` — dense (semantic) search, hand-written cosine

**Job:** the entire "vector database" in ~10 lines — embed the question, dot-product it against all
chunk vectors, sort.

- **Module globals + `_load()`** — lazy-loads the model, chunks, and vectors once (cached in
  module globals) so repeated calls don't reload. `_model is None` gate = load-on-first-use.
- **`QUERY_PREFIX = "Represent this sentence for searching relevant passages: "`** — BGE's model
  card requires queries to carry this instruction prefix (passages are embedded without it). Skipping
  it silently degrades recall — a subtle correctness detail.
- **`search(question, top_k=5)`**
  - `q = _model.encode([QUERY_PREFIX + question], normalize_embeddings=True)[0]` — the question as a
    unit vector on the same map.
  - `scores = _vecs @ q` — **one matrix-vector product**: every chunk's similarity at once (431
    dot products).
  - `best = np.argsort(scores)[::-1][:top_k]` — argsort ascending, reverse for descending, take
    top-k indices.
  - Returns `[(score, chunk), ...]`.

**What they'll probe:**
- *"You wrote your own vector search — why not FAISS?"* — at 431 chunks a linear scan is ~10ms;
  a library would be premature. Writing it myself means I can explain every line. At 100× scale I'd
  drop in an ANN index (FAISS/HNSW) behind the same function signature — the architecture already
  isolates it.
- *"Complexity?"* — O(N·d) per query (N chunks × d dims). Fine here; sublinear ANN at scale.

## `src/bm25.py` — keyword search, implemented from scratch (the "I built it" showpiece)

**Job:** rank chunks by keyword overlap, weighting rare words heavily and long chunks lightly — the
classic Okapi BM25, no library.

- **Constants:** `K1 = 1.5` (term-frequency saturation), `B = 0.75` (length normalisation).
- **`tokenize(text)`** — `re.findall(r"[a-z0-9]+", text.lower())`. Keeps digits — "16", "50000"
  matter in a legal doc.
- **`class BM25Index`**
  - **`__init__`** builds, in one pass:
    - `self.doc_len` — token count per chunk; `self.avgdl` — average.
    - `self.postings` — an **inverted index**: `term -> [(chunk_id, term_freq), ...]`. This is the
      data structure real search engines use; scoring only touches chunks that contain a query term.
    - `df` — document frequency per term (how many chunks contain it).
    - `self.idf[term] = ln((N - n + 0.5)/(n + 0.5) + 1)` — **inverse document frequency**; the `+1`
      keeps it non-negative. Rare terms → high IDF → strong signal.
  - **`search(query, top_k=5)`** — for each query term, walk its postings and add
    `idf * (f*(K1+1)) / (f + K1*(1 - B + B*dl/avgdl))` to that chunk's score. Sort, return top-k.

**Explain the formula in words:** a chunk scores higher when it contains more of the query's words
(term frequency `f`, but **saturating** — the 10th occurrence adds little), those words are **rare**
across the corpus (IDF), and the chunk **isn't padded out** with length (the `B·dl/avgdl` term).

**What they'll probe:**
- *"Why keyword search if you already have embeddings?"* — they have opposite blind spots.
  Embeddings blur exact tokens: "Section 16" and "Section 61" are almost the same point on the
  meaning-map. BM25 nails exact/rare terms ("OVD", "V-CIP", "16") but fails on paraphrases. You want
  both. I *measured* they're complementary — each catches the other's misses.
- *"What's IDF doing?"* — down-weighting words that appear everywhere ("customer" appears 900×,
  tells you nothing about *which* chunk) and up-weighting homing-beacon words ("OVD" appears in one).

## `src/retrievers.py` — the swappable-retriever seam (dense / bm25 / hybrid / rerank)

**Job:** one factory, `get_retriever(name)`, returning a callable `(question, top_k) -> [(score,
chunk)]`. This seam is what let Phase 3 A/B every idea with one flag.

- **`get_retriever("dense")`** → returns `search` from `search.py`.
- **`get_retriever("bm25")`** → builds a `BM25Index`, returns a lambda wrapping `.search`.
- **`get_retriever("hybrid")`** → **Reciprocal Rank Fusion**:
  - Pulls `POOL=30` candidates from **each** of dense and BM25.
  - `fused[c["id"]] += 1.0 / (RRF_K + rank + 1)` with `RRF_K=60` — each retriever contributes
    `1/(60+rank)` per chunk. **Uses rank position only**, never the raw scores — so cosine's 0–1
    scale and BM25's unbounded scale never have to be reconciled. A chunk ranked high by *either*
    gets a good total; ranked high by *both* wins.
  - Sorts fused scores, returns top-k.
- **`get_retriever("rerank")`** → two-stage:
  - Reuses `hybrid` as the fast first stage to shortlist `pool=20`.
  - `ce = CrossEncoder("BAAI/bge-reranker-base")` — a cross-encoder that reads **(question, chunk)
    together** and scores true relevance (unlike embeddings, which score them separately).
  - `ce.predict([(q, c["text"]) for ...])`, sort by that score, return top-k.

**Why RRF over weighted sum?** A weighted sum of cosine + BM25 needs the two scores normalised to a
common scale — fiddly and dataset-dependent. RRF sidesteps it entirely by fusing **ranks**. This is
a deliberate, defensible choice.

**Why the reranker is two-stage:** the cross-encoder is accurate but slow (it runs the model once
per (query,chunk) pair). Running it on all 431 chunks is wasteful; running it on 20 hybrid
candidates is cheap and captures almost all the benefit. Fast-rough filter → slow-sharp judge.
Exactly how production search ranks.

**What they'll probe:**
- *"Reranker helped — anything surprising?"* — the FIRST reranker (ms-marco) made it **worse**
  (0.91→0.84): my chunks start/end mid-sentence, which is out-of-distribution for a web-passage
  reranker. BGE (which pairs with my embedder) took it to 0.93. Same code, opposite result — the
  model choice mattered as much as the technique. That's the single best story in the project.
- *"Embedding vs cross-encoder — difference?"* — embeddings encode query and chunk *separately*
  then compare vectors (fast, approximate). A cross-encoder feeds the pair *jointly* through the
  model and outputs one relevance score (slow, sharp). Two-stage retrieval gets both.

---

# PART 3 — GENERATION

## `src/llm.py` — the provider-flexible LLM (the "vendor is a commodity" point)

**Job:** hide *which* LLM answers behind one function, so the architecture doesn't depend on any
vendor. Picks Gemini (free tier) or Claude by which key is present.

- **`GEMINI_MODEL = "gemini-2.5-flash"`, `CLAUDE_MODEL = "claude-haiku-4-5"`** (env-overridable).
- **`_load_dotenv()`** — a dependency-free `.env` reader (KEY=value per line). Keeps the friend's
  key in a gitignored file, no `python-dotenv` dependency.
- **`provider()`** — resolves which backend is available: `GEMINI_API_KEY`/`GOOGLE_API_KEY` →
  gemini; else `ANTHROPIC_API_KEY` → claude; else raises a helpful error pointing at the free-key URL.
- **`complete(system, user, max_tokens=1024)`** — the single interface every caller uses. Dispatches
  to `_gemini` or `_claude`. Deterministic (`temperature=0`) for reproducible eval.
- **`_gemini(...)`** — calls `client.models.generate_content` with `system_instruction`,
  `temperature=0`, and **`thinking_config=ThinkingConfig(thinking_budget=0)`**. That last one is a
  real gotcha: Gemini 2.5 models spend "thinking" tokens out of `max_output_tokens`, which was
  truncating short answers; RAG answers are grounded in provided context, so we buy the full output
  budget back by disabling thinking.
- **`_claude(...)`** — the Anthropic equivalent via `client.messages.create`.

**What they'll probe:**
- *"Why is the LLM behind an interface?"* — because retrieval is where the engineering is; the
  generator is interchangeable. This let me develop on Gemini's free tier and keep Claude as a
  drop-in fallback with zero changes upstream. It's also honest architecture: swappable dependency.
- *"Why temperature 0?"* — reproducible evals. (Caveat I found: Gemini's free tier isn't *perfectly*
  deterministic even at 0 — one run fabricated a citation — which is exactly why the Phase 4
  guardrail exists.)

## `src/answer.py` — assemble the prompt, generate, guard

**Job:** the whole question→answer path in one function.

- **`_search = get_retriever(os.environ.get("RETRIEVER", "hybrid"))`** — the shipped default is
  hybrid (fast, 0.91, no 1.1GB model); `RETRIEVER=rerank` swaps in the peak config.
- **`SYSTEM`** — the strict-grounding system prompt: *answer ONLY from the excerpts, cite
  `[KYC Master Direction, p.N]` for every claim, and if it's not there reply exactly "Not found in
  the provided documents."* This prompt is doing real safety work — it fights the LLM's default
  instinct to be helpful and fill gaps from memory.
- **`answer(question, top_k=5, retriever=None)`**
  - `hits = (retriever or _search)(question, top_k=top_k)` — the `retriever` param lets the eval
    harness pass the SAME retriever it grades with (this fixed a real bug — see `run_eval.py`).
  - `retrieved_pages = {c["page"] for _, c in hits}` — remembered for the guardrail.
  - Builds `excerpts` — each chunk labelled `[Excerpt i — KYC Master Direction, p.N]` so the model
    knows each snippet's page for citing.
  - `raw = llm.complete(SYSTEM, f"{excerpts}\n\nQUESTION: {question}")` — the one LLM call.
  - `checked, _verdict = verify.enforce(raw, retrieved_pages)` — Phase 4 citation guardrail (below).
  - returns the checked answer.

**What they'll probe:**
- *"How do you stop hallucination?"* — three layers: (1) the strict prompt, (2) the model's own
  grounding — I saw it decline a plausible-but-wrong "₹1 lakh" figure that belonged to a different
  account type, and (3) the `verify.enforce` post-check that flags any cited page not retrieved.
- *"Why pass `retriever` in?"* — so generation and the grounding check use the *same* retrieved set.
  Earlier they didn't (harness graded dense, answered hybrid) and grounding was measured against the
  wrong context. Fixed.

## `src/ask.py` — the CLI

**Job:** `python src/ask.py "question" [--show-chunks]` — the whole pipeline behind one command.

- Parses argv; `--show-chunks` prints what the retriever found *before* the answer — the debugging
  ergonomic that lets you tell "the librarian missed" from "the writer messed up".
- Imports `answer` lazily (only when actually answering — so `--show-chunks` alone needs no key).

**What they'll probe:** *"How do you debug a wrong answer?"* — `--show-chunks`. If the right clause
isn't in the retrieved list, it's a retrieval problem (Phase 3 territory). If it's there but the
answer is wrong, it's a generation/prompt problem. Separating the two is the whole method.

---

# PART 4 — SAFETY LAYER (the differentiators tutorials skip)

## `src/verify.py` — citation verification (guardrail against hallucinated cites)

**Job:** a deterministic post-check — every cited page must be a page we actually retrieved.

- **`CITE = re.compile(r"\[KYC Master Direction, p\.(\d+)\]")`** — pulls cited page numbers out.
- **`verify(answer_text, retrieved_pages)`** returns a verdict:
  - `refusal` — the answer *is* the refusal line (nothing to check).
  - `uncited` — answered but cited no page (suspect).
  - `grounded` — every cited page was retrieved. ✓
  - `ungrounded` — a cited page was NOT retrieved → a hallucinated citation.
- **`enforce(answer_text, retrieved_pages)`** — appends a visible `⚠ … UNVERIFIED` note when the
  verdict is ungrounded/uncited. **Annotates rather than silently deleting** — auditability over
  tidiness; a reviewer sees exactly what the model did.

**What they'll probe:**
- *"Why did you need this?"* — I literally caught the model, on one non-deterministic free-tier run,
  fabricating a `p.26` citation for a fact that wasn't in the retrieved context. A cite you can't
  trace to a retrieved chunk is worthless in compliance. This catches it, cheaply, with no LLM.
- *"Why annotate instead of strip?"* — in a regulated setting you want an audit trail of what the
  model produced, not a silently edited answer.
- Backed by **7 unit tests** in `eval/test_verify.py` (grounded / ungrounded-single / ungrounded-
  mixed / refusal / uncited / enforce-annotates / enforce-passes).

## `src/amendments.py` — versioning from the document's own footnotes

**Job:** parse footnotes like *"Amended vide circular DOR.AML.REC.46/… dated August 14, 2025"* into
an amendment index — the honest "versioning" story without the (bot-blocked) individual circular
PDFs.

- **`PAT`** — a regex matching `(Amended|Inserted|Deleted) vide circular <ID> dated <Month DD, YYYY>`.
- **`build_index()`** — scans every page's text, builds `circular_id -> {dates, actions, pages}`.
- **`timeline()`** — flattens to `(date, circular, #pages-touched)`, sorted newest-first by parsing
  the date string with `datetime.strptime(d, "%B %d, %Y")`.

Result: **14 distinct amending circulars**, newest Aug 14 2025 back to May 29 2019; the April 2023
circular touches 42 pages (the big consolidation).

**What they'll probe:**
- *"Regulations change — how do you handle it?"* — each amended clause names its amending circular
  in a footnote; I parse those into a timeline, so the system knows what changed and when. Full
  old-vs-new text diffing needs the separate circular PDFs (RBI's server bot-blocks scripted
  downloads — a real-world data-acquisition wall), so that's scoped as future work; the consolidated
  doc's footnotes already encode the history.

---

# PART 5 — SERVING

## `src/app.py` — thin FastAPI app + a self-contained demo page

**Job:** a web UI for the demo. `uvicorn app:app --app-dir src` → http://127.0.0.1:8000.

- **`POST /ask`** — Pydantic `Ask` body `{question}` → calls `answer(...)`, times it, returns
  `{answer, provider, latency_ms}`.
- **`GET /amendments`** — returns the versioning timeline as JSON (the versioning showcase).
- **`GET /`** — serves `PAGE`, a single self-contained HTML string (no build step, no framework):
  a textarea, an Ask button, three example buttons (including an out-of-scope one to demo refusal),
  and a little JS that POSTs to `/ask` and renders citations green / `⚠` warnings red.

**What they'll probe:**
- *"Why no React?"* — the UI is a demo surface, not the substance; a self-contained HTML page has
  zero build/deps and shows the two things that matter: citations and refusal. I spent the effort
  on retrieval.
- *"How would you productionise?"* — stream tokens (Gemini supports it), add auth + rate limiting,
  move the index to a vector DB, and put the retriever behind a service boundary (already a clean
  function).

---

# PART 6 — EVALUATION (the measurement discipline that makes it credible)

## `eval/questions.csv` — the hand-verified ground truth (50 questions)

**Schema:** `id, question, answer_in_own_words, source_doc, clause_ref, answerable`.
- 44 answerable + 6 "trick" (out-of-corpus: Section 80C tax, SEBI demat, IRDAI insurance, mutual
  funds, crypto, min-balance).
- Flavors: direct lookups, **paraphrased** (deliberately avoiding the document's words — these test
  semantic search honestly), numeric thresholds, and amendment-aware.
- **`clause_ref` carries the page(s)** — this is what the eval grades against. Every one was
  verified against the PDF by hand.

**What they'll probe:** *"Who wrote the answer key and how do you trust it?"* — I did, by reading the
clause for every row. Human-verified ground truth is the rarest and most valuable thing in a RAG
project; an eval an AI wrote and an AI-built system passes proves nothing.

## `eval/run_eval.py` — the unified harness (one command, one scorecard)

**Job:** grade retrieval (no LLM) and, optionally, generation behaviour (`--gen`).

- **`expected_pages(clause_ref)`** — parses `p.26`, `p.26-27`, `p.13` out of the clause_ref into a
  set of page numbers (handles ranges and multiple refs).
- **`answer_with_retry(answer_fn, question, top_k, retriever, tries=4)`** — wraps the LLM call in
  exponential backoff (10s/20s/40s) because the Gemini free tier throws transient 429s; on final
  failure returns an `__ERROR__` sentinel the caller records but doesn't score. **This is why one
  bad call no longer kills an 8-minute run.**
- **`main()`**
  - Builds the chosen retriever (`--retriever`, default dense).
  - **Retrieval loop:** for each question, retrieve top-k; for answerable ones, `recall@1` =
    right page in top-1, `recall@5` = right page in top-5; collect best-scores; record misses.
  - **`separation`** — `min(answerable best-scores)` vs `max(trick best-scores)`. If they don't
    separate, a refusal threshold is impossible — this line is *why* refusal is done at generation,
    not by a cutoff. It printed OVERLAP on every retriever.
  - **Generation loop (`--gen`):** for each question, `answer_with_retry(... retriever=search)`
    (same retriever as graded — the bug fix); classifies `lead_refusal`, parses `cited_pages`,
    records `retrieved_pages`; writes a per-question JSONL.
    - **`_flush()`** rewrites the whole results file in question order after each answer — crash-safe
      progress.
    - **`--resume`** keeps prior *successful* answers and re-attempts only errored/missing rows —
      so a quota-truncated run finishes across days without redoing work.
  - **Metrics:** `cited` (answered with ≥1 cite), `grounded` (every cite ∈ retrieved), `false_ref`
    (answerable wrongly refused), `refused` (trick correctly refused), plus an `errored` count.
  - Prints a ready-to-paste `EXPERIMENTS.md` row.

**What they'll probe:**
- *"Walk me through recall@5."* — fraction of answerable questions where a top-5 chunk came from the
  clause's page. Grades the retriever *alone*, so I can localise failures. 0.82 → 0.93 across Phase 3.
- *"What's `separation` and why is it there?"* — it tests whether out-of-corpus questions score
  lower than real ones. They didn't (overlap), which is the evidence behind refusing at generation
  rather than by a score threshold.
- *"Free-tier limits — how did you handle them?"* — retry/backoff + crash-safe flush + `--resume`;
  and I keep retrieval eval LLM-free so the daily quota never blocks the core measurement.

## `eval/test_verify.py` — unit tests for the guardrail

7 deterministic tests (no LLM) covering every `verify` verdict and both `enforce` paths. Run:
`python eval/test_verify.py` → `7/7 passed`.

**What they'll probe:** *"You tested it?"* — the guardrail is pure logic on `(text, pages)`, so it's
unit-testable without spending a single API call. That's a deliberate design property.

## `eval/perf.py` — latency numbers

Measures retrieval latency over all 50 queries (warm-up call first, then p50/p95/max in ms). Result:
**p50 ≈ 10ms, p95 ≈ 18ms** locally — retrieval is not the bottleneck; the LLM call (~2–4s) is.

---

# PART 7 — TRACE ONE QUESTION END TO END (the money section)

Ask this out loud with the question **"Can I finish opening my bank account over a video call?"**

1. **`ask.py`** parses argv, calls `answer("Can I finish opening my bank account over a video call?")`.
2. **`answer.py`** calls the default **hybrid** retriever with `top_k=5`.
3. **hybrid** (`retrievers.py`) asks BOTH:
   - **dense** (`search.py`): embeds the question with the BGE query-prefix, `_vecs @ q`, returns 30
     candidates by cosine. "video call" lands near V-CIP text even though the doc never says "video
     call" — that's the embedding paying off.
   - **BM25** (`bm25.py`): tokenizes to `["can","i","finish","opening","my","bank","account","over",
     "a","video","call"]`, scores by rare-term overlap, returns 30 candidates. "video"/"call" are
     rareish; "account" common.
   - **RRF** fuses the two rank lists (`1/(60+rank)`), returns the top 5 chunks.
4. **`answer.py`** records the 5 pages, builds `excerpts` (each labelled with its page), and calls
   **`llm.complete(SYSTEM, excerpts + question)`**.
5. **`llm.py`** → `provider()` sees `GEMINI_API_KEY` → `_gemini(...)` with thinking disabled,
   temperature 0. The model, bound by the SYSTEM prompt, answers **only** from the excerpts and cites
   `[KYC Master Direction, p.27]` — or, if the retrieved chunks happen to be V-CIP *conditions*
   rather than the "V-CIP may be used for onboarding" opening, it **refuses** ("Not found…") rather
   than guess (this exact case is documented in the lab notebook).
6. **`verify.enforce`** (`verify.py`) parses the cited page (27), checks 27 ∈ retrieved pages. If
   yes → returns the answer unchanged (`grounded`). If the model had cited a page it wasn't given →
   appends `⚠ … UNVERIFIED`.
7. **`ask.py`** prints the final, guarded, cited answer.

Say the closing line: *"Every arrow in that chain is a function I can open and explain, and every
quality claim — recall 0.93, the refusals, the citations — has a number or a test behind it in the
repo."*

---

# APPENDIX — the 30-second "map" if they ask "what's in the repo?"

- **`src/`** — pipeline: `extract → chunk (/chunk_clause) → embed` (indexing); `search + bm25 +
  retrievers` (retrieval); `llm + answer + ask` (generation); `verify + amendments` (safety);
  `app` (serving).
- **`eval/`** — `questions.csv` (50-q ground truth), `run_eval.py` (scorecard), `test_verify.py`
  (unit tests), `perf.py` (latency), `results/` (per-question outputs).
- **Docs** — `README.md` (the story), `EXPERIMENTS.md` (the table), `LAB_NOTEBOOK.md` (every run),
  `BUILD_TIMELINE.md` (how it was built), `INTERVIEW_PACK.md` (pitch + Q&A), this file
  (`CODEBASE_WALKTHROUGH.md`), `FRIEND_ONBOARDING.md` (how to own it).

> Golden rule for the room: **never claim, always point.** Every capability maps to a file; every
> number maps to `EXPERIMENTS.md` or `LAB_NOTEBOOK.md`; every design choice has a rejected
> alternative you can name. That's what turns "I built a RAG bot" into a defensible engineering
> conversation.
