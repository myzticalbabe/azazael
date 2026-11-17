# GAP ANALYSIS — the push-gate path (2026-11-16)

**HEAD when written:** `79bb4095` on `professional-public-standards-rule-0z-r`, 29 ahead
of `origin/…` at `cd908411`.
**Expiry:** the numbers below are trusted through **2026-11-23**. After that, re-measure
rather than quote — every figure here names the command that produced it for that reason.

**What a gap is in this document.** Not a wish, not an idea: a *measurable* difference
between what a claim says and what the tree does, or between the population a gate
judges and the population it appears to judge. Each one below carries the command and
the line it printed. A gap with no command would be a recollection, and this session
already paid for one of those.

---

## 1. The trigger — what this session was sent to fix

The branch carried 29 unpushed commits, five of them Sarah's. `git push` was refused by
the `changeset-focus` stanza of `.githooks/pre-commit`, and the only way through was
`ALLOW_BULK_COMMIT=1` — a declaration spent on work that had already been split
correctly, which is what that constant is explicitly *not* for (AGENTS.md: "a
declaration to justify, not a silent bypass").

Root cause: the gate judged `git diff base HEAD` — the **union** of the whole range —
while its caps are **per-commit** numbers (8 files, 150 changed lines in one file). A
range of 29 focused commits therefore read as one 1,215-file changeset carrying 24
oversized files. One commit in the range (`37c29a95`) genuinely did carry a 206-line
single-file change; the other 28 were dragged in by arithmetic, not by dirt.

---

## 2. Gaps

### G1 — a range was judged as one changeset — **FIXED in `81b922ae`**

**Class:** wrong denominator. The gate reported a per-commit violation as if it were a
property of a range, so 28 clean commits inherited one commit's finding.

**Evidence, after the repair:**

```bash
python scripts/commit_gate.py --hook --base cd90841137cd28a50728eacee25946856c0c7ec0
# → RC=0
#   23 commit(s) judged on their own changeset, each within the caps
#   (6 excused by their own message, 0 clean merge(s) skipped,
#    0 merge(s) with their own edits), 19 generated file(s) exempt
```

**Control — the exemption does one job, not two.** Removing `ARC/esquire/pins.json`
from `GENERATED_PATHS` in-process changes exactly one verdict:

```
A (as shipped):      problems=0   judged=23 declared=6 generated_rows=19
B (entry removed):   problems=1   judged=23 declared=6 generated_rows=17
  ! ARC/esquire/pins.json changes 206 lines (limit 150/file). Split 37c29a95, …
```

**Control — the exemption's premise is true, not asserted:**

```bash
python tools/arc_ledger.py --check
# → RC=0  CANONICAL: ARC\esquire\pins.json -- 29714 bytes, 20 pins, CRLF line endings
```

**Cost, measured:** the range path takes **1.08 s for 29 commits**; the index path
(`--hook` with no `--base`) takes **0.19 s**.

---

### G2 — an exemption is proved by *naming*, not by *regenerating* — **INSTRUMENT LANDED in `97aebbc6`**

**Class:** shape-check standing in for a behaviour-check — the same defect class HED-10
records twice, where a detector trusted a shape and reported a truth it had not tested.

`tests/test_commit_gate.py:80-82` verifies each `GENERATED_PATHS` entry like this:

```python
for path, generator in cg.GENERATED_PATHS.items():
    source = (ROOT / generator).read_text(encoding="utf-8")
    assert Path(path).name in source, (path, generator)
```

That asserts the *generator's source mentions the basename*. It passes for a generator
that names the file in a comment and writes something else, for a generator whose
output drifted from disk, and — the case that matters — for a generator that is never
run. Five entries are currently exempt on this evidence.

**Measured after the instrument landed.** `python tools/generated_audit.py` prints
`5/5 excused paths accounted for (DRIFTED=1, NO-VERIFIER=2, PROVED=2)`. The DRIFTED
entry is `docs/INDEX.md`: **disk 32 460 bytes against a 33 784-byte render**, so the
index on disk names 287 documents where a fresh render names 298. The exemption is
true for four entries and is currently concealing a stale file for the fifth — a
finding that was invisible while the test only checked that a name appeared in a
source file. The two `NO-VERIFIER` entries are `logs/basedpyright_*.json`, which
record a MEASUREMENT rather than a rendering; they are registered with their reason
and counted separately from PROVED rather than rounded into it.

The instrument reads `GENERATED_PATHS` by import from `scripts/commit_gate.py`, never
from a copy, so the table and its auditor cannot drift apart (HED-5).

**Avenue.** Give each generator a `--check` contract and call it. `tools/arc_ledger.py`
is the template already in the tree: `--check` renders, compares bytes, exits 0
identical / 1 drifted-and-named / 2 unreadable. An entry whose generator exposes no
`--check` should be *reported* as unchecked rather than passed — the registry pattern
`tools/preflight_all.py` already uses for uncontrolled gates ("NONE … never green").

**Price:** ~40 lines in the test, one subprocess per entry (5 today, +0.6 s).
**Risk of deferring:** the table is a growing list of hand-granted exemptions whose
truth decays silently, which is precisely what the 2026-11-03 narrowing and this
session's repair were both reacting to.

---

### G3 — the interpreter claim has no check, and the tree contradicts it — **MEASURED; DECISION OPEN (G3)**

**Measured 2026-11-16** by `python tools/interpreter_audit.py`, which runs the pin
rather than reading it:

```
interpreter_audit: pin      C:/Azazael/.venvs/py315t/Scripts/python.exe
interpreter_audit: measured 3.15  gil_enabled=False
interpreter_audit: canon    3.16
interpreter_audit: DRIFTED -- hook pin measures 3.15, canon claims 3.16
interpreter_audit: DECISION OPEN (G3)
```

The drift is real and now falsifiable. The tool deliberately does **not** move the
pin: 3.15t is free-threaded and is the documented GIL sidecar for packages with no
`cp316t` wheel, so pinning it is a defensible engineering choice and pinning 3.16t
is a defensible parity choice. Which one gates commits is the principal's call, so
the tool reports and stops.

**Class:** a canon sentence with no instrument. AGENTS.md §"Tooling facts" states:

> **Session startup, test suite, commit hooks, and all gates use 3.16t**

The tree says otherwise:

```bash
sed -n '69,83p' .githooks/pre-commit
# 71: PYTHON3="C:/Azazael/.venvs/py315t/Scripts/python.exe"
#     comment: "# 3.15t production interpreter … Pin here so every gate runs on 3.15t."
# 75-83: fallback ladder = py315 → py314m → python3.15t → python3   (no py316t tier)
```

`tools/preflight_all.py:1008-1017` resolves `"python3"` to **py315t** as well, so the
gate registry agrees with the hook and disagrees with canon. Both venvs exist on this
box (`py315t`, `py316t`), so this is a stale pin, not a missing interpreter: the hook's
comment reasons about 3.14t retirement and predates 3.16t entirely.

The same `--self-test` run also prints an honest note that partly contradicts the
hook's own comment — and only one non-blocking gate is the second interpreter:

```
[note] the hook runs its gates on 2 different interpreters (py315t, pmb-venv)
       -- resolved by NAME; a gate may behave differently depending on which one
39 gate(s), 0 failure(s), 0 blind, 8 with no declared control        RC=0
```

(`pmb-venv` covers `pmb-outcome-observer` alone, whose exit code the hook ignores.)

**Avenue — a decision, not a repair.** Both directions are legitimate, and choosing
silently is the failure: either add `py316t` as tier 0 in the hook ladder and in
`resolve_interpreter`, or give the canon sentence its scope ("hooks: 3.15t; session and
tests: 3.16t"). Whichever is chosen, add the check that reads the pin and compares it
to a declared value, so the sentence cannot drift again.

**Price:** 2 lines plus 1 test. **This one is the principal's call** — it changes which
interpreter every commit is gated under.

---

### G4 — generatedness is a hand-kept table discovered reactively — **OPEN**

**Class:** a derivation replaced by a list. `GENERATED_PATHS` holds 5 entries, and each
arrived *after* a gate blocked a push: 2026-11-14 (`SHARD_INDEX.json`, a regeneration
measured at 43,345 lines), 2026-11-16 (`basedpyright_{report,baseline}.json` ×2, then
`pins.json`).

Each entry is true now — and each was found by being refused, not by looking. The sixth
will arrive the same way: as another blocked push and another temptation to reach for
`ALLOW_BULK_COMMIT=1`.

**Avenue.** An `--audit-generated` sweep that names every tracked file a generator would
rewrite byte-identically, so the table is *derived*. It depends on G2: the sweep needs a
`--check` per generator before it can tell "regenerable" from "regenerated once".

**Price:** high (~1 day). **Value grows with the table** — do it when the table passes
~10 entries, not at 5.

---

### G5 — cost is linear in range length — **MEASURED**

`commit_violations` makes two git subprocesses per commit (`diff-tree --numstat` and
`diff-tree --name-status`). 29 commits → 58 subprocesses → 1.08 s.

**Avenue:** one `git log --numstat -z` pass. **Not urgent on its own** — the ordinary
(index) path every commit actually runs costs 0.19 s. See G5b for why the linear term
is nonetheless not the harmless one it first appears to be.

---

### G5b — one unreadable commit refuses the whole range — **OPEN, found by running**

**Class:** one failing leg aborting the run — the shape HED-6 forbids ("no leg may abort
the run; the middle path is a recorded failure next to the readings that did land").

**How it was found, which is the point.** This gap was not reasoned out; it surfaced
while *running* the acceptance command I had just written into the build instructions.
The first version of that command said `--base origin/main`:

```
python scripts/commit_gate.py --hook --base origin/main
# → RC=1  cannot read origin/main..HEAD (git diff-tree … f59c31c3 timed out after
#          60 seconds) -- refusing to pass on a range that was not read
```

Three measurements turn that into a characterised defect:

```
git rev-list --count origin/main..HEAD                    → 1909
git diff-tree --no-commit-id --numstat -r --root f59c31c3 → RC=0, 116 s, 31 426 rows
git log -1 --format=%B f59c31c3 | grep -ic bulk           → 0
```

So: `f59c31c3` ("track: snapshot ALL project files — full local tracking") changes
**31,426 files**, takes **116 s** to read against a **60 s** bound
(`scripts/commit_gate.py:114`), and carries **no** bulk token. Because
`declares_bulk` is checked *before* the read, so the intent is right — a declared bulk
commit is never read at all — but this commit never declared, so it is read, times out,
and the range is refused with a message that is indistinguishable from real dirt.

**Avenue.** On a per-commit read timeout, record **that sha** as `unreadable` and keep
judging the rest; refuse the range only if nothing was readable. A 60 s bound is a fine
bound — the defect is that exceeding it is fatal to 1,908 commits that were never in
question.

**Price:** ~15 lines. **Contrast:** the identical range over the branch's own upstream
takes 1.08 s and returns RC=0, which is why this was invisible until a wider base was
tried.

---

### G6 — a green gate does not cover the client's live MCP session — **OPEN**

**Class:** the gate proves the wrong surface. Measured twice this session:

```
pmb__prepare(...)  →  {"code":-32600,"message":"Session not found"}
```

while, in the same session:

```
[PASS] pmb-daemon   initialize pmb in 14 ms
memory-tools: pmb-recall rc=0 chars=1003 ok
```

Both are true. The gate proves the **daemon** answers `initialize`; `session_start`
proves the **direct client** can recall; neither says anything about the **stdio child
this client is holding**, whose transport session is dead. The failure is therefore
discovered by a tool call failing mid-task, not by the gate that exists to prevent
exactly that `[BLOCKED]` state.

The workaround is already written and is the model for the fix —
`tools/session_start.py` calls the direct client precisely to "bypass a stale MCP
transport", so no memory work was lost. What is missing is the *row*.

**Avenue.** Add a `pmb-transport` gate row that reads the client's own load log (the
same authority `session_start` already trusts for LOADED/CONFIG-ONLY) and requires a
pmb connect recorded after the config mtime, plus one successful tool call from this
process. On failure: `[BLOCKED]`, named in the agent's first sentence.

**Price:** ~1 hour; the load-log reader already exists.

---

## 3. What this analysis does not cover

Stated so the next reader does not mistake absence for clearance:

- **Other lanes' paths.** `git status` carries modified `Project_Nurse_Ratchet/*`,
  `docs/bible/*` and untracked files, none of them touched or judged here.
- **The other ten hook stanzas** and the evidence tier — not measured this session.
- **The Sarah build itself.** These gaps are about the gate path that lands it.

**One risk named, not fixed (out of scope, and it belongs to whoever owns the repo
root):** the tree root holds untracked `credentials_final.json`,
`credentials_real.json`, `credentials_template.json` and `add_passwords.py`. AGENTS.md
§0.3 already forbids `git add -A` partly for this reason; a single lane that ignores
that rule stages live credentials. This is a disclosure question for the principal —
whether those files should exist untracked in a pushed tree at all.

**Re-checkable since `97aebbc6`.** `python tools/disclosure_audit.py --strict` names
its population (`untracked, not ignored`), its denominator
(`listed=543 scanned=44 skipped-large=15 skipped-binary=484`), and fails on **three**
files: `add_passwords.py`, `credentials_final.json`, `credentials_real.json`.
`credentials_template.json` is labelled a template and excluded from `--strict`
unless `--fail-on-template` is passed; the 13 PNGs under `evidence/` are labelled
`screenshot` for the same reason. No matched value is ever printed — a scanner that
prints the secret has made a second copy of the leak.

---

## 4. Order of work

| # | gap | why here | price |
|---|-----|----------|-------|
| 1 | ~~**G3** interpreter~~ | **landed `97aebbc6`**: `interpreter_audit.py` measures DRIFTED; the pin is the principal's call | done |
| 2 | ~~**G2** `--check` per generator~~ | **landed `97aebbc6`**: `generated_audit.py` proves 4/5 and names `docs/INDEX.md` stale | done |
| 3 | **G6** transport row | turns a silent dead tool path into a named gate row | ~1 hour |
| 4 | **G5b** continue past an unreadable commit | one commit can refuse 1,908; ~15 lines | small |
| 5 | **G5** batch the git calls | only past ~100-commit ranges | medium |
| 6 | **G4** derive the table | needs G2 first; worth it past ~10 entries | ~1 day |

G1 is closed and landed as `81b922ae` (3 files, 507 insertions / 51 deletions; its own
`ALLOW_BULK_COMMIT=1` declared for that commit alone, which is why the range gate now
excuses it individually rather than on the range's behalf). Re-measured after it landed,
with the fix commit itself inside the range:

```
python scripts/commit_gate.py --hook --base '@{upstream}'
→ RC=0  23 commit(s) judged on their own changeset, each within the caps
        (7 excused by their own message, 0 clean merge(s) skipped,
         0 merge(s) with their own edits), 19 generated file(s) exempt
```

That is the whole answer to the trigger in §1: the push range passes with **no**
override — 30 commits, 23 judged individually, 7 that declare bulk in their own
messages, one of which is this fix. The two commits that were dragged in by arithmetic
before (28 of 29 were clean) are now judged and pass on their own evidence.
