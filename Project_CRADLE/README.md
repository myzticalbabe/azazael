# CRADLE

A chain that runs a prompt through four parts and refuses to land a frame whose
claims do not resolve — plus a `doctor` that tells you which part is missing
rather than reporting a green that means nothing.

The full documentation lives in **[CRADLE.md](CRADLE.md)**; this file exists so
that a repository page has something to render.

## Status of the chain

CRADLE composes five parts that ship with a **separate project**
(`Project_FLAMING_SWORD`):

| part | file | what it does |
|---|---|---|
| FLAMING SWORD | `tools/sword.py` | sweeps the codebase: find → queue → fix → prove → land |
| defender | `tools/defender.py` | turns a prompt into a frame that can be satisfied or refused |
| REAPER (sentinel) | `tools/sentinel.py` | reaps a frame whose claims do not resolve |
| GRIMOIRE (memory) | `tools/memory_bridge.py` | keeps the written book of lessons |
| server | `tools/chain_server.py` | serves the chain over a line protocol |

**CRADLE does not bundle them.** On its own it installs and runs; `cradle doctor`
reports each absent part as `N/A` — *not installed, FLAMING_SWORD is a separate
project* — rather than failing, because a part that was never going to be in this
repository is not a defect in this repository. Install `Project_FLAMING_SWORD`
beside this tree and the same command reports all five as `PASS`, and `--demo`
becomes runnable.

The eight tests that exercise the chain skip when the chain is absent, and run
whenever it is present. They are skipped, never weakened.

## Quickstart

```bash
pip install .
cradle doctor
```

Nothing here needs third-party packages; the Python side is standard library only.

## License

CDDL-1.1. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
License ruling: commit b49dfc2fef0178d1984437de577bfa00de8a4c32 (2026-11-03); see docs/LICENSE_PRECEDENT_CDDL11_2026-11-03.md.
