# Disclosure Policy

## Purpose

This policy governs how Project_HYDRA_MLCluster handles sensitive information encountered during
its operation as a ml-core component in the Azazael ecosystem.

## What We Do Not Distribute

Project_HYDRA_MLCluster **does not distribute**:

- Raw primary data from analyzed systems (unless explicitly allowed by license)
- Secrets, API keys, credentials found during operation
- Proprietary algorithms or business logic from analyzed codebases
- Any material about identifiable individuals that is not already public

## What We Do Distribute

- The component **METHOD** (algorithms, patterns, techniques)
- Open-source tooling for ml-core operations
- Documentation and examples using synthetic/public data
- Configuration templates

## Handling Sensitive Data

If the component encounters sensitive data (secrets, keys, PII, proprietary code):

1. **Stop** — do not commit, log, or report the sensitive data
2. **Redact** — remove or hash the sensitive identifiers
3. **Report** — notify the project maintainers via security@azazael.local
4. **Verify** — ensure no sensitive data would be distributed

## Attribution

The Contributor Covenant text in CODE_OF_CONDUCT.md is used under
CC BY 4.0 with attribution retained in that file.

## Contact

For questions about this policy, contact **disclosure@azazael.local**.
