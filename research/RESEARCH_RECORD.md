# Azazael Project — Comprehensive Research Record

> **Generated:** June 11, 2026
> **Sources:** 5 researcher-web agents, 3 researcher-docs agents, 2 thinker-with-files-gemini
> **Coverage:** 15 domains, 28 subjects → 67 sub-domains ([SUBDOMAINS.md](./SUBDOMAINS.md))

---

## Domain Index

| # | Domain | Subjects | Status |
|---|--------|----------|--------|
| 1 | Python 3.14t Free-Threading | Stability, C-extension compatibility, GIL-free patterns | COMPLETE |
| 2 | VLP Cryptography | Ed25519, Merkle trees, quantum-resistant sigs, replay prevention | COMPLETE |
| 3 | Agent Compliance | Z3 SMT, Casbin, wrapt, transitions state machines | COMPLETE |
| 4 | Observability | OpenTelemetry, structlog, behavioral graph anomaly detection | COMPLETE |
| 5 | Multi-Agent Governance | Consensus patterns, confidence gates, dual-ledger verification | COMPLETE |
| 6 | Docker | Python 3.14t images, container patterns, security hardening | COMPLETE |
| 7 | SQLite | WAL mode, concurrent performance, PRAGMA optimization | COMPLETE |
| 8 | Audit Trails | Certificate Transparency, append-only logs, dual-ledger validation | COMPLETE |
| 9 | Nuitka | 4.x 3.14t support, standalone packaging | COMPLETE |
| 10 | Codebuff Platform | Spawn limits, model routing, concurrency architecture | COMPLETE |
| 11 | Canonical Documents | Docs-as-code patterns, modular includes, skill sync | COMPLETE |
| 12 | ML/RL | SB3, GRPO, NSGA-II on 3.14t | COMPLETE |
| 13 | Worm Registry | AST-based discovery, caching, import time reduction | COMPLETE |
| 14 | Memory Systems | PAMS, DirectMemory, MemoryBus, LocalMemoryStore, dual-ledger correlation | COMPLETE |
| 15 | Testing | pytest 3.14t status, alternative test runners | COMPLETE |
| + | Data Validation | pydantic v2, jsonschema, AST anti-pattern scanning | COMPLETE |
| + | Hashing | hashlib, BLAKE2 vs SHA-256/512 performance | COMPLETE |

---

## 1. Python 3.14t Free-Threading

> **Informs Azazael RULEs:** 0M (concurrent inference mandate depends on free-threading safety)

**Findings:**
- Free-threading is stable and first-class in Python 3.14 (no longer experimental)
- `asyncio` optimized for multi-core in free-threading mode
- Prefer queue-based patterns over `threading.Lock` to minimize contention
- Test with `PYTHON_GIL=0` environment variable
- Subtle race conditions possible if C-extensions assume implicit GIL serialization

**C-Extension Thread Safety:**
- NumPy 2.2+ explicitly addresses free-threading — generally safe
- `wrapt`, `z3-solver`, `psutil` NOT guaranteed thread-safe — rely on internal global state
- `cryptography` natively enforces canonical checks (not a threading concern)
- `pydantic-core` — status unclear, watch for updates
- Primary risk: implicit global state in C-extensions assuming GIL serialization
- Mitigation: `Py_IsInterpreterFinalizing()`, C11 `stdatomic.h`, or Python's internal locking

**Recommendations for Azazael:**
- Audit all C-extension dependencies for thread safety before enabling free-threading in production
- Use `concurrent.futures.ThreadPoolExecutor` with queue-based patterns
- Run CI with `PYTHON_GIL=0` to catch race conditions early
- Prefer `SubprocVecEnv` for SB3 (multi-processing over threads)

---

## 2. VLP Cryptography

> **Informs Azazael RULEs:** 0T (Verifiable Truth Mandate), 0T-B (VLP Hardening — 15-layer verification stack)

**Ed25519:**
- MUST enforce canonical check ($S < L$) to prevent signature malleability
- CVE-2026-33895 pattern: inadequate bounds checking enables authentication bypass
- `cryptography` library natively enforces canonical signatures — use it, don't roll your own
- Raw private/public key format: `PrivateFormat.Raw` / `PublicFormat.Raw`

**Merkle Trees:**
- RFC 6962 (Certificate Transparency) — use SHA-256 for internal nodes
- RFC 9162 (CT v2.0) — architectural improvements, target this for new implementations
- Python libraries: `merkletools`, `pymerkle`
- O(log n) inclusion proof verification
- Consistency proofs for log integrity across checkpoints

**Quantum-Resistant Signatures:**
- FIPS 204: ML-DSA (lattice-based, formerly Dilithium) — balanced performance/size
- FIPS 205: SLH-DSA / SPHINCS+ (stateless hash-based) — larger signatures, higher security confidence
- `liboqs-python` wraps the C-based Open Quantum Safe library
- **Hybrid signatures recommended**: sign with both Ed25519 AND ML-DSA — security survives compromise of either

**Replay Attack Prevention:**
- Embed nonce + monotonic counter in each audit entry
- Timestamp ±60s validation window
- Cross-session hash chaining prevents session isolation attacks

**Recommendations for Azazael:**
- Use `cryptography` library for all Ed25519 operations (native canonical enforcement)
- Prefer BLAKE2 over SHA-256 for local performance-critical hashing
- Implement hybrid signatures (Ed25519 + ML-DSA) via `liboqs-python`
- Target RFC 9162 for Merkle tree implementation

---

## 3. Agent Compliance

> **Informs Azazael RULEs:** 0J (Pre-Action Gate), 0X (Auto-Compliance — Z3 SMT, Casbin, transitions)

**Z3 SMT Formal Verification:**
- VeriGuard pattern (arXiv:2510.05156): encode agent constraints as SMT variables
- `Solver()` class for satisfiability, `Optimize()` for maximization
- Model agent actions as symbolic variables with logic constraints
- Provides mathematical "proof of safety" that actions cannot violate invariants

**Casbin Policy Enforcement:**
- RBAC/ABAC via `.conf` model + `.csv` policy files
- `enforcer.enforce(subject, object, action)` pattern
- Custom Adapters for persistence, Role Managers for hierarchy
- Decorator-based enforcement: `@casbin_enforce(resource, action)`

**wrapt Interception:**
- `ObjectProxy` for transparent object wrapping
- `@wrapt.decorator` preserves function signatures, metadata, docstrings
- Negligible performance overhead vs `functools.wraps`
- Ideal for tool call validation middleware

**transitions State Machines:**
- `Machine` class: `states`, `transitions` with `trigger`, `source`, `dest`
- `HierarchicalMachine` for nested states
- `MachineError` raised on illegal transitions
- `before`/`after` callbacks + `conditions` (callable predicates)
- Enforce: `IDLE → GATE_ASSERT → GEMINI_SPAWN → CODE_EDIT → CODE_REVIEW → SYNC → IDLE`

**Recommendations for Azazael:**
- Implement Z3 SMT constraint encoding for PRE-ACTION GATE verification
- Deploy Casbin with RBAC policies for tool call authorization
- Wrap all code-modifying tools with `@wrapt.decorator` enforcement layer
- Model agent lifecycle as hierarchical state machine with `transitions`

---

## 4. Observability

> **Informs Azazael RULEs:** 0Q (Post-Phase Inference Check), 0Q-A (Inference Verification), 0T-A (Sentinel Self-Recording)

**OpenTelemetry:**
- `TracerProvider` with `BatchSpanProcessor` for efficient span export
- Wrap LLM invocations and tool calls in spans for full visibility
- `OTLPSpanExporter` to ship to collectors (Jaeger, Honeycomb)
- Context propagation via W3C TraceContext
- Manually create nested spans around agent "reasoning loops"

**structlog:**
- Structured logging: replace `logging` records with dictionaries
- Processor chains: `JSONRenderer`, `add_log_level`, `TimeStamper`
- Integration: `structlog.stdlib.LoggerFactory` wraps stdlib logging
- Ideal for machine-parseable compliance telemetry

**Behavioral Graph Anomaly Detection:**
- SentinelAgent (arXiv:2505.24201): directed action graphs
- Agents = nodes, tool calls = directed edges
- Detect: unauthorized cycles, forbidden edges, statistical outliers
- Catches emergent non-compliance that individual rule checks miss

**Recommendations for Azazael:**
- Instrument all agent actions with OpenTelemetry spans
- Use structlog JSONRenderer for audit trail supplement
- Implement directed action graph for behavioral anomaly detection per Rule 0Y

---

## 5. Multi-Agent Governance

> **Informs Azazael RULEs:** 0Y (Multi-Agent Governance — 2/3 consensus, dual-ledger), 0X (Auto-Compliance)

**Consensus Patterns:**
- Worker-Verifier-Judge triad: Worker executes, Verifier inspects, Judge decides
- Team-of-rivals: multiple agents critique from different perspectives (Security, Performance, Style)
- 2/3 consensus threshold for code changes

**Confidence Gates:**
- Aggregate collective confidence scores across spawned inference nodes
- Block actions below accepted threshold
- Threshold-based gating combined with consensus voting

**Dual-Ledger Validation:**
- JSONL (append-only) + SQLite (queryable index)
- Commit-then-Verify: write JSONL first, process into SQLite, then compare
- Hash-chain break = immediate tamper detection
- Certificate Transparency gossip protocol emulation with independent Merkle roots

**Recommendations for Azazael:**
- Implement Worker-Verifier-Judge pipeline for all code changes
- Set 2/3 consensus threshold per Rule 0Y
- Automate dual-ledger cross-validation (JSONL ↔ SQLite)
- Deploy confidence scoring with threshold gating

---

## 6. Docker

> **Informs Azazael RULEs:** Infrastructure layer — supports all deployment-dependent rules

**Findings:**
- Official `python:3.14-slim` images available
- Multi-stage builds: separate build-time deps from production
- `distroless` or `alpine` bases for minimal attack surface
- Free-threading available via build flags in official images
- Ensure C-extension deps support free-threaded ABI

**Recommendations for Azazael:**
- Use `python:3.14-slim` base image
- Multi-stage Dockerfile with security hardening
- Verify all binary deps have cp314t wheels before containerizing

---

## 7. SQLite Concurrency

> **Informs Azazael RULEs:** 0T (audit trail storage backbone), 0T-B (ledger storage integrity)

**WAL Mode Configuration:**
```sql
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA busy_timeout=5000;
PRAGMA wal_autocheckpoint=1000;
```

**3.14t Threading:**
- Thread-local connections required in free-threading mode
- Use `uri` mode: `file:db.sqlite?mode=memory&cache=shared`
- WAL allows multiple readers + one writer concurrently
- `synchronous=NORMAL` safe in WAL mode, higher performance than FULL

**Recommendations for Azazael:**
- Apply WAL PRAGMAs to all SQLite connections (DirectMemory, LocalMemoryStore, MemoryBus)
- Use thread-local connection pool for 3.14t
- `busy_timeout=5000` minimum for concurrent write workloads

---

## 8. Audit Trails

> **Informs Azazael RULEs:** 0T (Verifiable Truth Mandate — primary), 0T-A (Sentinel Self-Recording), 0T-B (15-layer VLP stack)

**Certificate Transparency Patterns:**
- RFC 6962: Merkle trees with SHA-256, inclusion proofs, consistency proofs
- RFC 9162 (CT v2.0): architectural improvements for new implementations
- Append-only hash-chained JSONL as primary ledger
- SQLite as queryable index for cross-validation

**Dual-Ledger Architecture:**
- Primary: append-only JSONL with per-entry SHA-256 hashes + Ed25519 signatures
- Secondary: SQLite WAL with mirrored entries + Merkle root snapshots
- Validation: periodic hash-chain recomputation from JSONL, compare against SQLite state
- Tamper detection: hash-chain break immediately signals corruption

**Recommendations for Azazael:**
- Target RFC 9162 compliance for VLP audit trails
- Implement Commit-then-Verify dual-ledger pattern
- Periodic cross-validation script comparing JSONL ↔ SQLite
- Merkle root gossip between independent ledger-keepers

---

## 9. Nuitka

> **Informs Azazael RULEs:** Infrastructure layer — supports deployment packaging for all components
> **⚠️ Error #16 context (June 2, 2026):** Nuitka 4.1.2 C backend generates code incompatible with Python 3.14t free-threading. Requires 7 C-level patches applied via `patch_nuitka_314t.py`.

**Findings:**
- Nuitka 4.1.2 provides **experimental** support for Python 3.14t — NOT production-stable out of the box
- Upstream Nuitka 4.2+ expected to include proper 3.14t support; monitor [Nuitka changelog](https://nuitka.net/changelog/Changelog.html)
- **Error #16 documented failures** (see `azazael/ERROR_LOG.md#error-16` — 7 targeted fixes applied):
  - `ob_gc_bits` direct access should use `_Py_atomic_store` for GIL-disabled builds
  - `Py_SET_REFCNT_IMMORTAL` param name bug (`op` → `object`) in GIL-disabled path
  - `_gc_runtime_state` uses `generations[3]` but GIL-disabled mode expects `young/old[2]`
  - `_Py_IMMORTAL_REFCNT` renamed to `_Py_IMMORTAL_REFCNT_LOCAL` in 3.14t
  - Missing `#include "internal/pycore_stackref.h"` for `_PyStackRef_FromPyObjectNew`
  - `HelpersAllocator.c`: ternary expression not l-value for `++` in MSVC
  - LNK2001 linker errors on Windows (unresolved external symbols for free-threaded builds)
- After patching: works for standalone `.exe` builds, but each Nuitka upgrade requires re-verification
- Python 3.13 is NOT used — all builds are on 3.14t with patches applied

**Recommendations for Azazael:**
- ALWAYS run `python azazael/docs/scripts/patch_nuitka_314t.py --apply` before any Nuitka build
- Verify patches with `patch_nuitka_314t.py --verify` before building
- Monitor Nuitka 4.2+ for native 3.14t support; remove patches when upstream fixes land
- Audit all bundled C-extensions for thread safety before packaging (Nuitka cannot make non-thread-safe C code thread-safe)
- Target `cp314t` wheels for all dependencies; avoid pre-3.14t wheels in the bundle

---

## 10. Codebuff Platform

> **Informs Azazael RULEs:** 0K (document reading order — agent startup), 0M (Concurrent Inference Mandate), 0Q (Post-Phase Inference Check), 0W (Agent Utilization — spawn all applicable agents)

**Architecture:**
- Orchestrator-Agent pattern: parent (Buffy) decomposes tasks, spawns specialized sub-agents
- Model routing: complex reasoning → DeepSeek, code generation → Claude, routine → Gemini Flash
- Async job queue dispatch (Celery/Redis-backed pattern)
- Token-bucket algorithm for API rate limit management

**Known Limitations:**
- Context drift when sub-agents lose local state during hand-offs
- Frequent Project Map serialization/deserialization trade-off
- API rate limits (TPM/RPM) are primary bottleneck
- Undocumented concurrency caps on parallel agent spawns

**Recommendations for Azazael:**
- Implement centralized `ModelRouter` evaluating (task_complexity, token_budget)
- Batch spawns for parallel research tasks
- Account for context drift in multi-phase workflows

---

## 11. Canonical Documents

> **Informs Azazael RULEs:** 0K (document reading order — canonical files must be read first), 0H (Anti-Pattern Recording Mandate)

**Docs-as-Code Patterns:**
- Markdown partials with `{% include %}` for modular includes
- Single Source of Truth (SSoT) — docs live in repo alongside code
- CI/CD triggers auto-sync to canonical site
- `markdownlint` + `vale` for documentation linting

**Modular Structure:**
- Feature folders with own `.md` files
- Central `index.md` with includes to assemble
- Prevents monolithic 100kb+ files (current SYSTEM_INSTRUCTIONS.md: 121kb)
- `sync_skills.py` automation for skill propagation

**Recommendations for Azazael:**
- Split SYSTEM_INSTRUCTIONS.md into modular includes (rules, protocols, compliance)
- Maintain SSoT in `azazael/docs/` with CI/CD sync to `.agents/skills/`
- Add markdownlint to pre-commit checks

---

## 12. ML/RL

> **Informs Azazael RULEs:** No specific rule — infrastructure/tooling domain supporting all agent optimization workflows

**Stable-Baselines3 (SB3):**
- NOT inherently thread-safe — uses `SubprocVecEnv` (multi-processing)
- PyTorch backend: share tensors via `multiprocessing.shared_memory`
- Avoid native Python threading; use vector environments

**GRPO (Group Relative Policy Optimization):**
- No Critic model required — uses group output mean as baseline
- Reduces memory usage and complexity vs PPO
- Primary reference implementation: `verl` library
- Not native to SB3 (SB3 targets classical control, GRPO targets LLM token spaces)
- Free-threading accelerates CPU rollout phase

**NSGA-II:**
- `pymoo` and `deap` libraries
- Multi-processing preferred over threading for compute-intensive genetic operators
- `Evaluator` classes with `threads` or `processes` backends
- Ensure fitness function is stateless for thread safety

**Recommendations for Azazael:**
- Use `verl` library for GRPO (not SB3)
- SB3: SubprocVecEnv for parallel environments
- NSGA-II: pymoo with multiprocessing backend
- All ML training: prefer processes over threads for safety

---

## 13. Worm Registry

> **Informs Azazael RULEs:** 0W (Agent Utilization — fast discovery enables concurrent agent spawning without cold-start penalty)

**Discovery Optimization:**
- AST-based metadata discovery: parse source files WITHOUT importing them
- Extract decorators, class names, version strings from AST
- Cache results in JSON or SQLite registry database
- Background index scan or git-hook for cache updates

**Pipeline:**
1. **Index**: Background scan creates registry cache via AST parsing
2. **Lookup**: Runtime queries registry to find plugins
3. **Lazy Load**: `importlib.import_module` only when plugin is actually invoked
4. **Extreme Performance**: PyO3 Rust bindings for directory traversal

**Recommendations for Azazael:**
- Replace `discover_worms()` runtime imports with AST-based index
- Cache registry to SQLite for persistence across sessions
- Implement lazy loading to avoid 38s cold start
- Consider git-hook for automatic registry updates on file changes

---

## 14. Memory Systems

> **Informs Azazael RULEs:** 0T (Verifiable Truth Mandate — session audit trail storage), 0T-B (dual-ledger integrity — SQLite ↔ JSONL correlation)
> **Research completed:** June 11, 2026
> **Sources:** Source code analysis (4 files), researcher-web, researcher-docs, thinker-with-files-gemini
> **Components analyzed:** PamsRecorder, DirectMemory, MemoryBus, LocalMemoryStore

---

### 14.1 Architecture Overview

Azazael has **4 memory system components** sharing a **single SQLite database** (`~/.azazael/memory_store.db`):

```
┌──────────────────────────────────────────────────────────────────┐
│                     memory_store.db (WAL mode)                    │
├────────────────┬────────────────┬────────────────┬──────────────┤
│   memories     │   sessions     │ memorybus_queue│ memories_fts │
│ (PamsRecorder, │ (DirectMemory, │  (MemoryBus)   │  (FTS5 index)│
│  DirectMemory, │ LocalMemory)   │                │              │
│  LocalMemory)  │                │                │              │
└────────────────┴────────────────┴────────────────┴──────────────┘
```

**Key insight:** All four components write to the same database but with different `session_id` formats:
- **DirectMemory**: `codebuff_20260611_143000` (timestamp-based, human-readable)
- **PamsRecorder**: `a3f8b2c1` (UUID4 first 8 chars)
- **LocalMemoryStore**: `codebuff_20260611_143000` (timestamp-based, matches DirectMemory default)
- **MemoryBus**: `e7d4a9f2` (UUID4 first 8 chars)

This **session_id mismatch** is the primary dual-ledger correlation gap — PamsRecorder and DirectMemory events cannot be trivially joined because they use different session ID formats.

---

### 14.2 PamsRecorder — Fallback Chain Analysis

**Current fallback chain (v2.0.0):**

| Layer | Target | Mechanism | Thread Safety |
|-------|--------|-----------|---------------|
| 1 | PAMS HTTP API (`:21434`) | `requests.post` with 2s timeout | Thread-safe (immutable URL + per-request connection) |
| 2 | LocalMemoryStore (SQLite) | Delegates to `store.record_event()` | ✅ Thread-safe (LocalMemoryStore uses `self._lock`) |
| 3 | JSON buffer (`pams_fallback_records.json`) | `self._lock`-protected append | ✅ Thread-safe (lock acquired before write) |

**Removed layers (F10 fix, June 7 2026):**
- ~~Layer 3: `conversations.db` direct write~~ — hardcoded path to nonexistent Python site-packages directory
- ~~Layer 4: JSON buffer without locking~~ — could corrupt data on concurrent writes

**Thread-safety assessment under 3.14t:**

| Concern | Status | Details |
|---------|--------|---------|
| Module-level `LocalMemoryStore` import (F05 fix) | ✅ SAFE | Eliminates double-checked locking + lazy import deadlock |
| `_pams_unreachable` class-level flag | ⚠️ RISK | Read outside lock at line `not type(self)._pams_unreachable`, then written inside lock. Classic TOCTOU race — two threads can both decide PAMS is reachable, both attempt HTTP call |
| `_pams_last_attempt` class-level flag | ⚠️ RISK | Same TOCTOU pattern as `_pams_unreachable`. Under 3.14t, two threads can read the same stale timestamp simultaneously |
| `_ensure_local_store()` double-check | ✅ SAFE | Correct double-checked locking with `_local_store_init_attempted` flag — the critical section (instantiation + migration) happens inside `self._lock` |
| `event_count` increment | ⚠️ RISK | `self.event_count += 1` occurs outside any lock (line after `self._lock` release in layer 3). Under 3.14t, two threads can race on this increment |
| `PamsRecorder()` singleton (no double-check) | ⚠️ RISK | `get_recorder()` creates a new `PamsRecorder()` on every call — NOT a singleton! The `_instance` class var exists but is never used. Under 3.14t, concurrent `get_recorder()` calls create multiple instances writing to the same JSON buffer |

**JSON buffer write safety:** The JSON buffer (layer 3) uses `self._lock` for append + periodic flush. This is correct for a single instance but becomes a problem with the non-singleton pattern above — multiple `PamsRecorder` instances have separate `self._lock` objects, so two instances can write to the same file simultaneously without coordination.

**Recommendations:**
- **P0**: Fix `get_recorder()` to actually return a singleton (use double-checked locking on `_instance`)
- **P1**: Protect `_pams_unreachable` / `_pams_last_attempt` reads with the class lock (or use `threading.RLock` + atomic read pattern)
- **P1**: Move `self.event_count` increment inside lock-protected sections
- **P2**: Add `_pams_unreachable` hysteresis — require N consecutive failures before marking unreachable (prevents transient network blip disabling PAMS for 60s)

---

### 14.3 DirectMemory — SQLite Schema & Signal Safety

**Schema (shared with LocalMemoryStore):**
```sql
-- memories table (shared across all components)
CREATE TABLE memories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT NOT NULL,
    source      TEXT NOT NULL,
    event_type  TEXT NOT NULL,
    data        TEXT NOT NULL DEFAULT '{}',
    severity    TEXT NOT NULL DEFAULT 'info',
    tags        TEXT NOT NULL DEFAULT '[]',
    timestamp   TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- sessions table (also shared)
CREATE TABLE sessions (
    session_id  TEXT PRIMARY KEY,
    started_at  TEXT NOT NULL,
    ended_at    TEXT,
    source      TEXT NOT NULL DEFAULT 'unknown',
    metadata    TEXT NOT NULL DEFAULT '{}',
    event_count INTEGER NOT NULL DEFAULT 0
);
```

**Key design decisions:**
- `check_same_thread=False` on all connections — each `_get_conn()` creates a fresh connection, never shares across threads
- WAL mode with `synchronous=NORMAL`, `busy_timeout=5000`, `wal_autocheckpoint=1000`
- `INSERT OR IGNORE` for session creation — atomic, no SELECT-then-INSERT race
- `"session-recording"` tag auto-appended to every event for easy filtering

**Signal handler analysis (F02 fix):**

The signal handler for SIGTERM/SIGINT/SIGBREAK does **direct DB writes without acquiring `self._lock`**. This is intentional — if the signal arrives while `self._lock` is held by a normal `record()` call, acquiring the lock would deadlock. The design is:
1. `_signal_ending` flag prevents re-entry
2. Opens a **separate connection** (not shared with normal operations)
3. Writes `ended_at` + `session_end` event directly
4. Calls `os._exit()` to terminate

**Thread-safety assessment under 3.14t:**

| Concern | Status | Details |
|---------|--------|---------|
| Signal handler DB writes | ⚠️ ACCEPTABLE RISK | Separate connection avoids lock contention. SQLite WAL serializes the write. Risk of partial write if signal arrives mid-commit is mitigated by WAL atomicity |
| `INSERT OR IGNORE` for sessions | ✅ SAFE | Atomic at SQLite level — no TOCTOU |
| `_files_changed` list access | ⚠️ RISK | Protected by `self._lock` in `file_edit()`/`file_create()`, but read without lock in `end()`. Under 3.14t, a concurrent `file_edit()` could mutate the list during `end()`'s read |
| `get_dm()` singleton | ✅ SAFE | Correct double-checked locking with `_dm_lock` |
| `atexit` handler | ⚠️ RISK | `atexit` runs during interpreter shutdown when threads may be in undefined states. The handler calls `self.end()` which acquires `self._lock` — potential deadlock if another thread holds it during shutdown |
| Class-level vars (DB_PATH) | ✅ SAFE | Set at module import time, immutable thereafter |

**Schema conflicts with LocalMemoryStore:**
Both `DirectMemory._init_db()` and `LocalMemoryStore._init_db()` execute DDL on the same `memory_store.db`. Since both use `CREATE TABLE IF NOT EXISTS` / `CREATE INDEX IF NOT EXISTS`, there is no conflict during initialization — the second call is a no-op. However:
- `DirectMemory._SCHEMA` creates only the `memories` + `sessions` tables (bare minimum)
- `LocalMemoryStore.SCHEMA_SQL` creates 8 indexes, FTS5 virtual table, and 3 triggers
- If `DirectMemory` initializes FIRST, the FTS5 index won't exist until `LocalMemoryStore` initializes
- FTS5 triggers fire on INSERT whether or not the FTS table was created by the same component

**Recommendations:**
- **P1**: Protect `_files_changed` reads in `end()` with `self._lock`
- **P1**: In `_atexit_handler`, use a separate flag instead of acquiring `self._lock` (same pattern as signal handler)
- **P2**: Ensure `LocalMemoryStore._init_db()` always runs before `DirectMemory` records events (FTS5 index must exist before INSERTs fire triggers)
- **P2**: Add a `source` column index on the sessions table (`CREATE INDEX idx_sessions_source ON sessions(source)`) — currently sessions has no indexes beyond PRIMARY KEY

---

### 14.4 MemoryBus — Persistent Queue Design

**Schema:**
```sql
CREATE TABLE memorybus_queue (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    topic       TEXT NOT NULL,
    content     TEXT NOT NULL,
    metadata    TEXT NOT NULL DEFAULT '{}',
    source      TEXT NOT NULL DEFAULT 'memorybus',
    session_id  TEXT NOT NULL,
    timestamp   TEXT NOT NULL,
    flushed     INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX idx_mbqueue_flushed ON memorybus_queue(flushed, id);
```

**Dual-queue architecture:**
1. **In-memory list** (`self._local_queue`): `List[BusMessage]`, capped at 1000 entries. Fast path for local delivery.
2. **Persistent SQLite queue** (`memorybus_queue`): Durability guarantee. Written in parallel with in-memory list.

**Publish flow (when PAMS is down):**
1. Create `BusMessage` with `message_id = len(local_queue) + 1`
2. Append to in-memory list (under `_local_queue_lock`)
3. Persist to SQLite via `_persist_to_queue()`
4. Track `message_id` in `_persisted_ids` set for later correlation

**Flush flow:**
1. Flush in-memory queue: iterate, POST to PAMS, remove successes
2. Flush persistent queue: SELECT unflushed, POST to PAMS, batch UPDATE with `flushed=1`

**Close flow:**
1. Persist any unpersisted in-memory messages to SQLite
2. Call `flush_local_queue()`
3. Clear in-memory queue
4. WAL checkpoint (TRUNCATE)

**Thread-safety assessment under 3.14t:**

| Concern | Status | Details |
|---------|--------|---------|
| `_local_queue` access | ✅ SAFE | Protected by `_local_queue_lock` |
| `_persist_to_queue()` | ⚠️ RISK | Opens a new connection per call — no lock coordination with other MemoryBus components writing to `memory_store.db`. Under 3.14t, concurrent `_persist_to_queue()` + `LocalMemoryStore.record_event()` could hit `SQLITE_BUSY` |
| `_persisted_ids` set | ⚠️ RISK | Python `set` operations are not atomic under free-threading. `self._persisted_ids.add(msg.message_id)` in `publish()` races with `msg.message_id not in self._persisted_ids` in `close()` |
| Batch UPDATE in `flush_local_queue()` | ✅ SAFE | Single UPDATE statement — atomic at SQLite level |
| `_init_persistent_queue()` | ⚠️ RISK | No lock protection — two threads calling `__init__` simultaneously could both execute `CREATE TABLE IF NOT EXISTS`. Safe in practice (DDL is atomic) but wasteful |
| `message_id` generation | ⚠️ RISK | `len(self._local_queue) + 1` is not atomic. Two threads can get the same `message_id`. Duplicate IDs cause `poll()` deduplication to drop valid messages |

**Queue durability guarantee:**
Messages are persisted to SQLite **before** being added to the in-memory queue. If the process crashes between SQLite write and in-memory append, the message survives in `memorybus_queue` (with `flushed=0`) and will be flushed on next startup. This is the correct durability ordering.

**Recommendations:**
- **P0**: Replace `len(self._local_queue) + 1` with an atomic counter (`itertools.count` or `threading.atomic` equivalent) for `message_id` generation
- **P1**: Protect `_persisted_ids` with a lock or use a thread-safe set wrapper
- **P1**: Add a WAL busy_handler or retry loop around `_persist_to_queue()` connections (currently no retry on `SQLITE_BUSY`)
- **P2**: Add a `flushed_at` timestamp column to `memorybus_queue` for flush latency monitoring
- **P2**: Add a composite index on `(session_id, flushed, id)` for per-session queue queries

---

### 14.5 LocalMemoryStore — The Backbone

**v2.0.0 feature set:**
- FTS5 full-text search with automatic trigger-based index sync
- 8 indexes (5 single-column + 3 composite) for optimized query patterns
- Database health scoring (0-100) across 6 dimensions
- Auto-vacuum and auto-backup background threads
- Query performance tracking with slow-query detection (500ms threshold)
- Instance-level performance counters (moved from class-level for 3.14t safety)
- `_QueryTimer` context manager for automatic timing

**FTS5 triggers:**
```sql
-- Auto-sync: INSERT, UPDATE, DELETE all fire FTS index updates
CREATE TRIGGER memories_ai AFTER INSERT ON memories BEGIN
    INSERT INTO memories_fts(rowid, event_type, data, tags)
    VALUES (new.id, new.event_type, new.data, new.tags);
END;
```
These triggers fire on EVERY insert to `memories` — regardless of whether the insert came from `DirectMemory`, `PamsRecorder`, or `LocalMemoryStore`. This is correct behavior: the FTS index is always current.

**Thread-safety assessment under 3.14t:**

| Concern | Status | Details |
|---------|--------|---------|
| `_QueryTimer.__exit__()` stat updates | ⚠️ RISK | Comment says "lock NOT acquired here — caller already holds it." But `query_memories()` does NOT hold `self._lock` when it calls `_QueryTimer`. Under 3.14t, two threads calling `query_memories()` simultaneously will race on `self._query_count += 1`, `self._total_query_time_ms += ...`, etc. The comment is correct for `record_event()` (which does hold the lock) but WRONG for `query_memories()` and `search_memories()` |
| `_size_warning_issued` flag | ⚠️ RISK | Read without lock in `record_event()` after the lock is released. Two threads can both pass the `if not self._size_warning_issued` check and both issue warnings |
| `_config_applied` flag | ⚠️ RISK | Read outside lock in `_apply_config()`, set to True inside the method. Two threads calling `_apply_config()` simultaneously both execute the config import |
| `get_memory_store()` singleton | ✅ SAFE | Correct double-checked locking |
| `_init_db()` | ✅ SAFE | `CREATE TABLE IF NOT EXISTS` is idempotent under `self._lock` |
| Auto-vacuum thread | ⚠️ RISK | Calls `self.vacuum()` which acquires `self._lock`. During VACUUM (which can be slow on large DBs), all `record_event()` calls block. The separate `_maintenance_lock` prevents double-start but doesn't prevent contention |
| Class-level performance counters (old) | ✅ FIXED | Moved to instance-level in v2.0.0: `self._query_count` (was `LocalMemoryStore._query_count`) |

**`_QueryTimer` race condition detail:**
```python
# In query_memories():
with self._QueryTimer(self, "query_memories"):  # <-- does NOT hold self._lock
    conn = self._get_conn()
    rows = conn.execute(sql, params).fetchall()
    conn.close()
# _QueryTimer.__exit__ fires here, writing to self._query_count WITHOUT lock
```
Under 3.14t free-threading, two threads calling `query_memories()` simultaneously will read-modify-write `self._query_count` without synchronization. Python integers are immutable, so `+=` is a read (load value) → add → write (store new object) sequence. Both threads can read the same old value, increment independently, and one increment is lost.

**Recommendations:**
- **P0**: Add `self._lock` acquisition in `query_memories()` and `search_memories()` around `_QueryTimer` usage, OR make the performance counters `threading.Lock`-protected separately
- **P1**: Protect `_size_warning_issued` with `self._lock` or use `threading.Event`
- **P1**: Schedule VACUUM during low-activity windows (or use `VACUUM INTO` to avoid blocking writes)
- **P2**: Add `idx_memories_source_timestamp` composite index for the common "recent events from source X" query pattern

---

### 14.6 Dual-Ledger Event Correlation

**Current correlation capability:**

| Ledger | Storage | Session ID Format | Correlation Keys |
|--------|---------|-------------------|-----------------|
| DirectMemory | `memory_store.db` → `memories` | `codebuff_20260611_143000` | `session_id`, `timestamp`, `event_type` |
| PamsRecorder | `memory_store.db` → `memories` (via LocalMemoryStore) | `a3f8b2c1` (UUID8) | `session_id`, `timestamp`, `event_type` |
| MemoryBus | `memory_store.db` → `memorybus_queue` | `e7d4a9f2` (UUID8) | `session_id`, `timestamp`, `topic` |
| audit_trail.py | `audit_trail.jsonl` (append-only) | Varies | `session_id`, `timestamp`, `event_type`, `hash` |

**Critical gap: Inconsistent session_id formats.** DirectMemory uses timestamp-based IDs (`codebuff_20260611_143000`) while PamsRecorder and MemoryBus use UUID8 (`a3f8b2c1`). These cannot be trivially joined. A single Codebuff session may have events scattered across all three session_id formats.

**Correlation strategy:**
1. **Timestamp-based fuzzy join**: Match events within ±5s window across ledgers. Fragile — high-frequency events can collide.
2. **Application-level correlation ID**: Add a `correlation_id` (or `parent_session_id`) field to all memory events. Pass the DirectMemory session_id as the canonical session identifier. PamsRecorder and MemoryBus store it as metadata.
3. **Cross-reference table**: Create a `session_map` table linking `(codebuff_session_id, pams_session_id, memorybus_session_id)` on session creation.

**JSONL ↔ SQLite divergence detection:**
The recommended pattern (from Domain 8 research):
1. **Commit-then-Verify**: Write JSONL entry first (append-only, hash-chained)
2. Record to SQLite (DirectMemory + LocalMemoryStore)
3. Periodically: recompute JSONL hash chain, compare against SQLite Merkle root snapshot
4. Divergence = immediate tamper flag

Currently Azazael has NO automated cross-validation between JSONL audit entries and SQLite memories. This is a gap for Rule 0T compliance.

**Recommendations:**
- **P0**: Standardize session_id format across all components to `codebuff_YYYYMMDD_HHMMSS` (or add a `parent_session_id` column)
- **P0**: Add `correlation_id` field to `memorybus_queue` for linking bus messages to sessions
- **P1**: Build automated cross-validation script: `python -m CORE.verify_dual_ledger --cross-ref`
- **P1**: Add `audit_hash` column to `memories` table storing the JSONL entry hash for each event
- **P2**: Implement periodic Merkle root comparison (JSONL root vs SQLite root) per RFC 9162

---

### 14.7 Best Practices from Industry Research

**SQLite persistent queues:**
- WAL mode is mandatory for concurrent read/write
- Single writer bottleneck — serialize writes or use queue-per-producer
- `synchronous=NORMAL` balances durability and performance in WAL mode
- Implement exponential backoff for `SQLITE_BUSY` retries
- UUIDv7 (time-sortable) recommended for event IDs over autoincrement

**Dual-ledger patterns:**
- JSONL is the "source of truth" — SQLite is rebuilt from JSONL on corruption
- Atomic dual-write: wrap both JSONL append and SQLite INSERT in a transaction
- Audit checksums: store an MD5/SHA hash of the event in SQLite that corresponds to the JSONL line offset
- Replay recovery: truncate SQLite, replay from JSONL log

**3.14t free-threading SQLite:**
- **Never share a raw `sqlite3.Connection` across threads** — even with `check_same_thread=False`
- Use `queue.Queue` for connection pooling in threaded environments
- Thread-local connections preferred: each thread opens its own connection
- Python's `sqlite3` defaults to `Multi-thread` mode (connections can be shared across threads, but individual connections shouldn't be)

**AI agent memory architecture:**
- Three-tier memory: Short-term (context window) → Medium-term (SQLite sessions) → Long-term (vector store)
- Structured state tracking: JSON snapshots of agent "beliefs" stored in SQLite
- Cross-session recall: enables agent self-correction based on past session outcomes
- LangGraph's State pattern: schema-defined object persisted across agent re-runs

---

### 14.8 Prioritized Recommendations

**P0 — Critical (fix before 3.14t production):**
- [ ] Fix `get_recorder()` singleton — currently creates new instance on every call
- [ ] Fix `message_id` generation in MemoryBus — use atomic counter, not `len(local_queue) + 1`
- [ ] Fix `_QueryTimer` race in `query_memories()` and `search_memories()` — add lock or separate performance lock
- [ ] Standardize session_id format across all 4 components
- [ ] Add `correlation_id` field to `memorybus_queue`

**P1 — High (fix before enabling free-threading CI):**
- [ ] Protect `_pams_unreachable` / `_pams_last_attempt` reads with class lock
- [ ] Protect `event_count` increment in PamsRecorder with lock
- [ ] Protect `_persisted_ids` with lock in MemoryBus
- [ ] Protect `_files_changed` read in DirectMemory.end() with lock
- [ ] Protect `_size_warning_issued` and `_config_applied` flags properly
- [ ] Add `SQLITE_BUSY` retry logic to MemoryBus `_persist_to_queue()`
- [ ] Build automated JSONL ↔ SQLite cross-validation script

**P2 — Medium (improve observability & performance):**
- [ ] Add `_pams_unreachable` hysteresis (N failures before flag set)
- [ ] Add `flushed_at` timestamp to `memorybus_queue`
- [ ] Add composite index `idx_memories_source_timestamp` on `memories(source, timestamp)`
- [ ] Add composite index `idx_mbqueue_session_flushed` on `memorybus_queue(session_id, flushed, id)`
- [ ] Add `audit_hash` column to `memories` for JSONL cross-referencing
- [ ] Schedule VACUUM during low-activity windows
- [ ] Implement periodic Merkle root comparison (JSONL ↔ SQLite)

---

## 15. Testing

> **Informs Azazael RULEs:** 0M (concurrent execution testing), 0X (compliance verification testing)

**pytest 3.14t Status:**
- Free-threading mode is experimental for pytest
- Known issues: thread-local storage races, C-extension segfaults
- Use `pytest-xdist` for managed parallelism
- Thread-safe fixtures required — avoid `unittest.mock` patching of shared global state
- Monitor pytest GitHub "free-threading" issues tracker

**Alternative Runners:**
- Python stdlib `unittest` — more predictable in threaded contexts
- Standalone test execution: `python tests/test_*.py`
- `python run_tests.py --skip-slow` for CI-friendly subset

**Recommendations for Azazael:**
- Run tests standalone (`python tests/test_file.py`) on 3.14t
- Use `pytest-xdist` with `--dist=loadfile` for parallelism
- Audit all test fixtures for thread safety
- CI: `PYTHON_GIL=0 python run_tests.py --skip-slow`

---

## Additional: Data Validation

**pydantic v2:**
- BaseModel with strict mode: `model_config = ConfigDict(strict=True)`
- `@field_validator` for field-level, `@model_validator` for cross-field
- `model_dump(mode="json")` for serializable output
- `model_json_schema()` for Draft-compliant schema generation

**jsonschema:**
- Draft 2020-12 fully supported
- Custom validators via `extend(base, {"keyword": func})`
- `format-nongpl` extra for full format checking (email, URI)

**AST Anti-Pattern Scanning:**
- `ast.parse(source)` for tree generation
- `ast.NodeVisitor` subclass with `visit_Call`, `visit_Name` methods
- Detect: `eval()`, `exec()`, `os.system()`, hardcoded paths, Unicode in code

---

## Additional: Hashing

**hashlib:**
- SHA-256/512: standard, NIST-approved
- BLAKE2: superior performance and security. Use `blake2b` for 64-bit, `blake2s` for 32-bit
- All utilize optimized C extensions
- For extreme performance, BLAKE2 is the recommended default

---

## Implementation TODOs

### P0 — Critical (blocking 3.14t production readiness)
- [ ] Fix `get_recorder()` singleton in PamsRecorder — creates new instance on every call (Domain 14.2)
- [ ] Fix `message_id` atomicity in MemoryBus — use atomic counter, not `len(local_queue) + 1` (Domain 14.4)
- [ ] Fix `_QueryTimer` race in `query_memories()` / `search_memories()` — add lock around stat updates (Domain 14.5)
- [ ] Standardize `session_id` format across all 4 memory components to `codebuff_YYYYMMDD_HHMMSS` (Domain 14.6)
- [ ] Add `correlation_id` field to `memorybus_queue` for dual-ledger linking (Domain 14.6)

### P1 — High (fix before enabling free-threading CI)
- [ ] Protect `_pams_unreachable` / `_pams_last_attempt` reads with class lock in PamsRecorder (Domain 14.2)
- [ ] Protect `event_count` increment in PamsRecorder with lock (Domain 14.2)
- [ ] Protect `_persisted_ids` with lock in MemoryBus (Domain 14.4)
- [ ] Protect `_files_changed` read in DirectMemory.end() with lock (Domain 14.3)
- [ ] Protect `_size_warning_issued` and `_config_applied` flags properly in LocalMemoryStore (Domain 14.5)
- [ ] Add `SQLITE_BUSY` retry logic to MemoryBus `_persist_to_queue()` (Domain 14.4)
- [ ] Build automated JSONL ↔ SQLite cross-validation script: `python -m CORE.verify_dual_ledger --cross-ref` (Domain 14.6)
- [ ] Audit all C-extension dependencies for 3.14t thread safety (Domain 1)
- [ ] Implement hybrid Ed25519 + ML-DSA signatures via `liboqs-python` (Domain 2)
- [ ] Deploy Casbin RBAC policies for tool call authorization (Domain 3)
- [ ] Wrap code-modifying tools with `@wrapt.decorator` enforcement layer (Domain 3)
- [ ] Model agent lifecycle as `transitions` HierarchicalMachine (Domain 3)
- [ ] Encode PRE-ACTION GATE constraints as Z3 SMT variables (Domain 3)
- [ ] Instrument all agent actions with OpenTelemetry spans (Domain 4)
- [ ] Implement directed action graph for behavioral anomaly detection (Domain 4)
- [ ] Deploy Worker-Verifier-Judge pipeline with 2/3 consensus (Domain 5)
- [ ] Automate dual-ledger cross-validation (JSONL ↔ SQLite) — see Domain 14.6 (Domain 5, 8)

### P2 — Medium (improve performance, observability, and developer experience)
- [ ] Add `_pams_unreachable` hysteresis — N consecutive failures before flag set (Domain 14.2)
- [ ] Add `flushed_at` timestamp to `memorybus_queue` for flush latency monitoring (Domain 14.4)
- [ ] Add composite index `idx_memories_source_timestamp` on `memories(source, timestamp)` (Domain 14.5)
- [ ] Add composite index `idx_mbqueue_session_flushed` on `memorybus_queue(session_id, flushed, id)` (Domain 14.4)
- [ ] Add `audit_hash` column to `memories` for JSONL cross-referencing (Domain 14.6)
- [ ] Schedule VACUUM during low-activity windows (Domain 14.5)
- [ ] Implement periodic Merkle root comparison (JSONL ↔ SQLite) per RFC 9162 (Domain 14.6)
- [ ] Build AST-based Worm Registry cache to eliminate 38s cold start (Domain 13)
- [ ] Split SYSTEM_INSTRUCTIONS.md into modular markdown includes (Domain 11)
- [ ] Lock Python 3.14t multi-stage Dockerfile (Domain 6)
- [ ] Configure pytest with `pytest-xdist` and audit shared-state fixtures (Domain 15)
- [ ] Implement GRPO via `verl` library for RL training (Domain 12)
- [x] Research ALL 15 domains — complete (see Domain Index above)

---

## Libraries to Integrate

| Priority | Library | Purpose |
|----------|---------|---------|
| **Critical** | `cryptography` | Ed25519 canonical enforcement, hybrid signatures |
| **Critical** | `casbin` | RBAC/ABAC policy engine for tool calls |
| **Critical** | `wrapt` | Zero-overhead decorator interception |
| **Critical** | `pydantic` (v2) | Strict data validation, schema generation |
| **High** | `structlog` | Structured JSON logging for compliance telemetry |
| **High** | `opentelemetry-sdk` | Distributed tracing of all agent actions |
| **High** | `transitions` | Hierarchical state machine enforcement |
| **High** | `z3-solver` | SMT formal verification of agent constraints |
| **Medium** | `liboqs-python` | Post-quantum hybrid signatures |
| **Medium** | `merkletools` / `pymerkle` | RFC 6962/9162 Merkle tree audit trails |
| **Medium** | `verl` | GRPO reinforcement learning |
| **Medium** | `pymoo` / `deap` | NSGA-II multi-objective optimization |
| **Low** | `markdownlint` | Documentation linting in CI |
| **Low** | `pytest-xdist` | Parallel test execution |

---

*End of Research Record — June 11, 2026*
*15/15 domains complete. All research subjects covered.*
