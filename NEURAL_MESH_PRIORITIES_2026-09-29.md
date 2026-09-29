# NEURAL MESH — PRIORITIES, relisted 2026-09-29 (13:40)

Relisted from measured state at 13:40, not from the previous list. Six
items on the last list were wrong or stale and are corrected below; four
are now closed. P3 and P4 were corrected a second time at 13:48 — see
the correction table.

Every number was read from the live tree, the live ledger, or a tool run in
this session. Where a claim could not be measured it says so rather than
carrying the old figure forward.

**Supersedes** the 11:40 version of this file. Related:
`GRAPH_TOOLS_AUDIT_2026-09-29.md`, `NEURAL_MESH_AUDIT_2026-09-29.md`.

---

## Corrections to the previous list

| was | now | why |
|---|---|---|
| P1: "995 lines exist only in WSL, in no commit" | **withdrawn** | WSL is two months *behind* (HEAD `7d883ba`, 2026-07-29), 453 files untracked, and 2 of the 4 test files fail there too. They test code in neither tree. Copied, SHA-verified, then removed. |
| P2: "reset exposure has no guard" | **closed** | `scripts/reset_guard.py` (`cac421dd`) + 12 tests. Verified live: it refuses and names 64 modified files and 13 unpushed commits. Re-verified 13:48 after the P4 push: still refuses, 64 modified, and the unpushed count is now gone. |
| P6: "109 pending functions" | number right, **scope wrong** | 109 is current (artifact regenerated 13:11) but it covers only `src/CORE/WORMS/expansion`. See P1 below. |
| P3: "the green-suite claim is still false" | **closed** | 9 remaining failures confirmed pre-existing by stash-and-rerun, byte-identical with and without my changes. |
| P3: "`G:/source-of-truth/azazael` is unversioned and still a sync target" | **real, wrong reason** | It *does* hold a hollow `.git` (`hooks/pre-commit` only — no HEAD/objects/refs/config). But it is a sync **destination**, never a source, so "a sync from it is a one-way overwrite" describes a path that does not exist. The actual hazard is worse — see P3. |
| P4: "13 commits are on no remote" | **closed** | A `gdrive` remote does exist and is bare. The "no remote / no `{@u}`" claim came from never having run `git remote -v` in the right repository. Pushed and verified. |

---

## Closed today

**Fabricated route telemetry removed and stable.** The `8000.0ms` eBPF
window, the interleaved counters and the malformed `route:windows>route` key
are gone. Verified across three save/load cycles: 10 genuine ~95ms samples
per wsl2 route preserved, zero `8000.0` samples, counters at 0 and pinned by
a watermark that survives the fold-in.

**The graph rebuilt and scoped.** 28,279 files / 451,307 nodes / 638 MB →
3,122 / 47,411 / 46 MB; rebuild 31 min → 75 s. `artifact_freshness` and
`capability_liveness` both exit 0.

**Three audit tools, each fixed after shipping a false PASS.**
`dead_function_check`, `manifest_reconcile`, `dict_key_contract` —
committed `dccc5846`, 33 tests, 8 mutations all bite. The P0 checker is
`5dae1f09`; the cd2/manifest/test-hygiene fixes are `d6c3203c`.

---

## P0 — `MeshRouterWorm.invalidate_route` is unreachable, and that is deliberate

`invalidate_route` (`src/CORE/WORMS/expansion/mesh.py:258`) has zero
callers. Its only caller, `invalidate_q`, is itself called by nothing except
a comment at `spine.py:2313` saying it is deliberately *not* called.

The comment's reasoning is correct: the method exists to discount a penalty
*because the cause is fixed*, so a caller firing it on failure would invert
the contract. **Do not add a caller.** But the consequence stands — the
evidence-floor machinery added in `3a948a26` is correct and reached by
nothing in production, which is why liveness reports `dormant`/`unproven`.

Action: decide whether this is a capability to wire or documentation to
write. It is currently neither.

## P1 — 155 unreferenced functions outside the one directory anyone audits

`mesh_function_preflight` scans exactly `MESH_DIR = src/CORE/WORMS/expansion`
(`tools/mesh_function_preflight.py:37`) and its `wire_or_cut` artifact
enforces *"no finding is undeclared"* over that scope. `tests/test_mesh_wire_or_cut.py`
passes, 29 tests, and the invariant holds — **for that directory.**

`dead_function_check` scans all of `src/`. Of its 161 findings:

- **6** inside the audited directory (already covered)
- **155** outside it, previously unexamined:

  | dir | findings |
  |---|---|
  | `CORE` | 83 |
  | `ORCHESTRATION` | 31 |
  | `UTILITIES` | 24 |
  | `CODEX` | 7 |
  | other | 10 |

  134 have their name mentioned *nowhere* in the repo. Two verified dead by
  hand: `get_contract_report` and `batch_upgrade_worms` each have exactly one
  mention — their own `def`. 27 are dispatched by string and need a human
  decision, not a deletion.

**Correction, 13:35:** the scope is not that directory. `SCOPE_GROUPS` is
**61 named module stems**, a semantic list; measured against disk it covers
61 of 645 modules under `src/` — **9.5%**. The other 584 are excluded by
design, not by oversight.

Widening is not the fix, and would be wrong: blind widening declares 156
things pending that are mostly legitimate (`get_secret`, `audit_secrets`,
`get_q_variance` are public API; `bdam_blocks`, `fgsm_delta_f1` are research
code). Instead `tools/scope_coverage.py` (`aff97b17`) makes the boundary
measurable and fails when a declared stem matches no file — the dangerous
direction, where findings can never be reported while the wire-or-cut test
stays green over a silently smaller question.

Action: decide the boundary on purpose, then keep it enforced.

## P2 — 6 tracked `.py` files at the repo root are FORKS, not stale copies

**The earlier version of this item was wrong, and the correction is the
point.** It read "last touched 2026-09-06 against `src/` copies from
2026-09-28" and proposed deleting the root files as stale. Measuring content
instead of commit dates:

| root file | lines only in root | lines only in `src/` | root defines, twin lacks | twin defines, root lacks |
|---|---|---|---|---|
| `health_server.py` | **1** | **120** | `_get_azazael_health` | — |
| `metrics.py` | 242 | 127 | `WormMetrics` | `DriftAlert`, `HealthCheck`, `MetricsCollector` |
| `run_tests.py` | 231 | 253 | `main`, `list_test_files` | `run_all_tests`, `test_bat_file` |
| `NATURE_CLUSTERS.py` | 572 | 355 | `_get_dm` | `_get_cluster_tracer` |
| `METACLUSTER.py` | 167 | 271 | `_get_dm` | — |
| `PamsRecorder.py` | 32 | 78 | — | — |

**Neither copy is strictly ahead.** Each defines symbols the other lacks.
`health_server.py`'s root copy has `_get_azazael_health()`; `run_tests.py`'s
twin has `test_bat_file` and `run_all_tests` while root has `main` and
`list_test_files`. These are divergent forks of the same module, and
deleting either side destroys working code.

The `src/` copy of `health_server.py` was last committed **2026-06-21** — not
because the root copy is newer, but because nobody has touched it since June.
"Older commit date" and "older content" are different claims, and the first
version of this list read the first as the second.

What *is* true and still actionable: these names make every whole-repo tool
ambiguous. `dict_key_contract` reported `NATURE_CLUSTERS.py:706` when the
reader would have had `src/CORE/WORMS/NATURE_CLUSTERS.py` open — the line
numbers pointed at a different file. No tracked `.py` imports any of these
by bare name, so **no import resolves ambiguously today**; the hazard is
naming, not resolution.

Action: reconcile the forks by hand — merge each pair, keep the union, and
delete one side — with `tools/shadowed_module_check.py` (added this pass) to
list what each side uniquely holds. Six live forks plus 9 archive shadows.

## P3 — `G:/source-of-truth/azazael` is a sync destination with a hollow `.git`

**Corrected 13:48. The original text here was wrong in both its reason and
its direction.**

A remote *does* exist: `gdrive` → `G:/source-of-truth/azazael.git`, a **bare**
repo (`core.bare = true`, 282 commits). That is the versioned G: artifact and
it is the push target. P4 claimed otherwise; both items were written before
the remote was ever checked.

The path this item is actually about is the *other* one,
`G:/source-of-truth/azazael` — a separate working copy beside the bare repo.
Measured now, not assumed:

- `git -C` there: `fatal: not a git repository`. That part was right, but for
  a reason the old text missed: **`.git` exists and contains only
  `hooks/pre-commit`** (2797 bytes, Jun 4) — no `HEAD`, no `objects/`, no
  `refs/`, no `config`. Any check that tests repository-ness by `.git`
  existing gets a false yes; git itself rejects the directory. (That is the
  same class of defect as this session's other false-PASS tools: the
  existence check and the real check disagree.)
- Last modified 2026-06-02, and stale in content: it has `src/` and `tools/`
  but not `tools/dict_key_triage.py` or this file.

**The direction in the old text was backwards.** Nothing syncs *from* it.
`sync_all.py` uses it only as a destination — `sync_wsl_to_g` (line 284) and
`sync_docs_to_target` (line 409) both copy *into* it. So "a sync from it is a
one-way overwrite with no recovery" describes a code path that does not exist.

**The real hazard is worse than the one described.** `sync_wsl_to_g` ends in
`shutil.copy2(src_file, dest)` with no backup, no recency check and no
conflict detection, and its source — WSL `/root/azazael` — sits at `7d883ba`
dated **2026-07-29**, two months behind. Running it would overwrite the
archive with two-month-old content, silently, with nothing to roll back to
because the `.git` beside it is hollow. (The copy is the only destructive
step: the module contains no `rmtree`/`unlink` on these paths, so it cannot
delete, only overwrite.)

Action: do not run `sync_wsl_to_g` until WSL is current or the copy is gated
on source recency. **On hold pending your call.**

## P4 — 18 commits were unpushed

**Closed 13:46.** A remote does exist: `gdrive` → `G:/source-of-truth/azazael.git`,
bare, `core.bare = true`. My earlier claim that there was no remote and no
`{@u}` on this branch was simply unmeasured — I had not run `git remote -v`.

Pushed `bc4d51db..f3f18772`: fast-forward, no force, 18 commits. Verified
four ways rather than by the push command's own success message:

| check | result |
|---|---|
| `git log gdrive/master..HEAD \| wc -l` | `0` |
| `git ls-remote gdrive` | `f3f18772…` for both `HEAD` and `refs/heads/master` |
| `git --git-dir=G:/source-of-truth/azazael.git rev-parse master` | `f3f18772…` |
| read `tools/dict_key_triage.py` *out of* the remote object store | present, correct content |

`scripts/reset_guard.py` no longer reports an unpushed count. Note the
distinction that caused the original error: a `gdrive` remote existing does
**not** mean the sibling `G:/source-of-truth/azazael` working copy is
versioned. It is not — see P3.

## P5 — 3,464 dict-key asymmetries, none triaged

`dict_key_contract` output. These are *questions*, not defects — the tool
says so on every run — and no rule exists for closing them.

**Done, 13:35.** `tools/dict_key_triage.py` (`aff97b17`) provides the
closure mechanism, mirroring the `wire_or_cut` pattern that already works
here — including the half usually left out: a declaration with no finding is
**stale** and fails, so the file cannot grow forever. An `accepted` verdict
needs a stated reason and can carry a review date that expires.

`DICT_KEY_TRIAGE.json` is deliberately **not seeded**. `--init` would write
2,441 entries all marked `accepted` with blank reasons, which the gate then
rejects — a blanket dismissal is exactly the rot the mechanism prevents.

Action: rule on each finding. `--check` fails until then, and should.

## P6 — the tree is being written while it is being worked on

40+ files dirty at any moment from live `chain_controller` jobs; the `meta`
job is what purged restored routes at 10:05. Every commit today was
path-scoped for this reason.

A corollary found today: a pristine `git worktree` at HEAD was **missing
`scripts/wiring_cycle.py`**, because the controller generates modules and
tests together, uncommitted. HEAD cannot be tested in isolation — which is
why the P3 baseline had to be established by stash-and-rerun rather than by
checkout.

**Correction, 13:35:** the premise was wrong. Measured over 40 seconds,
**zero** non-`state/` files changed content. Five `state/*.json` bookkeeping
files churn; the controller is not currently mutating source. The 633 dirty
entries are accumulated machine state, not a live hazard.

The real failure is different: with 633 dirty entries a path-scoped commit
is easy to get wrong. `tools/commit_scope_check.py` (`03bde7c5`) reads the
git **index** rather than the working tree — 633 dirty entries is a fact
about the tree, while what a commit contains is a fact about the index — and
fails when machine-state files are staged.

Action: none. The hazard as described does not exist; the guard covers the
one that does.

## P7 — `route_censoring` is unproven, and that is the honest state

`capability_liveness` reports `unproven`, not `ok`: no unreachable peer has
been observed since the fix. The capability exists, the failure has not
recurred, and neither fact is evidence that the capability is why.

An evidence gap, not a code defect. Settling it needs one unreachable peer
or a `--since` window containing one. **Should not be closed by assertion.**

## P8 — `src/SCRIPTS/monitor_learning.py` == `scripts/monitor_learning.py`

Byte-identical (`4345f07971f7fe03bfbc09dca7f2f83e`), no generator, no
symlink. One of them is redundant.

Action: the call belongs to its owner.

## P9 — graphify skill/package version skew

Skill 0.9.55 against package 0.9.50; warned on every refresh and resolved
correctly, so nobody acted.

**Partly done, 13:35.** `tools/graphify_version_check.py` (`03bde7c5`) makes
it a return code: `--strict` exits 1. Alignment requires the versions to
match **and** the install to be patched — an unpatched 0.9.55 would satisfy
a naive equality check and quietly produce a `graph.html` that cannot render
this tree.

**The skew itself is deliberately not fixed.** The remedy is
`uv tool install graphifyy==0.9.55 --force`, which installs outside this
project and would replace a **patched** 0.9.50 whose huge-mode marker
currently checks out. Unattended, that trades a version warning for an
unpatched renderer on a tree that needs the huge-mode path. The remedy is
printed, not run.

Action: yours. It is an environment change outside the repo, taken
deliberately or not at all.

---

## Deliberately untouched

- **Firewall rule for TCP 18210** — needs admin and an explicit go-ahead.
- **`sync_all.py` to `G:`** — see P3. The push is done (P4); the WSL→G: copy
  is the one still gated, because its source is two months stale.
- **Deleting any root-level `.py`** — see P2. Six are forks, not stale
  copies; deleting either side loses code.
- **`tests/test_chain_refactor.py` and its 4 WSL siblings** — see the P1
  correction. They should not be committed.
