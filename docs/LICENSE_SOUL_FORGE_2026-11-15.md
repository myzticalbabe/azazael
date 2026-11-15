# License — Soul Forge License v1.0 (adopted 2026-11-15)

> **License status (2026-11-15): current.** This is the operative ruling, not a
> historical record. Every tree in this repository is licensed under the Soul Forge
> License v1.0 (`LICENSE`). Where this document describes an earlier license it is
> describing what it replaced, not what applies.

**Ruling:** every tree in this repository — the repository root and all 37
`Project_*` directories — is licensed under the **Soul Forge License v1.0**.
The full, unmodified text is the `LICENSE` file in every tree; all 38 copies are
byte-identical.

```text
Soul Forge License v1.0
Author: myzticalbabe
Forged: 2026-11-14
Source: https://github.com/myzticalbabe/<repository>
Spirit: "Code is crystallized intention. Tend the fire."
```

This supersedes every earlier license decision in this tree, including commit
`b49dfc2fef0178d1984437de577bfa00de8a4c32` (2026-11-03), which unified four Projects
under CDDL-1.1, and the Apache-2.0 state that preceded it — a state the root did not
even declare, so GitHub reported `license: null`. Those commits remain in history;
they no longer describe the license of any file here.

## Why one license

Three Vows, and what each one costs the project:

| Vow | Obligation | Effect here |
|---|---|---|
| I — Attribution of Spirit | keep the maker's mark in every copy, derivative and deployment | `LICENSE` and `NOTICE` carry it in all 38 trees |
| II — No Cage for the Flame | no DRM, obfuscation or mechanism that blocks reading, modifying or running | shipped code stays inspectable, including the compiled/WASM surfaces |
| III — Reciprocity of Forge | modifications distributed are offered back under this same license; no closing, no patenting | forks stay open |

## What is *not* relicensed

Third-party material keeps its own license. Relicensing someone else's work
would be a false statement, so these stay as they are and are named in `NOTICE`:

- `CODE_OF_CONDUCT.md` — adapted from Contributor Covenant v2.1, used under
  CC BY 4.0, attribution retained in the file. Third-party text only.
- Dependency lock files (`package-lock.json`) and vendored build material
  (`nuitka_build_backup/`, `.agents/skills/`) — each entry keeps its upstream
  license. Not first-party code.
- `docs/LICENSE_COMPLIANCE_REPORT.md` — an inventory of dependency licenses.
  It lists what dependencies require; it does not license this project.

## Enforcement

`tools/soul_license_audit.py` is the audit and the migration:

```bash
python tools/soul_license_audit.py --audit   # report every defect, exit 1 if any
python tools/soul_license_audit.py --apply   # rewrite them
```

It fails when any of the 38 trees has a `LICENSE` that is not byte-identical to
the canonical text, or when `CITATION.cff`, `CONTRIBUTING.md`, `pyproject.toml`,
`PUBLIC_MANIFEST.json`, `NOTICE` or `README.md` names a different license.
`tests/test_soul_license_only.py` pins the same invariants in CI.
