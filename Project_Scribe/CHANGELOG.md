# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- **One licence in the tree: the Soul Forge License v1.0.** Every other licence
  reference in this project was removed on 2026-11-15. Third-party material keeps its
  own terms and is named in `NOTICE`.
- **This changelog has no history before 2026-11-15, and that loss is recorded rather
  than hidden.** The file that stood here belonged to another project, so it was not
  this component's history to keep. Nothing real was discarded.

### Fixed

- Replaced metadata copied wholesale from `Project_Nurse_Ratchet`, including a
  manifest declaring `"project": "nurse-ratchet"` and an allowlist rooted at
  `../src/PSYCHE` — a path that resolves from this tree. All four files now describe
  this tree, and `evidence/` and `profiles/` are named in `never_ship` because they
  quote third parties and named funders.
  
  Fixed `profiles/cradle_proposal.md`, which cited a licence document that no longer
  exists.

### Added

- `certification.json` written for this component, with every `done` criterion citing
  a path that exists in this tree.
- `HARDWARE.md` stating this component's actual toolchain dependencies instead of a
  clinical deployment's.
- `MANIFEST_NOTES.md` stating plainly that `PUBLIC_MANIFEST.json` is not yet an
  allowlist.
