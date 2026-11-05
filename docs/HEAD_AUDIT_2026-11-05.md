# HEAD AUDIT — 2026-11-05

**A head is where work is thought to be. This is the reading of every one of them,
and the gap each is carrying.**

- **HEAD**: `c258c209` on `azazael-intel-ultra-9-evo`; repository `C:/Azazael/azazael`
- **Command**: `C:/Azazael/.venvs/py315t/Scripts/python.exe tools/head_audit.py --json state/head_audit.json`
- **Result**: exit `0` (advisory), `10 ref(s) [local=5, remote=2, other=3], 6 worktree(s), 7 lane head(s), 16 gap(s)`
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
| local | `azazael-intel-ultra-9-evo` | `c258c209` | **6** | **+6 / −8** vs `origin/azazael-intel-ultra-9-evo` |
| local | `lane-813-recovery` | `12b75fda` | 2 | none configured |
| local | `main` | `02fbdd63` | 0 | +0 / −0 vs `origin/main` |
| local | `migration/baseline-20261001` | `dd08ee95` | 3 | none configured |
| local | `push-clean` | `e9b2cbf3` | 0 | none configured |
| remote | `origin/azazael-intel-ultra-9-evo` | `e9b2cbf3` | 0 | — |
| remote | `origin/main` | `02fbdd63` | 0 | — |
| other | `refs/backup/orphaned-2026-11-05` | `2ea4718c` | **15** | — |
| other | `refs/prefetch/remotes/origin/main` | `02fbdd63` | 0 | — |
| other | `refs/prefetch/remotes/origin/azazael-intel-ultra-9-evo` | `3ea21d7a` | 0 | — |

`exclusive` is *commits reachable from this ref and no other*. Two refs at one
sha hold nothing exclusive — the first version of the tool excluded only other
**shas** and therefore reported 30 exclusive commits on `main`, `origin/main` and
the prefetch ref simultaneously: three copies of one reading, all wrong in the
alarming direction. Fixed and re-measured before this table was written.

## 2. Worktrees (6)

| path | HEAD | branch | dirty | note |
| --- | --- | --- | --- | --- |
| `C:/Azazael/azazael` | `c258c209` | `azazael-intel-ultra-9-evo` | 6 | this lane |
| `C:/Azazael/azazael-coord` | `dd08ee95` | `migration/baseline-20261001` | **28 778** | 23 top-level groups; `archived=25 125`, `skills=1 186`, `nuitka_build_backup=657` |
| `C:/tmp/clean_head3` | `ed3f0e9f` | DETACHED | 0 | **in no ref** |
| `…/Temp/headcheck` | `324ce549` | DETACHED | n/a | prunable + **in no ref** |
| `…/Temp/kilo/baselinewt` | `c7caa606` | DETACHED | n/a | prunable + **in no ref** |
| `…/Temp/opencode/headwt` | `ed3f0e9f` | DETACHED | n/a | prunable + **in no ref** |

## 3. Lane instruction heads (7)

`state/head.json` records 7 paths and their digests; **all 7 match** on disk
(`AGENTS.md` ×4, `CLAUDE.md`, `rules.md`, `BEAM_AGENTS.md`). No lane is obeying
bytes nobody re-read. This is the reading that goes stale first after a
regeneration, so it is re-checked on every run rather than trusted from
`state/head.json`'s own claim.

## 4. Gaps (16) and what each one costs

| class | n | rows | action |
| --- | --- | --- | --- |
| `orphaned_worktree_head` | 4 | `ed3f0e9f` (×2), `324ce549`, `c7caa606` | Commits reachable from **no ref**: only the reflog holds them, and `git gc` takes those. Either `git branch rescue/<sha> <sha>` or record that they are disposable — **do not** prune before deciding |
| `no_upstream` | 4 | `azazael-intel-ultra-9-evo`, `lane-813-recovery`, `migration/baseline-20261001`, `push-clean` | `branch.<name>.remote` unset, so push/pull have no default. `git branch --set-upstream-to=origin/<name>` where the remote ref exists; the other three have no remote counterpart at all |
| `prunable_worktree` | 3 | `Temp/headcheck`, `Temp/kilo/baselinewt`, `Temp/opencode/headwt` | `gitdir file points to non-existent location` — registration only. `git worktree prune` clears them **after** the orphaned-head decision above |
| `exclusive_commits` | 2 | `refs/backup/orphaned-2026-11-05` (15), `azazael-intel-ultra-9-evo` (6) | The rescue ref is doing its job; the 6 on the lane branch are this session's work, unpublished |
| `dirty_worktree` | 2 | this tree (6), `coord` (28 778) | Named in full above; the 28 778 are enumerated group-by-group in the JSON |
| `diverged` | 1 | `azazael-intel-ultra-9-evo` | **+6 / −8**: 8 commits are on the published head and not here, 6 here and not there. A merge or a deliberate discard, decided by a human — not a `--force` |

### The one that is not a tidy-up

`+6 / −8` means the branch this session commits to is **missing 8 commits that
were already published**, while holding 6 that are not. Every test result in this
tree is therefore a result about a tree that is not the published one. That is
not a defect `head_audit` can repair; it is the reading that says a merge is owed
before the next "verified" claim.

## 5. Knob improvements (`config/defaults.json`)

Measured by `tools/settings_shadow.py` on 2026-11-05:
`14 config leaf(s), 8 key(s) read across 479 module(s), 8 shared, 7 finding(s)
[bypass_reader=1, orphan_knob=6]`.

| knob | current | suggestion | why |
| --- | --- | --- | --- |
| `ast_audit` | present, never read | **either** wire it (`deep_dive` reads it) **or** delete it | A knob no code reads is documentation wearing a control's clothes; HED-5 says a silently-off default is indistinguishable from a deleted gate |
| `fallback.on_error` | present, never read | same | Same class; it describes behaviour that is actually hard-coded |
| `fallback.record` | present, never read | same | Same |
| `golden_arrow.enabled` | present, never read | same | `golden_arrow.py` reads its own constants — the config surface is decorative |
| `golden_arrow.strict` | present, never read | same | Same |
| `retention.composite_eviction` | read, but **bypassing** `read_default` (`src/CORE/data_retention.py:425`) | route it through `read_default` | The only behavioural knob whose reader ignores the shared surface, so `--show` cannot prove its value is in force |
| *(new)* `hyper_edge.*` | absent | add `{"reading_audit": true, "settings_shadow": true, "leg_ledger": true, "strict": false}` | The three HED auditors gated as a leg, off-strict by default per HED-2's debt model |

**Do not wire the five `orphan_knob` rows live in one pass.** Making a documented
knob behavioural changes what the tree does; each needs its own verification that
the behaviour it claims was already the behaviour. Left as findings, deliberately.

## 6. Reproduce

```bash
C:/Azazael/.venvs/py315t/Scripts/python.exe tools/head_audit.py --json state/head_audit.json
C:/Azazael/.venvs/py315t/Scripts/python.exe tools/head_audit.py --strict   # exit 1 while any gap is open
```
