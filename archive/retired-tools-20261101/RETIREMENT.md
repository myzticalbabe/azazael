# Retired tools — 2026-11-01

Two scripts were retired from `tools/` on 2026-11-01. They are copied here,
byte-identical to the last committed version, so the decision is reversible
without git archaeology. Canon's archive-restore pattern applies: copy, never
move; the retired copies carry their hashes so a restore can be verified.

## `cain_render_gate.py` (131 lines, 5,966 bytes)

```
sha256 8d18b7e39fb1c2ff652359b7dd6bdb4c67ddb1335c2ef3d6894dd557957cf13d
```

A PRE-RENDER gate: nothing rendered until it passed. Written for one document,
`dashboard/CAIN_20260930.html`, and pinned to that session (`SPAN_H = 10.74`,
the first user message to the last on 2026-09-30).

**Why it was retired.** It cannot judge anything any more. Measured on
2026-11-01, under the production interpreter:

```
$ python tools/cain_render_gate.py --check
FileNotFoundError: [Errno 2] No such file or directory:
  'C:\Azazael\azazael\dashboard\CAIN_20260930.html'
exit 1 (100 ms)
```

Its target document is gone, and its span constant belongs to one session, so a
second document could never pass it either. A gate whose subject does not exist
is not a gate; leaving it in `tools/` meant every inventory reported a gate that
nothing ran and nothing could run.

**What replaces it.** Nothing, deliberately. The defect it encoded — "the
document was rendered twice while known-incomplete" — is now covered where the
document actually lives: the render entrypoint and the session templates. The
gate's own constants are the lesson worth keeping, not the file: a check that
encodes the state of the document at the moment it was written starts failing on
correct content later. `cain_fix_checks.py` (below) is the same defect one step
further along.

## `cain_fix_checks.py` (83 lines, 3,782 bytes)

```
sha256 2a7ad340084733ac5dee9db638139f70c35bbf908d59779876401e2d323de45b
```

Retired in the same change because it exists only to REWRITE the gate: it opened
`cain_render_gate.py` for writing and patched two of its checks. With the gate
gone its first action is a `FileNotFoundError`, so keeping it would have
converted one dead script into two.

## Provenance of the decision

- 2026-11-01 — `tests/test_preflight_gate_wiring.py` reported
  `cain_render_gate.py` among gates that no hook runs and no allowlist names.
- Same day — the allowlist entry was re-adjudicated: its `AZ` constant had been
  repointed at this repo, so the recorded reason ("judges a different tree") was
  false. Kind became `unregistered`, with the crash above as the reason.
- Same day — the user directed the retirement. This archive is the record, and
  `test_retired_tools_stay_retired` keeps the file from reappearing without a new
  adjudication.

## Restoring one of these

Copy it back and re-run the wiring control. Do not restore it to satisfy an
inventory: the reason it was retired is in this file, and a restore that does not
answer that reason recreates a gate nobody runs.
