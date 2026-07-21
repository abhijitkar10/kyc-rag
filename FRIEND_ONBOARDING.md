# Onboarding — Make This Project Yours

This repo was scaffolded for you (by a friend working with an AI mentor). Everything in it
is real and verified — but **a project only helps you in interviews if you can defend it**.
An interviewer needs about two questions to detect outsourced understanding. This file is
the path from "I received a repo" to "I can survive a 20-minute grilling." Budget: ~2 weeks
of evenings alongside DSA prep.

## The honest story (memorize this, it's true and it's safe)

> "I built this with help — a friend and an AI assistant scaffolded it with me. I verified
> the evaluation set against the RBI documents myself, ran all the experiments, and I can
> walk you through every design decision."

In 2026, AI-assisted building is normal. Claiming understanding you don't have is what
sinks candidates. The steps below make the second sentence TRUE.

## Step 1 — Understand what this is (1 evening)

Read, in order: `README.md` → `BUILD_TIMELINE.md` (the story so far) → `READING_GUIDE.md`
(how the RBI document works). Then read the RBI PDF's page 1–3 and skim the table of
contents. You now know what the corpus is and why the project exists.

## Step 2 — The verification pass (2 evenings) ← the most important step

Open `eval/questions.csv` next to `data/raw/kyc-master-direction-2025-08-14.pdf`.
For EVERY row: go to the page in `clause_ref`, read the actual clause, and confirm the
answer is right. If anything looks off, fix it and note it in `LAB_NOTEBOOK.md`.

Why this matters twice over:
- It makes the eval **human-verified** — which you can then honestly claim.
- It IS the domain reading, disguised as checking. By row 20 you will know OVDs, V-CIP,
  OTP e-KYC limits, PEPs, retention rules — the exact vocabulary fintech interviewers use.

## Step 3 — Self-test (30 minutes, closed book)

Answer from memory: What's an OVD (list them)? What are the three OTP e-KYC monetary
limits and the one-year rule? How often is KYC updated for high/medium/low risk? How long
are records kept, from when? Who can V-CIP be used for? What's a PEP and what extra steps
apply? — If you can answer these cold, you're safe on domain questions.

### Getting an LLM key (free)

The answer step needs a language model. Get a **free Gemini key** at
https://aistudio.google.com/apikey (Google login, "Create API key", copy it),
then in the repo folder run — substituting your key:

```bash
echo 'GEMINI_API_KEY=paste-your-key-here' > .env
```

`.env` is gitignored, so the key never leaves your machine. Test it:
`python src/ask.py "Can I open an account over a video call?" --show-chunks`

## Step 4 — Own the build (Phases 1–5)

From Phase 1 onward, **you run everything yourself**: type the commands, run each
experiment, record results in `LAB_NOTEBOOK.md` in your own words. The experiment table
(recall climbing run by run) is only defensible if the runs were yours. Rule of thumb:
never commit a result you didn't personally execute.

Strongly recommended: re-implement ONE core component from scratch yourself after it
exists — BM25 (~60 lines) is the designated one. "I wrote the BM25 implementation" is a
sentence you want to be able to say truthfully.

## Step 5 — Rehearse (before placement season)

- Do the 90-second demo out loud, 5 times.
- Have someone grill you with the mock questions below.

### Mock interview questions (the ones that actually get asked)

1. Why RAG instead of just asking the LLM directly?
2. Walk me through what happens from question to answer.
3. Why did you chunk by clause instead of fixed size? What changed when you did?
4. What is recall@5 and why is it your retrieval metric?
5. Why hybrid search — what does BM25 catch that embeddings miss, and vice versa?
6. How do you stop the system from hallucinating a compliance answer?
7. How do you handle the fact that RBI amends this document? (Point at the footnotes.)
8. What breaks at 100x more documents? What would you change?
9. What was the hardest bug / most surprising result?
10. What's your cost per query and where does the money go?

Answers to 1–7 are all in this repo's guides and your lab notebook. 8–10 come from doing
Phase 3–5 yourself.
