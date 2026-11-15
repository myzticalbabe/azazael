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

- **Fixed** `tools/PERSEPHONE/requirements_wsl.txt`: ten lines of Python source
  (`wsl_to_windows`, `windows_to_wsl`) were filed inside the requirement list, which
  made `pip install -r` fail to parse the file outright. They are commented out; the
  behaviour they described belongs in the library, not in a requirements file.
  
  **Known, not fixed**: the same file still fails to resolve. `socketio>=0.8.0` is not
  a PyPI distribution name — the package is `python-socketio` — and several other pins
  (`argparse`, `pathlib2`, `jsoncomment`, `pyvbox`, `rsync`) were never verified.
  Renaming them means deciding what was meant, which is not a one-line fix. The file
  also declares roughly 150 dependencies this component does not use, because it was
  written as an environment manifest for the whole tree.
  
  Replaced metadata copied wholesale from `Project_Nurse_Ratchet`, including a
  manifest declaring `"project": "nurse-ratchet"` and an allowlist rooted at
  `../src/PSYCHE` — a path that resolves from this tree.

### Added

- `certification.json` written for this component, with every `done` criterion citing
  a path that exists in this tree.
- `HARDWARE.md` stating this component's actual toolchain dependencies instead of a
  clinical deployment's.
- `MANIFEST_NOTES.md` stating plainly that `PUBLIC_MANIFEST.json` is not yet an
  allowlist.
