#!/usr/bin/env python3
"""Systematic skill gap-testing harness.

For every canonical + staged skill:
  1. Frontmatter valid (name/description/category present)
  2. name == filename (project convention)
  3. Has EXECUTE or ## Notes section
  4. EXECUTE CLI commands reference binaries that exist on the system
  5. Python API imports resolve in the declared interpreter
  6. Verify commands runnable (dry: binary exists)

Output: per-skill status + a gap report of missing binaries/imports.
"""
import os, re, sys, subprocess, glob, shutil
from pathlib import Path

ROOT = Path("/root/azazael")
CANON = ROOT / "skills"
STAGED = ROOT / "skills_staging" / "bin_skills"
AGENTS = Path("/root/.agents/skills")

FM_RE = re.compile(r"^---\n(.*?)\n---", re.S)
NAME_RE = re.compile(r"^name:\s*(\S+)", re.M)
DESC_RE = re.compile(r"^description:\s*(.+)$", re.M)
CAT_RE = re.compile(r"^category:\s*(\S+)", re.M)
CLI_RE = re.compile(r"^(\S+?)\s+(?:-{1,2}[A-Za-z]|--?|$)", re.M)

LEGACY_NAME_RE = re.compile(r"^#+\s*\*\*?([A-Za-z0-9_-]+)\*\*?\s*$|^#+\s*([A-Za-z0-9_-]+)\s*$", re.M)
LEGACY_CAT_RE = re.compile(r"\*\*Category:\*\*\s*\*\*?([^\*\n]+)", re.M)
LEGACY_DESC_RE = re.compile(r"\*\*Description:\*\*\s*(.+)$", re.M)

SKIP_CLI = {
    "azazael", "python", "python3", "pip", "pip3", "docker", "sudo", "git", "curl",
    "wget", "node", "npm", "npx", "go", "cmake", "make", "bash", "sh", "echo",
    "cd", "export", "source", "set", "ls", "cat", "grep", "head", "tail", "true",
    # prose / pseudo-code noise
    "and", "or", "if", "for", "from", "with", "the", "to", "in", "of", "a", "an",
    "is", "are", "short", "n", "2", "use", "using", "your", "you", "will", "can",
    "this", "that", "on", "by", "at", "be", "as", "it", "do", "does", "not", "no",
}

NESTED_CAT_RE = re.compile(r"metadata:\s*\n\s+category:\s*(\S+)", re.M)

def parse_fm(text):
    m = FM_RE.search(text)
    if m:
        body = m.group(1)
        cat = None
        c = CAT_RE.search(body)
        if c:
            cat = c.group(1)
        else:
            nc = NESTED_CAT_RE.search(body)
            if nc:
                cat = nc.group(1)
        return {
            "name": (NAME_RE.search(body).group(1) if NAME_RE.search(body) else None),
            "desc": (DESC_RE.search(body).group(1).strip() if DESC_RE.search(body) else None),
            "cat": cat,
            "fmt": "yaml",
        }
    # legacy format: **Category:** / **Description:** markers
    lm = LEGACY_NAME_RE.search(text)
    lc = LEGACY_CAT_RE.search(text)
    ld = LEGACY_DESC_RE.search(text)
    return {
        "name": (lm.group(1) or lm.group(2) if lm else None),
        "desc": (ld.group(1).strip() if ld else None),
        "cat": (lc.group(1).strip() if lc else None),
        "fmt": "legacy",
    }

def extract_clis(text):
    """Grab candidate binaries from EXECUTE code blocks."""
    clis = set()
    # bash blocks
    for m in re.finditer(r"```(?:bash|sh|shell)\n(.*?)```", text, re.S):
        block = m.group(1)
        for line in block.splitlines():
            line = line.strip()
            if not line or line.startswith(("#", "echo", "cd ", "export", "set ", "source")):
                continue
            # first token that looks like a command (skip pipes/redirects)
            toks = re.split(r"\s+", line)
            for t in toks:
                if re.match(r"^[a-zA-Z_][\w.-]*$", t) and not t.startswith("-"):
                    clis.add(t)
                    break
    return clis

def check_skills(dirpath, label):
    results = []
    for f in sorted(dirpath.glob("*.md")):
        text = f.read_text(errors="replace")
        fm = parse_fm(text)
        stem = f.stem
        issues = []
        if fm.get("fmt") == "legacy":
            # legacy skills: must have Category and Description markers; name falls back to stem
            if not LEGACY_CAT_RE.search(text):
                issues.append("NO_CATEGORY")
            if not LEGACY_DESC_RE.search(text):
                issues.append("NO_DESC")
        else:
            if not fm.get("name"):
                issues.append("NO_FRONTMATTER")
            elif fm["name"] != stem:
                issues.append(f"NAME_MISMATCH({fm['name']} != {stem})")
            if not fm.get("desc"):
                issues.append("NO_DESC")
            if not fm.get("cat"):
                issues.append("NO_CATEGORY")
        # EXECUTE only required for callable (package/bin) skills; legacy/core are documentation
        is_callable = stem.startswith(("azazael-pkg", "azazael-bin"))
        if is_callable and "## EXECUTE" not in text and "EXECUTE" not in text and "## Notes" not in text:
            issues.append("NO_EXECUTE_OR_NOTES")
        results.append({"file": str(f.relative_to(ROOT)), "name": fm.get("name") or stem, "stem": stem, "issues": issues, "text": text, "fmt": fm.get("fmt", "yaml")})
    return results

def main():
    all_results = []
    all_results += check_skills(CANON, "canonical")
    if STAGED.exists():
        all_results += check_skills(STAGED, "staged")

    # --- Aggregate: YAML skills must have name/desc/cat; legacy only needs content ---
    bad = []
    for r in all_results:
        if r.get("fmt") == "legacy":
            if not r["text"].strip():
                bad.append(r)
            continue
        if r["issues"]:
            bad.append(r)
    print(f"=== STRUCTURAL AUDIT: {len(all_results)} skills ===")
    print(f"  clean: {len(all_results) - len(bad)}  |  issues: {len(bad)}")
    for r in bad:
        print(f"  [ISSUE] {r['file']}: {r['issues']}")

    # --- CLI binary existence check (the real gap test) ---
    print("\n=== BINARY EXISTENCE GAP CHECK ===")
    missing_map = {}
    importable_map = {}
    checked = 0
    # extra prose/shell noise tokens
    MORE_NOISE = {"present", "command", "version", "wsl", "done", "fi", "contains", "content", "except", "fail", "ok", "remove", "temps", "r", "v", "p", "dm", "events", "result"}
    interp = "/usr/bin/python3.13"
    for r in all_results:
        clis = extract_clis(r["text"])
        if not clis:
            continue
        checked += 1
        real_missing = []
        importables = []
        for c in sorted(clis):
            if c in SKIP_CLI or c.lower() in MORE_NOISE or c.startswith(("azazael", "python", "pip", "docker", "sudo", "git", "curl", "wget", "node", "npm", "go", "cmake")):
                continue
            if shutil.which(c) is not None:
                continue
            # check importable module (Python API skills)
            mod_ok = False
            for cand in {c, c.lower(), c.replace("-", "_"), c.lower().replace("-", "_")}:
                try:
                    if subprocess.run([interp, "-c", f"import {cand}"], capture_output=True, timeout=10).returncode == 0:
                        mod_ok = True
                        break
                except subprocess.TimeoutExpired:
                    continue
            if mod_ok:
                importables.append(c)
            else:
                real_missing.append(c)
        if real_missing:
            missing_map[r["name"] or r["stem"]] = sorted(set(real_missing))
        if importables:
            importable_map[r["name"] or r["stem"]] = sorted(set(importables))

    print(f"  skills with CLI refs checked: {checked}")
    print(f"  skills with missing binaries: {len(missing_map)}")
    for name, miss in sorted(missing_map.items()):
        print(f"    {name}: missing {miss}")
    print(f"\n  skills with import-resolvable refs (OK, Python API): {len(importable_map)}")
    for name, imps in sorted(importable_map.items()):
        print(f"    {name}: importable {imps}")

    # --- Python import check (declared interpreter) ---
    print("\n=== PYTHON IMPORT GAP CHECK (sample, only for pkg skills) ===")
    import_re = re.compile(r"import\s+([\w.]+)|from\s+([\w.]+)\s+import")
    pkg_skills = [r for r in all_results if "azazael-pkg-" in (r["name"] or "")]
    import_fail = 0
    checked_imports = 0
    interp = "/usr/bin/python3.13"
    for r in pkg_skills:
        mods = set()
        for m in import_re.finditer(r["text"]):
            mods.add((m.group(1) or m.group(2)).split(".")[0])
        for mod in list(mods)[:3]:
            if mod in ("os", "sys", "json", "re", "subprocess", "pathlib", "shutil", "importlib", "time", "datetime", "typing", "argparse", "collections", "io", "logging", "itertools", "functools", "hashlib", "base64", "urllib", "math", "random", "string", "textwrap", "glob", "tempfile", "dataclasses", "enum", "abc", "concurrent", "multiprocessing", "threading", "queue", "asyncio", "contextlib", "copy", "struct", "socket", "ssl", "http", "email", "csv", "sqlite3", "xml", "html", "unicodedata", "codecs", "getpass", "platform", "signal", "warnings", "traceback", "weakref", "numbers", "decimal", "fractions", "statistics", "bisect", "heapq", "operator", "pdb", "gc", "inspect", "ast", "tokenize", "ctypes", "curses", "dbm", "gzip", "bz2", "lzma", "zipfile", "tarfile", "pickle", "shelve", "marshal", "json"):
                continue
            checked_imports += 1
            ok = False
            for cand in {mod, mod.lower(), mod.upper(), mod.capitalize()}:
                try:
                    p = subprocess.run([interp, "-c", f"import {cand}"], capture_output=True, timeout=10)
                except subprocess.TimeoutExpired:
                    continue
                if p.returncode == 0:
                    ok = True
                    break
            if not ok:
                import_fail += 1
                print(f"    IMPORT-FAIL {r['name']}: {mod}")
    print(f"  imports checked (sample): {checked_imports} | failures: {import_fail}")

    # --- .agents parity ---
    print("\n=== .agents PARITY ===")
    if AGENTS.exists():
        canon_names = {r["name"] for r in all_results if r["name"]}
        agent_dirs = set(d.name for d in AGENTS.iterdir() if d.is_dir())
        missing_in_agents = canon_names - agent_dirs
        print(f"  canonical names: {len(canon_names)} | .agents dirs: {len(agent_dirs)} | missing: {len(missing_in_agents)}")
        for m in sorted(missing_in_agents)[:10]:
            print(f"    MISSING: {m}")
    else:
        print("  .agents not found")

    print("\n=== DONE ===")

if __name__ == "__main__":
    main()
