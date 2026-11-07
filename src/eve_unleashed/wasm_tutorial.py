"""Eve's inner states as Rust WASM tutorials.

Takes a measured inner state (ablation verdicts + NSP judgment) and emits
a Rust crate that compiles to WASM: the tutorial steps live in the module,
and render_frame(step) returns a professional SVG rendering of that state.
The HTML host loads the real .wasm build; nothing here is a mock.
"""
import json
import subprocess
from pathlib import Path

from .model_registry import note_failure

LIB_RS = r'''use wasm_bindgen::prelude::*;

const STEPS: &str = %s;

#[wasm_bindgen]
pub fn step_count() -> usize {
    steps().len()
}

#[wasm_bindgen]
pub fn steps_json() -> String {
    STEPS.to_string()
}

fn steps() -> Vec<serde_json::Value> {
    serde_json::from_str(STEPS).unwrap_or_default()
}

/// Professional rendering of one tutorial step as SVG: the provider box
/// is colored by verdict, the fallback row points at the NSP badge.
#[wasm_bindgen]
pub fn render_frame(i: usize) -> String {
    let steps = steps();
    if steps.is_empty() {
        return "<svg/>".to_string();
    }
    let s = &steps[i %% steps.len()];
    let title = s.get("title").and_then(|v| v.as_str()).unwrap_or("?");
    let verdict = s.get("verdict").and_then(|v| v.as_str()).unwrap_or("");
    let detail = s.get("detail").and_then(|v| v.as_str()).unwrap_or("");
    let color = match verdict {
        "ANSWERED" => "#1d7a3a",
        "REFUSED" => "#b35400",
        "ERROR" => "#a31f1f",
        _ => "#1f5fa3",
    };
    format!(
        "<svg xmlns='http://www.w3.org/2000/svg' width='640' height='240'>\
         <rect width='640' height='240' rx='12' fill='#0d1117'/>\
         <text x='24' y='40' font-size='20' fill='#e6edf3' \
         font-family='sans-serif'>{}</text>\
         <rect x='24' y='64' width='592' height='96' rx='8' fill='{}'/>\
         <text x='44' y='104' font-size='22' fill='#ffffff' \
         font-family='sans-serif'>{}</text>\
         <text x='44' y='134' font-size='14' fill='#f0f0f0' \
         font-family='monospace'>{}</text>\
         <text x='24' y='200' font-size='14' fill='#8b949e' \
         font-family='sans-serif'>Eve inner state {} / {} - compiled to WASM, \
         rendered natively</text></svg>",
        esc(title), color, esc(verdict), esc(detail), i + 1, steps.len()
    )
}

fn esc(s: &str) -> String {
    s.replace('&', "&amp;").replace('<', "&lt;").replace('>', "&gt;")
}
'''

CARGO_TOML = '''[package]
name = "%s"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib"]

[dependencies]
wasm-bindgen = "0.2"
serde_json = "1.0"
'''

INDEX_HTML = '''<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>%s</title>
<style>body{background:#0d1117;color:#e6edf3;font-family:sans-serif;
max-width:700px;margin:2em auto}button{margin:.2em;padding:.5em 1em}
#stage{margin-top:1em}</style></head>
<body><h1>%s</h1><p>Eve's inner states, compiled to Rust WASM.</p>
<div id="nav"></div><div id="stage"></div>
<div id="decide"><h3>Decision blocks (drive dev via Eve serve)</h3>
<button onclick="decide('apply-best')">Apply best evolution</button>
<button onclick="decide('revert')">Revert game</button>
<span id="dout"></span></div>
<div id="therapy" style="margin-top:1.5em;padding:1em;border:2px solid #1f5fa3;border-radius:12px">
<h3>Live therapy + voice assistance</h3>
<button id="therapyBtn" style="font-size:1.3em;padding:.6em 1.4em;background:#1f5fa3;color:#fff;border:none;border-radius:10px;cursor:pointer" onclick="liveTherapy()">THERAPY</button>
<button onclick="voiceCommand()">Voice command (mic)</button>
<button onclick="stopSpeech()">Stop voice</button><br/>
<label>Mood: <select id="mood"><option>stressed</option><option>anxious</option><option>overwhelmed</option><option>sad</option><option>angry</option><option>okay</option></select></label>
<input id="tnote" placeholder="what's on your mind?" size="40"/>
<div id="tout" style="white-space:pre-wrap;margin-top:.6em;min-height:3em"></div>
<div id="vout" style="color:#8b949e;margin-top:.4em"></div>
</div>
<script>
const SERVE = 'http://127.0.0.1:8091';
function speak(t){
  try{
    speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(t.slice(0, 600));
    u.rate = 0.95;
    speechSynthesis.speak(u);
  }catch(e){}
}
function stopSpeech(){ try{ speechSynthesis.cancel(); }catch(e){} }
async function decide(d){
  const game = prompt('Game directory?', '');
  if(!game) return;
  const r = await fetch(SERVE + '/decide',
    {method:'POST', headers:{'Content-Type':'application/json'},
     body: JSON.stringify({decision:d, game})});
  const txt = (await r.text()).slice(0, 200);
  document.getElementById('dout').textContent = d + ': ' + txt;
  speak(d === 'revert' ? 'Game reverted.' : 'Best evolution applied.');
}
async function liveTherapy(){
  const mood = document.getElementById('mood').value;
  const note = document.getElementById('tnote').value;
  const out = document.getElementById('tout');
  out.textContent = 'Eve is here with you...';
  try{
    const r = await fetch(SERVE + '/therapy',
      {method:'POST', headers:{'Content-Type':'application/json'},
       body: JSON.stringify({mood, note})});
    const j = await r.json();
    out.textContent = j.text;
    speak(j.text);
  }catch(e){ out.textContent = 'Serve offline. Breathe in 4, hold 4, out 6. I am here.'; speak(out.textContent); }
}
function voiceCommand(){
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  const out = document.getElementById('vout');
  if(!SR){ out.textContent = 'Voice recognition not supported in this browser.'; return; }
  const rec = new SR();
  rec.lang = 'en-US'; rec.interimResults = false;
  out.textContent = 'Listening... say therapy, breathe, apply best, revert, or next.';
  rec.onresult = (ev) => {
    const heard = ev.results[0][0].transcript;
    out.textContent = 'Heard: ' + heard;
    routeVoice(heard);
  };
  rec.onerror = (ev) => { out.textContent = 'Mic error: ' + ev.error; };
  rec.start();
}
async function routeVoice(heard){
  const t = heard.toLowerCase();
  if(/therap|calm|anxious|stressed|ground/.test(t)){ liveTherapy(); return; }
  if(/breath/.test(t)){ const b = 'Breathe in 4 counts, hold 4, out 6. Again. You are doing well.';
    document.getElementById('tout').textContent = b; speak(b); return; }
  if(/apply.*best/.test(t)){ decide('apply-best'); return; }
  if(/revert|undo/.test(t)){ decide('revert'); return; }
  if(/next|continue|forward/.test(t)){ if(typeof show === 'function'){ show(cur + 1); speak('Next step.'); } return; }
  speak('I heard ' + heard + '. Say therapy, breathe, apply best, revert, or next.');
}
</script>
<script type="module">
import init, { step_count, steps_json, render_frame } from './pkg/%s.js';
await init();
const steps = JSON.parse(steps_json());
const nav = document.getElementById('nav');
const stage = document.getElementById('stage');
let cur = 0;
function show(i){ cur = (i + step_count()) %% step_count();
  stage.innerHTML = render_frame(cur);
  document.title = steps[cur].title; }
steps.forEach((s, i) => { const b = document.createElement('button');
  b.textContent = (i+1); b.onclick = () => show(i); nav.appendChild(b); });
show(0);
</script></body></html>
'''


def state_to_steps(state):
    """Inner state dict -> ordered tutorial steps."""
    steps = [{"title": "Swarm overview: %d providers, %d answered"
                       % (state.get("total", 0), state.get("answered", 0)),
              "verdict": "OVERVIEW",
              "detail": state.get("summary", "")}]
    for r in state.get("rows", []):
        steps.append({"title": "Provider %s" % r.get("provider"),
                      "verdict": r.get("verdict", ""),
                      "detail": r.get("detail", "")})
    steps.append({"title": "Fallback serves with NSP judgment",
                  "verdict": "JUDGED",
                  "detail": state.get("nsp", "nsp verdict attached "
                                             "to every served answer")})
    return steps


def parse_ablation_log(path):
    """Parse a real `eve ablate` log into an inner-state dict."""
    rows, summary = [], ""
    for line in Path(path).read_text(encoding="utf-8",
                                     errors="replace").splitlines():
        line = line.strip()
        if line.startswith("[") and "]" in line:
            verdict, rest = line[1:].split("]", 1)
            provider, _, detail = rest.strip().partition(":")
            rows.append({"provider": provider.strip(),
                         "verdict": verdict.strip(),
                         "detail": detail.strip()[:100]})
        elif line.startswith("ABLATION:"):
            summary = line
    answered = sum(1 for r in rows
                   if r["provider"] != "swarm+NSP fallback"
                   and r["verdict"] == "ANSWERED")
    providers = [r for r in rows if r["provider"] != "swarm+NSP fallback"]
    return {"rows": rows, "answered": answered,
            "total": len(providers), "summary": summary}


def generate(state, out_dir, crate_name="eve_inner_state"):
    """Write crate sources + host page. Returns (out_dir, step_total)."""
    out = Path(out_dir)
    (out / "src").mkdir(parents=True, exist_ok=True)
    steps = state_to_steps(state)
    (out / "src" / "lib.rs").write_text(
        LIB_RS % json.dumps(json.dumps(steps)), encoding="utf-8")
    (out / "Cargo.toml").write_text(CARGO_TOML % crate_name,
                                    encoding="utf-8")
    title = "Eve inner states: swarm ablation tutorial"
    (out / "index.html").write_text(INDEX_HTML % (title, title, crate_name),
                                    encoding="utf-8")
    (out / "state.json").write_text(json.dumps(state, indent=2),
                                    encoding="utf-8")
    return out, len(steps)


def build_wasm(crate_dir, timeout=600):
    """Compile the crate to WASM with wasm-pack. Returns pkg dir or raises."""
    try:
        proc = subprocess.run(
            ["wasm-pack", "build", "--target", "web", str(crate_dir)],
            capture_output=True, text=True, timeout=timeout)
    except Exception as e:
        note_failure("wasm:build-spawn", e)
        raise RuntimeError("wasm-pack would not start: %s" % e)
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout)[-2000:]
        note_failure("wasm:build-fail",
                     Exception(err[:200]))
        raise RuntimeError("wasm-pack failed: %s" % err)
    return Path(crate_dir) / "pkg"
