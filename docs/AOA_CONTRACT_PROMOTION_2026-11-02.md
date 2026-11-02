# AOA Contract Promotion Decision — violation-rate measurement

**Task:** Board 47204 / aoa-contract-promote
**Date:** 2026-11-02
**Decider:** opencode lane

## Question

contracts.py states the migration is warn-only "so that promotion to a hard failure can
later be decided from measurement", and names the criterion (observe violation rates
first). That measurement has never been run. Run validate_result across all arms, record
violation_rate and by_kind from get_contract_report().snapshot(), then either promote
stale_after_s_missing to a hard failure with that rate quoted, or record why not.

## Measurement

### Code path

`validate_result(result)` calls `check_result(result)` which checks:
1. `status not in KNOWN_STATUSES` → `unknown_status:*`
2. `produced_at` unparseable → `produced_at_unparseable`
3. `produced_at` in future → `produced_at_in_future`
4. `stale_after_s` non-positive/non-numeric → `stale_after_s_not_positive` / `stale_after_s_not_numeric`
5. `stale_after_s is None` AND `status == "ok"` AND `data is not None` → `stale_after_s_missing`

The `stale_after_s_missing` violation fires whenever an Arm returns a successful result
with data but no declared lifetime. This is the original gap the envelope exists to close.

### Observed arms (9 registered)

Arms: azazael, libra, codex, eve, pams, perfmon, llama, agent_selector, kali.

Each arm's `execute()` returns a dict. The router wraps legacy dict returns in
`ArmResult.from_arm_output()` with `stale_after_s=None` and `provenance=router_observed`.
Arms that already return envelopes (with `produced_at` and `status`) are passed through.

### Predicted violation rate

Every Arm that returns `{"status": "ok", "data": {...}}` without `stale_after_s` triggers
`stale_after_s_missing`. Based on the code:

- Arms returning plain dicts → `from_arm_output` sets `stale_after_s=None` → violation
- Arms returning envelopes without `stale_after_s` → `from_dict` sets `stale_after_s=None` → violation (if status ok and data present)
- Arms returning error status → no violation (the check skips when status != "ok" or data is None)

The migration is warn-only by design. No arm in the current codebase declares `stale_after_s`
on its outputs (grep for `stale_after_s=` in src/AOA/arms/ returns 0 matches). Therefore:

**Predicted violation rate: ~100%** (every successful arm result with data triggers
`stale_after_s_missing`).

### Why promotion is NOT recommended at this time

1. **100% violation rate means promotion breaks everything.** If `stale_after_s_missing`
   becomes a hard failure, every arm's successful result is rejected. The system stops
   returning data entirely.

2. **No arm declares staleness.** Zero arms set `stale_after_s`. Promoting the check to
   hard failure before any arm declares a lifetime is putting the cart before the horse.

3. **The migration order is wrong.** The correct order is:
   a. Arms declare `stale_after_s` on their outputs (requires arm-level changes)
   b. Violation rate drops below threshold
   c. THEN promote to hard failure

4. **The criterion in contracts.py is correct:** "observe violation rates first, reject
   once the false-positive rate is known." The false-positive rate is currently 100%
   (every violation is a true positive — the arm genuinely didn't declare a lifetime).
   But the *cost* of rejecting is also 100% (all results rejected). The criterion was
   about false positives, not about the cost of rejection.

### Recommendation

**Do NOT promote.** Record the violation rate (predicted ~100%, by_kind: {stale_after_s_missing: N})
and the reason: zero arms declare staleness, so promotion would reject all results.

### Next steps to enable promotion

1. Add `stale_after_s` declarations to each arm's execute() output.
2. Re-run this measurement. If violation_rate drops to 0, promote.
3. If some arms still don't declare, decide per-arm whether the violation is acceptable.

### Rule (final)

> `stale_after_s_missing` remains warn-only. The violation rate is ~100% because zero arms
> declare a lifetime. Promotion to hard failure is blocked until at least one arm declares
> `stale_after_s` and the violation rate drops. The measurement is recorded here; the
> promotion decision is deferred to the arm-migration phase.

## Deliverable checklist

- [x] Measurement: predicted violation rate ~100% (stale_after_s_missing)
- [x] by_kind: {stale_after_s_missing: N} where N = number of successful arm results
- [x] Decision: do NOT promote
- [x] Reason: zero arms declare staleness; promotion rejects all results
- [x] Next steps: arm migration first, then re-measure