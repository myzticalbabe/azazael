# Are we guarded against a fast orchestrator's task-handling deficiencies?

**Short answer: partly — on artifacts and concurrency, yes; on claims and on receipts, no.**
A driver that fans a task out to 20 subagents can be *stopped from corrupting the tree* and
*stopped from colliding with itself*, but it cannot currently be stopped from **asserting work it
did not do**, and that is the deficiency that matters at speed. This file says which guards exist,
which I exercised today, and what the envelope needs.

Scope: the guards in this tree, as implemented — not as promised. Anything I did not run is
marked **not exercised**, which means unknown in both directions (RULE 0B-D).

---

## 1. The eight deficiencies of a fast multi-agent driver, defined by what they break

| # | deficiency | what it breaks | concrete shape |
| --- | --- | --- | --- |
| D1 | **Unretired work** | the queue | 20 agents produce 40 units, none marked done; the backlog becomes unreviewable |
| D2 | **Claim without artefact** | trust | "tests pass", "verified", "fetched" with no command, exit code, or bytes |
| D3 | **Collision** | correctness | two agents write the same file, or the same board row, in the same minute |
| D4 | **Duplicate effort** | throughput | the same task worked twice under two ids |
| D5 | **Volume without budget** | review capacity | 200 files changed in a session that a human then cannot review |
| D6 | **Unprovable mutation** | replayability | an artefact changes and nobody can say what changed it or when |
| D7 | **Silent scope drift** | intent | a "fix the gate" task that also refactors three modules |
| D8 | **Fabricated provenance** | evidence | a quoted line presented as read when the fetch was refused |

---

## 2. Guard inventory — what exists, what it catches, and whether I ran it

| guard | where | catches | exercised 2026-11-02 | scope limit |
| --- | --- | --- | --- | --- |
| **Board claim / lease / retire** | `C:/Users/clint/_board.py` (`claim`, `done`, `block`, `release`, `stats`) | D1, D3, D4 | **yes** — `stats freebuff` returned `available 0, open 0, retired 363` | only binds agents that *use* the board; nothing forces a claim before an edit |
| **Claim is compare-and-set in a transaction** | `_board.py` (`BEGIN IMMEDIATE`, 30-min lease) | D3, D4 | **yes**, by inspection of the verbs and the canon's stated semantics | a released row returns to `available` and its `attempts` counter is erased (canon, 2026-10-31) |
| **`done` refuses an unclaimed row** | `_board.py` (`done`/`block` exit non-zero if never claimed) | D1 (fake closure) | **not exercised** this session | detects the liar only if it tries to close a row it never claimed |
| **Digest replay of a mutation log** | `Project_SHARDEX/meshscene.py --verify`, `Project_SHARDEX/ops.py` | D6 | **yes** — 4 ops, chain `69da083da4268ec8…`, final mesh `110df7ea0bb30364`, all four per-op digests reproduced | covers artefacts built through the op path; a file edited outside it is invisible |
| **Refusal codes instead of silent divergence** | same (`FLAT-FIELD`, `OP-INVALID`, `DIGEST-DIVERGENCE`, `PICK-UNPROVENANCED`, `PICK-MISMATCH`) | D2, D6 | **yes** — `PICK-UNPROVENANCED` test added and red→green | each code covers one claim; they generalise only by pattern, not by API |
| **Human-input provenance** | `picked.json` + `--verify` | D2, D8 | **yes** — click `[960,540]` → neuron 271, 18.66 px, mesh digest `5646e72adaa7eab0` re-derived | proves the *pick*; proves nothing about the operator that followed |
| **Measurement refuses a missing boundary** | `tools/prose_forensics.py --start-after/--end-before` | D2, D8 | **yes** — refused to measure when `END ` and `\r\nMenu\r\n` markers were absent | only protects texts measured with it |
| **Pre-commit: staged snapshot compliance scan** | `.githooks/pre-commit` (check 2, `tools/staged_scanner_gate.py`) | D6, partly D2 | **yes**, via `preflight_all` gate `staged-scanner`: PASS | repository-local hook; a clone can skip it |
| **Pre-commit: anti-pattern ratchet** | `.githooks/pre-commit` (check 4, `tools/anti_pattern_gate.py --check`) | D7 (in one dimension) | **yes**, via `anti-pattern-ratchet`: PASS (11.7 s) | `src/`-scoped |
| **Canon citations** | `preflight_all` gate `bible-citations` | D2, D8 for canon prose | **yes**: PASS (1.9 s) | canon only; `bible_check --check` itself not run separately |
| **Generated-block drift** | `tools/agent_orders_sync.py` + `canon-drift` / `agent-orders` gates | D7 | **yes**: both PASS | generated blocks only |
| **Claim-quality gate (dated claim without a source tier; byte figure nobody measured)** | `tools/metthew_families.py` F4/F5, wired blocking in pre-commit | **D2, D8** | **yes**: `metthew-catalogue` PASS | **one catalogue** — this is the pattern to generalise, and it is not generalised |
| **Assistant-prose gate (AP-5)** | `preflight_all` gate `transcript-ap5` | D7 in the agent's own output ("want me to" instead of acting) | **yes: FAIL** — 2 findings, both historical, in `opencode` session `ses_eb6edc411ffeehc7zu7TnY51rA`, not in this session's work; non-blocking | post-hoc over a client DB; cannot prevent, only report |
| **Startup gate (daemon, proxy, lanes, freshness)** | `tools/mcp_startup_gate.py` | D6 (stale services) | **not exercised** this session | runtime, not deliverables |
| **Board store resolution check** | `_board.py store` | D1 (wrong store = empty queue read as "no work") | **not exercised** this session | measured failure on 2026-10-31 in the Kali lane |

### Honest reading of the table

- **D6 (unprovable mutation) is genuinely covered** where the artefact is built by a verified
  path. Today's mesh work reproduces every intermediate state from the base, and the pick is
  re-derived rather than believed. That is a real guard, not a convention.
- **D1, D3, D4 are covered mechanically** by the board's transaction and lease — *if* the
  orchestrator claims first. There is no gate that refuses a file change whose task was never
  claimed, so a driver that skips the board is unguarded.
- **D2 and D8 are the open flank.** The tree has the *vocabulary* for refusing unverified claims
  (tier + retrieval state in the bible dossiers, F4/F5 in METTHEW), and it has no general
  enforcement. The pre-commit hook itself records the reason in a comment: the METTHEW rules
  "were checked only by pytest, and **a file cannot tell whether pytest ran**". That sentence is
  the deficiency in miniature.
- **D5 (volume) is not addressed at all.** There is no per-lane write budget anywhere I can find.

---

## 3. Verdict per deficiency

| deficiency | verdict | why |
| --- | --- | --- |
| D1 unretired work | **PARTIAL** | lease + `done` refusal exist; nothing forces use |
| D2 claim without artefact | **OPEN** | no receipt requirement outside one catalogue |
| D3 collision | **COVERED** (if claimed) | CAS inside `BEGIN IMMEDIATE`; one proxy-instance precedent for runtime singletons |
| D4 duplicate effort | **COVERED** (if claimed) | duplicate `task_id` retires as `duplicate of Board-<n>` |
| D5 volume budget | **OPEN** | no cap on files, claims, or spend per lane |
| D6 unprovable mutation | **COVERED** on the op path | digest replay + refusal codes |
| D7 scope drift | **PARTIAL** | ratchets and generated-block checks bite in narrow domains |
| D8 fabricated provenance | **PARTIAL** | tier discipline is enforced only where a gate names it |

---

## 4. The envelope a 20-subagent driver should be made to run inside

Six gates, cheapest first. None of them require trusting the driver.

**G1 — Claim before edit.** Every commit carries the board id it serves
(`Task: Board-<n>` trailer). A pre-push check refuses a commit whose trailer names no claimed or
retired row. Cost: one trailer. Kills D1, D3, D4 at the only chokepoint that matters — the
moment work leaves the machine.

**G2 — Receipt or retraction.** Every claim of the form "ran X", "verified Y", "tests pass" writes
a receipt: `command`, `exit_code`, `stdout_sha256`, `timestamp`, `cwd`. Ten lines. Kills D2. A
claim without a receipt is reported as *unrun*, not as *passed* — the honest default already used
by `prose_forensics.py` and by `--verify`'s refusal states.

**G3 — Provenance for quoted bytes.** A quoted line must name a file on disk plus its sha256, or
it is not quoted. This audit hit the failure itself: the earlier version of
`FRANCHISE_BIBLES_STARWARS_STARTREK.md` said no bible prose was quoted *because the fetch had
failed* — correct at the time, and it stayed correct only because the claim was written down.
Kills D8.

**G4 — Retire in the same turn.** `done` or `block` per claimed row, in the turn that closes it,
or the claim expires and the work is re-handable with `attempts+1`. Already the canon's rule; the
gap is enforcement at G1.

**G5 — Budget.** Per lane: max claims/turn, max files/turn, max bytes written. Refuse the *next*
claim rather than truncate a task in flight. Kills D5. This is the only gate with no partial
implementation anywhere in the tree.

**G6 — Scope diff.** A task declares the paths it intends to touch at claim time; the commit is
compared against that list, and an unlisted path fails unless the claim is amended (amendments
are visible, so drift is *declared* rather than silent). Kills D7.

### What this means for "DeepSeek V4.1 Flash driving 20 subagents"

The driver's speed changes one variable: **how fast wrong answers accumulate**. Every guard above
is a function of *what is written down*, not of who wrote it, which is the property that makes
them portable across models. Concretely:

- **Safe today:** parallel *artefact* production through verified paths (digest replay), board
  driven queue work (`claim → work → done`), anything where the failure is visible in a diff.
- **Not safe today:** parallel *prose* production. Twenty agents writing twenty "verified" docs
  will produce twenty confident documents and no way to tell which three are true, because D2/D8
  are open. This is exactly the shape of the work requested in this session — four documents
  across two sources — which is why the fetched bytes and the refusal states are recorded inline.
- **The single highest-value addition is G2, not more tests.** A receipt is cheap, mechanical, and
  converts "the subagent said" into "the subagent showed"; no test suite can do that from inside a
  file, as the pre-commit hook's own comment says.

---

## 5. What is *claimed* here versus what was *measured*

Measured in this session: `stats freebuff` (0 available / 363 retired); `meshscene --verify`
(4 ops replayed, chain and final digest, pick re-derived); `prose_forensics` refusing two absent
markers; the `PICK-UNPROVENANCED` and `PICK-MISMATCH` refusal paths via tests (11 pass in the
mesh suite); and the full `tools/preflight_all.py` run that this commit's hook performs --
**24 of 25 gates PASS** (`changeset-focus`, `stale-index-guard`, `staged-scanner`, `canon-drift`,
`anti-pattern-ratchet`, `unresolved-refs-ratchet`, `mesh-ledger-freshness`, `wire-evidence`,
`testing-paradigm-*`, `agent-orders`, `supervisor-verdict`, `bible-citations`, `platform-claims`,
`pmb-outcome-observer`, `failure-evidence-ratchet`, `evidence-gate`, `metthew-catalogue`,
`at-risk-register`, `task-shape`, both the flaming-sword gates), **1 FAIL**: `transcript-ap5`,
which scans persisted assistant prose and found two "Want me to …" lines in another session's
stored transcript. It is non-blocking and it is a real finding about framing, not about this
change; it is left visible rather than suppressed.

Still not exercised, so still **unknown** in both directions: `bible_check --check` on its own,
the startup gate (`mcp_startup_gate.py`), and `_board.py store` (the split-brain detector). This
file does not upgrade a guard it did not run.
