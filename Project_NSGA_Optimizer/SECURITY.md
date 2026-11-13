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

Project_NSGA_Optimizer is a ml-core component with the following security properties:

1. **Minimal dependencies** — stdlib-only where possible
2. **No network access** — unless explicitly required for the component's function
3. **No arbitrary code execution** — does not eval or execute untrusted code
4. **Input validation** — all external inputs validated at boundaries

## Disclosure Policy

We follow coordinated disclosure. Once a vulnerability is confirmed and a
fix is available, we will:

1. Release a patch
2. Publish a security advisory
3. Credit the reporter (unless they request anonymity)

## Scope

This policy covers the component's source code and any bundled dependencies.
