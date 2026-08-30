"""Thin FastAPI app + a single self-contained web page for the demo.

    uvicorn app:app --reload --app-dir src     # then open http://127.0.0.1:8000

GET  /          -> the demo page
POST /ask       -> {question} -> {answer, retrieved_pages, provider, latency_ms}
GET  /amendments-> the amendment timeline (versioning showcase)
"""

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

 <div class="examples">
   <p class="hint">Try:</p>
   <button class="ex" onclick="fill(this.textContent)">What are the three monetary limits on Aadhaar OTP e-KYC accounts?</button>
   <button class="ex" onclick="fill(this.textContent)">Can I open a bank account over a video call?</button>
   <button class="ex" onclick="fill(this.textContent)">What are the tax benefits under Section 80C?</button>
 </div>

 <div id="out"></div>

 <footer>Retrieval: hybrid dense&#8202;+&#8202;BM25 with cross-encoder re-ranking &middot;
 recall@5&nbsp;0.93 on a 50-question hand-verified set &middot; citations verified against
 retrieved context.</footer>
</main>
<script>
 function fill(t){const q=document.getElementById('q');q.value=t.trim();q.focus()}
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
