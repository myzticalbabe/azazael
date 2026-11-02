# AUDIT — Project_Nurse_Ratchet (2026-11-02)

**Target:** `C:/Azazael/azazael/Project_Nurse_Ratchet` — the THERAPEUTIC HEALTH agent, publishing as its own standalone repo.
**Mode:** READ-ONLY. Nothing was edited. No command was executed.
**Verdict:** **COUPLED** — soft coupling. It imports cleanly in a fresh clone and then silently loses a capability. Details in §6.

Every claim carries a `file:line`. Where an instrument could not see, it says UNKNOWN rather than guessing.

---

## 0. One structural fact that governs this whole audit

`nurse_ratchet/psyche/*` is **generated, not authored, and is gitignored**:

- `PUBLIC_MANIFEST.json:354` — "layout": the package is materialised from `../src/PSYCHE` by `tools/publicize.py`
- `PUBLIC_MANIFEST.json:357` — "generated_not_committed": psyche/* is gitignored and produced at build time

Two consequences, both material to the fix:

1. **`code_search` cannot see `nurse_ratchet/psyche/` at all** — it excludes git-ignored files. Any defect found there must be fixed in **`src/PSYCHE/<module>.py`**, the source, because regeneration overwrites the copy and would silently discard a hand-fix.
2. The published surface is 11 sources, per `PUBLIC_MANIFEST.json:12-262`: `__init__.py`, `affect.py`, `traits.py`, `network.py`, `intuition.py`, `rt_agent.py`, `rt_channel.py`, `constructions.py`, `elicitation.py`, `data/triage_corpus.jsonl`, `data/affect_bridge.json`.

---

## 1. Remaining ELIZA self-identification

Only **one** is wrong, and it is the hardest to notice.

| Location | String | Correct? |
|---|---|---|
| `nurse_ratchet/__init__.py:1` | `"""ELIZA -- see docs/index.md. Package layout mirrors PUBLIC_MANIFEST.json."""` | **WRONG — self-identifies as ELIZA** |
| `NOTICE:20` | "ELIZA is a SEPARATE project in the Azazael tree -- the forensic investigation suite ... It is not this package." | CORRECT |
| `NOTICE:23` | Weizenbaum 1966, CACM 9(1):36-45 | CORRECT — external citation, explicitly "no code from that program is included here" |
| `CITATION.cff:53,59` | Weizenbaum reference; "itself is Nurse Ratched's, not ELIZA's -- see the abstract" | CORRECT |
| `CHANGELOG.md:28-36` | package rename `eliza`→`nurse_ratchet`, plus "Correction (2026-11-02): the directory rename … was an agent error" | CORRECT — historical record, deliberately retained |
| `README.md:4` | "investigation suite is **Project ELIZA** and is a separate package with its own [gate]" | CORRECT — accurate statement about the *other* project |
| `README.md:22` | "ELIZA (1966) demonstrated it with a joke about therapy" | CORRECT — history |
| `docs/explanation/why-nurse-ratchet.md:8-9` | "Weizenbaum wrote ELIZA as a joke about therapy … and Nurse Ratched was written as an antagonist" | CORRECT — history/contrast, not identity |

### Why `__init__.py:1` persists

`tools/publicize.py:147-149`:

```python
init = PROJECT / "nurse_ratchet" / "__init__.py"
if not init.exists():
    init.parent.mkdir(parents=True, exist_ok=True)
    init.write_text('"""Project Nurse Ratchet -- see docs/index.md. ...')
```

The generator writes the **correct** docstring, but only `if not init.exists()`. The file already exists carrying the pre-rename text, so **regeneration will never repair it**. The stale artifact is sticky by construction. `nurse_ratchet/__init__.py` is also absent from `PUBLIC_MANIFEST.json`, so nothing else touches it.

**Fix:** delete `nurse_ratchet/__init__.py` and re-run `python Project_Nurse_Ratchet/tools/publicize.py`. Do not hand-edit the generated file — that repair is silently reverted by the next regeneration, which is the same class of bug.

**Not defects:** two `.pyc` files under `nurse_ratchet/psyche/__pycache__/` contain the string, but they are gitignored build artifacts; a clean removes them. Do not edit bytecode.

---

## 2. CORE imports — the real coupling

The guard `from CORE.failure_ledger import note_failure` appears in **9 source modules** under `src/PSYCHE`. **5 of them ship** (per `PUBLIC_MANIFEST.json:12-262`):

| Source | Ships? | Guard style |
|---|---|---|
| `src/PSYCHE/traits.py:44` | **YES** | bare `except ImportError:` → `pass` |
| `src/PSYCHE/affect.py:58` | **YES** | bare `except ImportError:` → `pass` |
| `src/PSYCHE/network.py:60` | **YES** | captures `_ledger_exc` → `_LEDGER_IMPORT_ERROR` |
| `src/PSYCHE/intuition.py:57` | **YES** | captures `_ledger_exc` → `_LEDGER_IMPORT_ERROR` |
| `src/PSYCHE/rt_channel.py:47` | **YES** | captures `_ledger_exc` → `_LEDGER_IMPORT_ERROR` |
| `src/PSYCHE/distill.py:39` | no | bare `except ImportError:` → `pass` |
| `src/PSYCHE/evaluate.py:46` | no | bare `except ImportError:` → `pass` |
| `src/PSYCHE/artifact.py:34` | no | bare `except ImportError:` → `pass` |
| `src/PSYCHE/identify.py:40` | no | bare `except ImportError:` → `pass` |

`CORE` is a monorepo package. Outside `C:/Azazael/azazael` it does not exist, so **all five published guards take the `except` branch on every import in a fresh clone.** Nothing crashes — which is exactly why this survived until now.

Note the generated copy confirms it too: `nurse_ratchet/psyche/traits.py:44` (read directly; invisible to scoped search because it is gitignored).

---

## 3. The silent-swallow pattern — the tree's own rule is violated

`src/PSYCHE/network.py:57-59` states the rule explicitly:

> "Import guard written with two statements rather than `pass`: a missing ledger must be distinguishable from a working one, and the staging gate reads a bare `except ImportError: pass` as a swallowed defect."

The named form (`intuition.py:57-64`) honours it:

```python
except ImportError as _ledger_exc:          # pragma: no cover - host always has it
    _LEDGER_IMPORT_ERROR = str(_ledger_exc)
    def note_failure(...): """Record nothing: the ledger itself is missing. Named, not silent."""
```

The bare form does not, and its own comment concedes the tradeoff — `traits.py:44-47`:

```python
except ImportError:                               # never break the host
    def note_failure(where, exc=None) -> None:
        pass  # ledger missing; evidence-vs-silence tradeoff capped here
```

**Finding:** of the five *published* CORE guards, **two use the bare form that this tree declares a defect** — `traits.py:44` and `affect.py:58`. Those are the two that would matter most in a fresh clone: `affect.py` and `traits.py` are the persona quarter that `README.md:35` advertises as "45 evaluated constants, invariance tested".

This is not a style point. In a standalone install, the failure ledger is *always* missing, so `note_failure` is permanently a no-op and every swallowed exception in the published package is discarded. A therapeutic loop that cannot record its own failures is the defect class `README.md` elsewhere calls the project's worst recurring bug.

**Fix:** add a local `_ledger.py` inside the package that provides `note_failure` (writing to a local file or `logging`), and import from it in all published modules — removing the `CORE` dependency entirely rather than guarding it. Per §0, edit `src/PSYCHE/*`, then regenerate.

---

## 4. Tests and declared dependencies

- `pyproject.toml:16-21` — `dependencies = []`, with the rationale stated: stdlib-only by design, numerical work lives in `tools/` and is not imported.
- `pyproject.toml:31` — only optional dev dependency is `pytest>=7`.
- `pyproject.toml:53-57` — `testpaths = ["tests"]`, `pythonpath = [".", "tools"]`.
- 12 test files in `tests/`: `test_psyche_{affect,bridge_fit,constructions,elicitation,fit_pams,intuition,network,rt_agent,rt_channel,traits}.py`, plus `test_certification_bar.py` and `test_triage_eval.py`.

**Conceptual gap, not a test bug:** every test imports `nurse_ratchet.psyche.<module>` (e.g. `tests/test_psyche_traits.py:18`, `tests/test_psyche_network.py:23`), but that package **does not exist in a clone** — it is gitignored and generated. So the suite is unrunnable until `tools/publicize.py` has been executed. `README.md:178` acknowledges this ("The shipped package is generated, not authored") and `.github/workflows/ci.yml:31` runs generation "Before install, because nurse_ratchet/psyche/ is generated and gitignored".

That means the published repo's tests test the **generated** artifact, never the source — so a defect introduced into `src/PSYCHE` reaches the public tree and only the generator's probes stand between it and release. `tools/publicize.py:158-174` documents exactly this history: an earlier version "verified only the IMPORT and passed while two instruments were broken in the public tree."

**UNKNOWN:** whether the suite passes end-to-end in a materialised tree. Not executed (no terminal in this slice). The `dependencies = []` claim is *true for third-party packages* and *false as written* if `CORE` is counted as a dependency — see §6.

---

## 5. Spelling: "Nurse Ratchet" vs "Nurse Ratched"

**Both spellings appear, and the split is deliberate and documented — this is not a typo.**

| File | Spelling | Context |
|---|---|---|
| `README.md:1,17` | Ratchet | project name; `:17-18` states "(The repository spells it \"Ratchet\", which is the name it was given here; a ratchet is also a mechanism that only turns one way…)" |
| `NOTICE:1,16` | Ratchet | project name and attribution |
| `CITATION.cff:3` | Ratchet | title "Project Nurse Ratchet: …" |
| `CITATION.cff:16` | **Ratched** | "Named for Nurse Ratched, who administers care as control" |
| `CITATION.cff:59` | Ratched | "itself is Nurse Ratched's, not ELIZA's" |
| `README.md:15` | **Ratched** | "Named for Nurse Ratched in *One Flew Over the Cuckoo's Nest*" |
| `NOTICE:16` | Ratchet | "The name Nurse Ratchet refers to the character…" — here the *project* spelling is used to name the *character*, which is the one mildly inconsistent line |

**Verdict:** the character is **Ratched** (Kesey), the project is **Ratchet**, and `README.md:17-18` records the divergence on purpose. The only wording worth a second look is `NOTICE:16`, which attaches the project spelling to the character; that is a stylistic slip, not an error requiring a code change. No file requires a spelling correction.

---

## 6. Verdict: COUPLED

**Not STANDALONE.** The precise reason matters, because it is not the usual one:

`Project_Nurse_Ratchet` **imports cleanly in a fresh clone.** Every `CORE` reference is inside `try/except ImportError`, so nothing raises. It then fails in the worse way — silently:

1. **Capability loss:** 5 of 11 published sources drop failure recording permanently (`traits.py:44`, `affect.py:58`, `network.py:60`, `intuition.py:57`, `rt_channel.py:47`).
2. **Rule violation inside the tree:** 2 of those 5 use the bare swallow that `network.py:57-59` declares a swallowed defect.
3. **Claim contradiction:** `pyproject.toml:16-21` says `dependencies = []` and justifies it as stdlib-only, while five published modules import a monorepo package. The claim is true of third-party packages and incomplete as written.
4. **Sticky stale identity:** `nurse_ratchet/__init__.py:1` self-identifies as ELIZA and `publicize.py:147` will never overwrite it.

**Release gate for this project — all four must clear before publish:**

| # | Item | Where to fix |
|---|---|---|
| 1 | Delete `nurse_ratchet/__init__.py`, re-run `tools/publicize.py` so the correct docstring is generated | generated tree only |
| 2 | Replace the `CORE.failure_ledger` import with a local `_ledger` module in all 5 published modules — remove the dependency, do not guard it | `src/PSYCHE/{traits,affect,network,intuition,rt_channel}.py` |
| 3 | Convert the 2 bare swallows (`traits.py:44`, `affect.py:58`) to the named form, or delete them once #2 lands | `src/PSYCHE/{traits,affect}.py` |
| 4 | Amend `pyproject.toml:16-21` so the stdlib-only rationale is true after #2 | `pyproject.toml` |

Item 2 is the only one that is real work; 1, 3 and 4 are small. Until item 2 lands, the honest label for this package is **"imports standalone, does not run standalone."**

**Separation check — PASSES.** With the single exception of the stale `__init__.py:1`, Nurse Ratchet no longer presents itself as ELIZA. `NOTICE:20`, `CITATION.cff:16,59`, `README.md:4` and `docs/explanation/why-nurse-ratchet.md:8` all correctly describe ELIZA as a *separate* project. The earlier rename's damage is otherwise repaired.

---

*Read-only audit. No file in `Project_Nurse_Ratchet` or `src/PSYCHE` was modified. No test, import or generator was executed — every verdict rests on reading the files cited above, and the four unchecked items in the release gate are marked as work, not as findings.*
