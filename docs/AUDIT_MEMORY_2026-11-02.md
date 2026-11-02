# AUDIT — memory/store write path (2026-11-02)

READ-ONLY audit. No file under `src/CORE/` was modified. One file written: this one.

**Scope:** `src/CORE/{local_memory,direct_memory,atomic_store,recorder_guard,data_retention}.py`,
root `conftest.py`, and `tests/conftest.py`.

**Question under test:** a prior audit claimed (a) tests were writing to the production
memory store, and (b) `PamsRecorder` was an unguarded writer.

**Instrument warning first, because it changes how the zeros below should be read.**
`code_search`/`ripgrep` is non-functional in this environment (`exit 2`, `Found 0 matches`,
stderr `rg cannot open .\dist / .\ollama*.dll`). A control search for a token known to exist
also returned 0. **Every "not found" below therefore rests on `read_files`/`list_directory`,
never on a search.** Line numbers marked `~` are anchored to a read window and are
approximate within it; unmarked numbers are exact.

---

## 1. Writer inventory — every path into `memory_store.db`

| Writer | Entry point | Writes |
|---|---|---|
| `CORE.local_memory.LocalMemoryStore.record_event()` | `local_memory.py:~717` | `INSERT INTO memories(...)` + `UPDATE sessions SET event_count` — the main event tap |
| `CORE.direct_memory.DirectMemory` | `direct_memory.py:99` `DB_PATH = _get_db_path()` | own session/event ledger, same file |
| `CORE.PamsRecorder` | listed in `tests/conftest.py` `_MEMORY_DB_RESOLVERS` | recorder rows |
| `CORE.record_session` | same resolver list | session rows |
| `CORE.MemoryBus` | resolver list, global `_MEMORYBUS_DB_PATH` | queue rows |
| `CORE.data_retention` | `enforce_type_caps`, `enforce_event_ttl`, `enforce_global_quota`, `enforce_span_ttl` | **deletes**, not writes (see §5) |

Two path resolvers are duplicated deliberately rather than shared:
`local_memory._get_store_path()` (`local_memory.py:~127`) and
`direct_memory._get_db_path()` (`direct_memory.py:92`) both resolve
`AZAZAEL_MEMORY_DIR` → `~/.azazael` → `memory_store.db`. They agree today; they are two
copies of one rule, so a change to one and not the other silently splits the store. That is
a real drift surface, not a style note.

`direct_memory.py:22-29` documents that read commands never construct `DirectMemory()` because
`__init__` starts a session — so "reading the store" cannot write to it via that module.

---

## 2. Is there a guard on the WRITE path, or only at the reader?

**Both, and the write path has two independent guards. This contradicts the prior audit's
framing that guarding happened only at the reader.**

**Guard A — constructor refuses the production store under pytest** (`local_memory.py:~260-268`):

```python
if (db_path is None and os.environ.get("PYTEST_CURRENT_TEST")
        and not os.environ.get("AZAZAEL_MEMORY_DIR")):
    raise RuntimeError(
        "LocalMemoryStore() with no db_path is forbidden under pytest; "
        "pass an explicit db_path to avoid writing to the production store.")
```

The comment above it records that an earlier version of this guard fired whenever the argument
was `None`, which broke the very isolation it was written for; the current form fires only when
the resolved path would be the live default with no override. That is the correct predicate.

**Guard B — recorder guard before the INSERT** (`local_memory.py:~711-715`):

```python
try:
    from CORE.recorder_guard import allow as _guard_allow
    if not _guard_allow(event_type, severity):
        return 0
except Exception as exc:
    _note_failure("local_memory:recorder-guard", exc)
```

It runs **before** the lock and before the INSERT, so a throttled row never takes the writer
lock. It is fail-open on import failure, which is the right trade for a rate limiter and the
wrong trade for a correctness gate — and it is correctly used as the former.

`recorder_guard.py` is a per-type token bucket with three properties worth recording:

- errors/criticals bypass everything (`_exempt`, `severity in {error, critical}`);
- an unclassified event type is **still** capped by the default bucket (8 rows/s, burst 200),
  so the next runaway does not need to be named in `RATE_LIMITS` to be contained;
- a per-process session ceiling (`SESSION_MAX`, default 100 000 non-exempt rows) sits above the
  buckets, which is the only limit that still holds if an emitter invents a new event type each tick;
- suppression is counted and reported (`snapshot()`, `totals()`), and a one-line `stderr` notice is
  emitted at most once per type per minute. A guard whose drops are invisible would be
  indistinguishable from a broken emitter, and that is explicitly designed against.

**The residual gap is not the rate limiter — it is the size ceiling.** `DB_SIZE_QUOTA_MB = 500`
(`data_retention.py:99`) is only read by `check_db_size_quota`, and on the write path the store
size is used solely to **warn** (`local_memory.py:~800`, once per process via
`_size_warning_issued`). Nothing on the write path refuses a row because the file is large. Rate
and size are different failure modes: a slow emitter of 500 different types passes every bucket and
still grows the file. **Write-path enforcement tied to actual DB size does not exist.**

---

## 3. Can tests bind the production store? — the conftest analysis

**The named claim about `PamsRecorder` is already false: it is in the rebind list.**
`tests/conftest.py` `_MEMORY_DB_RESOLVERS` contains five entries, including
`("CORE.PamsRecorder", "_get_db_path", "DB_PATH")` — so the fix the prior audit called for has
already landed, and `tests/test_memory_dir_caching.py` rediscovers the set by AST and fails when a
module is missing from it. The list cannot silently rot.

Isolation is layered, and the layering is the thing to understand:

1. **Root `conftest.py`** sets `AZAZAEL_MEMORY_DIR`, `AZAZAEL_GENERATED_DIR`,
   `AZAZAEL_ENTRENCHMENT_PATH` and `AZAZAEL_NO_HEART` at **module level** — at collection, before any
   test module imports, because these modules compute their path once at import time
   (`local_memory.py:~140` `DB_PATH = _get_store_path()`). Its docstring states the reason the fix
   lives at rootdir: a conftest applies only to its own subtree, and `src/tests/` (14 modules,
   reached only by IDE discovery or a direct invocation) had no conftest at all. The measured
   consequence is recorded there — 608 `spawn_selected` rows of which **408 were unit-test fixtures**
   naming worms that do not exist.
2. **`tests/conftest.py`** additionally overrides per xdist worker
   (`PYTEST_XDIST_WORKER` → per-worker temp dir), which the root conftest does not do, and restores
   module globals after **every** test with an autouse snapshot/restore fixture.

**The hole that remains:** the snapshot/restore of derived globals lives only in
`tests/conftest.py`, so it applies to the `tests/` subtree. `src/tests/` receives the environment
redirect from root `conftest.py` but **not** the global restore. The `tests/conftest.py` block
documents the exact failure this admits (Error #196 shape): a suite that mutates
`direct_memory.DB_PATH` to a temp file and restores only the env var leaves the global pointing into
a **deleted** directory, and every later `DirectMemory()` in the process dies with
`unable to open database file` — measured 2026-09-22 as 52 failed / 3 628 passed, reproduced in 18 s
with three files run together, each passing alone. Root `conftest.py`'s own stated principle is that
the defect class is "a test directory anywhere". By that principle the restore belongs at rootdir
too, and it is not there.

Practical likelihood: low (it needs a legacy unittest-style suite in `src/tests/` that mutates
`DB_PATH`), but the failure mode is cross-file and order-dependent, which is precisely the shape
that is never seen in per-file CI.

---

## 4. Transaction and durability handling

| Mechanism | Evidence | State |
|---|---|---|
| `busy_timeout=60000` on init | `local_memory.py:~320` | **verified** |
| commit per row, rollback on `OperationalError` | `local_memory.py:~740-790` | **verified** |
| 3 attempts with 1 s/2 s backoff, then raise | `local_memory.py:~741` loop | **verified** |
| exhaustion recorded to `lock_exhaustion.jsonl` sidecar | `local_memory.py:~790` | **verified** — a record lost to lock contention is counted where a monitor can read it, not just logged |
| WAL journal mode | implied by `wal_checkpoint` being exported from `data_retention.py` (`__all__`) and by "600MB WAL DB" in the retry comment | **UNKNOWN** — the `PRAGMA journal_mode` statement itself was not read |
| `atomic_write_bytes` / `atomic_write_json` (temp + `os.replace` + `fsync`) | `atomic_store.py:44-77` | **verified, and NOT used for this store.** It covers JSON stores (morphed_registry, sweep.json, antibodies.json). SQLite supplies its own atomicity here; no claim of temp-file atomicity should be made about `memory_store.db` |
| cross-process locking helper | `atomic_store.py:105-165`, two layers: in-process `RLock` then `fcntl`/`msvcrt`, and the absence of an OS primitive is ledger-noted rather than silent | **verified** — again for file-backed stores, not the SQLite path |

One honest sampling limit: the durability conclusions above are from the `record_event` window and
`_init_db`. Other writers (`DirectMemory`, `PamsRecorder`, `MemoryBus`) were **not** read line by
line, so their transaction discipline is **UNKNOWN** — do not extend these findings to them.

---

## 5. Retention / quota — can it silently drop rows?

`data_retention.py` defines the enforcers and the caps; `recorder_guard.py`'s own docstring records
the measured origin of the whole class: `trainers_v2` emitting ~150k `episode_complete` rows in
~35 min took the store to **6.41 GB / 4 743 846 rows**, while `DB_SIZE_QUOTA_MB` merely warned and
nothing called `enforce_*`.

Verified design intent, each with evidence:

- `TYPE_CAPS` (`data_retention.py:~120-150`) keeps the newest N per high-volume type. Every cap
  carries a stated 10× margin over its actual consumer (e.g. `state_saved: 50` against a reader that
  takes `limit=5`).
- `PROTECTED_EVENTS` (`~158`) excludes `evolution_result`, `evolution_promotion` and
  `memory_distilled` from distillation and from cap trimming — selection history and already-distilled
  rows are never silently removed.
- errors are additionally spared by the quota backstop, and `ALWAYS_ALLOW` in `recorder_guard.py`
  keeps `security`, `credential`, `compliance`, `audit`, `incident`, `admission_refusal` unthrottled.

**Drops are counted where they happen at the guard, and are silent where they happen at retention.**
`recorder_guard.snapshot()`/`totals()` answer "what did you drop" per type. For the retention
enforcers I read the definitions and caps but **not** the delete implementations (the file is 1 213
lines; I read the first 200), so whether `enforce_type_caps` logs a per-type count before deleting is
**UNKNOWN**. That asymmetry is the one worth checking: a capped row that produced no `memory_distilled`
rollup first is gone without a receipt, and the module's own history shows rows were archived to
`G:/MEMORY_ARCHIVE_2026-10-31` before trimming only because someone did it by hand.

Admission refusal is the best-behaved path: `_admit_or_refuse` (`local_memory.py:~648-700`) refuses
only on an explicit `False`/`admitted=False`, admits on anything else including `None`, records a
gate that **raises** as a failure and still admits (fail-open — "admitting one row a gate would have
rejected is recoverable, a lost event is not"), and writes an `admission_refused` row for every veto.
That is the pattern the rest of the retention path should match.

---

## 6. Findings, ranked

1. **No write-path ceiling tied to DB size.** Rate limiting exists (`recorder_guard`); the 500 MB
   quota is advisory only (`local_memory.py:~800`). A many-type emitter is unbounded. *High.*
2. **Global-restore isolation is missing at rootdir.** `src/tests/` gets the env redirect but not the
   `DB_PATH` snapshot/restore, admitting the Error #196 cross-file failure class that
   `tests/conftest.py` documents at length. *Medium; low likelihood, high diagnosability cost.*
3. **Two copies of one path rule** (`local_memory._get_store_path`, `direct_memory._get_db_path`).
   Drift silently splits the store into two files. *Medium.*
4. **`PamsRecorder` claim is already resolved** — it is in `_MEMORY_DB_RESOLVERS`, and
   `tests/test_memory_dir_caching.py` fails if the list rots. The prior audit's finding is stale.
   *Closed.*
5. **Retention deletes are not demonstrably receipted** (enforcer bodies unread). *Unknown, not a
   defect claim.*

## 7. Not verified — stated so absence is not read as a pass

- `PRAGMA journal_mode` on the live store — **UNKNOWN** (WAL inferred, not read).
- Transaction/durability of `DirectMemory`, `PamsRecorder`, `MemoryBus` write paths — **UNKNOWN**.
- `data_retention.enforce_*` bodies (lines 200-1213) — **UNKNOWN**; the "silent drop" question is
  therefore open, not answered.
- `src/tests/` was not inspected; finding 2 is derived from conftest scoping rules plus the failure
  the `tests/conftest.py` docstring records, **not** from observing a `src/tests/` leak.
- Nothing was executed. No test run, no query against the live store, no size measurement was taken
  by this audit — every figure quoted is from a docstring or comment recording an earlier measurement.
- `code_search` is broken here (§ warning), so "no other writer exists" is not established; it is
  established only that the five resolvers named in `_MEMORY_DB_RESOLVERS` exist.
