# Manifest notes

`PUBLIC_MANIFEST.json` is meant to be an allowlist: nothing ships that it does not
name. In this tree it is **not yet an allowlist**, and the manifest says so in
`allowlist_status` rather than pretending otherwise.

## The state of this tree

This tree publishes in place. `tools/CODEX` is both the source and the artifact, and it carries 500+ files including rendered reports and captured artifacts, which is exactly the shape a per-file allowlist exists to make you think about. None is written yet, so `ship` is empty and the tree as a whole is the artifact.

## Why an allowlist instead of a deny-list

A deny-list fails open. A directory added after the list was written ships by
default, the push succeeds, the artifact is public, and nobody looks again. An
allowlist fails closed, and the failure is a red gate before anything leaves the
machine.

## What is deliberately excluded

`never_ship` is enforceable today, because it names globs that nothing needs to
maintain: requiem's grave records, `node_modules`, `__pycache__`, and `.env` files.

## Correcting the record

Until 2026-11-15 this file, `certification.json`, `HARDWARE.md` and `CHANGELOG.md`
were verbatim copies of `Project_Nurse_Ratchet`'s. The copied manifest declared
`"project": "nurse-ratchet"` and an allowlist rooted at `../src/PSYCHE`, which
resolves from this tree. A publicize run would have copied the clinical package into
this component.
