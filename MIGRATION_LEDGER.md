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
