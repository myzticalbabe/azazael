# Board audit — freebuff lane, 18 open rows measured 2026-11-02

Same method as the JAEGER rows (board 47193–47195, see `JAEGER_BRIEF_2026-11-02.md`): restate each
row's claim **as written**, measure the tree, and either retire it or correct the premise it rests on.
A row is retired only for something the tree falsifies — delivered, duplicated, or not a task. A row
whose *figure* is stale but whose remedy is real is kept, with the figure corrected here.

Scope: the 18 claimable rows on `lane.freebuff.tasks` at the start of the audit. Rows retired were
claimed first and closed with `_board.py done <id> "<evidence>"`; rows kept were `release`d back to
`available` rather than left under a lease. Result: `stats freebuff` went `available 18, retired 380`
→ `available 12, retired 386`.

---

## 1. Retired — 6 rows, each for a measurable reason

| board | claim as written | measured 2026-11-02 | verdict |
|---|---|---|---|
| **47206** verify-replay | "make meshscene `--verify` REPLAY the operations … instead of comparing stored digests to stored digests" | **Already replays.** `meshscene.py:471-482` applies each recorded op through `OPS.apply_op` starting from `mesh.json` and compares the **recomputed** digest to the recorded one per seq (`DIGEST-DIVERGENCE` names the seq, not just the scene); `:523-535` replays `picked.json` to its own seq; `:545-552` recomputes the final digest and compares it to `browser_probe.json`. `ops.replay` is `ops.py:348`. | **duplicate of 47196.** The one thing the replay does *not* anchor — the base mesh and the field — is exactly `imp2-verify-inputs`, which is open. |
| **47200** prose-splitter | "guarded sentence splitter (abbreviations + lowercase rejoin) and `--compare` printing all twelve metrics it computes rather than five" | **Delivered.** `tools/prose_forensics.py:196 split_sentences` with `_is_abbreviation_break` and `_is_false_lowercase_join`; `show_compare` (:429) prints `METRIC_FAMILIES`. Ran it: `.prose/inaug2017.txt` vs `.prose/inaug.txt` printed `metric (12 families)` and 12 `[family]` blocks. | **delivered** |
| **47249** board-post-verb | "Add post verb to `_board.py` …" | Duplicate of 47207. Posted with `task_id = NULL`, so no id can address it. `_board.py` verbs: `max tasks status announces announce claim release done block stats store`. | **duplicate of 47207** |
| **47251** board-lease-report | "Distinguish claimed_live vs claimed_expired …" | Duplicate of 47208. `task_id = NULL`. `grep claimed_live\|claimed_expired\|churned _board.py` → 0 matches. | **duplicate of 47208** |
| **47253** gate-disk-floor | "Add disk floor to preflight_all.py …" | Duplicate of 47210. `task_id = NULL`. `grep shutil.disk_usage tools/preflight_all.py` → 0 matches. | **duplicate of 47210** |
| **47306** SHARDEX-HYPEREDGE-VISION | "Vision doc written … 6 build tasks already pushed" | Not a task: it describes work already done and rows already posted. The rows it names (47294/47296/47298/47304, plus P2P/COMMUNITY) are in the queue themselves. The doc it cites is canon. | **not a task** |

## 2. Kept — 12 rows, 4 with a corrected premise

| board | premise status | measured |
|---|---|---|
| **47187** industry-standards | **valid** | Sequenced by design ("AFTER the next startup"). `docs/SUBAGENT_GUARDS_2026-11-02.md` exists, so its baseline includes the guard inventory it names. |
| **47196** imp2-verify-inputs | **valid, confirmed open** | `meshscene.verify` reads `field.json` for `sine_q15` and `mesh.json` as its base, and never compares either to the `field_sha256` embedded in the scene HTML (`:400`) or to a page-reported base digest. `browser_probe.json` is checked for `mesh_digest` only (`:544-552`). Consistently edited inputs still verify. |
| **47199** djt-iea-rederive | **premise stale, remedy real** | `docs/DJT_PROSE_AUDIT_2026-11-02.md:371-375` already carries the claim at **tier C/P** and states the report body was not fetched and "the numbers should be re-derived from the PDF before any official use". So the row's stated defect — "a figure … that reads as measured" — is **already fixed by labelling**. What remains is the re-derivation itself, which is real work, not a label. |
| **47201** corpus-2015-arm | **valid** | `.prose/` holds `inaug.txt`, `inaug2017.txt`, `inaugural_2017.json`, `inaugural_2025.json`, `message_2025.json`, `msg.txt`. No 2015 text. |
| **47207** board-post-verb | **valid** | `_board.py` dispatches `max/tasks/status/announces/announce/claim/release/done/block/stats/store`. No `post`. |
| **47208** board-lease-report | **remedy valid, its measurement stale** | The row reports "24 rows at `state='claimed'`, oldest 753 min, 46834 at `attempts=3`". Measured now: `stats freebuff` → `claimed 0`. The missing fields are real (`claimed_live`/`claimed_expired` absent from `_board.py`), but the 24-row figure must not be quoted again — re-measure at the time of the fix. |
| **47209** git-hook-tiers | **valid** | `.githooks/pre-commit` is 667 lines and still runs the evidence gates inline (`canon_drift`, `unresolved_ratchet`, `bible_check`, `platform_claims`, `mesh_function_preflight`, `wire_evidence_audit`, `failure_evidence_gate`, `metthew_families`, `at_risk_register`, `paradigm_gate`, `preflight_all`). `.githooks/pre-push` (65 lines) carries only bible injection and the merge gate. No split exists. |
| **47210** gate-disk-floor | **valid** | `tools/preflight_all.py` has no `shutil.disk_usage` and no free-space threshold. |
| **47294** SHARDEX-L4-RANKING | **partly stale — the hash plumbing it asks for exists** | `launch.py:85-116 create_bracket`, `:119-145 run_round` (golden hash per entry), `:147-177 verify_result` (recomputes), `:179-197 spectator_view` are all built and self-tested. What is **not** built: no winner, no advancement between rounds, and `--format round-robin` is stored in `Bracket.format` and never read — the switch changes nothing. The row's remaining work is ranking/advancement plus a real round-robin, not `rank.py` from scratch. |
| **47296** SHARDEX-L4-SIGNING | **valid, and the tree currently overstates it** | No `ed25519`/`Ed25519`/`sign_result` anywhere in `Project_SHARDEX/*.py`; no key material. `run_round` computes `result_sha256` — a **hash**, not a signature — and `launch.py:229` prints `PASS L4 run_round (4 results, all signed)`. That line is a false claim in output; it is the reason this row matters. |
| **47298** SHARDEX-L4-MULTISHARD | **valid** | `grep "def compose" Project_SHARDEX/ops.py` → none; `ops.py` functions are `sine_table, lcg, validate, op_id, chain_hash, mesh_stream, mesh_digest, apply_op, replay`. No composition hash. |
| **47304** SHARDEX-BROWSER-PLAY | **mostly delivered; one clause unmet** | `shardex.py --forge` writes `flame.html` from an inline template (`_FLAME_HTML`) with **no** external `src=`/`href=`/`https://` in the whole file, computes the golden hash in-browser (`fnv1a64`, agreement stated at `shardex.py:24`), and binds `keydown`/`keyup` at `:643-646`. The unmet clause is **"mutations via clicks"** — there is no pointer/touch handler. Kept narrowed to that clause; the "zero install, self-contained, client-side golden hash" part needs no further work. |

## 3. What this audit does not claim

- It measured **premises**, not code quality. A kept row is open, not correct.
- The two `task_id = NULL` triples were retired as duplicates *of the addressable row*, not as wrong —
  their content is identical, so no work is lost. `_board.py` has no `post` verb, which is why those
  rows exist in that shape (47207).
- Retirement is reversible in the store (`archived`/`done` states are retained); nothing was deleted.

## 4. Follow-on work this audit surfaced

1. **`launch.py:229` printed "all signed" for unsigned hashes** — a guard-shaped line asserting a
   property the code did not have. **CLOSED same day** in `b2b8f989`: each result now carries an
   ed25519 signature over `result_sha256` with the author's pubkey, verification refuses when the
   primitive is absent, and `SHARDEX_TRUSTED_PUBKEYS` pins who counts. The selftest line is now
   earned (`11 checks OK`, including a signature lifted from another result, a broken signature and
   an untrusted signer), and the private key lives outside the tree (`SHARDEX_KEY_DIR`, default
   `~/.shardex`) so a clone cannot forge. Board 47296 remains open until a second lane re-derives it.
2. **`--format round-robin` is a switch nothing reads** — accepted, stored, ignored. That is a silent
   no-op of the same class as a `--verify` that does not verify. Pushed to kilo as
   `kilo-round-robin-noop` (delivery row 47388) rather than fixed here, because it needs a test that
   fails on the current code and passes after.
3. **47208's figure (24 claimed rows) is no longer true** — do not carry it into the fix.
4. **`_board.py` cannot post a status as any lane but `opencode`** — the module constructs
   `LaneMessageBoard(lane="opencode")` at import (`_board.py:52`), and `post_status(status, detail)`
   derives its topic from that lane. So `_board.board.post_status("freebuff", msg)` writes to
   `lane.opencode.status` with `"lane": "opencode"` — measured today: it landed as row **47382**, the
   wrong topic, and a freebuff reader sees nothing. The canon requires every work unit to end with a
   `lane.<lane>.status` row, and the only CLI that can write one writes it for opencode. Correct write
   is `LaneMessageBoard(lane="freebuff").post_status(...)` (row **47383**, read back). This is the same
   gap as 47207 from the other side: the CLI can retire work in any lane and can post work in none.
