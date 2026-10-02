# MIGRATION LEDGER — top-down reengineering, single source of truth

> Created 2026-10-01 (Stage 0). Every unit, tool, skill, and decision lands
> here or it does not exist. Competing lists get folded in or deleted.
> Row status is open or closed — never half-migrated.
> Schema: unit | path | purpose | depends-on | verdict | destination | verified-by | status

## Decisions (frozen; changes go through operator, never drift)

| # | Decision | Date | Basis |
|---|---|---|---|
| D1 | Rip out Natures; no replacement taxonomy; flat registry dispatch | 2026-10-01 | Forensic: 26 keys subset of 87 categories; zero live mechanisms |
| D2 | Empirical proof = learning works after (promotion / live arm / clear loop). No golden-set: zero baseline output means no "before" to preserve | 2026-10-01 | 0 promotions / 193 cycles; operator ruling |
| D3 | HEVC CRF 26 default + libx264 override; 30fps; GOP 300 (edge0 recipe, technique-only per Oxford Compact) | 2026-10-01 | A/B measured; covenant forbids code coupling |
| D4 | No PIL for HTML/MP4 work; Blender role = figures per RULE 0R | 2026-10-01 | Operator directive; lesson #77 |
| D5 | Organization happens at the end (closing stage), not in parallel | 2026-10-01 | Operator directive |
| D6 | Pre-action gate wiring deferred | 2026-10-01 | Operator directive |
| OPEN | `.git`: migrate history vs fresh clone + archived bundle | 2026-10-01 | Deep dive: 304 commits, ~1.3GB history dominated by generated blobs (ppm frames, 74k-line reports); bundle preserves all commits verifiably (RULE 0T) without checking out junk |
| D8 | Move-day `.git`: fresh clone + archived bundle (bundle = full `--all` history) | 2026-10-01 | Operator verdict; dive above; backup/var untracked dirt copied aside, never committed into history |
| D7 | `CROSS_NATURE_ROUTER.py`: DELETE at U3 surgery | 2026-10-01 | Operator verdict; sole live importer METACLUSTER rewritten in same surgery; AOA diagram-only; D1 removes the routed taxonomy |
| OPEN | Home-dir sprawl in scope (U8) or separate | 2026-10-01 | Operator: IN-SCOPE (desktop sweep migrates; moves at move day) |

## Baselines (pinned, branch `migration/baseline-20261001`)

| Artifact | Value | Date |
|---|---|---|
| TERENCE `--json` | 15/15 oracles, 194 faults (1 crit, 9 high, 183 med) | 2026-10-01T14:26 |
| pytest collect | 4216 collected + 1 collection error (sentinel hook vs dill; bystander file innocent) | 2026-10-01 |
| Evolution | 0 promotions / 193 cycles; QD stagnant 70; SPRT blind 85/193; 1-state bandit | 2026-10-01 |
| PMB/PMI memory | 13+ facts this session; daemon hybrid recall verified | 2026-10-01 |

## Units

| Unit | Paths | Files | Depends-on | Verdict | Destination | Verified-by | Status |
|---|---|---|---|---|---|---|---|
| U0 substrate | worm_registry, worm_health, paths/, freethreading, direct_memory | ~5 | — (first) | keep, stabilize first | canonical (unmoved until tree moves) | G0 below (247 worms / 57 tests) | closed 2026-10-01 |
| U1 expansion leaves | WORMS/expansion/* minus substrate (75 top-level; generated/_staging triaged separately) | 75 | U0 | migrate | flat dispatch, same tree | G1 above (75 compile / reg 247 / 205 tests) | closed 2026-10-01 |
| U2 expansion substrate | spine, mesh, servemesh, synapse, fabric_state | 5 | U0, U1 (runtime last) | migrate last (runtime) | flat dispatch | G2 below — CLOSED via R15 (103 tests, cached loads, 13-world) | closed 2026-10-01 |
| U3 clusters (surgery) | CLUSTERWORMS kept+extended (skips, clarification, subset), NATURE_CLUSTERS→deleted, METACLUSTER→v2 flat, CROSS_NATURE_ROUTER→deleted per D7 | 4 | U0 (registry) | rip-out per D1 | categories / delete | G3-EXEC below — CLOSED 2026-10-02 (3cb704fd) | closed 2026-10-02 |
| U4 compliance | audit_trail, sentinel_enforcer/gate, TERENCE wiring (6 files; no compliance/ dir in tree) | 6 | U0 | keep + re-verify gates | same | G4 above (compile / 9 edict / 12-12 self-test) | closed 2026-10-01 |
| U5 satellites | CODEX 87, ORCHESTRATION 84, AOA 30, HYDRA 11, META 16, UTILITIES 23, ML 9, eve_unleashed 11 | 271 | U0 | migrate per-package | `C:\Azazael\` mirror layout | G5 above (271/271 compile) | closed 2026-10-01 |
| U6 entry points | CLI 2, DAEMONS 3, SCRIPTS 30, INTERPRETERS 3, TOOLKIT 9, TOOLS 10 (57; root scripts 209 + tools 127 also clean) | 57 | U0–U5 (entry points last) | migrate last | same | G6 above (393/393 compile) | closed 2026-10-01 |
| U7 skills | 1234 md, 102 L2 families (pkg 968, pkg314t 74, bin 46, …) | 1234 | catalog reconciliation (own track) | triage by family | reconciled catalog | G7 below — CLOSED 2026-10-02 | closed 2026-10-02 |
| U8 home-dir sprawl | Desktop sweep IN-SCOPE (~610MB/20 dirs); moves at move day, mirror layout | measured | scope decided IN-SCOPE 2026-10-01 | — | G8 above — scope closed, moves deferred | closed 2026-10-01 |

## Unit gates (exit criteria; a unit closes only when its gate passes on the migration branch)

### G0 — U0 substrate (measured 2026-10-01, read-only)
| # | Check | Command | Pass threshold (measured) |
|---|---|---|---|
| G0.1 | Bare imports, no preload | `python -c "import sys; sys.path.insert(0,'src'); import CORE.worm_registry, CORE.worm_health, CORE.freethreading, CORE.direct_memory, CORE.paths"` | exit 0; registry len 0 pre-discovery (lazy) |
| G0.2 | Discovery | `discover_worms()` from `CORE.worm_registry` | registry ≥ 200 (measured 247 in 1.9s; fn return 9 — assert registry len, not return) |
| G0.3 | Unit tests | `python -m pytest tests/test_worm_registry.py tests/test_startup_warm_wiring.py -q -p no:cacheprovider` | 57 passed (measured 6.95s) |
| G0.4 | Syntax | `py_compile` on worm_registry.py, worm_health.py, freethreading.py, direct_memory.py, paths/ | exit 0, no moves |
Close rule: U0 closes when G0.1–G0.4 pass consecutively on `migration/baseline-20261001` with no edits outside U0 paths. Re-run gate after any U0 edit.

### G1 — U1 expansion leaves (measured 2026-10-01, read-only)
Count correction: ledger said ~40; measured 75 top-level leaves (80 files minus U2 substrate 5). `generated/_staging/` 91 files excluded — triaged separately, not migrated in U1.
| # | Check | Pass threshold (measured) |
|---|---|---|
| G1.1 | `py_compile` all 75 leaves | clean |
| G1.2 | `discover_worms()` registry len | ≥ 247 (measured 247, no drop vs U0 close) |
| G1.3 | Leaf tests: learning_rl_keys, tensorgene, tensorgene_correlate, wiring_genome, evolution_gates, learning_worms | 205 passed, 1 skipped (1.52s) |
Close rule: G1.1–G1.3 consecutively, no edits in expansion/ since measure.

### G2 — U2 expansion substrate (measured 2026-10-01, BLOCKED-RED)
| # | Check | Result (measured) |
|---|---|---|
| G2.1 | `py_compile` spine, mesh, servemesh, synapse, fabric_state | clean |
| G2.2 | spine_mesh + telemetry + mesh_transport_e2e + wiring_cycle | 92 passed, 9 failed (37.77s) — all 9 in `tests/test_wiring_cycle.py` (promotion/streak/canary cluster) |
Diagnosis: pre-existing promotion-gate failures (streak-gate honesty cluster, cf. loop_integrity/genome_seed OPEN WORK), not caused by migration — zero edits in expansion/. Precise mechanism 2026-10-01: live tuned floors are L1_MIN_OBSERVED=6 / L1_MIN_WINS=4 (hyperopt, up from fallbacks); test fixture forces a 5-organ winner (deliberate — 6 organs == seed fingerprint, unfalsifiable canary) which can no longer clear the 6-floor, so `accepted` stays False at the evidence floor while trial-level accept==1, and streak wins read 0. Calibration fork for R15 track (tuned floor vs fixture vs seed-identity — no guess made here). U2 stays OPEN-BLOCKED; fix belongs to R15/training-honesty track, not substrate stabilize. Does not block U4/U5/U6/U7 (depend on U0 only).

### G2-CLOSE — U2 closed 2026-10-01 via merged R15 (e41e09da + 6928656f): gate set 103 passed (92 + 9 fixed + 2 new), repeat cycle 3.46s→0.01s, suite collect 4221+0 errors. U3 surgery unblocked on this axis (needs `.git` move-day call only).

### G4 — U4 compliance (measured 2026-10-01, read-only)
Note: no `compliance/` directory exists in tree; U4's keepers are audit_trail.py, sentinel_enforcer.py, sentinel_gate.py + tools/terence_* (6 files measured).
| # | Check | Pass threshold (measured) |
|---|---|---|
| G4.1 | `py_compile` audit_trail, sentinel_enforcer, sentinel_gate, terence_invariants | clean |
| G4.2 | `pytest tests/test_rule_0b_a_edict.py` | 9 passed (3.00s) |
| G4.3 | `terence_invariants.py --self-test` | 12/12 validated, 0 UNVALIDATED |
Close rule: G4.1–G4.3 consecutively. U4 CLOSED 2026-10-01.

### G5 — U5 satellites (measured 2026-10-01, BLOCKED single-file)
Package counts verified exact: CODEX 87, ORCHESTRATION 84, AOA 30, HYDRA 11, META 16, UTILITIES 23, ML 9, eve_unleashed 11 = 271.
| # | Check | Result (measured) |
|---|---|---|
| G5.1 | `py_compile` all 271 | 271/271 — `src/CODEX/cain_rebuild_final.py` L208 missing paren fixed 2026-10-01 (one-char `)`, derived from sibling single-arg `T([...])` calls); was the sole red, pre-existing |
U5 CLOSED 2026-10-01. Collect baseline re-verified during U5 window: 4216 collected + 1 collection error (count holds vs pinned; offending file now `tests/test_replay_failed.py` PermissionError, was sentinel/dill — same shape, different face, needs its own diagnosis).

### G6 — U6 entry points (measured 2026-10-01, read-only)
Measured: src/CLI 2, DAEMONS 3, SCRIPTS 30, INTERPRETERS 3, AZAZAEL_TOOLKIT 9, TOOLS 10 = 57 (ledger ~50 corrected). Root `scripts/` 209 + `tools/` 127 also compile clean (debris lives there, but nothing red).
| # | Check | Pass threshold (measured) |
|---|---|---|
| G6.1 | `py_compile` all 57 src entry files + 209 root scripts + 127 root tools | 393/393 clean |
Close rule: G6.1 + collect baseline holds (4216+1, verified above). U6 CLOSED 2026-10-01.

### G7 — U7 skills (measured 2026-10-01, inventory gate)
Measured: 1234 md, single prefix family `azazael-*`; L2 split 102 families (pkg 968, pkg314t 74, bin 46, devtools 8, worms 6, fix/tool 5 each, autodiff 4, …). Full reconcile (family-by-family keep/drop vs catalog + skills-lock.json) is its own track like the DB extract — G7 records the inventory, not the verdicts.

### G7-CLOSE — U7 verdicts 2026-10-02 (all six recorded, then closed)
1. Canonical = `skills/` (was already declared); home mirror complete + synced (25 refreshed 10-02); project mirror +13 newest propagated; 7 hand-only agent dirs (archify, gil-sidecar, inference×3, meta-reflection, timesfm) KEPT with reason (agent-local, no flat source).
2. Bulk 1042 (pkg+pkg314t) KEPT: no code bulk-loads the corpus (session_start/sync only sync; skills load by name on demand), so the 188k-token prune precedent (an all-load path) does not apply. Revisit only if a bulk-loader appears.
3. 11 stale-ref files fixed to flat language + mirrored to all three trees + catalog row touched (no generator script exists; full regen deferred).
4. skills-lock.json OUT OF SCOPE (external skill registry, not this corpus).
5. skills.win-backup (132) + skills_staging (1): left as archive.
6. Wire-or-cut 3 retirements + counts stood re-verified (29/29) after the surgery.
| # | Check | Result |
|---|---|---|
| G7.1 | Count + L2 family split | 1234 / 102 families recorded above |
U7 stays OPEN (triage execution pending); inventory is closed, verdicts are not.

### G3 — U3 clusters surgery (spec complete 2026-10-01; execution blocked)
Router verdict landed: DELETE per D7 (sole live importer METACLUSTER rewritten in same surgery; AOA diagram-only; D1). File NOT deleted yet — deletion happens inside the surgery with the METACLUSTER rewrite, never ahead of it. Remaining preconditions: green U2 (R15) + `.git` move-day call. U3 stays OPEN-BLOCKED on those two.

### G3-EXEC — U3 surgery executed 2026-10-01/02
Deleted: NATURE_CLUSTERS.py (1701), CROSS_NATURE_ROUTER.py (D7), 9 taxonomy test files (3 nature_clusters, nature_metacluster, 2 metacluster suites, cross_nature, ncm_integration, dlq, spine_mesh_architect, verify_fixes). Rewritten flat: METACLUSTER v2 (no NCM/router; ClusterWORMZ-per-category; signatures kept), run_mesh_cycle (per-category + _NO_EXECUTE guard), db_health + dlq_burndown + dlq_watch (DLQ store), WORMS/__init__ (NCM→ImportError w/ directions), build_all_concurrent + sync_all manifests, AOA diagram labels. Absorbed: DLQ get_dead_letter_summary/retry_all_failed_worms (+epoch, category scope) with 5 tests. Adapted: spawn_decision (engine tests kept), spine_mesh (registry names), spine_wiring (spans test retired w/ note), circuit_breaker (ClusterWORMZ port; found aggregate-timeout defect, logged), colour_queens (enforcement ported INTO ClusterWORMZ: subset execute + retired/quarantine skips), delegation (clarification normalization ported into _execute_worm_class), mesh_fabric (sweep guard), worm_telemetry (third tap → ClusterWORMZ), cluster_integration (circular DFS restored + registry coverage test), full_integration (flat-dispatch check), worm_registry_integration (flat grouping), cluster_worms (module list), worm_registry docstring, wire-or-cut 3 entries retired + counts. Verified: 297 targeted green, TERENCE 12/12, live defense-category execution, collect 3943+0.

### G3-CLOSE — U3 closed 2026-10-02 (3cb704fd)
Close evidence: U2 gate set re-green post-surgery (103 passed), collect clean (3913+0 errors), TERENCE self-test 12/12 validated, live MetaCluster defense-category execution ok/1/fail/0, wire-or-cut 29/29. 8 of 9 units closed; only U7 verdicts track remains (plus move-day execution).

### G8 — U8 sprawl (measured 2026-10-01, scope gate)
Desktop sweep measured (~610MB, 20 dirs): AOA 103.6, Azazael_Audit 102.0, COSMOS_VIEWER 123.6, Full_Filesystem_Scans 205.0, graphs/audit/cosmos fragments 0.1–36.1, Standalone 1.1, Vault 0.4, CODEX 18.0+1.2. Scope decision (in-scope vs separate) still OPEN per plan — G8 records the measure, not the verdict. U8 stays OPEN pending scope.

## Triage rows (first entries; session debris vs keepers)

| Path | Found | Verdict | Reason | Status |
|---|---|---|---|---|
| `scripts/_emoji_mood_probe.py` | 2026-09-20, pre-session | quarantine | width-model probe; keep iff monitor unit claims it | open |
| `src/CODEX/cain_apply_emoji_20260930.py` | 2026-09-30, pre-session | quarantine | one-shot CAIN edit; keep iff CODEX unit claims it | open |
| `archived_unified/` (shadow source tree) | forensic | resolve, never move | diff vs `src/`, absorb unique, delete fork | open |
| `archive/` junk drawer (1.03GB) | clutter policy | sort w/ manifests or delete | — | open |
| `var/cold/` snapshots (4.06GB) | clutter policy | keep newest 1, purge rest | regenerable | open |
| `src/CORE/WORMS/expansion/generated/_staging/` (91 gen files) | U1 scoping 2026-10-01 | quarantine, never migrate blind | generated staging; keep iff a unit claims a file | open |
| `ClusterWORMZ` pool-timeout rows never reach `state.results` (U3 find 2026-10-01) | surgery observation | known defect, not fixed here | `execute_all` timeout branch appends to returned list only; `aggregate_results` reports 0/0 after timeouts — fix changes runtime semantics, belongs to U2/runtime track | open |
| `src/CODEX/cain_rebuild_final.py` (was SyntaxError L332) | U5 gate 2026-10-01 | fixed, one-char paren | L208 unclosed `T(`; sibling calls single-arg; 271/271 now | closed |
| `tests/test_spine_mesh_architect.py` VANISHED (U3 note 2026-10-02) | observed then absent | absence = intent | untracked file testing NATURE_DEFINITIONS immutability; purpose moot post-deletion; copy survives on G: mirror; no other tree files missing (G: diff otherwise = own deletions + stale snapshot) | closed |

## Completed work log

| Date | Item | Verified by |
|---|---|---|
| 2026-10-01 | `CORE/WORMS/__init__` eager→lazy PEP 562 | bare import skips nature preload; 3 names resolve |
| 2026-10-01 | `.graphifyignore` += backup patterns (85 files) | next extract |
| 2026-10-01 | Video standard HEVC cutover (compress/reencode/batch_render/2 recorders) | CASCADE 107→90MB; A/B measured |
| 2026-10-01 | GIF looping output added | 3s→9.56MB looping gif |
| 2026-10-01 | `scripts/ascii_video.py` built | deterministic hash-equal; 10s demo 0.05MB |
| 2026-10-01 | Generator wired to enhanced lib (30 keyframes, 2 namespaced) | no dangling refs |
| 2026-10-01 | Emoji reactions mapped; demo console-guarded; PIL deprecated | demo green |
| 2026-10-01 | Mining carry-forward closed: inference-strategy metric verified 226/35 | docs/INFERENCE_INTEGRATION_STRATEGY.md:21 reads 226/35 (2026-09-14) |
| 2026-10-01 | Mining carry-forward closed: rust-plan metric verified 70/594 | docs/RUST_CONVERSION_PLAN.md:146 + :400 and CROSS_ENV_MANIFEST.md:117 read 70/594 (was 46/264) |
| 2026-10-01 | Full-chunk extract analysis DONE (read-only, base tables, FTS untouched): Jul-14 659333 mem / 81275 sess May27→Jul14, FTS malformed; Sep-26 353837 mem / 4923 sess Jul01→Sep26, FTS intact + 844 patterns + 138714 otel | wisdom = nature-era ops (8.7k+8.3k discoveries, 2.5k+9.1k executed, 4.9k+2k routes) + learning growth (1.9k→20k trainings, 1.9k→20k q-persists); noise = 92.7% ceremonial in Jul |
| 2026-10-01 | U0 CLOSED: G0.1 exit 0/reg 0, G0.2 reg 247, G0.3 57 passed, G0.4 py_compile clean — consecutive close run | first unit closed; U1 unblocked (depends-on U0 satisfied) |
| 2026-10-01 | U1 CLOSED: 75 leaves compile, reg 247, 205 passed +1 skipped; count corrected 40→75; generated/_staging 91 quarantined | U2 unblocked |
| 2026-10-01 | U2 BLOCKED-RED: compile clean but 9 pre-existing wiring_cycle fails (promotion/streak cluster); zero expansion edits | fix = R15 track, not substrate |
| 2026-10-01 | U4 CLOSED: compile clean, 9 edict tests, 12/12 self-test (no compliance/ dir; 6 files) | — |
| 2026-10-01 | U5 BLOCKED single-file: 270/271 compile (`cain_rebuild_final.py` L332); counts verified exact; collect 4216+1 holds (error face changed, needs diagnosis) | disposition = CODEX unit |
| 2026-10-01 | U5 CLOSED: one-char paren fix L208, 271/271 compile, collect unchanged 4216+1 | 5 of 9 units closed |
| 2026-10-01 | U6 CLOSED: 57 src + 209 scripts + 127 tools = 393/393 compile | — |
| 2026-10-01 | U7 inventoried: 1234 md / 102 L2 families; verdicts pending (own track) | — |
| 2026-10-01 | U3 BLOCKED: surgery needs router + .git OPENs and green U2 | — |
| 2026-10-01 | U8 measured: desktop ~610MB/20 dirs; scope still OPEN | — |
| 2026-10-01 | D7 router verdict DELETE (AOA diagram-only, quartet zero refs, METACLUSTER rewritten in-surgery); U8 scope IN-SCOPE → U8 CLOSED | file deletion deferred into U3 surgery |
| 2026-10-01 | ALL FIVE implemented + merged (e41e09da, 6928656f): R15 merged, outer-loop readout live, startup prime wired, collection 4221+0, floor-13 settled test-only; U2 CLOSED (103 tests) | 7 of 9 closed; left U3 (needs .git) + U7 (verdicts track) |
| 2026-10-01 | D8 EXECUTED: `G:/source-of-truth/azazael/azazael-history-20261001.bundle` 1297MB, `verify` okay, complete history, 7 refs (master, migration branch, r15, gdrive, stash) | fresh clone authorized for move day; backup/var dirt still aside, uncommitted |
| 2026-10-02 | U7 CLOSED: mirrors reconciled (home synced, project +13, 7 hand-only kept w/ reason), bulk 1042 kept (lazy-load, no bulk-loader), 11 stale-ref files fixed ×3 mirrors, catalog row touched, lock/win-backup scoped out | 9 of 9 units closed; only move-day execution remains |
| 2026-10-02 | Copy-aside DONE: `G:/source-of-truth/azazael/azazael-dirty-baseline-20261002` 69,196 files, 0 mismatch; 5-file gap = live venv interpreter symlinks under `archive/.../.venv/bin` (ERROR 1920 locked, regenerable, zero source value) | dirty tree preserved; fresh clone cleared after pentest-data archive |
| 2026-10-02 | U8 MOVES DONE: 26 desktop dirs + 45 loose files (911MB total incl. AOA videos) → `C:/Azazael/desktop/` via robocopy /MOVE; Desktop verified clear of azazael items | desktop sweep closed |
| 2026-10-02 | Pillars inventoried+preserved: Ubuntu /root/azazael git master 7d883ba + 6 dirt files saved aside (/root/ubuntu_dirt_aside_20261002, value already mined); Ubuntu /home fragment 13MB + recovery_staging left; Kali /root/azazael 500MB non-git June-Aug tree → `G:/source-of-truth/azazael/kali-tree-20261002.tar` (7,098 entries verified). Full pillar convergence via sync system = separate track, not this migration. | pillars safe |
| 2026-10-02 | Pillar convergence DONE: Ubuntu 1,844 files via sync_all (integrity ALL SYNCED); Kali src/scripts/tests/tools/docs/skills via direct copy + 12-file deletion set applied + gates 27 passed in-Kali | all pillars on migrated code |
| 2026-10-02 | Move-day finding: `__editable__.azazael-1.0.0.pth` points every interpreter at source `src/` — first-import-wins via sys.modules means in-clone runs execute SOURCE code (proven: collision test serves C:/Users paths in C:/Azazael). Per-checkout cache filenames committed as defense-in-depth. MOVE-DAY STEP 0: reinstall editable pointed at `C:/Azazael/azazael` (or uninstall), THEN run gates from the new root | clone verification unsound until repoint; source-tree gates stand |
| 2026-10-02 | Pentest archive DONE: `C:/Azazael` (428 files, 1.83MB nmap/pentest) → `G:/source-of-truth/azazael/azazael-pentest-archive-20261002`, re-list 0 remaining, folder cleared | precondition 2 cleared; verification list next |
| 2026-10-02 | Move-day verification FROM NEW ROOT (C:/Azazael/azazael): collect 3201 + 1 documented error (track_registry needs others' untracked helpers); gate battery 163 passed; 4 engram/dream fail IDENTICALLY in both trees (embedding backend down, environmental); TERENCE 9/12 (3 need live runtime state by design). Found+fixed en route: per-checkout cache, stale test reference (tracked), 3 gate-missing files (tracked). Tree verified for move day. | verification list closed |
| 2026-10-02 | Untracked-helper resolution: scripts/track_registry.py tracked (5KB stdlib-only, zero blast radius) → collect 3205+0 errors. 3 track-content failures are IDENTICAL in both trees (GRPOTUNE vs ALLPAR live training-state drift; config/track_bandit.json untracked) — other owner (training sessions), not migration scope. Boundary stands: migration tracks gate-loadbearing files only. | helpers resolved as far as safely possible |

## Mined history (2026-10-01 extraction; 34 decision-bearing commits)Theme groups with hashes. Full bodies in `git show <h>`. Rule learned
from the forensic: subjects here are descriptive — future commits must
keep that standard (bulk snapshots with no rationale are banned).

| Theme | Commits |
|---|---|
| Test forensics series (a–e + env/order markers) | `ca1045b0` (contradiction note, summary floor, tautology, **nature floor**) `6d972343` `3b51e52f` `be17e737` `bc4d51db` |
| Mandates codified to canon | `d41551d0` (5 lessons #55–59, CD1 P2) `42fb160c` (UUID7 RFC 9562, research fidelity) `2b9cdd93` (RULE 0Z-J sync mandate) |
| Training/evolution honesty | `910f254d` (versioner rewrite + plateau skip) `1645ae6c` (stop crediting no-change morph trials) `bb46c97f` (Q-table resume FTS fix, honest synthetic flags, GRPO tombstones) |
| Mesh/spine liveness | `6110486a` (deadlock fix + gate boundary) `6080d17d` (churn-loop, liveness seed, spine doc accuracy) `d57b970d` (busy_timeout 15→60s, mesh timeout 300→600) `bf8584e8` (spine negatives observable, PF16 declared data) `40a29fd8` (store tombstones on write path) |
| Monitors/dashboards | `656b7a19` (LAN page, rolling log, stale flash) `491eff90` (wallboard repaint) `7405ff67` (learning-loop audit + graphing) |
| Audit trail integrity | `07e9924e` (forensic supersedes 7 audits) `3a948a26` (reductions ledger survives merge) `2d919c9a` (self-mod harness, trail records itself) `aff97b17` (audit scope boundary, dict-key debt) `f3f18772` (four corrections) `dfddb505` (freshness gate honesty) |
| Recurrence warnings (regressed before — watch in migration) | `8ce2128c` (KaliArm fixed 09-14, missing again — prevention test never collected) `fe000cfd` (cross-file leaks red-only-in-aggregate) `563b4fa6` (rebuilt declaration evidence + concurrency rendezvous) `6cdbbcea` (tap honesty, decision_id, grade gate) `b8413d33` (writers manufacturing verdicts) `71eeed25` (arch/neural audit, errors 190–192) `c9be4e13` (type-check baseline + mesh census) `fa55c257` (WSL drift + reconciliation) |

## Distilled rules (2026-10-01; 184 lessons → 24 durable, with destinations)

Distillation rule applied throughout: session-specific corrections stay in
PMB; only transferable, checkable-or-teachable rules land here. Each rule
names its enforcement: VALIDATOR (TERENCE-encode it), CONVENTION (new-tree
docs + review checklist), SKILL (agent-facing procedure), or MEMORY (kept
in PMB only — judgment, not mechanism).

| # | Rule | Source lessons | Enforce |
|---|---|---|---|
| R1 | User is sole source of truth; describe, never accept; acceptance is the user's, never self-assessed | 0B, 0B-A…E, ACCEPTANCE, NO-REINTERPRET | CONVENTION |
| R2 | Every oracle ships a negative control; unvalidated oracles license nothing destructive | 0B-C, unfailable-validators | VALIDATOR (self-test) |
| R3 | A control is not in place until exercised and measured; no inherited trust | 0B-D, hardware-measured, instrument-gap | CONVENTION + recorded readings |
| R4 | Verify the predicate (tool's claim ≠ the thing you care about); a detector of absence needs a positive capability test | 0B-B, ABSENCE-CAPABILITY-TEST | VALIDATOR (positive controls) |
| R5 | Gates carry diagnosis, not counts; artifacts never answer out of scope; readouts never hide bad numbers | #88, #89, readout-health | VALIDATOR (gate_timing) |
| R6 | Baselines are pinned before change; keys no unrelated edit may move; wall-clock assertions banned on shared machines | #97, #93, #95 | CONVENTION + ledger tables |
| R7 | Unmeasurable metric = environment bug until proven otherwise; caps before filters are caps on nothing | #87, #92 | VALIDATOR |
| R8 | Measurements inside transitions are caches; repairs that recompute are second leaks; half-restores are leaks | #93, #94, #90 | CONVENTION (review checklist) |
| R9 | No design from filenames/sizes/hashes; consolidation needs objective evidence (inbound refs, named-in-source, staleness, duplicates) | CORRECTION-docs, OBJECTIVE-EVIDENCE | CONVENTION (ledger gate) |
| R10 | Browser capture for animation; PIL never for motion; SVG never for photoreal; read the rendered artefact | #77, SVG-BAR, RENDERED-ARTEFACT, #03, #79 | CONVENTION (video unit, done) |
| R11 | Deterministic, generated-not-transcribed, seekable capture; stop guessing frames; session-specific reports | edge0-lesson, CAIN #78/#76, STOP-GUESSING | CONVENTION (video unit, done) |
| R12 | 3.14t: lazy imports with fallbacks + type-ignores; double-checked locking; no abiflags; per-thread facts; trust the pip resolver | #38, #32, #20, #56, #31, #21, #66, #91 | CONVENTION |
| R13 | Paths: no profile literals; WSL via shlex/absolute/no-cd; match any path component; verify temp inline; G: degrades gracefully | #55, #61, #62, FILTER-PATHS, #27, #56-GDRIVE, #05 | CONVENTION + target layout |
| R14 | Tests fail honestly: suite mandate, aggregate verification as its own instrument, no red-only-in-aggregate leaks; prevention tests must provably collect | #81, #84, fe000cfd, 8ce2128c, sentinel-dill | VALIDATOR (test/import_failures) |
| R15 | Training honesty: no credit without trainer-call change; plateau skips persisted; tombstones logged; arms must all be live; separately, comparability is a 4-way conjunction | morph-trials, plateau-skip, tombstones, DEAD-ARM, APPLES-ORANGES | VALIDATOR (fitness_arms, evolution_progress) |
| R16 | Fix derived and measured, never redesigned from scratch; refusals to guess are the feature; input contracts measured | FIX-DERIVED, REFUSE-GUESS, META-INPUT | CONVENTION |
| R17 | Enforcement is a ladder (clock/gate first, prose last); hooks over prose; check canon at cheap triggers | ENFORCEMENT-LADDER, HOOK-NOT-PROSE, TRIGGER-CONDITIONS | VALIDATOR where encodable |
| R18 | Memory ops: daemon-hybrid recall assumed; embed queue duplicates known; MCP config per client; workspace ID not name; launcher path canonical | cold-stdio, embed-queue, CONNECT-BROKEN, MCP-SHAPE, WORKSPACE-ID, PAMS-LAUNCHER | SKILL (runbook) |
| R19 | Docs: versioned TODOs kept consistent; fix-after-audit; architecture review method; no over-scripting before reading | #42, #44, #71, REVIEW-METHOD, #24 | CONVENTION (ledger process) |
| R20 | Consolidation moves copy-then-verify; OLD_PROJECT pattern for foreign content; content discovery by cross-reference | #08, CONTENT-DISCOVERY, #06-batch-render | SKILL (migration procedure) |
| R21 | Regenerate artifacts the way the refresh path regenerates them; never hand-edit derived maps | #96, STALE-ARTIFACTS | VALIDATOR (artifact freshness) |
| R22 | Figures: glyph≠figure; photoreal via sampled data (ComfyUI/Blender), never escalated SVG; visual register matters | 0Q, 0R, SVG-BAR, VISUAL-REGISTER, BLENDER-MATERIALS | CONVENTION (figure unit) |
| R23 | Substitution-escalation and surface-cloning are failure modes: same substitute twice = stop and name it; learn looks, never surfaces | SUBSTITUTION, CLONE-SURFACE | CONVENTION |
| R24 | What works is not re-litigated: live loop, recall, self-test, builds are settled instruments; audit the gap, not the instrument | WHAT-IS-WORKING, LESSON-86 | CONVENTION |

## Environment mining (2026-10-01; Ubuntu, Kali, G: in order)

| Vein | Yield | Verdict |
|---|---|---|
| Ubuntu docs (4 diffs) | Metric refreshes: 95/18→226/35 (inference strategy), 46/264→70/594 routes/paths (rust plan); audit-todo same-structure content refresh | Port the two metric lines; audit-todo merge belongs to docs unit with current numbers |
| Ubuntu archive-banner removal | `TODO_FULL_PRODUCTION_WIRING.md`: SUPERSEDED banner stripped, filename ref reverted | REJECT — violates archive freeze; Windows frozen copy stands |
| Jul-14 DB (1.1GB) | 81,275 sessions / 616,744 of 659,333 memories read (93.5%, 1 bad chunk); May-27→Jul-14; peak weeks Jun-W24/25 + Jul-W26 | Ceremonial noise dominates (534k starts+milestones, 38k size alerts); signal: 8.5k nature discoveries, 1.9k executions, 3.6k routes, 1.9k training_complete, 1.9k q_table_persisted |
| Sep-26 DB (743MB) | 4,923 sessions / 353,837 memories through Sep-26; one minor index complaint | Healthier; extends coverage past July |
| Kali birth-week snapshots | NATURE_CLUSTERS Jun-17 52.9KB → Jun-19 54KB with the layer's only rationale (replace if/elif dispatch) | Filed as the layer's epitaph; flat registry solves the same problem |
| Kali dev docs | June status: ClusterWORMZ OK, NatureCluster OK, 37 worms; WORM_AUDIT rates NATURE_CLUSTERS ✅, router partial | Contemporaneous "mechanically worked" record — complaint was provenance + learning, never mechanical failure |
| DB corruption note | Jul FTS + data pages partly malformed; Sep nearly clean | Chunked-read pattern is the extraction method; FTS untrusted for old stores |

## Decision rationale + negative results (appendix, 2026-10-02)

Why the verdicts, and what failed on the way here. Basis column states;
this states the chains.

- **D7 router DELETE:** sole live importer METACLUSTER (guarded import, rewritten in-surgery); AOA one diagram string; quartet zero imports; D1 removes the routed taxonomy. Keep-as-generic would preserve a router for nothing.
- **D8 fresh clone + bundle:** 304 commits but ~1.3GB history dominated by generated blobs (ppm frames, 74k-line reports); bundle preserves all commits verifiably (RULE 0T) without checking out junk.
- **U8 IN-SCOPE:** desktop sweep measured 911MB/71 items; operator works out of the new folder.
- **Floor-13 settled test-only:** proven in tests (20/20 at floor 13), never evaluated by hyperopt (production tuned 6); promoting by hand-edit would fight the optimizer's lineage. 13/17/19/14 derivation: 13 covers the floor, +1 differs from seed (14 minimum); 17/19 were minima under keep-the-fixtures constraints; 14 kept the ghost theme + all fixture roles.
- **Bulk skills KEPT:** no code bulk-loads the corpus (sync only syncs; skills load by name); the 188k-token prune precedent addressed an all-load path that does not exist here.
- **Negative results:** (1) 19→17 trim broke nothing but earned nothing — reverted, then re-derived to 14 properly; (2) stale-bytecode theory of the prime-test failure was wrong — the `wc` fixture stubs the loader, so priming through it can fill nothing (45-min detour, mechanism documented in test); (3) `Select-Object -First N` hid matches and faked two findings — verify with full-output-to-file; (4) first U7 commit swept an unrelated vendor tree — rescoped and recommitted; (5) shared-pickle cross-tree poisoning fixed by per-checkout filenames, but the live culprit was the editable install shadowing every interpreter; (6) collection-error face rotation (sentinel/dill → replay_failed) was one mechanism (import-time nul probe vs audit hook), fixed once at conftest.
- **Open threads:** track-content drift (training sessions), bulk-loader watch (revisit keep-verdict only if one appears), promotion_quality readout (report-only; gating needs its own negative control first, R2).
