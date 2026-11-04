# Disclosure Policy

## Purpose

This policy governs how Project CRADLE handles sensitive information that
may be encountered during code quality sweeps, static analysis, or
orchestration of Project_FLAMING_SWORD tools.

## What We Do Not Distribute

Project CRADLE and its orchestrated tools **do not distribute**:

- Raw primary documents (case files, medical records, legal filings)
- Entity-resolution output (identified persons, organizations, addresses)
- Rendered findings (investigation reports, analysis artifacts)
- Correspondence naming identified organizations and people
- Any material about identifiable individuals that is not already public

## Allowlist Gate

CRADLE inherits the allowlist gate from Project_FLAMING_SWORD via
`PUBLIC_MANIFEST.json`. Nothing ships that the manifest does not name.
The release gate (`tools/eliza_release_gate.py` equivalent) fails the
build when a path crosses the line the manifest declares.

## What We Do Distribute

- The investigation **METHOD** (code, algorithms, orchestration logic)
- Open-source tooling for code quality, static analysis, composition
- Documentation and examples using synthetic/public data
- Configuration templates

## Handling Sensitive Data in Analysis

If a sweep or analysis encounters sensitive data:

1. **Stop** — do not commit or log the sensitive data
2. **Redact** — remove or hash the sensitive identifiers
3. **Report** — notify the project maintainers via security@azazael.local
4. **Verify** — ensure the allowlist gate would have blocked distribution

## Attribution

The Contributor Covenant text in CODE_OF_CONDUCT.md is used under
CC BY 4.0 with attribution retained in that file.

## Contact

For questions about this policy, contact **disclosure@azazael.local**.