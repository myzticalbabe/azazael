# Protocol detail archived out of `C:/Azazael/AGENTS.md` (2026-10-30)

Moved **verbatim** when the pushed instruction file was compressed: the
summary and the operational bottom line stay in `AGENTS.md`, the evidence
lives here. Nothing in this file is superseded by its absence above.

## ENGRAM MCP RESTART GUARD — RESOLVED: LOADED (verified Oct 09 2026)

The `engram` MCP server was added to `~/.agents/mcp.json` on 2026-10-08 21:45:52 and
could not be observed until the client restarted. **It has now been observed loaded,
so this pending check is closed — do not re-run it as a standing task.**

Evidence (all four servers answering, `C:/Azazael`, Oct 09 2026): the guard returns
`exit=0`, `verify_engram_mcp.py` prints PASS, and the client's own log records the
load — sessions `2026-10-09T15-22-17.207Z` and `2026-10-09T16-35-17.926Z` each logged
`servers: [codegraph, pams, pmb, engram]` from `C:\Users\clint\.agents\mcp.json`.
Sessions before the restart listed only three servers.

Background: `codebuff.json` was never read — it has 0 references in the client binary;
the client reads `mcp.json` from `<cwd>/.agents`, `<cwd>/../.agents`, and `~/.agents`.

The guard runs automatically at the end of step 1 (`session_start.py`), so just read
its `engram MCP guard: exit=` line. To see full detail:

```bash
python C:/Azazael/azazael/tools/verify_engram_mcp.py
```

It **validates and self-heals** `~/.agents/mcp.json` — restores the engram entry,
and recovers from the newest good backup instead of wiping the file if the JSON is
invalid (which would otherwise destroy `pams`, `pmb` and pmb's bearer token). That
runs at session start, so the config is guaranteed loadable at the **next** client
start. Every run appends a durable record, **errors included**, to
`azazael/state/engram_mcp_restart_log.jsonl`.

- **exit 0** — engram loaded; tools appear as `engram__*` and the entry is healthy.
- **exit 1** — the client has not restarted since the config changed.
- **exit 2** — something is broken: the config could not be made loadable, the
  entry will not spawn, or the guard found **no evidence at all** (no session log,
  or the newest start logged no MCP load event). Absence of evidence is never
  reported as a pass.

## OPENCODE SESSIONS — SEPARATE STATUS (updated Oct 08 2026)

The no-push analysis above is **Freebuff-specific** (`freebuff.exe`). Opencode
sessions are a different client with a plugin hook surface
(`~/.config/opencode/plugins/`, auto-loaded at startup): `tool.execute.before`
can throw and fail the intercepted tool call.

- Driving gate **code** exists: `C:/Users/clint/.config/opencode/plugins/engram.ts`
  consults `engram doctor` + `conflicts stats` and throws on a real NO-GO
  (memory tools exempt, fail-open otherwise). Unit-verified 21/21 via bun build.
- **Live refusal is now LOGGED, but never reproduced by a Freebuff session.**
  The Oct 08 proof FAILED (Engram #94: real NO-GO, 3 pending, 70s past the 60s TTL —
  probe `bash` executed anyway). Superseded Oct 09: `opencode.log` holds 30
  `engram gate REFUSING` lines in run `77d3c23f` (13:31–13:49Z) with matching
  `verdict=NO-GO` evals, including the SAME `todowrite`/`pmb_record_batch` call
  refused four times over ~47s — the shape of a hard block, not an advisory log —
  and a lesson records the first demonstrated refusal (probe-B NO-GO refused
  bash+read → judged → GO). What separates *enforced* from merely *logged*, per the
  Oct 08 failure: repeated identical refusals plus a documented resume.
  **Caveat:** this was read from the gate's own log; a Freebuff session cannot
  exercise opencode's plugin hook surface, so it is not reproduced here.
- **"Memory tools exempt" means Engram's tools only.** `ENGRAM_TOOLS` (`engram.ts:41`)
  holds the canonical `mem_*` names and `canonicalEngramToolName()` strips an
  `engram_` prefix, so `pmb_recall`/`pmb_record_batch` are NOT exempt and can be
  refused — observed doing exactly that. Engram's tools are the resolution path; that
  is why they pass, not because PMB is memory too.
- Positive load signal (added Oct 08 2026): the plugin logs
  `engram plugin loaded | gate=... | bin_ok=... | dir=...` via `client.app.log`.
  Grep `~/.local/share/opencode/log/opencode.log` for `engram plugin loaded`.
  No marker line = gate not loaded = no push, regardless of what the code says.

## ENFORCEMENT SURFACES — what can actually block (verified from source Oct 17 2026)

**The distinction that explains every "unwired rule" in canon: INJECTION IS NOT ENFORCEMENT.**
A prompt can *advise*. Only a throwing hook can *block*.

| Mechanism | Surface | Can it block? |
|---|---|---|
| `experimental.chat.system.transform` (engram.ts:1126) | injects `MEMORY_INSTRUCTIONS` + nudge into the system prompt | **No — advice** |
| `chat.message` (engram.ts:998) | inbound; calls `capturePrompt()` only | **No — capture** |
| `tool.execute.before` (engram.ts:1020) | 44 tools, throws on NO-GO | **Yes** |
| `.githooks/prepare-commit-msg` | `claim_guard.py` | **Yes** |
| `.githooks/pre-commit` | commit gates + `transcript_ap5_gate.py` (advisory, `\|\| true`) | Partly |
| **assistant output** | **NO HOOK EXISTS** | **Impossible** |

Read the whole `Hooks` interface at `@opencode-ai/plugin/dist/index.d.ts:173-284`
before claiming a hook is missing. `chat.params`, `chat.headers`, `permission.ask`,
`command.execute.before`, `shell.env`, `experimental.chat.messages.transform`,
`experimental.chat.system.transform`, `experimental.session.compacting` all exist.
**Not one receives assistant output.**

**Consequence: prose rules cannot be enforced pre-send. Enforce them downstream, on
the durable artifact.** Assistant text persists in
`~/.local/share/opencode/opencode.db` — table `part`, column `data`, role via
`message.data`. `tools/transcript_ap5_gate.py` scans it. It runs AFTER emission: it
cannot prevent, only make visible. **Never promise prevention for a rule governing
what the agent says.**

Evidence it is not theoretical: that gate returned **5 AP-5 violations in its own
author's transcript** from one session — 3 of 5 true violations (`Want me to`, `Say the
word and I'll`); bare-`let me` announcements are the false-positive class.

## VERIFICATION PROTOCOL — read before claiming anything is correct (Oct 17 2026)

Six rules, each earned by getting it wrong the same night:

1. **Establish the interpreter before the first verification.** Production is
   **3.15t** (`.venvs/py315t/Scripts/python.exe`, 3.15.0rc3, `abiflags='t'`, GIL off).
   Bare `python` is **3.14.7 GIL** — legacy. 3.14t is retired (#10, #499).
   `.githooks/pre-commit` used to invoke `python3`, which resolved to **3.13.14** from
   WindowsApps — a fourth interpreter, since pinned.

2. **Integrity is not liveness.** `PRAGMA quick_check` returning `ok` means the file is
   not corrupt, not that anything works. Measured Oct 17: all five PAMS DBs passed
   `quick_check` while `conversations` held **0 messages since 2026-05-28**,
   `tool_calls` held 19 rows, and `curated_memories.importance_level` was **uniformly 8
   across all 6,063 rows** — making `pams_search_memories(min_importance=,
   max_importance=)` inert. PAMS's own health endpoint makes this same substitution
   and still reports `healthy`.

3. **Re-derive before reporting system-wide state.** Search memory for whether it was
   already measured. On Oct 17 the PAMS conversations condition was reported as a
   fresh audit; **#380 measured it on Oct 10** with a four-phase plan attached. A
   known-unremediated gap and a new defect need different responses.

4. **Read the cited line before accepting an instrument's finding.** Six times in one
   session an instrument was right about *a* thing and wrong about *which*: a gate fired
   on its own rulebook (fenced blocks unstripped), a line-text read flagged multi-line
   calls, a script printed `0 sites` from its own filter bug. Reading the cited line
   caught every one.

5. **A truncated read is not a measurement.** Eight lines of audit output showed
   vendored paths; "all 159 findings are vendored" was unfounded and had to be re-issued
   as a filtering task.

6. **A reported verdict is not a reproduced verdict.** Kilo reported
   `0 findings on 3 parts`; reproduction gave 5 on 53–63. The wiring was correct, the
   evidence was not. **Reproduce before repeating a lane's number.**

## GATE SEMANTICS — verified from source Oct 10 2026

Read from the code, not inferred. A session that guessed at these re-ran a gate
against a stale index and read a fixed tree as failing.

**Six checks, five blocking** (`.githooks/pre-commit`): 1. bulk-diff focus
(`scripts/commit_gate.py --hook`), 2. staged anti-patterns
(`tools/staged_scanner_gate.py`), 3. canon drift (`tools/canon_drift_check.py`),
4. repo-wide ratchet (`tools/anti_pattern_gate.py --check`), 5. mesh wire-or-cut
ledger freshness (`tools/mesh_function_preflight.py --check`). The sixth (PMB
outcome observer) is deliberately **non-blocking**: its exit code is ignored, so a
memory side-effect can never reject a commit.

**An `except` handler is flagged only when its body is a SINGLE statement** — the
ExceptHandler branch early-returns on `len(body) != 1`
(`src/CORE/compliance/scanner.py:487`). A bare `pass` -> `silent_except_pass`
(`:494`); a bare `return` or a return of a Constant (None/False/0/"") ->
`except_return_default` (`:503`); a **constructed** failure value that carries the
error is NOT flagged. So the structural fix is to **record the failure as a second
statement** — body length 2 clears the finding. Suppression is the fallback, not
the fix.

**`# scanner:ignore`** is the value of `_SUPPRESSION_MARKER` (`scanner.py:197`); it
suppresses any rule on the line it sits on (`:516` compares by line number).
Findings are reported at the **statement's** line, never the `except` line, so the
marker goes on the pass/return line. Such a site is hidden from the counter but not
from the auditor — it still appears as `marker_hidden` in `SWALLOW_INVENTORY.md`.

**Severity is what makes a finding blocking**: `silent_except_pass`,
`except_return_default` and `subprocess_no_timeout` are `warning`
(`scanner.py:73`) and check 2 runs at `--severity warning`. But it fails only on a
**per-category INCREASE** against that file's HEAD version, so a legacy file full of
existing warnings still commits while a NEW one does not; new files are compared
against empty and so must be clean.

**Check 2 scans the INDEX, not the worktree** — `git show :0:<path>` vs
`HEAD:<path>` (`tools/staged_scanner_gate.py`). Editing a file without `git add`
therefore re-reports findings you already fixed. `git add` first, then re-run.

**The ratchet is `src/`-scoped** (2670 findings in 702 files, Oct 10 2026), so a
finding in `tools/*.py` is invisible to it — that asymmetry is exactly why the
per-file staged check exists.

**Bulk gate:** more than 8 staged files is blocked (`DEFAULT_MAX_FILES = 8`,
`scripts/commit_gate.py:32`), as is any tracked file changing more than 150 lines
(`COMMIT_GATE_MAX_LINES`). Newly created files are exempt from the per-file line
cap but still count toward the file tally. `ALLOW_BULK_COMMIT=1` — tested as the

## LANE EXECUTION PROTOCOL — proof, lessons, harvest, batch looping (2026-10-21)

Four behaviors that were word-of-mouth until they each caused a real miss.
Verified in live lanes (Beam #1597, GLM #1598, typecheck batches 5-10, G: re-sync).

### 1. Execution proof — a passing filter is not a passing test

- Preserve the tested command's exit status through every pipe: `set -o pipefail`
  or explicit status capture. A green `grep`/`tail` downstream of a red check is a lie.
- Reproduce at HEAD before claiming: re-run the exact check on the exact files,
  live — never cite a stale report or another lane's number.
- Smoke through the user path: import AND execute the touched behavior
  (call the fixed function, run the CLI codepath), not just the typechecker.
- Fix causes: never skip tests, weaken assertions, swallow errors, or add
  type/lint suppressions just to silence a finding — the structural fix comes
  first, suppression is the fallback, never the fix. If the requested behavior
  requires touching a check, say why and verify the behavior itself.
- Re-verify after every repair; earlier passes do not cover later edits.
  Do not repeat passes on files that have not changed.
- Content beats names: hash-compare artifacts, never trust filename/subset
  tallies (`verify_integrity` reported ALL SYNCED with G: at 370 diffs +
  286 missing — the hash diff was the real gate).

### 2. Lesson following — surface, follow, report

- Lane start: `pmb__find_lessons` (and `prepare` on the project). What surfaces
  carries `surface_id` — that id is an obligation, not a suggestion.
- After acting: `pmb__mark_lesson_followed` every time — `followed` plus a
  one-line `note`, or `applicable=false` when genuinely irrelevant. Unmarked
  lessons rot the signal that chose them.
- Never judge another lane's conflict pairs blind (13 foreign pairs left to
  their owner, Oct 21). Judge only your own: `related` unless a real
  contradiction, always with reason.

### 3. Harvest — encounter time, or it didn't happen

- Skill `azazael-bake-harvest` is correct as written — use it, don't reinvent it.
- Record errors, near-misses, and falsifications the moment they appear into
  `state/bake_harvest_<agent>_<date>.jsonl` (schema
  `{source, item_id, title, body, kind}`, `body >= 40 chars`). Session-end
  reconstruction loses detail and over-weights what is still salient.
- Validate before landing: `tools/merge_bake_lane.py --lane <file> --apply`
  must report 0 drops; commit the lane file alongside the fix.

### 4. Batch looping — fronts, queues, slices

- Mint one front task per lane (Beam #1597 / GLM #1598 shape): the title names
  the verify-target plus the ordered queue; the body pins HEAD, lists the file
  set, and carries the ERROR CAPTURE clause (TASK TEMPLATE section above).
- Each iteration: verify the front at HEAD with a live check (never the plan
  item's word) → execute the next queue item → land as explicit-pathspec slice
  commits (bulk gate: max 8 files, 150 lines/file, never `git add -A`) →
  refresh the pool report → commit the lane → record DONE.
- Close superseded queue items with proof (in-HEAD ancestry / live 0E), never
  by assertion. Other lanes' worktree edits stay unstaged and untouched.
- A fix that lands after a sync re-dirties every downstream copy: re-push the
  touched files to WSL2/Kali/G: with hash verification (Oct 21: `a459ec36`
  landed post-sync, four targets stale by one file until re-pushed).
