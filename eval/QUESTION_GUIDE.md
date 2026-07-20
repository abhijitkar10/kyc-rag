# How to Write Your 20 Eval Questions

These 20 rows are the **answer key your entire system gets graded against** — every experiment
number in the project inherits its trustworthiness from the care you take here.
Write them in `eval/questions.csv` (two example rows are already seeded — follow that format).

## The columns

| Column | What goes in it |
|---|---|
| `id` | 1, 2, 3, ... |
| `question` | The question, phrased the way a *person* would ask it |
| `answer_in_own_words` | The answer as YOU understand it — never copy-pasted document text |
| `source_doc` | `kyc-master-direction` (all of them, for now) |
| `clause_ref` | Exact location you verified: e.g. `Section 17(iii)` or `Section 3(a)(vi)` |
| `answerable` | `yes`, or `no` for trick questions |

## The recipe — 20 questions in 5 flavors

| # | Flavor | How to write it |
|---|---|---|
| 6 | **Direct lookups** | Question uses roughly the document's own vocabulary. "What is the aggregate balance limit for accounts opened via Aadhaar OTP e-KYC?" These test basic retrieval. |
| 6 | **Paraphrased / everyday language** | Same kind of fact, but phrased like a normal person — deliberately avoiding the document's words. "Can I open a bank account over a video call?" (doc says "V-CIP", you didn't). These honestly test *semantic* search — they're the rows where keyword search will fail and embeddings must carry. **Rule: if your question reuses the clause's exact key terms, rewrite it.** |
| 3 | **Numbers & thresholds** | Rupee limits, percentages, years, deadlines. Precise, unambiguous, easy to grade. |
| 2 | **Amendment-aware** | Questions touching things the footnotes say changed. "Which circular amended the V-CIP rules, and when?" These seed Phase 4. |
| 3 | **Trick (unanswerable)** — `answerable=no` | Plausible-adjacent, NOT absurd. Good: "What are the tax benefits under Section 80C?" / "What are SEBI's KYC rules for opening a demat account?" / "What KYC does an insurance company need?" — all *feel* nearby but are outside this corpus. Bad: "What's the capital of France?" (too easy to refuse; teaches you nothing about the threshold). |

## Quality rules

1. **Verify every clause_ref yourself.** Open the PDF, find the clause, confirm the answer.
   If you can't point to it, the question doesn't go in.
2. **One home per answer.** Prefer questions whose answer lives in ONE clause — makes grading
   ("did the right chunk appear?") unambiguous. If an answer genuinely spans two clauses,
   note both refs separated by `;`.
3. **Own words in the answer column.** If you can't write the answer without looking, you
   don't know it yet — reread the clause. (This is also interview rehearsal.)
4. **Spread across chapters.** Don't let all 20 come from Section 16–18; pull some from
   definitions (Ch I), record-keeping (Ch VII), periodic updation (Ch VI Part V).
5. **Write them while reading**, not after — the best questions are the ones that occur to
   you naturally as "huh, I didn't know that."

## Done when

20 rows, every `clause_ref` personally verified, at least 5 phrased in vocabulary the
document doesn't use, 3 trick questions that would genuinely tempt a naive system to answer.
Then commit: `git add -A && git commit -m "phase 0: 20 verified eval questions"`
