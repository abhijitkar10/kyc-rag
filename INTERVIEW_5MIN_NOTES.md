	# 5-Minute Spoken Notes + Plain-English Glossary

Two parts:
1. **The script** — what to say, in simple words, for ~5 minutes straight.
2. **The glossary** — every technical term on the resume bullet, in plain English,
   plus the one-line answer if the interviewer stops you and asks "what's that?"

Rule for the room: **speak plainly, then let them pull you deeper.** Don't open with jargon.

---

# PART 1 — THE 5-MINUTE SCRIPT

## [0:00 – 0:45] The problem (start here, always)

> "Every bank, NBFC and payment company in India has to follow RBI's KYC rulebook —
> that's the rules about how you verify a customer's identity before opening an account.
> The rulebook is about a hundred pages of dense legal text, and RBI keeps amending it.
> So when someone inside a company asks a simple question — 'can we open this account with
> just a PAN card?' — somebody has to dig through a hundred pages to find the answer.
> Getting it wrong means real fines. That's the problem I built for."

*Why start here: it proves you understand the business, not just the tech.*

## [0:45 – 1:30] What it actually does

> "I built an assistant you can ask that question in plain English. It answers, and with
> every answer it tells you exactly which page and clause the answer came from — so a
> compliance officer can go verify it. And if you ask something that isn't in the rulebook —
> say a tax question — it says 'not found in the provided documents' instead of guessing.
> In compliance, a confident wrong answer is worse than no answer, so refusing is a feature."

## [1:30 – 3:00] How it works (the simple version)

> "There are two halves: a search half and a writing half.
>
> First I take the PDF, pull the text out, and cut it into about 431 small pieces — I call
> them chunks. Then I turn every chunk into a list of numbers that captures its meaning, so
> pieces about similar topics end up close together. That's called an embedding.
>
> When a question comes in, I turn the question into numbers the same way, and find the five
> closest chunks. Then — and this is the important bit — I hand only those five pieces to a
> language model with a strict instruction: answer only from this text, cite the page for
> every claim, and if the answer isn't here, say so.
>
> So the AI isn't answering from memory. It's an open-book exam where I control which pages
> are open. That's what stops it making things up."

## [3:00 – 4:15] The engineering — where the real work was

> "The hard part isn't the AI writing the answer — that's the easy part. The hard part is
> making sure the right five chunks get pulled up. So I measured it.
>
> I wrote 50 test questions myself, reading the rulebook and noting the exact clause that
> answers each one. Then I could score the system: for what fraction of questions does the
> correct page show up in the top five? That's called recall at 5. My first version scored
> 0.82.
>
> Then I improved it one change at a time, re-measuring after each. I added a keyword search
> that I wrote from scratch, because meaning-based search is bad at exact terms like
> 'Section 16'. I combined the two searches. Then I added a re-ranking step that takes 20
> candidates and re-reads them more carefully to pick the best 5.
>
> That took me from 0.82 to 0.93. And two of my experiments actually made it *worse* — I
> kept those in the repo, documented, because knowing what didn't work is the whole point of
> measuring."

*If you only remember one number, remember: **0.82 → 0.93**.*

## [4:15 – 5:00] Safety + the lesson (close strong)

> "On top of that I added a safety check. The model is told to cite a page — but I actually
> verify that the page it cited was one of the pages I gave it. If it cites a page it never
> saw, that's a made-up citation, and I flag the answer as unverified. I caught the model
> doing exactly that once, which is why I built it.
>
> The biggest thing I learned: don't trust that a change helped — measure it. Two of my
> 'obvious' improvements made things worse, and I'd never have known without the test set."

**Then stop talking.** Let them ask.

---

# PART 2 — GLOSSARY (every term on the resume, in plain words)

For each: what it means → the one-liner if they probe.

### RAG (Retrieval-Augmented Generation)
**Plain:** Instead of letting the AI answer from memory, you first *search* your documents,
then hand it only the relevant snippets and say "answer from these."
**If probed:** *"Retrieval-augmented generation — search first, then generate from what you
found. It fixes hallucination and lets you cite sources, which memory-based answering can't."*

### Chunks / chunking (431 chunks)
**Plain:** Cutting the document into small pieces so search can find one specific rule
instead of returning a whole page.
**If probed:** *"800-character overlapping windows. Overlap so a rule sitting on a cut
boundary isn't split in half and lost."*

### Embeddings (and "dense" retrieval)
**Plain:** Turning text into a list of numbers that captures meaning. Similar meanings get
similar numbers — so "ID proof" and "Officially Valid Document" land near each other even
though they share no words.
**If probed:** *"384-dimensional vectors from a local BGE model. I normalise them, so
comparing two texts is just a dot product."*

### BGE
**Plain:** The name of the free, open-source model I used to make those number-lists. It runs
on a laptop — nothing is trained by me.
**If probed:** *"BAAI's BGE-small. Chosen because it's free, local, and pairs with the BGE
re-ranker I use later."*

### Cosine similarity
**Plain:** The measure of "how close" two of those number-lists are. Close = similar meaning.
**If probed:** *"Angle between two vectors. Since I normalise to unit length, it's just a dot
product — the whole search is one matrix multiply and a sort."*

### BM25 ("hand-written")
**Plain:** Classic *keyword* search. It scores a chunk higher if it contains your words,
counts **rare** words much more than common ones, and doesn't reward padding.
**If probed:** *"I implemented it from scratch — inverted index, term frequency with
saturation, IDF weighting, length normalisation. About 60 lines, no library."*
**Why both searches:** *"Embeddings are great at paraphrases but blur exact terms — 'Section
16' and 'Section 61' look almost identical to them. BM25 nails exact rare terms but fails on
paraphrases. Opposite blind spots, so I use both."*

### RRF (Reciprocal Rank Fusion)
**Plain:** The way I *merge* the two search results. Each search ranks its favourites; a chunk
that both lists rank highly wins.
**If probed:** *"It uses rank positions, not raw scores — one over sixty-plus-rank, summed.
That sidesteps the fact that cosine scores and BM25 scores aren't on the same scale, so I
never have to hand-tune a weighting."*

### Cross-encoder re-ranker
**Plain:** A slower, smarter model that reads the question and a chunk *together* and judges
"does this actually answer it?" Too slow for all 431 chunks, so: fast search shortlists 20,
then this re-reads those 20 and picks the final 5.
**If probed:** *"Embeddings score the query and chunk separately then compare vectors. A
cross-encoder feeds the pair jointly through the model — much sharper, much slower. Classic
two-stage retrieval: cheap filter, expensive judge."*

### recall@5 and recall@1
**Plain:** My score. **recall@5** = out of my 50 test questions, how often the correct page
appeared in the top 5 results. **recall@1** = how often it was the *very first* result.
**If probed:** *"0.82 → 0.93 for recall@5, 0.61 → 0.77 for recall@1. Note it grades the
search alone, with no AI involved — so when an answer is wrong I know immediately whether to
blame the search or the writing."*
**The insight to volunteer:** *"recall@1 being much lower than recall@5 told me the right
chunk was usually being found but ranked poorly — which is exactly why a re-ranker was the
highest-value fix."*

### "50-question eval" / eval set
**Plain:** My test paper. 50 questions where *I* read the rulebook and wrote down the correct
answer and its exact clause — including 6 questions whose answers aren't in the document at
all, to test refusing.
**If probed:** *"Hand-verified ground truth. Every improvement is measured against it, so no
change goes in on vibes."*

### "5 retrieval configs / 2 negative results"
**Plain:** I tried five different search setups and measured each. Two made things *worse*,
and I kept them documented instead of hiding them.
**If probed (this is your best story):** *"The first re-ranker I tried actually dropped my
score from 0.91 to 0.84 — my chunks start and end mid-sentence, which is out of distribution
for a re-ranker trained on clean web passages. I swapped in a stronger one and got 0.93. Same
code, opposite result — the model choice mattered as much as the technique."*

### "no LangChain"
**Plain:** LangChain is a popular library that does RAG plumbing for you. I didn't use it — I
wrote the pipeline myself.
**If probed:** *"I wanted to be able to explain every line. At this scale the framework would
have hidden the parts that are actually interesting — the search, the fusion, the ranking."*

### Citation guardrail / hallucinated citations
**Plain:** The model is told to cite a page number. My code then checks that the page it
cited was actually one of the pages I gave it. If not, that citation is invented, and I flag
the answer as unverified.
**If probed:** *"I caught the model fabricating a page reference on one run. A citation you
can't trace back to retrieved context is worthless in compliance. It's a pure-logic check —
no AI call — so it's fast and unit-testable."*

### "Hallucination"
**Plain:** When an AI says something that sounds right but isn't real — because it's
predicting plausible text, not looking anything up.
**If probed:** *"That's the whole reason for RAG plus the guardrail: ground it, then verify
the grounding."*

### Refusal / "out-of-corpus"
**Plain:** If you ask something the rulebook doesn't cover, it says "not found" instead of
guessing.
**If probed (important — be precise):** *"I deliberately did NOT use a similarity-score
threshold, because I measured that out-of-corpus questions score in the same range as real
ones — so a cutoff would wrongly refuse genuine questions. Refusal is enforced by the strict
prompt at generation time and validated by the citation check."*

### Unit tests (7)
**Plain:** Small automatic tests that prove the citation checker behaves correctly — good
citation passes, invented citation gets flagged, refusal recognised, and so on.
**If probed:** *"The guardrail is pure logic over text and page numbers, so it's testable
without spending a single API call — that was a deliberate design property."*

### Amendment index (14 circulars)
**Plain:** RBI keeps changing the rulebook, and every changed clause has a footnote saying
which circular changed it and when. I parse those footnotes into a timeline — so the system
knows the document's own edit history.
**If probed:** *"14 distinct amending circulars, newest August 2025 back to 2019. The April
2023 one touched 42 pages. Full old-vs-new text diffing would need the individual circular
PDFs — RBI's server blocks scripted downloads — so that's scoped as future work."*

### FastAPI / Sentence-Transformers
**Plain:** FastAPI = the small web server for the demo page. Sentence-Transformers = the
library that runs the free local embedding model.
**If probed:** *"The UI is a single self-contained HTML page — no framework, no build step.
The effort belonged in retrieval, not the front end."*

### Provider-agnostic LLM layer
**Plain:** The writing model sits behind one function, so I can swap Gemini for Claude
without touching anything else.
**If probed:** *"Retrieval is where the engineering is; the generator is a commodity. It also
let me develop on a free tier."*

---

# PART 3 — BEFORE YOU WALK IN: verified vs. not

Say only what you can back up. Current status:

| Claim | Status |
|---|---|
| recall@5 0.82 → 0.93, recall@1 0.61 → 0.77 | ✅ Fully measured, in `EXPERIMENTS.md` |
| 5 configs / 2 negative results | ✅ Measured and documented |
| 431 chunks, 107 pages, 14 circulars | ✅ Factual |
| 7 unit tests | ✅ Run `./run.sh test` |
| Retrieval latency: 408 ms (rerank default) / 11 ms (hybrid) | ✅ Measured (`eval/perf.py`) — **don't say "<20 ms"**, that was the old default |
| **Zero hallucinated citations (14/14 grounded)** | ✅ Measured (exp6, 2026-08-26) |
| **Refused 3/3 out-of-corpus questions** | ✅ Measured — say **3/3**, not 6/6 |
| Full 50-question generation run | ⚠️ 21/50 done; free-tier daily quota. `./run.sh eval-gen --resume` finishes it. |

**Do NOT say "6/6".** Only 3 trick questions were reached before the quota cut in. Say:
> *"It refused 3 out of 3 out-of-corpus questions it was tested on, with zero hallucinated
> citations across the run — I'm still completing the remaining questions because of a
> free-tier API quota."*

## The best safety story you have (use this — it's stronger than any single number)

> "Four answerable questions got refused, which looks like a failure. But when I checked, three
> of those four were cases where retrieval never found the right page — so refusing was the
> *correct* behaviour. The system failed safe instead of making something up. Only one was a
> genuine false refusal. That's exactly why I measure retrieval and generation separately —
> otherwise 'four false refusals' would have looked like a bug instead of the system working."

That answer shows judgement, honest measurement, and understanding of failure modes — worth more
than a clean number.
