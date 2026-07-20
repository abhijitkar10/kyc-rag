# Reading Guide — RBI KYC Master Direction (updated Aug 14, 2025)

Your copy: `data/raw/kyc-master-direction-2025-08-14.pdf` — 107 pages, 17 updates since 2016.
Goal of this guide: turn two intimidating evenings into a structured walkthrough.
Page numbers below are the **printed** page numbers (bottom of each page), verified against the actual PDF.

## How this document works (read this first)

- **It's consolidated**: every amendment since 2016 is already merged into the text.
- **Amendments are marked with footnotes**: a superscript number in the text → footnote at the
  bottom naming the exact circular and date (e.g. *"Amended vide circular DOR.AML.REC.46/14.01.001/2025-26
  dated August 14, 2025"*). **These footnotes are your Phase 4 versioning gold** — when you
  deep-read a section, jot down which circulars touched it.
- Page 1 lists all 17 update dates. Page 2 is the table of contents.
- Key vocabulary: **RE** = Regulated Entity (any bank/NBFC/fintech RBI supervises — i.e. "the company").
  **CDD** = Customer Due Diligence (the actual checking process). **OVD** = Officially Valid Document.

## Pass 1 — the skim (~40 minutes, do once)

Don't read; *map*. Look at page 1's update list, the TOC on page 2, read the 1-page
Introduction (p.3), then flip through the whole PDF noticing chapter starts and how
footnotes look. Done. You now know the shape of the book.

## Pass 2 — the deep read (priority map)

| Chapter | Pages | Priority | What it is / what to capture |
|---|---|---|---|
| Introduction | 3 | **Read fully** (1 page) | Why the rulebook exists: PMLA 2002, FATF. Gives you the interview-ready origin story. |
| **Ch I — Preliminary (Definitions, Section 3)** | 4–14 | **DEEP** | The dictionary everything else uses. Nail: **OVD** (the exact document list), **Beneficial Owner** (note the ownership % thresholds differ by entity type — company vs partnership vs trust), Certified Copy, Digital KYC, e-KYC authentication, V-CIP, Regulated Entity. |
| Ch II — General | 15–18 | Medium | The four elements every KYC policy must have. |
| Ch III — Customer Acceptance Policy | 19–20 | Medium (short) | What REs must/must-not do when taking customers. |
| Ch IV — Risk Management | 21 | Quick | Risk categorization of customers. |
| Ch V — Customer Identification Procedure | 22–23 | Quick | *When* identification must happen. |
| **Ch VI — CDD Procedure** | 24–48 | **THE HEART — DEEP** | See breakdown below. |
| Ch VII — Record Management | 49–50 | Quick but **quizzable** | Retention periods (note the exact number of years). |
| Ch VIII — Reporting to FIU-India | 51–52 | Quick | STR/CTR reporting — know what the acronyms mean. |
| Ch IX — International Agreements | 53–56 | Skim | UAPA/sanctions screening context. |
| Ch X — Other Instructions | 57–69 | Skim + spot-read | Grab-bag; includes CKYCR (central KYC registry) mechanics and periodic-updation details. Spot-read anything your Ch VI reading referenced (e.g. "paragraph 56"). |
| Ch XI — Repeal | 70 | Skip | |
| Annexes I–IV | 71–96 | Skim titles | Annex I = the Digital KYC process (Section 16 points here). Note what each annex is so you know where detail lives. |
| Appendix | 97+ | Skip | List of repealed circulars. |

### Chapter VI breakdown (pages 24–48) — spend most of your time here

- **Part I — Individuals (p.24–34). The most quizzable pages in the document:**
  - **Section 16** (p.24): the master list of what an RE must collect — Aadhaar routes,
    proof-of-possession, OVD, KYC Identifier from CKYCR, **plus PAN or Form 60**. Notice the
    (a)/(aa)/(ab)/(ac) structure — each is a different route to identity.
  - **Section 17** (p.26): accounts opened with **Aadhaar OTP e-KYC** — a fully number-loaded
    section: consent requirement, balance cap, yearly credit cap, term-loan cap, the one-year
    deadline and what happens if it's missed, the "no other OTP account" declaration.
  - **Section 18** (p.27): **V-CIP (video KYC)** — who it can be used for and its conditions.
- Part II — Sole proprietary firms (p.34); Part III — Legal entities (p.35–37): medium; note
  what *extra* documents entities need.
- Part IV — Beneficial Owner (p.38): ties back to the Ch I definition.
- **Part V — Ongoing Due Diligence (p.38–44)**: periodic KYC updation — timelines by risk
  category are classic eval-question material.
- Part VI — Enhanced & Simplified DD (p.45–48): PEPs (politically exposed persons),
  high-risk cases, when *less* diligence is allowed.

## What to capture while reading (your notes file)

1. **Every number**: rupee thresholds, percentages, years, deadlines → best eval questions.
2. **Every acronym** the first time it appears: RE, CDD, OVD, CKYCR, V-CIP, STR, CTR, PEP, BO.
3. **Footnoted amendments** on sections you deep-read: which circular, what date → Phase 4 fuel.
4. Anything that surprises you → those make the most natural interview talking points.

## Self-check prompts (answer from memory after each session; look up what you miss)

- After Ch I: What exactly counts as an OVD? At what ownership % does someone become a
  beneficial owner of a company — and is it the same for a partnership?
- After Ch VI Part I: What are the different *routes* a customer can take through Section 16?
  What three monetary limits apply to OTP e-KYC accounts, and what's the deadline attached?
  Who can V-CIP be used for?
- After Ch VI Part V: How often must KYC be updated for high-risk vs low-risk customers?
- After Ch VII: How long must records be kept, counted from when?

## Suggested schedule

- **Evening 1**: Pass 1 skim + Ch I definitions (deep) + Intro. Write acronym list.
- **Evening 2**: Ch VI in full (deep on Part I and Part V). Capture every number.
- **Evening 3** (lighter): Ch II–V, VII, VIII at their priorities + annex titles → then start
  writing questions with `eval/QUESTION_GUIDE.md` open beside you.

## Amendment circulars (needed for Phase 4, not now)

RBI's document server blocks scripted downloads, so grab these manually in your browser
when Phase 4 approaches (each page has a PDF link at the top):
- Aug 14, 2025 amendment: https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=12893&Mode=0 → save as `data/raw/amendment-2025-08-14.pdf`
- Jun 12, 2025 amendment: https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=12866&Mode=0 → save as `data/raw/amendment-2025-06-12.pdf`
- Earlier amendment (from the MD's own footnotes): https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=12746&Mode=0 → save as `data/raw/amendment-2024.pdf`
