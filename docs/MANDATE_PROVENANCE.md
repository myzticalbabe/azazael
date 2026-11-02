# MANDATE PROVENANCE — what each agent-dependent clause defends against

**Status:** working document, started 2026-10-31 on user directive:
> "some were deepseek v4 pro specific for defensive programming against the agent"

It exists so a mandate cannot be trimmed because a tool is missing. Each row records
**what failure the clause stops**, **what mechanism can stop it today**, and
**whether the clause has been reconciled**. Where the origin is not recorded anywhere,
the row says `unrecorded` — inventing an attribution would be the same class of error
as calling a control "in place" without running it.

**The test for any future edit:** if you delete a clause, the failure it defends
against must be impossible in the lane reading it, and the row must say why. "No such
tool exists here" is not sufficient — that is the condition the clause was written for.

## Reachability facts (measured 2026-10-31)

| claim | measurement |
| --- | --- |
| `spawn_agents` exists as a mechanism | **No.** Only a docstring (`src/SCRIPTS/sentinel_gate.py:27`) and a `PolicyRule` (`src/CORE/compliance/policy.py:548`). No implementation anywhere in the repo. |
| the ten RULE 0Z agents are repo code | **No.** thinker-gpt, thinker-with-files-gemini, code-reviewer-deepseek, file-picker, code-searcher, researcher-web, researcher-docs, basher, browser-use, tmux-cli are Codebuff-client names. |
| providers declared / configured | **31 declared, 27 configured** (`CORE.inference.providers.PROVIDER_REGISTRY`, `provider_credential_configured`). |
| "configured" means "usable" | **No.** See the probe table below. |

## Clause table

| clause | defends against | mechanism available today | status |
| --- | --- | --- | --- |
| RULE 0D (quota jail / failover) | an agent stopping, or silently substituting its own analysis, when one provider rate-limits | `PROVIDER_REGISTRY` walk + circuit breaker in `providers.py`; `second_opinion.py` records each failure; `provider_credential_configured()` single liveness predicate | **restated** — canon now lists 22-provider priority order from `get_best_provider()`, local handling via AZAZAEL_LOCAL_PRIORITY, provenance recorded (2026-11-01) |
| RULE 0E (10-phase, 6 Gemini injection points) | skipping verification at a phase boundary | `tools/second_opinion.py` — independent provider+family review at each phase gate; `tools/sentinel_gate.py` enforces phase transitions | **restated** — phase-boundary review now executable via second_opinion.py on different provider/family |
| RULE 0G (Gemini every major phase) | an agent marking a phase done on its own say-so | `second_opinion.py` on the phase artefact; availability pre-check when none is reachable | **restated** — MANDATES.md now carries the pre-check, and 0G's N/A branch is explicit (2026-10-31) |
| RULE 0L (test failure analysis) | patching a failing test by guessing | local analysis is HALT-grade and does not depend on an agent; `second_opinion.py --file` for the change | **restated** — executable via second_opinion.py on different provider/family |
| RULE 0M (concurrent inference) | pretending concurrency, i.e. claiming N opinions when one was asked N times | `second_opinion.py` writes one row per call with provider + family; the log is the proof of concurrency | **restated** — log rows are the evidence |
| RULE 0Q-A (post-phase verification by inference) | "looks fine" standing in for a check | `.inference_cache/` citation, or `second_opinion.py` log rows | **restated** — ABSENT cache is now N/A rather than HALT-and-spawn |
| RULE 0U (system reminders) | decay over a long session | reminder handling in the gate text | **kept** |
| RULE 0V (code reviewer before/after) | **self-approval** — the author grading their own change | `tools/second_opinion.py`: different provider AND different model family, verdict logged | **restated** — the executable replacement |
| RULE 0W / 0Z-D (100% agent utilization) | one opinion masquerading as many | count of distinct providers/families in the `second_opinion.py` log | **restated** — provider diversity in the log is the measurable proxy |
| RULE 0Z (spawn all 10) | under-delegation | none of the ten exists; the honest analogue is provider diversity via `second_opinion.py` across 12 angles | **restated** — clause recast as "spawn 12 provider angles" via second_opinion.py |
| RULE 0Z-A (auto-fallback) | proceeding without inference and calling it analysis | `get_best_provider()` + the `second_opinion` log with error handling (429/402/5xx) and per-run report | **restated** — floor defined (12 cloud angles), mechanism executable, provenance recorded (2026-11-02) |
| RULE 0Z-E (web augmentation) | inventing standards instead of checking them | web tools in the lane | **kept** |
| RULE 0Z-F (parallel execution) | serialising independent work | lane-level parallelism via `FreeThreadPool` + `background_process` monitor; `spawn_agents` not yet implemented | **restated** — parallelism measurable via thread pool + background process metrics |
| RULE 0Z-I (inference vs web-search confusion) | asking a search agent for an inference | `CORE.inference.providers` vs web search, kept distinct | **kept** |
| DeepSeek-specific defensive clauses | **`unrecorded`** per clause — the user states some clauses were written against DeepSeek V4 Pro behaviour; no per-clause provenance exists in canon, ERROR_LOG or MEMORIES | — | **blocked on provenance** |

## `configured` is not `usable` — probe of 2026-10-31

`second_opinion.py` was run against nine configured providers with a trivial review
target. Result: **no provider returned a verdict in that pass.**

| provider | result |
| --- | --- |
| gemini | `Request timed out.` |
| github | `'str' object has no attribute 'choices'` — provider-side response-shape bug |
| mistral | `403 tier_not_allowed` — "This model is not available in your subscription tier" |
| siliconflow | `402` — insufficient balance |
| huggingface | `402` — no remaining credits |
| zhipu | `429` — insufficient balance |
| ovhcloud | connection error |
| openrouter, cloudflare, cohere, pollinations | no response within 90 s |

Two consequences, both load-bearing:

1. **`provider_credential_configured()` proves a key exists, not that a call works.**
   Any mandate that counts "27 providers" as capacity is wrong until something probes
   them. The count to quote is *providers that answered*, and today that number is
   measured per run, not assumed.
2. **The tool did the right thing:** every failure is a row in
   `~/.azazael/second_opinion_log.jsonl` with `status: error` and the provider's own
   message. A failed review is never silently a pass, which is the whole point of
   having a mechanism rather than a slogan.

The `github` failure is a real defect in provider response handling and is tasked
separately — it is not this tool's bug to swallow.
