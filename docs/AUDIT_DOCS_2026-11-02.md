# AUDIT — docs/ publish suitability (2026-11-02)

Auditor 18 of 18, FULL AUDIT fan-out. **Read-only**: no file in `docs/` was modified by this
audit, and nothing was executed.

## Coverage, stated before any conclusion

- **Listed**: the whole `docs/` inventory (files plus 14 subdirectories).
- **Read**: 6 files — `BCC_PREFLIGHT_GATE_2026-10-28.md`, `CHAIN_OF_INFORMATION.txt` (truncated at
  ~18.5k tokens), `WSL_DIAGNOSTIC.md` (first 35 of 81 lines), `SECURITY_AUDIT_CHECKLIST.md`
  (first 60 lines), `docs/README.md` (first 35 of 65 lines), plus directory listings of
  `docs/audit/` and `docs/societal/`.
- **Subdirectories opened**: 2 of 14.
- So this is roughly **5% of files read, 14% of directories opened**. Everything below is
  evidence-backed; anything not read is marked UNKNOWN rather than assumed clean.

Instrument note: `code_search` and `glob` have been returning 0 with exit code 2 in parts of this
tree during this session even where matches exist. No "not found" claim below rests on either tool.

---

## Findings

| File | Concern | Would ship? | Action |
|---|---|---|---|
| `BCC_PREFLIGHT_GATE_2026-10-28.md` | **BCC investigation operations inside the codebase's docs.** Names the `.bcc_audit` proof layer ("120 edges"), a "home repo `7482178`", "82 redaction timestamps", "59/81 UNPROOFED", DOS re-sourcing, lane confirmation protocol, and cites commits `75b6d4fb` / `7482178`. | **NO** | **EXCLUDE.** This is the same contamination class as root-level `PEOPLE_DOSSIER.html`: investigation workspace in a project tree. Highest-severity finding in this audit. |
| `SECURITY_AUDIT_CHECKLIST.md` | 17 checks, **0 passed, 0 failed, 17 N/A** (its own summary table). A blank form presented as a security audit. | **NO** | **EXCLUDE, or finish it.** Publishing an all-N/A checklist invites a reader to infer coverage that does not exist. |
| `CHAIN_OF_INFORMATION.txt` | ~18.5k tokens of ASCII flow diagrams describing the author's manual workflow; references `/My Passport/` as an external backup and `~/Documents/AZAZAEL_BOOT/`. No PII seen in the portion read. | **NO** | **EXCLUDE.** Large, zero public value, describes a private process. |
| `WSL_DIAGNOSTIC.md` | Machine-absolute paths `C:\Azazael\.venvs\py315t` and `C:\Azazael\.venvs\py314m`; environment-specific. Also **internally contradictory**: the header declares 3.14 retired while the body documents 3.14t as the live WSL runtime. | **NO as-is** | **EXCLUDE or sanitize.** If kept, fix the contradiction first — a doc that contradicts itself is worse than no doc. |
| `docs/README.md` | Named "Azazael Documentation Index" but **last updated June 4, 2026**. Links to `specs/GOSP-specification.md`; there is **no `specs/` directory** in `docs/` (directories are agent_orders, architecture, archive, audit, bible, graphify-out, icons, METTHEW, platforms, scripts, societal, transubstantiation, _shard01_frames). So the index ships with a **dangling link**. | PARTLY | **Regenerate before ship.** It cannot serve as a public index in this state. |
| `YGGDRASIL_3D_BLOOM_2026-10-31.mp4`, `YGGDRASIL_SHARD_01_WORMS.mp4`, `_shard01_check.png`, `_shard01_guardian_check.png`, `_shard01_guardian_fixed.png`, `_shard01_guardian_fixed2.png`, `_shard01_frames/` | Binary media committed inside a documentation directory. | **NO** | **EXCLUDE from a code publish** (or move to releases). Video in a docs tree inflates the clone for every reader. |
| `docs/audit/backlog_triage.json`, `docs/audit/AST_AUDIT_ALL_ENVIRONMENTS_2026-11-01.md`, `docs/audit/ast_audit_2026-11-01/` | Internal audit output that enumerates named environments. | **NO** | **EXCLUDE.** |
| `docs/societal/PROBLEMS_2026-11-01.md`, `docs/societal/tasks.json` | Societal problem statements and a task list. **Not read** — could reference real people or organisations as data. | **UNKNOWN** | **Read before any ship.** Do not assume clean. |
| `docs/agent_orders/*`, `MANDATE_PROVENANCE.md` | Canon and lane protocol. A sibling audit found `agent_orders/03_lane_queue.md:15-16` **teaches `C:/Users/clint/_board.py` to every lane**, i.e. it encodes the username and a private workflow. | **NO** | **EXCLUDE or sanitize.** |
| The 2026-11-02 working set: `PUBLISH_READINESS_2026-11-02.md`, `HISTORY_STRIP_PLAN_2026-11-02.md`, `COMMIT_SLICES_2026-11-02.md`, `SUBAGENT_GUARDS_2026-11-02.md`, `DISPATCH_DEEPSEEK_2026-11-02.md`, `OSS_CONTRIBUTION_2026-11-02.md`, `CHECKS_AND_BALANCES_GAP_2026-11-02.md`, `STATE_POLICY_COMPARISON_2026-11-02.md`, `DJT_PROSE_AUDIT_2026-11-02.md`, and this audit with its siblings | Session artefacts written today. Several **name live security defects and unpublished weaknesses**; `SECURITY_AUDIT_CHECKLIST.md` above shows the same shape. | **NO** | **EXCLUDE.** One-day-old internal working documents. |
| `docs/bible/`, `docs/platforms/`, `docs/architecture/`, `GLOSSARY.md`, `API_REFERENCE.md`, `AZAZAEL_TREE_OF_LIFE.md` | The plausible public-facing set. Examined only as names and directory listings. | **LIKELY YES** | **Review individually.** `INSTALL_GUIDE*.md` in particular should be checked for absolute paths before it is quoted as a working install. |

---

## What a public reader needs that is absent

1. **No `LICENSE`.** Neither the repo root nor `docs/` holds one (an earlier audit in this session
   confirmed `LICENSE*` resolves to zero files). The owner has decided Apache-2.0; the file is
   still missing.
2. **No `SECURITY.md`.** `SECURITY_AUDIT_CHECKLIST.md` is a blank self-audit form, not a
   vulnerability-disclosure policy, and it would be wrong to offer it as one.
3. **No current index.** `docs/README.md` is five months stale and carries a dangling `specs/` link.
4. **No per-project documentation here.** The six publishable projects each need their own README
   and index **inside their own repo**. `docs/` belongs to the monorepo, which is not being
   published, so nothing in it follows the projects into their repositories.
5. **`CONTRIBUTING.md` and `BUILD.md` exist at the repo root**, not in `docs/`; a published
   standalone project gets neither unless it is copied in.

---

## Verdict

**`docs/` must not be published as a directory.** It is a working archive: it holds BCC
investigation operations, an all-N/A security form, 18,000 tokens of ASCII process diagramming,
committed video, and a one-day-old pile of internal notes that name live defects.

Publishing is a **per-document selection**, not a directory copy. The safe procedure is to start
from each project's own tree and add only documents that describe that project's behaviour to a
stranger. Anything that describes the operator's workflow, the investigation, or a defect stays in
the monorepo.

Two items need a human read before they can be cleared at all: `docs/societal/` and the
`docs/platforms/` install path — this audit did not read them and will not call them clean.
