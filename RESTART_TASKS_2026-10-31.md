# Restart task list — 2026-10-31

Every item below is a **measured** failure or unknown, not a suspicion. Each was
also posted to the board (`memorybus_queue`, lane `kilo`, read back as
`status=pending`) and recorded in PMB + Engram + supervisor.

Board rows: **46818–46825** (verify: `python C:/Users/clint/_board.py tasks kilo 46817`).

> **This file is not the task queue. `RESTART_TASKS_INDEX.md` is the index, and the board
> is the body.** Generated 2026-11-01 by `tools/restart_tasks_index.py`: 16 EV entries,
> 29 board rows, 0 dangling ids. Each row's authoritative text is
> `memorybus_queue.content.detail`; this file keeps only what a queue row cannot carry —
> the measurement, the refutation, and the correction. **All 29 rows were still
> `status=pending`** at index time, so nothing below has been done: it is a record of
> measurement, not a list of work in flight. Task text deleted here is not lost, it is
> the row's own `detail` field; if you edit a task, edit the row.

---

## Landed and verified today (context for the rest)

| change | evidence |
|---|---|
| `SecretRotator.rotate_secret` rewritten | it returned `success: True` while writing no credential; now backs up, writes atomically, reads the value back, and derives `success` from that read. 7 tests in `tests/test_secret_rotation.py`. Unknown key refused (`unknown_secret`), same-value refused. |
| `tools/rotate_secret.py` | operator CLI (`status` / `rotate --dry-run`); the schedule-safe half reads the audit trail and never mutates a credential. |
| `tools/evidence_gate.py` + `state/evidence_gate_baseline.json` | six AST/live checks, exit 1 on NEW debt, UNVERIFIED is never a pass. Wired into `.githooks/pre-commit` (Check 6b) and `tools/preflight_all.py` registry. 15 negative-control tests. |
| order-dependent test fixed | `tests/test_memory_dir_caching.py` skipped any module not yet imported, so it passed alone and failed in a subset. Now static-when-unimported; also its scanner followed only one helper hop and missed `TELEMETRY_DB_PATH` (env-derived via `_get_telemetry_db_dir` → `_get_db_dir`). Subset that failed: **378 passed, 0 failed**. |
| `xenomorph:ChestbursterWorm.burst` false resurrection | caused by a local named `burst` in `src/CORE/recorder_guard.py` I wrote on 10-29; renamed `burst_rows`. Mesh test row cleared. |
| 5 stale store copies | 3.17 GB archived to `G:/STALE_MEMORY_COPIES_2026-10-31`, each extracted and row-count-verified before deletion. |
| `opencode.db` | 2.45 GB archived to `G:/OPENCODE_ARCHIVE_2026-10-31` (1.50 GB gz, 226 825 rows across 29 tables MATCH from the extracted copy), then cleared. First attempt reported MISMATCH and was right to: a read-only open cannot replay the 15 MB WAL, so it counted a pre-migration 16-table schema. Checkpoint first, then archive. |
| `semantic_index.jsonl` | 1.68 GB → 442 MB, 0 duplicates, 71 765 embeddings repacked base64 float32; reader accepts both encodings; growth cap + `compact` + `--rebuild` added. |
| mesh ledger refreshed | `NEURAL_MESH_WIRE_OR_CUT.json` regenerated via the probe; `rotate_secret` moved `dispatched → wired` with its justification updated. `--check` now reports **fresh**. |

---

## TASKS — all measured 2026-10-30

### EV-001 — PF16 reachability must be module-linked, then 134 rows re-disposed
**Failing:** `tests/test_mesh_wire_or_cut.py::test_dispatched_is_not_a_way_to_hide_a_static_caller`
→ `config:FeatureFlagCtrl.is_enabled`, matched by Selenium's `WebElement.is_enabled()`
in `scripts/ddap_portal_selenium.py` — no import of the defining module.

The probe already knows this rule (`_module_qualified_hit`,
`tools/mesh_function_preflight.py:363`; its docstring cites the same incident).
Its **core** `build()` / `_reference_index()` path still counts bare tokens.

**Plan:** filter bare-name evidence through the import link in `build()`; run
`--verdict --propose`; re-dispose the rows that flip from `wired` to carried
(`dispatched` where `string_references()` has the name, `accepted_gap` with a
stated measurement otherwise); confirm the mesh test and
`evidence_gate --only wired_claims` are both green.
**Blast radius:** 206 token-only functions; 135 wired rows; 3 module-linked.

### EV-002 — 135 `wired` rows have no module-linked caller
`evidence_gate --only wired_claims` → **3/138** linked. The ledger's own
`carry_evidence` shows why: `__init__` matched in 25 files, `execute` in 117.
Same class as Error #472/#682/#719. Baselined so it cannot grow; task is to
shrink it to 0.

### EV-003 — 37 dead controls
Control-named functions with no module-linked caller outside tests, e.g.
`STRIDE_VERIFIER_WORM.py:258 verify_policy`,
`expansion/backup.py:225 restore_checkpoint`,
`audit_trail.py:1625 verify_citation_exists`.
Note the rule bought today: **do not wire a control that reports success without
proving the effect** — that is what `rotate_secret` did.

### EV-004 — `memory_store.db` at 1835 MB against a 500 MB configured quota
600 080 rows, 3.7× `DB_SIZE_QUOTA_MB`. Retention's caller
(`get_memory_store` → `enforce_*`, once per process, over quota) is incremental,
not a purge. Decide deliberately: prune by type caps, archive-then-vacuum, or
raise the configured quota. The gate accepts 1900 MB as a ceiling — visibility,
not a fix.

### EV-005 — rotation UNVERIFIED (0 rotations recorded)
The capability is real and tested; nothing has been rotated. `--dry-run` first.
No key was rotated here because rotating a live provider key without updating the
provider is an outage, not a hardening.

### EV-006 — two gates are BLIND
`two-interpreter-suite` (`logs/ci_two_interpreter_gate_baseline.json` absent) and
`aggregate-suite-isolation` (`logs/aggregate_suite_baseline.json` absent).
A gate that cannot judge is not a pass; preflight reports BLIND on purpose.
Record one baseline each, then confirm the self-test line flips to OK.

### EV-007 — semantic index under cap on the next full re-index
Run one `python semantic.py index --all` and confirm it stays below
`SEMANTIC_INDEX_MAX_MB` (512). The compaction path is exercised; a full re-index
is not.

### EV-008 — AP-5 finds one historical request in archived prose
Scanning the restored store reports 1 finding, from a session that predates this
work: `ses_eb6edc41…` msg `msg_14a54cfe…` line 45, "Want me to mint the two
scope/re-derivation gates…". Written before the mandate; the gate runs after
emission by design, so it can only surface it. Task: baseline findings older
than a cutoff so the gate distinguishes new prose from archived prose.

**Correction to my own space reclaim:** archiving and clearing `opencode.db`
made this gate report `STORE ABSENT -- nothing was scanned`. I restored the
archive to the live path in the same session — blinding an audit gate to save
2.45 GB is the wrong trade, and "nothing was scanned" is not a clean result.
Net reclaim after the restore is 3.17 GB (stale copies) + 1.24 GB (index).

---

## EV-009 — batch-loop queue protocol (built and verified this session)

The board could not be driven as a queue. Measured 2026-10-31: **743 open rows**
on the three lane topics, oldest nine days old, `mcp_config_fix` posted **75
times**, and **no record anywhere of a row having been picked up** — `status`
lives inside each row's JSON, so every poller re-read its whole backlog every
pass. A "batch loop" built on that board gets slower per iteration.

Built and tested this session:

- `LaneMessageBoard.claim_tasks(lane, limit, agent)` — compare-and-set inside
  `BEGIN IMMEDIATE`, oldest first, 30-minute lease (`CLAIM_LEASE_SECONDS`), so
  an abandoned claim is reclaimed instead of stranding work.
- `complete_task(id, state='done'|'blocked', note)` — retires; returns **False**
  when the id was never claimed, so "could not retire" cannot read as success.
- `release_task(id)` — hand work back unretired (a lane that claimed work it
  cannot do must not hold it until the lease); refuses to resurrect retired rows.
- `archive_backlog(before_iso, lane, dry_run, dump_path)` — retires pre-cutover
  rows **without deleting them**, writing a TSV audit copy first.
- Duplicate collapse: a `task_id` already retired, live elsewhere, or already
  handed out earlier in the batch is retired as `duplicate of Board-<n>` instead
  of becoming separate work.
- CLI: `_board.py claim | done | block | release | stats | archive-backlog`.
- `docs/agent_orders/03_lane_queue.md` — one source, generated into **all seven**
  lane instruction files by `agent_orders_sync.py` (`--check`: 17 targets in
  sync, 0 problems). opencode is named the push hook / dispatcher.
- `tests/test_lane_task_queue.py` — 11 tests, all passing.

### Measured run, so the claim is not taken on trust

```
before: {'open': 743}
after archive-backlog all 2026-10-31: {'blocked': 728, 'open': 15}
  opencode 96, kilo 310, freebuff 322  -> C:/Users/clint/_board_backlog_archive_2026-10-31.tsv (729 lines)
final:  {'blocked': 729, 'done': 1, 'open': 14}
```

**The speed claim, stated honestly:** `claim` costs **13.2 ms** against the
reader's **1.0 ms** per call — the queue verbs do **not** make an individual
call faster. The gain is that retired rows stop being returned (the loop
terminates and stops re-processing), duplicates collapse before they reach a
batch, and each claim is bounded so no lane is handed 300 rows. Reporting this
as a throughput win would be the same error as calling a ledger "wired" without
a caller.

Tasked for restart: the 14 open rows are today's real work; the 729 archived
rows remain inspectable in the dump and in `memorybus_queue` (nothing deleted).

### EV-010 — 33 control-named functions have no caller (tasked, not bulk-wired)

`evidence_gate.py dead_control` now separates **exported-but-uncalled** (3: their
caller is outside this repo — `backup.verify_backup_integrity`,
`backup.restore_backup`, `cd3_exporter.purge_old_spans`) from genuinely
unreachable (**33**). Wiring 33 controls into live paths immediately before a
restart is the change most likely to break the restart, so each is task-ledgered
in `NEURAL_MESH_WIRE_OR_CUT.json` disposition terms and must be **wire | delete |
public-api** on evidence. Highest-value first:

- `sentinel_gate.validate_rule_0r` — **fixed this session**: it existed with a
  real FALSE-PASS path and was never dispatched, so RULE 0R was skipped by every
  gate run. Now dispatched, parsed from `RULE 0R (Sync):`, and its negative
  control fires (`FALSE PASS - sync claimed without audit citation`).
- `compliance/policy.enforce_gate` — the RULE 0X-2 runtime broker decorator is
  applied to nothing, so no write path is intercepted.
- `secrets_manager.audit_secrets` — the secret audit never runs anywhere.
- `DirectMemory.validate_event_type` / `purge_session`, `SessionMemory.validate_lesson`,
  `MathCertainty.MerkleTree.verify_proof` — validation and retention paths that
  nothing calls.

The gate fails on any **new** unreachable control, so this list cannot grow
silently. It is in the 33-row baseline until each row is disposed.

---

## EV-011 — domain trees (built; 8 of them measured, renders tasked)

The per-environment atlas answers "what is in this directory". The questions
asked on 2026-10-31 were domain questions — a tree for the RULES layer, CAIN,
EVE/RANI artifacts, swarm hives, GOSP, ML shards/modules, the shard repository,
edge0 — and those span roots, or live outside the repo, or are half canon.

`tools/domain_trees.py` makes a domain a **declaration**: named roots, named
single files, named canon documents, optional skill roots and evidence dirs. It
emits `~/yggdrasil_forest/domain_atlas_<domain>.json` in the SAME schema as the
environment atlases plus `forest_manifest.json` with one render descriptor per
domain, so `render_tree.py` draws any domain with **no code change**. That is the
interop contract, and it is stated in the instruction block.

Measured 2026-10-31 (`--check`, 0 missing paths):

| domain | trees | modules | lines | classes | worms | rules |
| --- | --- | --- | --- | --- | --- | --- |
| sentinel | 12 | 50 | 39 600 | 42 | 0 | 66 |
| cain | 8 | 94 | 37 635 | 43 | 0 | 0 |
| eve_rani | 2 | 22 | 5 936 | 55 | 0 | 0 |
| hives | 2 | 151 | 74 752 | 417 | 206 | 0 |
| gosp | 5 | 3 | 357 | 1 | 0 | 0 |
| ml | 2 | 50 | 17 470 | 104 | 0 | 0 |
| shards | 2 | 4 | 1 125 | 0 | 0 | 0 (204 skill shard dirs + 37 loose md) |
| edge0 | 5 | 161 | 30 802 | 142 | 0 | 0 |

Renderer interop proven: `render_tree.py --descriptor descriptor_sentinel.json`
produced **300/300 frames, 0 misses**. Two defects were found by looking at the
rendered still rather than the code: six `file.*` labels overlapped into an
unreadable run, and the canon limbs read `0 cls` because a rule file has no
classes. Both fixed in the emitter (`kind: file|canon|shards|evidence`, bare
stems), not in the renderer.

**The gap this does not close, and says so:** each declared root is scanned on its
owner, so `edges.tree_pairs` is a **sum of per-root values** and undercounts
coupling between roots of one domain. Every atlas carries
`cross_root_edges_resolved: false`. Tasked as DT-EDGE-RESOLVE.

### Queued for after startup — 16 rows, bodies on the board

Rows and purposes: `RESTART_TASKS_INDEX.md` → EV-011. Ids, for a reader who got here
first: 46829 (DT-FK1), 46830 (DT-FK2), 46831 (DT-FK3), 46832 (DT-TREE-SENTINEL),
46833 (DT-TREE-CAIN), 46834 (DT-TREE-EVE-RANI), 46835 (DT-TREE-HIVES), 46836
(DT-TREE-GOSP), 46837 (DT-TREE-ML), 46838 (DT-TREE-SHARDS), 46839 (DT-TREE-EDGE0),
46840 (DT-EDGE-RESOLVE), 46841 (DT-MANDATE-0D), 46842 (DT-MANDATE-0G), 46843
(DT-MANDATE-0ZA), 46844 (DT-MANDATE-PROVENANCE). The per-row "purpose" column that
used to sit here was a second copy of each row's `detail` field, and a copy that does
not change when the row does — which is exactly how a task list starts lying.

### EV-012 — two inference mandates do not match the code (measured 2026-10-31, tasked)

User directive: "the gemini and inferencing mandates will have to be rereview during
dev". Measured before tasking, so the re-review starts from facts rather than
taste:

```
CORE.inference.providers.PROVIDER_REGISTRY -> 31 declared, 27 configured
   unconfigured: cohere_native, gemini_native, huggingface_native, mistral_fim_native
```

- **RULE 0D** names a **10-provider** chain (Groq → OpenRouter → NIM → Mistral →
  GitHub → HuggingFace → Cloudflare → SiliconFlow → Zhipu → Cohere) and elsewhere
  in the same file says "12-provider". Both are smaller than the registry by
  20+ providers, so the mandate describes an ordering the code does not follow.
- **RULE 0G** requires `thinker-with-files-gemini` at every major phase. The name
  exists only in `.agents/skills` (8 files) and canon — **there is no spawner in
  `azazael/tools`**, so no lane can execute it. SOP already carries the escape
  hatch ("If agent UNAVAILABLE per pre-check: N/A"); the mandate itself does not.
  A mandate that cannot be executed in the lane reading it is a mandate that
  trains agents to fake compliance.
- **RULE 0Z-A / azazael-6api-analysis** says "all" APIs; the reachable set is the
  27 configured providers, not 6.

Not edited now: a canon rewrite needs the decision about whether canon states a
chain or a registry walk, and that is the re-review. Recorded so the numbers are
not re-derived from memory.

### EV-012a — these are DEFENCES, not generic policy (user, 2026-10-31)

> "some were deepseek v4 pro specific for defensive programming against the agent"

This changes the shape of the re-review. Several clauses exist to stop a specific
agent behaviour — substituting its own analysis for a delegated second opinion,
self-approving its own change, silently skipping the phase check. Deleting
"spawn X" because no spawner exists removes the defence and keeps the hole.

Measured, so the re-review is not guessing about what is reachable:

- `spawn_agents` has **no implementation anywhere in the repo**. The only
  occurrences are a docstring (`src/SCRIPTS/sentinel_gate.py:27`) and a PolicyRule
  (`src/CORE/compliance/policy.py:548`).
- The ten agents RULE 0Z names (thinker-gpt, thinker-with-files-gemini,
  code-reviewer-deepseek, file-picker, code-searcher, researcher-web,
  researcher-docs, basher, browser-use, tmux-cli) are **Codebuff-client names**,
  not repo code. RULE 0G, 0V and 0Z therefore cannot be executed by any lane from
  this repo — only asserted, which is how they decayed into recitation.
- **SOP.md already has the correct escape hatch** (lines 14-26, AVAILABILITY
  PRE-CHECK): an UNAVAILABLE agent converts only the checks that DEPEND on it from
  HALT to N/A, while AP-1, RULE 0H, 0I, 0L-local, 0U, 0W and the 0B-E claim guard
  stay HALT-grade. **MANDATES.md — the canonical copy — lacks it.** The two files
  disagreeing is the defect, and the fix is to pull SOP's wording up, not to invent
  a third.

A clause may be restated only after naming (a) the failure it defends against and
(b) a mechanism that exists in the lane. The honest equivalent where no spawner is
present is an independent second opinion through `CORE.inference.providers` using a
different provider **and** a different model family from the author, with the
verdict recorded — not the agent reviewing its own work.

Provenance is per-clause and must be recorded as `unrecorded` where no source
attribute exists. I am not going to invent which clause came from which model.

---

## Verification state at handoff

```
python tools/evidence_gate.py                 -> 5 checks, 0 new offenders
    ast_parse_coverage  pass  1688/1688 files parse
    dead_control        pass  33 unreachable (0 new), 3 exported-but-uncalled
    wired_claims        pass  3/4 module-linked, 1 token-only (0 new)
    ledger_freshness    pass  fresh
    store_growth        pass  196 MB / 35526 rows (cap 1900 MB)
python tools/agent_orders_sync.py --check     -> 24 target(s) in sync, 0 problem(s)
python tools/domain_trees.py --check          -> 8 domains, 0 missing paths
    sentinel 12 limbs/66 rules · cain 8 · eve_rani 2 · hives 2/206 worms
    gosp 5 · ml 2 · shards 2 (204 skill shard dirs) · edge0 5
render_tree --descriptor descriptor_sentinel.json -> 300/300 frames, 0 misses
board: 26 open (14 prior + 12 queued DT-*)
python -m pytest tests/test_lane_task_queue.py -> 11 passed
python tools/mcp_startup_gate.py              -> BLOCKED=2 PASS=6 in 1.0s
    PASS lane-config, orders-in-sync, lane-context, pmb-daemon, floor-proxy, proxy-singleton
    BLOCKED supervisor-fresh (2 procs predate the edit) + pams-running -> both clear on client restart
python -m pytest tests/test_evidence_gate.py  -> 15 passed
python -m pytest tests/test_secret_rotation.py-> 7 passed
python -m pytest tests/test_anti_pattern_gate.py -> 18 passed
python -m pytest -k "memory or record or retention" -> 378 passed
python tools/mesh_function_preflight.py --check -> ledger fresh
python tools/preflight_all.py --self-test --run-controls -> 1 failure (EV-001), 2 blind (EV-006)
python tools/preflight_all.py --check -> 14 ran, 1 failed (0 blocking): transcript-ap5 (EV-008)
```

`ALLOW_EVIDENCE_GATE=1` overrides the new hook check, declared, never silent.

---

## EV-014 — the WSL lanes were starting with NO standing orders (found and fixed 2026-10-31)

Found while double-checking every lane's instructions for the restart. Measured,
not assumed:

```
Ubuntu-26.04  /root/AGENTS.md                        2003 bytes   0 AO blocks
kali-linux    /root/BCC-REINVESTIGATION/AGENTS.md   14783 bytes   0 AO blocks
kali-linux    /root/AGENTS.md                       MISSING
Ubuntu-26.04  /root/.config/{kilo,opencode}/AGENTS.md  MISSING
windows       7 lane files                            24 blocks   24 targets in sync
```

`agent_orders_sync.TARGETS` is Windows-host-absolute, so the generator never had
a Linux target. Every Windows lane carried the lane-queue + domain-trees protocol
and **neither Linux lane carried any of it** — the two environments that run the
FCC/BCC work were starting on canon that predates the board protocol entirely.
A `--check` that reports "24 in sync" while two lanes are un-instructed is a
gate measuring the half it can see.

### Fixed

- `tools/agent_orders_sync.py` grew `WSL_TARGETS` + `render_for_wsl`: the same
  source blocks, host-rewritten (`C:/Users/clint` -> `/mnt/c/Users/clint`,
  `C:/Azazael` -> `/mnt/c/Azazael`, `python X` -> `python3 X`).
- Delivered and **read back**: Ubuntu 5/5 blocks, Kali 5/5 blocks.
  `python3 /mnt/c/Users/clint/_board.py max` from Kali returns `MAX 46846` — the
  same shared board, so the rewritten path is live, not decorative.
- `--wsl` wired into `.githooks/pre-commit` check 10 (3.6 s measured). A host
  with no `wsl` on PATH prints "not verified" and passes; a present distro that
  drifts blocks the commit.
- Controls added (2 tests): no Windows path survives, no bare `python`, and the
  rewrite is idempotent when an apply is retried.

Two defects in my own first attempt, both caught by re-reading the target rather
than trusting the apply:

1. **Lost update.** The write sat inside the per-block loop and rebuilt each
   block from the same pre-read text, so only the last block survived. Kali came
   back with `lane-queue` and the other four MARKERS ABSENT one second after
   "5 written". Now the document is assembled in memory and written once.
2. **WinError 206.** Kali's 19 KB file through base64 on argv exceeded the
   Windows command-line limit. Content goes on stdin now; argv carries only the
   path.

Backups: `/root/AGENTS.md.bak-20261031`, `/root/BCC-REINVESTIGATION/AGENTS.md.bak-20261031`.

### Board hygiene — CORRECTED, my first reading was wrong

I first wrote that the blocked pile (730 rows: kilo 311, opencode 97, freebuff
322) was accidental rot "where unfinished work goes to become invisible", and
filed DT-BOARD-BLOCKED-TRIAGE to triage it. **That diagnosis was mine and it was
wrong.** Measured afterwards: **729 of the 731 blocked rows carry the note
`archived pre-cutover backlog (< 2026-10-31)`** — it is a declared archive, and
only 2 rows are individually blocked. Mass-flipping them to open would have
resurrected six days of dead backlog.

46847 is retired with that correction in its note; the real part of the finding
(the 394 duplicate copies) became **DT-QUEUE-DUPLICATE-ROWS** (46851).

The counts were real. The interpretation was not. Reporting a number is a
reading; naming its cause is a claim, and the claim needed the note field that
was already in the rows.

### Verification after all of the above

```
python tools/agent_orders_sync.py --wsl    -> 34 target(s) in sync, 0 problem(s), 0 written
python tools/agent_orders_sync.py --hook --wsl -> 0   (the hook's exact command)
python tools/evidence_gate.py              -> GATE: PASS (1 unverified: rotation)
python -m pytest tests/test_agent_orders_sync.py -> 10 passed
python -m pytest test_evidence_gate + memory_dir + observers + recorder_guard + pams_recorder -> 52 passed
python tools/second_opinion.py --self-test -> 0 problem(s)
git config core.hooksPath                  -> .githooks   (so the wiring is live)
board: no live claims left by BUFFY; kilo 22 open, opencode 2, freebuff 7
```

One test fixed rather than skipped: `test_evidence_gate.py` pinned the prose
`"0 dead"` and broke when the check was renamed to `"unreachable control(s)"`.
It now asserts the property (`startswith("0 ")`, `"(0 new)"`, `offenders == []`),
which is stricter than before.

---

## EV-015 — the task queue was 2x duplicated, and nothing refused a re-post (fixed 2026-10-31)

Found while reading a board row back during the restart sweep: `_board.py tasks
kilo` printed the SAME row (`1039`) three times in a row. Not a renderer bug.

```
task rows in queue      764
distinct task_ids       370          -> 394 surplus rows
1039                    75 rows      source: opencode 74, kilo 1
mcp-001                 76 rows      source: opencode 73, kilo 2, freebuff 1
span                    2026-10-23 16:40 -> 2026-10-29 01:03
median gap between copies  130 s     (min 6 s)
```

An opencode poster re-posted the same two tasks every ~130 s for six days and
then stopped. `claim_tasks` already retires a duplicate when it finds one, so the
board never handed out the same work twice — but the ROWS stayed, so every reader
(`tasks`, `stats`, any lane scanning the queue) pays for 394 copies, and the live
queue is buried in them.

### Fixed

`LaneMessageBoard.post_task` now refuses to create the duplicate:

- an IDENTICAL re-post (same lane, task_id, action and detail) of an unretired
  row returns the existing `board_id` and writes nothing;
- a CHANGED action or detail still posts a new row — collapsing on task_id alone
  would swallow a revised brief and leave the lane working the old one, which is
  worse than the duplicate;
- a retired row (done/blocked) never blocks a legitimate re-post.

Proved on the live store before writing the test: identical re-post returned the
same id (46849 == 46849), changed detail returned a new id (46850), and both probe
rows were retired immediately (0 left unretired).

### Controls

`tests/test_lane_task_queue.py` +3 (14 passed): identical re-post collapses and
the store gains exactly ONE row; changed detail still posts; a retired row does
not block a re-post. The fixture needed a `_fake_bus` — `post_task` publishes
through MemoryBus while the fixture only redirected the readback path, so every
`post_task` test died with "published but no durable queue row could be read
back". Checked for pollution first: 0 rows landed in the production store.

### Not fixed

The 394 surplus rows are still there. Deleting them is safe (retired or
superseded copies) but it is a data change on the shared store, so it rides with
**DT-QUEUE-DUPLICATE-ROWS** (46851) rather than being done blind at restart. That
row carries the safety steps: copy the store first, never delete a row that has a
`lane_task_state` entry (those carry retirement history), delete in one
transaction, re-run `max` + `stats` after.

### Gate after this change

```
python tools/evidence_gate.py            -> GATE: PASS (1 unverified: rotation)
python -m pytest tests/test_lane_task_queue.py -> 14 passed
```

---

## EV-016 — the duplicate check was keyed on task_id alone (fixed 2026-10-31)

EV-015's guard let a revised task through, and the claim path then killed it.
Measured on the live board during cleanup:

```
board 46849  DUP-GUARD-CONTROL  state=blocked
board 46850  DUP-GUARD-CONTROL  state=done   note="duplicate of Board-46849"
```

46850 had the SAME task_id as 46849 but a DIFFERENT detail. `post_task` correctly
posted it as a revision; `claim_tasks` then retired it as a duplicate, because the
duplicate check keyed on `task_id` alone — so a genuinely updated brief would be
silently dropped and the lane would work the superseded one. Two paths, two
definitions of "duplicate", and the wrong one won.

### Fixed

One definition, in `_task_sig(payload)` = `(task_id, action, detail)`. Both the
post guard and the claim-time dedupe use it. `claim_tasks` now retires a row only
when its CONTENT matches a retired, actively-claimed or already-claimed-in-batch
row.

First attempt broke `test_a_dict_detail_does_not_crash_the_claim`: I bound
`detail` into SQL, and legacy rows carry it as a dict, which sqlite refuses to
bind. Signatures are now computed in Python with values normalised to strings, so
a dict detail is compared as JSON text and the legacy path still works.

### Controls

`tests/test_lane_task_queue.py` → **15 passed**, including the new
`test_a_revised_task_is_not_retired_as_a_duplicate` (both rows survive a claim,
no duplicate note is written) and the pre-existing dict-detail test.

### Gate

```
python tools/evidence_gate.py -> GATE: PASS (1 unverified: rotation)
```

### Correction carried with this entry

EV-014's "board hygiene" paragraph claimed the blocked pile was rot. It is not:
729 of 731 blocked rows are the declared pre-cutover archive. See the corrected
paragraph above and the retirement note on 46847.
