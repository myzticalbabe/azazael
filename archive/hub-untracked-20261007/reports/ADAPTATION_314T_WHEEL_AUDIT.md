# Adaptation Stack on Python 3.14t — Wheel Audit & Fix

**Date:** 2026-09-20
**Question:** *Why won't the self-adaptation stack (`gymnasium`, `stable-baselines3`,
`peft`, `trl`, `datasets`, `transformers`) install on the free-threaded 3.14t
interpreters, and which packages are genuinely blocked by wheel availability?*

## Verdict

**Nothing is wheel-blocked. Zero packages were blocked by the absence of a
`cp314t` wheel.** The premise behind the claim in
`PRIORITIES_2026-09-18.md` —

> *"LLM fine-tuning is blocked, not skipped. No venv in this tree has
> `peft`/`trl`/`transformers`, and CPython 3.14 free-threaded has no wheels for
> them."*

— is **false**, and it was false on the day it was written. Both halves are
wrong:

1. The Windows *global* environment already had `peft 0.19.1`, `trl 1.4.0`,
   `transformers 5.17.0` installed and importable.
2. The free-threaded interpreters resolve the whole stack from binary wheels
   with no source builds.

The real defects were (a) **nobody installed the stack into the 3.14t venv**, and
(b) **two transitive modules that `transformers` 5.17 imports are not declared
in its metadata.** Both are fixed below.

---

## 1. Evidence — resolution on each free-threaded interpreter

### Windows `venv-314t` (3.14.7, `gil_enabled=False`, pip 26.1.2)

```
pip install --dry-run --only-binary=:all: gymnasium stable_baselines3 peft \
            trl datasets transformers
→ Would install Farama-Notifications-0.0.6 accelerate-1.15.0 datasets-5.0.1
  dill-0.4.1 fsspec-2026.6.0 gymnasium-1.3.0 mpmath-1.3.0 multiprocess-0.70.19
  networkx-3.6.1 peft-0.21.0 safetensors-0.9.0rc0 stable_baselines3-2.9.0
  sympy-1.14.0 transformers-5.17.0 trl-1.13.0 xxhash-4.0.1
```

`--only-binary=:all:` **succeeded**. A source build would have failed loudly; it
did not, because no source build is required.

### WSL Ubuntu-26.04 `/usr/bin/python3` (3.14.7, free-threaded)

```
Would install Farama-Notifications-0.0.6 accelerate-1.15.0 cloudpickle-3.1.2
  datasets-5.0.1 dill-0.4.1 gymnasium-1.3.0 multiprocess-0.70.19
  nvidia-* (25 CUDA wheels) peft-0.21.0 pyarrow-25.0.1 stable_baselines3-2.9.0
  triton-3.7.0 trl-1.13.0 xxhash-4.0.1
```

Modern versions, clean resolution.

### WSL Kali `/usr/bin/python3` (3.14.6, free-threaded)

```
Would install ... peft-0.21.0 pyarrow-25.0.1 stable_baselines3-2.9.0
  torch-2.14.0 transformers-2.3.0 triton-3.8.0 trl-0.12.2
```

⚠️ **Kali backtracks hard**: `transformers-2.3.0` (year 2019) and `trl-0.12.2`
instead of `5.17.0` / `1.13.0`. The resolver is not finding the modern line on
that interpreter — a constraint conflict, not a missing wheel. **Kali cannot
currently obtain the modern stack without an explicit pin and conflict
resolution.** This is the one environment where "install the stack" is not a
one-liner.

---

## 2. The real blockers (both undeclared transitive imports)

Importing the stack on `venv-314t` after install produced:

```
OK   torch 2.14.0+cpu     OK   trl 1.13.0        OK   gymnasium 1.3.0
OK   transformers 5.17.0  OK   datasets 5.0.1    OK   stable_baselines3 2.9.0
FAIL peft  → ModuleNotFoundError: Could not import module 'AutoModel'
```

`transformers` 5.17.0 shuffles this failure through its `_LazyModule`, so the
outer error names `AutoModel` and hides the cause. Walking `__cause__` exposed:

| Depth | Error |
|---|---|
| 1 | `Could not import module 'AutoModel'` |
| 2 | `Could not import module 'GenerationMixin'` |
| 3 | **`No module named 'narwhals'`** |

Then, after `narwhals` was installed, the chain re-formed one link deeper:

| Depth | Error |
|---|---|
| 3 | **`No module named 'threadpoolctl'`** |

Both are imported by the `GenerationMixin` path of `transformers` 5.17.0 but are
**absent from its `Requires-Dist` metadata**. Any environment that installs
`transformers` 5.17.0 without `scikit-learn`/`narwhals` present elsewhere will
hit this. Under the old GIL environment the failure was masked because
`scikit-learn` (which provides `threadpoolctl`) and `narwhals` happened to be
installed for unrelated reasons.

**This is a silent-failure class, not a packaging class**: the lazy-import
wrapper reports the *symbol* it wanted, never the *module* it lacked, so a
missing leaf dependency looks like a broken library.

---

## 3. Fix applied (2026-09-20)

```bash
PY=/c/Users/clint/venv-314t/Scripts/python.exe
"$PY" -m pip install --only-binary=:all: \
    gymnasium stable_baselines3 peft trl datasets transformers
"$PY" -m pip install --only-binary=:all: narwhals threadpoolctl   # undeclared leaf deps
```

**Result: `venv-314t` 161 → 178 packages; 12/12 stack modules import on a
free-threaded interpreter.**

```
OK   torch                2.14.0+cpu      OK   trl                  1.13.0
OK   transformers         5.17.0          OK   datasets             5.0.1
OK   gymnasium            1.3.0           OK   accelerate           1.15.0
OK   stable_baselines3    2.9.0           OK   safetensors          0.9.0-rc.0
OK   peft                 0.21.0          OK   tokenizers           0.23.2
OK   numpy                2.4.6           OK   networkx             3.6.1
RESULT: 12/12 importable — python 3.14.7 free_threaded=True
```

### Functional proof (not just imports)

```
free_threaded = True
gymnasium  : reset OK obs (4,) actions Discrete(2)
sb3        : PPO.learn(256) OK; actions [1, 1, 1]
peft       : LoraConfig OK r=4 alpha=8
transformers: AutoConfig OK GPT2Config
datasets   : Dataset OK 3 rows
trl        : OK 1.13.0

ALL STAGES FUNCTIONAL UNDER FREE-THREADING (3.14t)
```

`PPO.learn()` actually executes a training loop; `LoraConfig` constructs a real
adapter config. The evolution/training path is now runnable free-threaded — the
**I1 interop fault in `MASTER_ENVIRONMENT_INVENTORY.md` is closed on Windows.**

---

## 4. Per-environment status

| Environment | Interpreter | Wheels available | Modern stack | Action needed |
|---|---|---|---|---|
| Windows `venv-314t` | 3.14.7t | ✅ | ✅ **12/12 live** | **done** |
| Windows global | 3.14.7 (GIL on) | ✅ | ✅ already present | none |
| WSL Ubuntu-26.04 | 3.14.7t | ✅ | resolves cleanly | `pip install` (adds ~25 CUDA wheels ≈ 4–6 GB) |
| WSL Kali | 3.14.6t | ✅ | ⚠️ backtracks to `transformers 2.3.0` | needs explicit pin + conflict resolution |
| Windows `venv-interpreter` | 3.14.7 (GIL on) | ✅ | numpy only | not the target runtime |
| `azazael/.venv-3.14t` | 3.14.7t | ✅ | 11-package stub | repoint or rebuild (I7) |

---

## 5. Corrections and follow-ups

| # | Item |
|---|---|
| C1 | Retract the `PRIORITIES_2026-09-18.md` claim that 3.14t has no wheels for `peft`/`trl`/`transformers`. It was misinformation that plausibly suppressed the fix for two days. |
| C2 | Add `narwhals` + `threadpoolctl` to the 3.14t requirements as **explicit** entries, with a comment recording that `transformers` 5.17 omits them. |
| C3 | `transformers`' lazy-import wrapper should be treated as an **unvalidated instrument**: it reports the missing *symbol*, not the missing *module*. Any future "package X is broken" conclusion must walk `__cause__` first. |
| C4 | Ubuntu should install the stack but **without** the CUDA extras unless the accelerator is actually used — `--no-deps` auditing or a CPU-only index avoids ~5 GB of `nvidia-*` wheels. |
| C5 | Kali's resolver backtrack must be diagnosed before the stack is considered available there. |

### Suggested requirements block (Windows 3.14t)

```
# self-adaptation stack — verified resolvable from binary wheels on cp314t
gymnasium==1.3.0
stable_baselines3==2.9.0
peft==0.21.0
trl==1.13.0
datasets==5.0.1
transformers==5.17.0
accelerate==1.15.0
torch==2.14.0+cpu
# undeclared transitive leaf deps required by transformers 5.17 GenerationMixin
narwhals>=2.26.0
threadpoolctl>=3.1.0
```
