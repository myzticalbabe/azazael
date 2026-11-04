# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

**Do not report security vulnerabilities via public GitHub issues.**

Instead, please report them via email to **security@azazael.local**.

Include the following information:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Any known workarounds

We will acknowledge receipt within 48 hours and provide a status update
within 5 business days.

## Security Model

JAEGER is the BCC Re-Investigation forensic layer with the following security properties:

1. **No runtime dependencies** — stdlib-only
2. **No network access** — JAEGER does not make network requests
3. **Disclosure gate** — Allowlist-based release gate (`PUBLIC_MANIFEST.json`) prevents unauthorized distribution
4. **Evidence provenance** — All claims tied to source documents with SHA-256 verification

## Disclosure Policy

We follow coordinated disclosure. Once a vulnerability is confirmed and a
fix is available, we will:

1. Release a patch
2. Publish a security advisory
3. Credit the reporter (unless they request anonymity)

## Scope

This policy covers the JAEGER forensic investigation machinery, including
the disclosure gate, entity resolution, claim-to-source citation, and
evidence provenance tracking.