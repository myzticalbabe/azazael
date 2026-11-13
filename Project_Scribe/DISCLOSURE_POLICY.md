# Disclosure Policy

## Purpose

This policy governs how Project Scribe handles sensitive information
encountered during grant application form filling, including project
details, contact information, and submission receipts.

## What We Do Not Distribute

Project Scribe **does not distribute**:

- Agent project profiles (profiles/*.json) — these contain proprietary project details
- Contact information (emails, names) from profiles
- Grant program credentials or authentication tokens
- Session cookies (stored locally, encrypted at rest)
- Submission receipts and confirmation codes
- Evidence screenshots and HTML captures (stored locally in evidence/)

## What We Do Distribute

- The **METHOD** (form detection, field mapping, bypass techniques)
- Grant program definitions (publicly available application URLs and requirements)
- Open-source tooling for form automation and browser bypass
- Template profiles (with placeholder data only)

## Data Handling During Application

1. **Profile Loading** — Profiles loaded from local JSON, never transmitted except to target form
2. **Form Filling** — Data sent only to the grant program's application endpoint
3. **Session Persistence** — Cookies stored locally in `sessions/` with timestamps
4. **Evidence Collection** — Screenshots and HTML saved to `evidence/` with timestamps
5. **Cleanup** — Sessions can be purged with `--clean-sessions` flag (not yet implemented)

## Evidence Retention

Evidence in `evidence/` serves as an audit trail:

- **Screenshots** — Full-page PNGs at each stage (navigation, fill, submit, result)
- **HTML Captures** — Complete page source for forensic analysis
- **Network Logs** — Request/response metadata (when enabled)
- **Retention** — Default 90 days; configurable per program

## Handling Sensitive Data in Profiles

If a profile contains unexpectedly sensitive data:

1. **Stop** — Do not submit the application
2. **Redact** — Remove sensitive fields from the profile file
3. **Report** — Notify maintainers via security@azazael.local
4. **Rotate** — Clear sessions and evidence for that profile

## Grant Program Terms Compliance

Scribe users are responsible for:

- Reading and complying with each grant program's terms of service
- Not using Scribe for programs that prohibit automated submission
- Respecting rate limits and submission windows
- Providing accurate information in applications

## Attribution

The Contributor Covenant text in CODE_OF_CONDUCT.md is used under
CC BY 4.0 with attribution retained in that file.

## Contact

For questions about this policy, contact **disclosure@azazael.local**.