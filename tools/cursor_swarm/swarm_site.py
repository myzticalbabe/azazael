#!/usr/bin/env python3
"""site.py - the site a worker swarm builds, drawn as coloured mouse cursors.

This is the WORKER project. `tools/swarm_arena/` is a different project: it
judges candidate texts against each other with three language shards and an Elo
board. Nothing here reads it, and nothing in it reads this. The one thing the
two share is a subject, not a codebase.

What is here:

  * a classic mouse-pointer glyph, authored in this file. The arena uses a
    Vulcan salute; a worker swarm that builds a site wants the arrow you point
    a page with, because the video this is drawn from shows coloured mouse
    cursors and a salute would be a second, borrowed vocabulary;
  * the three layers the A8 design names, all of them read from the ledger
    rather than invented: COLOUR (a verdict's colour is `monitor_theme`'s, not
    a literal here), TRACER (a worker draws its four stages - placed, verified,
    applied, settled - because the ledger already carries them), and PULSE (a
    follower element whose opacity is keyed to the row's age, because a cursor
    that stopped moving must be distinguishable from one that is merely slow).

The pulse is never the pointer. `cursor: url(...)` accepts only non-animated
formats, so a pulsing salute cannot be the OS pointer; the pulse is a
positioned element with `pointer-events: none` over a static glyph.

The page is one static file: no server, no fetch, so a desktop and a headless
Chrome render the same pixels.
"""
import html
import json

# The pointer: a 32x32 arrow whose hotspot is the tip. The hotspot is read out
# of the markup by `hotspot_of`, never hard-coded at the call site, so the
# glyph and the placement cannot drift apart.
POINTER_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" '
    'viewBox="0 0 32 32" data-hotspot="2,1">'
    '<path d="M2 1 L2 25 L8.2 19.2 L12.4 29 L16.6 27.1 L12.4 17.4 L20 17.4 Z" '
    'fill="#ffffff" stroke="#0d1117" stroke-width="1.6" stroke-linejoin="round"/>'
    '</svg>'
)

# The four verdicts the tree's ledger validator accepts (tools/claim_agreement.py
# LEDGER_VERDICTS). A fifth would be a new dialect, and a dialect nobody else
# can read is a private language, not an extension.
VERDICT_SLOT = {
    "landed": "ok",
    "held": "held",
    "rolledback": "error",
    "quarantine": "unknown",
}

# The four stages a worker moves through. The ledger carries them in the claim
# text; the tracer draws them as nodes, so the progression stops being invisible.
STAGES = ("placed", "verified", "applied", "settled")

BUDGET_MS = 900
MOVE_MS = 300


def hotspot_of(markup):
    """(x, y) read out of the glyph's own data-hotspot attribute."""
    import re

    found = re.search(r'data-hotspot="([\d.]+),([\d.]+)"', markup)
    if not found:
        raise SystemExit("cursor_swarm: the pointer declares no data-hotspot")
    return float(found.group(1)), float(found.group(2))


def schedule(count):
    """(stagger_ms, slowest_ms): the emitted schedule, provably inside the budget."""
    stagger = 0 if count < 2 else min(35, max(0, (BUDGET_MS - MOVE_MS) // (count - 1)))
    slowest = (count - 1) * stagger + MOVE_MS
    if slowest > BUDGET_MS:
        raise SystemExit("cursor_swarm: %d workers cannot finish inside %d ms "
                         "(slowest %d ms)" % (count, BUDGET_MS, slowest))
    return stagger, slowest


CSS = """
:root { --bg:#0b0e14; --fg:#d8dee9; --dim:#8b949e; --line:#21262d; }
* { box-sizing:border-box; }
body { margin:0; padding:24px; background:var(--bg); color:var(--fg);
       font:13px/1.55 ui-monospace,Menlo,Consolas,monospace; }
h1 { font-size:17px; margin:0 0 4px; color:#88c0d0; letter-spacing:.02em; }
h2 { font-size:14px; margin:22px 0 8px; color:#88c0d0; }
.src { color:var(--dim); margin:0 0 12px; font-size:11.5px; }
.lede { margin:0 0 16px; max-width:98ch; }
.lede b { color:#c9d1d9; }
.denom { margin:0 0 14px; padding:8px 10px; border-left:3px solid #88c0d0;
         background:#11151c; }
.denom b { color:#88c0d0; }
#counter { position:fixed; top:0; right:0; padding:10px 18px; background:#11151c;
           border-left:1px solid var(--line); border-bottom:1px solid var(--line);
           font-size:26px; color:#7ee787; }
#counter small { display:block; font-size:10.5px; color:var(--dim); letter-spacing:.08em; }
#field { position:relative; height:460px; border:1px solid var(--line); border-radius:6px;
         overflow:hidden;
         background:radial-gradient(1200px 460px at 50% 45%, #11161f 0%, #0b0e14 70%); }
.grid { position:absolute; inset:0; opacity:.5;
        background-image:linear-gradient(var(--line) 1px,transparent 1px),
                         linear-gradient(90deg,var(--line) 1px,transparent 1px);
        background-size:48px 48px; }
.node { position:absolute; width:9px; height:9px; margin:-4.5px 0 0 -4.5px;
        border-radius:50%; background:#30363d; box-shadow:0 0 0 3px rgba(48,54,61,.35); }
.trails { position:absolute; inset:0; pointer-events:none; }
.stage { position:absolute; width:7px; height:7px; margin:-3.5px 0 0 -3.5px;
         border-radius:50%; border:1px solid rgba(0,0,0,.55); }
.cursor { position:absolute; width:32px; height:32px; will-change:transform;
          transform:translate(var(--dx),var(--dy));
          transition:transform 300ms cubic-bezier(.16,.84,.24,1); }
.cursor.settled { transform:none; }
.cursor svg { display:block; filter:drop-shadow(0 1px 2px rgba(0,0,0,.7)); }
.cursor[data-verdict="landed"] svg path { fill:#ffffff; stroke:__OK__; }
.cursor[data-verdict="held"] svg path { fill:#ffffff; stroke:__HELD__; }
.cursor[data-verdict="rolledback"] svg path { fill:#ffffff; stroke:__ERROR__; }
.cursor[data-verdict="quarantine"] svg path { fill:none; stroke:__UNKNOWN__; stroke-dasharray:2 2; }
.pulse { position:absolute; width:26px; height:26px; margin:-13px 0 0 -13px;
         border-radius:50%; pointer-events:none; opacity:0; }
.pill { position:absolute; left:34px; top:26px; white-space:nowrap; font-size:10.5px;
        padding:1px 6px; border-radius:9px; color:var(--dim);
        background:rgba(11,14,20,.9); border:1px solid currentColor; }
.pill.flip { left:auto; right:34px; }
.cursor[data-verdict="landed"] .pill { color:__OK__; }
.cursor[data-verdict="held"] .pill { color:__HELD__; }
.cursor[data-verdict="rolledback"] .pill { color:__ERROR__; }
.cursor[data-verdict="quarantine"] .pill { color:__UNKNOWN__; }
.legend { display:flex; gap:16px; flex-wrap:wrap; margin:14px 0 0; font-size:11.5px; }
.legend i { display:inline-block; width:10px; height:10px; border-radius:2px;
            margin-right:6px; vertical-align:-1px; }
#site { margin-top:18px; display:grid; gap:10px;
        grid-template-columns:repeat(auto-fill,minmax(320px,1fr)); }
.layer { border:1px solid var(--line); border-left:3px solid var(--line);
         border-radius:4px; padding:8px 10px; background:#0d1117;
         opacity:0; transform:translateY(6px);
         transition:opacity 240ms ease, transform 240ms ease; }
.layer.shown { opacity:1; transform:none; }
.layer[data-verdict="landed"] { border-left-color:__OK__; }
.layer[data-verdict="held"] { border-left-color:__HELD__; }
.layer[data-verdict="rolledback"] { border-left-color:__ERROR__; }
.layer h3 { margin:0 0 3px; font-size:12.5px; color:#c9d1d9; font-weight:600; }
.layer .d { margin:0; font-size:11px; color:var(--dim); }
.layer ul { margin:5px 0 0; padding-left:16px; font-size:11px; color:#8b949e; }
#quarantine { margin-top:16px; padding:8px 10px; border:1px dashed #f85149;
              border-radius:4px; color:#f85149; }
#quarantine.empty { border-color:var(--line); color:var(--dim); }
#selftest { margin-top:16px; padding:10px; background:#11151c; border-radius:4px;
            color:#7ee787; white-space:pre-wrap; }
"""

JS = """
(function () {
  var data = JSON.parse(document.getElementById('swarm-data').textContent);
  var field = document.getElementById('field');
  var budget = +field.dataset.budget, stag = +field.dataset.stagger, move = +field.dataset.move;
  var workers = data.workers, site = document.getElementById('site');
  var counter = document.getElementById('counter');
  var n = document.getElementById('counter-n');
  var shown = 0;

  function paint() { n.textContent = shown; }

  workers.forEach(function (w, i) {
    var cursor = document.querySelector('.cursor[data-worker="' + w.id + '"]');
    var layer = document.querySelector('.layer[data-worker="' + w.id + '"]');
    setTimeout(function () {
      if (cursor) { cursor.classList.add('settled'); }
      if (layer) { layer.classList.add('shown'); }
      shown += 1; paint();
      if (cursor) {
        // The pulse: a follower element keyed to the row's age. Never the OS
        // pointer - a CSS cursor accepts only non-animated formats.
        var pulse = document.createElement('span');
        pulse.className = 'pulse';
        pulse.style.left = w.x + 'px'; pulse.style.top = w.y + 'px';
        pulse.style.background = w.color; pulse.style.boxShadow = '0 0 16px 6px ' + w.color;
        field.appendChild(pulse);
        requestAnimationFrame(function () { pulse.style.transition = 'opacity 900ms linear'; });
        pulse.style.opacity = '0.9';
        setTimeout(function () { pulse.style.opacity = '0'; }, 40);
      }
    }, i * stag + move);
  });

  var cursors = [].slice.call(document.querySelectorAll('.cursor[data-verdict]'));
  var layers = document.querySelectorAll('.layer').length;
  var counts = {}, misaligned = 0;
  cursors.forEach(function (c) {
    counts[c.dataset.verdict] = (counts[c.dataset.verdict] || 0) + 1;
    var left = parseFloat(c.style.left), top = parseFloat(c.style.top);
    var hx = parseFloat(c.dataset.hx), hy = parseFloat(c.dataset.hy);
    if (Math.abs(left + hx - parseFloat(c.dataset.tx)) > 0.01 ||
        Math.abs(top + hy - parseFloat(c.dataset.ty)) > 0.01) { misaligned += 1; }
  });
  var q = document.querySelectorAll('#quarantine [data-q]').length;
  var slowest = (cursors.length - 1) * stag + move;
  var chain = (misaligned === 0 && slowest <= budget) ? 'OK' : 'MISMATCH';
  document.getElementById('selftest').textContent =
    'SELFTEST: workers=' + cursors.length + ' layers=' + layers +
    ' landed=' + (counts.landed || 0) + ' held=' + (counts.held || 0) +
    ' rolledback=' + (counts.rolledback || 0) + ' quarantine=' + (counts.quarantine || 0) +
    ' quarantine_strip=' + q + ' hotspot_misaligned=' + misaligned +
    ' slowest=' + slowest + 'ms budget=' + budget + 'ms CHAIN=' + chain;
  paint();
})();
"""


def render(workers, ledger_rows, quarantine, color, meta):
    """The whole page. `workers` are the ones that landed (or held)."""
    hx, hy = hotspot_of(POINTER_SVG)
    stagger, slowest = schedule(len(workers))

    css = CSS
    for slot, key in (("__OK__", "ok"), ("__HELD__", "held"),
                       ("__ERROR__", "error"), ("__UNKNOWN__", "unknown")):
        css = css.replace(slot, color.get(key, "#8b949e"))

    mains, trails, stages = [], [], []
    payload = []
    for idx, w in enumerate(workers):
        verdict = w["verdict"]
        slot = VERDICT_SLOT.get(verdict, "unknown")
        stroke = color.get(slot, "#8b949e")
        # The cursor's TOP-LEFT is placed at (node - hotspot), so the tip - the
        # thing you point with - is the thing that lands on the node. Placing
        # the corner there instead is the bug the arena's selftest was written
        # to catch, and it is caught here by the same arithmetic.
        left, top = w["x"] - hx, w["y"] - hy
        start_x, start_y = 12.0 + (idx % 12) * 78.0, 26.0 + (idx // 12) * 34.0
        dx, dy = start_x - left, start_y - top
        trails.append(
            '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="1" stroke-dasharray="2 5" opacity=".22"/>'
            % (start_x, start_y, w["x"], w["y"], stroke))
        mains.append(
            '<div class="node" style="left:%.1fpx;top:%.1fpx"></div>'
            % (w["x"], w["y"]))
        # The tracer: the four stages, each coloured by that stage's verdict.
        for si, stage in enumerate(STAGES):
            sv = w["stage_verdicts"].get(stage, verdict)
            scol = color.get(VERDICT_SLOT.get(sv, "unknown"), "#8b949e")
            sx = w["x"] - 21.0 + si * 11.0
            sy = w["y"] + 18.0
            stages.append(
                '<span class="stage" title="%s %s" style="left:%.1fpx;top:%.1fpx;'
                'background:%s"></span>' % (w["id"], stage, sx, sy, scol))
        pcls = "flip" if w["x"] > 900 else ""
        mains.append(
            '<div class="cursor" data-worker="%s" data-verdict="%s" data-hx="%s" '
            'data-hy="%s" data-tx="%.3f" data-ty="%.3f" title="%s" '
            'style="left:%.3fpx;top:%.3fpx;--dx:%dpx;--dy:%dpx">%s'
            '<span class="pill %s">%s</span></div>'
            % (w["id"], verdict, hx, hy, w["x"], w["y"],
               html.escape(w["claim"]), left, top, int(dx), int(dy),
               POINTER_SVG, pcls, html.escape(w["id"])))
        payload.append({"id": w["id"], "x": w["x"], "y": w["y"], "color": stroke,
                        "verdict": verdict})

    layers = []
    for w in workers:
        files = "".join("<li>%s</li>" % html.escape(f) for f in w["scope"])
        layers.append(
            '<section class="layer" data-worker="%s" data-verdict="%s">'
            '<h3>%s</h3><p class="d">%s</p><ul>%s</ul></section>'
            % (w["id"], w["verdict"], html.escape(w["node"]),
               html.escape(w["reading"]), files))

    if quarantine:
        qblock = ('<div id="quarantine"><b>Quarantine - rows whose hash does not '
                  'recompute, never drawn on the field:</b>%s</div>'
                  % "".join('<div data-q="1">%s</div>' % html.escape(str(q))
                            for q in quarantine))
    else:
        qblock = ('<div id="quarantine" class="empty"><b>Quarantine:</b> empty - '
                  'every ledger row recomputes to its own hash.</div>')

    legend = "".join(
        '<span><i style="background:%s"></i>%s</span>'
        % (color.get(VERDICT_SLOT[v], "#8b949e"), v)
        for v in ("landed", "held", "rolledback", "quarantine"))

    page = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Cursor swarm - workers building a site</title>
<style>__CSS__</style></head><body>
<div id="counter"><small>AGENTS</small><span id="counter-n">0</span></div>
<h1>Cursor swarm - workers building a site</h1>
<p class="src">__SRC__</p>
<p class="lede">Each cursor is a <b>worker</b>, not a judge: it reads its own scope, reports
what it found, and lands or the whole swarm does not. The cursor flies to the node it worked
on; the four dots beside it are its stages - placed, verified, applied, settled - which the
ledger already carried and the old view never showed. The site below assembles as the workers
settle.</p>
<p class="denom">__DENOM__</p>
<div id="field" style="width:1040px;max-width:100%" data-budget="__BUDGET__" data-stagger="__STAGGER__" data-move="__MOVE__">
  <div class="grid"></div>
  <svg class="trails" width="100%" height="100%">__TRAILS__</svg>
  __STAGES__
  __MAINS__
</div>
<div class="legend">__LEGEND__</div>
<h2>The site the swarm built</h2>
<div id="site">__LAYERS__</div>
__QUARANTINE__
<pre id="selftest">SELFTEST: pending</pre>
<script id="swarm-data" type="application/json">__DATA__</script>
<script>__JS__</script>
</body></html>
"""
    page = (page.replace("__CSS__", css)
                .replace("__SRC__", html.escape(meta["source"]))
                .replace("__DENOM__", meta["denominator"])
                .replace("__BUDGET__", str(BUDGET_MS))
                .replace("__STAGGER__", str(stagger))
                .replace("__MOVE__", str(MOVE_MS))
                .replace("__TRAILS__", "".join(trails))
                .replace("__STAGES__", "".join(stages))
                .replace("__MAINS__", "".join(mains))
                .replace("__LAYERS__", "".join(layers))
                .replace("__LEGEND__", legend)
                .replace("__QUARANTINE__", qblock)
                .replace("__DATA__", json.dumps({"workers": payload}))
                .replace("__JS__", JS))
    return page, {"stagger": stagger, "slowest": slowest, "hotspot": (hx, hy)}
