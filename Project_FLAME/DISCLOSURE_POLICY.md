# Disclosure Policy

## Purpose

This policy governs how Project FLAME handles sensitive information that
may be encountered during game engine development, testing, or simulation.

## What We Do Not Distribute

Project FLAME **does not distribute**:

- User game data, save files, or personal information
- Proprietary game assets or code from developers using FLAME
- Any material about identifiable individuals that is not already public

## What We Do Distribute

- The engine **METHOD** (fixed-step orchestrator, integer timebase)
- Open-source engine code and orchestration logic
- Documentation and examples using synthetic/public data
- Configuration templates

## Handling Sensitive Data in Testing

If engine testing encounters sensitive data:

1. **Stop** — do not commit or log the sensitive data
2. **Redact** — remove or hash the sensitive identifiers
3. **Report** — notify the project maintainers via security@azazael.local
4. **Verify** — ensure no sensitive data would be distributed

## Attribution

The Contributor Covenant text in CODE_OF_CONDUCT.md is used under
CC BY 4.0 with attribution retained in that file.

## Contact

For questions about this policy, contact **disclosure@azazael.local**.