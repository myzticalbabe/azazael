# FULL MAPPING AUDIT — 3.15t production, 2026-10-09

Question this answers: *what is mapped to what, and which parts of that map do we
actually have evidence for?* Every row carries either a command whose output is
quoted in this session or the marker **ASSERTED** (a claim from a document, not
measured here). Rows nobody could verify are listed in §7 rather than smoothed
over.

---

## 1. Interpreter map — what exists, and what production is

| Interpreter | Path | Version | Role now |
|---|---|---|---|
| **py315t (production)** | `C:\Azazael\.venvs\py315t\Scripts\python.exe` | 3.15.0rc3, free-threaded, `gil_enabled=False` | **the only production target** |
| system 3.15t | `...\Programs\Python\Python315\python3.15t.exe` | 3.15.0rc3 | fallback rung in launcher ladders |
| system 3.15 GIL | `...\Python315\python.exe` | 3.15 | venv base; not a run target |
| Python 3.14 | `...\Python314\python.exe` | 3.14.7 | **legacy base install** — exists, but is not a run target; `codegraph` still names it (open, §7) |
| **py314m (fallback)** | `C:\Azazael\.venvs\py314m\Scripts\python.exe` | 3.14.5 GIL | the **only sanctioned 3.14** runtime, for a package with no 3.15 build |
| py315 / build315t venvs | `C:\Azazael\.venvs\{py315,build315t}` | 3.15 | build/env support, not run targets |
| `.pmb-venv`, `venv-314t`, `venv-313-tools`, `venv-interpreter` | outside repo | mixed | **outside this audit** — `venv-314t` is RETIRED (2026-10-19, archived); PMB ships its own venv |

## 2. Consumer map — who chooses which interpreter (all verified)

| Consumer | Interpreter | How it is decided | Evidence |
|---|---|---|---|
| MCP `pams` | py315t | literal path in `~/.agents/mcp.json` | file re-parses; `pams` → py315t |
| MCP `codegraph` | **Python314** | literal path in `~/.agents/mcp.json` | **not yet repointed** (see §7) |
| MCP `engram` | `engram.exe` | native binary | n/a |
| MCP `pmb` | **none — client-side** | entry is `type: http` → `http://127.0.0.1:8765/mcp` with a bearer header. **No command and no interpreter**, so there is nothing to repoint at the client layer; whichever interpreter serves it belongs to the daemon, not the client | `mcp.json` keys for `pmb` are `headers, type, url` only |
| chain controller (22 jobs) | py315t | `_python()` = `AZAZAEL_PYTHON` or `sys.executable`; `run_chain_live.bat` sets `PY` | dry-run showed all four sampled jobs resolving to py315t |
| evolution cycle (`run_evolution_cycle_*.bat`) | py315t | launcher literal (was `python3.14t.exe` + a `py314t_site` PYTHONPATH) | repointed; the cp314t site dir was removed, not carried over |
| AOA / Lilith wallboards, `refresh_oa_data.bat` | py315t | launcher ladder | ladder rebuilt: py315t → system 3.15t → PATH |
| `config/config.yaml` `free_threading.python_path` | py315t | config literal | repointed |
| Everything launched by `chain_controller` jobs | py315t | inherits the controller | 22/22 jobs |
| The Freebuff/opencode clients themselves | own runtime | not controllable here | n/a |

**The load-bearing consequence:** because `chain_controller._python()` reads
`sys.executable`, one line in `run_chain_live.bat` decides the interpreter for
all 22 jobs, including the `meta` (meta-evolution) and `render` (ouroboros) hops.
There is exactly one place to get right, and it is now right.

## 3. Subsystem map — size vs dependency health

**1417** active `.py` files, measured by `find` excluding `archive/`, `archived/`,
`archived_unified/`, `nuitka_build_backup/` and `.build/`.

> **Denominator warning.** `state/dep_gap_315t.json` records `files_scanned: 1368`.
> That walk used a *different, narrower* exclusion set than the `find` above, so
> 1368 and 1417 are not interchangeable: a module "missing" against one
> denominator is not missing against the other. Quote the denominator with the
> number, or the count means nothing.
>
> An earlier draft of this section said 1345. That number was not reproducible.

| Subsystem | .py | Dep status on 3.15t |
|---|---|---|
| `src/CORE` | 291 | healthy; `local_memory` + `direct_memory` import and **write live** |
| `tests` | 269 | collects (4047 tests total incl. src/tests); full run in flight |
| `scripts` | 213 | chain + evolution + monitors verified runnable |
| `tools` | 181 | renderers/instruments verified runnable |
| `src/CODEX` | 87 | needs `pygame` (blocked), `moviepy` (absent) |
| `src/ORCHESTRATION` | 84 | needs `onnx`/`onnxruntime`/`tensorflow`/`jax`/`ray` (all blocked or absent) |
| `src/AOA` | 30 | verified runnable (`refresh_oa_data --check` rc=0) |
| `src/META`, `src/HYDRA`, `src/UTILITIES` | 16 / 11 / 23 | partly guarded imports |
| `src/eve_unleashed` | 11 | needs `onnxruntime` + `llama_cpp` (both blocked) |

## 4. Technique map — harvested steals → code

Corpus size, from `state/SOTA_TECHNIQUE_CODEBASE_MAP.md` (read this session):
**141 distinct episode codes** (168 note rows deduped by code), mapped by 8 workers
against a module inventory and then re-checked by 4 more. Verdict totals:
**PRESENT 1 · PARTIAL 121 · ABSENT 19 · total 141**. The first pass produced
PRESENT 1 · PARTIAL 101 · ABSENT 39; the re-check moved **20 ABSENT rows to
PARTIAL** by finding live modules the first inventory omitted. Both passes are
recorded in that file because the movement is itself the finding.

**Correction.** An earlier draft of this section called the corpus "199 harvested
steals". **199 is a real, sourced number — but it is a different quantity.**
`SOTA_STEAL_AUDIT.md` §7.1 records the Engram `sota-steal/*` store at
**40 + 159 = 199 records**, verified live against `~/.engram/engram.db`. So:

| Figure | Means | Source |
|---|---|---|
| **199** | records **in the Engram memory store** | `SOTA_STEAL_AUDIT.md` §7.1, verified against `engram.db` |
| **168** | deduped technique note rows (159 distinct `topic_key`; 9 verbatim pairs collapse) | §7.1 |
| **141** | distinct papers/episode codes mapped to code | `SOTA_TECHNIQUE_CODEBASE_MAP.md` |
| **114** | distinct papers the 141 rows first covered — the 27-row duplication masked 27 papers with no note; §7.7 fixed coverage to 141/141 | §7.7 |
| **33** | algorithms audited in `SOTA_STEAL_AUDIT.md` §1–6 (27 ADD-new, 6 EXTEND-existing), batches 01–04 | §6 verdict line |
| **18** | episode codes where both entries persist (title-only difference ⇒ different slugs ⇒ different `topic_key`) | §7.8 |

The draft's other error stands uncorrected-by-accident: it wrote "PARTIAL=121/139",
and 139 is not a total anywhere. The verified verdict totals are the ones above
in this section (121 of 141). Carrying a store-record count and a paper count in
one sentence is how these figures get swapped — keep them in the table.

| Layer (blueprint) | Implementation | Status |
|---|---|---|
| L7 interfaces | `src/CORE/structured_action.py`, `latent_align.py`, `latent_refine.py` | exercise scripts exit 0, `chain: true` |
| L5 dispatch | `src/CORE/dispatch_plan.py` | `exercise_p2b_dispatch` + `_slice2` exit 0 |
| L6 evolution | `src/CORE/rubric_evolution.py` | `exercise_p2c_rubric` exit 0 |
| L2 skills | `src/CORE/skill_library.py` | present; no dedicated exercise yet — **ASSERTED working** |
| L1/L3 | `src/CORE/verification_gate.py` | present; now has `z3` installed for the SMT path |
| Real gaps (unimplemented) | **19** episode codes | `SOTA_TECHNIQUE_CODEBASE_MAP.md` — ABSENT after the re-check, each row naming its nearest module and what is missing |
| Duplicate records | 18 papers stored twice | `SOTA_STEAL_AUDIT.md` §7.8 — open decision |

All six incorporation modules import **stdlib only** (`typing`, `math`), which is
why they ran on 3.15t without any new dependency — the dependency risk sits in
the *subsystems they will be wired into*, not in the modules themselves.

## 5. Meta-evolution (ouroboros) hop map

| # | Hop | Implementation | Verified |
|---|---|---|---|
| 1 | search → measurement | `evolution_cycle.py` → `logs/evolution_cycle.log` | **run this session**; 0-byte log became 29 lines |
| 2 | instruments | `tools/evolution_progress.py`, `tools/fitness_arm_liveness.py` | **run this session**; produced `loop_integrity.json` + `fitness_arms.json` (were absent → `NO_DATA`) |
| 3 | closing arrow | `evolution_cycle.py::_loop_integrity_gate()` | **INERT** — logs `absent -- BLIND ... not blocking`, returns `(True, None)` |
| 4 | readout | `tools/render_all_monitors.py` → `render_ouroboros.py` → `dashboard/ouroboros.html` | **run this session on py315t**, 88,277 bytes |
| 5 | scheduling | `chain_controller.py` job table | **BROKEN** — `--status` reports the `Azazael-Chain` task `"Disabled"` |
| 6 | interpreter | `run_chain_live.bat` | **FIXED** this session (was 3.14t/Python314) |

Hops 5→1 is the arrow that makes it an ouroboros, and it is the one that is off:
the task is disabled, so nothing fires the producer, so the instruments stay
empty, so the closing arrow stays blind.

## 6. Verification status (measured, this session)

| Check | Result |
|---|---|
| `pytest --co` on 3.15t | 4047 collected |
| full suite on 3.15t | **IN FLIGHT — 36% at last check** (PIDs 17224/2688 alive). **2 failures** so far (one near 21%, one near 33%). Identities are **unavailable until the run ends**, because pytest prints its failure list only at completion — so they are untriaged. This row is *not* a pass |
| LocalMemoryStore live write | PASS (row 2201713, delta +1, read back) |
| DirectMemory live write | PASS (row 2201715, FTS in sync) |
| 6 incorporation exercises | PASS, all exit 0 |
| audit append under 4 processes | PASS atomic 1000/1000 chained; buffered control FAILS (negative control holds) |
| `test_daemon_health.py` | PASS 48, skipped 3 (collection was broken before this session) |
| dep gap on 3.15t | 40 module-level misses, 95 optional-absent, 20 present |
| technique dep install | 12 installed, 5 blocked-no-wheel, 1 failed |
| `verify_audit_chain` on the live sidecar | **FAIL** — 2 orphan fragments at lines 42/110 (T-8) |

## 7. Known-unmapped / unresolved (not hidden)

1. **`codegraph` still runs on Python314 — now REFUSED WITH EVIDENCE, not
   deferred on principle.** The migration was attempted and fails for a reason that
   is not codegraph's fault:

   ```
   TypeError: issubclass() arg 1 must be a class
     File "...\py315t\Lib\site-packages\mcp\server\fastmcp\tools\base.py", line 67, in from_function
       if issubclass(param.annotation, Context):
   ```

   raised from `codegraph_mcp.py:214 @mcp.tool()`. The installed `mcp` package in
   py315t is not compatible with 3.15's annotation handling, so `param.annotation`
   comes back as a non-class and `issubclass()` raises. The **same file works on
   Python314** (`--help` prints usage, exit 0). Keeping the legacy entry is therefore
   the correct call: a broken MCP server is worse than a legacy one, and this is now
   measured rather than presumed. Revisit only when py315t's `mcp` is upgraded.

   **Corrected:** an earlier draft listed `pmb` here too. `pmb` is an HTTP-transport
   entry with no interpreter at all (see §2), so it was never a repoint candidate.

   **Follow-on risk checked and cleared.** The same `mcp` package is why this needed
   verifying: `pams` was repointed to py315t, and if it used the fastmcp decorator it
   would have hit the identical TypeError. It does not — the launcher goes through
   `from persistent_ai_memory import mcp_server` and the live run logs
   `mcp.server.lowlevel.server: Initializing server 'ai-memory'` followed by
   `Registering handler for ListToolsRequest` / `CallToolRequest`, i.e. the low-level
   API with its handlers registering cleanly under 3.15. An incidental warning was
   observed and is **not** attributed to the interpreter change:
   `Failed to start HTTP server: API Key could not be loaded from keys/mcpo_api_key.txt`.
   The stdio transport the client actually uses came up.

2. **The measured accelerator verdict is in `TODO_315T_BUILD.md` §5.6**, not here:
   on this hardware the Arc iGPU **loses** to the 16-thread CPU (prefill 22.84 vs
   58.01 tok/s; decode 21.05 vs 27.56). Any future "use the GPU for speed" claim must
   cite `state/accelerator_bench.jsonl` or it does not exist.

3. **Still open from the 11-item batch:** T-5 (one shared evolution-log parser for the
   four current consumers), the 18 duplicate SOTA records, and triage of the py315t
   suite failures — the suite was still running at 82% when this was written, and
   pytest prints failure identities only at completion. Reported as unfinished rather
   than as passed.
2. **The full suite has not finished**, so "all functions/tools test on 3.15t"
   is *in progress*, not complete. The two failures seen so far are untriaged.
3. **`.pams` store vs `G:\source-of-truth\persistent-ai-memory`**: the cold-backup
   mirror claim is from the forensic report — **ASSERTED**, not re-verified here.
4. **Intel Arc GPU**: no path is verified working; see `TODO_315T_BUILD.md` §0.
5. **`nuitka_build_backup/` and `archived/`** contain vendored third-party trees
   that are excluded from every count in this audit; they are not "our" code and
   mapping them would inflate the inventory.
6. **Upstream `docs/`, `dashboard/`, `config/`** were not opened for this audit;
   the map covers code, not prose.
