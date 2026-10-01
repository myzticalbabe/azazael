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
| OPEN | `.git`: migrate history vs fresh clone + archived bundle | — | Matters at move day only |
| OPEN | `CROSS_NATURE_ROUTER.py`: delete vs keep-as-generic | — | |
| OPEN | Home-dir sprawl in scope (U8) or separate | — | |

## Baselines (pinned, branch `migration/baseline-20261001`)

| Artifact | Value | Date |
|---|---|---|
| TERENCE `--json` | 15/15 oracles, 194 faults (1 crit, 9 high, 183 med) | 2026-10-01T14:26 |
| pytest collect | 4216 collected + 1 collection error (sentinel hook vs dill; bystander file innocent) | 2026-10-01 |
| Evolution | 0 promotions / 193 cycles; QD stagnant 70; SPRT blind 85/193; 1-state bandit | 2026-10-01 |
| PMB/PMI memory | 13+ facts this session; daemon hybrid recall verified | 2026-10-01 |

## Units

| Unit | Paths | Files | Verdict | Destination | Status |
|---|---|---|---|---|---|
| U0 substrate | worm_registry, worm_health, paths/, freethreading, direct_memory | ~5 | keep, stabilize first | canonical (unmoved until tree moves) | open |
| U1 expansion leaves | WORMS/expansion/* minus substrate | ~40 | migrate | flat dispatch, same tree | open |
| U2 expansion substrate | spine, mesh, servemesh, synapse, fabric_state | ~6 | migrate last (runtime) | flat dispatch | open |
| U3 clusters (surgery) | CLUSTERWORMS, NATURE_CLUSTERS→delete, METACLUSTER→rewrite, CROSS_NATURE_ROUTER→verdict | 4 | rip-out per D1 | categories / delete | open |
| U4 compliance | compliance/, audit_trail, sentinel, TERENCE wiring | ~15 | keep + re-verify gates | same | open |
| U5 satellites | CODEX 87, ORCHESTRATION 84, AOA 30, HYDRA 11, META 16, UTILITIES 23, ML 9, eve_unleashed 11 | ~271 | migrate per-package | `C:\Azazael\` mirror layout | open |
| U6 entry points | CLI, DAEMONS, SCRIPTS 30, INTERPRETERS, TOOLKIT, TOOLS | ~50 | migrate last | same | open |
| U7 skills | 1234 md (generator-verified families + ~50 hand-review) | 1234 | triage by family | reconciled catalog | open |
| U8 home-dir sprawl | TBD | TBD | scope decision OPEN | — | open |

## Triage rows (first entries; session debris vs keepers)

| Path | Found | Verdict | Reason |
|---|---|---|---|
| `scripts/_emoji_mood_probe.py` | 2026-09-20, pre-session | quarantine | width-model probe; keep iff monitor unit claims it |
| `src/CODEX/cain_apply_emoji_20260930.py` | 2026-09-30, pre-session | quarantine | one-shot CAIN edit; keep iff CODEX unit claims it |
| `archived_unified/` (shadow source tree) | forensic | resolve, never move | diff vs `src/`, absorb unique, delete fork |
| `archive/` junk drawer (1.03GB) | clutter policy | sort w/ manifests or delete | — |
| `var/cold/` snapshots (4.06GB) | clutter policy | keep newest 1, purge rest | regenerable |

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

## Mined history (2026-10-01 extraction; 34 decision-bearing commits)

Theme groups with hashes. Full bodies in `git show <h>`. Rule learned
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
