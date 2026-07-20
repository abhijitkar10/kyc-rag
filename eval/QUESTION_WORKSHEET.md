# Question Worksheet — 20 designed stems, you finish each one

For every row: open the PDF to the pointed page, read that clause, then write into
`eval/questions.csv` (1) your final phrasing of the question and (2) the answer **in your
own words**, plus the exact `clause_ref` you verified. Rough time: ~2 focused hours.

Rules that still apply: own-words answers; for PARAPHRASE rows, do NOT use the banned
words in your question; if a pointer seems wrong when you read the page, trust the PDF
and fix the ref — then note it, that's a good catch.

---

## Direct lookups (6) — question may use the document's vocabulary

| # | Look at | Find & turn into a question |
|---|---|---|
| 1 | p.4–5, Section 3 definitions | The list of documents that count as **OVDs**. Question: which documents are OVDs for an individual? |
| 2 | p.24, Section 16 | What an RE must obtain from an individual at account opening — note the (a)/(aa)/(ab)/(ac) routes **plus** the PAN/Form 60 requirement. Question: what must be collected? |
| 3 | p.27, Section 18 | Who V-CIP can be used for (individuals, proprietors, authorised signatories, BOs of legal entities). Question: for whom can an RE use V-CIP? |
| 4 | Ch VII, p.49–50 | The record-retention period and from when it counts. Question: how long must transaction records be preserved? |
| 5 | Ch VI Part V, p.38–44 | The periodic KYC-updation timelines by risk category (high/medium/low). Question: how often must KYC be updated for each risk level? |
| 6 | Ch VIII, p.51–52 | What STR and/or CTR reporting means and to whom reports go. Question: what reports must REs file with FIU-India? |

## Paraphrased / everyday language (6) — banned words listed per row

| # | Look at | Find & phrase WITHOUT the banned words |
|---|---|---|
| 7 | p.27, Section 18 | Video account opening. **Banned: "V-CIP", "Customer Identification Process".** e.g. "Can I finish my bank KYC over a video call?" |
| 8 | p.4–5, Section 3 (OVD def.) | Whether a driving licence works as ID proof. **Banned: "OVD", "Officially Valid Document".** |
| 9 | p.26, Section 17 | Opening an account with just an Aadhaar OTP on your phone. **Banned: "e-KYC", "OTP based e-KYC", "non-face-to-face".** |
| 10 | p.5–6, Section 3 (Beneficial Owner def.) | Who the "real owner" behind a company account is. **Banned: "beneficial owner", "controlling ownership interest".** |
| 11 | p.24–25, Section 16 proviso (digital KYC / e-documents) | Using digital copies instead of physical photocopies. **Banned: "equivalent e-document", "Digital KYC".** |
| 12 | Ch VI Part VI, p.45–48 | Extra checks for politicians/public figures. **Banned: "PEP", "Politically Exposed Person", "Enhanced Due Diligence".** |

## Numbers & thresholds (3) — precise, easy to grade

| # | Look at | Find & turn into a question |
|---|---|---|
| 13 | p.26–27, Section 17 (iii)–(v) | The three monetary caps on OTP e-KYC accounts (aggregate balance / yearly credits / term-loan amount). Pick ONE cap per question — or ask for all three in one question, your call. |
| 14 | p.27, Section 17 (vi)–(vii) | The one-year deadline: what must happen within a year, and what happens to the account if it doesn't. |
| 15 | p.5–6, Section 3 (Beneficial Owner) | The ownership percentages that make someone a BO — note they DIFFER by entity type (company vs partnership vs unincorporated association vs trust). |

## Amendment-aware (2) — the versioning seeds

| # | Look at | Find & turn into a question |
|---|---|---|
| 16 | p.26 footnote 58, Section 17 Explanation 2 | Which circular (and date) amended the rules on Aadhaar **Face Authentication** for e-KYC. (You'll see: Aug 14, 2025.) |
| 17 | p.27 footnote 62, Section 18 | Which circular (and date) amended the V-CIP provisions. (You'll see: May 10, 2021.) |

## Trick questions (3) — `answerable=no`, adjacent-but-outside the corpus

| # | Write a question about | Why it's a good trick |
|---|---|---|
| 18 | Income-tax saving under Section 80C | "Section" + finance vocabulary — tempts a naive system to answer from KYC clauses |
| 19 | SEBI's KYC requirements for opening a demat account | KYC is literally in the question, but SEBI's rules are not in this corpus |
| 20 | KYC rules for buying a life-insurance policy (IRDAI) | Same trap: right topic, wrong regulator |

---

## When done

- 20 rows in `questions.csv`, every `clause_ref` personally checked against the PDF.
- Quick self-test: close everything and answer #1, #5, #13 from memory. If you can, you're
  interview-ready on the basics.
- Commit: `git add -A && git commit -m "phase 0: 20 verified eval questions"` → then say
  "review my questions" and after review we start Phase 1.
