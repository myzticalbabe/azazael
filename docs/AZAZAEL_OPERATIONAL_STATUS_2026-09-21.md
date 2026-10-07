# AZAZAEL Operational Status — 2026-09-21

## The finding in one line

**The system is not learning because it is not running; when it runs it has no
authority to write; and the one input that authority depends on cannot be
produced by anything it owns.**

Each tier below is measured, not inferred.

---

## Tier 0 — Nothing is scheduled to run

```
Azazael-Chain            Disabled      <- the single entry point
Azazael-DreamCycle       Disabled
Azazael-EveBattery       Disabled
Azazael-EvolutionCycle   Disabled
Azazael-FullPass         Disabled
Azazael-GospBattery      Disabled
Azazael-MetacogCycle     Disabled
Azazael-NightlyMainten.  Disabled
Azazael-TrainingOrch.    Disabled
AzazaelBerksMonitor      Disabled
```

10 of 10. And `scripts/run_azazael_chain.py` is the **only** scheduled entry
point: the other nine loops are its `JOBS` dict (`dream`, `metacog`, `evolution`,
`train`, `fullpass`, `liveness`, `maint`, `eve`, `gosp`, `wslclean`). So ten
disabled tasks are not ten independent outages — they are **one** outage with
nine aliases, which is why the watchdog below misreads it.

Chain task detail:

```
Last Run Time:      9/20/2026 3:56:06 AM
Last Result:        1            <- non-zero
Power Management:   Stop On Battery Mode, No Start On Batteries
```

Newest telemetry in the live store: outcome `2026-09-20T07:34:05`, nature
`2026-09-20T08:01:13`, choice `2026-09-14T16:50:51`. Nothing since.

---

## Tier 1 — The watchdog reports GREEN while nothing runs

`logs/chain_liveness.log`, last entry (2026-09-20T03:41 — one minute before the
last fire):

```
OK: every discovered loop is enabled, recent, and writing.

coverage: 9 task(s) retired on purpose, judged NOT failed
          (a chain job does the same work)
```

Two structural reasons it cannot see this failure:

1. It is itself a chain job, so it cannot run when the chain is off. Its own
   source says so: *"It cannot detect its own death by running."*
2. It deliberately whitelists the nine disabled tasks as "retired on purpose,
   judged NOT failed" — so it classifies the disabled state of everything except
   the one task that matters, and cannot evaluate that one.

This is the **second** documented occurrence. The same file's comment records the
first: *"the chain itself sat DISABLED from 2026-09-16T01:54 for four days with
nothing red anywhere."* The watchdog was added afterwards and did not prevent the
recurrence, because it was added as a job inside the thing it watches.

---

## Tier 2 — When invoked, it works — with one permanent failure

Reproduced live today (`main([])` in `scripts/run_azazael_chain.py`):

```
cycle natures=36 ok=231 fail=1 deferred=0 dur=66s
  ERR security:NucleiBridge: NucleiBridge.scan() missing 1 required positional argument: 'targets'
  ERR NucleiBridge: ... (after 2 attempts)
```

The failure is **structural, not transient**:

| Fact | Value |
|---|---|
| NucleiBridge registered | `@register_worm(category="security", priority=7, cooldown_seconds=30.0)` — `expansion/nuclei.py:94` |
| Its entry point | `def scan(self, targets, ...)` — `nuclei.py:165` |
| The fleet's entry point | `scan()` with no arguments — `DnsWorm().scan()`, `NmapWorm().scan()`, `glia.execute() -> self.scan()` |

So a component is registered into the fleet, dispatched by the fleet, and cannot
execute under the contract the fleet uses. It fails, is retried, and fails again —
every cycle.

**This is the unit problem in miniature:** "232 registered components" counts
names in a registry, not parts that can be executed. At least one is structurally
unexecutable, and 209 have never run at all.

---

## Tier 3 — The applying cycle is refused, permanently, by construction

`run_cycle(apply=True)` refuses with:

```
stale_self_image:
  stale artifacts: NEURAL_MESH_FUNCTION_TODO.md, NEURAL_MESH_WIRE_OR_CUT.json,
                   NEURAL_MESH_INTEGRATION_MAP.json, NEURAL_MESH_INTEROP.mmd
```

`tools/refresh_all.py` regenerates **5 of 7** → the remaining two are
`graphify-out/graph.json` and `graphify-out/GRAPH_REPORT.md` (**stale by 90 newer
sources**). The gate is `tools/artifact_freshness.py`: stale artifacts **plus** a
graph/report mismatch.

And then the decisive measurement:

```
graphify references in chain job scripts:
  nightly_maintenance.py                 0
  run_full_pass.py                       0
  dream_cycle.py                         0
  metacog_cycle.py                       0
  run_evolution_cycle_hyper.bat          0
  run_training_orchestrator.py           0
```

**Nothing in the automation produces the graph.** It is produced only by
standalone scripts (`scripts/graphify_refresh_all.sh`, `graph_refresh_no_llm.py`,
`graphify_huge_mode.py`) invoked by hand. Every code change makes the self-image
stale again.

> **Therefore the system can never restore its own write authority.** Write
> permission depends on an artifact that no running component can regenerate, so
> the loop's ability to act is permanently dependent on a human running a tool.

The tool is also currently unhealthy: `graphify update .` has been running for
hours (2.5–6 GB resident, log last advanced 11:05), and warns
`skill is from graphify 0.9.55, package is 0.8.8. Run 'graphify install'`.

---

## Tier 4 — Even with authority, the signal was empty

Measured before this session's repairs:

| Fact | Value |
|---|---|
| Components registered | 232 |
| Components with any evidence | 23 |
| Components never observed | **209** |
| Components ever *chosen* by the decider (real) | **1** (`MetaCluster`) |
| Choice tap before the scrub | 608 rows, **408 of them test fixtures** |
| Reward | `f(severity)`, with severity in the state → oracle ≡ constant |

All four are repaired and tested, and **none of them can be exercised until
Tiers 0–3 are cleared** — which is why the repair work has not changed observable
behaviour.

---

## Tier 5 — The last fire left no trace

`main()` returns `0` on every normal path (including "another fire holds the
lock"); it returns `2` only if the lock directory cannot be created. A Task
Scheduler result of **1** therefore means an unhandled `BaseException` or a raise
in the unguarded step-2/3 region.

The traceback is **gone**: Task Scheduler discards stderr, and
`logs/azazael_chain.log` has 882 lines ending at `2026-09-20T03:50:07` — before
the 03:56 fire — with **zero** `FAIL`/`START-FAIL`/`KILLED` lines in its entire
history.

Every unguarded helper and a full fire were reproduced today and returned 0, so
the trigger was transient. **The durable defect is not the crash; it is that a
crash there is unobservable.**

---

## What it looked like when it *was* running

`logs/azazael_chain.log`, 03:20–03:50 on 9/20 — fired continuously, with each
fire lasting 41–427 seconds against a **1-minute** trigger:

```
03:25:08 START dream  pid=3156      chain done 366s
03:32:09 START evolution pid=19680  chain done 427s
03:43:07 START train  pid=19616     chain done  41s
03:44:07 START dream  pid=18708     chain done  48s
03:45:07 START evolution pid=1332   chain done  45s
03:47:07 START metacog pid=3916     chain done  53s
03:48:07 START train  pid=16612     chain done  61s
03:50:07 START dream  pid=16000     chain done  44s
```

And `logs/chain_train.log` ends:

```
STATUS: TRAINING SUCCESSFUL          <- 5000 timesteps, SAC, eval reward 227.25
SKIP overlap: previous training run still running
```

So the jobs *worked*; the cadence restarted them faster than they could finish.
That is a throughput pathology, not a functional one — but it means the on-state
was thrash, not accumulation.

---

## Ranked fixes

| # | Fix | Why it is first |
|---|---|---|
| 1 | Add a `graph` job to the chain's `JOBS` (or call the refresh from `maint`) | Removes the only human-dependent step in the write path; without it, authority can never return |
| 2 | Make the watchdog able to see the chain: check the chain **task's** enabled state and last result, from outside any chain job | It currently reports green through exactly the failure that keeps recurring |
| 3 | Enable `Azazael-Chain` (single task — the other nine stay disabled by design) | Ten disabled tasks are one outage; one task restores the whole surface |
| 4 | Give the chain a top-level exception guard that logs the traceback **and** records the failure before exiting non-zero | An exit-1 with no trace is indistinguishable from never running |
| 5 | Fix or quarantine `NucleiBridge.scan(targets)` so a registered component satisfies the fleet's `scan()` contract | A registry entry that cannot execute is worse than an absent one — it consumes a slot and reports a failure forever |
| 6 | Re-space the job intervals against measured durations (fires of 41–427s on a 300s interval) | Stops the overlap-restart thrash |

**Not done here on purpose:** enabling tasks is a production action with real
consequences — `eve` and `gosp` call LLM backends nightly and `train` runs SB3
training, so turning on the chain starts spending money and CPU. That is the
operator's call, not a side effect of a diagnosis.
