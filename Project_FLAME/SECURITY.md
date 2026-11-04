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

FLAME is a fixed-step game engine orchestrator with the following security properties:

1. **No runtime dependencies** — stdlib-only, no third-party packages
2. **No network access** — FLAME does not make network requests
3. **Deterministic execution** — Fixed-step integer timebase prevents timing attacks
4. **No arbitrary code execution** — FLAME does not eval or execute untrusted code

## Disclosure Policy

We follow coordinated disclosure. Once a vulnerability is confirmed and a
fix is available, we will:

1. Release a patch
2. Publish a security advisory
3. Credit the reporter (unless they request anonymity)

## Scope

This policy covers the `tools/flame_engine.py` entry point and the `tools/`
directory within Project_FLAME.