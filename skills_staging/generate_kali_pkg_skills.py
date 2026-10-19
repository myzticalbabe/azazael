#!/usr/bin/env python3
"""Generate one formal callable skill per installed Python package.

Usage:
  generate_pkg_skills.py [--meta PATH] [--out DIR] [--prefix NAME] [--interp PATH] [pkgname]

Input : metadata JSON from importlib.metadata extraction (default /tmp/pkgs_meta.json)
Output: <out>/<prefix><sname>.md

Each skill is a formal callable skill:
  - YAML frontmatter (name, description, metadata) for skill() loadability
  - Purpose summary
  - Version + install metadata
  - EXECUTE section with real CLI entry points (if any) and Python import
    invocation patterns so an agent can actually call the package
  - Verify command
"""

import argparse
import json
import os
import re

DEFAULT_META = "/tmp/pkgs_meta.json"
DEFAULT_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pkg_skills")


def skill_name(pkg_name: str) -> str:
    """Sanitize a package name into a valid skill name (a-z0-9-)."""
    n = pkg_name.lower().replace("_", "-").replace(".", "-").replace("+", "-plus")
    n = re.sub(r"[^a-z0-9-]+", "-", n).strip("-")
    n = re.sub(r"-{2,}", "-", n)
    return n


def render(pkg: dict, prefix: str, interp: str, interp_label: str, env_label: str) -> str:
    name = pkg["name"]
    version = pkg["version"]
    summary = pkg["summary"] or "No summary available."
    eps = pkg["entry_points"]
    modules = pkg["modules"]
    sname = skill_name(name)

    lines = []
    lines.append("---")
    lines.append(f"name: {prefix}{sname}")
    lines.append(
        "description: "
        f"Callable skill for Python package {name} {version} — {summary}"
    )
    lines.append("metadata:")
    lines.append("  category: packages")
    lines.append("  project: azazael")
    lines.append("  priority: low")
    lines.append("---")
    lines.append("")
    lines.append(f"# {name} {version}")
    lines.append("")
    lines.append(f"> {summary}")
    lines.append("")

    lines.append("## Identity")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("|-------|-------|")
    lines.append(f"| Distribution | `{name}` |")
    lines.append(f"| Version | `{version}` |")
    lines.append(f"| Interpreter | {interp_label} |")
    lines.append("")

    if eps:
        lines.append("## EXECUTE — CLI entry points")
        lines.append("")
        lines.append("The package installs the following console commands (run with `python3.15 -m` or directly):")
        lines.append("")
        for ep in eps[:8]:
            lines.append(f"- `{ep}`")
        if len(eps) > 8:
            lines.append(f"- ... plus {len(eps) - 8} more")
        lines.append("")
        lines.append("Invocation pattern:")
        lines.append("")
        lines.append("```bash")
        lines.append(f"{eps[0]} --help")
        lines.append("```")
        lines.append("")
        if len(eps) > 1:
            lines.append("Alternates:")
            lines.append("")
            lines.append("```bash")
            for ep in eps[1:4]:
                lines.append(f"{ep} --help")
            lines.append("```")
            lines.append("")

    if modules:
        lines.append("## EXECUTE — Python API")
        lines.append("")
        lines.append("Importable top-level module(s):")
        lines.append("")
        for m in modules:
            lines.append(f"- `{m}`")
        lines.append("")
        lines.append("Invocation pattern:")
        lines.append("")
        lines.append("```python")
        lines.append(f"import {modules[0]}")
        lines.append("print(" + f'"{modules[0]} loaded OK"' + ")")
        lines.append("```")
        lines.append("")

    if not eps and not modules:
        lines.append("## Notes")
        lines.append("")
        lines.append("No console entry points or detectable top-level modules; treat as a library dependency.")
        lines.append("")

    lines.append("## Verify")
    lines.append("")
    lines.append("```bash")
    if modules:
        lines.append(f"{interp} -c \"import {modules[0]}; print('{modules[0]} OK')\"")
    else:
        lines.append(f"{interp} -m pip show {name}")
    lines.append("```")
    lines.append("")
    lines.append("## Related")
    lines.append("")
    lines.append(f"- Environment: {env_label}")
    lines.append("- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--meta", default=DEFAULT_META)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--prefix", default="azazael-pkg-")
    ap.add_argument("--interp", default="/usr/bin/python3.13")
    ap.add_argument("--interp-label", default="Python 3.13.12 (`/usr/bin/python3.13`)")
    ap.add_argument("--env-label", default="Kali Python 3.13.12 system packages")
    ap.add_argument("pkgname", nargs="?", default=None)
    args = ap.parse_args()

    with open(args.meta, encoding="utf-8") as f:
        data = json.load(f)
    os.makedirs(args.out, exist_ok=True)
    written = 0
    for pkg in data["packages"]:
        if args.pkgname and pkg["name"].lower() != args.pkgname.lower():
            continue
        sname = skill_name(pkg["name"])
        path = os.path.join(args.out, f"{args.prefix}{sname}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(render(pkg, args.prefix, args.interp, args.interp_label, args.env_label))
        written += 1
    print(f"Wrote {written} skill(s) to {args.out}")


if __name__ == "__main__":
    main()
