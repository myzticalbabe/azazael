# Ordering / host-dependent quarantine — measured 2026-10-15 (#721 item 2 & 3)

Task: #712 Phase 3-B (quarantine the 9 ordering-dependent reds with same-invocation
exoneration proof each) + 3-E (docker-benchmark host enumeration).

**Method**: every entry is proven green by running THE SAME pytest command in
isolation (the #704 S15 rule — a same-invocation exoneration, never "re-run alone
and hope"). Exit status captured explicitly, not piped away.

| # | Test(s) | Class | Full-suite behaviour (#704) | Isolation command | Result | exit |
|---|---|---|---|---|---|---|
| 1 | `tests/test_memorybus.py` + `tests/test_memorybus_persistent.py` | B | 4 reds leg1 / 2 leg2 | `pytest tests/test_memorybus.py tests/test_memorybus_persistent.py` | **34 passed** | 0 |
| 2 | `tests/test_inference.py::test_sklearn_inference` | B | leg2-only red | `pytest tests/test_inference.py::test_sklearn_inference` | **1 passed** | 0 |
| 3 | `tests/test_reasoning_overhead_pad.py` (test_chat_pads_the_default...) | B | leg2-only red | `pytest tests/test_reasoning_overhead_pad.py` | **9 passed** | 0 |
| 4 | `tests/test_cutting_edge_production_fixes.py::test_b_a_zero_update_step_returns_no_delta_and_a_current_loss` | B | leg2-only red | same, both interpreters | **1 passed (3.14 and py315t)** | 0 |
| 5 | `tests/test_cross_domain_integration.py::test_cd5_docker_benchmark` | E | host-tuned red (tuned 100410 vs default 269186 tps; assert wants >=0.5x) | same, alone | **1 passed** | 0 |

Distinct ordering-dependent reds covered: 4 modules/tests (entries 1-4 = the 9 red
instances). Entry 5 is the E class.

## Findings that differ from #704

- **E is NOT a standing red.** `test_cd5_docker_benchmark` now **passes**. The
  tuned-vs-default WAL ratio cleared the `>=0.5x` bar on this run, so the red is
  **host/run variance**, not a broken test. Disposition: keep it out of any
  "expected red" list; treat a failure as flaky-host and re-probe, do not "fix"
  the threshold (that would be weakening an assertion to match one host).
- **B entry 4 is green on BOTH interpreters** when isolated, so its py315t-only
  red in the full suite is confirmed ordering/shared-state, not interpreter-specific.

## Quarantine discipline (never a silent skip)

- Nothing is deleted, `xfail`ed, or `skip`ped. These are recorded as an
  ordering-sensitive set with per-entry exoneration proof; the full suite may show
  them red because it shares state (DBs, audit ledgers, `state/*.json`).
- **Re-probe condition**: if an entry fails under its isolation command above on a
  clean checkout, it stops being a quarantine entry and becomes a real defect.

## Not covered

- Entry 4's sibling Class-A reds in the same file are NOT quarantine entries —
  they are the `use_cutting_edge` feature gap (#721 item 1).
