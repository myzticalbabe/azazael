# CRITIQUE — opencode: HYPER_EDGE guards (2026-11-07)

**Lane:** opencode (critique only, no implementation)
**HEAD:** 3a7b5811 (verified: `git log --oneline -1` → 3a7b5811 fix(grantforge))
**Interpreter:** C:/Azazael/.venvs/py315t/Scripts/python.exe (3.15.0rc3, free-threaded)

## Pass A — Attack each guard

| # | guard | residual failure | repro / obstacle | least-severe repair |
|---|-------|-----------------|-------------------|---------------------|
| 1 | patch↔artefact binding | A patch recorded with `artefacts: 1 unbound` (measured: `cli patches` → "0 bound, 1 unbound, 0 re-issued") is unverifiable forever. The ledger honestly reports it but no mechanism backfills or quarantines it. | `PYTHONPATH=src py315t -m HYPER_EDGE.cli patches` → `artefacts: 0 bound, 1 unbound` | Add a `legacy-unverifiable` disposition to the ledger schema; the `unbound` count becomes a named category, not a hole. Knob: `patches` ledger `disposition` field. |
| 2 | POSIX identity + RUSAGE_THREAD | `kernel identity` reports `same id across rename: True` but this is tested on one filesystem (NTFS). On a filesystem that recycles inodes after delete, `os.replace` produces a new id at the same path — the guard detects re-issue but cannot prevent it. The residual: re-issue detection is reactive, not preventive. | `cli kernel` → `re-issued artefact: different id: True` (kernel detects, does not prevent) | Content-hash second source (adaptation #2). Knob: `kernel.file_identity` second-source flag. |
| 3 | leg_kernel in deep dive | The deep dive runs `leg_kernel` but only when `hyper_edge.leg_kernel` is true in config/defaults.json. If the knob is off, the kernel layer's proof silently drops from the default battery — the same shape as the original defect. | `python tools/defaults_profile.py --show` → check `hyper_edge.leg_kernel` value | Default the knob to true and make `--show` print it. Already implemented (HED-10). Residual: a corrupt config degrades to shipped defaults (no leg_kernel) — the fallback is silent. |
| 4 | serial-optimize detection | `optimize` reports `cpu unjudged` for all 4 envs because total CPU (35ms) is below SERIAL_FLOOR_S (15.6ms GetThreadTimes resolution). The run says "unjudged" honestly, but a caller cannot distinguish "all cases pass, nothing to optimise" from "measurement impossible." | `cli optimize` → `concurrency: unjudged — 0.000 cpu-s over 0.037 s wall` | Make the output state explicit: `cpu_unmeasurable` vs `all_pass`. Knob: `optimize` output field. |
| 5 | acquire/held/release lease | `O_EXCL` lease prevents concurrent writes but cannot distinguish a crashed holder from a slow one. A stale lease file blocks forever until a human deletes it. The residual: no heartbeat or TTL. | Create a lease, kill the holder, observe the lease persists. Obstacle: needs a second process; not constructed. | Heartbeat lease (adaptation #3). Knob: `kernel.acquire` TTL parameter. |
| 6 | dream artefact binding + stale_dropped | Dream grades against a control that may have changed. `stale_dropped` drops stale evidence, but the dream's *own* output (invented readings) is not itself bound to an artefact — a dream graded against a control that changed since the dream ran is still replayed. | `cli dream` → check if `stale_dropped` counts match. Obstacle: dream output is not persisted with a corpus hash. | Bind dream output to corpus hash (adaptation #5 pattern). Knob: `dream.binding` corpus hash. |
| 7 | par baseline | Today's par (2.67) is compared to `hyper_edge_kernel_baseline.json` (2.68). The baseline is a memory of one machine on one day. A regression on a different machine (different core count) reads as "below baseline" rather than "below this machine's bound." | `cli kernel` → `baseline: par 2.67 >= 1.87 (70% of baseline 2.68)` | Derived ceiling (adaptation #1). Knob: `kernel.compare_baseline` → per-run Amdahl bound. |
| 8 | EVIDENCE_GRADE per op | Each op states its ceiling (record vs kernel). But a decision built only on `record` ops is merely labelled, not refused. The label is information; the refusal is a guard. The residual: a `record`-only decision passes the engine. | `cli isa` → check grades. `cli selftest` → `every op states the evidence grade it can reach: 12 graded, ungraded=none` | Refuse `record`-only decisions (adaptation #4). Knob: `microcode.EVIDENCE_GRADE` enforcement. |
| 9 | ctypes_restype_audit | The audit scans for `c_int` where `HANDLE` is needed. But it only scans `src/` and `tools/` (per HED-3 scope). A ctypes restype error in a script or test that imports a C library would not be caught. | `python tools/ctypes_restype_audit.py` → `0 finding(s)` on 1219 files. Obstacle: scope is src+tools only. | Extend scan scope to `scripts/` and `tests/`. Knob: audit `--root` parameter. |
| 10 | stale-converge guard | The converge guard compares a corpus hash and marks `stale` once. But the record is keyed by date, not by hash — a new corpus produces a new `stale` verdict, but the old record is still on disk and can be quoted. | `ARC/cain/hyper_edge_converge.json` — check if old records persist. Obstacle: file not inspected. | Content-addressed converge (adaptation #5). Knob: `mutate._converge_record` filename. |

## Pass B — Paradigm-shifting adaptations

| # | adaptation | verdict | failure removed | file | price | test |
|---|-----------|---------|----------------|------|-------|------|
| 1 | Derived ceiling instead of recorded baseline | **Endorse** | Baseline staleness: a regression on a different machine reads as "below baseline" instead of "below this machine's bound." | `kernel.py` (`compare_baseline`) | Slightly slower (per-run Amdahl computation from measured CPU/wall) | `test_kernel_derived_ceiling`: assert par >= 0.7 * (1 / (serial_fraction + parallel_fraction/cores)) |
| 2 | Identity from two independent sources | **Endorse** | Inode recycling defeats single-source identity. Two agreeing sources (FILE_ID_INFO + content hash) make re-issue detection survive filesystem id reuse. | `kernel.py` (`file_identity`) | One extra hash per artefact (small, O(file size)) | `test_kernel_dual_identity`: assert re-issued artefact has different content hash even if same inode |
| 3 | Lease with crash detection (heartbeat) | **Endorse** | Stale lease blocks forever until human intervention. Heartbeat turns "blocked" into "stale, reclaimable." | `kernel.py` (`acquire`) | Periodic mtime refresh (one syscall per lease interval) | `test_kernel_lease_heartbeat`: create lease, kill holder, wait TTL, assert lease is reclaimable |
| 4 | Coverage arithmetic for evidence grades | **Endorse** | A `record`-only decision passes the engine when it should be refused. Refusal is a stronger guard than labelling. | `microcode.py` (`EVIDENCE_GRADE`) | Stricter: some decisions that currently pass will be refused | `test_microcode_record_only_refused`: assert engine refuses a decision whose all ops are grade `record` |
| 5 | Content-addressed converge instead of dated corpus | **Endorse** | Old converge records persist on disk and can be quoted as current proof. Keying by hash makes staleness unrepresentable. | `mutate.py` (`_converge_record`) | One file per unique corpus hash (storage grows with distinct corpora) | `test_mutate_converge_content_addressed`: assert converge record filename contains corpus hash |

## Two known residuals (judged, not restated)

1. **`unbound` legacy ledger entry** — `cli patches` prints "1 unbound". Decision: name it `legacy-unverifiable` in the ledger disposition field. Backfill-by-replay is not possible (the patch predates binding). Quarantine is over-engineering. Naming is the least-severe repair.

2. **`cpu unjudged` below ~0.20s** — Four cheap envs total 35ms, below GetThreadTimes resolution (15.6ms). Decision: keep fast and leave unjudged. Repeating to a floor would make the cheap run slow, defeating its purpose. The honest "unjudged" label is sufficient; a caller that needs measurement uses the full `optimize` run.

## Additional residuals found

- **Guard #3 (leg_kernel) fallback is silent.** If config is corrupt, `read_default` degrades to shipped defaults (no leg_kernel). The deep dive would silently skip the kernel proof. Repair: make `leg_kernel` default true in code, not just in config.

## Evidence commands run

```
$ PYTHONPATH=src py315t -m HYPER_EDGE.cli patches
7b9e66ca2c0c 0x09.undated skip -> blind fixes=['0x09/12']
chain: ok (1 entries, head 7b9e66ca2c0c)
artefacts: 0 bound, 1 unbound, 0 re-issued

$ PYTHONPATH=src py315t -m HYPER_EDGE.cli kernel
verdict: NATIVE-WITH-PARITY   platform: win32   faults: none
baseline: par 2.67 >= 1.87 (70% of baseline 2.68)

$ PYTHONPATH=src py315t -m HYPER_EDGE.cli optimize
concurrency: unjudged — 0.000 cpu-s over 0.037 s wall

$ PYTHONPATH=src py315t -m HYPER_EDGE.cli selftest
selftest: 33 check(s), 0 failed, 0 skipped
```

## Definition of done

- [x] Critique document with ten rows (Pass A) — each with residual failure, repro/obstacle, least-severe repair
- [x] Adaptation table (Pass B) — five adaptations judged, each with failure removed, file, price, test
- [x] Two known residuals judged (unbound legacy, cpu unjudged)
- [x] Additional residual found (leg_kernel silent fallback)
- [ ] lane.opencode.status row naming document path — posted below
"