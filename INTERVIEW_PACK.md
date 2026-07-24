# Interview Pack — RBI KYC Compliance RAG

Everything you need to demo and defend this project. Rehearse the demo and the Q&A out loud.
The numbers here are real — they come from `EXPERIMENTS.md` and `LAB_NOTEBOOK.md`.

---

## The 60-second pitch

> "Every RBI-regulated fintech has to follow the KYC Master Direction — a 100-page rulebook
> that's amended constantly. I built a system that answers compliance questions from it with
> exact clause citations, refuses when the answer isn't in the document, and tracks the
> amendment history. The interesting part isn't the LLM — it's the retrieval. I built BM25 and
> vector search from scratch, no LangChain, and improved recall@5 from 0.82 to 0.93 by testing
> one change at a time against a 50-question eval set I hand-verified — including two changes
> that looked good and measurably made it worse, which I reverted."

## 90-second demo script

1. **CLI, a clean answer.** `python src/ask.py "What are the three monetary limits on Aadhaar OTP e-KYC accounts?"`
   → three limits, each with `[KYC Master Direction, p.N]`. *"Every claim is cited."*
2. **The refusal.** `python src/ask.py "What are the tax benefits under Section 80C?"`
   → "Not found in the provided documents." *"It won't answer outside its corpus — a wrong
   compliance answer is worse than none."*
3. **The scorecard.** `python eval/run_eval.py` → recall@1/recall@5 in one command. *"Every
   change I made was measured against this."*
4. **The web UI** (optional): `uvicorn app:app --app-dir src`, ask the video-KYC question,
   point at the green citations.
5. **Versioning.** `python src/amendments.py` → the 14-circular amendment timeline. *"Parsed
   from the document's own footnotes — the system knows what changed and when."*

## 5-minute deep-dive walkthrough

1. **Problem & framing** (30s) — compliance is where fintechs bleed money; citations + refusal
   are the product.
2. **Architecture** (60s) — two halves: retrieval (the hard part) and generation (a swappable
   commodity behind one function). Draw the pipeline.
3. **The retrieval climb** (120s) — walk the experiment table: dense 0.82 → BM25 (complementary)
   → hybrid RRF 0.91 → BGE rerank 0.93. Emphasise the **two negative results** and *why* they
   failed. This is the heart of the interview.
4. **Safety layer** (60s) — citation post-check catches hallucinated cites; refusal is
   evidence-based (scores overlap, so no threshold); versioning from footnotes.
5. **Honesty** (30s) — what's not done and why (generation eval blocked by free-tier quota;
   page-level grading is optimistic). Knowing your system's limits reads as senior.

---

## Design-decisions log (every choice, why, alternative rejected)

| Decision | Why | Alternative rejected |
|---|---|---|
| One document (KYC MD), deep | tight scope, rich amendment history, universally understood | whole RBI corpus — shallow, unfocused |
| No LangChain | must defend every line; frameworks hide the machinery | LangChain — fast to wire, nothing learned |
| Hand-written cosine + BM25 | "I built it" credibility; full understanding | `rank_bm25`/FAISS from day 1 — black box |
| BGE-small local embeddings | free, on-laptop, teaches the mechanism | OpenAI/Voyage API embeddings — costs, less insight |
| Hybrid via **RRF** | combines lexical + semantic using ranks (no score-scale mismatch) | weighted score sum — needs score normalisation, fiddly |
| Gemini free tier, swappable | ₹0 for a student; generator is a commodity | hard-wire one paid vendor |
| Refusal at generation, **no score threshold** | *measured* that answerable/trick scores overlap | a cutoff — would false-refuse real questions |
| Page-level recall metric | simple, unambiguous to grade | chunk-level — stricter but more label work (noted as future work) |
| Kept negative results in the repo | the measurement discipline *is* the story | quietly deleting failed experiments |

## Anticipated Q&A (grounded in real findings)

**Q: Why RAG instead of just asking the LLM?**
An LLM answers from fuzzy memory — it blends versions, invents clauses, can't cite, and has a
training cutoff. RAG hands it the actual pages and forces it to answer only from them. In
compliance, "plausible but wrong" is the worst output.

**Q: What's recall@5 and why that metric?**
Fraction of answerable questions where a top-5 retrieved chunk came from the clause's page. It
grades the *retriever alone*, separate from the LLM — so when an answer is wrong I know which
half to fix. It went 0.82 → 0.93.

**Q: Why hybrid search — what does each half catch?**
Embeddings match *meaning* (great for paraphrases like "video call" → "V-CIP"); BM25 matches
*exact terms* (great for "Section 16", "OVD", rare tokens). They're complementary — I measured
that each catches the other's misses, so fusing them beat either alone (0.82/0.84 → 0.91).

**Q: You added a reranker and it helped — anything surprising?**
Yes. The *first* reranker I tried (ms-marco) made it **worse** (0.84) — my chunks start and end
mid-sentence, which is out-of-distribution for a web-passage-trained model. The BGE reranker,
which pairs with my embedder, took it to 0.93. Same technique, opposite result — the model
choice mattered as much as the technique.

**Q: How do you stop hallucinated answers / citations?**
Two layers. The strict-grounding prompt makes the model answer only from the excerpts — I saw it
correctly decline a plausible-but-wrong "₹1 lakh" figure that was in context for a *different*
account type. And a deterministic post-check (`verify.py`) flags any cited page not in the
retrieved set — I caught the model fabricating a page citation on one non-deterministic run.

**Q: How do you decide when to refuse?**
Not with a retrieval-score threshold — I measured that out-of-corpus questions score in the same
range as real ones on every retriever, so a cutoff would wrongly refuse real questions. Instead
the model refuses at generation time when the excerpts don't support an answer, validated by the
citation check.

**Q: The document gets amended — how do you handle that?**
Each amended clause carries a footnote naming the amending circular and date. I parse those into
an amendment index (14 circulars, newest 2025 back to 2019). Full old-vs-new text diffing would
need the individual circular PDFs — RBI's server bot-blocks scripted downloads, so that's noted
as future work; the consolidated doc's footnotes already encode the history.

**Q: What breaks at 100× the documents?**
Retrieval is a linear scan today (fine for 431 chunks, ~10ms). At scale I'd swap the hand-written
cosine for an ANN index (FAISS/HNSW) — same interface, sublinear search — and shard BM25. The
architecture already isolates retrieval behind one function, so it's a component swap.

**Q: What was the hardest bug / most surprising result?**
An eval-harness bug: I was grading citation-grounding against the pages from one retriever while
the answer was generated from another, so "grounded" was measured against the wrong context. It
taught me that an eval must generate and grade through the *same* path.

**Q: What's your cost and latency?**
Retrieval p95 ≈ 18ms locally. ₹0/query on the free tier; ~₹0.09–0.23/query on paid tiers by
token count. The bottleneck is the LLM call (~2–4s), not retrieval.

**Q: What would you do differently / next?**
Chunk-level recall grading (page-level is slightly optimistic), finish the generation-behaviour
eval (blocked only by free-tier daily quota), and ingest the amendment circulars for true version
diffing.

## Honest framing (say this, it's true and it lands well)

> "I built this with an AI assistant as a pair-programmer — it scaffolded code and taught me
> concepts. But I verified the evaluation set against the RBI documents myself, I ran every
> experiment, and I can defend every design decision — which is what this walkthrough is."

AI-assisted building is normal in 2026. Claiming understanding you don't have is what fails.
Everything above is answerable because the work is real — so **do the onboarding in
`FRIEND_ONBOARDING.md`** (verify the eval, run the experiments yourself) and these answers become
yours, not memorised.
