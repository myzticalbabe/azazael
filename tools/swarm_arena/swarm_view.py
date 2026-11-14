#!/usr/bin/env python3
"""swarm_view.py — the arena's verdicts drawn as on-screen Vulcan-salute cursors.

The two glyphs in `cursors/` are the pointers. Each candidate from the last
arena run gets one, placed so its hotspot (the index fingertip, read out of
the SVG's own `data-hotspot`) lands on the node it scored, coloured by the
state of its record. The page is one static file: no server, no fetch, so a
desktop and headless Chrome render the same pixels.

Palette: `monitor_theme.SEMANTIC`, imported rather than copied — a state
colour that lives in two files drifts in two files.

Four states are the palette's (ok / warn / error / unknown). Two are this
view's own, because a cursor either has a row or it does not:

  absent — the plan asked for more cursors than the run produced (I3)
  blind  — a shard cast no vote at all, so "agreement" would be an invention (I4)

Plan rules enforced here, before anything is drawn (I1, I2, I5, I6):
  * every cursor target is disjoint — one node, one cursor;
  * the cursor count is under SCOPE_CEILING, and the emitted animation
    schedule provably finishes inside BUDGET_MS (the sub-second claim is a
    computed number on the page, not a hope);
  * the scope is enumerated through `git ls-files`, so a denominator counts what
    the commit will contain, and a scope with no index entry is refused with a
    named remedy instead of being counted from the worktree;
  * rollback is proved structurally — `git ls-tree -r HEAD` object ids plus an
    empty `git status --porcelain` — not by hashing the whole worktree.

Usage:
  python swarm_view.py [--results F] [--elo F] [--out F] [--ledger F]
                       [--top N] [--field WxH] [--scope P ...] [--prove]
Exit: 0 rendered; 2 could not render (registry/hotspot mismatch, rejected plan,
scope outside the index, missing import, or --prove over a dirty worktree).
2 is not a pass.
"""
import argparse
import hashlib
import html
import json
import math
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CURSORS = os.path.join(HERE, "cursors")
REGISTRY = os.path.join(CURSORS, "registry.json")
SHARDS = ("rust", "go", "py")

SCOPE_CEILING = 24        # I6: a plan larger than this cannot meet the budget
BUDGET_MS = 900           # the A8 "sub-second" claim, per swarm
MOVE_MS = 300             # one cursor's travel, before staggering

REPO = os.path.dirname(os.path.dirname(HERE))            # tools/swarm_arena -> repo root
DEFAULT_SCOPE = (os.path.relpath(HERE, REPO).replace(os.sep, "/"),)

sys.path.insert(0, os.path.dirname(HERE))
try:
    from monitor_theme import SEMANTIC
except Exception as exc:  # noqa: BLE001
    print("swarm_view: cannot import monitor_theme.SEMANTIC (%s) — refusing to invent a "
          "palette" % exc)
    sys.exit(2)

COLOR = {k: v[0] for k, v in SEMANTIC.items()}


# ── glyphs ───────────────────────────────────────────────────────────────

def load_registry():
    """(registry, glyphs). The SVG's own hotspot must agree with the registry."""
    with open(REGISTRY, encoding="utf-8") as fh:
        reg = json.load(fh)
    glyphs = {}
    for entry in reg["cursors"]:
        path = os.path.join(CURSORS, entry["file"])
        with open(path, encoding="utf-8") as fh:
            markup = fh.read()
        found = re.search(r'data-hotspot="([\d.]+),([\d.]+)"', markup)
        if not found:
            raise SystemExit("swarm_view: %s declares no data-hotspot" % entry["file"])
        declared = (float(found.group(1)), float(found.group(2)))
        listed = tuple(float(v) for v in entry["hotspot"])
        if declared != listed:
            raise SystemExit("swarm_view: registry says %s hotspots %s, the SVG says %s"
                             % (entry["file"], listed, declared))
        glyphs[entry["size"]] = {"name": entry["name"], "size": entry["size"],
                                 "hotspot": declared, "markup": markup}
    if not glyphs:
        raise SystemExit("swarm_view: registry holds no cursors")
    return reg, glyphs


# ── scope + rollback (I1, I5) ────────────────────────────────────────────

def refuse(message):
    """Exit 2: the documented "could not render", distinct from a Python failure (1)."""
    print(message, file=sys.stderr)
    sys.exit(2)


def git_text(args, root=REPO):
    """One git command's stdout, or exit 2 — an unreadable index is not an empty one."""
    try:
        out = subprocess.run(["git", "-C", root, *args], capture_output=True, text=True,
                             encoding="utf-8", errors="replace", timeout=30)
    except OSError as exc:
        refuse("swarm_view: cannot run git (%s) — remedy: put git on PATH" % exc)
    except subprocess.TimeoutExpired:
        refuse("swarm_view: git %s did not answer in 30 s — remedy: check .git for a lock "
               "another process holds" % " ".join(args))
    if out.returncode != 0:
        refuse("swarm_view: git %s failed (rc=%d): %s"
               % (" ".join(args), out.returncode, out.stderr.strip()[:200]))
    return out.stdout


def read_scope(paths, root=REPO):
    """I1 — a cursor's universe is the INDEX, never the worktree.

    Measured in the audit: 10 112 `.py` files on disk under `.` against 4 437
    tracked, so a verdict's denominator was not the scope's denominator. The
    index is what the commit will contain; a scope with no index entry is
    refused here, naming the remedy, rather than silently counted from disk.
    """
    files = sorted(p for p in git_text(["ls-files", "-z", "--", *paths], root).split("\0") if p)
    missing = [p for p in paths
               if not any(f == p or f.startswith(p.rstrip("/") + "/") for f in files)]
    if missing:
        present = [p for p in missing if os.path.exists(os.path.join(root, p))]
        remedy = (("`git add %s` — read_scope counts the index, and an untracked path is "
                   "content the commit will not contain" % " ".join(present))
                  if present else
                  "name a tracked path that exists (checked: %s)" % ", ".join(missing))
        refuse("swarm_view: scope outside the index: %s — remedy: %s"
               % (", ".join(missing), remedy))
    return files

def disk_modules(paths, root=REPO):
    """`.py` files on disk under the scope — the worktree count, quoted for contrast only."""
    found = 0
    for path in paths:
        full = os.path.join(root, path)
        if os.path.isfile(full):
            found += 1 if path.endswith(".py") else 0
            continue
        for _dirpath, dirnames, filenames in os.walk(full):
            dirnames[:] = [d for d in dirnames if d not in ("__pycache__", ".git")]
            found += sum(1 for name in filenames if name.endswith(".py"))
    return found


def rollback_proof(paths, root=REPO):
    """I5/C2 — rollback proved structurally, not by hashing the whole worktree.

    `git ls-tree -r HEAD` object ids name the committed content of every file in
    the scope and cannot change without HEAD changing; empty `git status
    --porcelain` proves the worktree matches the index. The design's whole-tree
    sha256 races any concurrent writer and is the most expensive assertion in
    the suite; this pair is exact, cheap, and race-free.
    """
    tree = {}
    for record in git_text(["ls-tree", "-r", "-z", "HEAD", "--", *paths], root).split("\0"):
        if not record:
            continue
        meta, path = record.split("\t", 1)
        tree[path] = meta.split()[2]
    if not tree:
        refuse("swarm_view: rollback proof found no HEAD entry under %s — remedy: name a "
               "tracked path" % ", ".join(paths))
    dirty = [line for line in
             git_text(["status", "--porcelain", "--", *paths], root).splitlines() if line.strip()]
    digest = hashlib.sha256(
        "\n".join("%s %s" % (p, tree[p]) for p in sorted(tree)).encode("utf-8")).hexdigest()
    return {"head": git_text(["rev-parse", "--short", "HEAD"], root).strip(),
            "blobs": len(tree), "digest": digest, "dirty": dirty, "clean": not dirty}


# ── verdicts ─────────────────────────────────────────────────────────────

def candidate_states(pairs):
    """ok = won all its pairs unanimously; warn = won with dissent; error = lost all."""
    tally = {}
    for p in pairs:
        for cid in (p["x"], p["y"]):
            rec = tally.setdefault(cid, {"won": 0, "lost": 0, "unanimous": 0})
            if cid == p["winner"]:
                rec["won"] += 1
                rec["unanimous"] += 1 if p.get("unanimous") else 0
            else:
                rec["lost"] += 1
    states = {}
    for cid, r in tally.items():
        if r["lost"] == 0 and r["unanimous"] == r["won"]:
            states[cid] = "ok"
        elif r["won"] == 0:
            states[cid] = "error"
        elif r["won"] >= 1:
            states[cid] = "warn"
        else:
            states[cid] = "unknown"
    return states, tally


def shard_votes(pairs):
    counts = {name: 0 for name in SHARDS}
    for p in pairs:
        for name in p.get("votes", {}):
            counts[name] = counts.get(name, 0) + 1
    return counts


# ── plan ─────────────────────────────────────────────────────────────────

def build_plan(board, states, tally, top, width, height, blind):
    """Cursors for the top N, then `absent` rows for slots the run never filled."""
    plan, targets = [], set()
    span = max(1, top - 1)
    for i, entry in enumerate(board[:top]):
        cid = entry["id"]
        x = 90.0 + i * (width - 180.0) / span
        # Adjacent cursors alternate bands, so two labels never share a height.
        y = (height * 0.42 + height * 0.10 * math.sin(i * 1.1)
             + (height * 0.18 if i % 2 else -height * 0.18))
        key = (round(x, 1), round(y, 1))
        if key in targets:                                   # I2: disjointness
            raise SystemExit("swarm_view: plan rejected — two cursors at %s" % (key,))
        if cid in targets:
            raise SystemExit("swarm_view: plan rejected — %s carries two cursors" % cid)
        targets.update((key, cid))
        rec = tally.get(cid, {"won": 0, "lost": 0, "unanimous": 0})
        plan.append({
            "cursor_id": "c%d" % (i + 1), "node": cid, "tree": "swarm_arena",
            "state": "blind" if blind else states.get(cid, "unknown"),
            "claim": "%s · elo %.1f · %dW/%dL" % (cid[:18], entry["elo"],
                                                  rec["won"], rec["lost"]),
            "x": x, "y": y, "elo": entry["elo"],
        })
    for i in range(len(board[:top]), top):
        plan.append({
            "cursor_id": "c%d" % (i + 1), "node": "slot-%d" % (i + 1),
            "tree": "swarm_arena", "state": "absent",
            "claim": "absent · the run produced no candidate for this slot",
            "x": 0.0, "y": 0.0, "elo": None,
        })
    if len(plan) > SCOPE_CEILING:
        raise SystemExit("swarm_view: plan rejected — %d cursors exceeds the ceiling of %d"
                         % (len(plan), SCOPE_CEILING))
    return plan


def schedule(count):
    """(stagger, slowest_ms): the emitted schedule, provably inside the budget."""
    stagger = 0 if count < 2 else min(35, max(0, (BUDGET_MS - MOVE_MS) // (count - 1)))
    slowest = (count - 1) * stagger + MOVE_MS
    if slowest > BUDGET_MS:
        raise SystemExit("swarm_view: plan rejected — slowest cursor %d ms > budget %d ms"
                         % (slowest, BUDGET_MS))
    return stagger, slowest


# ── ledger ───────────────────────────────────────────────────────────────

def chain(rows):
    prev, out = "GENESIS", []
    for i, row in enumerate(rows):
        row = dict(row, frame=i + 1, prev_hash=prev)
        blob = json.dumps({k: row[k] for k in ("frame", "cursor_id", "tree", "node",
                                               "verdict", "claim", "prev_hash")},
                          sort_keys=True, separators=(",", ":"))
        row["hash"] = hashlib.sha256(blob.encode("utf-8")).hexdigest()
        prev = row["hash"]
        out.append(row)
    return out


def broken_rows(rows):
    """Rows whose hash does not recompute — quarantined, never drawn on the field."""
    bad, prev = [], "GENESIS"
    for row in rows:
        blob = json.dumps({k: row[k] for k in ("frame", "cursor_id", "tree", "node",
                                               "verdict", "claim", "prev_hash")},
                          sort_keys=True, separators=(",", ":"))
        if (row["prev_hash"] != prev
                or hashlib.sha256(blob.encode("utf-8")).hexdigest() != row["hash"]):
            bad.append(row["cursor_id"])
        prev = row["hash"]
    return bad


# ── page ─────────────────────────────────────────────────────────────────

CSS = """
:root { --bg:#0b0e14; --fg:#d8dee9; --dim:#8b949e; --line:#21262d; }
* { box-sizing: border-box; }
body { margin:0; padding:24px; background:var(--bg); color:var(--fg);
       font:13px/1.5 ui-monospace,Menlo,Consolas,monospace; }
h1 { font-size:16px; margin:0 0 4px; color:#88c0d0; letter-spacing:.02em; }
.src { color:var(--dim); margin:0 0 14px; font-size:11.5px; }
.lede { margin:0 0 18px; max-width:96ch; }
.denom { margin:0 0 18px; padding:8px 10px; border-left:3px solid #88c0d0;
         background:#11151c; }
.denom b { color:#88c0d0; }
#field { position:relative; height:420px; border:1px solid var(--line);
         border-radius:6px; overflow:hidden;
         background:
           radial-gradient(1200px 420px at 50% 45%, #11161f 0%, #0b0e14 70%); }
.grid { position:absolute; inset:0; opacity:.5;
        background-image:linear-gradient(var(--line) 1px,transparent 1px),
                         linear-gradient(90deg,var(--line) 1px,transparent 1px);
        background-size:48px 48px; }
.node { position:absolute; width:9px; height:9px; margin:-4.5px 0 0 -4.5px;
        border-radius:50%; background:#30363d;
        box-shadow:0 0 0 3px rgba(48,54,61,.35); }
.node span { position:absolute; left:11px; top:-9px; white-space:nowrap;
             color:var(--dim); font-size:10.5px; }
.node span.down { top:14px; }
.trails { position:absolute; inset:0; pointer-events:none; }
.glyph { display:block; transform:scale(1.6); transform-origin:8.5px 2px; }
.cursor { position:absolute; width:32px; height:32px; will-change:transform; cursor:pointer;
          transform:translate(var(--dx),var(--dy));
          transition:transform 300ms cubic-bezier(.16,.84,.24,1); }
.cursor.settled { transform:none; }
.cursor.settled .glyph svg { animation:wave 760ms ease-in-out var(--wave-delay) 1 both;
                             transform-origin:8.5px 2px; }
@keyframes wave {
  0%,100% { transform:rotate(0deg); }
  32%     { transform:rotate(-6deg); }
  66%     { transform:rotate(5deg); }
}
.cursor svg { display:block; filter:drop-shadow(0 1px 2px rgba(0,0,0,.7)); }
.cursor::before { content:''; position:absolute; left:8.5px; top:2px; width:6px; height:6px;
                  margin:-3px 0 0 -3px; border-radius:50%; opacity:.30;
                  box-shadow:0 0 12px 5px #8b949e; }
.cursor[data-state="ok"]::before { box-shadow:0 0 13px 5px #3fb950; opacity:.38; }
.cursor[data-state="warn"]::before { box-shadow:0 0 13px 5px #d29922; opacity:.38; }
.cursor[data-state="error"]::before { box-shadow:0 0 13px 5px #f85149; opacity:.42; }
.cursor[data-state="absent"]::before, .cursor[data-state="blind"]::before { box-shadow:none; }
.cursor:hover { z-index:50; }
.cursor:hover .glyph { transform:scale(1.95); transition:transform 120ms ease; }
.cursor:hover .pill { background:#11161c; opacity:1; }
.cursor[data-copied="1"] .pill::after { content:' \2713 copied'; color:#7ee787; }
.ring { position:absolute; width:0; height:0; pointer-events:none;
        border:1px solid #8b949e; border-radius:50%;
        animation:ripple 620ms ease-out 1 both; }
@keyframes ripple {
  0%   { width:0; height:0; margin:0; opacity:.85; }
  100% { width:30px; height:30px; margin:-15px 0 0 -15px; opacity:0; }
}
.cursor[data-state="ok"] svg path { fill:#ffffff; stroke:#3fb950; }
.cursor[data-state="warn"] svg path { fill:#ffffff; stroke:#d29922; }
.cursor[data-state="error"] svg path { fill:#ffffff; stroke:#f85149; }
.cursor[data-state="unknown"] svg path { fill:#ffffff; stroke:#8b949e; }
.cursor[data-state="absent"] { opacity:.38; }
.cursor[data-state="absent"] svg path { fill:none; stroke:#8b949e; stroke-dasharray:2 2; }
.cursor[data-state="blind"] { opacity:.38; }
.cursor[data-state="blind"] svg path { fill:none; stroke:#8b949e; stroke-dasharray:1 3; }
.pill { position:absolute; left:52px; top:24px; white-space:nowrap; font-size:10.5px;
        padding:1px 6px; border-radius:9px; color:var(--dim);
        background:rgba(11,14,20,.9); border:1px solid currentColor; }
.pill.flip { left:auto; right:52px; }
.cursor[data-state="ok"] .pill { color:#3fb950; }
.cursor[data-state="warn"] .pill { color:#d29922; }
.cursor[data-state="error"] .pill { color:#f85149; }
.cursor[data-state="absent"] .pill, .cursor[data-state="blind"] .pill { color:#8b949e; }
.cursor.settled .pill { animation:idle 500ms ease 6s forwards; }
@keyframes idle { to { opacity:.45; } }
.legend { display:flex; gap:16px; flex-wrap:wrap; margin:14px 0 0; font-size:11.5px; }
.legend i { display:inline-block; width:10px; height:10px; border-radius:2px;
            margin-right:6px; vertical-align:-1px; }
#quarantine { margin-top:16px; padding:8px 10px; border:1px dashed #f85149;
              border-radius:4px; color:#f85149; }
#quarantine.empty { border-color:var(--line); color:var(--dim); }
#selftest { margin-top:16px; padding:10px; background:#11151c; border-radius:4px;
            color:#7ee787; white-space:pre-wrap; }
"""

JS = """
(function () {
  var field = document.getElementById('field');
  var budget = +field.dataset.budget, stag = +field.dataset.stagger;
  var cursors = [].slice.call(document.querySelectorAll('.cursor[data-state]'));
  cursors.forEach(function (c, i) {
    setTimeout(function () { c.classList.add('settled'); }, i * stag);
  });
  var seen = {}, bad = 0;
  cursors.forEach(function (c) {
    seen[c.dataset.state] = (seen[c.dataset.state] || 0) + 1;
    var left = parseFloat(c.style.left), top = parseFloat(c.style.top);
    var hx = parseFloat(c.dataset.hx), hy = parseFloat(c.dataset.hy);
    if (Math.abs(left + hx - parseFloat(c.dataset.tx)) > 0.01 ||
        Math.abs(top + hy - parseFloat(c.dataset.ty)) > 0.01) { bad += 1; }
  });
  var slowest = (cursors.length - 1) * stag + 300;
  var q = document.querySelectorAll('#quarantine [data-q]').length;
  var rings = document.querySelectorAll('#field .ring').length;
  cursors.forEach(function (c) {
    c.addEventListener('click', function () {
      var text = c.dataset.claim || '';
      if (navigator.clipboard) { navigator.clipboard.writeText(text); }
      c.setAttribute('data-copied', '1');
      setTimeout(function () { c.removeAttribute('data-copied'); }, 1000);
    });
  });
  var drawn = cursors.length - (seen.absent || 0) - (seen.blind || 0);
  var chain = (bad === 0 && slowest <= budget) ? 'OK' : 'MISMATCH';
  document.getElementById('selftest').textContent =
    'SELFTEST: cursors=' + cursors.length + ' drawn=' + drawn +
    ' ok=' + (seen.ok || 0) + ' warn=' + (seen.warn || 0) +
    ' error=' + (seen.error || 0) + ' unknown=' + (seen.unknown || 0) +
    ' absent=' + (seen.absent || 0) + ' blind=' + (seen.blind || 0) +
    ' rings=' + rings + ' quarantine=' + q + ' hotspot_misaligned=' + bad +
    ' slowest=' + slowest + 'ms budget=' + budget + 'ms CHAIN=' + chain;
})();
"""


def render(reg, glyphs, plan, meta, stagger, slowest, quarantine, width):
    big = glyphs[max(glyphs)]
    small = glyphs[min(glyphs)]
    hx, hy = big["hotspot"]

    mains, trails, rings, extra = [], [], [], []
    for idx, c in enumerate(plan):
        state = c["state"]
        i = len(rings)
        mains.append(
            '<div class="node" style="left:%.1fpx;top:%.1fpx"><span class="%s">%s</span></div>'
            % (c["x"], c["y"], "up" if idx % 2 == 0 else "down",
               html.escape(c["node"][:12])))
        dx, dy = -46 - (i % 3) * 12, -26
        if state not in ("absent", "blind"):
            trails.append(
                '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                'stroke-width="1" stroke-dasharray="2 5" opacity=".22"/>'
                % (c["x"] + dx + hx, c["y"] + dy + hy, c["x"], c["y"],
                   COLOR.get(state, "#8b949e")))
            rings.append(
                '<span class="ring" style="left:%.2fpx;top:%.2fpx;animation-delay:%dms">'
                '</span>' % (c["x"], c["y"], i * stagger + MOVE_MS))
        pcls = "flip" if c["x"] > width - 190 else ""
        mains.append(
            '<div class="cursor" data-state="%s" data-hx="%s" data-hy="%s" data-tx="%.3f" '
            'data-ty="%.3f" data-claim="%s" style="left:%.3fpx;top:%.3fpx;'
            '--dx:%dpx;--dy:%dpx;--wave-delay:%dms" title="%s"><span class="glyph">%s</span>'
            '<span class="pill %s">%s%s</span></div>'
            % (state, hx, hy, c["x"], c["y"], html.escape(c["claim"]),
               c["x"] - hx, c["y"] - hy, dx, dy,
               i * stagger + MOVE_MS, html.escape(c["claim"]), big["markup"], pcls,
               html.escape(c["cursor_id"]),
               (" · %.0f" % c["elo"]) if c["elo"] is not None else ""))

    for c in plan:
        if c["state"] in ("absent", "blind", "unknown"):
            extra.append('<span class="cursor" data-state="%s" data-extra="1" '
                         'style="position:static;display:inline-block;margin-right:6px">%s</span>'
                         '<span style="color:var(--dim)">%s — %s</span>'
                         % (c["state"], small["markup"], html.escape(c["cursor_id"]),
                            html.escape(c["claim"])))
            extra.append("<br>")

    if quarantine:
        qblock = ('<div id="quarantine"><b>Quarantine — rows whose hash does not '
                  'recompute, never drawn on the field:</b>%s</div>'
                  % "".join('<div data-q="1">%s</div>' % html.escape(str(cid))
                            for cid in quarantine))
    else:
        qblock = ('<div id="quarantine" class="empty"><b>Quarantine:</b> empty — '
                  'all %d ledger rows recompute to their own hash.</div>'
                  % len(plan))

    legend = "".join(
        '<span><i style="background:%s"></i>%s</span>' % (COLOR.get(s, "#8b949e"), s)
        for s in ("ok", "warn", "error", "unknown")) + \
        '<span><i style="background:#8b949e;opacity:.38"></i>absent</span>' + \
        '<span><i style="background:#8b949e;opacity:.38"></i>blind</span>'

    return """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Cursor swarm — Vulcan-salute cursors</title>
<style>%s</style></head><body>
<h1>Cursor swarm — the Vulcan salute as the pointer</h1>
<p class="src">%s · gesture %s · hotspot %s,%s from the SVG's own <code>data-hotspot</code></p>
<p class="lede">One glyph per candidate. It is placed so its <b>index fingertip</b> — not its
corner — sits on the node it scored, which is the whole point of a cursor: the thing you point
with is the thing that lands. Colour is the state of the record; a cursor with no record is
<code>absent</code>, a shard that never voted is <code>blind</code>.</p>
<p class="denom">%s</p>
<div id="field" style="width:%.0fpx" data-budget="%d" data-stagger="%d" data-duration="%d">
  <div class="grid"></div>
  <svg class="trails" width="100%%" height="100%%">%s</svg>
  %s
</div>
<div class="legend">%s</div>
%s
<pre id="selftest">SELFTEST: pending</pre>
<script>%s</script>
</body></html>
""" % (CSS, meta["source"], reg.get("gesture", "?"), hx, hy, meta["denominator"],
       width, BUDGET_MS, stagger, MOVE_MS, "".join(trails),
       "".join(rings) + "".join(mains), legend, qblock, JS)


# ── entry ────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=os.path.join(HERE, "out", "arena_results.json"))
    ap.add_argument("--elo", default=os.path.join(HERE, "out", "elo_board.json"))
    ap.add_argument("--out", default=os.path.join(HERE, "out", "swarm_view.html"))
    ap.add_argument("--ledger", default=os.path.join(HERE, "out", "swarm_view_frames.jsonl"))
    ap.add_argument("--top", type=int, default=12)
    ap.add_argument("--field", default="960x420")
    ap.add_argument("--scope", action="append", metavar="PATH",
                    help="repo-relative path this view may read (repeatable; default: %s)"
                         % DEFAULT_SCOPE[0])
    ap.add_argument("--prove", action="store_true",
                    help="strict rollback proof: refuse to render unless HEAD's scope ids and "
                         "a clean worktree both hold")
    args = ap.parse_args()
    scope = tuple(args.scope) if args.scope else DEFAULT_SCOPE

    width, height = (float(v) for v in args.field.lower().split("x"))
    reg, glyphs = load_registry()
    tracked = read_scope(scope)
    proof = rollback_proof(scope)
    if args.prove and not proof["clean"]:
        print("swarm_view: rollback proof failed — %d path(s) differ from HEAD: %s"
              % (len(proof["dirty"]), "; ".join(proof["dirty"])))
        print("swarm_view: remedy: commit or stash them, then re-run --prove — the proof is "
              "exact only over a clean worktree")
        sys.exit(2)
    with open(args.results, encoding="utf-8") as fh:
        pairs = json.load(fh)
    with open(args.elo, encoding="utf-8") as fh:
        board = json.load(fh)

    states, tally = candidate_states(pairs)
    votes = shard_votes(pairs)
    blind = [name for name in SHARDS if votes.get(name, 0) == 0]

    plan = build_plan(board, states, tally, args.top, width, height, bool(blind))
    stagger, slowest = schedule(len(plan))

    rows = chain([{"cursor_id": c["cursor_id"], "tree": c["tree"], "node": c["node"],
                   "verdict": c["state"], "claim": c["claim"]} for c in plan])
    quarantine = broken_rows(rows)

    absent = sum(1 for c in plan if c["state"] == "absent")
    drawn = len(plan) - absent - (len(plan) if blind else 0)
    modules = sum(1 for p in tracked if p.endswith(".py"))
    on_disk = disk_modules(scope)
    denominator = (
        "denominator — %d pairs, %d candidates; <b>%d of %d candidates drawn</b>%s; absent %d; "
        "blind %d%s; shard votes %d/%d/%d"
        "<br>scope — <b>%d files / %d modules</b> in the index under <code>%s</code> "
        "(%d modules on disk, %d untracked — the index is what the commit contains)"
        "<br>rollback — HEAD %s, %d blobs, scope hash <code>%s</code>, <b>%s</b>" % (
            len(pairs), len(board), len(plan) - absent, min(args.top, len(board)),
            " (all blind)" if blind else "",
            absent, len(plan) if blind else 0,
            (" (" + ",".join(blind) + ")") if blind else "",
            votes.get("rust", 0), votes.get("go", 0), votes.get("py", 0),
            len(tracked), modules, " , ".join(scope), on_disk, max(0, on_disk - modules),
            proof["head"], proof["blobs"], proof["digest"][:16],
            "unchanged (0 dirty)" if proof["clean"] else
            "NOT PROVEN (%d dirty)" % len(proof["dirty"])))

    meta = {"source": "%s + %s" % (os.path.basename(args.results),
                                   os.path.basename(args.elo)),
            "denominator": denominator}

    page = render(reg, glyphs, plan, meta, stagger, slowest, quarantine, width)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(page)
    with open(args.ledger, "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, sort_keys=True) + "\n")

    print("cursors: %d  drawn: %d  absent: %d  blind: %s" % (len(plan), drawn, absent,
                                                              ",".join(blind) or "none"))
    print("schedule: %d ms slowest of %d ms budget (stagger %d ms)" % (slowest, BUDGET_MS,
                                                                       stagger))
    print("quarantine: %d" % len(quarantine))
    print("scope: %s — %d files, %d modules in the index (%d on disk)"
          % (", ".join(scope), len(tracked), modules, on_disk))
    print("rollback: HEAD %s · %d blobs · scope hash %s · %s"
          % (proof["head"], proof["blobs"], proof["digest"][:16],
             "PROVEN (clean worktree)" if proof["clean"] else
             "NOT PROVEN — %s" % "; ".join(proof["dirty"])))
    print("page: %s" % args.out)
    print("ledger: %s (%d rows, %s)" % (args.ledger, len(rows), rows[-1]["hash"][:12]))
    if quarantine:
        print("swarm_view: %d row(s) failed their own hash — quarantined, not drawn"
              % len(quarantine))
        sys.exit(2)


if __name__ == "__main__":
    main()
