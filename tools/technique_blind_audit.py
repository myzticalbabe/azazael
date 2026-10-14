"""technique_blind_audit.py — which registered techniques have a BLIND mechanism?

BLIND = the registry's `where` symbol has NO reference anywhere in the repo
except the line that defines it. Intra-module calls COUNT as references (v1
wrongly excluded the defining file, which false-flagged every symbol called from
a sibling function -- e.g. EP461 divergence_gate is called at
verification_gate.py:431 in its own module).

Also separates PROSE `where` values ("ACID agents: ...", survey/doctrine rows)
from real MODULE:symbol bindings -- prose rows have no mechanism to be blind.
"""
import re
from pathlib import Path

EXCL = ("technique_wiring", "__pycache__", "archive", "archived",
        ".build", ".venvs", "node_modules", "site-packages")

# ---------- 1. resolve `where` ----------
srcs = list(Path("src/CORE/technique_wiring").glob("*.py"))
srcs += [Path("src/CORE/technique_runtime.py")]
wmap = {}
for p in srcs:
    t = p.read_text(encoding="utf-8", errors="replace")
    for m in re.finditer(r"['\"](EP\d+)['\"](.{0,320}?)(?=['\"]EP\d+['\"]|\Z)", t, re.S):
        ep, blob = m.group(1), m.group(2)
        strs = re.findall(r"['\"]([^'\"]{4,})['\"]", blob)
        cand = [s for s in strs if ":" in s or s.startswith("no-host")]
        if cand and ep not in wmap:
            wmap[ep] = cand[0]

nohost, prose, real = [], [], {}
for e, w in wmap.items():
    if w.startswith("no-host"):
        nohost.append((e, w))
    elif ":" not in w:
        prose.append((e, w))
    else:
        mod, sym = w.split(":", 1)
        mod, sym = mod.strip(), sym.strip()
        # a real binding has a dotted module path and no spaces
        if " " in mod or "/" in sym or not sym:
            prose.append((e, w))
        else:
            real[e] = (mod, sym)

print("EPs with resolved `where` : %d" % len(wmap))
print("  declared no-host        : %d" % len(nohost))
print("  prose / survey (no sym) : %d" % len(prose))
print("  bound to MODULE:symbol  : %d" % len(real))

# ---------- 2. index ONLY the target symbols ----------
targets = set()
for mod, sym in real.values():
    targets.add(sym.split(".")[-1])

hits = {s: [] for s in targets}
files = []
for f in Path(".").rglob("*.py"):
    s = str(f).replace("\\", "/")
    if any(x in s for x in EXCL):
        continue
    files.append((f, s))
print("caller-corpus files       : %d" % len(files))

for f, s in files:
    try:
        lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        continue
    for i, ln in enumerate(lines, 1):
        for tok in set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", ln)):
            if tok in hits:
                hits[tok].append((s, i, ln))

print("indexed target symbols    : %d" % len(hits))

# ---------- 3. blind = every hit is a def/class line for that symbol ----------
BLIND, LIVE = [], 0
for ep, (mod, sym) in sorted(real.items(), key=lambda kv: int(kv[0][2:])):
    short = sym.split(".")[-1]
    refs = []
    for s, i, ln in hits.get(short, []):
        st = ln.strip()
        if re.match(r"^(async\s+)?(def|class)\s+%s\b" % re.escape(short), st):
            continue                      # the definition itself, not a use
        refs.append((s, i))
    if refs:
        LIVE += 1
    else:
        BLIND.append((ep, mod + ":" + sym, short))

print()
print("LIVE  : %d" % LIVE)
print("BLIND : %d" % len(BLIND))
print()
for ep, w, short in BLIND:
    print("  %-7s %-56s sym=%s" % (ep, w[:56], short))
