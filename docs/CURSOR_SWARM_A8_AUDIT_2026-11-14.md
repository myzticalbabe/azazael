# CURSOR SWARM (A8) — AUDIT, 2026-11-14

**Subject:** `docs/CURSOR_SWARM_A8_DESIGN_2026-11-13.md` (603 lines).
**HEAD at audit time:** `ea5402e8`. **Interpreter:** `C:/Azazael/.venvs/py316t/Scripts/python.exe`.
**What this is:** a measurement of the design against the live tree, plus the gaps that
would cost a build cycle if they surfaced during implementation.
**What this is not:** a build. No cursor code exists yet, and this audit adds none.

---

## 0. Verdict in one paragraph

The design is buildable and its central discipline — refusing to call a whole swarm
"sub-second" while projecting ~160 ms for one cursor — survives measurement. The five
blocking gaps are not in the Rust coordinator; four of them are in how a verdict is
*defined* (what scope is read, what an absent report means, what an unreachable environment
means, when a deadline cancels). The largest measured problem is one the doc never states:
**every auditor reads the worktree, not the index**, so `--root .` scans 2.3x the modules
the swarm can change, and 55% of what it scans belongs to `Project_ELIZA`.

---

## 1. Measurements, with their denominators

Every figure below is a command run on 2026-11-14 in this tree. The doc's figure sits
beside it. Where the two runs do not share a denominator, the delta is recorded as *not
comparable* rather than as a speed-up.

| reading | command | 2026-11-14 | doc (2026-11-13) | comparable? |
|---|---|---:|---:|---|
| whole-tree settings | `settings_shadow.py --root .` | **57 561 ms** over **10 112 modules** | 105 044 ms (modules not recorded) | no — denominator unrecorded in doc |
| one package | `settings_shadow.py --root src/CORE/paths` | 70.7 ms over 3 modules | 73 ms | yes |
| one directory | `settings_shadow.py --root src/CORE` | **4 811 ms** over **344 modules** | not in doc | new |
| lane heads | `head_audit.py --root .` | 281 ms | 436 ms | denominators unrecorded either side |
| log verdicts | `reading_audit.py --glob logs/*.json` | 83.7 ms over **67 files** | 401 ms (glob unrecorded) | no |
| ledger | `leg_ledger.py logs/deep_dive.json` | 50.2 ms | 54 ms | yes |

Two of those deltas look like 2x–5x speed-ups and are not: the doc records a wall time
without the population it ran over, which is the defect HED-9 names. They are recorded
here as **not comparable**, never as improvements.

**Worktrees:** `git worktree list | wc -l` = **1**. A figure of 24 worktrees has been
carried in conversation as a cost driver; it is not reproducible today and is used nowhere
in this audit.

**Disk:** 679 G used of 756 G, **90%**, 77 G free. The design's 2 GB floor is not close to
being breached, but the 5.4 GB DirectMemory store and any per-cursor worktree share this
volume.

---

## 2. What "sub-second" actually buys, from the cost curve

Three points, all measured today:

```
   3 modules    70.7 ms   (src/CORE/paths)    -> 23.6 ms/module
 344 modules  4 811  ms   (src/CORE)          -> 14.0 ms/module
10112 modules 57 561 ms   (.)                 ->  5.7 ms/module
```

Cost per module **falls** as scope grows, the signature of a fixed start-up cost plus a
marginal per-file cost. A two-point fit through the 3-module and whole-tree points gives a
53.6 ms intercept and a 5.69 ms/module slope — and that line predicts 2 010 ms for
`src/CORE`, where the measured value is 4 811 ms. So the model is **not linear** and
per-file cost is content-dependent (2.4x between two of the three points). The honest
statements:

- a scoped read of **a few dozen modules** is tens of milliseconds;
- four auditors per cursor over one parse is the ~160 ms projection in §1.4, and today's
  numbers are consistent with it;
- the claim that fails is not "160 ms per cursor" — it is any sentence saying "the swarm is
  sub-second", because an all-or-nothing landing costs the **slowest** cursor, and
  `settings_shadow` alone costs 57 s when a cursor's scope is `.`.

**A cursor's scope is a budget, not a label.** At the measured marginal cost a sub-second
settings verdict covers roughly 30–100 modules depending on their content. The plan format
in §5.1 should carry that ceiling, and the coordinator should reject an over-budget scope
at parse time instead of timing out at run time.
---

## 3. Blocking gaps

### B1 — The auditors read the worktree, not the index

`settings_shadow.py:325` is `sorted({p for root in roots for p in root.rglob("*.py")})`.
Measured today: **10 112** `.py` files on disk under `.`, against **4 437** tracked in the
index. The difference is not noise:

```
 5586  Project_ELIZA          (a foreign tree)
  875  src                    (the tree a cursor's scope names)
  823  build                  (generated)
  567  tests
  415  MAAT
  412  tools
  379  nuitka_build_backup    (generated)
```

More than half of every whole-tree verdict concerns a tree the swarm will never edit, and
two of the top contributors are build output. Two consequences the design must absorb:

1. A verdict's denominator is not the scope's denominator. `settings_shadow --root .`
   reporting "85 key(s) read across 10 112 module(s)" invites a reader to conclude the
   *scope* was 10 112 modules.
2. A cursor scoped to `src/CORE/WORMS/CLUSTERWORMS.py` and a cursor scoped to `.` read
   different universes, so their verdicts are not comparable and must never be summed into
   a swarm summary.

**Fix:** `read_scope` enumerates through `git ls-files` (the index), filtered to the scope
paths, and refuses a scope outside the index with a named remedy. This also makes the
per-cursor hash in §3.6 meaningful: hashing untracked files hashes content the commit will
not contain.

### B2 — No disjoint-scope rule, so two cursors can collide at merge

§3.5 lands every worktree in one commit, and nothing forbids two cursors from declaring
overlapping scopes. Two cursors editing `src/CORE/WORMS/CLUSTERWORMS.py` produce two valid
diffs and one conflict, so "all green" is false precisely at the landing the verdict phase
already reported as successful. §5.1 carries `scope` as a list of paths with no uniqueness
constraint.

**Fix:** reject a plan whose scopes are not pairwise disjoint, at parse time, naming both
cursor ids and the intersecting path. Sort the flattened scope list and compare adjacent
entries; no scheduling machinery required.

### B3 — A cursor with no report artifact reads as `ok`

§5.2 makes `state` one of `green|red|timeout` and `verdicts` an object keyed by whatever
ran. A cursor whose auditor child died before writing a verdict produces `{"verdicts": {}}`,
and a summariser counting `all(v["ok"] for v in verdicts.values())` returns `True` over an
empty set. That is HED-9's failure exactly: 0/0 reported as a pass, failing in the
direction that hides work.

**Fix:** make "no verdict" its own state (`absent`), and require every verdict to carry a
non-zero denominator before it may be `ok`. Make `verdicts` a list with a required
`denominator` field rather than a free-form object.

### B4 — Parity has no `blind` state

§3.6 defines parity as `match` or `mismatch` across four environments. An unreachable
environment neither matches nor mismatches, and any implementation that defaults a missing
comparison to `match` converts "1 of 4 was unreachable" into the strongest claim in the
document. Not hypothetical: the commit gate has reported the WSL leg unreachable in this
tree, and nothing in the design distinguishes that from agreement.

**Fix:** parity is `match | mismatch | blind`, with `blind` carrying the probe error. A
swarm result containing any `blind` may not say "hash-verified parity"; it says "parity 3/4
verified, 1 blind (wsl: <error>)". This is HED-11's four-states rule applied to
environments instead of legs.

### B5 — Build-order step 1 is undone, restated with a measurement

The design's first step is extracting `read_scope` from `settings_shadow`. Confirmed absent
today: `grep -rn "def read_scope" tools/ src/` returns nothing. All four auditors still
expose only `main()`, with argparse at module scope and `sys.exit` at the bottom, so a
cursor cannot call any of them in-process. Steps 1–2 are the entire sub-second claim (§7
says so explicitly), and nothing later in the order can be measured until they land.

---

## 4. Correctness gaps

### C1 — §4.3 contains two contradictory hash rules, left in the file

Lines 461–465 read, verbatim:

> every existing row keeps its hash (the hash is over the 8 keys; a 9th column would
> change it — no: if the hash covers only the 8 canonical keys, then adding `ts` does
> **not** change any hash, and the chain stays valid)

The self-correction is honest and belongs in a working note, not in a section an
implementer reads as a specification: read line 464 alone and it says the opposite of what
the design chose. Worse, §4.3 concludes the validator must hash **over `LEDGER_KEYS`**
rather than "all keys except `hash`" — and `tools/claim_agreement.py:111-113` currently
does the latter:

```python
sha256(json.dumps({k: v for k, v in row.items() if k != "hash"}, sort_keys=True))
```

So the required change is a one-line edit whose blast radius is **every existing row**: if
any row already carries a non-canonical key, its hash was computed over 9 keys and will not
verify under the 8-key rule. The design says only "the chain stays valid". That is a
migration, and it needs a pre-flight count before it is called a one-liner.

**Fix:** delete the self-correction, state the chosen rule once, and make the migration a
numbered step that reports how many rows will fail before the change.

### C2 — Rollback proof by whole-tree sha256 is racy and expensive

§7's acceptance test is "force one cursor red, assert the whole tree's sha256 is
unchanged". Hashing the whole worktree includes files another process may touch mid-run, so
a red test can fail for reasons the swarm did not cause, and a green test can pass because
two changes cancelled. With 10 112 `.py` files plus everything else tracked, it is also the
most expensive assertion in the suite.

**Fix:** prove the property structurally. `git ls-tree -r HEAD` object ids are immutable
and cheap, and an empty `git status --porcelain` proves the worktree matches the index.
Both are exact, neither races a concurrent writer the way a content hash does, and together
they are an order of magnitude faster.

### C3 — Deadline semantics are undefined

§3 has "deadline-bounded fan-in" and §5.2 has a `timeout` state, but no rule says whether
the coordinator cancels a slow cursor or waits. All-or-nothing landing makes this wrong in
both directions: cancel too eagerly and a cursor 50 ms from done is lost; wait and the
deadline is decorative. Wall time is the slowest cursor either way, so `deadline_ms: 30000`
under a 57 s whole-tree scope is unsatisfiable before the first cursor starts.

**Fix:** `deadline_ms` bounds the fan-in. A cursor past the deadline is cancelled and
reported `timeout` with elapsed ms and the phase it was in. Cancellation must be
cooperative at phase boundaries (parse / verdict / edit), never a kill, or a cursor killed
mid-edit leaves a worktree that §3.5's rollback then has to reason about.

### C4 — `monitor_theme` cannot distinguish `warn` from `advisory`

If a cursor's state renders through the house palette, two distinct severities arrive at
one colour:

```
tools/monitor_theme.py:110   "warn":     ("#d29922", "rgba(210,153,34,0.28)")
tools/monitor_theme.py:111   "advisory": ("#d29922", "rgba(210,153,34,0.28)")
```

and the module's own docstring at line 27 says `SEMANTIC` is "state, and only state: ok /
warn / error / unknown" — yet `advisory` is in that map. Either `advisory` is a state (the
docstring is wrong) or it is a severity (it does not belong in the state map). A swarm
summary that reports both renders them identically.

### C5 — The title promises what §1.4 refuses

Title: "sub-second verdicts". §1.4: "NOT a sub-second-per-cursor number, and NOT claimed as
one." Both are correct about different things — per cursor versus per swarm — but the title
is the part a future session reads before quoting. §1.4 should be reachable from the title,
and the swarm-level number should be named as what it is: the slowest cursor, bounded by a
scope budget.
---

## 5. Improvements, ranked by cost

| # | improvement | why | cost |
|---|---|---|---|
| **I1** | enumerate scope through the index (B1) | makes every denominator mean the scope | one function, ~40 lines |
| **I2** | reject non-disjoint plans (B2) | turns a merge conflict into a parse error | ~10 lines |
| **I3** | `absent` state + mandatory denominator (B3) | closes the 0/0 pass | schema change, no code yet |
| **I4** | `blind` parity state (B4) | stops unreachable reading as agreement | one enum, one probe-error field |
| **I5** | `git ls-tree` rollback proof (C2) | exact, cheap, race-free | replaces one acceptance test |
| **I6** | scope ceiling in the plan format (§2) | a 57 s scope cannot meet a 30 s deadline | one validation constant |

None of these touch the Rust coordinator. That is the useful result: the design's
expensive part is sound, and every gap sits in the contract around it.

---

## 6. The cursor glyph

A8 asks for cursors that look like the Vulcan salute. Two glyphs are added:

- `tools/swarm_arena/cursors/vulcan_salute_32.svg` — 32x32, `data-hotspot="8.5,2"`
- `tools/swarm_arena/cursors/vulcan_salute_16.svg` — 16x16, `data-hotspot="4.25,1"`

Geometry, from the salute's own description (palm forward; index and middle travel
together, ring and little travel together, the split opening between middle and ring):

- index+middle as one pair with tips at `y 2..3`, ring+little as the other at `y 6..7`, so
  the pairs sit at different heights and the split survives being shrunk;
- the V is cut from `(14,7)` to an apex at `(16,16)` and back up to `(18,7)`;
- the thumb is a lobe crossing the palm low and left, `(7.5,22) -> (2,19.5) -> (7.5,16.5)`;
- white fill with a `#141414` stroke, so the silhouette reads on a dark desktop and the
  outline survives on a light one.

**Verified by rendering, not by description.** Both files were inlined into an HTML page and
captured with headless Chrome at 32 px, 180 px and 16 px, on a `#202020` background and in
a white box (`logs/salute_check.png`). The first two attempts read as a mitten — a narrow
slot instead of a V, both finger pairs at one height, and a thumb shaped like a pennant —
and were discarded after looking at them, not after reasoning about them.

**What this is not:** an anatomically faithful hand, or a substitute for the platform
`.cur`/`.ani` a real cursor needs. It is the vector master a build step would compile. No
`.cur` build step exists.

**Superseded 2026-11-14 — something loads them now.** `tools/swarm_arena/swarm_view.py`
reads both SVGs through `cursors/registry.json`, takes the hotspot from each file's own
`data-hotspot` (a registry/file disagreement exits 2), and renders the swarm as an
on-screen page of salute cursors whose fingertips sit on the nodes they scored. Measured
on the arena corpus: `cursors: 12 drawn: 12 absent: 0 blind: none`, selftest
`hotspot_misaligned=0 … CHAIN=OK`, slowest cursor 685 ms of a 900 ms budget, 0 rows
quarantined. The graphics claim is therefore a rendered artifact, not a description; the
`.cur` claim above is unchanged.

---

## 7. Measured absent, or not inspected

- **`read_scope`** — absent from all four auditors (B5).
- **`native/swarm` crate** — absent; `native/` contains only `worm_manifest`.
- **`worm_manifest` cdylib** — `Cargo.toml` is correct (`crate-type = ["cdylib"]`, pyo3 0.29,
  `extension-module`), `target/debug/deps` holds pyo3 and serde build artefacts, and no
  `libworm_manifest` artifact exists. Cargo ran; the cdylib did not land. The doc's
  "MEASURE-ABSENT: native import cost" therefore still holds and cannot be closed by
  reading the manifest.
- **WSL / Kali / Ubuntu parity** — not probed here. B4 is written from the design and from
  the commit gate's report, not from a fresh four-environment run.
- **`C:/Users/clint/LIVEVIEW_CURSOR_SWARM_V0.html`** — exists (3 134 bytes) and has never
  been rendered in this session. Not inspected; no claim is made about it.

---

## 8. Delta to the build order in §7

The nine steps stand, with five changes:

1. **Step 1** gains B1: `read_scope` enumerates the index, not the worktree, and its
   acceptance test is a module count matching the scope's `git ls-files` count.
2. **New step 2.5:** plan validation — disjoint scopes (B2) and a scope ceiling (§2). Both
   are parse-time rejections with no runtime cost.
3. **Step 4** gains C3: the deadline cancels at phase boundaries and reports elapsed ms.
4. **Step 6** replaces the whole-tree sha256 with `git ls-tree -r HEAD` plus an empty
   `git status --porcelain` (C2).
5. **Step 8** gains the `blind` parity state (B4) before it may claim hash-verified parity
   in any environment.

The numbered migration for `claim_agreement.py`'s hash rule (C1) is a prerequisite for step
5 and must be counted, not assumed clean.

---

## 9. Closed after the audit (2026-11-14)

Two of the six §5 improvements touch the arena view that draws the cursors. Both are now
instruments in `tools/swarm_arena/swarm_view.py`, not recommendations. The other four
(I2, I3, I4, I6) were already enforced by the same module when it was written — the §5 list
is ordered by cost, not by when it landed.

**I1 / B1 — index-based `read_scope`.** `read_scope(paths)` enumerates
`git ls-files -z -- <paths>`, so a cursor's universe is what the commit will contain.
Measured on the view's own scope, 2026-11-14:

```
scope: tools/swarm_arena — 13 files, 4 modules in the index (4 on disk)
```

The page prints the index count and the worktree count side by side, so
`85 key(s) read across 10 112 module(s)` can no longer be read as the scope's
denominator. Refusal was verified in both directions, and each exits **2** (the module's
documented "could not render"), not 1:

```
--scope tools/swarm_arena/out/swarm_view.html   (exists, untracked)
  scope outside the index: … remedy: `git add tools/swarm_arena/out/swarm_view.html` —
  read_scope counts the index, and an untracked path is content the commit will not contain
--scope tools/swarm_arena/nope.py               (absent)
  scope outside the index: … remedy: name a tracked path that exists (checked: …nope.py)
```

**I5 / C2 — rollback proved structurally.** `rollback_proof(paths)` reads
`git ls-tree -r HEAD` object ids plus `git status --porcelain` over the same scope.
Negative control, run with this file edited and uncommitted:

```
rollback: HEAD fe526e1b · 13 blobs · scope hash 2118690a621a49a3 · NOT PROVEN —  M tools/swarm_arena/swarm_view.py
$ python tools/swarm_arena/swarm_view.py --prove   → exit 2
```

The positive control is the same command after the change is committed: `unchanged
(0 dirty)` and exit 0. `scope hash` is a digest over `path object-id` pairs, so it names
committed content and cannot race a writer the way a whole-worktree content hash can —
which is what §7 step 6 needs for `scope_hash_before` / `scope_hash_after`.

**Not closed here.** B5 / build step 1 — extracting `read_scope` out of the four auditors —
is unchanged. `grep -rn "def read_scope" tools/ src/` returned nothing at audit time and now
returns only `tools/swarm_arena/swarm_view.py`. The auditors still own their extraction, and
their CLI output must stay byte-identical when it happens.
