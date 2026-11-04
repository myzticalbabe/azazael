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

FLAMING SWORD is a code quality sweep tool with the following security properties:

1. **No runtime dependencies** — stdlib-only, only requires `git` executable
2. **No network access** — FLAMING SWORD does not make network requests
3. **No arbitrary code execution** — Does not eval or execute untrusted code
4. **File system access** — Reads code for analysis, writes reports; does not execute analyzed code

## Disclosure Policy

We follow coordinated disclosure. Once a vulnerability is confirmed and a
fix is available, we will:

1. Release a patch
2. Publish a security advisory
3. Credit the reporter (unless they request anonymity)

## Scope

This policy covers the `tools/` directory within Project_FLAMING_SWORD,
including all six tools (sword, defender, sentinel, memory_bridge, chain_server, housekeep)
and the disposition ledger.