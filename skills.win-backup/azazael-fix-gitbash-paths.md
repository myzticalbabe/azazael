---
name: azazael-fix-gitbash-paths
description: Quick-reference fixes for Git Bash/MSYS2 environment errors — path translation, PowerShell escaping, and shell quoting.
metadata:
  category: fixes
  project: azazael
---

# 🛠️ Skill: Fixes for Environment & Path Handling

*Quick-reference solutions extracted from ERROR_LOG.md for known errors in Environment & Path Handling.*

## Error #51 — MSYS2 Path Translation Breaks WSL Commands from Git Bash
**Symptom:** See ERROR_LOG.md.
**Fix Solution:**
See ERROR_LOG.md
**Prevention:**
Add `MSYS2_ARG_CONV_EXCL=/mnt` prefix to all WSL commands run from Git Bash. If robocopy is involved, use `MSYS2_ENV_CONV_EXCL='*' cmd.exe //c "robocopy ..."`.

---
## Error #52 — Python 3.14t Source Build on Ubuntu 26.04 (apt_pkg + libdb)
**Symptom:** See ERROR_LOG.md.
**Fix Solution:**
post_install.sh updated with:
- `apt install --reinstall -y python3-apt` before `apt update`
- `libdb-dev` → `libdb5.3-dev` with `|| warn` guard (optional dep)
- Dynamic Intel repo check via `wget --spider` + `lsb_release -cs` codename detection
**Prevention:**
When writing distro-specific scripts, check package names with `apt-cache search` first. Always handle optional dependencies with `|| warn` to avoid `set -e` aborting the script.

---
## Error #55 — False Diagnosis: "Autoflake Doesn't Work on 3.14t" — Actually a Shell-Escaping Bug
**Symptom:** A previous assistant incorrectly concluded that `autoflake v2.
**Fix Solution:**
See ERROR_LOG.md
**Prevention:**
1. Before declaring ANY tool "broken on 3.14t", isolate the failure mode:
   - Test the tool directly in Python: `python -c "import subprocess; ..."`
   - Run `python -m autoflake --version` to confirm it loads
   - Check if it's a C-extension package (needs cp314t wheel) or pure-Python (works everywhere)
2. Pure-Python tools (autoflake, pyflakes, isort, black, ruff) work on 3.14t —
   they have n

---
## Error #56 — PowerShell Cmdlet Escaping in Git Bash basher Commands
**Symptom:** See ERROR_LOG.md.
**Fix Solution:**
Always write complex PowerShell commands to a `.ps1` temp file and execute
with `powershell -File _tmp.ps1`. For simple commands, avoid `$` variable references
by using Python to write PowerShell scripts.
**Prevention:**
1. For any PowerShell command with `$`, `{`, `}`, `|`, or `%`: write to `.ps1` file first
2. Keep PowerShell one-liners to single commands without variable interpolation
3. Use Python pathlib instead of PowerShell for file operations when possible
4. Test the command standalone in PowerShell before putting it in basher

---
## Error #59 — Windows Backslash Path Interpretation in Git Bash
**Symptom:** See ERROR_LOG.md.
**Fix Solution:**
See ERROR_LOG.md
**Prevention:**
1. Prefer Python pathlib for all file operations in scripts
2. When using shell commands, use forward slashes
3. Never pass Windows backslash paths directly to bash commands
4. For `cmd.exe` commands, use `cmd.exe //c` prefix to bypass MSYS2 translation

---
## Error #60 — Worm Registry Test Returns 0 Worms Due to Shell Escaping
**Symptom:** See ERROR_LOG.md.
**Fix Solution:**
Write Python scripts to temp files, then execute with `python _tmp.py`.
This is the SAME root cause as Error #55 (autoflake false diagnosis) and
Anti-pattern #1 (nested quotes in basher commands).
**Prevention:**
1. For any Python code longer than 1-2 lines, write to `_tmp.py` file (Anti-pattern #1)
2. Never use `python -c` with list comprehensions that contain `{}`, `$`, or `[]`
3. If a test shows 0 results but should have many, suspect shell escaping first

---
## Error #63 — Unicode Escape Crash in DirectMemory Basher Command
**Symptom:** Python `-c` command string passed via basher contained `C:\Users\clint` with backslashes.
**Fix Solution:**
Rewrote the recording command to avoid backslash paths entirely. Used forward slashes and simplified descriptions without Windows path literals.
**Prevention:**
Never include Windows backslash paths in basher Python `-c` commands — write to `_tmp.py` file first (Anti-pattern #1). Use forward slashes or pathlib in Python code. Same root cause as Error #59.

---
