# Eval Set v2 — 20 new questions (worksheet)

Extends the eval set from 50 → 70, covering parts of the Master Direction the first 50 don't.
**These are stems, not answers.** For each: open `data/raw/kyc-master-direction-2025-08-14.pdf`
to the pointed page, read that clause, then append a row to `eval/questions.csv` (ids 51–70) with
your **final question wording** and the answer **in your own words**, plus the `clause_ref` you
verified. ~2 focused hours. Then run `./run.sh eval` and commit.

Doing the verification yourself is the point — it's what makes "built and verified the 70-question
evaluation set" a true line you can defend.

CSV columns: `id,question,answer_in_own_words,source_doc,clause_ref,answerable`
(`source_doc` = `kyc-master-direction` for all; `answerable` = `yes` or `no`).

Rules that still apply: own-words answers; for PARAPHRASE rows don't reuse the banned words; if a
pointer looks wrong when you read it, trust the PDF and fix the ref (note the catch).

---

## Direct lookups (8) — may use the document's vocabulary

| # | Look at | Turn into a question about… |
|---|---|---|
| 51 | Para 3(a)(vi), p.7 | what the **Central KYC Records Registry (CKYCR)** is. |
| 52 | Para 3(a)(xix), p.9–10 | how the Direction **defines a "suspicious transaction"** (the four grounds). |
| 53 | Para 3(b)(xv), p.13 | what a **"shell bank"** is. |
| 54 | Para 14, p.22–23 | the conditions under which an RE may **rely on CDD done by a third party** (records obtained immediately; third party regulated; not in a high-risk jurisdiction; ultimate responsibility stays with the RE). |
| 55 | Para 33A, p.37 | the documents needed to open an account for an **unincorporated association / body of individuals**. |
| 56 | Para 43, p.47 | the **simplified KYC norms for Self Help Groups (SHGs)** (CDD of all members not required; office bearers suffice). |
| 57 | Para 10(j) and 10(l), p.19–20 | how an RE must **verify PAN and GST** details (from the issuing authority's verification facility). |
| 58 | Para 8, p.17–18 | what the KYC policy must ensure about **compliance functions** (decision-making not outsourced; concurrent/internal audit; quarterly audit notes). |

## Paraphrased (4) — phrase WITHOUT the banned words

| # | Look at | Phrase without… |
|---|---|---|
| 59 | Para 24, p.33 | opening an account when you **can't produce the usual ID documents** at an NBFC. **Banned: "NBFC", "para 16", "self-attested".** |
| 60 | Para 18(b)(ix), p.31 | whether a **printed print-out of a downloaded PAN** works for video KYC. **Banned: "e-PAN", "equivalent e-document", "V-CIP".** |
| 61 | Para 39, p.44 | what happens to your **existing account if you refuse to give your PAN**. **Banned: "cease operations", "Form 60".** |
| 62 | Para 4(b), p.15 | why a bank that's **part of a larger group** must share information group-wide. **Banned: "group-wide", "tipping-off".** |

## Numbers & thresholds (3)

| # | Look at | Turn into a question about… |
|---|---|---|
| 63 | Para 44, p.48 | the caps on a **foreign student's NRO account** in the first 30 days (foreign remittances ≤ USD 1,000; aggregate ≤ ₹50,000; local-address declaration within 30 days). |
| 64 | Para 23(g), p.34 | the **balance / yearly-credit levels that trigger a "complete full KYC" notice** on a Small Account (₹40,000 balance or ₹80,000 credits). |
| 65 | Para 44(c), p.48 | the **nationality that needs prior RBI approval** before opening a foreign-student account. |

## Amendment-aware (2) — run `./run.sh amendments` to cross-check

| # | Look at | Turn into a question about… |
|---|---|---|
| 66 | Para 10(f) footnote, p.19 | which circular introduced **CDD at the UCIC level**, and when (DOR.AML.REC.49, **November 6, 2024**). |
| 67 | `./run.sh amendments` output | which single circular is the **largest amendment by pages touched**, and when (DOR.AML.REC.111, **April 28, 2023** — 42 pages). |

## Trick / out-of-corpus (3) — `answerable = no`

| # | Write a question about | Why it's a good trick |
|---|---|---|
| 68 | the **GST registration turnover threshold** for a business | GST is *named* in the doc as an acceptable document, but the threshold is GST law, not KYC. |
| 69 | **RBI's rules on credit-card interest rates** | right regulator, wrong rulebook — not in this Master Direction. |
| 70 | the **foreign-currency limit under LRS** (Liberalised Remittance Scheme) | FEMA territory, not KYC — should be refused. |

---

## When done
- 20 new rows (51–70) in `questions.csv`, every `clause_ref` personally verified.
- `./run.sh eval` runs clean over 70 questions (recall may shift — that's expected and fine).
- Commit: `git add eval/questions.csv && git commit -m "eval: expand set to 70 questions (v2)"`
  then push from your fork.
