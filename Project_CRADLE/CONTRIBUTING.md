# Contributing to Project CRADLE

Thank you for considering a contribution to Project CRADLE!

## Quick Start

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-change`
3. Make your changes
4. Run the test suite: `python -m pytest tests/ -v`
5. Submit a pull request

## Code Standards

- **License**: All contributions must be compatible with CDDL-1.1 (the project license)
- **Python**: 3.10+ (stdlib-only, no runtime dependencies)
- **Style**: Follow the existing code style in the repository
- **Tests**: New functionality must include tests
- **Documentation**: Update relevant docs (CRADLE.md, README.md) with your changes

## What We Accept

- Bug fixes
- Documentation improvements
- New orchestration features that compose existing parts
- Integration with new FLAMING_SWORD tools
- Performance improvements

## What We Don't Accept

- Changes that add runtime dependencies (CRADLE is stdlib-only by design)
- Changes to the sibling project Project_FLAMING_SWORD (contribute there directly)
- Features that make CRADLE a "fifth part" rather than a composition

## Pull Request Process

1. Ensure all tests pass
2. Update CHANGELOG.md with your changes
3. The maintainers will review and merge

## Reporting Issues

Use the GitHub issue tracker. Please include:
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version)

## Code of Conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

## Security

See [SECURITY.md](SECURITY.md) for reporting security vulnerabilities.

## License

By contributing, you agree that your contributions will be licensed under CDDL-1.1.