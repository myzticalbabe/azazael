# Security Policy

## Supported Versions

Project CRADLE is a composition tool that orchestrates Project_FLAMING_SWORD.
Security issues in the underlying parts should be reported to
Project_FLAMING_SWORD directly.

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

CRADLE itself has no runtime dependencies (stdlib-only). Its security
surface consists of:

1. **Sibling orchestration** — CRADLE invokes Project_FLAMING_SWORD tools via
   subprocess. Vulnerabilities in those tools are the responsibility of
   Project_FLAMING_SWORD.

2. **File system access** — CRADLE reads configuration files and writes
   output. It does not execute arbitrary code from untrusted sources.

3. **No network access** — CRADLE does not make network requests.

## Disclosure Policy

We follow coordinated disclosure. Once a vulnerability is confirmed and a
fix is available, we will:

1. Release a patch
2. Publish a security advisory
3. Credit the reporter (unless they request anonymity)

## Scope

This policy covers the `cradle.py` entry point and the `tools/` directory
within Project_CRADLE. The four parts it orchestrates (sword, defender,
sentinel, memory_bridge) have their own security policies in
Project_FLAMING_SWORD.