# ASSUMPTIONS.md — Falsifiable Assumptions Ledger

**Purpose:** Every assumption that drives a decision, gate, or claim is recorded here with a falsifier. An assumption without a falsifier is not an assumption — it's a belief.

## Format

| ID | Assumption | Domain | Falsifier | Status | Owner | Date |
|----|------------|--------|-----------|--------|-------|------|
| A-001 | Python 3.16t free-threaded is production-ready | runtime | Any segfault in production workload not reproducible on 3.15t | ACTIVE | infra | 2026-11-15 |
| A-002 | cffi/pillow/scipy/sklearn will have 3.16t wheels within 6 months | packaging | No wheel published on PyPI for 3.16t by 2027-05-15 | ACTIVE | packaging | 2026-11-15 |
| A-003 | Canvas 2D forest renderer is sufficient for <3000 nodes | visualization | Frame rate drops below 30fps at 3000 nodes on target hardware | ACTIVE | viz | 2026-11-15 |
| A-004 | GitHub Pages deployment latency < 5 minutes | deployment | Pages deployment takes > 5 minutes for 3 consecutive pushes | ACTIVE | infra | 2026-11-15 |
| A-005 | CodeQL finds actionable security issues in public repos | security | 30 days with zero CodeQL alerts across 25 repos | ACTIVE | security | 2026-11-15 |
| A-006 | arc-container advisory INCOMPLETE is acceptable for release | release | Any blocking gate depends on eliza/provenance READY | ACTIVE | release | 2026-11-15 |
| A-007 | Professional standards verification catches all compliance gaps | compliance | A repo passes verification but fails manual audit | ACTIVE | compliance | 2026-11-15 |
| A-008 | Negative controls validate the verifier | testing | Negative control passes when it should fail | ACTIVE | testing | 2026-11-15 |
| A-009 | FETCH_LOG row exists before CUT grade | evidence | CUT grade assigned without FETCH_LOG entry | ACTIVE | evidence | 2026-11-15 |
| A-010 | Atlas auto-sync completes within 10 minutes | sync | Atlas sync workflow runs > 10 minutes | ACTIVE | sync | 2026-11-15 |

## Adding New Assumptions

1. Assign next sequential ID (A-XXX)
2. State the assumption precisely
3. Name the domain (runtime, packaging, viz, deployment, security, release, compliance, testing, evidence, sync)
4. Provide a **concrete falsifier** — an observable condition that would prove the assumption wrong
5. Set status: ACTIVE / SUPERSEDED / FALSIFIED
6. Assign owner and date

## Review Cadence

- **Weekly:** Check falsifiers for ACTIVE assumptions
- **Monthly:** Review SUPERSEDED assumptions for cleanup
- **On falsification:** Record as FALSIFIED, document impact, create follow-up task

## Falsification Log

| ID | Falsified Date | Evidence | Impact | Follow-up |
|----|----------------|----------|--------|-----------|
| — | — | — | — | — |