# AUDIT — Project_CRADLE (2026-11-02)

**Target:** `C:/Azazael/azazael/Project_CRADLE`
**Question:** can this publish as its own standalone GitHub repo, usable with no monorepo present?
**Verdict:** **COUPLED — does not publish as-is.** One blocking item, named in §5.
**Read-only audit.** No project file was edited. Every claim below carries a `file:line`.

---

## 1. What is actually in the directory

| Item | Present | Evidence |
|---|---|---|
| `cradle.py` | yes | entry point, 1 file |
| `CRADLE.md` | yes | the document (there is no `README.md`) |
| `LICENSE` | yes | Apache-2.0, added this session |
| `NOTICE` | yes | added this session; already declares the sibling dependency |
| `tests/test_cradle.py` | yes | 12 test functions |
| `pyproject.toml` | **no** | none in the directory listing |
| `README.md` | **no** | `CRADLE.md` carries the role |

So: a launcher, a document, two licence files and one test module. There is no package, no
`__init__.py`, and no packaging metadata.

## 2. The part/entry list, and whether each resolves inside its own tree

`cradle.py` composes five parts. The base path is set at **`cradle.py:73`**:

```python
SWORD_TOOLS = REPO / "Project_FLAMING_SWORD" / "tools"     # cradle.py:73
REPO = ROOT.parent                                          # cradle.py:72
ROOT = Path(__file__).resolve().parent                      # cradle.py:71
```

and the registry at **`cradle.py:76-82`**:

| Part | Declared path | Inside `Project_CRADLE/`? | Exists in sibling? |
|---|---|---|---|
| `defender` | `cradle.py:77` → `Project_FLAMING_SWORD/tools/defender.py` | **No** | yes |
| `sentinel` | `cradle.py:78` → `.../tools/sentinel.py` | **No** | yes |
| `memory` | `cradle.py:79` → `.../tools/memory_bridge.py` | **No** | yes |
| `server` | `cradle.py:80` → `.../tools/chain_server.py` | **No** | yes |
| `sword` | `cradle.py:81` → `.../tools/sword.py` | **No** | yes |

**0 of 5 parts resolve inside the project.** All five resolve only because the sibling
`Project_FLAMING_SWORD/tools/` exists in this monorepo; I confirmed all five filenames are
present there, alongside two files CRADLE does not reference (`disposition.py`,
`housekeep.py`).

## 3. Every filesystem reference that leaves the directory

| Location | Reference |
|---|---|
| `cradle.py:73` | `SWORD_TOOLS` — the single base path that all coupling flows from |
| `cradle.py:77-81` | the five `PARTS` values, all under that base |
| `cradle.py` `demo()` (target string) | `"Project_FLAMING_SWORD/tools/sword.py"` used as the demo's relative target |
| `cradle.py` `demo()` (`root=str(REPO)`) | hands the **repo root** to `defender.to_aio(...)`, so the sibling tree is the frame's working root |
| `CRADLE.md` part table | the "where it lives" column names `Project_FLAMING_SWORD/tools/*.py` for all four named parts |
| `CRADLE.md` §Uninstall | "Delete `Project_CRADLE/` **and** `Project_FLAMING_SWORD/`" |
| `NOTICE` §Attribution notes | declares the four parts live in a sibling project "and NOT redistributed here" |

**A clean finding worth stating:** there are **zero machine-absolute paths**. A search for
`C:\\`, `C:/`, `/home/`, `/root/` across the directory returned 0 matches. Nothing here is
tied to `C:/Users/clint` or `C:/Azazael`, so this project will not leak the author's
username and will not break on another host for path reasons. Its only coupling is
relative, which is the good kind.

Note also that the coupling is **not import-level**. Every import in `cradle.py` is stdlib
(`argparse`, `importlib.util`, `json`, `shutil`, `sys`, `tempfile`, `urllib`,
`pathlib`, `typing`), and the parts are loaded at runtime via `_load()` with
`importlib.util.spec_from_file_location`. The consequence is the worse failure mode: the
module imports cleanly in a fresh clone and fails on first *use*.

## 4. Runnability from a fresh clone with no monorepo

| Command | Behaviour in a fresh clone | Why |
|---|---|---|
| `python cradle.py --doctor` | exits **1**; five checks FAIL | `cradle.py` `doctor()` appends a `(name, path.exists(), ...)` check per part, and a missing part is a failure — correct behaviour, but the machine is never "ready" |
| `python cradle.py --demo` | exits **1**, prints `CANNOT DEMO: defender is missing` | explicit guard at the top of `demo()` for `defender` and `memory` |
| `python cradle.py --grimoire` | exits **1**, prints `CANNOT READ THE GRIMOIRE` | explicit guard on `PARTS["memory"]` |
| `python cradle.py --serve` | exits **1**, prints `CANNOT SERVE` | explicit guard on `PARTS["server"]` |
| `python -m pytest tests/` | **fails** | `tests/test_cradle.py:38-40` asserts every `PARTS` path exists; `test_doctor_reports_ready_on_this_tree` then fails too, and the demo/grimoire tests depend on the parts |

Every failure is **honest** — each one names the missing file rather than reporting a green.
That is a real virtue of this tree and it is why the coupling is diagnosable rather than
mysterious. But it means a published CRADLE is a project whose every command exits 1.

`--doctor` itself is well built: it checks the interpreter against `MIN_PYTHON = (3, 9)`
(`cradle.py:95`), a writable state dir via a temp probe, `git` on `PATH`, and treats "no
model configured" as a **stated pass** rather than a failure. That last choice is correct
and worth preserving.

## 5. Verdict and the blocking item

**COUPLED.**

**Blocking item:** all five parts live in `Project_FLAMING_SWORD/tools/`, reached through
the single line `cradle.py:73`. With that sibling absent, `--doctor`, `--demo`, `--serve`,
`--grimoire` and the whole test module all exit 1.

Three ways to close it, in the order I would rank them:

1. **Publish CRADLE and FLAMING SWORD as one repo** (CRADLE at the root, the tools at
   `tools/`, `SWORD_TOOLS` pointed at `ROOT / "tools"`). This matches what CRADLE actually
   *is* — the README's own framing is "the composition, the launcher"; the composition
   cannot be split from what it composes. It also makes `NOTICE`'s
   "not redistributed here" line unnecessary rather than merely accurate.
2. **Declare the dependency and accept it.** Keep them separate and make the README say
   plainly: "this is the front door of `Project_FLAMING_SWORD`; install that alongside."
   The `NOTICE` and `CRADLE.md` §Uninstall already say this. It publishes, but as a
   companion, not a standalone tool — which conflicts with the owner's "usable
   independently" requirement.
3. **Vendor the five parts** into `Project_CRADLE/tools/`. Cheapest mechanically, worst
   structurally: `CRADLE.md` spends a paragraph arguing that paths must not be renamed to
   match the story, and a copy creates two sources that will drift.

**What is already right and should not be touched:** no absolute paths; every failure names
its missing file; `--doctor` treats an absent model as a pass with a reason; the licence
pair (`LICENSE` + `NOTICE`) is present and the `NOTICE` already attributes the sibling
honestly; `CRADLE.md` has a real "What this does not do" section (sentinel judges a frame
not an inference; `--serve` has no auth; a frame is advisory until something requires it,
open item M-42).

## 6. Not verified

- I did not execute anything — no terminal. The runnability table in §4 is derived from
  reading the guards and assertions, not from a run.
- I did not read `Project_FLAMING_SWORD/tools/*.py` beyond confirming the five filenames
  exist, so I cannot say whether those parts have their own monorepo coupling that would
  surface once CRADLE is fixed.
- I did not check whether `tests/test_cradle.py` needs anything outside the project besides
  the five parts.
