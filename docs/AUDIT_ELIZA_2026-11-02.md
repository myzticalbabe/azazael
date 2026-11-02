# AUDIT — Project_ELIZA (restored from 3fd0b463)

**Date:** 2026-11-02 · **Auditor:** worker 6 of 18 · **Mode:** READ-ONLY, no file in `Project_ELIZA/` was modified.

**Target:** `C:/Azazael/azazael/Project_ELIZA`, restored this session by
`git checkout 3fd0b463 -- Project_ELIZA` after commit `f8c80428` renamed it into
`Project_Nurse_Ratchet`.

---

## VERDICT ON THE CENTRAL QUESTION

**The restored tree is a MIXTURE, and the code is the THERAPEUTIC stack, not the forensic suite.**

Precisely:

| Layer | What the restored tree contains |
|---|---|
| **Code (100% of it)** | The PSYCHE therapeutic agent: trait/affect model, construct network with partial correlations, compiled-inference "intuition", JITAI realtime loop. Modules named `eliza/psyche/traits.py`, `affect.py`, `network.py`, `intuition.py`, `rt_agent.py`, `rt_channel.py`. |
| **Tests (100% of them)** | 9 files, `tests/test_psyche_*.py` ×8 plus `tests/test_triage_eval.py`. All therapeutic. |
| **Governance (forensic)** | `DISCLOSURE_POLICY.md`, `PUBLIC_MANIFEST.json` (`never_ship`, `deny_substrings`), `tools/eliza_release_gate.py`, and the README's Ethics section. This is genuine forensic-investigation machinery. |

The tree's own words, both self-descriptions:

- `README.md` line 1–3: `# Project ELIZA` / "**A therapeutic agent** that is honest about what it cannot do, plus the instruments that prove it."
- `CITATION.cff` (title field, 3rd line): "**Project ELIZA: a therapeutic agent loop** with auditable psychological modelling".

And its provenance, which is what makes your framing correct in one sense:

- `DISCLOSURE_POLICY.md`, section "The line": "This project **grew out of a forensic investigation** into how a care provider treated the people it served. The *techniques* that investigation produced — flock-based edge accounting, tier-graded evidence, negative universes, partial correlation networks over constructs, evaluation splits — are general … The *records* are the private lives of identifiable people".

**So there are two true statements, and they are not the same statement:**

1. ELIZA is the project **born of** the forensic investigation, and it carries the investigation's *publishing discipline* (allowlist, never-ship classes, disclosure gate) as working code.
2. ELIZA's **operational subject** is a therapeutic agent loop. There is no forensic investigation code in this tree — no flock accounting, no tier-graded evidence, no `edge_idx`, no `FETCH_LOG` consumer, no BCC anything. Those live in `C:/Azazael/azazael-forensics` (own `.git`, `goal_liveness`/`marker_audit`/`count_derivation`/`board_stale`) and in the investigation scripts at `C:/Users/clint/`.

Do **not** read this as "the restore was wrong". The restore recovered a real, complete, publish-ready project. It did not recover a *forensic tool*, and the two must not be described interchangeably in the manifest.

---

## 1. File inventory

13 files, 4 directories. No `eliza/` package (see §3 — this is the headline defect).

| Path | Kind | What it does |
|---|---|---|
| `README.md` | governance | States what it is, four layers, limitations, ethics, status. Leads with the router recall spread rather than a single figure. |
| `CITATION.cff` | governance | CFF 1.2.0, Apache-2.0, v0.1.0, released 2026-11-01, 4 references. No `repository-code`/`url` — deliberate, commented as "a citation file that points at a URL nobody has reserved is worse than one that says it will be added." |
| `LICENSE` | governance | Apache License 2.0, full text. |
| `NOTICE` | governance | Names Project ELIZA + Apache-2.0; attributes the *name* to Weizenbaum 1966 with "No code from that program is included here"; states the corpus is invented utterances. |
| `PUBLIC_MANIFEST.json` | governance/machine | The allowlist: `ship_roots: ["Project_ELIZA"]`, ~45 `ship` entries, 14 `never_ship` globs, 6 `deny_substrings`. |
| `MANIFEST_NOTES.md` | docs | Why allowlist-not-denylist; why files are copied not moved; why imports are rewritten. |
| `DISCLOSURE_POLICY.md` | governance | The line: "The method ships. The case does not." Six never-publish classes with reasons. |
| `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` | governance | Community files; CONTRIBUTING carries the negative-control rule. |
| `CHANGELOG.md` | docs | Keep-a-Changelog; `Unreleased` records the crisis-detector replacement and the 0.00→0.83→0.18 holdout history. |
| `pyproject.toml` | packaging | `name = "eliza"`, `dependencies = []`, `requires-python >=3.10`, console script `eliza-psyche`. |
| `.gitignore` | packaging | **`/eliza/` is ignored — see §3.** |
| `.github/` | governance | `workflows/ci.yml`, `PULL_REQUEST_TEMPLATE.md`, 3 issue templates. |
| `docs/` | docs | `index.md` (Diátaxis, honestly lists the empty tutorial quadrant), `reference/psyche.md`, `explanation/why-eliza.md`, `tutorial.md`. |
| `tools/` | instruments | 5 files, below. |
| `tests/` | tests | 9 files, `test_psyche_*` + `test_triage_eval.py`. |

## 2. The five instruments (`tools/`)

| Tool | Size class | What it does, from its own header |
|---|---|---|
| `publicize.py` | 296 lines | Materialises the public tree **from `PUBLIC_MANIFEST.json`** (not directory walking), rewrites `PSYCHE` → `eliza.psyche` across `("code","instrument","test")` kinds only, then **verifies by importing the public package in a fresh subprocess with only the public tree on `sys.path`**. `--check` verifies, `--clean` removes. |
| `eliza_release_gate.py` | 279 lines | Fails publication on: missing community file, issue-template frontmatter keys, manifest path absent, declared path matching a `never_ship` rule, **undeclared file above the size floor**, **secret-shaped string anywhere in the tree**, and loss of the README `Limitations` section. |
| `triage_eval.py` | — | The crisis-router numbers (dev/holdout/holdout2/holdout3). |
| `psyche_fit_pams.py` | — | Probes a real memory store; **exits 2** when it finds no construct readings rather than fitting a graph to the wrong data. Current answer is exit 2. |
| `fit_affect_bridge.py` | — | Ridge fit of the affect→construct bridge; judges coefficient recovery against each coefficient's own standard error, not a hand-picked tolerance. |

`eliza_release_gate.py` resolves its root in two layouts — quoted from the file: `PROJECT = ROOT / "Project_ELIZA" if (ROOT / "Project_ELIZA").is_dir() else ROOT` — so one copy stays honest in both the monorepo and the materialised public tree. That is the right pattern and it survives extraction.

## 3. Dependency state — two separate answers

**(a) Does it need `CORE`? — NO.** No `from CORE`, no `import CORE`, no `src.` imports anywhere in the tree's own files. Every tool imports stdlib only (`argparse`, `fnmatch`, `json`, `os`, `re`, `subprocess`, `sys`, `pathlib`, `typing`). `pyproject.toml` declares `dependencies = []`. Your "they don't need the core" decree is **satisfied here**.

**(b) Is it standalone? — NOT AS RESTORED. It cannot run.** This is the finding that matters:

- `.gitignore` line 5 is `/eliza/`, commented: "`eliza/psyche/` is GENERATED by tools/publicize.py from PUBLIC_MANIFEST.json."
- The restored tree therefore contains **no `eliza/` package at all** — confirmed by directory listing: 13 files, dirs `.github`, `docs`, `tests`, `tools`.
- Every test imports `eliza.psyche.*`, so **all 9 test files fail at import** in the restored state. The README's first Quickstart command (`python -m pytest tests/ -q`) cannot pass.
- `PUBLIC_MANIFEST.json` sources the package from outside the tree: `"from": "../src/PSYCHE/affect.py"`, `../src/PSYCHE/traits.py`, `../src/PSYCHE/network.py`, `../src/PSYCHE/intuition.py`, `../src/PSYCHE/rt_agent.py`, `../src/PSYCHE/rt_channel.py`, plus `../src/PSYCHE/data/triage_corpus.jsonl` and `../src/PSYCHE/data/affect_bridge.json`.

So the tree is **stdlib-pure but source-dependent**: it needs `src/PSYCHE/` present in the monorepo to materialise. Once materialised it is genuinely standalone, which is the design — but a fresh clone of `Project_ELIZA` alone cannot produce its own package.

**Publish consequence, and it is a hard blocker:** because `.gitignore` ignores `/eliza/`, a fresh standalone repo seeded from this directory would **ignore the very package it is meant to ship**. The released repository would contain tests that cannot import and a `pyproject.toml` declaring `packages = ["eliza", "eliza.psyche"]` that do not exist. Publishing this tree requires either (i) materialising first and committing the generated package into the public repo (which contradicts the "generated, never committed" rule at `MANIFEST_NOTES.md`), or (ii) shipping the `src/PSYCHE` sources inside the tree and generating at install time. **This is a decision the owner must make; it is not a mechanical fix.**

## 4. LICENSE / NOTICE / CITATION state

Complete and consistent. Apache-2.0 in `LICENSE`, `pyproject.toml` (`license = { text = "Apache-2.0" }`), `PUBLIC_MANIFEST.json` (`"license": "Apache-2.0"`), `CITATION.cff` (`license: Apache-2.0`) and `NOTICE`. This is the precedent that makes Apache-2.0-everywhere the consistent choice for the sibling projects — ELIZA already shipped it, so nothing is being invented.

One gap the file itself admits: `pyproject.toml` has no `authors`, commented "Fill `authors` in before a PyPI upload — a placeholder name is worse than none." That is correct as written and blocks only a PyPI upload, not a GitHub publish.

## 5. Defects found (all cosmetic, none blocking publish independently of §3)

1. **`tools/publicize.py` docstring contradicts its own constants.** It states "Source modules are imported as `eliza.psyche.affect`; the public package is `eliza.psyche.affect`" — identical names, i.e. no rewrite — while the constants below it are `SOURCE_PKG = "PSYCHE"` and `PUBLIC_PKG = "eliza.psyche"`. The code is right and the prose is wrong. In the one file whose job is to guarantee the rewrite, a reader who trusts the docstring concludes no rewrite happens. UNKNOWN whether this is a copy-time edit artefact; it is worth correcting before the file is read by a stranger.
2. **`CHANGELOG.md` `Unreleased` references `src/PSYCHE/data/affect_bridge.json` and `Project_ELIZA/tools/publicize.py`** — monorepo-relative paths that a public reader cannot resolve. Low harm, but it is the same class of leak the gate exists to catch.
3. **`docs/index.md` says "The closest artefact is `rt_channel.py --demo`"** while `README.md` Quickstart runs `src/PSYCHE/rt_channel.py --demo` — the public path is `eliza/psyche/rt_channel.py` post-materialise. Path prose will drift; UNKNOWN which the tutorial uses without reading it (not read).

## 6. Recommended disposition

**Keep it as `Project_ELIZA`. Do not rename its contents toward Nurse Ratchet, and do not fold `azazael-forensics` into it.**

Reasoning, stated so it can be contested:

1. **The identity is not in doubt — only its label is.** `README`, `CITATION`, `pyproject`, `PUBLIC_MANIFEST` and `NOTICE` all agree this is the ELIZA project. `Project_Nurse_Ratchet` is the rename victim, not the container: it now holds this project's psyche stack under a different name. Restoring the name restored the project.
2. **Renaming the contents to match Nurse Ratchet would re-commit the original error** — it would merge two projects a second time, in the opposite direction.
3. **Folding `azazael-forensics` in would produce a tree that is neither.** They have different provenance, different licences of reasoning (forensics is "Yggdrasil Cleave #11", portable-capability), and forensics already has its own `.git` and would be double-published.
4. **What the manifest must say instead** is the correction: ELIZA = the therapeutic agent loop *and the disclosure/gate discipline the forensic investigation produced*; `azazael-forensics` = the portable forensic detectors. Two repos, one lineage, no merge.

**Before ELIZA can publish, three things must happen — none of them in this auditor's scope:**

- Resolve §3 (generated package vs shipped sources) — the hard decision.
- Materialise and run the 9 test files, which have never been executed in this restored form.
- Correct the `publicize.py` docstring (defect 1) so the rewrite claim matches the constants.

## 7. What this audit did not establish

- **No test was run, no instrument was run, no import was attempted.** Verdicts rest on reading files; the coordinator has a terminal.
- `docs/tutorial.md`, `docs/reference/psyche.md`, `docs/explanation/why-eliza.md`, `.github/workflows/ci.yml`, `tools/triage_eval.py`, `tools/psyche_fit_pams.py`, `tools/fit_affect_bridge.py` and all 9 test files were **not opened**. Their descriptions above come from the README/CHANGELOG/MANIFEST summaries, flagged where so.
- Whether `src/PSYCHE` still exists in the current monorepo and still matches the `ship` manifest was **not checked** — if it has drifted, materialisation would produce a package differing from what 0.1.0 measured.
- The `never_ship` globs were read but not exercised against the actual tree; whether one of them matches a legitimate shipped path is UNKNOWN.
