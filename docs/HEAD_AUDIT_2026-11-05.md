# HEAD AUDIT — 2026-11-05

**A head is where work is thought to be. This is the reading of every one of them,
and the gap each is carrying.**

- **HEAD**: `250543562c26` on `azazael-intel-ultra-9-evo`; repository `C:/Azazael/azazael`
  (first measured at `c258c2093619`; two commits landed during this session — §7)
- **Command**: `C:/Azazael/.venvs/py315t/Scripts/python.exe tools/head_audit.py --json state/head_audit.json`
- **Result**: exit `0` (advisory), `10 ref(s) [local=5, remote=2, other=3], 6 worktree(s), 7 lane head(s), 16 gap(s)`
  — re-measured at `250543562c26`, same 16 gaps in the same six classes
- **Machine-readable report**: `state/head_audit.json` — **`state/` is gitignored**, so that
  file is local to this tree. The numbers below are the durable copy; the JSON is the
  full one, including `dirty_paths` for all 28 784 uncommitted paths.
- **Expiry**: re-measure before quoting after 2026-11-12, or immediately after any
  branch/worktree/push operation.

`head_audit.py` is HED-12 (see `docs/agent_orders/05_hyper_edge_defaults.md`):
`done`, `pushed`, `clean` are claims about a head, and a head drifts silently —
nothing raises, the next session simply starts from a false premise.

## 1. Refs (10)

| kind | ref | sha | exclusive commits | vs upstream |
| --- | --- | --- | --- | --- |
| local | `azazael-intel-ultra-9-evo` | `250543562c26` | **8** | **+8 / −8** vs `origin/azazael-intel-ultra-9-evo` |
| local | `lane-813-recovery` | `12b75fdae6d8` | 2 | none configured |
| local | `main` | `02fbdd632370` | 0 | +0 / −0 vs `origin/main` |
| local | `migration/baseline-20261001` | `dd08ee954831` | 3 | none configured |
| local | `push-clean` | `e9b2cbf37579` | 0 | none configured |
| remote | `origin/azazael-intel-ultra-9-evo` | `e9b2cbf37579` | 0 | — |
| remote | `origin/main` | `02fbdd632370` | 0 | — |
| other | `refs/backup/orphaned-2026-11-05` | `2ea4718c63ff` | **15** | — |
| other | `refs/prefetch/remotes/origin/azazael-intel-ultra-9-evo` | `3ea21d7a8f67` | 0 | prefetch mirror left by a refmapped fetch — not a head, but it keeps a commit no branch names alive |
| other | `refs/prefetch/remotes/origin/main` | `02fbdd632370` | 0 | same, and duplicates `origin/main`'s sha |

`exclusive` is *commits reachable from this ref and no other*. Two refs at one
sha hold nothing exclusive — the first version of the tool excluded only other
**shas** and therefore reported 30 exclusive commits on `main`, `origin/main` and
the prefetch ref simultaneously: three copies of one reading, all wrong in the
alarming direction. Fixed and re-measured before this table was written.

## 2. Worktrees (6)

| path | HEAD | branch | dirty | note |
| --- | --- | --- | --- | --- |
| `C:/Azazael/azazael` | `250543562c26` | `azazael-intel-ultra-9-evo` | 3 | this lane |
| `C:/Azazael/azazael-coord` | `dd08ee954831` | `migration/baseline-20261001` | **28 778** | 23 top-level groups; `archived=25 125`, `skills=1 186`, `nuitka_build_backup=657` |
| `C:/tmp/clean_head3` | `ed3f0e9f635e` | DETACHED | 0 | **in no ref** |
| `…/Temp/headcheck` | `324ce54960ef` | DETACHED | n/a | prunable + **in no ref** |
| `…/Temp/kilo/baselinewt` | `c7caa6061432` | DETACHED | n/a | prunable + **in no ref** |
| `…/Temp/opencode/headwt` | `ed3f0e9f635e` | DETACHED | n/a | prunable + **in no ref** |

## 3. Lane instruction heads (7)

`state/head.json` records 7 paths and their digests; **all 7 match** on disk
(`AGENTS.md` ×4, `CLAUDE.md`, `rules.md`, `BEAM_AGENTS.md`). No lane is obeying
bytes nobody re-read. This is the reading that goes stale first after a
regeneration, so it is re-checked on every run rather than trusted from
`state/head.json`'s own claim.

## 4. Gaps (16) and what each one costs

| class | n | rows | action |
| --- | --- | --- | --- |
| `orphaned_worktree_head` | 4 | `ed3f0e9f635e` (×2), `324ce54960ef`, `c7caa6061432` | Commits reachable from **no ref**: only the reflog holds them, and `git gc` takes those. Either `git branch rescue/<sha> <sha>` or record that they are disposable — **do not** prune before deciding |
| `no_upstream` | 4 | `azazael-intel-ultra-9-evo`, `lane-813-recovery`, `migration/baseline-20261001`, `push-clean` | `branch.<name>.remote` unset, so push/pull have no default. `git branch --set-upstream-to=origin/<name>` where the remote ref exists; the other three have no remote counterpart at all |
| `prunable_worktree` | 3 | `Temp/headcheck`, `Temp/kilo/baselinewt`, `Temp/opencode/headwt` | `gitdir file points to non-existent location` — registration only. `git worktree prune` clears them **after** the orphaned-head decision above |
| `exclusive_commits` | 2 | `refs/backup/orphaned-2026-11-05` (15), `azazael-intel-ultra-9-evo` (8) | The rescue ref is doing its job; the 8 on the lane branch are this session's work, unpublished |
| `dirty_worktree` | 2 | this tree (3), `coord` (28 778) | Named in full above; the 28 778 are enumerated group-by-group in the JSON |
| `diverged` | 1 | `azazael-intel-ultra-9-evo` | **+8 / −8**: 8 commits are on the published head and not here, 8 here and not there. A merge or a deliberate discard, decided by a human — not a `--force` |

### The one that is not a tidy-up

`+8 / −8` means the branch this session commits to is **missing 8 commits that
were already published**, while holding 8 that are not. Every test result in this
tree is therefore a result about a tree that is not the published one. That is
not a defect `head_audit` can repair; it is the reading that says a merge is owed
before the next "verified" claim.

## 5. Knob improvements (`config/defaults.json`)

Measured by `tools/settings_shadow.py` on 2026-11-05:
`19 config leaf(s), 13 key(s) read across 480 module(s), 13 shared, 7 finding(s)
[bypass_reader=1, orphan_knob=6]`. The 19-vs-13 gap is exactly the six
`orphan_knob` rows below: leaves nothing reads.

| knob | current | suggestion | why |
| --- | --- | --- | --- |
| `ast_audit` | present, never read | **either** wire it (`deep_dive` reads it) **or** delete it | A knob no code reads is documentation wearing a control's clothes; HED-5 says a silently-off default is indistinguishable from a deleted gate |
| `fallback.on_error` | present, never read | same | Same class; it describes behaviour that is actually hard-coded |
| `fallback.record` | present, never read | same | Same |
| `golden_arrow.enabled` | present, never read | same | `golden_arrow.py` reads its own constants — the config surface is decorative |
| `golden_arrow.strict` | present, never read | same | Same |
| `retention.composite_eviction` | read, but **bypassing** `read_default` (`src/CORE/data_retention.py:425`) | route it through `read_default` | The only behavioural knob whose reader ignores the shared surface, so `--show` cannot prove its value is in force |
| `hyper_edge.*` | **landed** in `449a8dacd2c5` — `reading_audit`, `settings_shadow`, `leg_ledger`, `head_audit`, `strict`, all four read at literal call sites in `deep_dive.hyper_edge_flags()` | keep; add only if a fifth leg appears | Off-strict by default per HED-2's debt model |

**Do not wire the five `orphan_knob` rows live in one pass.** Making a documented
knob behavioural changes what the tree does; each needs its own verification that
the behaviour it claims was already the behaviour. Left as findings, deliberately.

## 6. Reproduce

```bash
C:/Azazael/.venvs/py315t/Scripts/python.exe tools/head_audit.py --json state/head_audit.json
C:/Azazael/.venvs/py315t/Scripts/python.exe tools/head_audit.py --strict   # exit 1 while any gap is open
```

## 7. Amendment — what landed after this reading, and one real event

Two commits landed while this document was being written, and both move the
numbers above:

- **`449a8dacd2c5`** — HED-9..HED-12 as instruments (`tools/reading_audit.py`,
  `settings_shadow.py`, `leg_ledger.py`, `head_audit.py`), the `hyper_edge` leg in
  `deep_dive.py`, the `hyper_edge` knobs, and this document.
- **`250543562c26`** — `head_audit` printed one sha at two widths (8 in the ref and
  worktree tables, 12 in the gap details), so a reader comparing two tables could
  not tell a real difference from a formatting one. A single `SHA_W = 12` now
  feeds all five sites. Its unreadable-count branch also sliced git's own output
  to 120 characters with no marker — a diagnostic that cuts its own evidence, in
  the file whose job is to report what is missing. Printed whole now.

Two `[:N]` sites remain and are **not** cuts: `hexdigest()[:16]` is the equality
key `head_state.digest()` also uses, and `entry[:2]` is the two-character XY field
of `git status --porcelain`. A fixed-width format field is read, not truncated.

**The event that proved the detector.** At `449a8dacd2c5` the audit read **17 gaps**:
the new one was `stale_head_state=1`, raised because the commit landing the
auditor moved HEAD past the `state/head.json` the auditor reads.
`head_state.py --write` cleared it and the reading returned to **16 gaps** at
`250543562c26`. Twice in one session the detector fired on a real drift rather than a
fixture — and it is why a gap count in a commit message may differ by one from the
count here: they were measured on different heads, and both were right.

Every sha in this document now carries the 12 characters `head_audit` prints,
tables and prose alike, so no two readings of one commit can look different. §1
has 10 rows for 10 refs; an earlier draft of this section listed 8 under a
heading that said 10 — the same denominator defect HED-9 exists to catch, made by
the document that documents it.

One number here cannot be pinned: the lane's *exclusive* count rises by one for
every commit this session lands, so `8` is a reading at `250543562c26`, not a
constant. The durable quantity is the divergence (`+8 / −8`), and it moves only
when someone merges or publishes.
