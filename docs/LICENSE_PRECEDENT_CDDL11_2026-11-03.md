# Precedent — CDDL-1.1 licensing ruling (2026-11-03)

**Precedential ruling:** commit `b49dfc2fef0178d1984437de577bfa00de8a4c32`
("license: unify 4 projects under CDDL-1.1"), 2026-11-03 09:49:33 -0500,
author `myzticalbabe <clintonoxford47@gmail.com>` — the working repo's own
committer authorship. **This commit is the ruling everything else in this file
cites.** Verified gratis:

```
git show --stat b49dfc2f
# 4 files changed, 523 insertions(+), 804 deletions(-)
# Project_FLAME/LICENSE, Project_FLAMING_SWORD/LICENSE,
# Project_Nurse_Ratchet/LICENSE, Project_SHARDEX/LICENSE
```

**Rationale stated in the ruling itself:** "CDDL-1.1 provides explicit patent
grants and source code distribution obligations suitable for the
component-based architecture of these sub-projects. Sun Microsystems, Inc. is
the initial license steward. Portions Copyright 2026 Azazael Contributors."

**Citation rule going forward:** any license dispute anywhere in this tree is
resolved in one sentence — *"The ruling is b49dfc2fef0178d1984437de577bfa00de8a4c32
(2026-11-03): each Project carries the full, unmodified CDDL-1.1 text in its own
LICENSE; see docs/LICENSE_PRECEDENT_CDDL11_2026-11-03.md and the project's NOTICE."*

---

## 1. The ruling's sense, traced to "yaeger" (Project_JAEGER)

The user's request named "yaeger licence cddl-1.1 precedential ruling". The
ruling's own tree keeps the JAEGER package precedent at its head:

| # | Opinion (judge record) | Position | Where |
|---|---|---|---|
| O1 | Project_JAEGER README, § License, line 188: `CDDL-1.1 — see \`LICENSE\`.` | **pro-CDDL, on-disk ruling text** | harvest `project-jaeger-readme-md-L186` (bible/harvest.json:6718-6720; the file line is 188, the harvest id records the pre-shift line) |
| O2 | Project_JAEGER CHANGELOG line 35: "Changed from Apache-2.0 to **CDDL-1.1**" | **pro-CDDL, public change log** | `Project_JAEGER/CHANGELOG.md:33-35` |
| O3 | The ruling itself: 4 Projects flattened to one unified CDDL text in one commit | **operative** | `git show --stat b49dfc2f` (read back above) |
| O4 | Auditor 14 of 18 (2026-11-02), `docs/AUDIT_LICENSING_2026-11-02.md`: "every LICENSE is the complete, unmodified Apache License 2.0" | **opinion now superseded** — true when read (2026-11-02), false from 2026-11-03 09:49 onward | recorded here as the prior state, not as a defect |

O4 stays in the record with its date attached: the audit was correct
for its reading date, and the ruling came after it. Nothing in the audit
scanned for "shortened or reworded Apache", and no such defect exists — the
change went the other way, wholesale, with each project's full text replaced.

---

## 2. Every opinion the judge's records carry on licensing

From `docs/bible/harvest.json` (the bible's decision record, the system's
"judge" for opinions):

| Surface | Panel record | Belief held |
|---|---|---|
| `Project_JAEGER/README.md:188` | `harvest.json:6719` `project-jaeger-readme-md-L186` | CDDL-1.1 — see `LICENSE`. |
| `Project_JAEGER/CHANGELOG.md:35` | (line, no harvest id) | changed from Apache-2.0 to CDDL-1.1 |
| `Project_ELIZA/README.md:284` | `harvest.json:6268-6313` family | Apache-2.0 — **stale, resolved in this commit** |
| `Project_CRADLE/README.md:44` | `harvest.json:6423-6455` family | Apache-2.0 — **stale, resolved in this commit** |
| `Project_SHARDEX/README.md:36` | `harvest.json:6725-6753` | Apache-2.0 — **stale, resolved in this commit** |
| `Project_Nurse_Ratchet/README.md:252` | `harvest.json:6236-6268` family | Apache-2.0 — **stale, resolved in this commit** |

Each of the five stale opinions above is now corrected on disk to the ruling
text with a citation to this file, and the files carrying them are in the same
commit as this document.

---

## 3. The disputes — enumerated, resolved, each carrying the citation

All 16 stale Apache references found by `grep -n -i apache` across the seven
Projects (all measured 2026-11-03 before this commit), now reworded and cited
to the ruling:

| File | Site | Dispute | Resolution in this commit |
|---|---|---|---|
| `Project_ELIZA/README.md` | 284 | "Licensed Apache-2.0" | "Licensed CDDL-1.1; see `NOTICE` for attribution." |
| `Project_ELIZA/NOTICE` | 4 | Apache license statement | CDDL statement + ruling citation line |
| `Project_ELIZA/CITATION.cff` | 6 | `license: Apache-2.0` | `license: CDDL-1.1` |
| `Project_ELIZA/pyproject.toml` | 11, 21 | Apache text + classifier | `text = "CDDL-1.1"`; wrong classifier removed |
| `Project_CRADLE/README.md` | 44 | "Apache-2.0. See LICENSE…" | "CDDL-1.1. See [LICENSE] and [NOTICE]." |
| `Project_CRADLE/NOTICE` | 4, 25 | Apache statement; wrongly licenses FLAMING_SWORD as Apache separately | CDDL + citation; sibling named as under the same ruling (its own NOTICE governs) |
| `Project_CRADLE/pyproject.toml` | 13, 26 | Apache + classifier | as above |
| `Project_SHARDEX/README.md` | 36 | "Apache-2.0. See LICENSE…" | CDDL wording |
| `Project_SHARDEX/NOTICE` | 4 | Apache statement | CDDL + citation |
| `Project_SHARDEX/pyproject.toml` | 12, 25 | Apache + classifier | as above |
| `Project_FLAMING_SWORD/NOTICE` | 4 | Apache statement | CDDL + citation |
| `Project_FLAMING_SWORD/pyproject.toml` | 11, 22 | Apache + classifier | as above |
| `Project_FLAME/NOTICE` | 4 | Apache statement | CDDL + citation |
| `Project_FLAME/pyproject.toml` | 11, 22 | Apache + classifier | as above |
| `Project_Nurse_Ratchet/README.md` | 252 | "Licensed Apache-2.0" | CDDL wording |
| `Project_Nurse_Ratchet/NOTICE` | 4 | Apache statement | CDDL + citation |
| `Project_Nurse_Ratchet/CITATION.cff` | 6 | `license: Apache-2.0` | `license: CDDL-1.1` |
| `Project_Nurse_Ratchet/pyproject.toml` | 11, 20 | Apache + classifier | as above |

The PyPI trove classifier `License :: OSI Approved :: Apache Software License`
is dropped, not reworded: no trove classifier exists for CDDL-1.1, and a
classifier naming Apache while the license field names CDDL is precisely the
metadata lie SHARDEX's README warns the tree has already been burned by.

---

## 4. Evidence — attached (raw + sha; flock proof format: raw / sha / url / fetched / tier)

| Raw file | sha256 | url (path) | fetched | tier |
|---|---|---|---|---|
| `Project_JAEGER/LICENSE` | `33a190c4ce8f4ba013206ba14764ccb16b82afd18c1d52b7aff21986bca5f80e` | repo-relative path | 2026-11-03, this working tree | A (primary doc) |
| `Project_ELIZA/LICENSE` | `6466067853bf4d2647ae63a8b2d384251927912be2bbc14304255a9913214b7b` | repo-relative path | 2026-11-03, this working tree | A |
| `Project_CRADLE/LICENSE` | `6466067853bf4d2647ae63a8b2d384251927912be2bbc14304255a9913214b7b` | repo-relative path | 2026-11-03, this working tree | A |
| `Project_SHARDEX/LICENSE` | `6466067853bf4d2647ae63a8b2d384251927912be2bbc14304255a9913214b7b` | repo-relative path | 2026-11-03 (committed in b49dfc2f) | A |
| `Project_FLAMING_SWORD/LICENSE` | `6466067853bf4d2647ae63a8b2d384251927912be2bbc14304255a9913214b7b` | repo-relative path | 2026-11-03 (committed in b49dfc2f) | A |
| `Project_FLAME/LICENSE` | `6466067853bf4d2647ae63a8b2d384251927912be2bbc14304255a9913214b7b` | repo-relative path | 2026-11-03 (committed in b49dfc2f) | A |
| `Project_Nurse_Ratchet/LICENSE` | `6466067853bf4d2647ae63a8b2d384251927912be2bbc14304255a9913214b7b` | repo-relative path | 2026-11-03 (committed in b49dfc2f) | A |

**The six sibling sha256 are one hash.** Measured 2026-11-03:
`diff <(tail -n +2 Project_ELIZA/LICENSE) <(tail -n +2 Project_SHARDEX/LICENSE)`
→ `ELIZA_TEXT_EQ_SHARDEX`; same for CRADLE → `CRADLE_TEXT_EQ_SHARDEX`. The two
LICENSEs sitting as worktree edits at the time of this ruling's recording
(ELIZA, CRADLE — 13106 bytes each, disk date Nov 3 04:26) are byte-identical to
the text `b49dfc2f` already committed for the other four Projects. The ruling
is retroactively satisfied by both remaining files; this commit closes them.

**One state file record attached** (the session's head ledger, tier B):
`state/head.json` sits at commit `b49dfc2f`'s descendant HEAD — quoted only via
`git rev-parse HEAD` at session time, never from prose.

---

## 5. What this ruling binds

- Every publishable Project (`JAEGER, ELIZA, CRADLE, SHARDEX, FLAMING_SWORD,
  FLAME, Nurse_Ratchet`) ships one `LICENSE` — the full unmodified CDDL-1.1 text,
  byte-identical across the six siblings (JAEGER differs only in its preamble
  copyright lines).
- No project's README, NOTICE, CITATION.cff or pyproject.toml may assert a
  different license; where it does, that is a dispute under §3 and resolves to
  the citation in one sentence, citing `b49dfc2f` and this file.
- The precedent applies to future Projects: adopt the six-sibling sha's text
  verbatim, name Sun Microsystems as initial license steward, copyright
  "2026 Azazael Contributors" for portions, and update NOTICE + CITATION + pyproject
  + README in the same commit. A LICENSE changed without its metadata is
  b49dfc2f's own defect class — the ruling's first commit only replaced the four
  LICENSE bodies and left the metadata stale, and §3 is that defect closed.

Prepared 2026-11-03. Every sha and every citation in this file is the measured
output of a command run in this working tree on 2026-11-03; re-measure before
re-quoting after any LICENSE change.
