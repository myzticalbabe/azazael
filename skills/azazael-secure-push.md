# Skill: azazael-secure-push

# Azazael Secure Push — pre-push scanning adapted to this tree

> Adapted from agentsoflearning `secure-push` (gitleaks + semgrep + trivy).
> Tool reality on this box (2026-09-27): **trivy present**, gitleaks and
> semgrep NOT installed. The skill degrades honestly: what exists runs,
> what doesn't is an install step, never a silent skip.

---

## Trigger

Use before any `git push`, and before syncing vendored skills outward.
The home tree is 456-dirty; the azazael subtree is git-ignored and ships
via G: snapshot + mirror sync instead — scan what actually moves.

## Layer 1 — Secrets (gitleaks; install if missing)

```powershell
winget install Gitleaks.Gitleaks
gitleaks detect --source C:\Users\clint\azazael --no-git -v
```

BLOCK on any hit. `.env` files, `use_model.dat`, API keys in scripts
(`OPENROUTER_API_KEY` et al. live in `.env` — verify none are inlined).

## Layer 2 — SAST (semgrep; install if missing)

```powershell
pip install semgrep
semgrep --config auto src/CORE --quiet
```

Focus: `os._exit`, `shutil.rmtree`, `subprocess` with `shell=True`,
bare `except`, dynamic `exec` — all present in this tree BY DESIGN
(chain, pilot, cleaner), so findings need human triage, not auto-block.

## Layer 3 — Dependencies (trivy; present)

```powershell
trivy fs --severity HIGH,CRITICAL C:\Users\clint\azazael
trivy fs --severity HIGH,CRITICAL C:\Users\clint\venv-314t
```

BLOCK on Critical. venv-314t just gained nuitka — scan it with the venv.

## Policy

- BLOCK: secrets anywhere; Critical CVEs; SAST findings on NEW code
  (grandfather existing triaged patterns — the tree documents its
  dangerous calls inline with rationale comments).
- WARN: Medium/Low, dependency updates available.
- Home-tree BCC evidence (HTML/JSON) is out of scope — investigation
  artifacts, reviewed by humans, never pushed by automation.

## Verification

```powershell
gitleaks detect --source C:\Users\clint\azazael --no-git
trivy fs --severity HIGH,CRITICAL C:\Users\clint\azazael
```

Both clean (or triaged with reasons on file) before any push or snapshot
that leaves this machine.
