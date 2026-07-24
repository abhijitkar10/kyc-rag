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


PAGE = """<!doctype html><html><head><meta charset="utf-8">
<title>RBI KYC Compliance Assistant</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
 body{font:16px/1.6 system-ui,sans-serif;max-width:760px;margin:2rem auto;padding:0 1rem;color:#1a1a1a}
 h1{font-size:1.4rem} .sub{color:#666;margin-top:-.5rem}
 textarea{width:100%;padding:.7rem;font:inherit;border:1px solid #ccc;border-radius:8px;box-sizing:border-box}
 button{margin-top:.6rem;padding:.6rem 1.2rem;font:inherit;border:0;border-radius:8px;background:#0b5;color:#fff;cursor:pointer}
 button:disabled{background:#999}
 #out{margin-top:1.2rem;padding:1rem;border:1px solid #eee;border-radius:8px;background:#fafafa;white-space:pre-wrap;min-height:2rem}
 .cite{color:#0a6;font-weight:600} .warn{color:#c40} .meta{color:#888;font-size:.85rem;margin-top:.5rem}
 .ex{color:#06c;cursor:pointer;text-decoration:underline;font-size:.9rem;margin-right:1rem}
</style></head><body>
<h1>RBI KYC Compliance Assistant</h1>
<p class="sub">Answers grounded in the RBI Master Direction on KYC (2025), with clause-level citations. Refuses when the answer isn't in the corpus.</p>
<textarea id="q" rows="2" placeholder="e.g. Can I open a bank account over a video call?"></textarea>
<div><button id="go" onclick="ask()">Ask</button></div>
<div style="margin-top:.6rem">
 <span class="ex" onclick="fill('What are the three monetary limits on Aadhaar OTP e-KYC accounts?')">example: OTP limits</span>
 <span class="ex" onclick="fill('Can I finish KYC over a video call?')">example: video KYC</span>
 <span class="ex" onclick="fill('What are the tax benefits under Section 80C?')">example: out-of-scope</span>
</div>
<div id="out"></div>
<script>
 function fill(t){document.getElementById('q').value=t}
 async function ask(){
  const q=document.getElementById('q').value.trim(); if(!q)return;
  const btn=document.getElementById('go'), out=document.getElementById('out');
  btn.disabled=true; out.textContent='Retrieving + reasoning…';
  try{
   const r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});
   const d=await r.json();
   let html=d.answer
     .replace(/\\[KYC Master Direction, p\\.(\\d+)\\]/g,'<span class="cite">[p.$1]</span>')
     .replace(/\\[⚠[^\\]]*\\]/g,m=>'<span class="warn">'+m+'</span>');
   out.innerHTML=html+'<div class="meta">'+d.provider+' · '+d.latency_ms+' ms</div>';
  }catch(e){out.textContent='Error: '+e}
  btn.disabled=false;
 }
 document.getElementById('q').addEventListener('keydown',e=>{if(e.key==='Enter'&&(e.metaKey||e.ctrlKey))ask()});
</script></body></html>"""


@app.get("/", response_class=HTMLResponse)
def home():
    return PAGE
