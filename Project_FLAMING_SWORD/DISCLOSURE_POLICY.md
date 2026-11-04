# Disclosure Policy

## Purpose

This policy governs how Project FLAMING SWORD handles sensitive information
that may be encountered during code quality sweeps, static analysis, or
automated repair of codebases.

## What We Do Not Distribute

Project FLAMING SWORD **does not distribute**:

- Raw source code from analyzed projects (unless explicitly allowed by the project's license)
- Secrets, API keys, credentials found during sweeps
- Proprietary algorithms or business logic from analyzed codebases
- Any material about identifiable individuals that is not already public

## Allowlist Gate

FLAMING SWORD uses an allowlist gate via `PUBLIC_MANIFEST.json` (inherited
from the Azazael tree). Nothing ships that the manifest does not name.
The release gate fails the build when a path crosses the line the manifest declares.

## What We Do Distribute

- The sweep **METHOD** (tools, algorithms, fix patterns)
- Open-source tooling for code quality, static analysis, automated repair
- Documentation and examples using synthetic/public code
- Configuration templates

## Handling Sensitive Data in Sweeps

If a sweep encounters sensitive data (secrets, keys, PII, proprietary code):

1. **Stop** — do not commit, log, or report the sensitive data
2. **Redact** — remove or hash the sensitive identifiers in any output
3. **Report** — notify the project maintainers via security@azazael.local
4. **Verify** — ensure the allowlist gate would have blocked distribution

## Attribution

The Contributor Covenant text in CODE_OF_CONDUCT.md is used under
CC BY 4.0 with attribution retained in that file.

## Contact

For questions about this policy, contact **disclosure@azazael.local**.