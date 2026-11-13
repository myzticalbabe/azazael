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

Scribe is an agent-driven form-filler with the following security properties:

1. **No credential storage** — Profiles contain no secrets; only public project info
2. **Session isolation** — Each application run uses a fresh browser context
3. **Cookie persistence** — Session cookies stored locally, encrypted at rest
4. **No network credentials** — Does not store grant program credentials
5. **Evidence integrity** — Screenshots and HTML saved with timestamps for audit

## Bypass Stack Security

Scribe uses the same bypass stack as BCC re-investigation:

- **scrapling** — Browser automation with built-in challenge handling
- **curl_cffi headers** — Realistic TLS/HTTP fingerprints
- **No credentialed bypass** — Does not use stolen cookies or credentials
- **Rate limiting** — Respects program rate limits (configurable per program)

## Disclosure Policy

We follow coordinated disclosure. Once a vulnerability is confirmed and a
fix is available, we will:

1. Release a patch
2. Publish a security advisory
3. Credit the reporter (unless they request anonymity)

## Scope

This policy covers `scribe.py`, `bypass.py`, `forms.py`, and the `profiles/`
directory. The scrapling dependency has its own security policy.