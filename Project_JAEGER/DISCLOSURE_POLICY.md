# Disclosure Policy

## Purpose

This policy governs how Project JAEGER handles sensitive information
that is the subject of the BCC Re-Investigation. JAEGER is the forensic
layer that keeps investigation claims tied to documents and decides
what may leave the machine.

## What We Do Not Distribute

Project JAEGER **does not distribute**:

- Raw primary documents (case files, medical records, legal filings)
- Entity-resolution output (identified persons, organizations, addresses)
- Rendered findings (investigation reports, analysis artifacts)
- Correspondence naming identified organizations and people
- Any material about identifiable individuals that is not already public

## Allowlist Gate

JAEGER enforces an allowlist gate via `PUBLIC_MANIFEST.json`. Nothing
ships that the manifest does not name. The release gate fails the build
when a path crosses the line the manifest declares. Its `never_ship`
and `deny_substrings` sections name the material that stays home — raw
primary documents, entity-resolution output, rendered findings, and
correspondence naming identified organisations and people.

## What We Do Distribute

- The investigation **METHOD** (code, algorithms, provenance tracking)
- Open-source tooling for evidence provenance, entity resolution, claim citation
- Documentation and examples using synthetic/public data
- Configuration templates

## Handling Sensitive Data in Investigation

If the investigation encounters sensitive data:

1. **Stop** — do not commit or log the sensitive data
2. **Redact** — remove or hash the sensitive identifiers
3. **Report** — notify the project maintainers via security@azazael.local
4. **Verify** — ensure the allowlist gate would have blocked distribution

## Relationship to Other Projects

JAEGER is the forensic investigation suite. It is NOT the therapeutic
agent in this tree — that is a SEPARATE project, Project Nurse Ratchet,
with its own package, its own release gate and its own citations. The
two are not variants of one another and must not be described as one project.

## Attribution

The Contributor Covenant text in CODE_OF_CONDUCT.md is used under
CC BY 4.0 with attribution retained in that file.

## Contact

For questions about this policy, contact **disclosure@azazael.local**.