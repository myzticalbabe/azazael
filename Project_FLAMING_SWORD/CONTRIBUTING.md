# Contributing to Project FLAMING SWORD

Thank you for considering a contribution to Project FLAMING SWORD!

## Quick Start

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-change`
3. Make your changes
4. Run the test suite: `python -m pytest tests/ -v`
5. Submit a pull request

## Code Standards

- **License**: All contributions must be compatible with CDDL-1.1 (the project license)
- **Python**: 3.10+ (stdlib-only, no runtime dependencies)
- **Dependencies**: Only stdlib and `git` executable
- **Style**: Follow the existing code style in the repository
- **Tests**: New functionality must include tests
- **Documentation**: Update relevant docs (README.md) with your changes

## What We Accept

- Bug fixes in the sweep tools (sword, defender, sentinel, memory_bridge, chain, housekeep)
- New static analysis rules or fix patterns
- Performance improvements
- Documentation improvements
- Test coverage improvements

## What We Don't Accept

- Changes that add runtime dependencies (FLAMING SWORD is stdlib-only by design)
- Changes that require network access
- Changes that break the `git` dependency assumption

## The Six Tools

Contributions should be aware of the six tools and their roles:

- **sword** — Main sweep orchestrator
- **defender** — Defense/protection analysis
- **sentinel** — THE REAPER (monitoring)
- **memory_bridge** — THE GRIMOIRE (memory integration)
- **chain_server** — Chain/orchestration
- **housekeep** — Maintenance/housekeeping
- **disposition** — Ledger (internal, not a command)

## Pull Request Process

1. Ensure all tests pass
2. The maintainers will review and merge

## Reporting Issues

Use the GitHub issue tracker. Please include:
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, git version)

## Code of Conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

## Security

See [SECURITY.md](SECURITY.md) for reporting security vulnerabilities.

## License

By contributing, you agree that your contributions will be licensed under CDDL-1.1.