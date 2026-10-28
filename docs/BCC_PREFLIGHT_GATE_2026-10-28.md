# BCC Pre-Flight Gate (2026-10-28) — clear before ANY further work

Operator finding: the gap-engineering architecture is built but not yet jointly
visible — lanes are working from different states. No new edge/proof/store work
until every item below is checked. Each lane confirms on the message board.

## Landed state (what "same page" means)
| Artifact | Location | State |
|---|---|---|
| Azazael worktree | `75b6d4fb` | committed (138 files) |
| Proof layer (120 edges) | home repo `7482178` `.bcc_audit/` | committed, tally verified 50 / lead 69 / cut 1 |
| Gap stores | tracked 62 / enriched 66, enriched superset, no drift | writer roles in script banners |
| Manifests | `00_raw/SHA256SUMS` 202/202 green; research scope note; `cosmos_snapshot_2026-10-28/` | verified |
| Verifier | FAIL only on 82 redaction timestamps | known-lane-keys item |

## Pre-flight checklist
- [ ] **P1 — Same commit**: each lane reports `git log --oneline -1` for azazael
      (expect `75b6d4fb`) and home repo `.bcc_audit` (expect `7482178`).
- [ ] **P2 — Reinstruction read**: each lane confirms reading BEAM_AGENTS.md
      standing reinstruction + REDO memo §§7–8 + ladder memo.
- [ ] **P3 — Writer audit**: the concurrent `selenium_status` writes to
      `scripts/bcc_gap_index.json` (seen 2026-10-28, uncommitted) must conform
      to the field-update role or be blessed in the banner. No new writers.
- [ ] **P4 — Store sync**: re-run tracked-vs-enriched consistency (expect 62/66,
      enriched superset, no drift).
- [ ] **P5 — Verifier baseline**: confirm FAIL scope = 82 redaction timestamps
      only; no new violations.
- [ ] **P6 — Queue ownership**: 59/81 UNPROOFED, 79 quote repair, DOS re-source
      (KILO-DOS-RESOURCE-2026-10-28), 82 redaction keys — each has a named owner.
- [ ] **P7 — BEAM_AGENTS.md commit decision**: operator decides include/leave.
- [ ] **P8 — Record-first**: every lane demonstrates one Engram mem_save +
      PMB record_batch/outcome on its next action before doing proof work.
- [ ] **P9 — Memory live-fire** (operator 2026-10-28): every lane proves it can
      operate the memory loop before proof work — (0) reachability: if memory
      MCP tools are unreachable from the lane's session, report ENVIRONMENT-FAIL
      (fix the path, not the lane); (1) close one surfaced lesson via
      `mark_lesson_followed` + note; (2) `update_goal` progress on one real owned
      goal; (3) one cross-project `mem_search` (`all_projects=true`). The
      coordinator verifies the three rows exist — attestation without rows is not
      a check. Each lane's P1–P9 confirmation is itself a PMB goal closed with
      `done` (dogfood the mandate).

## Rule
Pre-flight first. Any proof/store/edge commit before P1–P9 all check is out of
sequence — the board task FREEBUFF-PREFLIGHT-2026-10-28 tracks it.
