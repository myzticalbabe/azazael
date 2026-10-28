# Protocol Index (2026-10-28) — every binding protocol, one page

Derived by reading the sources, not by memory. Line refs are to the source files as of this date.

## 1. Canon precedence (which doc wins a conflict)

1. Operator's live words > everything.
2. Kali `AGENTS.md` = BCC canon (v1.3). Kilo `AGENTS.md`/`BEAM_AGENTS.md` are **lane briefs, not canon** (kilo AGENTS §Canon sync; BEAM §Shared rulebook mirrors Kali).
3. Superseded sections stay in place **history-labeled** (BEAM §Beam1 Verdict pattern), never silently deleted.
4. Azazael `MANDATES.md` + `SOP.md` govern azazael-tree execution; BCC-lane rules govern BCC content.

## 2. BCC lane (Kali canon)

| Protocol | Source | One line |
|---|---|---|
| Lanes (BEAM1/1.0/12 + freebuff) + acceptance gates | Kali AGENTS §1 | Lanes own disjoint edge ranges; acceptance runs before commit |
| Flock taxonomy (canonical, one per edge) | Kali AGENTS §2 | GOVERN/CLINIC/SITE/LEAD/CUT etc; every edge gets exactly one |
| Sources ultra-loose, tiers decide grade | Kali AGENTS §3 | Any lawful source counts; tier (A/B/C/D) sets grade ceiling |
| Proof standard: 4 tests or lead/cut | Kali AGENTS §4 | VERIFIED needs quote+sha+url+identity keys; else lead/cut |
| P1–P8 faulty-premise set + P9 memory live-fire | Kali AGENTS §5 + gate doc | P1-P8 redo premises; P9 = drill verified by `tools/verify_p9_drill.py` |
| Field notes (binding precedents 2026-10-24) | Kali AGENTS §6 | Extend, never contradict §§1–5 |
| META LEVELS canon (user-decreed 2026-10-27) | Kali AGENTS §7 | Full text in `02_analysis/findings/META_LEVELS_CANON_2026-10-27.md` |
| Memory loop §8 (binding, forensic 2026-10-28) | Kali AGENTS §8 | Read-back mandatory: start-with-memory, close every lesson + goal |
| Clean-room (fresh investigation, non-taint) | `PROTOCOL.md` | No grep-old-first; vendored tooling, never shared live code |
| Commit discipline from first commit | `PROTOCOL.md` §Commit | Small focused commits, gates green before land |
| Pre-flight gate P1–P9 | `docs/BCC_PREFLIGHT_GATE_2026-10-28.md` | No new work until P1–P9 clear; coordinator re-derives P9 rows |
| Stuck edges: one best next-upgrade step | Lane convention | Name the single next step per stuck edge, don't sprawl |

## 3. Azazael execution (MANDATES.md / SOP.md)

Gates (run before the work, not after): 0C Sentinel, 0J/0S pre-action gate + banner, 0Z-C destructive-basher gate, 0T/0T-A/0T-B verifiable truth + VLP 15-layer stack, 0B-E claim-must-not-exceed-evidence (`tools/claim_guard.py`).

Quality: 0A verify-before-claim, 0B literal obedience, 0N runtime truth only, 0Z-K live-proof (no theater), 0Z-M defect-class → gate coverage, 0H/0H-A anti-pattern recording (runtime scans only).

Flow: 0F session startup (`tools/session_start.py` loads, `tools/engram_supervise.py` enforces), 0E/0E-1 10-phase protocol, 0G/0Z/0Z-A/0Z-F/0Z-L/0M/0W agent use + parallel sweep, 0Q/0Q-A post-phase inference check, 0L stop-and-spawn on test failure, 0V reviewer pre/post, 0J-A gated str_replace, 0P priority chain, 0U reminder compliance.

Hygiene: 0R + 0R-A skills sync (≤5s), 0Z-J no old cycles, 0Z-G no busy work, 0Z-B eleven followups, 0Z-I `providers.py` for inference, 0X/0Y compliance infra + multi-agent governance, 0K reading order, 0I batch-script governance, 0D quota-jail failover.

Dirty multi-lane commits (surface 5293): never `--no-verify`, never re-baseline another lane; `git worktree add --detach HEAD`, export staged diff, `git apply --index`, pre-run `tools/anti_pattern_gate.py --check`, commit from worktree.

## 4. Memory protocol (all lanes, forensic 2026-10-28)

Loop dies on the reader side, so: start-with-memory (`prepare`/`recall`), `find_lessons` channel only (recall/fanout surfaces hit the PMB false-OK defect — `mark_lesson_followed` returns ok, writes nothing), mark one lesson per task, close/update goals (282 orphans and counting), `all_projects=true` for cross-tree Engram search, record outcome twice (Engram save + PMB outbox). P9 drill verified mechanically: `python tools/verify_p9_drill.py --lane L --since EPOCH --source find_lessons --goal ULID --search Q --expect-id N` → exits 0 PASS / 1 FAIL / 2 ENVIRONMENT.

## 5. Media protocol (CAIN Standard, LESSONS #02/#77/#78/#79 + `src/CODEX/record_session_cain.js`)

Puppeteer, never PIL, for animation-rich HTML. Standard scroll: **5.0 WPS** (`WORDS_PER_SECOND`, 30.0 fast variant), 1920×1080 @30fps rAF, 3s bottom hold, recorder CRF 26 / medium / yuv420p / 800kbps; post speed-up 2.5x via `setpts=0.4*PTS` only if requested. `file://` constraint (#74): inline critical CSS, bundle fonts/JS locally — CDN `@import` fails offline. Outputs: HTML twins versioned (`docs/`), MP4s unversioned (`*.mp4` gitignored, no LFS — Desktop/precedent locations only). Duration is derived (`words/5.0`), never a round-number guess.

## 6. File protocol

Desktop is not a repo: no deliverable lives only on Desktop (violates #58 git mandate + RULE 0T). Canonical artifacts twin into the executing versioned tree (`state/BRIEF_*` pattern, surface 5280); re-verify every brief path against the live tree before executing (surface 5285); `git check-ignore -v` from the git root before claiming ignore-status (surface 5279); regenerating an instrument does not regenerate its outputs — re-run reports in the same session (surface 5286).

## 7. Known fractures (indexed, not hidden)

- PMB `mark_lesson_followed` false-OK on recall/fanout surfaces (repro surface 5267; drill scoped to `find_lessons`).
- 2 mesh tests red on HEAD (PF16 flat-token hole in probe-core; recorded for mesh owner).
- `record_session_cain.js` hardcodes `C:/Users/clint/azazael/...` + Desktop output — stale/mixed roots; migrate to unified `media/` tree paths.
- edge0 defects (2026-10-28 forensic): `quote_basis:verbatim` is false (assembled digest, not a raw substring; raw has `&amp;`), `url` empty on a tier-A verified (the BEAM1 poster-child defect in new clothes), window `…..open` despite Jun-2024 turnover-dating premise. Next upgrade: fetch real ProPublica URL for the FY2025 XML, window = return period, fix basis label.
