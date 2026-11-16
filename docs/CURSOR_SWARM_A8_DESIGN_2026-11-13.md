# CURSOR SWARM — sub-second verdicts, cursor-local scope, all-or-nothing landing

**Status:** design, not built. Every number carries the command that produced it.
**Date:** 2026-11-13 · **Lane:** opencode · **Implements:** A8 in `docs/ADAPTATIONS_HYPER_EDGE_2026-11-07.md`

> **Reading rule for this document.** A number is either **measured** (a command and
> its output are given), **absent** (the thing does not exist yet, so it is named as
> absent rather than estimated), or **projected** (a derivation from measured rates,
> labelled `PROJECTION` with the derivation shown). Nothing is quoted from memory.

---

## 0. What this is

A **cursor swarm** is a fan-out of *cursor agents* across the domain trees, each
cursor carrying its own hyper-edge verdict, each verdict computed in-process in
milliseconds, and the whole swarm landing or rolling back as one transaction.

It is the missing half of the hyper-edge architecture. `docs/ADAPTATIONS_HYPER_EDGE_2026-11-07.md`
§2 A8 names the requirement: *"N cursors across M domain trees applied as one atomic
land-or-rollback transaction, each cursor carrying its HED verdicts computed in-process
(ms via native Rust worm_manifest, not per-file Python spawns), one cursor per environment
(Win/WSL/Kali/Ubuntu) with hash-verified parity, placement evolved by defect priors
(head_audit gaps + golden_arrow DEBT), claim-verdict coupling at apply time,
denominator-proof sweeping."*

**Three words:** *in-process* (ms, not minutes), *transactional* (all cursors land or
none do), *cursor-local* (a cursor's verdict is about the files that cursor touched).

---

## 1. The measurements that decide the design

All measured 2026-11-13 on `C:\Azazael\.venvs\py316t\Scripts\python.exe` (3.16t),
repo `C:\Azazael\azazael`. Raw capture:
`C:\Users\clint\AppData\Local\Temp\opencode\cursor_swarm_measurements.txt`.

### 1.1 What the auditors cost today

| command | measured | exit |
|---|---|---|
| `python tools/settings_shadow.py --root .` | **105 044 ms** | 0 |
| `python tools/head_audit.py --root .` | **436 ms** | 0 |
| `python tools/reading_audit.py --glob logs/*.json` | **401 ms** | 0 |
| `python tools/leg_ledger.py logs/deep_dive.json` | **54 ms** | 0 |
| `python tools/reading_audit.py --root .` | 68 ms | **2** — `--root` is not a flag of this tool |

Two facts fall out, and both are load-bearing:

**Fact 1 — the whole-tree reading is 105 seconds.** `settings_shadow` over the whole
repository costs 105 044 ms. A swarm of 24 cursors that each spawned that would be
42 minutes of identical work. This is why A8 says *"not per-file Python spawns"*.

**Fact 2 — the same binary over a small scope is 73 ms.**

```
python tools/settings_shadow.py --root src/CORE/paths      ->    73 ms   (6 modules)
python tools/settings_shadow.py --root src/CORE/parallel  ->    81 ms   (2 modules)
python tools/settings_shadow.py --root .                  -> 105 044 ms  (whole repo)
```

**1 439× for the same binary and the same code path**, decided entirely by the scope
argument. No optimisation is needed to get this — the scope is already a parameter.

### 1.2 The spawn cost

```
python -c pass, 5 runs   ->  min 33 ms   median 34 ms   max 40 ms
```

A Python process costs ~34 ms to start. Per cursor, four auditors as subprocesses
cost ~136 ms of startup **before any work**. Twenty-four cursors: ~3.3 s of spawn
alone, and the GIL-free interpreter does not help because subprocesses do not share
memory.

### 1.3 In-process is already fast where a callable exists

```
python -c "import claim_agreement; claim_agreement.validate_ledger(p)"
   ->  0.5 ms   (22-row cursor ledger; verdicts {landed:8, held:4, rolledback:8, quarantine:2})
```

0.5 ms **in-process**, against 54 ms for the same ledger's sibling tool as a CLI
(`leg_ledger`). The ratio is the interpreter, not the algorithm.

### 1.4 The blocker: the auditors have no importable scoped entry point

Introspected live:

| module | importable callables today |
|---|---|
| `settings_shadow` | `main` only |
| `reading_audit` | `audit_file`, `main` |
| `leg_ledger` | `audit`, `main` |
| `head_audit` | `audit_lane_heads`, `main` |
| `claim_agreement` | `validate_ledger`, `main` |

`settings_shadow` and `head_audit` expose **only `main`** — argparse at module scope,
`sys.exit` at the bottom. A cursor cannot call them in-process today.

**`read_scope(paths)` on any of the four auditors: MEASURE-ABSENT.**
**In-process per-cursor verdict total: MEASURE-ABSENT** (depends on `read_scope`).
**Native `worm_manifest` import cost: MEASURE-ABSENT** (crate is not built).
**PyO3 GIL contention under 3.16t free-threading: MEASURE-ABSENT** (needs the crate).

A `PROJECTION` of the verdict phase, derivation shown:

```
PROJECTION  one cursor's verdict phase
  4 auditors, scoped, in-process, no spawn
  = 4 x (cost of a scoped read with the interpreter already warm)
  the scoped CLI read costs 73-81 ms OF WHICH the interpreter floor is 33-34 ms
  => the scoped WORK is ~40 ms, most of which is file I/O + AST parse, not compute
  => 4 auditors x ~40 ms ~= 160 ms per cursor, IF each auditor is a separate call
  => and if the scope is 3 files rather than 6, less
  NOT a sub-second-per-cursor number, and NOT claimed as one.
```

**This projection is the honest headline: extracting `read_scope` is necessary but
not sufficient.** At ~40 ms of scoped work per auditor, four auditors per cursor is
~160 ms — sub-second *per cursor*, but only if the work is not re-parsing files per
auditor. The design therefore specifies **one parse, four verdicts** (§3.2), which is
the only way to make the per-cursor number small.

### 1.5 The four auditors read four different things

This is not obvious from the names and it decides what "cursor-local" can even mean.

| auditor | what it actually reads | scope flag | cursor-scope mapping |
|---|---|---|---|
| `settings_shadow` | **source modules** — knob reads vs declared config | `--root` (dirs) | natural: the cursor's own files |
| `reading_audit` | **report artifacts** (JSON) — denominators in readings | `--glob` (files) | indirect: the cursor's reports |
| `leg_ledger` | **one deep-dive report** — leg state honesty | positional path | indirect: the cursor's own leg |
| `head_audit` | **git refs / worktrees / lane heads** | `--root` (repo) | global: not scopeable per cursor |

Only `settings_shadow` has a subject that is inherently per-cursor. `head_audit` is
inherently global. `reading_audit` and `leg_ledger` audit *artifacts the cursor
produced*, not the tree.

**This is the design's hardest constraint and it invalidates the naive "four
verdicts per cursor" shape.** See §6.2 and open question 2.

---

## 2. What already exists (measured)

| piece | where | state |
|---|---|---|
| cursor swarm vocabulary | `tools/arena_judge_swarm.py` (28 761 B), `tools/swarm_arena/` | Rust + Go + Python judge shards, seeded arena, majority vote |
| hyper-edge verdicts | `tools/{reading_audit,settings_shadow,leg_ledger,head_audit}.py` | all four run live; all four are whole-tree |
| native Rust dispatch | `native/worm_manifest/` (PyO3 0.29, 207 lines) | **no built artifact on disk; no importer** |
| cursor rendering | `tools/swarm_arena/arena.py` | renders shard-vs-shard verdicts, **not** cursors on a tree |
| cursor ledger schema | `tools/claim_agreement.py:68` | `LEDGER_KEYS` = 8 keys; `LEDGER_VERDICTS` = {landed, held, quarantine, rolledback} |
| Python cluster path | `src/CORE/WORMS/CLUSTERWORMS.py` | threading; free-threading deadlock documented (`LESSONS_MASTER #28`) |
| optimiser | `src/ML/nsga2.py` | native, numpy only |

**The gap:** the four auditors answer *whole-tree* questions. A cursor that touched
3 files gets a verdict about 3 000 files. That is not a cursor-local verdict; it is a
global one wearing a cursor's name.

---

## 3. Architecture

```
                    ┌───────────────────────────────────────┐
                    │  SWARM COORDINATOR  (Rust, tokio)     │
                    │  - parse plan once (serde, OnceLock)  │
                    │  - spawn N cursor tasks                │
                    │  - deadline-bounded fan-in            │
                    │  - all-or-nothing apply               │
                    └───────────────┬───────────────────────┘
                                    │ N tasks, parallel
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
   ┌─────────┐              ┌─────────┐              ┌─────────┐
   │ Cursor 1│              │ Cursor N│              │ Cursor M│
   │ scope:  │              │ scope:  │              │ scope:  │
   │ 3 files │              │ 3 files │              │ 3 files │
   │ ┌─────┐ │              │ ┌─────┐ │              │ ┌─────┐ │
   │ │parse│ │              │ │parse│ │              │ │parse│ │
   │ │ once│ │              │ │ once│ │              │ │ once│ │
   │ └─────┘ │              │ └─────┘ │              │ └─────┘ │
   │ 4 verdicts from that one parse                   │
   │ ┌─────┐ │              │ ┌─────┐ │              │ ┌─────┐ │
   │ │edit │ │              │ │edit │ │              │ │edit │ │
   │ └─────┘ │              │ └─────┘ │              │ └─────┘ │
   └────┬────┘              └────┬────┘              └────┬────┘
        │  verdict               │                       │
        └───────────────┬────────┴───────────────────────┘
                        ▼
              ┌───────────────────────┐
              │  COMMIT GATE          │
              │  all cursors green?   │
              │   yes → land all      │
              │   no  → roll back all │
              └───────────────────────┘
```

### 3.1 The cursor

```rust
struct Cursor {
    id:       CursorId,        // stable, hashable
    scope:    Vec<PathBuf>,    // exactly the files this cursor may touch
    verdict:  CursorVerdict,   // the readings, computed in-process
    mutation: Option<Mutation>,// the edit, held until the gate passes
    env:      Environment,     // Win / WSL / Kali / Ubuntu
}
```

The scope is the centre of gravity: it makes the verdict cursor-local, makes the audit
fast (§1.1), and makes rollback well-defined.

### 3.2 One parse, four verdicts

§1.4's projection says the win comes from not re-parsing files four times. The shape:

```
PARSE ONCE per cursor scope:
    parse(paths) -> ParsedScope { module_asts, config_knobs, file_digests, ... }
VERDICTS FROM THAT ONE PARSE:
    settings  <- config_knobs          (the module's knob reads)
    reading   <- file_digests + reports the cursor produced
    ledger    <- the cursor's own rows
    head      <- global (NOT scoped)   -- see below
```

`head_audit` reads git refs and worktrees — it has no per-cursor subject. Two options,
and the design takes the second:

| option | verdict |
|---|---|
| every cursor runs `head_audit` | 24 x 436 ms of identical global work, and the answer is the same for all 24 |
| `head` becomes a **swarm-level** verdict, computed once | 436 ms once; the cursor's own verdict set is the three that have a per-cursor subject |

**A cursor's green means: its scope is clean, its reports carry denominators, its own
rows are well-formed.** The swarm's green additionally means: no head moved. Both are
recorded; they are not confused. §6.2 records the open question this creates.

### 3.3 In-process means in-process

The four auditors are CLI scripts (`argparse` at module scope, `sys.exit` at the
bottom). Two of them expose only `main`. They cannot be called by a cursor as they
stand.

**The enabling change is a pure extraction:**

```
tools/settings_shadow.py
  + export function read_scope(paths: list[Path]) -> SettingsShadowResult
  + main() calls read_scope over the tree and prints  --  behaviour unchanged
```

The acceptance bar is that the CLI's output is **byte-identical before and after**.
Not "close enough" — identical. A cursor calls `read_scope`; a human runs the CLI;
both get the same verdict for the same inputs. If the extraction changes a number,
the extraction is wrong.

### 3.4 Placement: defect priors, then evolved

A8: *"placement evolved by defect priors (head_audit gaps + golden_arrow DEBT)."*

Two live defect sources, both already shipped:

- **`head_audit` gaps** — `tools/head_audit.py` finds lane/head drift, prunable
  branches, and refs holding commits no other ref names. A gap is a place where the
  tree's claim about itself is false.
- **`golden_arrow` DEBT** — `tools/golden_arrow.py` records known-failing test files in
  `logs/golden_arrow_baseline.json`. DEBT is a place where the tree's claim about its
  own behaviour is false.

**Placement rule (first version, deterministic, no learning):**

```
priority(scope) = SUM over defect sources of  weight[source] * severity(source, scope)
```

Weights start at **1.0 for every source** — there is no measurement yet that would
justify a different number, and inventing one is the failure mode the canon names
("optimizing prose against proxy metrics").

Placement is then **evolved**: a swarm run produces fitness — defects closed, defects
opened, wall time, rollback rate — and `src/ML/nsga2.py` selects the next generation of
weights. **Fitness is measured on the live swarm, never simulated** (E2R-1): a
simulated score teaches the optimiser nothing about the real tree.

### 3.5 Transactional apply: all cursors land, or none

1. **Worktree isolation (preferred).** Every cursor works in its own `git worktree`.
   Land = merge all worktrees in one commit; rollback = delete them. The main tree is
   never partially applied.
2. **Staged patch set.** If worktrees are impractical: collect every cursor's diff,
   verify all, then `git apply` as one patch. A failure mid-apply needs an inverse.
3. **Never.** Partial application is a defect, not a degraded mode.

**Rollback is proven, not asserted.** The acceptance test: force one cursor to fail,
run the swarm, assert the **whole tree's sha256 is unchanged** — not merely the
failing cursor's files.

### 3.6 One cursor per environment, hash-verified parity

A8: *"one cursor per environment (Win/WSL/Kali/Ubuntu) with hash-verified parity."*

The same cursor runs in each environment. Parity = **hash the cursor's scope after the
edit** in each environment and compare:

- **match** — the edit is environment-independent. This is the strong claim.
- **mismatch** — the edit behaves differently per environment. This is a **finding**,
  not a retry: it usually means the cursor's scope contains a platform-conditional path.

`native/worm_manifest/src/lib.rs:26` is the pattern to copy — a `OnceLock` singleton
parsed once from an embedded JSON via `include_str!`, exposed as PyO3 functions. The
swarm's plan file is the same shape.

### 3.7 The `worm_manifest` gap is a prerequisite, not the solution

A8's parenthetical — *"ms via native Rust worm_manifest, not per-file Python
spawns"* — points at `native/worm_manifest`, and that crate is **not wired**:

```
native/worm_manifest/     Cargo.toml (pyo3 0.29), src/lib.rs (207 lines, 8 pyfunctions)
                          -> no .pyd, no .dll, no importer anywhere in src/ or packages/
```

**Two options, honestly compared:**

| option | cost | buys |
|---|---|---|
| **A. wire `worm_manifest`** | build the crate, add a PyO3 import path | one fast manifest lookup; removes the 38 s Python cold-start import chain the crate was written for (`native/worm_manifest/Cargo.toml:4`) |
| **B. extract `read_scope` from the auditors** | extract from four CLI scripts | the actual sub-second win — the auditors *are* the hot path |

**B is the design; A is a prerequisite that is worth doing anyway.** A8's parenthetical
reads as if the crate *is* the solution. It is not: `worm_manifest` is a registry
lookup, and the cursor's cost is in the auditors. Saying this plainly is part of the
design — a plan that names the wrong bottleneck costs a cycle to discover.

### 3.8 Free-threading: Rust does not make PyO3 free

3.16t is free-threaded, but **PyO3 still acquires the interpreter lock** to touch
Python objects. A Rust coordinator that spends its time in Python calls does not get
free-threading for free.

So the Rust coordinator does everything it can *without* Python: parse the plan, compute
scopes, schedule, enforce deadlines, check parity hashes, commit. Python is called only
for the scoped reads — once per cursor, after one parse.

Whether those reads actually run in parallel under 3.16t is **MEASURE-ABSENT** and must
be measured before the concurrency claim is made (§6.2).

---

## 4. The three upgrade layers: colour, tracer, pulse

The v0 cursor swarm (`C:/Users/clint/LIVEVIEW_CURSOR_SWARM_V0.html` + `.jsonl`)
renders five static glyphs and nothing else. Measured against the ledger:

| v0 renders | v0 ledger holds | verdict |
|---|---|---|
| 1 glyph per cursor, final verdict only | **4 stages per cursor**: `[placed]` → `[verified]` → `[applied]` → `[settled]` | the progression is **never displayed** |

So all three upgrades are recoveries of data the tree already has.

### 4.1 COLOUR — derive, never invent

Two palettes already exist in this tree and the v0 HTML ignores both:

| source | what it holds | measured |
|---|---|---|
| `tools/gephi_mesh_pipeline.py` `NATURE_COLORS` | the canonical nature palette — **27 named natures** | `monitor_theme.py` says it is "the single place to change a colour", because "every monitor then re-invented its own hex strings per card, so the *same* nature could be blue on the graph and pink on the dashboard" |
| `~/yggdrasil_forest/forest_manifest.json` | per-domain palette — **11 domains × 5 colours** (`bg`, `trunk`, `leaf`, `text`, `dim`) | every domain has an entry; no invented hexes |
| `tools/monitor_theme.py` `SEMANTIC` | the semantic verdict colours | `ok #3fb950`, `warn #d29922`, `advisory #d29922`, `error #f85149`, `unknown #8b949e` |

The v0 HTML hardcodes `#2ea043 / #d29922 / #f85149` — close to the semantic set but not equal (`#3fb950` vs `#2ea043`). It is a **re-invention**, which is exactly the failure `monitor_theme.py` documents.

**The rule for the swarm:**

1. **Verdict colour comes from `monitor_theme.SEMANTIC`**, not from a literal in the view:
   `landed → ok`, `held → advisory`, `rolledback → error`, `quarantine → unknown`.
2. **Domain colour comes from `forest_manifest.json`** (`bg`, `trunk`, `leaf`, `text`, `dim`) — one palette per domain, 11 domains, no invented hexes.
3. **Category colour comes from `NATURE_COLORS`** where the category is mapped.

**The mapping is incomplete, and that is a finding, not a detail to paper over.** The hives atlas has **36 tree categories; 24 map to `NATURE_COLORS`; 12 do not**:

```
unmapped: axon, consolidation, dendrite, envmesh, expansion, glia,
           metabolic, ml, network, plasticity, thalamus, utility
```

`ml` is a **domain** in `forest_manifest.json`, not just a category. The rule is therefore:

- a category with no `NATURE_COLORS` entry renders in the **domain's** colour, not in an invented one;
- an unmapped category is never given a random hex — it is drawn in the domain colour and **flagged as unmapped**, the way `monitor_theme.nature_is_mapped()` already does for natures.

That is the same discipline the tree already applies to an unmapped nature: `UNMAPPED_NATURE` grey rather than a plausible-looking invented colour.

### 4.2 TRACER — the stage progression the ledger already carries

The v0 ledger's per-cursor rows, measured:

| cursor | frame | stage in the claim | verdict |
|---|---|---|---|
| c1 | 1 | `gate_str_replace guard scan [placed]` | landed |
| c1 | 2 | `…[verified]` | landed |
| c1 | 3 | `…[applied]` | landed |
| c1 | 4 | `…[settled]` | landed |

Four stages per cursor, **in the ledger, invisible in the view**. The v0 HTML contains no occurrence of `placed`, `verified`, `applied`, `settled`, `frame`, `fetch`, `jsonl` or `FileReader` — it is a **static HTML file with the cursor states hard-coded as five `<div>`s. It reads no data at runtime.

**The tracer is therefore the ledger's stage axis, made visible.** Concretely:

1. The view reads the ledger (the `.jsonl`) at runtime instead of hard-coding glyphs.
2. Each cursor renders as a **4-node trail** — `placed → verified → applied → settled` — coloured by that row's verdict.
3. A cursor's final glyph is the verdict of its **last** row; a row's colour is the verdict of *that* row, so a cursor that rolled back shows the rollback at the stage where it happened.
4. The quarantine strip keeps its rule: a row without `tree`/`node` is quarantined, never on the tree. Measured: **2 of 22 rows** are quarantined (`q1` claim without position, `q2` verdict without evidence) — the v0 already implements that rule, and the tracer makes it visible.

**The tracer is also the anti-cheat surface.** `claim_agreement.py` validates the 8-key schema and the 4 verdicts
(`landed`, `held`, `quarantine`, `rolledback`) — a verdict vocabulary that is already the tree's. The tracer therefore
renders **the same four verdicts** the ledger validator accepts, and it must not invent a fifth.

### 4.3 PULSE — liveness, which no cursor concept has today

There is no liveness notion for cursors anywhere in the tree. `tools/lane_watchdog.py` is the closest precedent and it
is about **lanes**: "heartbeat for lanes: page when claims outlive their lease", `LEASE_S = 30 * 60`.

A cursor needs the same property: a cursor that stopped making progress must be distinguishable from one that is
merely slow. Without it, a stalled cursor looks like a healthy one.

**The pulse is a heartbeat row, and it is derived from the ledger — not from a clock the view invents.**

| pulse property | source | rule |
|---|---|---|
| `age_ms` | now − the row's frame time | needs a timestamp: **the v0 schema has no time column** — see below |
| `stage` | the row's `[placed]`…`[settled]` marker | already present |
| `verdict` | the row's verdict | already present |
| `health` | derived: `stale` if the cursor's last row is older than a lease | mirrors `CLAIM_LEASE_SECONDS` |

**Schema consequence, and it is the one real change to the ledger:** the 8-key schema
(`frame`, `cursor_id`, `tree`, `node`, `verdict`, `claim`, `prev_hash`, `hash`) has **no timestamp**, and
`claim_agreement.py` enforces *exact* key equality:

```python
LEDGER_KEYS = {"frame", "cursor_id", "tree", "node", "verdict", "claim", "prev_hash", "hash"}
if keys != LEDGER_KEYS: bad.append(...)
```

So a pulse **cannot** be a 9th column without breaking the validator, and the validator is the tree's own
guard (`tools/claim_agreement.py` is wired into the hyper-edge leg set, `config/defaults.json` `hyper_edge.claim_agreement`).

Three ways out, and the design must pick one:

| option | change | cost |
|---|---|---|
| **A. add a 9th column `ts`** | breaks `LEDGER_KEYS` exact-equality check | the validator must be updated in the same commit; the ledger hash chain changes shape (every existing row's hash is over its own 8 keys, so old rows stay valid under a *superset* rule) |
| **B. derive liveness from `frame` + the sequence** | no schema change | liveness becomes "the cursor has a next stage", i.e. in-flight vs settled — no wall-clock age |
| **C. a separate pulse file** | new artifact | two files to keep consistent — the tree dislikes this (`tools/audit_tools` complains about "a cursor swarm is clean" claims) |

**The design picks A, with the validator widened to "required keys ⊆ present keys" and the hash computed over
exactly the 8 canonical keys**, so:

- every existing row keeps its hash (the hash is over the 8 keys; a 9th column would change it — no: if the hash
  covers only the 8 canonical keys, then adding `ts` does **not** change any hash, and the chain stays valid);
- old rows (no `ts`) validate;
- new rows carry `ts` and the view can compute age.

That is a **backward-compatible schema extension**: the hash covers the canonical 8 keys, optional columns are
excluded from the hash. `claim_agreement.py` must therefore hash over `LEDGER_KEYS` rather than "all keys except
hash" — a one-line change to the validator, and it makes the chain robust to added columns.

But careful: changing the validator's hash rule changes the meaning of existing rows? No — existing rows were hashed
over exactly their 8 keys, which equals the canonical set. So the rule is unchanged for them. **Backward compatible.**

### 4.4 What the three layers need, in one table

| layer | needs from the tree | needs from the swarm | blocked by |
|---|---|---|---|
| **colour** | `monitor_theme.SEMANTIC`, `forest_manifest.json` palettes, `NATURE_COLORS` | a view that reads the ledger and the manifest | 12 unmapped categories need the domain fallback rule (§4.1) |
| **tracer** | the 4-stage markers already in the ledger | a view that renders 4 nodes per cursor | the v0's static HTML must become data-driven |
| **pulse** | `lane_watchdog.py`'s lease idea | a heartbeat per cursor | the ledger needs a `ts` column (§4.3 option A) and the validator's hash rule widened |

---

## 5. Data shapes

### 5.1 The plan

```json
{
  "swarm_id": "2026-11-13-a8",
  "envs": ["windows", "wsl", "kali", "ubuntu"],
  "deadline_ms": 30000,
  "cursors": [
    {
      "id": "c01",
      "scope": ["src/CORE/WORMS/CLUSTERWORMS.py"],
      "intent": "thread-safety defect in cluster spawn",
      "defect_prior": {"source": "head_audit", "key": "..."}
    }
  ]
}
```

### 5.2 The cursor result

```json
{
  "cursor_id": "c01",
  "env": "windows",
  "verdicts": {
    "settings": {"ok": true, "ms": 41, "detail": "3/3 modules read no undeclared knob"},
    "reading":  {"ok": true, "ms": 12, "detail": "2/2 reports carry a denominator"},
    "ledger":   {"ok": true, "ms": 0.5, "detail": "22 rows well-formed"}
  },
  "scope_hash_before": "…",
  "scope_hash_after":  "…",
  "parity": {"wsl": "match", "kali": "match", "ubuntu": "match"},
  "state": "green|red|timeout"
}
```

**Denominators are mandatory** (A18 / HED-9): a verdict without a denominator is not a
verdict. `settings` above says "3/3 modules", never "modules".

### 5.3 The swarm result

```json
{
  "swarm_id": "2026-11-13-a8",
  "cursors": 24,
  "green": 23, "red": 1, "timeout": 0,
  "verdict_phase_ms": 1234,
  "apply_phase_ms": 4120,
  "committed": false,
  "rollback_proof": "tree sha256 unchanged"
}
```

---

## 6. What is explicitly not built, and what is not known

### 6.1 Refusals

| thing | why not |
|---|---|
| a new audit engine | the four auditors exist and are correct; the fix is scope, not replacement |
| a simulated fitness function | E2R-1: train on live experience; a simulator teaches nothing |
| per-file Python subprocesses | 34 ms spawn each; 24 cursors x 4 auditors is ~3.3 s of startup before any work |
| a Rust reimplementation of the auditors | a second implementation drifts from the maintained one |
| partial-apply support | a half-landed swarm is a defect, not a degraded mode |
| cross-env parity as a retry loop | a hash mismatch is a finding about the edit, not a flake |

### 6.2 Open questions (each one is a decision someone must make)

1. **Where do cursor *intents* come from?** Defect priors pick *where*, not *what*. The
   plan's intent per cursor is unsourced.
2. **What does a scoped verdict mean per auditor?** Only `settings_shadow` has a
   per-cursor subject. `reading_audit` audits artifacts, `leg_ledger` audits one report,
   `head_audit` audits the whole repo. A scope of 3 files changes the *question*, and
   the CLI's guarantee ("all 3 000 files have denominators") does not transfer to it.
   **Until each auditor's scoped semantics are written down, "green" is green about a
   question nobody asked.**
3. **Do the scoped reads actually run in parallel under 3.16t?** MEASURE-ABSENT. PyO3
   still takes the interpreter lock. The concurrency claim is unproven until measured.
4. **Does a cursor edit files or propose edits?** An autonomous-editing swarm needs a
   licence boundary; a proposing swarm needs a human or a gate. The design assumes the
   latter; the assumption is not yet justified.

---

## 7. Build order

Each step ships alone and is verified by a command.

| # | step | verification |
|---|---|---|
| 1 | `read_scope` extracted from `settings_shadow`; **CLI output byte-identical** | `python tools/settings_shadow.py --root .` output identical before/after; `read_scope` on 3 files returns in < 50 ms |
| 2 | the same extraction for `reading_audit`, `leg_ledger` | same shape of proof, per tool |
| 3 | native `worm_manifest` built and importable | `python -c "import worm_manifest; print(worm_manifest.get_worm_count())"` succeeds; import cost < 50 ms |
| 4 | `native/swarm` crate: plan parse, N cursors, deadline fan-in | `cargo test -p swarm`; a hung cursor does not block the fan-in |
| 5 | one-parse-four-verdicts cursor, parallel | 24 cursors; per-cursor verdict < 1 s wall; **parallelism measured**, not assumed |
| 6 | transactional apply: worktree per cursor | force one cursor red ⇒ **whole-tree sha256 unchanged** |
| 7 | cross-env parity by scope hash | 4 envs agree ⇒ `match`; a platform-conditional path ⇒ mismatch **reported as a finding** |
| 8 | placement by defect priors, then evolved by live fitness | a swarm lands in a `head_audit`-flagged scope; NSGA-II selects from measured outcomes only |
| 9 | swarm result persisted and rendered by the arena | `tools/swarm_arena/arena.py` renders per-cursor verdicts |

**Step 1–2 are the sub-second claim.** Steps 3–9 are correctness and reach. Without
steps 1–2 nothing else makes the swarm fast.

---

## 8. References

- `docs/ADAPTATIONS_HYPER_EDGE_2026-11-07.md` §2 A8 — the requirement
- `native/worm_manifest/src/lib.rs` — the parse-once singleton pattern
- `tools/arena_judge_swarm.py`, `tools/swarm_arena/` — the arena judging model
- `tools/claim_agreement.py:68` — the cursor ledger schema and verdict vocabulary
- `src/CORE/WORMS/CLUSTERWORMS.py` — the Python threading path and its free-threading
  deadlock (`LESSONS_MASTER #28`)
- `src/ML/nsga2.py` — the optimiser for evolved placement
- `tools/head_audit.py`, `tools/golden_arrow.py` — the two defect-prior sources
- `C:\Users\clint\AppData\Local\Temp\opencode\cursor_swarm_measurements.txt` — the raw
  measurement capture behind every number above
