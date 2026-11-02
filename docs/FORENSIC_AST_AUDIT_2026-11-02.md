# Forensic + AST audit — session 2026-11-02

Written after five subagent jobs died mid-run (`session_expired` / `waiting_room_required`),
to establish what actually survived and what is only claimed.

## Method

Two instruments, both re-runnable:

| instrument | scope | output |
|---|---|---|
| AST sweep | 1881 `.py` files across `src/`, `tools/`, `scripts/`, `tests/`, `azazael-forensics/{forensics,tests}` and all six `Project_*` dirs | `docs/ast_audit_2026-11-02.json` |
| Hardening sweep | same roots, AST-level exception handling + literal path scan | `docs/hardening_audit_2026-11-02.json` |
| Diff inspection | `git diff` of every file a subagent touched, read in full | `azazael-forensics/.git`, monorepo working tree |

## Verdict: the effort survived

**0 syntax errors in 1881 files.** Nothing was truncated, nothing was overwritten with a
partial write, no file ends mid-statement. Eight files were flagged as "empty" by the
truncation heuristic — all eight are `__init__.py` package markers, which are legitimately
empty.

**One instrument false positive, recorded so it is not re-litigated.** The duplicate-definition
detector fired on `src/CORE/failure_shim.py: note_failure` at lines 68, 74, 91, 100. That is
**correct Python**: three `@overload` stubs plus one implementation. The detector did not skip
`@overload`-decorated functions. The defect is in the detector, not the file.

## What the subagents produced, and whether it runs

| artefact | state | proof |
|---|---|---|
| `azazael-forensics/forensics/portable.py` — `CORE` import and `~/.azazael` default removed | **salvaged, correct** | diff is 32+/16−; no `from CORE` remains; `locate_board_db` is explicit arg → `FORENSICS_BOARD_DB` → `AZAZAEL_MEMORY_DIR` → raise `Environment` |
| tool count 49 → 52 in `README.md`, `CAPABILITIES.md`, `home.py` | **salvaged** | matches `test_home.py::test_registry_counts`; test suite 6 passed |
| `azazael-forensics/LICENSE` + `NOTICE` + `license` field | **salvaged** | md5 `09b658f7…` — identical to the canonical `Project_Nurse_Ratchet/LICENSE` after CRLF/blank-line normalisation, despite being transcribed by hand |
| 4 × `pyproject.toml` (CRADLE, FLAME, FLAMING_SWORD, SHARDEX) | **salvaged** | all 6 pyprojects parse under `tomllib`; every `readme` path resolves; **all 7 declared entry-point callables exist** (cradle 358, flame_engine 465, sword 1322, sentinel 302, housekeep 372, shardex 887, meshscene 557) |
| `Project_ELIZA/{NOTICE,CITATION.cff}`, `Project_Nurse_Ratchet/NOTICE` | **salvaged, and the best editorial work of the session** | NOTICE now states ELIZA is forensic, names Nurse Ratchet as a SEPARATE project, and refuses to attribute files that do not ship |
| 5 replacement workers (ELIZA repoint, docs sanitation, seed script, port plan) | **DID NOT LAND** | all five returned `session_expired` (410) / `waiting_room_required` (428). No partial files were written |

Nothing needed reverting.

## The one real open defect: ELIZA's subject is still wired to the wrong stack

Every downstream claim was corrected; the code was not. On disk right now:

| file | says |
|---|---|
| `PUBLIC_MANIFEST.json` `summary` | "A therapeutic-agent loop, the psychological network it reasons over…" |
| `pyproject.toml` | entry point `eliza-psyche` |
| `README.md` line 3 | "A therapeutic agent that is honest about what it cannot do" |
| `NOTICE` | "Project ELIZA is the forensic investigation suite…" |

The owner's ruling is that ELIZA is forensic investigation and Nurse Ratchet is the
therapeutic agent. So three files currently describe the wrong project, and the NOTICE
contradicts all three. `never_ship` and `deny_substrings` in the manifest are already
correct and must not be touched — they hold the right line ("the method ships, the case
does not").

Where ELIZA's actual method lives, for whoever does the repoint: `C:/Users/clint/.bcc_audit/`
(232 MB — `03_tooling/` holds `beam1_propose.py`, `beam1_apply.py`, `beam_fetch.py`,
`behavior_trace.py`, `grade_leads.py`, `bcc_graph3d.py`; `00_raw/` is 186 MB of evidence that
must never be copied). `C:/root/BCC-REINVESTIGATION/` is a 37 KB stub, not the suite.

## Hardening gap analysis

Real counts from `docs/hardening_audit_2026-11-02.json`:

| gap | count | worst offenders |
|---|---|---|
| Hard-coded machine paths (`C:/Users/clint`, `C:/Azazael`) | **437** | `src/CORE/PYTHON_MANAGER.py` (19), `src/META/HYDRAMETA_UV.py` (18), `src/META/HYDRAMETA.py` (12), `src/ORCHESTRATION/FusionHealer.py` (11) |
| `except …: pass` (silent failure) | **49** | `tools/mcp_eight_verify.py` (7), `src/CORE/LaneMessageBoard.py` (4), `tools/terence_invariants.py` (4) |
| Bare `except:` | **1** | `tools/cpg_joern_integration.py` |
| Unresolved first-party import | **1** | `tools/gephi_mesh_pipeline.py:123 → CORE.WORMS.NATURE_CLUSTERS` |

### The unresolved import is a silent capability loss, not a typo

`src/CORE/WORMS/` exists on this host but **`NATURE_CLUSTERS.py` does not**. So the import is
correct and its target is missing, and `tools/gephi_mesh_pipeline.py` handles that by
returning an empty dict:

```python
127:  try:
123:      from CORE.WORMS.NATURE_CLUSTERS import NATURE_DEFINITIONS
125:  except ImportError:
126:      return {}
```

The same shape repeats at line 135. The consequence is that the Gephi pipeline renders a
**graph with no nature definitions and exits successfully** — a silent loss of capability that
presents as a completed run. This is the defect class the forensics tree exists to catch
(`marker_audit`: false-OK marks), present in the tree that catches it.

**The 437 paths are the publish blocker, not the 954 MiB pack.** `tools/agent_orders_sync.py`
carries 9 of them and is the *generator* for 34 lane instruction files — so sanitising the
outputs while leaving the generator alone leaves the leak upstream of every copy.

**The forensics tree's oracles are still blind-able.** All four detectors exit **2
(ENVIRONMENT)** on this machine:

```
goal_liveness      exit=2
marker_audit       exit=2
count_derivation   exit=2
board_stale        exit=2
```

Six tests pass, but they prove the detectors cannot produce a *false green* — not that they
can see. There is no known-bad fixture a detector must fire on, which is half of RULE 0B-C.
An exit-2 on every detector is also the shape a genuinely broken locator would produce, so
"fails closed" and "cannot locate anything" are currently indistinguishable from the outside.
The next step is one positive-control fixture per detector.

## Remediation, in order

1. **ELIZA subject repoint** — `PUBLIC_MANIFEST.json` `summary` + `ship`, `pyproject.toml`
   entry points, `README.md`. Leave `never_ship`, `deny_substrings`, `rationale` byte-identical.
2. **`tools/agent_orders_sync.py` path literals** — fix the generator, then regenerate the 34
   lane files, then let `orders-in-sync` confirm. Editing the copies alone fails the gate.
3. **`src/CORE/WORMS/NATURE_CLUSTERS.py` is absent on Windows** — restore it (the Ubuntu lane
   carries a copy, `f9f12cce…`), or make `gephi_mesh_pipeline.py` fail loudly at lines 125-126
   and 135-136 instead of yielding `{}`. Silent `{}` is strictly worse than an error, because
   the pipeline reports success.
4. **Positive controls for the four detectors** — one fixture each that MUST fire, shipped with
   the tree, per RULE 0B-C.
5. **`except: pass` triage** — start with `mcp_eight_verify.py` (7), because it is a verifier and
   a swallowed exception there reports green on a server that is down.
6. Deferred: the 437 path literals outside the generator are a refactor, not a fix, and none of
   them block a per-project publish.
