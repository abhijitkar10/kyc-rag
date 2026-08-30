"""Thin FastAPI app + a single self-contained web page for the demo.

    uvicorn app:app --reload --app-dir src     # then open http://127.0.0.1:8000

GET  /          -> the demo page
POST /ask       -> {question} -> {answer, retrieved_pages, provider, latency_ms}
GET  /amendments-> the amendment timeline (versioning showcase)
GET  /questions -> the eval set, grouped by category (what each case tests)
"""

import csv
import sys
import time
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent))
import amendments  # noqa: E402
import llm  # noqa: E402
from answer import answer  # noqa: E402

app = FastAPI(title="RBI KYC Compliance Assistant")


class Ask(BaseModel):
    question: str


@app.post("/ask")
def ask(body: Ask):
    t0 = time.perf_counter()
    text = answer(body.question)
    try:
        provider = " ".join(llm.provider())
    except Exception:
        provider = "unknown"
    return {
        "answer": text,
        "provider": provider,
        "latency_ms": round((time.perf_counter() - t0) * 1000),
    }


@app.get("/amendments")
def amendment_timeline():
    return [{"date": d, "circular": c, "pages_touched": n}
            for d, c, n in amendments.timeline()]


# What each eval category is designed to test. Shown in the UI so a reader can see
# the eval set covers distinct failure modes, not 50 variations of one easy question.
CATEGORY_INFO = [
    ("direct", "Direct lookup",
     "Asked using the document's own vocabulary. Tests basic retrieval."),
    ("paraphrase", "Paraphrased",
     "Everyday wording that deliberately avoids the document's terms — the doc says "
     "\u201cV-CIP\u201d, the question says \u201cvideo call\u201d. This is what "
     "keyword search alone fails, so it tests the semantic half of retrieval."),
    ("numeric", "Threshold / limit",
     "A specific rupee cap, percentage, deadline or timeline. Unambiguous to grade, "
     "and the answer is easy to get subtly wrong by pulling a similar-looking number "
     "from a different account type."),
    ("entity", "Entity-specific",
     "Document requirements that differ by customer type (company, partnership, trust, "
     "sole proprietor). Tests whether retrieval keeps near-identical clauses apart."),
    ("amendment", "Amendment / provenance",
     "Which circular changed a clause, and when. The answer lives in small footnote "
     "text, which makes it the hardest category to retrieve."),
    ("trick", "Out of corpus \u2014 must refuse",
     "Plausible, adjacent, and NOT in this document (income tax, SEBI, IRDAI, crypto). "
     "The correct behaviour is to refuse, not to answer from a loosely-related clause."),
]


@app.get("/questions")
def questions():
    """The eval set, grouped by category — read live from eval/questions.csv."""
    path = Path(__file__).resolve().parent.parent / "eval" / "questions.csv"
    rows = list(csv.DictReader(path.open()))
    out = []
    for key, title, why in CATEGORY_INFO:
        items = [{"id": int(r["id"]), "question": r["question"],
                  "clause": r["clause_ref"] or None}
                 for r in rows if r.get("category") == key]
        if items:
            out.append({"key": key, "title": title, "why": why,
                        "count": len(items), "questions": items})
    return {"total": len(rows), "groups": out}


PAGE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>KYC Master Direction — Compliance Assistant</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
 /* Design intent: this is a tool for reading regulation, so it should look like a
    legal document, not a SaaS landing page. Serif for prose, sans for controls,
    footnote-style citations, paper/ink palette, near-square corners. */
 :root{
   --paper:#f7f5ef; --ink:#1c1b18; --muted:#6d6862; --rule:#ddd7ca;
   --ref:#1e4b7a;   /* citation blue, like a legal cross-reference */
   --flag:#8a2f22;  /* unverified / warning */
 }
 *{box-sizing:border-box}
 body{
   background:var(--paper); color:var(--ink); margin:0;
   font:16px/1.62 Charter,"Iowan Old Style","Palatino Linotype",Georgia,serif;
 }
 .sheet{max-width:40rem;margin:0 auto;padding:3rem 1.5rem 4rem}
 .eyebrow{
   font-family:ui-sans-serif,-apple-system,"Segoe UI",sans-serif;
   font-size:.68rem;letter-spacing:.14em;text-transform:uppercase;
   color:var(--muted);margin:0 0 .35rem
 }
 h1{font-size:1.5rem;font-weight:600;line-height:1.25;margin:0 0 .5rem}
 .lede{color:var(--muted);margin:0 0 1.25rem;font-size:.95rem}
 hr{border:0;border-top:1px solid var(--rule);margin:0 0 1.5rem}
 label{
   display:block;font-family:ui-sans-serif,-apple-system,sans-serif;
   font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;
   color:var(--muted);margin-bottom:.4rem
 }
 textarea{
   width:100%;padding:.65rem .7rem;border:1px solid #c9c2b4;border-radius:2px;
   background:#fffdf8;color:inherit;font:inherit;resize:vertical
 }
 textarea:focus{outline:2px solid var(--ref);outline-offset:-1px;border-color:var(--ref)}
 .row{display:flex;align-items:baseline;gap:1rem;margin-top:.7rem;flex-wrap:wrap}
 button{
   font-family:ui-sans-serif,-apple-system,sans-serif;font-size:.85rem;
   letter-spacing:.03em;padding:.5rem 1.15rem;border:1px solid var(--ink);
   border-radius:2px;background:var(--ink);color:var(--paper);cursor:pointer
 }
 button:hover:not(:disabled){background:#000}
 button:disabled{background:#a09a90;border-color:#a09a90;cursor:default}
 .hint{font-family:ui-sans-serif,sans-serif;font-size:.75rem;color:var(--muted)}
 .examples{margin-top:1.4rem}
 .examples p{margin:0 0 .3rem}
 .ex{
   display:block;background:none;border:0;padding:.12rem 0;text-align:left;
   font:inherit;font-size:.9rem;color:var(--ref);cursor:pointer;
   text-decoration:underline;text-underline-offset:2px;letter-spacing:0
 }
 .ex:hover{color:#12365a;background:none}
 #out{
   margin-top:1.6rem;padding-top:1.1rem;border-top:1px solid var(--rule);
   white-space:pre-wrap;min-height:1.5rem
 }
 #out:empty{border-top:0;padding-top:0;margin-top:0}
 .cite{
   font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.78em;
   color:var(--ref);border-bottom:1px solid #c3d3e2;padding-bottom:1px;
   white-space:nowrap
 }
 .warn{color:var(--flag);font-style:italic}
 .meta{
   font-family:ui-sans-serif,sans-serif;font-size:.72rem;color:var(--muted);
   margin-top:1rem;padding-top:.5rem;border-top:1px dotted var(--rule)
 }
 footer{
   margin-top:2.5rem;padding-top:.9rem;border-top:1px solid var(--rule);
   font-family:ui-sans-serif,sans-serif;font-size:.72rem;color:var(--muted)
 }
 /* eval-set browser */
 .evalhead{margin-top:2.2rem;padding-top:1.1rem;border-top:1px solid var(--rule)}
 details{border-bottom:1px solid var(--rule);padding:.55rem 0}
 details[open]{padding-bottom:.9rem}
 summary{
   cursor:pointer;list-style:none;display:flex;align-items:baseline;gap:.5rem;
   font-family:ui-sans-serif,-apple-system,sans-serif;font-size:.86rem
 }
 summary::-webkit-details-marker{display:none}
 summary::before{content:"+";color:var(--muted);font-weight:600;width:.8rem}
 details[open] summary::before{content:"\2013"}
 .n{
   margin-left:auto;font-variant-numeric:tabular-nums;font-size:.72rem;
   color:var(--muted);letter-spacing:.06em
 }
 .why{
   font-size:.85rem;color:var(--muted);margin:.5rem 0 .7rem 1.3rem;
   padding-left:.7rem;border-left:2px solid var(--rule)
 }
 ol.qs{margin:0 0 0 1.3rem;padding-left:1rem}
 ol.qs li{margin:.22rem 0}
 ol.qs button{
   background:none;border:0;padding:0;text-align:left;font:inherit;font-size:.9rem;
   color:var(--ref);cursor:pointer;text-decoration:underline;text-underline-offset:2px
 }
 ol.qs button:hover{color:#12365a;background:none}
 .clause{font-size:.72rem;color:var(--muted);font-family:ui-sans-serif,sans-serif}
</style></head><body>
<main class="sheet">
 <p class="eyebrow">Reserve Bank of India &middot; Master Direction on KYC, 2025</p>
 <h1>Compliance Assistant</h1>
 <p class="lede">Every answer is drawn only from the Master Direction and carries the page it
 came from. Questions outside the document are declined rather than guessed at.</p>
 <hr>

 <label for="q">Your question</label>
 <textarea id="q" rows="2" placeholder="Which documents are accepted as proof of identity?"></textarea>
 <div class="row">
   <button id="go" onclick="ask()">Look it up</button>
   <span class="hint">&#8984;&#8629; to submit</span>
 </div>

 <div id="out"></div>

 <section class="evalhead">
   <p class="eyebrow">The evaluation set &middot; <span id="qtotal">50</span> questions, every answer verified against the PDF by hand</p>
   <p class="lede" style="font-size:.88rem">These are the questions the system is scored on \u2014 grouped by the failure
   mode each one is designed to probe. Click any question to run it.</p>
   <div id="groups"></div>
 </section>

 <footer>Retrieval: hybrid dense&#8202;+&#8202;BM25 with cross-encoder re-ranking &middot;
 recall@5&nbsp;0.93 on a 50-question hand-verified set &middot; citations verified against
 retrieved context.</footer>
</main>
<script>
 function fill(t){
   const q=document.getElementById('q'); q.value=t.trim();
   q.scrollIntoView({behavior:'smooth',block:'center'}); q.focus();
 }
 const esc=t=>t.replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
 async function loadQuestions(){
   try{
     const d=await (await fetch('/questions')).json();
     document.getElementById('qtotal').textContent=d.total;
     document.getElementById('groups').innerHTML=d.groups.map(g=>
       '<details><summary><strong>'+esc(g.title)+'</strong>'+
       '<span class="n">'+g.count+'</span></summary>'+
       '<p class="why">'+esc(g.why)+'</p><ol class="qs">'+
       g.questions.map(q=>'<li><button onclick="fill(this.textContent)">'+
         esc(q.question)+'</button>'+
         (q.clause?' <span class="clause">'+esc(q.clause)+'</span>':'')+'</li>').join('')+
       '</ol></details>').join('');
   }catch(e){
     document.getElementById('groups').innerHTML=
       '<p class="hint">Could not load the eval set: '+esc(String(e))+'</p>';
   }
 }
 loadQuestions();
 async function ask(){
  const q=document.getElementById('q').value.trim(); if(!q)return;
  const btn=document.getElementById('go'), out=document.getElementById('out');
  btn.disabled=true; out.textContent='Searching the Master Direction\u2026';
  try{
   const r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});
   const d=await r.json();
   let html=d.answer
     .replace(/\[KYC Master Direction, p\.(\d+)\]/g,'<span class="cite">p.$1</span>')
     .replace(/\[\u26a0[^\]]*\]/g,m=>'<span class="warn">'+m+'</span>');
   out.innerHTML=html+'<div class="meta">'+d.provider+' &middot; '+d.latency_ms+'&#8202;ms</div>';
  }catch(e){out.textContent='Error: '+e}
  btn.disabled=false;
 }
 document.getElementById('q').addEventListener('keydown',e=>{if(e.key==='Enter'&&(e.metaKey||e.ctrlKey))ask()});
</script></body></html>"""


@app.get("/", response_class=HTMLResponse)
def home():
    return PAGE
