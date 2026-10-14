"""technique_blind_audit.py — which registered techniques are EXERCISE-ONLY?

READ THIS BEFORE QUOTING THE OUTPUT. The name says "blind" but the measurement
is narrower, and conflating the two produced a wrong finding once already:

    EXERCISE-ONLY = the registry's `where` symbol has no reference outside
                    `technique_wiring/` (its own exercise adapter calls it).
    BLIND         = no reference ANYWHERE. A STRICT SUBSET of exercise-only.

This tool reports the former. `technique_wiring/` is excluded from the corpus on
purpose (we want *production* callers), so a symbol that only its own adapter
calls scores here — that is exercise-only, NOT "zero callers". Measured against
the excluded region, every symbol this tool reports does have a call site inside
`technique_wiring/`.

GENERAL RULE this tool taught the hard way: a zero is only as good as the corpus
you searched. Always state the corpus, and re-test any zero against the region you
excluded. Three separate false zeros in one session came from excluded or
ill-matched corpora.

Intra-module calls COUNT as references (v1 wrongly excluded the defining FILE,
which false-flagged every symbol called from a sibling function — e.g. EP461
divergence_gate is called at verification_gate.py:431 in its own module).

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
#: Paths that are NOT production callers. `tests/` and `state/` are excluded
#: because a test or a throwaway probe that merely NAMES a symbol would otherwise
#: score as a production caller -- contamination observed live: adding a probe
#: script that listed the symbol names moved this report from 122/22 to 129/15
#: without a single line of production code changing.
NOT_PRODUCTION = ("tests/", "state/", "tools/technique_exercise_only_audit.py")

for f in Path(".").rglob("*.py"):
    s = str(f).replace("\\", "/")
    if any(x in s for x in EXCL):
        continue
    if any(s.startswith(x) for x in NOT_PRODUCTION):
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

# --- 3. exercise-only = no hit outside technique_wiring/ (NOT "never called") ---
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
print("PRODUCTION-CALLED      : %d" % LIVE)
print("EXERCISE-ONLY (of those): %d" % len(BLIND))
print("  ^ these are called ONLY from technique_wiring/ -- they are NOT uncalled.")
print()
for ep, w, short in BLIND:
    print("  %-7s %-56s sym=%s" % (ep, w[:56], short))
