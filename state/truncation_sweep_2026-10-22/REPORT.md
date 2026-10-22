# TRUNCATION & LIMIT SWEEP — LANE B — 2026-10-22

## Method (RULE 0Z-L compliance)

- HEAD at sweep time: `5d8f0477e400` (mint pin `784312de` moved during the sweep; Lane C
  landed `a74879ec` + `5d8f0477`. Pins are advisory by protocol — sweeps read live HEAD
  and recorded the move).
- **Sweep A** (Python): HEAD-pinned AST scanner via `git cat-file --batch`, 5,091 `.py`
  blobs, 24-thread consumer pool → **6,834 rows, missed=0, 0 parse failures**.
- **Sweep B** (text/script surfaces): regex scanner over `.md .json .toml .yaml .yml
  .txt .ini .cfg .sh .ps1 .bat .cmd` plus `.ts/.js` in code tops → 5,942 blobs →
  **541 rows, 0 errors, 0 scanner caps applied** (throughput bound never hit).
- Every verdict-class row below was deep-read **at HEAD** via `git show HEAD:<path>`
  (never the worktree). `git status --porcelain` verified clean before==after.
- Scripts live in Temp only; `state/` outputs are gitignored and never staged unforced.

## Classification taxonomy

| class | meaning |
|---|---|
| D0 | display-only, honest count preserved (bounded examples + `and N more`/total) |
| D1 | durable record truncation (persisted data cut without marker) |
| D2 | production recall window (query cap shapes what a live path can see) |
| D3 | toy-scale shaping constant (small const that shapes throughput/behavior) |
| D4 | deliberate policy — env/arg-overridable, exact-requirement, or documented |
| D5 | liveness / newest-record probe (`LIMIT 1` fetchone, fetch-latest) |
| D6 | id/hash prefix slices (collision-domain graded) |
| D7 | verified false positive (graphics widths, re.sub count, status parsing) |
| H  | harness layer (outside repo tree) |

## Exact sweep counters (first_party by band)

Sweep A: total=6,834 (first_party=3,946 / excluded=2,888)

| kind | 1-8 | 9-32 | 33-64 | 65-256 | 257-4096 | >4096 |
|---|---|---|---|---|---|---|
| slice_head | 634 | 539 | 254 | 773 | 239 | 21 |
| slice_tail | 48 | 51 | 36 | 43 | 104 | 4 |
| slice_win | 36 | 8 | 0 | 1 | 0 | 0 |
| drop_head | 177 | 0 | 2 | 1 | 0 | 0 |
| const | 265 | 39 | 19 | 36 | 57 | 41 |
| kw_cap | 155 | 111 | 30 | 45 | 77 | 17 |
| pos_cap | 1 | 0 | 0 | 0 | 0 | 0 |
| sql_limit | 34 | 25 | 1 | 6 | 16 | 0 |

Sweep B: total=541 (first_party=345 / excluded=196)

| kind | 1-8 | 9-32 | 33-64 | 65-256 | 257-4096 |
|---|---|---|---|---|---|
| named | 139 | 37 | 16 | 23 | 22 |
| slice | 20 | 20 | 13 | 38 | 12 |
| sql | 2 | 0 | 0 | 1 | 1 |
| cmd | 0 | 0 | 0 | 0 | 1 |
| flag | 0 | 0 | 0 | 0 | 0→10 total (bands 65+) |

## LAYER 1 — production code

### D1 — durable record truncation (real, ranked)

| site | cap | verified verdict |
|---|---|---|
| `tools/merge_bake_lane.py:131` | merged fields `source[:80] item_id[:80] title[:120] body[:4000]` | merged lanes persist with fields cut, **no marker, no drop row** — worst silent-cut site found |
| `tools/mesh_function_preflight.py:1447` | `entry["decider_evidence"] = evidence[:3]` | WIRE-OR-CUT gate records max 3 provenance facts per decision (decision itself computed separately; record window, not verdict window) |
| `tools/transcript_ap5_gate.py:848` | `f.session_id[:12]`, `f.message_id[:12]` (48-bit) | report linking IDs truncated — fine for joins, listed for completeness |
| `tools/transcript_ap5_gate.py:828` | `report.announcements[:5]` | gate output shows ≤5 announcements; `stats` count honest → D0/D1 hybrid |
| `src/session_memory.py:1014` | `sessions[:3]` in `print_context_banner` | honest: prints `Previous Sessions ({len(sessions)})` then first 3 summaries (`summary[:60]` each) |

### D2 — production recall windows (verified call sites)

| site | window | semantics verified |
|---|---|---|
| `scripts/evolution_cycle.py:565` | `query_memories(event_type='evolution_result', limit=1)` | **newest-only probe by design** (`last_best_genes`) |
| `scripts/evolution_cycle.py:2377` | `event_type="strategy_steered", limit=1` | newest strategy record — deliberate |
| `scripts/evolution_cycle.py:2889` | `limit=12` | margin-pressure streak window |
| `scripts/evolution_cycle.py:1439/:1629` | `limit=40` | full-history analysis paths |
| `src/CORE/WORMS/expansion/scheduling.py:623` | `limit=1` | newest training-run check |
| `src/CORE/WORMS/expansion/scheduling.py:659` | `limit=2` | explicit `if len(recent) < 2: return None` guard — honest |
| `src/CORE/WORMS/expansion/scheduling.py:716` | `limit=int(RAMPUP_WINDOW)` | =3 episodes drive ramp decisions |
| `src/CORE/WORMS/expansion/learning_grpo.py:687` | `limit=1` | `load_policy` newest-only |
| `src/CORE/WORMS/expansion/meta_cognition.py:1029` | `limit=5` | `load_state` |
| `src/CORE/WORMS/expansion/dreaming.py:198` | `limit=5` | error-neighbor anchors |
| `src/CORE/WORMS/WORM_SELECTOR.py:217` | `limit=10` | selection-result recording |
| `src/CORE/WORMS/expansion/learning_rl.py:357` | `limit=10` | Q-table load |
| `src/CORE/codebuff_tracker.py:871` | `list_sessions(limit=5)` | `get_session_summary` narrows fn default (20 at :254) |
| `src/CORE/health_server.py:135/:226`, `src/CORE/dashboard.py:235/:255/:552` | `search_memories(limit=10/5)` | dashboards/health |
| `src/CORE/compliance_auditor.py:744` | `get_audit_log(limit=5)` | audit tail |
| `src/ORCHESTRATION/AssistantLogProtocol.py:338` + `_Enhanced.py:597/660/666` | `query(limit=5/10)` | assistant context |
| `src/CORE/local_memory.py:2432` | `fetch_all_memories(limit=1)` | `capsule_probe` liveness (D5) |
| `src/CORE/local_memory.py:2593` | `evidence[:5]` in `recall_with_abstention` | abstention provenance window |

Memory-store **defaults** (`src/CORE/local_memory.py`): `recall_recent=20`,
`query_memories=50`, `search_memories=50`, `query_real_errors=100`,
`fetch_all_memories=2000`, `list_sessions=20`, object-graph `200` rows / `depth=1`,
and `MAX_QUERY_LIMIT=500` clamp `:258/:891-900` with one-time warning log — honest.

`scripts/evolution_cycle.py:2047` documents the store contract: "`query_memories` does
min(limit, 500)" and the alert pool is a "hard-capped 500-row sliding window" —
documented consequence-surface.

### D3 — toy-scale shaping constants (deep-read at HEAD)

| site | const | class note |
|---|---|---|
| `src/CORE/WORMS/expansion/scheduling.py:201` | `RAMPUP_WINDOW=3` | episode ramp decisions |
| `src/CORE/WORMS/expansion/scheduling.py:199` | `RAMPUP_MIN_LIMIT=25` | ramp floor |
| `src/CORE/WORMS/expansion/spine.py:3525` | `CHRONIC_WRITE_CAP=3` | chronic-state writes |
| `src/CORE/WORMS/expansion/spine.py:4106` | `MAX_EPISODES=3` | episode loop |
| `src/CORE/WORMS/expansion/spine.py:3519` | `MAX_GENERATED=24` | generation caps |
| `src/CORE/WORMS/expansion/spine.py:630/:1049/:1505` | `PROBE_LIMIT=4 / K_BUCKET_SIZE=5 / MAX_PROPOSALS=5` | spine policy |
| `src/CORE/WORMS/expansion/servemesh.py:324` | `REPROBE_LIMIT=2` | reprobe budget |
| `src/CORE/CORE/data_retention.py:75` → `src/CORE/data_retention.py:75` | `LOG_ROTATE_KEEP=5` | log rotation keeps 5 |
| `src/CORE/spine_registry.py:65/:81/:152` | `_HIST_MAX=20 / _OUTCOME_STRIPE_COUNT=8 / _STRIPE_COUNT=16` | registry history window |
| `src/CORE/WORMS/expansion/lazy_replan.py:33/:37/:42` | `tool_failure_count=3 / max_incremental_steps=20 / state_history_keep=20` | replan shaping |
| `src/CORE/WORMS/expansion/queens.py:452` | `MAX_PROPOSALS=8` | proposal fan |
| `src/CORE/WORMS/expansion/jev_advisor.py:483` | `DEFAULT_CANDIDATE_LIMIT=12` | advisor candidates |
| `src/CORE/WORMS/expansion/mars_claims.py:116` | `DEFAULT_EXPORT_RICH_COUNT=25` | MARS export |
| `src/CORE/WORMS/expansion/silence.py:77` | `_MAX_SIGNATURES=24` | signature dedupe set |
| `src/CORE/WORMS/expansion/meta_cognition.py:1099` | `window_size=10` | anomaly detection window |
| `src/CORE/WORMS/expansion/cutting_edge_model.py:128` | `DEFAULT_TOP_K=2` | retrieval top-k |
| `src/CORE/WORMS/expansion/mesh.py:659` | `BEACONS_MAX=64` | beacon set |
| `src/CORE/local_memory.py:583` + `src/CORE/postgres_memory.py:539` | `MAX_TAGS=50` | tag cardinality cap |
| `src/CORE/config.py:189/:191/:333/:131/:177` | `max_parallel_worms=8 / max_retries=3 / keep_count=7 / half_open_max_requests=3` | runtime config consts (mirrored in azazael.yaml) |
| `src/CORE/freethreading.py:902/:904` | `max_workers=16 / min_batch_size=1` | pool sizing |
| `src/CORE/circuit_breaker.py:71` | `half_open_max_requests=3` | breaker |
| `src/CORE/hlc.py:63` | `COUNTER_DIGITS=5` | logical clock width |
| `src/CORE/inference/nim_client.py:86/:87` + `providers.py:115/:116` | `max_retries=3 / rate_limit_rpm=40/30` | inference retry/rate |
| `src/CORE/technique_wiring/_l5_dispatch.py:268` | `window=2` in `_ep438` | wired episode |

### D4 — deliberate policy (documented / overridable / exact-requirement)

- `scripts/commit_gate.py:31-32` `DEFAULT_MAX_LINES=150`, `DEFAULT_MAX_FILES=8`;
  env-overridable (`COMMIT_GATE_MAX_LINES`/`_FILES` :124-127); bypass requires the
  **exact string** `ALLOW_BULK_COMMIT=1` (:127-129) and help text (:12/:19) states the
  intent — **doc-policy, not silent cap**.
- `src/CORE/meta_evolution.py:73-74` `MAX_PATCH_FILES=1`, `MAX_PATCH_SUBSTITUTIONS=1`
  enforced as **exact requirements** (:243 "patch must modify exactly one file",
  :249 "must contain exactly one substitution" — raises, never silently trims).
- `tools/engram_supervise.py:323` `--limit 100` for plan-task search with an explicit
  comment (:331) documenting engram's 500 server cap, newest-first ordering, and the
  error direction (old supersedes below window → read as still-open = fails visibly).
- `azazael.yaml` production config: `max_parallel_worms: 8` (:43), `max_retries: 3/2`
  (:45/:56/:62/:68), `keep_count: 7` (:100), `half_open_max_requests: 3` (:34),
  `dead_letter_max: 1000` (:38), `max_size_mb_warn: 100` (:95), `max_workers: null` (:75).

### D5 — liveness / newest probes (correct as written)

`src/session_memory.py:1148/:1161` (`LIMIT 1` fetchone), plus first_party `LIMIT 1`
probes: `scripts/live_monitor.py` :100/:109/:171/:1073/:1178/:1202/:1240,
`scripts/learning_loop_temporal.py:126/:131`, `scripts/exmachina_live_monitor.py:67/:76`,
`scripts/lilith_live_monitor.py:111/:120/:202`, `scripts/track_monitor.py:73/:82/:133`,
`scripts/monitor_learning.py:133`, `src/SCRIPTS/monitor_learning.py:146`,
`src/CORE/compliance/scanner_db.py:315/:396`, `src/CORE/data_retention.py:346`,
`src/CORE/direct_memory.py:639/:770/:968/:1095`, `src/CORE/local_memory.py:2432`,
`scripts/evolution_cycle.py:565/:2377` (newest-first semantics),
`src/CORE/compliance/governance.py:537` (`add_edge.count=1` — one-time edge insert).

### D6 — id/hash prefixes (collision domains)

| prefix | size | sites | verdict |
|---|---|---|---|
| `hexdigest[:6]` | 24-bit | `METACLUSTER.py:615/:534` `orchestrate` | smallest in tree; N low — fine, flag at scale |
| `uuid7.hex[:8]` / `uuid4.hex[:8]` | 32-bit | `Agent.py:204/:273/:362/:450`, `AgentPool.py:298/:380`, `MemoryBus.py:360`, `PamsRecorder.py:146`, `PIPELINE_WORM.py:150`, `SPECULATIVE_FORK_WORM.py:137` | ~4.3e9 domain; N≤10³ fine |
| `uuid4.hex[:12]` | 48-bit | `scripts/jev_advise.py:92`, `WORMS/expansion/delegation.py:111/:114` decision IDs | fine |
| `hexdigest[:16]` | 64-bit | `WORMS/expansion/engram.py:69` `_h` (shard **placement** only, :318 `% len(ENVS)`), `consolidation.py:32`, `cutting_edge_model.py:315`, `STRIDE_VERIFIER_WORM.py:189/:287`, `evolution_cycle.py:260/:414`, telemetry | fine — distribution hash, not verdict |
| `hexdigest[:32]` | 128-bit | `close_audit_sessions.py:118/:151/:164`, `WORMZ.py:184 `_compute_checksum` | fine |
| 12-hex compare | 48-bit | `check_tree_parity.py:56-71`, `backup.py:220`, `rotate_secret config.py:165` | parity-check fine |
| `key[:16]` display | — | `mesh_trusted_key.py:138/:141/:180/:207` | display (D0) |

### D7 — verified false positives (excluded from findings)

- Tk/graphics `width=` kwargs (Combobox/Button/Label/Spinbox/create_oval/create_line/
  rectangle) across `CLUSTERWORMS.py`, `CODEX_Studio.py`, `OS_CONGRUENCY.py`,
  `CONCURRENCY.py`, `AZAZAEL_Inference_Studio.py`, `POPUP_*.py` — graphical noise.
- `re.sub(count=1)` / `re.subn(count=1)` — substitution-count semantics, not truncation
  (`CODEX_Studio.py`, `cain_fill_all_20260930.py`, `build_bcc_cain_alternate.py`,
  `make_task_xml_utf16.py`).
- Status parsing `line[:2]` (`commit_gate.py:66/:75`) — two-field split of porcelain rows.
- Text-row tokens `Windows` (`SESSION_INSIGHTS_2026-07-07.md:124`),
  `pageerror` (`ERROR_LOG.md:7673`), `MAX_JOBS=8` (`docs/TORCH_BUILD_TROUBLESHOOTING.md:47`).
- `live_monitor.py:2460` `rows = frame_lines[:max_rows]  # never exceed the visible
  window` — explicitly commented monitor window.

## LAYER 2 — gates, tools, scripts (summary)

- `tools/engram_supervise.py` — verdict detail lines capped `line[:160]`,
  first-line `[:120]/[:200]` display caps (D0); `--limit 100` documented (D4).
- `tools/wire_evidence_audit.py:253-256` — honest count + `[:10]` examples (D0).
- `tools/command_center.py:104` `evidence[:4]`, `tools/graph_rebuild.py:191`
  `report[:6]` — panel display bounds (D0).
- `tools/session_start.py:130` — **`out[:12000] + "\n... [engram context truncated]"`**
  engram memory context window with an explicit marker (H/D0 hybrid — shapes the
  agent's working memory, honestly labeled).
- `scripts/db_health.py:252` `sub:summary[:15]`, `src/CORE/WORMS/dead_letter_queue.py:474`
  `summary[:20]`, `src/memory_status.py:183` `session_data[:10]` — bounded lists;
  counts carried alongside (D0).
- `src/ERRORZ.py:523` + `src/META/ERRORZ.py:498` `report.critical_errors[:10]`,
  `:527/:502` `code_snippet[:3]` lines — display windows (D0).
- `src/CORE/NeuralPipeline.py:1071/:465/:596` — `records[:3]` / `test_records[:20]` /
  `train_records[:5]` — analysis/display windows (D0).
- `scripts/*bcc_*` analytics (`sorted(...)[:10]` etc.) — research sampling (D0).

## LAYER 3 — memory stores & persisted data (SQL verified at HEAD)

- `src/local_memory.py` → `src/CORE/local_memory.py`: inventory backfill
  `LIMIT 1000` :389; lessons-hygiene clauses `LIMIT 10` :1648/:1651 (batch #1);
  clamped store defaults above.
- `src/session_memory.py` SQL: `LIMIT 15/15/100/100/10/10` (:943,:965,:1067,:1083,
  :1103,:1109,:1183) — audit/report tails with counts+prints (D0); `LIMIT 1`
  :1148/:1161 probes (D5).
- `src/CORE/cli_memory.py`: `LIMIT ?` parametrized :70, `LIMIT 20` :99, `LIMIT 50`
  :115, CLI timeline `session_id[-24:]`-style display tails :119 (D0).
- Integrity scoring thresholds (`local_memory.py:1481-1489` size_score 15/15/12/8/4) —
  thresholds, not truncation.
- Session summaries stored per session (`print_context_banner` summary[:60] display).
- `merge_bake_lane.py` merged-record caps (D1 above) — **the only persisted-window cut
  that silences longer bodies**.

## LAYER 4 — harness channels (outside the repo tree)

- **Engram `mem_save` record truncation at `limit_bytes: 50000`** — observed in
  `mem_save` output metadata (prior session, harness-side). Bodies >50KB are cut
  server-side; memory mirrors must respect this bound.
- **opencode transcript scan** default `--limit 500` (transcript_ap5_gate.py:340/:723)
  — scan window for AP-5 audits; documented in CLI help (`:14` doc line).
- **Freebuff/claude clients** discard MCP `instructions` payload (1921 chars) —
  injection-vs-enforcement gap codified in `AGENTS.md` (verified Oct 08 2026).
- Skill-doc examples carry API examples with `limit=20/1`
  (`skills/azazael-pams-memory.md:35/:78/:110` + `.agents/skills/.../SKILL.md:35/:78/:110`
  + win-backup copies) — documentation of recall API, not production caps.
- Process-log data (`NEURAL_MESH_WIRE_OR_CUT.json:2688/:3334/:5477/:3111`,
  `models_*.json`, `continued_audit_v3.json`) — `limit: 0` rows = no-limit markers;
  `top_k=2`, `max_depth=5` recorded facts, classified as recorded data.

## Ranked worst findings (can silently shape production)

1. **`tools/merge_bake_lane.py:131` — merged bake fields cut to `title[:120]`,
   `body[:4000]`, `source[:80]`, `item_id[:80]`** with no marker and no drop row.
   Only structural fix would be size-preserving (P1 candidate).
2. **Memory-recall newest-only semantics** (`evolution_cycle:565/:2377`,
   `scheduling:623`, `learning_grpo:687`) — deliberate, but a caller expecting history
   gets one record; the "500-row alert-pool saturation" comment (:2047) already
   documents the family.
3. **`tools/mesh_function_preflight.py:1447`** `decider_evidence[:3]` — gate verdict
   provenance window (record-only; decision separate).
4. **`tools/transcript_ap5_gate.py:828/:848`** announcements `[:5]`, IDs `[:12]` —
   gate report windows (count honest).
5. **`session_start.py:130`** 12,000-char engram context — the agent's read of its own
   memory is capped (marker present).
6. **3-episode shaping consts** (`RAMPUP_WINDOW=3`, `CHRONIC_WRITE_CAP=3`,
   `MAX_EPISODES=3`, `REPROBE_LIMIT=2`) — policy-writing loop shaped at episode scale.
7. **24-bit METACLUSTER orchestrate digest[:6]** — smallest hash prefix (low-N fine).

## Designed-not-toy exemplars (honesty-tested)

- `tests/test_objectgraph_format.py:100` `test_limit_truncates_and_says_so`
- `tests/test_objectgraph_format.py:335` `test_traversal_limit_is_a_cap_and_can_return_fewer_than_it`
- `src/CORE/local_memory.py` MAX_QUERY_LIMIT clamp + warning backstop
- `tools/engram_supervise.py:331` documented window + error direction
- `scripts/live_monitor.py:2460` "never exceed the visible window"
- `scripts/evolution_cycle.py:2047` documented 500-row saturation semantics

## Artifacts & provenance

- `state/truncation_sweep_2026-10-22/py_sweep.jsonl` (6,834 rows) — Sweep A sink
- `state/truncation_sweep_2026-10-22/text_sweep.jsonl` (541 rows) — Sweep B sink
- `state/truncation_sweep_2026-10-22/py_sweep_meta.json` / `text_sweep_meta.json` —
  run metadata (HEADs, counters, miss lists, worker errors, caps)
- `state/truncation_sweep_2026-10-22/classified_findings.json` — full first_party rows,
  uncapped (single source of the tables above)
- Scanner scripts: Temp only (`truncation_sweep_a.py`, `truncation_sweep_b.py`,
  `truncation_classify.py`) — never in the repo
- Bake lane: `azazael/state/bake_harvest_laneB_2026-10-22.jsonl` rows 11-13 (this sweep)

## Pending (deferred — needs user go/no-go)

P1 consolidation ("fix to a single threshold const") from the approved roadmap was
**not started** — awaiting explicit user instruction.
