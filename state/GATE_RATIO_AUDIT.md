# GATE RATIO AUDIT — fail-open vs fail-closed, blocking vs advisory, default-off vs default-on, reach

Recorded 2026-10-10. Every row cites what was read. Where the source could not settle a
question the cell says `UNKNOWN` and names what would settle it — absence is never
reported as absence unless a search actually covered the tree.

**Headline ratio.** The gates that run on *every* commit are the forgiving ones: all five
blocking checks in `.githooks/pre-commit` have an explicit `-- passing loud (unrunnable)`
escape branch that turns a missing gate into a pass. The gates that are fail-closed *by
explicit design* — `type_check_gate.py`, `aggregate_suite_gate.py`,
`ci_two_interpreter_gate.py` — are precisely the ones with **no caller found in this
tree**. So the robust instruments are unreached and the reached instruments are the ones
that degrade to a pass.

---

## 1. Gate inventory

`gate | fail-mode | blocking | default | reach | evidence`

### 1a. The commit path — `.githooks/pre-commit` (6 checks; 5 blocking, 1 not)

| gate | fail-mode | blocking | default | reach | evidence |
|---|---|---|---|---|---|
| bulk-diff focus (`scripts/commit_gate.py --hook`) | **FAIL-OPEN** if `python3` is absent (`else echo "[Gate] python3 not found -- passing loud (gate unrunnable)"`) | yes (`exit 1`) | ON | commit path | `.githooks/pre-commit` Check 1 block; `DEFAULT_MAX_FILES = 8` `git rev-parse`-adjacent `scripts/commit_gate.py:32`, `ALLOW_BULK_COMMIT == "1"` `:120` |
| staged anti-pattern (`tools/staged_scanner_gate.py`) | **FAIL-OPEN** two ways: the hook prints `[Scanner] gate not found -- passing loud`; and the gate itself returns 0 when the scanner cannot be imported — `except Exception as exc: print(f"[StagedScanner] scanner unavailable ({exc}) - passing loud"); return 0` | yes (`return 1`) | ON | commit path, `tests/test_staged_scanner_gate.py` | `tools/staged_scanner_gate.py` `main()` import guard; comparison is `HEAD:<path>` vs `:0:<path>` |
| canon drift (`tools/canon_drift_check.py --check`) | hook-level **FAIL-OPEN** (`[Canon] check not found -- passing loud`). The check's own behaviour on a missing/corrupt input is **UNKNOWN** — would be settled by running it against a deliberately broken corpus | yes (`exit 1` on drift) | ON | commit path | `.githooks/pre-commit` Check 3 block (captures output first, then tests `$?` — noted in its own comment as the correct pattern) |
| repo-wide ratchet (`tools/anti_pattern_gate.py --check`) | **FAIL-CLOSED** internally: missing baseline → `raise SystemExit(2)`, unreadable → `SystemExit(2)`, foreign `identity_scheme` → `return 2`. Hook-level **FAIL-OPEN** if the script is absent | yes (`return 1` on regression) | ON | commit path | `tools/anti_pattern_gate.py` `load_baseline()`, `cmd_check()` scheme guard; `IDENTITY_SCHEME = "category-counts-v1"` |
| mesh ledger freshness (`tools/mesh_function_preflight.py --check`) | hook-level **FAIL-OPEN** (`[Mesh] check not found -- passing loud`). Internal behaviour **UNKNOWN** — not read in this pass | yes (`exit 1`) | ON | commit path | `.githooks/pre-commit` Check 5 block |
| PMB outcome observer (`tools/pmb_session_observe.py --commit-ok --quiet`) | **ADVISORY — exit code discarded by design** (`|| true`), and additionally skipped silently when `$HOME/.pmb-venv/Scripts/python.exe` is not executable | **no** | ON | commit path | `.githooks/pre-commit` Check 6 block + its comment: "a memory side-effect must never reject a commit, so its exit code is ignored" |

### 1b. Gates with no caller found

| gate | fail-mode | blocking | default | reach | evidence |
|---|---|---|---|---|---|
| `tools/type_check_gate.py` (basedpyright baseline) | **FAIL-CLOSED** in four explicit places: checker could not run (`rc == 125`) → `return 1` with "an unchecked tree must not read as a clean one"; checker emitted no JSON → `return 1`; no baseline → `return 1`; foreign identity scheme → `return 1` | yes (`return 1` on a NEW diagnostic) | — | **NOT the commit path** (the hook's six checks do not include it) and **no `.github/workflows/` found** (glob returned 0 files, scan truncated at 10000 files so absence is NOT proven). In-repo references are its own docstring, `tests/test_type_check_gate.py:31`, prose in `tools/evidence_paths.py:7` / `tools/canon_drift_check.py:25` / `tools/anti_pattern_gate.py:20,25,44`, and an **INFERRED** graph edge `tools/graph_semantic/bridge_layer.py:137` `("githooks_pre_commit", "tools_type_check_gate", "references", "INFERRED", 0.85)` — which the hook's own text contradicts | gate docstring line 65 claims `--check` is "CI + pre-commit" |
| `tools/aggregate_suite_gate.py` (aggregate/isolation suite) | **FAIL-CLOSED**: `NO_VERDICT_CODES = (124, 126)` and a killed run → `return 1` ("a killed run is not a pass"); timeout and STALL both route here | yes (`return 1` on a NEW failing id) | — | **no caller found**; only `tools/watchdog_5min.py:33` mentions it in a comment | gate docstring line 30/53 say CI uses `--profile isolation` |
| `scripts/ci_two_interpreter_gate.py` | **FAIL-CLOSED**: missing baseline → `exit 2`; a run that did not complete → `problems += "run did not complete"` → `exit 1` ("A run that never completed is a failure, never a pass") | yes (`return 1`) | — | **no caller found** in the repo | its own module docstring + exit-code contract (0/1/2) |
| `src/SCRIPTS/enforce_pre_action_gate.py` | contains a **silent-swallow fallback**: `except ImportError:` redefines `note_failure` as `pass # ledger missing; evidence-vs-silence tradeoff capped here` | yes (`exit 1` denied, `2` reverted) | **OFF** — nothing installs a caller | **UNREACHED**: its own docstring says "This script is the ONLY way file edits should be applied. Direct str_replace or write_file tool calls bypass ALL heuristic and compliance checks." Every edit made in this session went through direct `str_replace`/`write_file`, so the mandate is advisory in practice | docstring lines 5-7 and the exit-code table |
| `tools/engram_supervise.py` | machine-readable: `VERDICT: NO-GO` → `return 1`; `GO` → `return 0`; `sys.exit(main())` | yes, **but only if the caller obeys it** | ON by convention | **agent convention only** — `AGENTS.md` step 2 instructs the agent to run and obey it; no automated caller. Per `AGENTS.md`, the only machine enforcement is the opencode plugin, whose live refusal is documented as logged-but-not-reproduced in a Freebuff session | `tools/engram_supervise.py:188-195` |

### 1c. In-process gates

| gate | fail-mode | blocking | default | reach | evidence |
|---|---|---|---|---|---|
| `pre_action_gate.authorize` (EP269 task authority) | **FAIL-OPEN BY CONSTRUCTION** — docstring: "Fail-open by construction: with no table installed, or on any error, the answer is True"; code: `except Exception as exc: # noqa: BLE001 - an authority check fails OPEN` then `return True, ""` | only if a table is installed | **OFF** — `install_capabilities` (line 895) is the only way to deny; its docstring: "with none installed `authorize` allows everything, so the default gate is unchanged" | consulted in `_check_rule_0x_0y` (line 976), which every `validate_str_replace`/`validate_write_file` runs — but those are only reached if an edit routes through the gate script above, which nothing does | `src/CORE/compliance/pre_action_gate.py:944-974`, `:895-910`, `:976-989` |
| `_check_rule_0x_0y` (RULE 0X/0Y) | claims **FAIL-CLOSED**: "This is PROGRAMMATIC ENFORCEMENT: if the orchestrator is unavailable, the gate DENIES the edit. No silent passes." | yes | ON | same reach problem as above | `src/CORE/compliance/pre_action_gate.py:976-989` |
| `CORE.compliance.scanner` suppression | **finding-level weakening**: `_SUPPRESSION_MARKER = "# scanner:ignore"`, matched by LINE (`:516` compares line numbers) | suppresses the finding | ON | the scanner is invoked by the two anti-pattern gates in 1a | `src/CORE/compliance/scanner.py:197`, `:516` |
| `CORE.sentinel_enforcer` | **FAIL-CLOSED by mechanism** — installs a process-wide audit hook that denies writes; importing it also installs a deny-write hook for the whole interpreter | yes | ON *if imported* | module import; no caller verified in this pass | reported from the sibling worker's read of the module; **UNKNOWN** line evidence — would be settled by reading the module's `enforce`/`sys.addaudithook` region |

---

## 2. The set that looks like protection and provides none

Fail-open **AND** default-off **AND** unreached — the intersection:

1. **`pre_action_gate.authorize` (EP269 task authority).**
   Fail-open by its own docstring; default-off because `install_capabilities` is the only
   path to a deny and nothing calls it; unreached because the enforcement script that
   would consult it is not invoked. This is the clearest case in the tree: three
   independent properties each individually neutralise it, and the row that added it is
   recorded as "adopted-host + unwired-source" — which is accurate, and is *not* protection.

2. **`src/SCRIPTS/enforce_pre_action_gate.py`.**
   Its docstring calls itself the ONLY sanctioned edit path; nothing routes edits through
   it. It is default-off (a script), and its reach is manual invocation that does not
   happen. It also carries a silent `pass` fallback inside the enforcement path itself.

3. **`tools/engram_supervise.py` (on Freebuff).**
   Fail-open in practice: the exit code is obeyed only by agent convention, and the one
   machine-enforcing surface (the opencode plugin) is documented in `AGENTS.md` as not
   reproducible from a Freebuff session. A NO-GO here stops work only because an agent
   chose to read it.

4. **The `-- passing loud` family (5 hook checks).**
   Not default-off, but each is *conditionally* fail-open: delete or mis-name one script
   and that check silently becomes a pass. `tools/staged_scanner_gate.py` is the same
   shape one level deeper (scanner import failure → `return 0`).

**Reach summary.** Commit-path gates: 5 blocking + 1 advisory. Fail-closed-by-design
gates: 4 (`type_check_gate`, `aggregate_suite_gate`, `ci_two_interpreter_gate`,
`anti_pattern_gate` internally), of which **3 have no caller found**. Fail-open branches
on the reached path: **at least 7** (5 hook `else` branches, the scanner-import guard, the
`-x "$PMB_PY"` skip).

---

## 3. Gates whose code contradicts their docstring

**A. `.githooks/pre-commit` documents four checks, implements six.**
Header comment: "Check order (cheap-and-broad first, so a bad commit is rejected early): 1.
bulk-diff focus gate  2. staged NEW anti-pattern  3. canon drift check  4. repo-wide
anti-pattern ratchet". The body then runs Check 5 (mesh ledger freshness) and Check 6
(PMB observer) as well. Two of the six checks are undocumented in the file that runs them.

**B. `tools/type_check_gate.py` claims a reach it does not have.**
Docstring line 65: `python tools/type_check_gate.py --check      # CI + pre-commit: exit 1 on
new`. The pre-commit hook's six checks do not include it, and no CI workflow directory was
found. A gate that describes itself as wired into two paths, and is wired into neither, is
the exact class this repo's own lessons warn about.

**C. `pre_action_gate` holds two opposite stances one function apart.**
`authorize` (line 948): "Fail-open by construction ... on any error, the answer is True."
`_check_rule_0x_0y` (line 983): "This is PROGRAMMATIC ENFORCEMENT: if the orchestrator is
unavailable, the gate DENIES the edit. No silent passes." Both are true of their own code;
the fail-open one is consulted first, so the fail-closed sentence describes the second
line of defence while the first line defaults to permit.

**D. `tools/graph_semantic/bridge_layer.py:137` asserts an edge the code denies.**
`("githooks_pre_commit", "tools_type_check_gate", "references", "INFERRED", 0.85)`. The
edge is marked INFERRED, and it is wrong: the hook does not reference the type gate. A
knowledge graph that claims a gate is wired is how a future session concludes it is.

---

## 4. What would settle the UNKNOWNs

- `tools/canon_drift_check.py` fail-mode on a missing/malformed corpus — run it with the
  load path deliberately broken and read the exit code.
- `tools/mesh_function_preflight.py --check` fail-mode with the ledger absent.
- `.github/workflows/` — the glob hit the 10000-file scan limit; a bounded directory
  listing would prove whether CI exists here.
- `CORE.sentinel_enforcer`'s audit-hook lines — read the `enforce`/`addaudithook` region.
