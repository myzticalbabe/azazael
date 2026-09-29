# NEURAL MESH — PRIORITIES, relisted 2026-09-29 (13:40)

Relisted from measured state at 13:40, not from the previous list. Four
items on the last list were wrong or stale and are corrected below; three
are now closed.

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
| P2: "reset exposure has no guard" | **closed** | `scripts/reset_guard.py` (`cac421dd`) + 12 tests. Verified live: it refuses and names 64 modified files and 13 unpushed commits. |
| P6: "109 pending functions" | number right, **scope wrong** | 109 is current (artifact regenerated 13:11) but it covers only `src/CORE/WORMS/expansion`. See P1 below. |
| P3: "the green-suite claim is still false" | **closed** | 9 remaining failures confirmed pre-existing by stash-and-rerun, byte-identical with and without my changes. |

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

Action: extend the preflight scope to all of `src/`, or accept 155
undocumented functions as a standing debt. The current artifact is honest
about its scope and should not be read as covering more than it does.

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

## P3 — `G:/source-of-truth/azazael` is unversioned and still a sync target

Confirmed again: `git rev-parse` there returns *not a git repository*. It
has no history, so a sync from it is a one-way overwrite with no recovery.

Action: decide whether it is a source, a mirror, or obsolete. Until then,
`sync_all.py` should not target it. **On hold pending your call.**

## P4 — 13 commits are on no remote

`dccc5846`, `d6c3203c`, `5dae1f09`, `cac421dd`, `31a72fd7`, `391be529`,
`8fd58db0`, `fe6b1edd`, `3a948a26` and four earlier ones. `reset_guard`
reports this on every run. There is no `{@u}` on this branch.

Action: push or establish a remote. I have not run `git push`.

## P5 — 3,464 dict-key asymmetries, none triaged

`dict_key_contract` output. These are *questions*, not defects — the tool
says so on every run — and no rule exists for closing them.

Action: either write a triage rule or stop running it. 3,464 unexamined
candidates is indistinguishable from not running it.

## P6 — the tree is being written while it is being worked on

40+ files dirty at any moment from live `chain_controller` jobs; the `meta`
job is what purged restored routes at 10:05. Every commit today was
path-scoped for this reason.

A corollary found today: a pristine `git worktree` at HEAD was **missing
`scripts/wiring_cycle.py`**, because the controller generates modules and
tests together, uncommitted. HEAD cannot be tested in isolation — which is
why the P3 baseline had to be established by stash-and-rerun rather than by
checkout.

Action: decide whether these jobs should run `--allow-mutations` against a
working tree at all.

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

Skill 0.9.55 against package 0.9.50; warns on every refresh. Resolves and
runs correctly. Not blocking, and nobody has acted because it is only a
warning.

---

## Deliberately untouched

- **Firewall rule for TCP 18210** — needs admin and an explicit go-ahead.
- **`git push` and `sync_all.py` to `G:`** — see P3 and P4.
- **Deleting any root-level `.py`** — see P2. Six are forks, not stale
  copies; deleting either side loses code.
- **`tests/test_chain_refactor.py` and its 4 WSL siblings** — see the P1
  correction. They should not be committed.
