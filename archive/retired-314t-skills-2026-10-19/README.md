# Retired 3.14t skill set — 2026-10-19

## What this is

The 3.14t free-threaded interpreter and its venv (`C:\Users\clint\venv-314t`,
3.14.6t, 2,034 MB) were retired on 2026-10-19. Production is the 3.15t
free-threaded venv `C:\Azazael\.venvs\py315t`; the same 3.15.0rc3 build with the
GIL on is `C:\Azazael\.venvs\py315`. The ONLY sanctioned 3.14 runtime is
`C:\Azazael\.venvs\py314m` (3.14.5, GIL), for a package that genuinely has no
3.15 build.

Two skill families were generated against the retired venv and are retired here:

1. **74 package skills**, one per distribution in that venv's `pip list`
   (`azazael-pkg314t-*`). Each states
   `Interpreter | Python 3.14.6 free-threading (/usr/local/bin/python3.14t)` and a
   verify command against that path. That interpreter no longer exists as a
   production role, so every one of those verify commands is now wrong.
2. **Four environment/fix skills** whose subject is the retired interpreter:
   `azazael-fix-python-314t`, `azazael_314t_master`, `azazael_314t_optimum`,
   and `azazael-timesfm-314t` (kept alive, re-pointed — see below).

## The 74 package skills

`azazael-pkg314t-` + each of:

```
anyio ast-serialize attrs autoflake azazael-core beautifulsoup4 blinker bs4
certifi charset-normalizer click colorama dnspython flask gevent greenlet h11
holehe httpcore httpx hypothesis idna iniconfig itsdangerous jinja2 joblib
librt markupsafe mypy-extensions mypy narwhals nuitka numpy outcome packaging
patchelf-wrapper patchelf pathspec phonenumbers pip pluggy progress psutil
pyflakes pygments pysocks pytest python-dotenv pytz pyyaml requests
scikit-learn scipy six sniffio socksio sortedcontainers soupsieve tabulate
termcolor threadpoolctl toml torbot tqdm treelib trio typing-extensions
unipath urllib3 validators werkzeug yt-dlp zope-event zope-interface
```

## Disposition

| Family | Disposition |
|---|---|
| 74 `azazael-pkg314t-*` | RETIRED. Live copies carry a retirement note in the description; catalog marks them retired; originals remain in git history. |
| `azazael-fix-python-314t` | RETIRED. Its content is a per-error log of 3.14t wheel/segfault fixes; the interpreter is gone. |
| `azazael_314t_master` | RETIRED. Describes `C:/Users/clint/.local/bin/python3.14t.exe` and `.venv-3.14t`, both gone. |
| `azazael_314t_optimum` | RETIRED. Backend survey against 3.14.5 free-threading. |
| `azazael-timesfm-314t` | KEPT, re-pointed to py315t/py314m. It documents a working financial pipeline whose numbers are still valid; only its interpreter claims changed. |

## Why there are no `azazael-pkg315t-*` successors yet

None were generated, and inventing them would be worse than leaving a gap: the
package set of a 3.15t venv is not the package set of the retired 3.14t one
(148 distributions vs 193; `basedpyright`, `mypy`, `nuitka`, `pytest-timeout`,
`timesfm`, `peft`, `trl`, `graphiti-core`, `open-interpreter` are among the ~100
present only in the retired venv). The honest successor is a fresh generation
from `C:/Azazael/.venvs/py315t/Scripts/python.exe -m pip list`, which has not been
run.

## Stubbing the live copies (mechanical, needs a shell)

The live trees are `azazael/skills/*.md` (flat), `C:/Azazael/.agents/skills/*/SKILL.md`
and `C:/Azazael/azazael/.agents/skills/*/SKILL.md`. The retirement note must be
applied to all three or a client that reads a different tree still serves the
retired text. Coordinated in one pass:

```bash
cd /c/Azazael/azazael
NOTE='> RETIRED 2026-10-19 — generated from the retired 3.14t venv; kept as provenance, not callable.'
for f in skills/azazael-pkg314t-*.md; do
  grep -q 'RETIRED 2026-10-19' "$f" || printf '%s\n\n' "$NOTE" | cat - "$f" > "$f.tmp" && mv "$f.tmp" "$f"
done
for f in /c/Azazael/.agents/skills/azazael-pkg314t-*/SKILL.md \
         /c/Azazael/azazael/.agents/skills/azazael-pkg314t-*/SKILL.md; do
  grep -q 'RETIRED 2026-10-19' "$f" || sed -i 's/^name: /# RETIRED 2026-10-19 — 3.14t venv archived; provenance only.\nname: /' "$f"
done
```

A retirement note inserted above `---` would break the YAML frontmatter, which
is why the directory form inserts it after the `name:` key rather than at the
top of the file.

## Provenance

Retired under the 2026-10-19 directive: production is 3.15t only; `py314m` is
the one sanctioned 3.14 fallback. Originals at their last pre-retirement content
are recoverable from git history (`git log -- skills/azazael-pkg314t-attrs.md`).
