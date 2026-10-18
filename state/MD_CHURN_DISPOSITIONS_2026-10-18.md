# MD Churn Dispositions — 2026-10-18 (coordinator)

Rebuilt the manifest from HEAD (`git ls-files *.md`, read-only sweep in
`/tmp/md_manifest.py`, 24 workers on 3.15t): **3454 tracked md rows,
17.7 MB, 1927 unique shas, 1410 dup groups, 1527 extra copies,
261 live-unique** after excluding archive/skills/graphify/BIBL trees
(`/tmp/md_manifest.jsonl`, `/tmp/md_live_shortlist.jsonl`; scratch, not committed).

## Dispositions (explicit, per goal)

| Class | Groups | Extra copies | Disposition |
|---|---|---|---|
| skill-mirror (`.agents/skills`, `skills/`, `skills.win-backup`) | 1252 | 1304 | **LEAVE** — per-tree agent-local by design; expected to diverge (Oct-18 mirror adjudication: 116 skill pairs). |
| mirror-tree (`archive/`, coord mirrors) | 155 | 220 | **LEAVE in tree; ARCHIVE candidates** for the G:\ pass (historical copies, not live docs). |
| in-repo-dup | 3 | 3 | **LEAVE** — see below. |

## In-repo dups (all 3 examined, none removed)

1. `archive/restored/Libra/README.md` == `archive/restored/Libra_Desktop/README.md` — archive tree, historical. Leave.
2. `src/CODEX/SESSION_TEMPLATE/README.md` == `.../SESSION_TEMPLATE/README.md` (nested) — the nested tree is referenced by data evidence (`tools/_e880_triage.json` names `SESSION_TEMPLATE/SESSION_TEMPLATE/data/failure_data.json`; 309 files / 37 MB subtree). Removing md leaves while the referencing data stays would break evidence paths for KBs of savings. Leave.
3. Same nested pair under `documentation/` — same rationale. Leave.

## Comparable subset

261 live-unique md files = the comparable subset, inventoried in
`/tmp/md_live_shortlist.jsonl`. No content edits made in this pass:
df65123a already corrected 24 stale doc claims; remaining staleness
corrections belong to owning lanes per brief.

## Explicitly NOT done

Mass deletion of duplicate copies. The measurable C: pressure (98% full)
is not md files (17.7 MB total) — it is build/venv/desktop weight, handled
by the archive pass. Deleting 1527 extra copies saves megabytes and risks
breaking per-tree skill isolation. If a future pass wants it: start from
`/tmp/md_manifest.jsonl` (regenerate — /tmp is ephemeral).
