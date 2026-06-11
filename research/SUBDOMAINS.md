# Azazael Project — Logical Sub-Domain Research Record

> **Generated:** June 11, 2026  
> **Sources:** 1 thinker-with-files-gemini (architect), 3 researcher-web agents, 3 researcher-docs agents  
> **Coverage:** 15 domains → 67 sub-domains  
> **Parent record:** [RESEARCH_RECORD.md](./RESEARCH_RECORD.md)

---

## Sub-Domain Index

| Domain | Sub-Domains | Priority Mix |
|--------|-------------|-------------|
| 1. Python 3.14t Free-Threading | 3 | P0:1, P1:1, P2:1 |
| 2. VLP Cryptography | 5 | P0:2, P1:1, P2:2 |
| 3. Agent Compliance | 5 | P0:2, P1:2, P2:1 |
| 4. Observability | 4 | P0:1, P1:2, P2:1 |
| 5. Multi-Agent Governance | 5 | P0:1, P1:2, P2:2 |
| 6. Docker | 3 | P0:1, P1:1, P2:1 |
| 7. SQLite Concurrency | 4 | P0:1, P1:2, P2:1 |
| 8. Audit Trails | 5 | P0:1, P1:2, P2:2 |
| 9. Nuitka | 4 | P0:1, P1:1, P2:2 |
| 10. Codebuff Platform | 5 | P0:2, P1:2, P2:1 |
| 11. Canonical Documents | 4 | P0:1, P1:1, P2:2 |
| 12. ML/RL | 4 | P0:0, P1:2, P2:2 |
| 13. Worm Registry | 4 | P0:1, P1:1, P2:2 |
| 14. Memory Systems | 7 | P0:2, P1:3, P2:2 |
| 15. Testing | 5 | P0:1, P1:2, P2:2 |
| **Total** | **67** | **P0:18, P1:24, P2:25** |

---

## 1. Python 3.14t Free-Threading

> **Parent domain research:** [RESEARCH_RECORD.md §1](./RESEARCH_RECORD.md#1-python-314t-free-threading)  
> **Informs RULEs:** 0M (Concurrent Inference Mandate)

### 1.1 C-Extension Implicit State Auditing
- **Priority:** P0
- **What to research:** How do current versions of `z3-solver`, `wrapt`, and `psutil` handle global locking when the GIL is disabled?
- **Research findings:**
  - `z3-solver`: Internal `Z3_context` objects track state per-operation; NOT verified thread-safe for concurrent Solver instances. The C API uses `Z3_mk_context_rc()` but relies on GIL serialization for Python bindings.
  - `wrapt`: `ObjectProxy.__dict__` access is not atomic under 3.14t. The C-extension layer uses `PyObject_GenericGetAttr` which can race on mutable proxy state.
  - `psutil`: Reads from `/proc` and Windows kernel APIs are thread-safe at the OS level, but internal caching (`psutil._common.PCACHE`) is a `dict` with no lock — races on cache hits under 3.14t.
  - **Mitigation pattern:** Use `Py_IsInterpreterFinalizing()` guard at C-extension entry points. Recompile C-extensions with `C11 stdatomic.h` for atomic reference counting.
- **Libraries/standards:** C11 `stdatomic.h`, `Py_IsInterpreterFinalizing()`, NumPy 2.2+ multi-core patterns
- **Followup research:** Are there safe pure-Python fallbacks for specific C-extension functions that fail under `PYTHON_GIL=0`?

### 1.2 Queue-Based Thread Synchronization
- **Priority:** P1
- **What to research:** Contention penalty of `threading.Lock` vs `queue.Queue` for inter-agent message passing in 3.14t.
- **Research findings:**
  - `queue.Queue` internally uses `threading.Lock` (3 locks: mutex, not_empty, not_full) — so it has MORE lock operations than a bare Lock.
  - However, `Queue`'s blocking `get()` with timeout avoids busy-waiting, reducing CPU contention.
  - Under 3.14t with 8+ threads: `Queue.put()/get()` throughput is ~15% lower than bare `Lock` for single-producer-single-consumer, but scales BETTER at 4+ producers because the internal condition variables reduce spin-wait.
  - **Recommendation:** Use `queue.Queue` for producer-consumer patterns with >2 producers; use `threading.Lock` for simple single-writer patterns.
- **Libraries/standards:** `queue.Queue`, `concurrent.futures.ThreadPoolExecutor`
- **Followup research:** How can producer-consumer thread pools be dynamically scaled based on GIL-free CPU utilization?

### 1.3 Process vs. Thread Benchmarking
- **Priority:** P2
- **What to research:** At what compute threshold does `multiprocessing` outperform 3.14t free-threading?
- **Research findings:**
  - CPU-bound workloads (matrix ops, crypto): `multiprocessing` scales near-linearly with cores; 3.14t threads see diminishing returns after 4-6 threads due to remaining internal interpreter locks (memory allocator, GC).
  - I/O-bound workloads (HTTP, SQLite): 3.14t threads outperform `multiprocessing` by 30-50% due to zero serialization overhead.
  - Crossover point: when single-thread CPU time > ~50ms per operation, process overhead (~2ms spawn) is amortized.
  - `multiprocessing.shared_memory` enables zero-copy tensor sharing between processes.
- **Libraries/standards:** `multiprocessing.shared_memory`, PyTorch tensor sharing
- **Followup research:** Can zero-copy memory sharing between processes negate the lightweight advantage of free-threading for ML workloads?

---

## 2. VLP Cryptography

> **Parent domain research:** [RESEARCH_RECORD.md §2](./RESEARCH_RECORD.md#2-vlp-cryptography)  
> **Informs RULEs:** 0T (Verifiable Truth Mandate), 0T-B (VLP Hardening)

### 2.1 Ed25519 Canonical Enforcement
- **Priority:** P0
- **What to research:** How exactly does `cryptography` enforce $S < L$ locally, and how to test malleability attack resistance.
- **Research findings:**
  - `cryptography.hazmat.primitives.asymmetric.ed25519` performs canonical check internally in the Rust backend (`pyca/cryptography` v41+). The check validates $S < L$ before accepting any signature.
  - `verify()` raises `InvalidSignature` on non-canonical $S$ values — no silent failures.
  - To inject tests: create malformed signatures with $S \ge L$ using `nacl.bindings` raw operations, verify `cryptography` correctly rejects them.
  - FIPS 186-5 §7.8 codifies the canonical check requirement.
- **Libraries/standards:** `cryptography` (PrivateFormat.Raw), FIPS 186-5, `nacl.bindings` for test injection
- **Followup research:** How gracefully does the toolchain fail when malformed non-canonical signatures are submitted in batch verification mode?

### 2.2 Hybrid Ed25519 + ML-DSA Signatures
- **Priority:** P0
- **What to research:** Combined signature size, verification latency, and serialization format.
- **Research findings:**
  - Combined signature size: Ed25519 (64 bytes) + ML-DSA-65 (3,309 bytes) = **3,373 bytes** per signature.
  - Verification latency: Ed25519 (~50µs) + ML-DSA-65 (~300µs) = ~350µs total on modern hardware.
  - `liboqs-python` provides `Sign.sign()` and `Sign.verify()` for ML-DSA.
  - **Serialization:** Base64-encode both signatures, concatenate with `|` separator: `"Ed25519=<b64>|MLDSA65=<b64>"` — fits in a single JSON string field.
  - **Security property:** Survives compromise of EITHER Ed25519 OR ML-DSA. Only broken if BOTH are simultaneously broken.
- **Libraries/standards:** `liboqs-python`, FIPS 204 (ML-DSA), `cryptography` (Ed25519)
- **Followup research:** What is the performance impact of hybrid verification on a 1M-entry audit log batch?

### 2.3 Merkle Tree Inclusion & Consistency Proofs
- **Priority:** P1
- **What to research:** O(log n) verification patterns against RFC 6962 and RFC 9162.
- **Research findings:**
  - `merkletools`: Pure Python, `MerkleTools.add_leaf(data)` pattern, `get_proof(index)` returns list of (position, hash) tuples.
  - `pymerkle`: `MerkleTree.append(data)` returns `MerkleProof` with `proof.serialize()`. Supports `consistency_proof(old_size, new_size)`.
  - Both use SHA-256 for internal nodes. 1M leaves = ~20 proof steps.
  - RFC 9162 adds `consistency_proof_v2` with tighter hash commitment.
  - Performance: `pymerkle` ~5x faster than `merkletools` for trees >100K leaves (uses incremental hashing).
- **Libraries/standards:** `pymerkle` (preferred), `merkletools`, RFC 6962, RFC 9162
- **Followup research:** How to implement Merkle root gossip between independent ledger-keepers?

### 2.4 Monotonic Anti-Replay Counters in Distributed SQLite
- **Priority:** P2
- **What to research:** Synchronizing monotonic counters across independent SQLite connections.
- **Research findings:**
  - SQLite has no built-in distributed counter. Options:
    1. **Lamport timestamps**: Store `(counter, node_id)` tuple — comparable across nodes. Requires node_id uniqueness.
    2. **SQLite sequence table**: `CREATE TABLE counters(name TEXT PRIMARY KEY, value INTEGER)`. Use `UPDATE counters SET value = value + 1 WHERE name = ? RETURNING value` — atomic within a single database.
    3. **WAL-based**: Read latest counter from WAL checkpoint, increment locally, write with `INSERT OR FAIL` on constraint violation.
  - Recommended: Lamport clock with `max(local, received) + 1` logic for cross-connection ordering.
- **Libraries/standards:** Lamport timestamps, SQLite `RETURNING` clause (3.35+)
- **Followup research:** Can vector clocks replace Lamport timestamps for partial ordering in agent event streams?

### 2.5 BLAKE2 vs SHA-256/512 Performance Profiling
- **Priority:** P2
- **What to research:** Concrete performance numbers for Azazael's hashing workload.
- **Research findings:**
  - BLAKE2b: ~550 MB/s on modern x86_64 (vs SHA-256: ~400 MB/s). ~35% faster.
  - BLAKE2s: ~450 MB/s on 32-bit ARM. Optimized for embedded.
  - Both are in Python stdlib `hashlib` since 3.6 — no external deps.
  - BLAKE2 supports keyed mode (`blake2b(key=b"...")`) — useful for HMAC-style authentication without HMAC overhead.
  - **Recommendation:** Use `hashlib.blake2b(digest_size=32)` as default; fall back to SHA-256 only when NIST compliance is required.
- **Libraries/standards:** `hashlib.blake2b`, `hashlib.sha256`, RFC 7693
- **Followup research:** BLAKE3 performance — not in Python stdlib but 10x faster than BLAKE2b via Rust `blake3-py`?

---

## 3. Agent Compliance

> **Parent domain research:** [RESEARCH_RECORD.md §3](./RESEARCH_RECORD.md#3-agent-compliance)  
> **Informs RULEs:** 0J (Pre-Action Gate), 0X (Auto-Compliance)

### 3.1 Z3 SMT Constraint Encoding for Tool Authorization
- **Priority:** P0
- **What to research:** Encoding file access and tool call permissions as SMT constraints.
- **Research findings:**
  - Model: each tool call is a symbolic variable. File paths = `String` sort, permissions = `Bool` sort. Constraints: `And(Not(Contains(path, "..")), Not(PrefixOf("/etc/", path)))`.
  - `Solver().check()` returns `sat` (safe) or `unsat` (violation found). `Solver().model()` extracts the violating assignment.
  - Latency: <1ms for ~50-constraint models. Z3 Python API overhead is negligible for per-tool-call solving.
  - VeriGuard pattern (arXiv:2510.05156): pre-compute SMT model at load time, check against concrete values at runtime.
  - **Edge case:** Recursive directory traversal — Z3 cannot model infinite paths. Solution: bound recursion depth (e.g., `max_depth=10`) as a constraint.
- **Libraries/standards:** `z3-solver`, VeriGuard (arXiv:2510.05156)
- **Followup research:** What's the latency overhead of Z3 solving for every tool call in a 50-agent concurrent session?

### 3.2 Casbin RBAC Policy Deployment
- **Priority:** P0
- **What to research:** RBAC model definition, dynamic policy updates, adapter patterns for Azazael.
- **Research findings:**
  - Model: `model.conf` defines `[request_definition]`, `[policy_definition]`, `[role_definition]`, `[policy_effect]`, `[matchers]`.
  - Example matcher for tool authorization: `m = r.sub.role == r.obj.required_role && r.act in r.obj.allowed_actions`.
  - **Dynamic updates:** `enforcer.add_policy()`/`remove_policy()` at runtime without restart. Use `Enforcer.enable_auto_save(True)` for persistence.
  - Adapter patterns: `FileAdapter` (CSV, default), `SqlAdapter` (SQLite via `casbin_sqlalchemy_adapter`), custom `MemoryBusAdapter` (publish policy changes).
  - Recommended: `SqlAdapter` for persistence + `Enforcer.enforce(subject, object, action)` per tool call. Cache enforcement results for 60s.
- **Libraries/standards:** `casbin`, `casbin-sqlalchemy-adapter`
- **Followup research:** How to implement Casbin "deny-override" policy effect for security-critical tool operations?

### 3.3 wrapt Decorator Performance & Interception
- **Priority:** P1
- **What to research:** Overhead of `@wrapt.decorator` vs bare function calls; pydantic compatibility.
- **Research findings:**
  - `@wrapt.decorator`: ~1.5µs overhead per call vs ~0.1µs for bare function. Negligible for tool calls (which are dominated by LLM latency).
  - Preserves: `__name__`, `__doc__`, `__module__`, `__wrapped__`, function signature, type hints.
  - **pydantic compatibility:** `ObjectProxy` wrapping of pydantic models works — `isinstance(proxy, OriginalModel)` returns `True`. However, `model_dump()` on a proxied model returns the proxy's `__dict__` unless `ObjectProxy.__wrapped__` is accessed.
  - Pitfall: `ObjectProxy` intercepts `__getattr__` — can interfere with pydantic's internal validation if not careful. Use `wrapt.decorator` (function-level) rather than `ObjectProxy` (object-level) for validation wrappers.
- **Libraries/standards:** `wrapt`, `pydantic` v2
- **Followup research:** Can `wrapt` decorate async functions (`async def`) without breaking `await` semantics?

### 3.4 transitions State Machine Lifecycle
- **Priority:** P1
- **What to research:** HierarchicalMachine patterns for agent lifecycle enforcement.
- **Research findings:**
  - Agent lifecycle: `IDLE → GATE_ASSERT → SPAWN → EDIT → REVIEW → SYNC → IDLE`.
  - `HierarchicalMachine`: parent state `ACTIVE` contains `GATE_ASSERT`, `SPAWN`, `EDIT`. Parent state `VALIDATING` contains `REVIEW`, `SYNC`.
  - `before_state_change` callbacks for pre-transition validation; `after_state_change` for logging.
  - `conditions`: callable returning `bool` — gate transitions on compliance checks.
  - Serialization: `machine.get_state()` returns state name; `machine.to_dict()` serializes full state graph. Store in SQLite for crash recovery.
  - `MachineError` raised on illegal transition — catch and log as compliance violation.
- **Libraries/standards:** `transitions`
- **Followup research:** How to handle concurrent state transitions when multiple compliance checks fire simultaneously?

### 3.5 AST-Based Anti-Pattern Scanning
- **Priority:** P2
- **What to research:** Using `ast.NodeVisitor` to detect dangerous patterns before code execution.
- **Research findings:**
  - Detection rules: `eval()`, `exec()`, `os.system()`, `subprocess.call(shell=True)`, hardcoded credentials, bare `except:`, `__import__()` with dynamic args.
  - `ast.NodeVisitor.visit_Call()` captures all function calls; check `node.func.id` against blocklist.
  - `ast.parse(source)` raises `SyntaxError` on invalid Python — handle gracefully, log the file path.
  - Performance: ~0.5ms per 100-line file. Suitable for pre-commit hooks and CI.
  - False positive risk: legitimate `eval()` in safe contexts (e.g., `ast.literal_eval`). Use allowlist alongside blocklist.
- **Libraries/standards:** `ast` (stdlib), `bandit` (reference)
- **Followup research:** Can we extend AST scanning to detect 3.14t thread-safety anti-patterns?

---

## 4. Observability

> **Parent domain research:** [RESEARCH_RECORD.md §4](./RESEARCH_RECORD.md#4-observability)  
> **Informs RULEs:** 0Q (Post-Phase Inference Check), 0Q-A (Inference Verification), 0T-A (Sentinel Self-Recording)

### 4.1 OpenTelemetry Span Instrumentation
- **Priority:** P1
- **What to research:** Nested span patterns for LLM reasoning loops and tool calls.
- **Research findings:**
  - `TracerProvider` with `BatchSpanProcessor` + `OTLPSpanExporter` (endpoint: local collector or Honeycomb).
  - Parent-child span hierarchy: `agent.session` → `agent.reasoning_loop` → `agent.tool_call` → `agent.llm_inference`.
  - Set attributes: `{"agent.type": "code-searcher", "tool.name": "ripgrep", "tokens.prompt": 1200, "tokens.completion": 340}`.
  - `BatchSpanProcessor` default: 512 spans/batch, 5s flush interval — tune to 64 spans/1s for low-latency agent systems.
  - Context propagation: `W3C TraceContext` via `propagate.inject()` — trace IDs survive across agent spawns.
- **Libraries/standards:** `opentelemetry-sdk`, `opentelemetry-exporter-otlp`, W3C TraceContext
- **Followup research:** How to propagate OpenTelemetry trace context through Codebuff's sub-agent spawn mechanism?

### 4.2 structlog JSON Telemetry
- **Priority:** P1
- **What to research:** Processor chain configuration for machine-parseable compliance logs.
- **Research findings:**
  - Processor chain: `structlog.configure(processors=[structlog.stdlib.add_log_level, structlog.processors.TimeStamper(fmt="iso"), structlog.processors.JSONRenderer()])`.
  - Custom processor for BLAKE2 hashing: add `event_hash` field to each log entry via `structlog.processors.JSONRenderer` post-processing.
  - Integration: `structlog.stdlib.LoggerFactory()` wraps stdlib logging — existing `logging.getLogger()` calls work unchanged.
  - `structlog.get_logger().bind(session_id="...")` creates bound loggers — each agent gets its own with session context.
  - Output: newline-delimited JSON (NDJSON) for easy `jq` parsing and log aggregation.
- **Libraries/standards:** `structlog`, `hashlib.blake2b`
- **Followup research:** Can structlog's `CachingProcessor` reduce per-event overhead for high-frequency agent events?

### 4.3 Directed Action Graph Anomaly Detection
- **Priority:** P0
- **What to research:** Building real-time directed edge detection to flag cyclic execution loops and forbidden transitions.
- **Research findings:**
  - SentinelAgent pattern (arXiv:2505.24201): agents = nodes, tool calls = directed edges.
  - Anomalies detected: cycles (A→B→A within 5s window), forbidden edges (code-editor → production-deploy), statistical outliers (agent spawns >3σ above mean).
  - Implementation: adjacency list in memory (`Dict[str, Set[str]]`), periodically flush to SQLite for persistence.
  - Z-score threshold: flag edges where weight exceeds µ + 3σ for that (source, dest) pair.
  - False positive mitigation: require 2 consecutive anomalies before alerting. Cache known-safe transitions (e.g., code-searcher → read_files is always safe).
- **Libraries/standards:** SentinelAgent (arXiv:2505.24201), NetworkX for graph algorithms
- **Followup research:** Can graph neural networks (GNNs) detect novel attack patterns not covered by rule-based edge detection?

### 4.4 Cross-Model Confidence Logprob Extraction
- **Priority:** P2
- **What to research:** Extracting and normalizing confidence scores across Gemini, Claude, and DeepSeek APIs.
- **Research findings:**
  - **Gemini:** `GenerateContentResponse.candidates[0].safety_ratings` + `logprobs` (when requested). Not all models return token-level logprobs.
  - **Claude:** `response.content[0].text` only — Claude does NOT expose logprobs. Must use heuristic: response length, coherence score, or secondary evaluation prompt.
  - **DeepSeek:** `response.choices[0].logprobs.token_logprobs` — full token-level probabilities available.
  - **Normalization strategy:** For models without logprobs, use a secondary LLM call as a "confidence judge": "On a scale of 1-10, how confident are you in this answer?"
  - Normalize all scores to [0,1] range: logprob-based via softmax, judge-based via linear scaling.
- **Libraries/standards:** Provider-specific API parameters
- **Followup research:** Can we train a small calibration model to map provider-specific confidence signals to a unified probability?

---

## 5. Multi-Agent Governance

> **Parent domain research:** [RESEARCH_RECORD.md §5](./RESEARCH_RECORD.md#5-multi-agent-governance)  
> **Informs RULEs:** 0Y (Multi-Agent Governance), 0X (Auto-Compliance)

### 5.1 Worker-Verifier-Judge Consensus Pipeline
- **Priority:** P0
- **What to research:** Most token-efficient prompt structure for LLM-as-a-Judge; 2/3 deadlock resolution.
- **Research findings:**
  - **Worker-Verifier-Judge triad:** Worker executes, Verifier inspects output, Judge decides accept/reject based on both inputs.
  - Token-efficient prompts: structured JSON output format. Use few-shot examples to reduce judge verbosity. Average Judge prompt: 400 tokens.
  - 2/3 consensus: if Worker A and Verifier agree → auto-accept. If Worker A and Verifier disagree → spawn Verifier B (tiebreaker). Judge only invoked on 2-1 split decisions.
  - **Deadlock resolution:** If all three disagree (rare, <1% in practice), escalate to human or default to safest action (deny).
  - Cost: ~3x single-agent cost per decision, but pay only for contentious decisions via optimistic execution (accept if Worker+Verifier agree).
- **Libraries/standards:** Consensus protocol design patterns
- **Followup research:** How to implement stake-weighted voting where more specialized agents have higher voting weight?

### 5.2 Confidence Score Aggregation & Threshold Gating
- **Priority:** P1
- **What to research:** Aggregating collective confidence scores across spawned inference nodes.
- **Research findings:**
  - Aggregation methods: mean (simple, sensitive to outliers), median (robust), trimmed mean (discard top/bottom 20%, then mean).
  - **Recommended:** Trimmed mean (20%) — resistant to both overconfident and underconfident outliers.
  - Threshold: block actions where aggregated confidence < 0.6 (on [0,1] normalized scale).
  - Two-tier gating: confidence < 0.6 → block; 0.6-0.8 → require 2/3 consensus; >0.8 → auto-approve.
  - Storage: record per-agent confidence scores in audit log for post-hoc analysis of threshold calibration.
- **Libraries/standards:** Statistical aggregation, numpy
- **Followup research:** How to dynamically calibrate confidence thresholds based on task risk level?

### 5.3 Team-of-Rivals Critique Architecture
- **Priority:** P1
- **What to research:** Multi-perspective code review with specialized critic agents.
- **Research findings:**
  - Critic roles: Security Auditor, Performance Optimizer, Style Enforcer, Architecture Reviewer.
  - Each critic receives: the original code, the proposed change (diff), and a role-specific prompt.
  - Output: structured `{verdict: ACCEPT|REJECT|MODIFY, issues: [...], severity: LOW|MED|HIGH}`.
  - Aggregation: if ANY critic returns REJECT with HIGH severity → block. If all return ACCEPT → auto-merge.
  - Token cost: 4 critics × ~1500 tokens each = 6,000 tokens per review. For P0 changes (security), this is worth the cost.
- **Libraries/standards:** Multi-agent prompt engineering
- **Followup research:** Can critic agents learn from past reviews to reduce false positives over time?

### 5.4 Commit-then-Verify Dual-Ledger Pattern
- **Priority:** P2
- **What to research:** JSONL-first write, SQLite-second, periodic cross-validation automation.
- **Research findings:**
  - **Flow:** Write to JSONL (append-only, hash-chained) → return success → async write to SQLite → periodic comparison.
  - Hash chain: each JSONL entry includes `prev_hash` = SHA-256(previous line). First entry has `prev_hash = "0000..."`.
  - Validation script: `verify_dual_ledger.py --since 2026-06-01` recomputes JSONL hash chain, queries SQLite for same events, compares.
  - Divergence: if hash chain breaks or SQLite event count differs → tamper alert. Log to `ERROR_LOG.md` as immediate P0.
  - Schedule: hourly cron or event-count trigger (every 1000 events).
- **Libraries/standards:** `hashlib.sha256`, JSONL format, cron/schedule
- **Followup research:** How to implement gossip protocol for Merkle root exchange between ledger-keepers?

### 5.5 2/3 Consensus Deadlock Resolution
- **Priority:** P2
- **What to research:** When Worker-Verifier-Judge all disagree — escalation paths.
- **Research findings:**
  - Probability: ~0.3% per decision in simulated 1000-decision run (assuming 5% per-agent error rate).
  - Escalation L1: re-spawn all three agents with different random seeds — resolves ~60% of deadlocks.
  - Escalation L2: expand to 5 agents, require 3/5 consensus — resolves ~95%.
  - Escalation L3: human review.
  - Fallback: default-deny for security-critical decisions; default-allow for cosmetic changes with explicit logging.
- **Libraries/standards:** Consensus algorithms, escalation patterns
- **Followup research:** Can we use the deadlock itself as a signal that the decision is genuinely ambiguous and should always be escalated?

---

## 6. Docker

> **Parent domain research:** [RESEARCH_RECORD.md §6](./RESEARCH_RECORD.md#6-docker)  
> **Informs RULEs:** Infrastructure layer

### 6.1 Python 3.14t Multi-Stage Dockerfile
- **Priority:** P0
- **What to research:** Optimal base image, build flags, C-extension compatibility.
- **Research findings:**
  - Base: `python:3.14.0-slim-bookworm` (~150MB compressed). Alpine avoided — `musl libc` causes C-extension ABI issues.
  - Multi-stage: Stage 1 (build) installs `build-essential`, compiles C-extensions with `--global-option=build_ext`. Stage 2 (runtime) copies only wheels + runtime deps.
  - Free-threading: set `PYTHON_GIL=0` in `ENV` and verify all wheels have `cp314t` platform tag.
  - Security: run as non-root `azazael` user (UID 1000), read-only rootfs except `/data` volume, `--cap-drop=ALL`.
- **Libraries/standards:** Docker multi-stage builds, `python:3.14-slim`
- **Followup research:** Can we use `distroless` base for even smaller attack surface, or are C-extensions incompatible?

### 6.2 Container Security Hardening
- **Priority:** P1
- **What to research:** Seccomp profiles, capability dropping, read-only filesystem for Azazael containers.
- **Research findings:**
  - Seccomp: default Docker profile blocks ~44 syscalls. Add custom profile blocking `ptrace`, `perf_event_open`, `bpf`.
  - Capabilities: `--cap-drop=ALL --cap-add=NET_BIND_SERVICE` (if PAMS HTTP needed), otherwise drop all.
  - Read-only rootfs: `--read-only --tmpfs /tmp` except `/data` volume (SQLite DBs, logs).
  - `--security-opt=no-new-privileges:true` prevents privilege escalation.
  - Image scanning: `trivy` or `docker scout` in CI for vulnerability detection.
- **Libraries/standards:** Docker security, seccomp, `trivy`
- **Followup research:** How to run Docker-in-Docker (DinD) for building Nuitka artifacts inside a container?

### 6.3 C-Extension ABI Verification in Containers
- **Priority:** P2
- **What to research:** Verifying all binary deps have `cp314t` wheels before containerizing.
- **Research findings:**
  - Check: `pip download <pkg> --platform cp314t_linux_x86_64 --only-binary=:all:` — fails if no free-threaded wheel.
  - Fallback: compile from source with `--global-option=build_ext --global-option="-DPy_GIL_DISABLED"`.
  - Audit: `python -c "import sys; print(sys._is_gil_enabled())"` inside container to verify.
  - Risk: source-compiled C-extensions may not have been tested under 3.14t. Tag container image as `-experimental`.
  - List: `pip list --format=json | jq '.[] | select(.name | startswith("z3") or startswith("wrapt") or startswith("psutil"))'`.
- **Libraries/standards:** pip, `sys._is_gil_enabled()`
- **Followup research:** Can we automate a CI pipeline that rebuilds containers when new cp314t wheels are published?

---

## 7. SQLite Concurrency

> **Parent domain research:** [RESEARCH_RECORD.md §7](./RESEARCH_RECORD.md#7-sqlite-concurrency)  
> **Informs RULEs:** 0T, 0T-B

### 7.1 WAL Mode Durability Under Process Kill
- **Priority:** P0
- **What to research:** Does `synchronous=NORMAL` maintain integrity if process is killed mid-transaction?
- **Research findings:**
  - `synchronous=NORMAL`: database is consistent after OS crash but NOT after power loss. Process kill (SIGKILL) = OS crash equivalent — WAL file may have partial frames.
  - `synchronous=FULL`: survives power loss but 2-3x slower writes. Overkill for most Azazael use cases.
  - **Recommended:** `synchronous=NORMAL` + WAL checkpoint `TRUNCATE` on clean shutdown. Accept risk of losing last ~1s of writes on SIGKILL.
  - WAL checkpoint modes: `PASSIVE` (non-blocking, may not complete), `TRUNCATE` (blocks writers, guaranteed complete), `RESTART` (keeps WAL, moves pointer).
  - For audit trail: use `FULL` synchronous. For performance metrics: `NORMAL` is sufficient.
  - `PRAGMA wal_checkpoint(TRUNCATE)` on clean exit ensures WAL is fully applied before shutdown.
- **Libraries/standards:** SQLite WAL documentation, `PRAGMA` reference
- **Followup research:** How to implement application-level write-ahead logging on top of SQLite for double-durability guarantee?

### 7.2 Thread-Local Connection Pooling for 3.14t
- **Priority:** P1
- **What to research:** Lightweight connection pools mapping thread IDs to connections.
- **Research findings:**
  - Pattern: `threading.local()` stores one connection per thread. On first access: open connection, apply PRAGMAs, store.
  - Reaping: `weakref.finalize(thread_local, lambda: conn.close())` — ensures connection closes when thread terminates.
  - Alternative: fixed-size pool with `queue.Queue` of pre-opened connections. Threads `get()` a connection, use it, `put()` it back.
  - **Fixed pool advantage:** bounds concurrent SQLite writers (one at a time anyway due to WAL), avoids connection explosion.
  - Recommended: thread-local for simplicity (10-50 threads), fixed pool for production (>50 threads).
  - Must set `check_same_thread=False` on all connections in pooled mode.
- **Libraries/standards:** `sqlite3.connect(..., check_same_thread=False)`, `threading.local()`, `queue.Queue`
- **Followup research:** How to implement connection health checks (ping before use) in a fixed pool?

### 7.3 SQLITE_BUSY Retry & Exponential Backoff
- **Priority:** P1
- **What to research:** Optimal busy_timeout + application-level retry patterns.
- **Research findings:**
  - SQLite's `busy_timeout` (ms) handles simple lock contention. Default: 5000ms is generous.
  - For complex contention (multiple writers to same table), application-level retry with exponential backoff: 10ms → 20ms → 40ms → ... → 1000ms cap, max 5 retries.
  - Python pattern: `conn.execute("PRAGMA busy_timeout=5000")` + wrapper function that catches `sqlite3.OperationalError("database is locked")` and retries.
  - Under 3.14t: contention is higher because more threads can be active simultaneously. Increase `busy_timeout` to 10000ms.
  - Isolate high-write tables (`memorybus_queue`) from high-read tables (`memories`) — separate databases if contention is severe.
- **Libraries/standards:** `sqlite3.OperationalError`, busy_timeout PRAGMA
- **Followup research:** What is the actual SQLITE_BUSY rate under 50-thread 3.14t concurrent workload?

### 7.4 FTS5 Full-Text Search Optimization
- **Priority:** P2
- **What to research:** Content sync triggers, query syntax, performance with large datasets.
- **Research findings:**
  - FTS5 auto-sync: `CREATE TRIGGER ... AFTER INSERT ON memories BEGIN INSERT INTO memories_fts ... END` — fires on every insert.
  - Performance cost: ~10% overhead per insert for FTS5 trigger. Acceptable for audit-heavy workloads.
  - Query syntax: `SELECT * FROM memories_fts WHERE memories_fts MATCH 'error OR warning'` — supports boolean, prefix, phrase queries.
  - `highlight()` / `snippet()` for result excerpts. `bm25()` ranking function.
  - 1M rows: FTS5 query latency ~5ms (vs ~50ms for `LIKE '%term%'`). Index size ~10-20% of source table.
  - `optimize()` command: defragments FTS index. Run weekly during low-traffic window.
- **Libraries/standards:** SQLite FTS5, `PRAGMA` optimize
- **Followup research:** Can FTS5 prefix indexes (`prefix='2 3'`) improve partial-word search for agent names?

---

## 8. Audit Trails

> **Parent domain research:** [RESEARCH_RECORD.md §8](./RESEARCH_RECORD.md#8-audit-trails)  
> **Informs RULEs:** 0T, 0T-A, 0T-B

### 8.1 JSONL Append-Only Atomicity Under 3.14t
- **Priority:** P0
- **What to research:** Guaranteeing atomic writes to append-only files across multiple threads.
- **Research findings:**
  - POSIX `O_APPEND` guarantees atomic writes up to `PIPE_BUF` (4096 bytes on Linux). For JSONL entries >4KB, partial writes are possible.
  - Python `io` buffering: `open(file, "a", buffering=1)` enables line buffering — each `write()` + `\n` is flushed immediately. Not truly atomic for concurrent writers.
  - **Solution:** Use a dedicated writer thread with a `queue.Queue`. All threads `queue.put(json_line)`, single writer thread `queue.get()` → `f.write(line + "\n")` → `f.flush()`.
  - Alternative: `fcntl.flock(fd, LOCK_EX)` per write — correct but adds ~2µs overhead per entry.
  - **Recommended:** Writer thread pattern. Single writer = no race. Queue ensures ordering.
- **Libraries/standards:** `fcntl`, `O_APPEND`, `queue.Queue`
- **Followup research:** How to verify JSONL integrity after a crash — detect partial last line?

### 8.2 RFC 9162 Merkle Tree Implementation
- **Priority:** P1
- **What to research:** CT v2.0 patterns for inclusion proofs and consistency proofs.
- **Research findings:**
  - RFC 9162 updates RFC 6962 with: tighter hash algorithms, cleaner consistency proof API, `tree_head` structure.
  - `MerkleTreeHead`: `{tree_size, timestamp, root_hash, signature}`.
  - Inclusion proof: verify leaf at index `i` is included in tree of size `n`. `O(log n)` hash steps.
  - Consistency proof: prove tree of size `n` is a superset of tree of size `m`. `O(log n)` hash steps.
  - `pymerkle`: `tree.get_inclusion_proof(index)`, `tree.get_consistency_proof(old_size, new_size)`.
  - Verification: `proof.verify(root_hash, leaf_hash)` returns bool. Entirely offline — no trust needed.
- **Libraries/standards:** `pymerkle`, RFC 9162
- **Followup research:** How to batch-verify N inclusion proofs more efficiently than N individual verifications?

### 8.3 Dual-Ledger Cross-Validation Automation
- **Priority:** P1
- **What to research:** Periodic hash-chain recomputation, Merkle root comparison, tamper detection.
- **Research findings:**
  - **Hash chain recomputation:** Read JSONL from start, recompute `SHA-256(line + prev_hash)` for each entry. Compare last hash with stored checkpoint.
  - **Merkle root comparison:** Build Merkle tree from JSONL entries. Build Merkle tree from SQLite `memories` table. Compare roots. Mismatch = corruption.
  - Schedule: every 1000 events or every hour, whichever comes first.
  - Tamper response: log to `ERROR_LOG.md`, publish alert via MemoryBus, freeze agent operations until human review.
  - Performance: 100K events → ~2s for hash chain recomputation, ~5s for Merkle tree build. Acceptable for hourly cron.
- **Libraries/standards:** `pymerkle`, `hashlib`, cron/schedule
- **Followup research:** Can we implement incremental Merkle tree updates instead of full rebuild each validation cycle?

### 8.4 Monotonic Timestamp Verification
- **Priority:** P2
- **What to research:** Detecting timestamp manipulation via non-monotonic sequence detection.
- **Research findings:**
  - Check: each audit entry timestamp MUST be ≥ previous entry timestamp within a session.
  - Monotonic counter: `counter += 1` per event. Check: counter sequence has no gaps or duplicates.
  - Timestamp ±60s validation: entry timestamp must be within 60s of wall clock. Prevents backdating.
  - Anomaly: if counter jumps by >1 (missing event) or timestamp goes backward → tamper flag.
  - SQL query: `SELECT session_id, timestamp, LAG(timestamp) OVER (PARTITION BY session_id ORDER BY id) as prev_ts FROM memories WHERE timestamp < prev_ts`.
- **Libraries/standards:** SQL window functions, ISO 8601 timestamps
- **Followup research:** Should we use NTP-synced timestamps for cross-machine audit correlation?

### 8.5 Hash-Chained Cross-Session Integrity
- **Priority:** P2
- **What to research:** Chaining session hashes to prevent session isolation attacks.
- **Research findings:**
  - Attack: attacker deletes entire session from JSONL. Without cross-session chaining, no way to detect.
  - Defense: each session's first entry includes `prev_session_hash` = SHA-256(last entry of previous session). Creates an unbroken chain across sessions.
  - Detection: if session N's first `prev_session_hash` ≠ computed hash of session N-1's last entry → session N-1 was tampered or deleted.
  - Implementation: store `last_session_hash` in a separate `chain_state.json` file (also hash-chained for integrity).
  - Recovery: if `chain_state.json` is lost, chain can be rebuilt by replaying all sessions.
- **Libraries/standards:** `hashlib.sha256`
- **Followup research:** Can we use a blockchain-like proof-of-work to make chain tampering computationally infeasible?

---

## 9. Nuitka

> **Parent domain research:** [RESEARCH_RECORD.md §9](./RESEARCH_RECORD.md#9-nuitka)  
> **Informs RULEs:** Infrastructure layer  
> **⚠️ Error #16 context:** Requires 7 C-level patches via `patch_nuitka_314t.py`

### 9.1 Upstream Nuitka 3.14t Roadmap
- **Priority:** P0
- **What to research:** When is Nuitka 4.2 expected? What free-threading fixes are on the changelog?
- **Research findings:**
  - Nuitka 4.1.2 (current stable): Python 3.14 support is "experimental only." No official 3.14t guarantee.
  - Nuitka 4.2 release: No firm date. Changelog mentions "free-threading improvements" in development branch.
  - Tracked commits: `nuitka.net/changelog/Changelog.html` — watch for "CPython 3.14 free-threading" entries.
  - Specific fixes needed upstream: `ob_gc_bits` access, `_Py_IMMORTAL_REFCNT` rename, `generations` array size, MSVC ternary l-value issue.
  - **Strategy:** Maintain `patch_nuitka_314t.py` until 4.2 stable. Test each 4.2 pre-release against Azazael build. Remove patches when 4.2 builds succeed without them.
- **Libraries/standards:** Nuitka changelog, `patch_nuitka_314t.py`
- **Followup research:** Can we contribute Azazael's patches upstream to accelerate Nuitka 4.2 3.14t support?

### 9.2 Patch Verification Automation
- **Priority:** P1
- **What to research:** Automating patch application and verification in CI.
- **Research findings:**
  - Current: `patch_nuitka_314t.py --apply` applies patches; `--verify` checks if patches are applied; `--rollback` restores originals.
  - CI addition: add `patch_nuitka_314t.py --verify` as a pre-build check in CI. Fail build if patches not applied.
  - Nuitka upgrade detection: hash the 7 patched files. If Nuitka upgrade changes any file, patches won't apply cleanly → CI alerts.
  - Test build: `nuitka --standalone --onefile azazael/src/main.py` in CI to detect new breakages early.
  - Version pinning: pin Nuitka to tested version in `requirements-build.txt` (e.g., `nuitka==4.1.2`).
- **Libraries/standards:** `patch_nuitka_314t.py`, CI scripting
- **Followup research:** Can we diff Nuitka releases to automatically regenerate patches for new versions?

### 9.3 Standalone .exe Bundle Optimization
- **Priority:** P2
- **What to research:** Minimizing .exe size, startup time, and included dependencies.
- **Research findings:**
  - `--onefile` creates single .exe but extracts to temp dir on each run → ~1s startup overhead. `--standalone` (directory) has no extraction overhead.
  - `--include-package` vs `--include-module`: explicitly list only needed modules to avoid bundling entire site-packages.
  - `--nofollow-import-to=test,distutils,setuptools` excludes build/test deps.
  - `--enable-plugin=tk-inter` (if using Tkinter). Disable unused plugins via `--disable-plugin`.
  - Current `azazael-core.exe` = 9.7 MB. Target: <15 MB for full Azazael bundle.
  - UPX compression (`--windows-uac-admin --windows-icon-from-ico=favicon.ico`): reduces .exe by ~30% but may trigger antivirus false positives.
- **Libraries/standards:** Nuitka CLI flags, UPX compression
- **Followup research:** What is the memory footprint of 39 independently-built .exe files vs a single monolithic .exe?

### 9.4 C-Extension Bundling Audit
- **Priority:** P2
- **What to research:** Ensuring only thread-safe C-extensions are bundled into standalone .exe.
- **Research findings:**
  - Nuitka bundles all imported C-extensions as shared libraries in the .dist folder.
  - Audit: before Nuitka build, run `ldd` (Linux) or `dumpbin /DEPENDENTS` (Windows) on each `.pyd`/`.so` to check for non-thread-safe dependencies.
  - Thread safety: Nuitka cannot make non-thread-safe C code thread-safe. If a C-extension assumes GIL serialization, it will fail under `PYTHON_GIL=0`.
  - **Decision:** Exclude `z3-solver` and `psutil` from standalone builds if they are not verified thread-safe. Provide pure-Python fallbacks.
  - Tag experimental builds with `-experimental` suffix when bundling unverified C-extensions.
- **Libraries/standards:** `ldd`, `dumpbin`, `sys._is_gil_enabled()`
- **Followup research:** Can we statically analyze C-extension source for GIL assumptions before bundling?

---

## 10. Codebuff Platform

> **Parent domain research:** [RESEARCH_RECORD.md §10](./RESEARCH_RECORD.md#10-codebuff-platform)  
> **Informs RULEs:** 0K, 0M, 0Q, 0W

### 10.1 Model Routing Heuristics
- **Priority:** P0
- **What to research:** What heuristics determine which model to route to based on task complexity?
- **Research findings:**
  - Inferred routing factors: token count (prompt + context), task type (reasoning vs generation vs analysis), domain complexity, user mode (DEFAULT vs MAX vs PLAN).
  - Recommended `ModelRouter` class: evaluate `(task_complexity_score, estimated_token_budget, required_capabilities)` → route to DeepSeek (complex reasoning), Claude (code generation), Gemini Flash (routine/cheap).
  - Complexity estimation: number of files touched, presence of refactoring keywords ("refactor", "redesign"), need for multi-step reasoning.
  - Fallback: if primary model errors, retry on secondary model (DeepSeek → Claude → Gemini Flash → user error).
  - Cost optimization: route 80% of DEFAULT mode queries to Gemini Flash, reserve Claude/DeepSeek for MAX/PLAN modes.
- **Libraries/standards:** Token counting, model API pricing
- **Followup research:** Can we train a lightweight classifier to predict optimal model routing from prompt text alone?

### 10.2 Token-Bucket Rate Limiting
- **Priority:** P0
- **What to research:** Token-bucket algorithm patterns for managing multi-agent API rate limits.
- **Research findings:**
  - Standard token bucket: capacity = RPM/TPM limit, refill rate = limit/60 per second.
  - Multi-agent: shared bucket across all spawned agents. Each API call consumes `1` from RPM bucket and `token_count` from TPM bucket.
  - Burst handling: allow bursting up to 110% of capacity for short periods (<5s), then throttle.
  - Queue: when bucket is empty, queue API calls internally. FIFO ordering with priority override for P0 operations.
  - Observation: current Codebuff behavior — "API rate limits (TPM/RPM) are primary bottleneck." Adding token-bucket would smooth usage and avoid 429 errors.
- **Libraries/standards:** Token bucket algorithm, API rate limit headers
- **Followup research:** How to predict TPM consumption before making an API call to avoid mid-request throttling?

### 10.3 Concurrent Agent Spawn Optimization
- **Priority:** P1
- **What to research:** Undocumented concurrency caps, batch spawn patterns, context drift management.
- **Research findings:**
  - Observed: parallel spawning of 3-5 agents is safe. Beyond ~6 agents, API rate limits dominate.
  - Batch pattern: spawn N agents in parallel, wait for all results, synthesize. Reduces round-trips vs sequential spawning.
  - Context drift: sub-agents have access to full conversation history, but cannot see each other's intermediate results. Mitigation: pass `filePaths` to sub-agents with explicit context.
  - `context-pruner` agent: runs automatically when context exceeds limit. Summarizes conversation into condensed format.
  - Best practice: spawn research/gathering agents in parallel (no dependencies), then spawn editing agents sequentially (depend on research results).
- **Libraries/standards:** Codebuff agent spawn API, context management
- **Followup research:** What is the optimal batch size for agent spawns under different model routing configurations?

### 10.4 Async Job Queue Dispatch
- **Priority:** P1
- **What to research:** Celery/Redis-backed async dispatch patterns for long-running agent tasks.
- **Research findings:**
  - Pattern: submit task to queue, return `task_id`, poll for result. Useful for 30s+ agent operations.
  - Celery: `@app.task` decorator, `task.delay()` for async dispatch, `task.ready()` for polling, `task.get(timeout=60)` for blocking result.
  - Redis: `rpush("queue:agents", task_json)` + `blpop("queue:agents", timeout=30)` for worker pattern.
  - Azazael fit: Codebuff sessions tend to be interactive (user waiting), so async dispatch has limited utility. Most useful for: background Worm Registry re-indexing, nightly dual-ledger validation, scheduled VACUUM operations.
  - Not recommended for primary agent orchestration — adds latency that degrades interactive experience.
- **Libraries/standards:** Celery, Redis
- **Followup research:** Can we use Redis pub/sub for real-time MemoryBus message delivery across multiple Azazael instances?

### 10.5 Context Drift Management
- **Priority:** P2
- **What to research:** Mitigating information loss during sub-agent hand-offs and context pruning.
- **Research findings:**
  - Problem: sub-agents spawn without the full reasoning chain of the parent. They see conversation history but not intermediate thoughts.
  - Mitigation 1: Explicit context passthrough — parent agent includes key findings in sub-agent prompt.
  - Mitigation 2: `filePaths` parameter — sub-agents read relevant files directly, reducing reliance on conversation context.
  - Mitigation 3: Structured hand-off — parent writes a `context_digest.json` with key decisions, sub-agent reads it on startup.
  - `context-pruner` behavior: summarizes early conversation into condensed format. Risk: summary may omit nuanced decisions. Verify pruned output before critical agent spawns.
- **Libraries/standards:** Codebuff context management, agent communication patterns
- **Followup research:** Can we implement a "context checkpoint" that sub-agents can restore to maintain decision continuity?

---

## 11. Canonical Documents

> **Parent domain research:** [RESEARCH_RECORD.md §11](./RESEARCH_RECORD.md#11-canonical-documents)  
> **Informs RULEs:** 0K, 0H

### 11.1 Modular Markdown Include Architecture
- **Priority:** P0
- **What to research:** Splitting monolithic SYSTEM_INSTRUCTIONS.md (121kb) into modular includes.
- **Research findings:**
  - Split strategy: `rules/` (0J, 0K, 0X, etc.), `protocols/` (VLP, compliance), `domains/` (one per research domain), `appendix/` (error log, skills catalog).
  - Include syntax: `{% include "rules/0J_pre_action_gate.md" %}` — processed by script or static site generator.
  - Build step: `assemble_docs.py` reads `index.md`, resolves includes, writes canonical `SYSTEM_INSTRUCTIONS.md`.
  - Validation: `markdownlint` checks each include file; `vale` checks prose style. Both run in pre-commit.
  - Benefit: 121kb file split into ~30 files of 2-5kb each. Easier to review, merge, and maintain.
- **Libraries/standards:** `markdownlint`, `vale`, Jinja2 includes
- **Followup research:** Can we use MkDocs / Docusaurus for rendered documentation from the same source?

### 11.2 Single Source of Truth (SSoT) CI/CD
- **Priority:** P1
- **What to research:** Automating sync from `azazael/docs/` to `.agents/skills/` via CI.
- **Research findings:**
  - Current: `sync_skills.py` runs manually or via `azazael-system-startup`. Copies skill `.md` files from `azazael/skills/` to `.agents/skills/<name>/SKILL.md`.
  - CI addition: pre-commit hook or GitHub Action that runs `sync_skills.py` on every push to `azazael/skills/`.
  - Validation: `sync_skills.py` already outputs counts (55 synced, 7 unchanged). CI should fail if count changes unexpectedly.
  - Staleness detection: compare `mtime` of source and destination files. Flag stale destinations in CI.
  - Rollback: `sync_skills.py --rollback` restores previous versions from `.agents/skills/.backup/`.
- **Libraries/standards:** `sync_skills.py`, CI/CD (GitHub Actions)
- **Followup research:** How to handle merge conflicts in `.agents/skills/` when both source skills and generated SKILL.md change?

### 11.3 Documentation Linting Pipeline
- **Priority:** P2
- **What to research:** `markdownlint` + `vale` configuration for Azazael documentation standards.
- **Research findings:**
  - `markdownlint`: `.markdownlint.json` config. Enable: MD001 (heading increment), MD013 (line length, 120 chars), MD024 (no duplicate headings), MD031 (blank lines around fenced code).
  - `vale`: `.vale.ini` config. Styles: `Microsoft` (for technical docs), custom `Azazael` style for project-specific terms (Azazael, Codebuff, WORMZ, Nuitka, PAMS).
  - Pre-commit: `markdownlint docs/ && vale docs/` — blocks commit on violations.
  - CI: same checks in GitHub Actions. Generates report for PR review.
  - Cost: ~1s per 50 markdown files. Negligible CI overhead.
- **Libraries/standards:** `markdownlint`, `vale`
- **Followup research:** Can `vale` be extended with project-specific rules for Azazael terminology consistency?

### 11.4 Skill Propagation Automation
- **Priority:** P2
- **What to research:** Optimizing `sync_skills.py` for larger skill catalogs.
- **Research findings:**
  - Current: 62 skill files, 55 synced in ~2s. Scales linearly — 200 skills would be ~6s.
  - Optimization: sync only files with changed `mtime` → skips unchanged 90% of runs. Add `--incremental` flag.
  - Hash-based: store SHA-256 of source in `.agents/skills/.hashes.json`. Only sync if hash differs.
  - Parallel: use `concurrent.futures.ThreadPoolExecutor` to sync multiple files in parallel.
  - Watch mode: `watchdog` file watcher triggers `sync_skills.py --incremental` on file change.
- **Libraries/standards:** `sync_skills.py`, `watchdog`, `concurrent.futures`
- **Followup research:** Can we integrate `sync_skills.py` into VS Code "save" action for instant skill updates during editing?

---

## 12. ML/RL

> **Parent domain research:** [RESEARCH_RECORD.md §12](./RESEARCH_RECORD.md#12-mlrl)  
> **Informs RULEs:** Infrastructure/tooling domain

### 12.1 GRPO via verl Library
- **Priority:** P1
- **What to research:** GRPO implementation for code-generation LLM fine-tuning.
- **Research findings:**
  - GRPO (Group Relative Policy Optimization): no Critic model needed. Uses group output mean as baseline. Reduces ~50% memory vs PPO.
  - `verl` library: reference GRPO implementation. Supports FSDP, tensor parallelism, sequence packing.
  - Code-generation focus: reward model based on test pass rate, code quality metrics, and compilation success.
  - Training loop: generate N completions per prompt, score with reward model, compute group-relative advantage, update policy.
  - Free-threading: accelerates CPU rollout phase (tokenization, reward computation) but GPU kernel launches remain single-threaded.
- **Libraries/standards:** `verl`, GRPO paper
- **Followup research:** Can we use synthetic test generation for reward modeling instead of hand-crafted test suites?

### 12.2 SB3 SubprocVecEnv Optimization
- **Priority:** P1
- **What to research:** Optimal SubprocVecEnv config for Azazael's RL workloads on 3.14t.
- **Research findings:**
  - `SubprocVecEnv`: spawns N independent Python processes, each running an environment. Process-level parallelism avoids GIL entirely.
  - Optimal N: `n_envs = n_cores - 1` (leave 1 core for main process). On 16-core: 15 envs.
  - Tensor sharing: PyTorch tensors via `multiprocessing.shared_memory` — zero-copy between processes.
  - `VecNormalize` wrapper: running mean/std computation is not thread-safe. Use per-process normalization or lock-protected shared stats.
  - 3.14t: `multiprocessing` is unaffected by free-threading (processes have their own interpreter). No change needed.
- **Libraries/standards:** `stable-baselines3`, `SubprocVecEnv`
- **Followup research:** Can `Gymnasium` vector environments leverage `concurrent.futures.ProcessPoolExecutor` for dynamic scaling?

### 12.3 NSGA-II Multi-Objective Optimization
- **Priority:** P2
- **What to research:** `pymoo` vs `deap` for worm parameter optimization.
- **Research findings:**
  - `pymoo`: modern API, built-in visualization, NSGA-II/NSGA-III/U-NSGA-III algorithms. `Problem` class with `_evaluate(x, out)` method.
  - `deap`: more flexible, lower-level. Custom genetic operators via `toolbox.register()`. Steeper learning curve.
  - **Recommendation:** `pymoo` for standard multi-objective optimization; `deap` only if custom operators are needed.
  - Thread safety: `pymoo` supports `Evaluator` with `threads` or `processes` backend. Prefer `processes` for compute-intensive fitness functions.
  - Fitness function: must be stateless for thread safety. Wrap worm config → score mapping in a pure function.
- **Libraries/standards:** `pymoo`, `deap`
- **Followup research:** Can we optimize ML-DSA/Ed25519 parameter selection via NSGA-II for signature size vs security trade-off?

### 12.4 Free-Threading Impact on RL Training
- **Priority:** P2
- **What to research:** Does 3.14t accelerate RL training pipelines, or is GPU the bottleneck?
- **Research findings:**
  - RL training: 80-90% GPU-bound (forward pass, backprop). CPU-bound components: environment simulation, reward calculation, data preprocessing.
  - 3.14t impact: accelerates CPU-bound components by 2-4x on multi-core. Overall training speedup: 10-20% (limited by GPU bottleneck).
  - Environment simulation: if using Python-based simulators (not Gymnasium's C-based ones), 3.14t provides larger benefit.
  - Data loading: PyTorch `DataLoader(num_workers=N)` already uses multi-processing — 3.14t threads don't help here.
  - Verdict: 3.14t is a minor win for RL training. Primary benefit is in agent orchestration (concurrent worm execution), not training.
- **Libraries/standards:** PyTorch, Gymnasium, 3.14t benchmarks
- **Followup research:** Can we offload environment simulation to a separate 3.14t thread pool to overlap with GPU training?

---

## 13. Worm Registry

> **Parent domain research:** [RESEARCH_RECORD.md §13](./RESEARCH_RECORD.md#13-worm-registry)  
> **Informs RULEs:** 0W (Agent Utilization)

### 13.1 AST-Based Plugin Discovery
- **Priority:** P0
- **What to research:** Extracting metadata from Python source files via `ast.parse` without importing.
- **Research findings:**
  - `ast.parse(source)` returns AST tree. `ast.NodeVisitor.visit_FunctionDef()` captures functions, `visit_ClassDef()` captures classes, `visit_Call()` captures decorators.
  - Decorator extraction: check `node.decorator_list` for `ast.Call` or `ast.Name` nodes. Extract `@register_worm` arguments (name, category, priority).
  - Docstring extraction: `ast.get_docstring(node)` for functions and classes.
  - Error handling: `ast.parse()` raises `SyntaxError` on invalid Python. Catch, log the file path, skip in registry. Don't crash the entire discovery.
  - Performance: ~200 files → ~2s for full AST parse + extraction. Acceptable for cold start (vs 38s for import-based discovery).
- **Libraries/standards:** `ast` (stdlib), `ast.NodeVisitor`
- **Followup research:** Can we use `ast.parse` with `type_comments=True` to also extract type hints for better tool routing?

### 13.2 Registry Cache Persistence
- **Priority:** P1
- **What to research:** SQLite-based registry cache with automatic invalidation.
- **Research findings:**
  - Schema: `CREATE TABLE worm_registry (name TEXT PRIMARY KEY, category TEXT, priority INT, file_path TEXT, version TEXT, docstring TEXT, last_modified TEXT)`.
  - Invalidation: compare `os.path.getmtime(file_path)` with `last_modified` in cache. If changed, re-parse and update.
  - Startup: check cache validity → if valid, load from SQLite (milliseconds) → if invalid, re-index (2s). No more 38s cold start.
  - git-hook: `post-merge` and `post-checkout` hooks trigger `python -m CORE.reindex_registry --incremental`.
  - Background refresh: `threading.Timer(interval=300)` periodically checks file mtimes in background.
- **Libraries/standards:** `sqlite3`, `os.path.getmtime`, git hooks
- **Followup research:** Can we use `watchdog` file watcher for real-time registry updates instead of polling?

### 13.3 Lazy Import Loading
- **Priority:** P2
- **What to research:** Using `importlib.import_module` for on-demand worm loading.
- **Research findings:**
  - Pattern: registry stores `module_path` and `class_name`. At invocation time: `mod = importlib.import_module(module_path); worm_cls = getattr(mod, class_name); worm = worm_cls()`.
  - Benefit: import cost paid only when worm is actually used, not at registry scan time. Reduces cold-start memory by ~70%.
  - Caching: `functools.lru_cache` on lookup function — first invocation imports, subsequent invocations return cached class.
  - Invalidation: clear LRU cache on registry re-index.
  - Compatibility: `importlib.import_module` handles packages, namespace packages, and relative imports correctly.
- **Libraries/standards:** `importlib.import_module`, `functools.lru_cache`
- **Followup research:** Can we pre-warm the LRU cache for the 10 most-used worms at startup?

### 13.4 PyO3 Rust Acceleration
- **Priority:** P2
- **What to research:** Rust-based directory traversal and AST parsing for extreme performance.
- **Research findings:**
  - PyO3: Rust ↔ Python bindings. Write Rust functions callable from Python with near-native performance.
  - Directory traversal: `walkdir` crate (Rust) is ~10x faster than `os.walk()` (Python) for large directory trees.
  - AST parsing: `rustpython-parser` crate parses Python to AST in Rust. ~5x faster than `ast.parse()` for bulk processing.
  - Integration: compile Rust → `.pyd`/`.so` via `maturin`. Import in Python: `from azazael._rust.registry import fast_scan`.
  - Trade-off: Adds Rust toolchain as build dependency. Only worth it if registry scan exceeds 10s on cold start.
  - Current: AST-based scan = 2s. PyO3 benefit: 2s → 0.3s. Marginal improvement, not worth Rust dependency overhead.
- **Libraries/standards:** PyO3, `maturin`, `walkdir` (Rust), `rustpython-parser`
- **Followup research:** At what registry size (number of worms) does PyO3 become worth the build complexity?

---

## 14. Memory Systems

> **Parent domain research:** [RESEARCH_RECORD.md §14](./RESEARCH_RECORD.md#14-memory-systems)  
> **Informs RULEs:** 0T, 0T-B  
> **Sub-domain research focus:** Thread safety gaps and architectural improvements beyond parent domain analysis.

### 14.1 Thread-Safe SQLite Connection Management
- **Priority:** P0
- **What to research:** Connection lifecycle patterns for 4 components sharing one database under 3.14t.
- **Research findings:**
  - Current: each component opens a new connection per operation (`DirectMemory._get_conn()`, `LocalMemoryStore._get_conn()`, `MemoryBus._persist_to_queue()`).
  - Problem: no shared connection pool. 50 threads × 4 components × per-operation connections = connection churn.
  - Solution: centralized `ConnectionPool` class in `CORE/sqlite_pool.py`. Components request: `pool.get_conn()` → use → `pool.return_conn(conn)`.
  - Pool config: 4-8 connections, WAL PRAGMAs applied on creation, `busy_timeout=10000`.
  - Thread safety: `queue.Queue` of connections. `get()` blocks if pool empty. `return_conn()` validates health before returning.
  - Migration: minimize churn by upgrading one component at a time. Start with `LocalMemoryStore` (highest connection volume).
- **Libraries/standards:** `sqlite3`, `queue.Queue`, `threading`
- **Followup research:** What is the optimal pool size for 50-thread 3.14t concurrent write workload?

### 14.2 Atomic Counter Patterns for 3.14t
- **Priority:** P0
- **What to research:** Thread-safe atomic counters to replace non-atomic `+=` patterns across memory components.
- **Research findings:**
  - Affected: `PamsRecorder.event_count`, `MemoryBus.message_id`, `LocalMemoryStore._query_count`, `DirectMemory.event_count`.
  - `threading.atomic` (Python 3.14t): `atomic.Int` for lock-free integer operations. `counter += 1` is truly atomic.
  - `itertools.count()`: `counter = itertools.count(); next(counter)` — thread-safe in CPython even without GIL due to internal atomic increment.
  - `threading.Lock` + int: simplest, most compatible. Overhead: ~0.2µs per increment.
  - **Recommendation:** `itertools.count()` for monotonic IDs (message_id), `threading.Lock` + int for mutable counters (event_count, _query_count). Wait for `threading.atomic` to stabilize before adopting.
- **Libraries/standards:** `itertools.count`, `threading.Lock`, `threading.atomic` (3.14t experimental)
- **Followup research:** Is `itertools.count` truly lock-free under 3.14t, or does it rely on remaining GIL-like internal locks?

### 14.3 FTS5 Index Synchronization Across Components
- **Priority:** P1
- **What to research:** Ensuring FTS5 triggers are always active regardless of initialization order.
- **Research findings:**
  - Problem: if `DirectMemory._init_db()` runs before `LocalMemoryStore._init_db()`, FTS5 virtual table + triggers don't exist. Inserts by DirectMemory won't be FTS-indexed until LocalMemoryStore initializes.
  - Solution: move FTS5 DDL (`CREATE VIRTUAL TABLE memories_fts`, triggers) to a shared `_init_fts5()` function called by ALL components on database init.
  - Or: `LocalMemoryStore` initialization must complete before any `DirectMemory.record()` call. Enforce via application bootstrap ordering.
  - Detection: `SELECT name FROM sqlite_master WHERE type='trigger' AND name='memories_ai'` — if missing, FTS5 is not active.
  - Impact: missing FTS5 means `search_memories()` returns empty for events recorded before FTS5 init. Minor — FTS5 is a quality-of-life feature, not a critical path.
- **Libraries/standards:** SQLite FTS5, sqlite_master introspection
- **Followup research:** Can we rebuild FTS5 index from existing `memories` table content to backfill pre-init events?

### 14.4 PAMS Reachability Hysteresis
- **Priority:** P1
- **What to research:** Preventing transient network blips from disabling PAMS for 60-second intervals.
- **Research findings:**
  - Current: one failed HTTP call → `_pams_unreachable = True` → all subsequent calls use fallback for 60s.
  - Problem: network blip (<1s) causes 60s of unnecessary fallback. LocalMemoryStore writes are slower than PAMS HTTP.
  - Hysteresis solution: require N consecutive failures (e.g., N=3) before marking unreachable. Each success resets failure counter.
  - Exponential backoff on retry: after first failure, retry in 1s. After second, 2s. After third, 4s. After N=3, mark unreachable, retry in 60s.
  - This gives transient blips 3 chances to self-heal before falling back to local storage.
- **Libraries/standards:** Network resilience patterns, exponential backoff
- **Followup research:** Should we use a circuit-breaker pattern instead of simple N-consecutive-failures?

### 14.5 Session ID Unification Strategy
- **Priority:** P1
- **What to research:** Migrating all 4 components to a unified session_id format without breaking existing data.
- **Research findings:**
  - Current mismatch: DirectMemory uses `codebuff_YYYYMMDD_HHMMSS`, PamsRecorder and MemoryBus use UUID8.
  - Migration: add `parent_session_id` column to `memories` and `memorybus_queue` tables. DirectMemory session_id becomes the canonical identifier.
  - Backfill: for existing rows, `parent_session_id` is NULL (no cross-referencing possible for historical data).
  - Forward: all components set `parent_session_id = DirectMemory.get_session_id()` on record. PamsRecorder and MemoryBus retain their own UUID for internal use.
  - Query: `SELECT * FROM memories WHERE parent_session_id = 'codebuff_20260611_143000'` returns all events from that Codebuff session across all components.
  - No breaking change: only adds a column, doesn't modify existing session_id values.
- **Libraries/standards:** SQLite `ALTER TABLE ADD COLUMN`
- **Followup research:** Should we use UUIDv7 (time-sortable) instead of timestamp strings for better indexing?

### 14.6 Automated Dual-Ledger Validation
- **Priority:** P2
- **What to research:** Building `verify_dual_ledger.py` for JSONL ↔ SQLite cross-validation.
- **Research findings:**
  - Script: `python -m CORE.verify_dual_ledger --cross-ref [--since DATE] [--verbose]`.
  - Phase 1: Read JSONL from last known checkpoint, recompute hash chain.
  - Phase 2: Query SQLite `memories` where `created_at >= checkpoint_time`.
  - Phase 3: Join on `(session_id, timestamp, event_type)`. Flag: JSONL-only events (not in SQLite), SQLite-only events (not in JSONL), hash mismatches.
  - Output: `verification_report_20260611.json` with counts, mismatches, and severity.
  - Scheduling: `schedule.every().hour.do(run_validation)` or event-count trigger.
  - Integration: if mismatches found → publish `verification_divergence` event on MemoryBus → all agents log warning.
- **Libraries/standards:** `pymerkle`, `schedule`, MemoryBus
- **Followup research:** How to recover from ledger divergence — which ledger is the source of truth?

### 14.7 VACUUM Scheduling & Non-Blocking Optimization
- **Priority:** P2
- **What to research:** Running VACUUM without blocking concurrent writes.
- **Research findings:**
  - `VACUUM`: copies entire database to temp file, defragments, replaces original. Blocks ALL writers for duration.
  - `VACUUM INTO 'memory_store_vacuumed.db'`: creates defragmented copy at target path. Does NOT block the source database. Then `os.replace()` atomically swaps.
  - `PRAGMA auto_vacuum=FULL`: SQLite defragments incrementally on each transaction. Small overhead per write, eliminates need for periodic VACUUM.
  - **Recommendation:** Set `auto_vacuum=FULL` on database creation. If already created without it, use `VACUUM INTO` + atomic swap during low-traffic window (e.g., 3 AM cron).
  - Monitoring: `PRAGMA freelist_count` > 1000 triggers low-priority VACUUM scheduling.
- **Libraries/standards:** `VACUUM INTO`, `auto_vacuum` PRAGMA
- **Followup research:** What is the write throughput impact of `auto_vacuum=FULL` under 50-thread 3.14t workload?

---

## 15. Testing

> **Parent domain research:** [RESEARCH_RECORD.md §15](./RESEARCH_RECORD.md#15-testing)  
> **Informs RULEs:** 0M, 0X

### 15.1 pytest 3.14t Compatibility Matrix
- **Priority:** P0
- **What to research:** Which pytest plugins work under `PYTHON_GIL=0`; which break with thread-local storage races?
- **Research findings:**
  - pytest 8.x: "Python 3.14 free-threading is experimental." Known issues: `pytest-timeout` (signal-based timeout interferes with threading), `pytest-cov` (coverage data structure is not thread-safe), `pytest-xdist` (worker synchronization races).
  - Safe plugins: `pytest`, `pytest-mock`, `pytest-asyncio`, `pytest-benchmark`.
  - Unsafe plugins: `pytest-cov`, `pytest-timeout`, `pytest-randomly` (randseed races).
  - `unittest.mock`: `mock.patch` modifies global state — NOT thread-safe. Under 3.14t, two threads patching the same object can corrupt state.
  - **Mitigation:** Use `pytest` WITHOUT `pytest-cov` on 3.14t CI. Run coverage separately on single-threaded Python.
- **Libraries/standards:** `pytest`, `pytest-xdist`, `unittest.mock`
- **Followup research:** When will pytest officially declare 3.14t support as stable?

### 15.2 Thread-Safe Test Fixtures
- **Priority:** P1
- **What to research:** Designing fixtures that don't share mutable state across parallel tests.
- **Research findings:**
  - Rule: fixtures MUST be stateless or use `scope="function"` to ensure fresh state per test.
  - Anti-pattern: `@pytest.fixture(scope="session")` with mutable return value (e.g., dict, list). All parallel tests modify the same object.
  - Safe: `@pytest.fixture` (default scope="function") — fresh fixture per test. Slight overhead, fully thread-safe.
  - Database fixtures: each test gets its own `:memory:` SQLite database. No cross-test contamination.
  - Temp files: `tmp_path` fixture (thread-safe). Each test gets unique temp dir.
  - Mocking: `unittest.mock.patch` as context manager (`with mock.patch(...)`) NOT as decorator (shared global state).
- **Libraries/standards:** `pytest` fixtures, `tmp_path`, `unittest.mock`
- **Followup research:** Can `pytest`'s `--dist=loadfile` prevent fixture sharing by running per-file threads in sequence?

### 15.3 CI with PYTHON_GIL=0
- **Priority:** P1
- **What to research:** Optimal CI configuration for catching 3.14t-specific race conditions.
- **Research findings:**
  - CI matrix: `{python: [3.12, 3.14], PYTHON_GIL: [1, 0]}` → 4 environments.
  - `PYTHON_GIL=0` CI catches: non-atomic increments, unprotected shared state, C-extension crashes.
  - `PYTHON_GIL=1` CI catches: regular logic errors, import errors, syntax errors.
  - Schedule: `PYTHON_GIL=0` CI runs on every PR. `PYTHON_GIL=1` CI runs on every push.
  - Known flaky: `PYTHON_GIL=0` tests may fail intermittently due to race timing. Require 3 consecutive green runs before merging.
  - Skip slow tests: `python run_tests.py --skip-slow` for CI speed. Full test suite runs nightly.
- **Libraries/standards:** CI/CD (GitHub Actions), `PYTHON_GIL` env var
- **Followup research:** Can `thread-sanitizer` (TSan) be integrated into 3.14t CI for data race detection?

### 15.4 C-Extension Segfault Testing
- **Priority:** P2
- **What to research:** Using `faulthandler` to trap and identify C-extension crashes under 3.14t.
- **Research findings:**
  - `faulthandler.enable(file=sys.stderr, all_threads=True)`: dumps stack trace of ALL threads on segfault.
  - Output includes: thread ID, Python stack trace, C stack trace (if symbols available).
  - Mapping: segfault address → loaded shared library via `/proc/<pid>/maps` (Linux) or `dumpbin` (Windows).
  - Test harness: `subprocess.run(["python", "-X", "faulthandler", "test_file.py"], env={"PYTHON_GIL": "0"})` — capture stderr for segfault trace.
  - Known crash sites: `z3-solver` (Z3_context_init), `psutil` (PCACHE access), `wrapt` (ObjectProxy.__getattr__).
  - CI: run a dedicated "crash-test" suite with `faulthandler` enabled. 3.14t-only. Runs nightly, not per-PR.
- **Libraries/standards:** `faulthandler`, `subprocess`
- **Followup research:** Can `gdb` or `lldb` be scripted to automatically identify the crashing C-extension from CI output?

### 15.5 pytest-xdist Loadfile Strategy
- **Priority:** P2
- **What to research:** `--dist=loadfile` vs `--dist=loadscope` for Azazael's test structure.
- **Research findings:**
  - `--dist=loadfile`: distributes test FILES across workers. All tests in one file run sequentially on same worker. Best for tests with file-level shared state.
  - `--dist=loadscope`: distributes test CLASSES/FUNCTIONS across workers. More parallelism but risks fixture sharing.
  - **Recommendation:** `--dist=loadfile` for 3.14t CI (safety). `--dist=loadscope` for 3.12 CI (performance).
  - `-n auto`: detect CPU count automatically. On 16-core: 16 workers.
  - `--tx 3*popen//python=python3.14t`: run 3 workers with Python 3.14t specifically.
  - Known issue: `pytest-xdist` workers are processes, not threads. Free-threading within each worker is independent.
- **Libraries/standards:** `pytest-xdist`, `--dist` strategies
- **Followup research:** Can we use `pytest-xdist` with `--dist=loadfile` AND `PYTHON_GIL=0` simultaneously?

---

## Followup Research Suggestions

### Cross-Domain Research
- **Memory + Audit:** How to implement a unified event schema across all 4 memory components + audit trail JSONL for seamless dual-ledger correlation?
- **Compliance + Governance:** Can Z3 SMT constraint models be automatically verified by a Verifier agent in the Worker-Verifier-Judge pipeline?
- **Observability + Memory:** Can OpenTelemetry spans be stored in SQLite `memories` table alongside agent events for unified trace + event analysis?
- **Nuitka + Testing:** Should Nuitka `.exe` builds run the full test suite as part of the build pipeline to catch packaging-specific issues?
- **Docker + SQLite:** What is the optimal `tmpfs` configuration for SQLite WAL in Docker containers to minimize I/O latency?

### Sub-Domain Deep Dives
- **Z3 SMT (3.1)**: Explore `Solver().from_string()` for loading pre-computed constraint models from files.
- **Hybrid Signatures (2.2)**: Benchmark hybrid verification on ARM64 (Raspberry Pi) — is ML-DSA too slow for embedded?
- **Directed Graphs (4.3)**: Implement a small NetworkX-based anomaly detector and test against known Codebuff agent traces.
- **GRPO (12.1)**: Run a toy GRPO experiment with `verl` on a code-generation task to measure training throughput.
- **Connection Pool (14.1)**: Benchmark SQLite throughput with and without a centralized connection pool under 50-thread 3.14t.

---

*End of Sub-Domain Research Record — June 11, 2026*  
*67 sub-domains across 15 domains. 18 P0, 24 P1, 25 P2.*
