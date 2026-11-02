# Restart handoff — 2026-11-02

Written for the next session. **HEAD at handoff is the commit containing this file; its parent is
`7a6a2da3`.** Five commits landed today, in order:

| commit | what it did |
| --- | --- |
| `a876c781` | pick-driven live mutation (`touch` op, `picked.json`, `PICK-UNPROVENANCED`), the bible dossier quoting the 1987 TNG guide, the DJT prose audit, the subagent-guard audit |
| `0dbd384` | the AI→SI decree inside the bible, with the cost-benefit, harm assessment and 10-measure pathway |
| `ed96f5fe` | improvement pass: pick coverage hole closed, unreadable-record refusals, prose negative control, instrument band disclosed |
| `7a6a2da3` | checks-and-balances gap analysis + state policy comparison |
| *(this)* | `.gitignore` for the scratch dirs, this handoff |

## State that can be trusted

- `Project_SHARDEX/tests/test_mesh_live.py` — **14 pass**; `tests/test_prose_forensics.py` — **6 pass**.
- `python Project_SHARDEX/meshscene.py --verify .live_pick` → **VERIFIED**, chain
  `69da083da4268ec8`, final mesh `110df7ea0bb30364` (`.live_pick` is gitignored but present locally).
- `tools/preflight_all.py` → **24 of 25 PASS**; the one FAIL is `transcript-ap5`, which reports two
  historical "Want me to…" lines in another session's stored transcript. Not introduced by this
  work and not blocking — leave it visible rather than suppress it.
- Board: row **47187** (`industry_standards_analysis`) is deliberately **pending** — it must run
  *after* startup so it measures the post-session tree. Row 47189/47190 are announcements.

## Open items, in the order I would take them

1. **IMP-2 — `--verify` still trusts its inputs.** `mesh.json`, `field.json` and
   `applied_ops.jsonl` could be edited consistently and verify would pass. Fix: have the page report
   the **base** digest and the field sha256 into `browser_probe.json`, and require both to match.
   This is the same defect class as the pick hole, one level up.
2. **G1/G2** — the claim trailer (`Task: Board-<n>`) and the receipt (`command`, `exit_code`,
   `stdout_sha256`). `docs/SUBAGENT_GUARDS_2026-11-02.md` §4 specifies both; G2 is ~40 lines and is
   the cheapest real gain in the tree.
3. **Board 47187** — industry-standards analysis against a captured baseline (NIST AI RMF/SSDF,
   ISO 42001/25010, SLSA+SBOM+Scorecard, OWASP ASVS, WCAG 2.2, DORA). Every cell carries a receipt;
   unmeasured cells report UNRUN.
4. **IEA figures** — §7 of the DJT audit carries 415 TWh (2024) / 945 TWh (2030) as tier **C/P**;
   the report body was never fetched. Re-derive from the PDF before any official use.
5. **Prose instrument** — guarded sentence splitter (abbreviations + lowercase rejoin) and a
   `--compare` that prints all twelve metrics it computes instead of five.
6. **Corpus arm 2** — the 2015 announcement. Time returns **406**; `presidency.ucsb.edu` served the
   campaign release fine, so use the APP spoken-address archive.

## First commands at startup (canon order — do not skip)

```bash
python C:/Azazael/azazael/tools/mcp_startup_gate.py --fix
python C:/Azazael/azazael/tools/session_start.py "<the task>"
# then supervisor__verdict through the MCP tool
python C:/Users/clint/_board.py claim freebuff 10     # the queue is the work queue
```

## Scratch directories, now ignored

`/.live/`, `/.live_pick/`, `/.prose/`, `/.transub/`, `/.tmp_mirror/` are in `.gitignore` as of this
commit. `.live_pick/` is **94 MB** and holds `frames/` (120 PNGs) plus `mesh_pick.mp4`; the frames
are regenerable from the committed source, and the *evidence* is `applied_ops.jsonl` +
`picked.json` + `mesh.json` + the digests quoted in commit `a876c781`, not the video. If disk
pressure matters (this box runs near 98%), `rm -rf .live_pick/frames .live/frames` is safe and
reversible by re-running capture — **but re-run `--forge` first**, because the page in those
directories was generated before the `touch` operator existed.

## One caution for the next session

The worktree carries ~200 pre-existing modifications from other lanes (workflows, baseline JSONs,
platform docs). **Do not `git add -A`.** Stage by path, and if a commit needs a bulk override,
declare `ALLOW_BULK_COMMIT=1` in the message as the two commits today did.
