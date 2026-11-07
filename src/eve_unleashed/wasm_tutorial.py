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
