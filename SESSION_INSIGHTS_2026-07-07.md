# SESSION_INSIGHTS — July 7, 2026

> **Session ID:** `codebuff_20260707_103024`
> **DirectMemory:** 12 events recorded
> **Duration:** ~3 hours

---

## Primary Task: Fix `interpreter -y --local`

The user reported that `interpreter -y --local` (Open Interpreter CLI) was not working. Investigation revealed 9 cascading failures across the dependency chain.

### Failures Diagnosed & Fixed

| # | Category | Issue | Fix |
|---|----------|-------|-----|
| 1 | Environment | `.env` file corrupted (byte 0x97 Windows-1252 em dash) | Binary read/replace → UTF-8 |
| 2 | Installation | Open Interpreter not installed | `pip install open-interpreter` → 0.4.3 |
| 3 | 3.14t C-ext | `regex` circular import | Force-reinstall → 2026.6.28 |
| 4 | 3.14t C-ext | `Pillow._imaging` broken | Force-reinstall → 12.3.0 |
| 5 | 3.14t C-ext | `matplotlib._c_internal_utils` circular import | Force-reinstall → 3.11.0 |
| 6 | 3.14t C-ext | `kiwisolver._cext` missing | Force-reinstall kiwisolver |
| 7 | 3.14t C-ext | `tokenizers.tokenizers` missing | Force-reinstall → 0.23.1 |
| 8 | 3.14t C-ext | `jiter.jiter` missing | Force-reinstall → 0.16.0 |
| 9 | Code bug | litellm `BadRequestError: LLM Provider NOT provided` | Patched `local_setup.py` to add `openai/` prefix |

### Secondary: Jan provider litellm crash

After fixing all C-extension issues, selecting Jan in Open Interpreter crashed with:
```
BadRequestError: LLM Provider NOT provided. You passed model=Jan-v3.5-4B-Q4_K_XL
```

**Root cause:** Open Interpreter 0.4.3's `local_setup.py` doesn't prefix Jan model names with `openai/` that litellm requires. One-line fix:
```python
# Before: interpreter.llm.model = jan_model_name
# After:  interpreter.llm.model = f"openai/{jan_model_name}"
```

Verified: `litellm.completion()` with Jan model → `"OK: Chill."`

---

## Additional Work

### Dependency Tree Scan
- Scanned all 141 packages in open-interpreter dependency tree (22 with C extensions)
- Found 1 remaining issue: `contourpy._contourpy` — fixed by force-reinstall
- All other C-extension packages clean on 3.14.6t

### TODO Audit
- Audited `CODEBASE_AUDIT_TODO.md` v11 and `MASTER_TASKS.md`
- **13/22 AR items done**, 8/12 production steps not started
- Top pending: AR-11 (mypy errors), Step 4 (error recovery)

### T5 — Syntax Audit
- **486/486 .py files pass** syntax check
- 2 minor SyntaxWarnings (invalid escape sequences, non-blocking)

### T6 — Worm Registry Integration Test
- **104 worms, 18 categories, 1.0s discovery** — PASS
- Was 91 worms at 38s (improvement from warm-path optimization)

### Documentation
- Error #188 recorded to `ERROR_LOG.md` with full fix chain
- Drafted GitHub bug report for open-interpreter issue #1177

---

## Key Lessons

1. **`.env` corruption is silent and catastrophic** — a single Windows-1252 byte blocks ALL processes that touch `.env`. Always validate UTF-8 after any file write.
2. **The `pip install --force-reinstall --no-deps` pattern works for all 3.14t C-extension issues** — 7 packages fixed this session, all same pattern.
3. **Watch for version mismatches when force-reinstalling** — pydantic-core 2.47.0 broke pydantic 2.13.4; `pip install --upgrade pydantic` auto-resolved.
4. **The 3.14t C-extension issue is well-documented now** — Errors #49, #54, #188 all follow the same pattern. Future sessions can reference these.

---

## Files Modified
- `C:/Users/clint/.env` — fixed corrupted byte
- `interpreter/terminal_interface/local_setup.py` — added `openai/` prefix
- `azazael/ERROR_LOG.md` — appended Error #188

---

# SESSION_INSIGHTS #2 — July 7, 2026 (continued)

> **Session ID:** `codebuff_20260707_144544` (startup) → `codebuff_20260707_154342` (milestone)
> **DirectMemory:** Session milestone recorded
> **Duration:** ~2 hours

---

## Primary Task: Fix Ubuntu root apt + prep `interpreter -y --local` on 3.14.6t

### Completed

| # | Task | Result |
|---|------|--------|
| 1 | Session startup | 14 skills loaded, canonical docs read, DirectMemory initialized |
| 2 | ERROR_LOG.md audit | Found Error #188 missing — appended full 9-failure fix chain |
| 3 | Ubuntu apt fix | Restored `/usr/bin/python3` → system 3.14 via `update-alternatives`, reinstalled `python3-apt` |
| 4 | Error #189 recorded | Documented apt fix with prevention rules (use `make altinstall`, never alias `python3` in root) |
| 5 | venv-314t diagnosis | Python 3.14.6 free-threading ✅, open-interpreter 0.4.3 installed but import cascade broken |

### Pending — venv-314t cascading deps

The venv has 3.14.6t and open-interpreter 0.4.3, but imports fail in a cascade:
1. `shortuuid` — missing (installed, now OK)
2. `pydantic-core` 2.47.0 vs `pydantic` 2.13.4 mismatch — downgraded to 2.46.4 (now OK)
3. `wget` — missing (installed, now OK)
4. `toml` — **NEXT TO FIX**
5. ... more likely queued behind it

**Recommended approach:** `pip install open-interpreter` with full deps in the venv (not `--no-deps`), then `--force-reinstall --no-deps` any C-extensions that need cp314t wheels.

### Pending — Ubuntu replication

After venv-314t works on Windows:
1. Install Python 3.14.6t on Ubuntu-26.04 (use `make altinstall`!)
2. Create venv with 3.14.6t
3. `pip install open-interpreter` + force-reinstall C-exts
4. Verify `interpreter -y --local` works on Ubuntu

---

## Key Lessons

1. **`make install` vs `make altinstall`** — the former overwrites `/usr/bin/python3`, breaking system tools. Always use `altinstall` for custom Python builds.
2. **Never alias `python3` in root's `.bashrc`** — even a `python3='python3.14t'` alias breaks apt and other system tools.
3. **venv cascading deps are like whack-a-mole** — `pip install <pkg>` with full deps first, then fix C-exts. Don't fix one-by-one.

---

## Files Modified This Session
- `azazael/ERROR_LOG.md` — appended Error #188 (9 cascading failures), Error #189 (Ubuntu apt fix)

