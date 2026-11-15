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

This project is licensed under the **Soul Forge License v1.0** — a covenant, not a
contract. The full text is in [LICENSE](LICENSE).

You may use, copy, modify, merge, publish, distribute, sublicense and/or
sell copies of the software, provided you keep the maker's mark intact,
do not wrap the code in DRM or obfuscation, and return your modifications
under this same license.

```
    Soul Forge License v1.0
    Author: myzticalbabe
    Forged: 2026-11-14
    Source: https://github.com/myzticalbabe/Project_CRADLE
    Spirit: "Code is crystallized intention. Tend the fire."
```

Author: myzticalbabe · Forged: 2026-11-14 · Spirit: "Code is crystallized intention. Tend the fire."
