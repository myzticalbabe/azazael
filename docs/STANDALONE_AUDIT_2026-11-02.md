# STANDALONE AUDIT — do the publishable trees actually run without the monorepo?

**Date:** 2026-11-02
**Scope:** `Project_FLAMING_SWORD`, `Project_FLAME`, `Project_SHARDEX`, `Project_CRADLE`, `Project_Nurse_Ratchet`
**Method:** read-only. Every Python file listed below was read and its import block inspected;
`code_search` was used only to confirm a reference already seen in a file. **No project was edited,
no file outside this document was written, nothing was built or run.**

## The claim being tested

The owner has decreed that these trees **do not need the CORE package** and are to publish as
independent projects — each usable alone, and together as one. This audit looks for where that
claim is **false**.

A `COUPLED` verdict below does not mean the project is bad. It means **that project does not
publish until the coupling is removed**, because a fresh clone has no sibling directory to resolve
against and no `CORE` package on `sys.path`.

## Verdict summary

| Project | Verdict | Offending references | `pyproject.toml` |
|---|---|---:|---|
| `Project_CRADLE` | **COUPLED** | 6 | **none** |
| `Project_Nurse_Ratchet` | **COUPLED** (1 line, silent) | 1 import | present, `dependencies = []` |
| `Project_SHARDEX` | **COUPLED** (documented workflow) | 9 | **none** |
| `Project_FLAMING_SWORD` | **STANDALONE** (example config not portable) | 3 | **none** |
| `Project_FLAME` | **STANDALONE** | 2 (documentation only) | **none** |

**4 of the 5 have no `pyproject.toml`.** Their dependencies are therefore undeclared — harmless
today only because they happen to import nothing outside the standard library.

---

## 1. Project_CRADLE — COUPLED (worst offender)

CRADLE is a launcher. Its four parts are **not in its own tree** — they are files in
`Project_FLAMING_SWORD/tools/`.

| File:line | The reference | Why it breaks standalone |
|---|---|---|
| `cradle.py:73` | `SWORD_TOOLS = REPO / "Project_FLAMING_SWORD" / "tools"` | resolves a sibling directory that a fresh clone does not have |
| `cradle.py` `PARTS` dict (~76-82) | requires `defender.py`, `sentinel.py`, `memory_bridge.py`, `chain_server.py` **from the sibling project** | `--doctor` cannot pass; every command fails |
| `cradle.py:201` | `target = "Project_FLAMING_SWORD/tools/sword.py"` | the demo's subject lives outside the tree |
| `cradle.py:206, 208` | `evidence=` / `must_not_break=` name `Project_FLAMING_SWORD/tests/test_defender.py` | acceptance command points at another repo's tests |
| `cradle.py:250, 252` | same, second demo path | same |
| `NOTICE:22-25` | *"CRADLE.md and NOT redistributed here: Project_FLAMING_SWORD … licensed separately (Apache-2.0)"* | honest — but it confirms the dependency is by design |

CRADLE's own imports are clean (stdlib only: `argparse`, `importlib.util`, `json`, `shutil`, `sys`,
`tempfile`, `urllib`, `pathlib`, `typing`). It therefore **imports** fine in a fresh clone and
**fails on first use** — the worse of the two failure modes, because the failure appears after
installation.

**What publishing it requires:** either (a) vendor the four FLAMING_SWORD modules into
`Project_CRADLE/`, which turns CRADLE into a fork and duplicates a project that ships separately,
or (b) publish CRADLE as a *companion* repo whose README states in the first line that it requires
`Project_FLAMING_SWORD` checked out as a sibling. (b) is the honest option and matches the NOTICE;
it just may not be published as a standalone tool.

---

## 2. Project_Nurse_Ratchet — COUPLED by exactly one silent line

| File:line | The reference | Why it breaks standalone |
|---|---|---|
| `nurse_ratchet/psyche/traits.py:44` | `from CORE.failure_ledger import note_failure` (inside `try/except ImportError`) | in a fresh clone the import raises, the `except` swallows it, and `note_failure` becomes a **no-op** |

This one is subtle and worth stating precisely. It will **not** crash. It will quietly reduce a
failure ledger to silence — and silence-as-a-result is the exact defect this estate's own documents
treat as its most expensive recurring bug. The fallback even admits it in a comment:
*"ledger missing; evidence-vs-silence tradeoff capped here"*.

It also contradicts the package's own declaration: `pyproject.toml` says
`dependencies = []` and explains that the package is deliberately stdlib-only. A stdlib-only
package must not import `CORE`.

| Other finding | File:line | Note |
|---|---|---|
| Stale name after the bad rename | `nurse_ratchet/__init__.py:1` | docstring still reads `"ELIZA -- see docs/index.md"` |
| Host-home default (portable, but named) | `tools/psyche_fit_pams.py:58, 70` | `Path.home()/".pams"`, `Path.home()/".psyche"` — `$HOME`-relative, not machine-absolute; acceptable, overridable |
| Host-home default | `tools/elicit.py:66` | `Path.home()/".psyche"/"elicitations.jsonl"` — same |

**Verdict: COUPLED, fixable in one line.** Replace the `CORE.failure_ledger` import with a local
no-op or a local `_swallowed` list, and this project is standalone. It is the closest of the five to
publishable: it already has `LICENSE`, `NOTICE`, `CITATION.cff`, `PUBLIC_MANIFEST.json`, a
release gate, and a `publicize.py` that materialises the tree from the manifest.

---

## 3. Project_SHARDEX — source is clean, the documented workflow is not

Python imports are **all standard library**, and the internal sibling imports
(`import ops`, `from transubstantiate import ...`) are resolved by `sys.path` inside the project —
correct for a standalone tree.

The coupling is in the pipeline the README and docstrings instruct a user to run:

| File:line | The reference | Why it breaks standalone |
|---|---|---|
| `meshscene.py:28` | `NODE_PATH=C:/Users/clint/node_modules node tools/sample_image.js` | absolute **username** path, and `tools/sample_image.js` is in the *repo's* `tools/`, not in `Project_SHARDEX` |
| `meshscene.py:31` | `node tools/capture_transubstantiation.js` | same missing harness |
| `meshscene.py:561` | help text: *"the field.json from tools/sample_image.js"* | points at a file the published tree does not contain |
| `shardex.py:36` | parser help references `tools/capture_transubstantiation.js` | same |
| `SHARDEX.md:145, 185-187` | same two JS files, same absolute `C:/Users/clint` path | the public README would instruct a user to run a path that does not exist on their machine |
| `transubstantiate.py:41` | `--extract docs/YGGDRASIL_CLEAVE.html` | fixture lives in the repo's `docs/` |
| `SHARDEX.md:63, 82` | `docs/METTHEW/reference-shards/…`, `docs/METTHEW/shard.schema.json` | fixtures in `docs/METTHEW`, outside the tree |

So: `shardex.py --mirror/--shatter/--forge/--verify/--selftest` works from a fresh clone. The
**image→mesh→live-mutation** layer (L2/L3) cannot be reproduced, because its two JavaScript harnesses
and its sample fixtures are not in the published tree.

**Verdict: COUPLED as documented.** Either ship the two `.js` harnesses and a fixture image inside
`Project_SHARDEX/`, or mark that layer "requires the monorepo" in the README instead of instructing a
user to invoke a path under someone's home directory.

---

## 4. Project_FLAMING_SWORD — STANDALONE (one bad example config)

All seven modules in `tools/` are stdlib-only, and siblings are loaded by absolute file path through
`importlib.util` (`sword.py` `_sibling()`), which is the correct pattern for a run-from-anywhere tool.

| File:line | The reference | Assessment |
|---|---|---|
| `config.example.json:5` | `"command": ["C:/Azazael/.venvs/py315t/Scripts/python.exe", "tools/platform_claims.py", "--check"]` | **absolute path with a username**, and `tools/platform_claims.py` is a **repo-level** tool not present in this project — an example config that cannot work after publish |
| `tests/test_sword.py:226` | absolute interpreter inside a fixture string | test fixture only; does not affect runtime |
| `README.md:211` | `--root C:/Azazael/azazael --scan` | a *measurement* recorded on the author's box, not an instruction; acceptable |

**Verdict: STANDALONE.** The code runs anywhere with Python and `git`. Fix
`config.example.json` (use `"python"` and a command that exists in this tree) before publishing, or
the first thing a user copies is broken.

---

## 5. Project_FLAME — STANDALONE (clean)

`tools/flame_engine.py` imports only `argparse`, `hashlib`, `json`, `sys`, `fractions`, `typing`.
The `Machine` protocol is a seam, not an import: FLAME does not reference FLAMING SWORD in code.

| File:line | The reference | Assessment |
|---|---|---|
| `README.md:39` | `C:/Azazael/.venvs/py315t/Scripts/python.exe` | records the interpreter a measurement was verified on — documentation, not an instruction |
| `README.md:4, 90` | mentions `Project_FLAMING_SWORD` and adopting `tools/` into `Project_FLAME/tools/` | prose describing the split, no runtime dependency |

**Verdict: STANDALONE — the cleanest of the five.** The only defect is the missing
`pyproject.toml`; with stdlib-only imports, adding one is a five-line file.

---

## 6. What this audit did not do

- No project was edited. This document is the only file written.
- Nothing was imported, executed, tested or built. The verdicts rest on reading import blocks and
  the references above — a runtime check from a real fresh clone is still owed, and would confirm or
  refute each verdict in seconds.
- Graph/document generation was out of scope; only the two JavaScript harnesses named in the SHARDEX
  pipeline were traced, not every asset either project writes.
- `Project_Nurse_Ratchet/tools/` was sampled (`publicize.py`, `psyche_fit_pams.py`, `elicit.py`);
  the remaining four tools were not read line by line, so a second `from CORE` import there is not
  excluded — though the scoped search returned none.
