# AI PANEL OPINIONS — SHARDEX license & ownership dispute (2026-11-03)

Every valid opinion below carries explicit per-holding reasoning; all API keys are
redacted in the raw layer, and no result was hand-fabricated. This record complements
the house ruling already committed in `docs/SHARDEX_UNIQUENESS_2026-11-03.md` (implied
measurements unchanged). Judge numbering follows the runner's bench order: only those
seats whose provider actually answered rule on the record — the four unreachable seats
cite their blockers honestly and produce no fabricated verdicts.

**This is an opinion record only — AI panel opinions are not legally binding.**

## Bench reached (7/11)

| # | judge | model (measured) | seconds | H1 | H2 | H3 | H4 | H5 | dissent |
|---|---|---|---|---|---|---|---|---|---|
| 1 | groq | openai/gpt-oss-120b (chat-capable, reaches #1 of the bench) | 2.8 | AFFIRM | **REVERSE** | AFFIRM | AFFIRM | AFFIRM | H2 |
| 3 | openrouter | meta-llama/llama-3.3-70b-instruct | 1.1 | AFFIRM | AFFIRM | AFFIRM | AFFIRM | AFFIRM | none |
| 5 | gemini | gemini-3.5-flash | 81.2 | AFFIRM | AFFIRM | AFFIRM | AFFIRM | AFFIRM | H2 |
| 6 | mistral | mistral-small-2603 | 7.8 | AFFIRM | AFFIRM | AFFIRM | AFFIRM | AFFIRM | H2 |
| 7 | cohere | command-r-plus-08-2024 | 50.9 | AFFIRM | AFFIRM | AFFIRM | AFFIRM | AFFIRM | none |
| 10 | pollinations | gpt-oss-20b (alias `openai`; openai-large unavailable, no Classic API entry) | 20.8 | AFFIRM | **REVERSE** | AFFIRM | AFFIRM | AFFIRM | H2 |
| 11 | groq | qwen/qwen3.8-27b (distinct weights from judge 1; same provider) | 1.1 | AFFIRM | AFFIRM | AFFIRM | AFFIRM | AFFIRM | H2 |

The two H2-REVERSE judges (J1 gpt-oss-120b, J10 gpt-oss-20b) both reasoned to the same
conclusion: an uncontrolled advisory sweep cannot *prove* the negative that no public
equivalent exists. The five H2-AFFIRM judges affirm H2 on its stated, dated, advisory
basis (the holding itself carries the caveat), while J5/J6/J11 also name H2 as the
holding they most doubt. Net: H2 carries 5 AFFIRM, 2 REVERSE, and 5 judges naming it
as their chief doubt — the case's one contested holding.

## Unreached judges (4 of the 11)

| # | provider | blocker (measured, in-session) |
|---|---|---|
| 2 | cerebras | HTTP 402 `payment_required_error` — account quota/credits exhausted |
| 4 | nim | chat path dead for this account: legacy EOL 410 for all named llama builds (e.g. `meta/llama-3.3-70b-instruct` EOL 2026-08-26) and 404 `Function '<uuid>': Not found for account` for provisioned alternates (`nvidia/nemotron-3-super-120b-a12b`, `moonshotai/kimi-k2.6`); `deepseek-ai/deepseek-v4.1-flash` timed out |
| 8 | huggingface | HTTP 402 — inference providers require pre-paid credits / PRO |
| 9 | github models | every call returned HTTP 200 with non-JSON body `OK\r\n` — endpoint or PAT path unusable from this host; no retry chain fixed it |

## Panels (only sizes reachable from a 7-seat reachable bench)

Panel-N is the first N reachable judges in bench order: panel-3 = {J1,J3,J5};
panel-5 = {J1,J3,J5,J6,J7}; panel-7 = {J1,J3,J5,J6,J7,J10,J11}. **9- and 11-judge
panels could not be convened** — only 7 of the 11 judges were reachable (above), so
those seats cite their blockers rather than fabricate opinions.

| Panel | H1 | H2 | H3 | H4 | H5 | named dissent |
|---|---|---|---|---|---|---|
| 3 | AFFIRM 3-0 | AFFIRM 2-1 | AFFIRM 3-0 | AFFIRM 3-0 | AFFIRM 3-0 | 2 (J1, J5) |
| 5 | AFFIRM 5-0 | AFFIRM 4-1 | AFFIRM 5-0 | AFFIRM 5-0 | AFFIRM 5-0 | 3 (J1, J5, J6) |
| 7 | AFFIRM 7-0 | AFFIRM 5-2 | AFFIRM 7-0 | AFFIRM 7-0 | AFFIRM 7-0 | 5 (J1, J5, J6, J10, J11) |

**Consensus pattern across panel sizes.** H1 authorship, H3 portability, H4 license
chain and H5 golden-witness are unanimous (7-0) in every panel — growth of the panel
did not create movement there. The single contested holding is **H2 uniqueness**, and
all five dissents name it with the same ground: the evidence is advisory only (no
decoy-controlled sweep) — the same limitation the house panel recorded as Q2. Panel
growth moves the H2 majority 2-1 → 4-1 → 5-2 and raises named-dissent count 2 → 3 → 5
(all H2), while H2-AFFIRM remains the modal decision at every size.

## Provenance / reproducibility

- Brief (identical for all 11 judges): `C:/Users/clint/panel_opinion_brief.txt`
- Runner (temp, outside repo): `C:/Users/clint/panel_opinion_runner.py` — per-provider
  `/chat/completions` calls, temperature 0.2, candidates chain-of-retry by model, 429
  two-strike sleep-retry. Pollinations judge distanced: pollinations/openai is alias of
  `gpt-oss-20b` per /_models list (11 seats were built as 11 openai / openai-fast, one-seat sized).
- Raw layer (redacted, all `<REDACTED>` on secrets): `C:/Users/clint/Documents/ai_panel_opinions_raw.json`
- Prior measures already in the record (not re-measured here): `docs/SHARDEX_UNIQUENESS_2026-11-03.md`
- Session command: `python panel_opinion_runner.py --full` → 7 valid / 4 unreachable (blocked reasons preserved verbatim in raw layer).

## Why H2 stays qualified

The sweep behind H2 has no decoy/query-baseline control, so the alternative it cannot
exclude is: an equivalent exists that the searches simply did not locate by name (or in
different terms). Every judge's reasoning converged on this exact boundary; none treated
H2 as independently settled. Until SHX-R1 or a decoy-controlled sweep lands, H2 should
be read as **AFFIRM-as-record (advisory)** — affirmed on the record strand itself, not
as an independently reproducible fact. The unreached 4 judges came from different
release paths (one payment-walled, one account-unprovisioned, one proxy-broken); nothing
in their absence implies a direction of verdict either way.
