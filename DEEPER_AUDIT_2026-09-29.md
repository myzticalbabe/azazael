# DEEPER DIVE AUDIT — 2026-09-29 (14:00–14:40)

A second pass over the audit tooling. The first pass found the same false-PASS
class three times in three new tools, so the question here was not "what is
broken in the code" but **"which of the things telling me the code is fine are
lying, and by how much."**

Every number was measured in this session. Four surfaces were covered: the
auditors, the graph artifact they rest on, the dead-code scope boundary, and the
audit documents. Two findings are fixed here, four are recorded unfixed.

---

## Summary

| # | Finding | Surface | Status |
|---|---|---|---|
| F1 | `artifact_freshness` watches 745 of 3,660 graph sources — 79.7% invisible | graph | **fixed** |
| F2 | mtime comparison cannot see staleness after a git checkout | graph | **fixed** |
| F3 | `aggregate_suite_gate` overwrote a 3,698-test report with a 0-passed run | auditors | recorded |
| F4 | `verify_hashes` crashed on cp1252 and never produced a verdict | auditors | **fixed** |
| F5 | No gate distinguishes "could not run" from "ran and found problems" | auditors | recorded |
| F6 | 34 of 75 tools carry non-ASCII; several will crash a Windows console | auditors | recorded |
| F7 | The 9.5% preflight scope contains 5 of 161 dead-code findings — widening buys ~nothing | scope | measured, not a bug |
| F8 | Live registry is 250 worms; the docs say 226 (×39), 232, 224, 104, 93, 91 | docs | recorded |

---

## F1 / F2 — the freshness gate could not see its own inputs

`tools/artifact_freshness.py` answered "OK: every derived artifact is at least
as new as its sources" on a tree where the graph was stale.

**F1: the watched source set was 20.3% of the real one.** The registry declares
every artifact as derived from `src/**/*.py`. The graph is actually derived from
**3,660 files** — the set recorded in `graphify-out/manifest.json`, of which
1,507 are `.md`, 205 `.html`, 158 `.png`, 137 `.json`. Only 745 are `.py` under
`src/`. So 79.7% of the graph's real inputs were invisible to the check.

Proven by mutation — each case makes the graph genuinely stale, then runs the
gate:

```
BASELINE                                   rc=0   OK
WATCHED   src/CORE/WORMS/expansion/mesh.py rc=1   caught
BLIND     scripts/sync_all.py               rc=0   OK   <- false PASS
BLIND     ARCHITECTURE.md                   rc=0   OK   <- false PASS
BLIND     tools/graphify_interpreter.py     rc=0   OK   <- false PASS
```

**F2: and mtime is the wrong instrument entirely.** The check compares
modification times, but `git checkout` and `git clone` restamp every tracked
file with the checkout time. A committed artifact is therefore *always* newer
than the sources it was derived from, and the comparison reports "current" no
matter how far the content has drifted.

This was not hypothetical. The committed `NEURAL_MESH_FUNCTION_TODO.md` points
at `learning_pipeline:DataPipelineWorm.temporal_cross_validation` **L438**. That
function is at **L442** in the current source. Regenerating the artifact shifts
every `learning_pipeline` entry by exactly +4. The artifact is wrong, and the
gate called it `current  0` newer sources.

### The fix

`graphify-out/manifest.json` records, for every ingested file, an `ast_hash`.
That value is a **plain md5 of the file's bytes** (verified against md5, sha1,
blake2s-128 and sha256-128 on sample entries). So content drift is decidable
without mtimes at all.

`graph_content_drift()` reads the newest manifest and compares each recorded
md5 against the file's current md5. Any difference means the graph was derived
from content that no longer exists.

Two bugs in the fix itself, both caught before commit:

- The first glob was `graphify-out/*/manifest.json`, which **misses the current
  manifest** — it sits at `graphify-out/manifest.json`, at depth 1. The glob
  fell through to `graphify-out/graphify-out/manifest.json`, a nested manifest
  from Sep 18 with 1,368 *absolute* Windows keys, and reported 134 spurious
  changes. The correct answer is 6.
- Manifest keys are not all relative; older ones are absolute. They are now
  relativised so the evidence reads identically on W11, WSL and bare metal.

The gate now reports:

```
graph inputs: DRIFTED -- 6 of 3668 files changed since graphify-out/manifest.json,
              0 missing (md5 vs recorded ast_hash; mtime cannot see this after a
              git checkout)
```

For the record, the 12:13 manifest shows **24** changed files, including
`src/CORE/direct_memory.py`, `src/CORE/local_memory.py`, `reflexion.py` and
`TERENCE.py`. The mtime rule could see **0 of 24**.

### The tests, and proof they bite

`tests/test_artifact_freshness.py` grew from 7 to 16 tests. The load-bearing one
pins the checkout case directly: a source whose content changes while its mtime
is deliberately left older. The mtime rule must report clean there; the content
rule must not.

Mutation-tested. All bite:

| Mutation | Result |
|---|---|
| verdict ignores drift | BITES (1 failed) |
| glob depth `*/` — **the real original bug** | BITES (8 failed) |
| pick the oldest manifest | BITES (1 failed) |
| absolute keys not relativised | BITES (1 failed) |
| drift check restricted to `.py` (reintroduces F1) | BITES (1 failed) |

A sixth mutation initially **survived**: sorting the manifest list by name. That
test was wrong, not the tool — sorting by name happens to pick the right file,
because `"graphify-out/manifest.json"` sorts after `"graphify-out/graphify-out/…"`.
The defect was the glob *depth*. The test was rewritten to place the correct
manifest where a `*/` glob cannot see it, and then it bit (8 failures).

---

## F4 — a gate that could not report, exiting the same code as one that could

`tools/verify_hashes.py` prints ✅/❌/⚠️/📦/🎯. Windows stdout defaults to
cp1252, which encodes none of them. The first emoji reached raised
`UnicodeEncodeError` and killed the run **after three lines of banner, before
any verdict**:

```
rc=1
=================================================================
  FILE HASH VERIFICATION — Ubuntu vs G: Archive
=================================================================
UnicodeEncodeError: 'charmap' codec can't encode character '\u274c'
```

So the tool that exists to answer "do the archive hashes match" had never
answered it on this machine, and its exit code was `1` — identical to what
"hashes mismatched" produces. `git log` shows the file has exactly one commit,
from the initial full-tree snapshot: it has never worked here.

Fixed by reconfiguring stdout/stderr to UTF-8 with `errors="replace"`, so an
unencodable glyph degrades instead of losing the run. It now reaches a real
verdict: `❌ Source not found: C:\Users\clint\Desktop\azazael-project-e`.

**That verdict is itself the finding.** The tool is WSL-side: its `SRC` is
`~/Desktop/azazael-project-e` and its `DST` is `/mnt/windows/g/…`. Neither
exists on Windows, so here it can only ever report "source not found". Its
exit code is not a hash verdict on this platform, and should not be read as one.

`tests/test_gate_output_encoding.py` forces a cp1252 stdout and asserts the tool
reaches a verdict rather than dying. Removing the reconfigure makes both tests
fail.

---

## F3 — a gate that destroys the evidence it is meant to protect

Sweeping the checker tools rewrote two committed artifacts, which I restored:

- `logs/aggregate_suite_report.json` — a real report of **3,698 passed, 2
  failed, 38 skipped in 1,524.90s** was overwritten by a run of **0 passed, 0
  failed, 1 error in 12.78s**. Default arguments, no guard, no refusal to
  clobber a good report with a degenerate one.
- `NEURAL_MESH_FUNCTION_TODO.md` — regenerated with the corrected line numbers
  (this is F2's evidence).

Both restored from git; the tree is as I found it. `mesh_function_preflight`
also writes, despite reading as a checker. **Running the audit suite is not
side-effect-free**, which is worth knowing before wiring these into CI.

---

## F5 — "could not run" and "found problems" share an exit code

Generalisation of F4, and it is the deeper defect. Across the 48 tools with an
exit-code contract, a crash and a finding are both `1`. `type_check_gate` is
the one tool that reasons about this correctly — it prints *"treating this as a
failure because an unchecked tree must not read as a clean one"* and returns 1
when no checker is available — but it returns 1 for a genuine diagnostic too, so
a caller still cannot tell the two apart.

This is a contract change across many tools, so it is **recorded, not fixed**.
The narrow version worth doing: give the tools that spawn a subprocess a
distinct code (e.g. 125, as `type_check_gate` already uses internally) for
"could not run".

---

## F6 — 34 of 75 tools carry non-ASCII

A repo-wide scan: 34 of 75 files in `tools/` contain characters above U+007F.
Emoji appear in `backup_to_g`, `flask_dashboard`, `health_check_azazael`,
`hydra_verbose`, `memory_profile`, `streamlit_dashboard` and `verify_hashes`.
Any of them can die the same way F4 did, on the same console, at whatever line
first reaches the glyph.

My own audit script hit this exact crash twice while producing this document,
which is the clearest evidence of how easy it is to trip. Recorded, not fixed —
the general fix is the same two-line reconfigure, applied per tool.

---

## F7 — the 9.5% scope gap is in the wrong place

`mesh_function_preflight`'s `SCOPE_GROUPS` covers 61 module stems of 645 under
`src/` (9.5%). The obvious reading is that widening it would surface a backlog.

Measured, it would not. Of the 161 findings `dead_function_check` reports:

| | count |
|---|---|
| inside the preflight's 61-stem scope | **5** |
| outside it, across 63 modules | **156** |

The narrow scope is not where the dead code is. `dead_function_check` is already
repo-wide (13,356 call edges, 3,583 candidates, no scope filter), so the dead-code
picture is complete; what the preflight does not cover is the *pending-verdict*
classification, in 584 modules that contain almost none of the dead functions
worth acting on. Widening it would declare pending a large set of mostly-public
API (`get_secret`, `audit_secrets`) and research code (`bdam_blocks`,
`fgsm_delta_f1`) — the same over-declaration the P1 correction already rejected.

**No change made.** This is a measurement, and it says the P1 scope question is
the wrong question.

---

## F8 — the most-repeated number in the docs is wrong

Live: `WORM_REGISTRY` holds **250** worms.

| Claim | Occurrences in root `*.md` |
|---|---|
| "226 worms" | 39 |
| "104 worms" | 14 |
| "224 worms" | 6 |
| "93 worms" | 6 |
| "91 worms" | 6 |
| "232 worms" (skill catalog) | — |

At least six mutually inconsistent counts, none current, all stated as present
tense. The single most repeated figure is off by 24. Recorded — rewriting
dozens of documents' numbers is a separate piece of work, and several of these
figures are quoted from dated measurements that were true when written.

---

## What was checked and found sound

Recording these, because an audit that only lists defects misrepresents the
surface:

- **`type_check_gate`** — returns 1 with an explicit, correct message when no
  checker can run. Correct behaviour, and the one tool that reasons about the
  F5 class out loud.
- **`fs_hygiene`** — prints `FAIL: 6 regression(s)` and exits **0**. This looked
  like F5 and is not: it gates on `--check`, and `--check` exits 1. Report mode
  and gate mode are distinguished by flag, as documented.
- **`dead_function_check`, `dict_key_contract`, `scope_coverage`,
  `manifest_reconcile`** — the four tools already mutation-tested in the first
  pass. All still behave.
- **`artifact_freshness`'s report/graph consistency check** — sound, and
  unchanged. It catches the case the docstring describes: a fresh report beside
  a graph whose `graph.json` write was refused.

## A note on measurement errors made during this audit

Three of my own intermediate readings were wrong and were caught before
becoming findings:

1. A `git log … | cat` pipeline made `$?` report `head`'s exit code, not the
   tool's. `type_check_gate` was nearly reported as "exits 0 while claiming
   failure"; it exits 1 correctly. **Exit codes must be read without a pipe.**
2. The first manifest-resolution pass treated the manifest as basename-keyed
   because 196 of 3,660 keys are bare. It is keyed by relative path; the other
   3,464 resolve fine. The "462 resolved" figure was my bug, not the repo's.
3. `fatal: ambiguous argument 'gdrive/master..HEAD'` on the first command was
   not a missing remote — the shell's default cwd is `C:/Users/clint`, a
   different repository. `C:/Users/clint/azazael` is its own repo.

## Related

`NEURAL_MESH_PRIORITIES_2026-09-29.md`, `GRAPH_TOOLS_AUDIT_2026-09-29.md`.
