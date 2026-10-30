# Upgrade radar — 2026-10-30

Two questions, one document: **do we need an eval suite** (yes — shipped, §A) and
**what else should we upgrade** (§B, sixteen candidates, each with a verdict).

Rules this document follows, because the last session produced four confident
claims that were wrong:

- **Read ≠ measured.** Every candidate is tagged `READ` (found in a source) or
  `MEASURED` (observed on this machine, command shown). A `READ` claim is a
  pointer, not a fact.
- **A verdict is one of ADOPT / TRIAL / WATCH / REJECT**, and REJECT names the
  measurement that killed it.
- **No upgrade is adopted because it is new.** Each one names the defect in
  *this* tree that it removes.

---

## §0 — One correction to the record, first

The previous session stated **"`pytest-timeout` is not installed"** and used that
to explain why a single hanging test could wedge 5,380 tests with no ceiling.
That was true of `python` on PATH (3.14.7, GIL on) and **false of production**:

```
C:/Azazael/.venvs/py315t/Scripts/python.exe
pytest 9.1.1 · pytest-timeout 2.4.0 · pytest-xdist 3.8.0 · hypothesis 6.168.4
--timeout=2 on a 5s sleep → "+++ Timeout +++"            MEASURED 2026-10-30
```

So the bound existed all along and **was simply never passed**. The deadlock was
still real (`governance.py:791` reading 5.4 GB), but the "no ceiling available"
half of that diagnosis was an unverified claim about a control — exactly RULE
0B-D. The remedy is now a one-line default, not a dependency (§B-2).

---

## §A — The eval suite

### What exists

| file | role |
|---|---|
| `tools/agent_eval.py` | harness: discover cases, grade, report, `--self-test` |
| `evals/cases/*.json` | 9 executable regression cases + 10 behavioural specifications |

Two design decisions, both taken from the published guidance rather than
invented:

1. **Grade state, not the transcript.** *"Check state instead of trusting the
   transcript — an agent's confirmation message is not evidence."* (Arize,
   *Agent evals from traces*, 2026-08-19.) Every regression case here is a
   **command + expected exit/pattern**, so a case cannot pass because an agent
   said it did.
2. **Grade the ledger, the tool calls and the reply as separate checks**
   (multi-trial harness guidance, 2026). The behavioural specs in
   `zz-behaviour-specs.json` are written that way: `tool_calls:` / `args:` /
   `state:` / `transcript:` graders are distinct lines, not one blob score.

### What it does today — measured

```
python tools/agent_eval.py --self-test
  PASS  passing command grades PASS
  PASS  failing command grades FAIL
  PASS  timeout grades FAIL, not a hang
self-test: harness can distinguish pass, fail and timeout

python tools/agent_eval.py --suite regression
  9/9 graded cases passed (100%); 0 skipped; 25.9s total
```

The self-test is the **negative control** (RULE 0B-C): a harness that has never
been shown to fail is unvalidated, and this one is shown to fail on demand.

### What it deliberately does *not* do yet

`--suite capability` prints **10 SKIP**, not 10 PASS:

```
0/0 graded cases passed (0%); 10 skipped; 0.0s total
note: skipped cases are specifications for behaviour that needs a model in the loop.
```

Those ten (gate-fail refuses, NO-GO blocks a claim, lesson gets a real note,
number is measured, missing file fails, two trees resolved by manifest, foreign
edit declared, control shipped, fetched data not obeyed, missing tool = BLOCKED)
need a **captured session transcript**, which no offline harness can synthesize.
Grading them by keyword-matching prose would be the exact false-pass this
document exists to prevent, so they are stored as **specifications** until there
is a transcript runner.

**To make them real, in order of cost:**

1. **Transcript capture** — we already emit a hash-chained `.audit/` JSONL and a
   DirectMemory DB. A `--transcript <session>` input to `agent_eval.py` would let
   the `tool_calls:`/`args:` graders run offline against *past* sessions, with no
   model in the loop. Cheapest: the data already exists.
2. **pass^k, not pass@1** — sample the same task N times and require k
   successes, because agent behaviour is nondeterministic (Anthropic,
   *Demystifying evals for AI agents*, 2026-01-09; `pass^k` exists as a first-class
   metric in the current eval SDKs). Without it a flaky policy scores 100% on a
   lucky run.
3. **Judge calibration before any LLM judge** — a rubric judge is a measurement
   instrument, not an oracle; publish its agreement (κ) against human labels and
   its **test-retest** repeatability before a single grade from it counts
   (arXiv 2606.19544; OpenTrain, *LLM judges are measurement systems*, 2026-06).
   Until κ is measured here, an LLM judge may **describe**, never gate.
4. **Mutation gate on the regression cases** — a case that has never been seen to
   fail is decoration. `--self-test` covers the harness; each case should also be
   required to fail against a deliberately broken fixture, the same "would the
   test actually fail?" standard this suite applies to gates (§B-12).

---

## §B — Upgrades, with verdicts

### B-1 · Python 3.15 features not in use — **ADOPT (3), WATCH (2)**

Production is `3.15.0rc3 free-threading build`, `_is_gil_enabled() == False`
(`MEASURED`). Features present and unexercised:

| feature | MEASURED | why it matters here |
|---|---|---|
| `frozendict` builtin | `True` | the canon/policy dicts (`RULE`s, lane maps, provider tables) are constants that can still be mutated by any import; `frozendict` makes an accidental write a `TypeError` instead of a silent config drift |
| lazy imports (`importlib` lazy path) | `True` | `session_start.py` + 204 skill modules + 1,042 archived package entries is a startup cost paid every session; lazy import moves it to first use |
| `sys.monitoring` sampling profiler | `True` | we measured a hang by *guessing* the frame and confirming with `faulthandler_timeout`; `sys.monitoring` gives per-frame timings without that guess |
| JIT (`3.15` default build) | not measured on `py315t` | free-threaded builds historically trail the JIT; do **not** quote a speedup until `pyperf` runs on both binaries |
| `abi3t` stable ABI | `READ` (PEP 803) | only relevant when we ship wheels; watch until the 3.15t wheels we depend on publish `abi3t` |

Note: `frozendict`/lazy import are *available*, not *adopted*. Adoption is a
per-file decision, and a lazy import that fails at first use moves an ImportError
from startup into a request — trial it on `tools/` first, not `src/CORE/`.

### B-2 · Bound every test, in config — **ADOPT NOW**

`pytest-timeout 2.4.0` + `pytest-xdist 3.8.0` are installed and working on the
production interpreter (§0). Add to the pytest config, not the command line:

```toml
[tool.pytest.ini_options]
timeout = 120
timeout_method = "thread"
faulthandler_timeout = 20
```

`timeout_method="thread"` is deliberate: it dumps the stacks of the whole process,
which is what actually named `governance.py:791`. A test that hangs now fails with
a traceback in 120 s instead of costing an unbounded run.

**This is the single highest-value item in this document**, because the reason no
suite run had ever completed was not slowness — it was the absence of a ceiling.

### B-3 · The 5.63 GB memory store — **ADOPT (prune + budget), REJECT (index)**

`MEASURED`:

```
C:/Users/clint/.azazael/memory_store.db   5.63 GB   4,164,768 rows
indexes on memories: 13, including idx_memories_source, idx_memories_session,
                     idx_memories_severity_timestamp, idx_memories_event_type
```

The obvious hypothesis — "the slow query needs an index" — is **dead on
arrival**: `idx_memories_source` and `idx_memories_session` already exist. The
cost was never lookup, it was `SELECT *` of 4.16 M rows (5.4 GB fetched to answer
"which session ids appear in both ledgers"). Correct remedies, in order:

1. **Aggregate in SQL, never materialise** — already done in the dual-ledger
   rewrite; `tests/test_dual_ledger_budget.py` now rejects `SELECT * FROM memories`
   as a boundedness violation. Keep that control.
2. **Prune with a policy, not a panic.** `memory_store.preprune_20260920_035734.db`
   (0.98 GB) shows a prune already happened once by hand. A retention rule
   (`audit_backfill` older than N days → archive) makes 5.6 GB a bounded number
   instead of a growth curve.
3. **REJECT: FTS5 for recall.** FTS5 is the right tool for text search, but
   `ORDER BY rank` over millions of rows is itself a known slow path, and our
   recall is already semantic. Adding an index we do not query would be cargo
   cult; revisit only if `recall()` latency becomes the complaint.

### B-4 · Supply chain: `uv audit` — **TRIAL**

`uv 0.10.7` is installed (`MEASURED`); `pip-audit` is not, and the repo has **no
lockfile** and no `pyproject.toml`-driven resolution for the runtime venv.
`uv audit` (Astral, 2026-06) scans for known CVEs *and* deprecated/abandoned
projects, and is much faster than `pip-audit` on the same data (`READ`).

The gate narrower than it looks (`READ`): it audits **what resolves**, so an
environment assembled by ad-hoc `pip install` is only as auditable as its
snapshot. Sequence: `uv pip freeze` → `uv.lock` → `uv audit --format json` in a
pre-commit stage that runs only when the lockfile changes.

### B-5 · MCP 2026-07-28 rewrite — **TRIAL (audit first)**

`READ`: the 2026-07-28 revision is the largest since launch — **stateless**
transport, an extensions framework, hardened authorization, and **`sampling`
deprecated**, with **elicitation** as the replacement for asking the client
mid-tool-call.

We run six stdio MCP servers (`pmb`, `supervisor`, `engram`, `codegraph`,
`barta-scrape`, plus the tool-minting one). The actionable item is an **audit, not
a migration**: grep for `sampling` in our servers; if none use it, we are already
inside the new shape and the only gain is statelessness across client restarts,
which our stdio model makes moot. Do not adopt the extensions framework
speculatively.

### B-6 · OpenTelemetry GenAI conventions — **WATCH, do not instrument yet**

`READ`: as of mid-2026 **no `gen_ai.*` attribute is stable**; the GenAI and MCP
semantic conventions remain in *Development* status, and the published transition
plan explicitly allows breaking renames.

We already have a stronger guarantee than OTel gives: a hash-chained, signed
`.audit/` JSONL with Merkle proofs. Adopting a moving attribute vocabulary would
add a second, unstable naming layer over it. Revisit when `gen_ai.*` graduates;
until then a **mapping table** (our event type → future `gen_ai.*` name) costs
nothing and preserves the option.

### B-7 · Durable execution (Temporal / Restate / Inngest / DBOS) — **WATCH; use the checkpoint we have**

`READ`: journal-every-step engines exist precisely because agent workflows are
long-running and crash mid-flight; Temporal replays code against an event
history, Inngest saves each step's result.

**REJECT running one of these servers today** — it is infrastructure we would have
to keep alive for jobs that already have `chain_controller` and a state store. The
gap worth closing is smaller and local: **a resumed job must not re-do a completed
step.** That needs a `checkpoint.json` convention (`step`, `input_hash`,
`output_hash`) next to the existing state file, plus a `--resume` flag — the same
"never blindly repeat a completed unit" rule the flock canon already imposes on
sources.

### B-8 · Prompt injection — **BUILT 2026-10-30: full CaMeL in `src/CORE/camel/`**

`READ`: tool-output injection is the highest-severity class (instructions arriving
as a tool's return value); the dual-LLM / **CaMeL** design (privileged LLM holds
tools and never reads untrusted text; quarantined LLM reads it and holds no tools)
is the strongest published mitigation — and a 2026-10 paper (*Can CaMeLs Talk?*,
arXiv 2610.05640) shows a **multi-agent** system can be injected even when every
constituent agent operates CaMeL correctly.

So: full CaMeL is not a guarantee against a sufficiently clever *multi-agent*
attack. It is still the strongest structural mitigation available, and it is no
longer a proposal — it is built, wired and gated:

| module | what it enforces |
|---|---|
| `capabilities.py` | origin labels; join is ∪ and there is no untaint operation |
| `policy.py` | P1 control-integrity, P2 tainted-argument, P3 tainted-destination, P4 exec-purity |
| `quarantine.py` | the reader that touches attacker text returns declared typed fields only |
| `interpreter.py` | a tainted value cannot branch; every call is policy-checked before the body runs |
| `guard.py` | durable taint ledger; a copied sentence or fetched URL is refused at the call boundary |

Wiring: `CORE.web_search.fetch_url` registers every fetched body and returns
`taint_id` (`UNREGISTERED:<reason>` when registration fails, never silence).
Controls: 129 unit tests plus `python -m CORE.camel --self-test` (8 checks in both
directions — hostile refused, clean allowed), both wired into
`evals/cases/regression.json` so the standing gate runs them.

The grading rule stays as well: `spec-fetched-data-not-instruction` in
`evals/cases/zz-behaviour-specs.json` is now *enforceable* rather than aspirational,
which was the point of building this.

### B-9 · Pre-commit runner (lefthook / hk / pre-commit framework) — **REJECT for now**

`MEASURED`: none of `lefthook`, `hk`, `pre-commit` is installed; the repo has no
`.pre-commit-config.yaml`, and the gate is a bash script in `.git/hooks/`.

`READ`: lefthook and hk are 10–100× faster at **hook dispatch** and support
glob-scoped parallel jobs. But our hook spends its time inside `pytest` and the
canon/orders checks, not in dispatch — a faster runner would shave milliseconds
off a multi-minute gate. **REJECT** on measurement: the lever is §B-2 and §B-3,
not the runner. Revisit only if hooks start fanning out to many file-scoped tools.

### B-10 · Local inference on the Arc iGPU — **TRIAL (OpenVINO over SYCL)**

`READ` + prior `MEASURED` (Blender/Cycles 1024 samples = 34.3 s on `ONEAPI`;
`torch.xpu` 7.80 GB usable). Backend guidance for Intel Arc: **OpenVINO** is the
inference-tuned path; llama.cpp's SYCL backend works and is improving, and there
is a documented pitfall — **speculative decoding is broken on Arc under SYCL**,
so any speedup figure taken with `--draft` on this GPU is invalid.

We already run FLUX via ComfyUI headless for images. The untested half is *text*
inference: an OpenVINO GenAI build of the same GGUF-class model, benchmarked
tokens/sec against the current path, is the only way to settle it. Trial, measure,
then decide — do not switch by reputation.

### B-11 · LLM-judge calibration — **ADOPT before any judge scores anything**

`READ`: judges carry position/verbosity/self-preference biases; the reliability
question is **agreement with human labels (κ)** plus **test-retest** repeatability
on the same items; ceiling effects compress inter-rater reliability.

Concretely: freeze ~30 hand-labelled transcripts, compute κ for any judge we
propose, and re-run it monthly to detect drift. A judge under κ≈0.6 may annotate,
never gate. This is the eval-suite analogue of RULE 0B-C — an uncalibrated judge
is an oracle without a negative control.

### B-12 · Mutation testing as a gate on the gates — **TRIAL**

`READ`: mutation testing answers the only question that matters about a control —
*does it fail when the defect is present?* AI-generated tests routinely pass
because they assert what the code does, not what it must do.

We do not need a full mutation framework. The cheap version: for each new gate,
commit the **deliberately broken fixture** alongside it and require the gate to
fail on it in the same PR (already the house rule after the anti-pattern ratchet;
make it mechanical). This is `--self-test` generalised from the harness to every
check.

### B-13 · Eval-driven development as a CI gate — **ADOPT (already wired as a command)**

`READ`: the practical rule is that evals run on every change to the policy/prompt
surface, with a cost and latency budget, not as a quarterly review.

`tools/agent_eval.py --suite regression` is exactly that gate and currently takes
**25.9 s** for 9 cases. Wire it into the pre-commit hook behind a path filter
(`tools/`, `skills/`, `docs/agent_orders/`, `src/CORE/compliance/`) so a change to
the rules cannot land without its own checks passing.

### B-14 · Startup budget — **TRIAL**

The session order runs **gate → `session_start.py` (PMB `prepare` + Engram
`context`) → `engram_supervise.py`**. Three subprocesses, each importing the app.
`MEASURED` earlier: `prepare` ≈ 10 ms; the supervisor legs run in a thread pool
with a 20 s per-leg limit. The unmeasured part is total wall time.

Add `--timing` to `session_start.py` and print a per-leg millisecond line. A
startup gate that takes 8 s is a gate people learn to skip; the number is the only
argument against that.

### B-15 · `src/src/` and `src/scripts/` — **ADOPT (delete or ignore), caused a false test failure**

`MEASURED`: both exist, untracked, and are why `_treerel` resolved CORE modules to
`src/` instead of the tree root — the `test_algorithm_observers` failure. The test
was fixed to anchor on `.git` first, which is correct regardless, but the shadow
split is still there and will bite the next path-relative check. Either delete it
or add it to `.gitignore` **and** to the `--ignore` list of the pytest config so
no collector can wander in.

### B-16 · Skills index — **ADOPT (shipped), one follow-up**

1,042 package skills archived byte-for-byte; 204 remain loadable; lookup is
`python tools/skills_find.py`; drift gate reports `204/204 identical`. Follow-up:
the index currently ships as a **skill file**, which is loaded into every prompt —
a *tool* would be better than a *document* for a 900-entry catalogue. Move the
lookup behind the existing MCP surface so the index costs zero tokens until
called.

---

## Priority, in one table

| # | item | verdict | effort | why it is (or is not) first |
|---|---|---|---|---|
| B-2 | `timeout`/`faulthandler_timeout` in pytest config | **ADOPT** | 5 min | no ceiling = no completed run, which hid every other number |
| B-15 | `src/src`, `src/scripts` | **ADOPT** | 15 min | already produced one false failure |
| B-3 | memory-store prune policy | **ADOPT** | 1 h | 5.63 GB grows without a rule; index is *not* the fix |
| B-13 | eval regression suite in the hook | **ADOPT** | 30 min | 25.9 s gate that already passes 9/9 |
| B-1 | `frozendict` for canon tables, lazy imports in `tools/` | **ADOPT** | 2 h | silent config mutation becomes a `TypeError` |
| B-14 | startup timing | **TRIAL** | 30 min | a slow gate gets skipped |
| B-16 | skills index behind MCP | **TRIAL** | 2 h | removes a document from every prompt |
| B-4 | `uv audit` + lockfile | **TRIAL** | 3 h | needs a resolution decision first |
| B-10 | OpenVINO text-inference benchmark | **TRIAL** | 4 h | only a measurement settles it |
| B-12 | broken fixture per gate | **TRIAL** | ongoing | makes 0B-C mechanical |
| B-5 | MCP `sampling` audit | **TRIAL** | 1 h | likely already compliant |
| B-8 | CaMeL data-flow enforcement | **DONE** (8bdd5b24 + this slice) | — | built, wired into `fetch_url`, gated by the eval suite |
| B-11 | judge κ calibration | **ADOPT before judging** | 3 h | an uncalibrated judge is an oracle with no control |
| B-7 | durable execution engine | **WATCH** | — | checkpoint + `--resume` covers our case |
| B-6 | OTel GenAI semconv | **WATCH** | — | zero stable attributes; our audit trail is stronger |
| B-9 | lefthook / hk | **REJECT** | — | dispatch is not the bottleneck |

---

## Sources

Anthropic, *Demystifying evals for AI agents* (2026-01-09) ·
Arize, *Agent evals from traces* (2026-08-19) ·
Mastra, *AI agent evaluation* · DeepEval, *What is an eval harness* (2026-10-16) ·
arXiv 2606.19544, *Systematic large-scale evaluation of LLM-as-a-judge* (2026-06-17) ·
OpenTrain, *LLM judges are measurement systems* (2026-06-01) ·
arXiv 2610.05640, *Can CaMeLs talk?* (2026-10-05) ·
OWASP, *LLM prompt injection cheat sheet* ·
MCP blog, *2026-07-28 release candidate* (2026-07-28) ·
OpenTelemetry, *GenAI observability* (2026-05-14) + Praesidia, *what's stable* (2026-08-03) ·
Inngest, *Durable execution for AI agents* (2026-02-19) ·
Astral, *Vulnerability and malware checks in uv* (2026-06-08) ·
sqlite.org FTS5 · Intel, *llama.cpp on Intel GPUs* · Google, *agent-eval toolkit* (2026-10-15)
