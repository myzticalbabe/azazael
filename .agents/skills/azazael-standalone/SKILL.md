---
name: azazael-standalone
description: AZAZAEL Standalone Suite — PLANNED, NOT BUILT. Zero .exe files exist; the Nuitka build fails on a transformers plugin bug. Read this before assuming any executable is available.
---

# AZAZAEL Standalone Suite Skill

## STATUS: NOT BUILT — read this before using anything here

**Verified 2026-09-29.** `Desktop/AZAZAEL_Standalone/` contains **zero
`.exe` files**. An earlier version of this skill claimed 39 of them. That
claim was never true of the current tree and has been removed rather than
softened, because a skill that says a capability exists is worse than one
that says it does not: the reader stops looking.

**Also absent:** `build_all.py` (referenced by the old skill as the build
entry point) is not in the directory. Neither are the 39 `.bat` launchers.

### Why the build fails

`nuitka-crash-report.xml` and `build_eve_2026-08-27.log` in that directory
record the same fatal error:

```
File "...nuitka/plugins/standard/TransformersPlugin.py", line 196,
  in _getImportStructureDefinition
  return self.queryRuntimeInformationSingle(...)
AttributeError: 'NoneType' object has no attribute 'key'
FATAL: transformers: Plugin issue while working on 'module transformers'.
```

This is upstream in Nuitka 4.1.2's `TransformersPlugin`, triggered by the
`transformers` import in `EveUnleashed_Selector/eve_unleashed_app.py`. It
is not a defect in this repository and the 3.14t patches do not address it.
Until Nuitka fixes it, the options are to pin a different Nuitka version, or
to exclude `transformers` from the compiled import graph.

### What IS in the directory

Documentation, skills, lesson files, a `docs/` tree, an empty
`eve_unleashed_app.dist/`, and the two build-failure artefacts above. The
`.dist` directory is empty because the compilation never completed.

## Do not

- Do not report the Standalone Suite as available or tested.
- Do not reference `.exe` paths from it; none resolve.
- If a task needs a self-contained binary, say the build is blocked and
  name the upstream error, rather than substituting a Python path without
  saying so.

## Intended design (not yet realised)

The plan was 39 modules across six tiers — core apps, CODEX utilities,
analysis/toolkit, video scripts, POPUPS GUI, and worm diagnostics — each
built `--standalone --onefile` with a patched Nuitka 4.1.2 on CPython
3.14.5t. None of it is built. Treat the tier list as a design note, not an
inventory.
