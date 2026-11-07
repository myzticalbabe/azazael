"""Native Rust/Go compilers in Eve: check, format, fix.

Eve shells the real toolchains (rustc/cargo/rustfmt/clippy, go/gofmt/vet)
-- no reimplementation, no mocks. The honest boundary is explicit:

- check: compiler diagnostics verbatim (the bug, named by the compiler).
- fmt/fix: only mechanical, compiler-owned fixes (rustfmt, gofmt) applied
  with a .evelang backup; then re-checked. Semantic bugs are surfaced
  with the compiler's own help text, never guessed at.
"""
import shutil
import subprocess
from pathlib import Path

from .model_registry import note_failure

RUST_TOOLS = ("rustc", "cargo", "rustfmt")
GO_TOOLS = ("go", "gofmt")


def detect(path):
    """Language of a source file: 'rust', 'go'. Raises ValueError."""
    suf = Path(path).suffix.lower()
    if suf == ".rs":
        return "rust"
    if suf == ".go":
        return "go"
    raise ValueError("eve langs handles .rs and .go only: %s" % path)


def have_tools(lang):
    """Tool availability: {tool: path or None}."""
    names = RUST_TOOLS if lang == "rust" else GO_TOOLS
    return {t: shutil.which(t) for t in names}


def _run(cmd, timeout=300):
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=timeout)
    except FileNotFoundError as e:
        return 127, "", "tool missing: %s" % e
    except subprocess.TimeoutExpired:
        note_failure("langs:timeout", Exception(str(cmd[:2])))
        return 124, "", "compiler timed out"
    return proc.returncode, proc.stdout, proc.stderr


def check(path):
    """Compile-check one file. Returns {lang, ok, diagnostics}."""
    lang = detect(path)
    if lang == "rust":
        import tempfile
        # rustc cannot emit to NUL (archive rename fails), so emit the
        # throwaway rlib into a temp dir on the same drive instead.
        with tempfile.TemporaryDirectory(prefix="evelang") as tmp:
            out_path = str(Path(tmp) / (Path(path).stem + ".rlib"))
            code, out, err = _run(["rustc", "--edition", "2021",
                                   "--crate-type", "lib", str(path),
                                   "-o", out_path])
        diagnostics = (out + err).strip()
        return {"lang": lang, "ok": code == 0, "diagnostics": diagnostics}
    code, out, err = _run(["go", "vet", str(path)])
    diagnostics = (out + err).strip()
    return {"lang": lang, "ok": code == 0, "diagnostics": diagnostics}


def fmt(path):
    """Format in place with the language's own formatter.

    Backs up to <file>.evelang.bak first. Returns True if bytes changed.
    """
    lang = detect(path)
    p = Path(path)
    bak = p.with_suffix(p.suffix + ".evelang.bak")
    if not bak.exists():
        bak.write_bytes(p.read_bytes())
    before = p.read_bytes()
    if lang == "rust":
        tool = ["rustfmt", "--edition", "2021", str(path)]
    else:
        tool = ["gofmt", "-w", str(path)]
    code, out, err = _run(tool)
    if code != 0:
        note_failure("langs:fmt", Exception((out + err)[:200]))
        raise RuntimeError("formatter failed: %s" % (out + err).strip()[:300])
    return p.read_bytes() != before


def fix(path):
    """Mechanical fix: format, then re-check. Returns the report dict.

    {fixed_by_format, check_before, check_after}. Anything still failing
    after formatting is a semantic bug: reported with diagnostics, not
    guessed at.
    """
    before = check(path)
    changed = fmt(path)
    after = check(path)
    return {"lang": before["lang"], "fixed_by_format": bool(changed),
            "check_before": before, "check_after": after,
            "clean": after["ok"]}
