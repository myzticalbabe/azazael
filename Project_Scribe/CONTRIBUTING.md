# Contributing to Project Scribe

Thank you for considering a contribution to Project Scribe!

## Quick Start

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-change`
3. Make your changes
4. Run tests: `python -m pytest tests/ -v`
5. Submit a pull request

## Code Standards

- **License**: All contributions must be compatible with CDDL-1.1 (the project license)
- **Python**: 3.10+ (requires scrapling, curl_cffi)
- **Style**: Follow existing code style
- **Tests**: New functionality must include tests
- **Documentation**: Update relevant docs

## What We Accept

- New grant program definitions (add to PROGRAMS registry)
- Improved bypass techniques (Cloudflare, reCAPTCHA, hCaptcha, etc.)
- Better form field detection/mapping
- Evidence collection improvements
- Profile schema enhancements

## Grant Program Definition

To add a new grant program, add a `GrantProgram` entry to the `PROGRAMS` dict in `scribe.py`:

```python
"program_key": GrantProgram(
    key="program_key",
    name="Program Name",
    url="https://example.com/apply",
    description="What this program funds",
    fields={
        "profile_field": "css_selector_or_xpath",
    },
    required_docs=["doc1", "doc2"],
    bypass_config={"cloudflare": True, "recaptcha": "v2"},
    submit_selector="button[type='submit']",
    success_indicators=["submitted", "confirmation"],
),
```

## Pull Request Process

1. Ensure all tests pass
2. The maintainers will review and merge

## Reporting Issues

Use the GitHub issue tracker. Please include:
- Steps to reproduce
- Expected vs actual behavior
- Program key, profile (sanitized), evidence screenshots

## Security

See [SECURITY.md](SECURITY.md) for reporting security vulnerabilities.

## License

By contributing, you agree that your contributions will be licensed under CDDL-1.1.