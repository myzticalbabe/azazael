#!/usr/bin/env python3
"""Render this tree's Markdown into a static site for GitHub Pages.

Deliberately self-contained. The earlier draft of ``pages-deploy.yml`` called
``tools/publicize.py``, ``mkdocs.yml`` and ``pyproject.toml``, and none of those
files existed in any of the eight publication roots -- so that workflow could
not have run in any of them. This script needs only ``README.md``, which every
publication root is already required to ship, plus the ``markdown`` package the
workflow installs.

Nothing is published that is not listed in PAGES: a landing site is not a file
server, and the governance tree is already public in the repository itself.
"""

from __future__ import annotations

import pathlib
import re
import sys

try:
    import markdown
except ImportError:  # pragma: no cover - the workflow installs it
    sys.exit("render_site: the `markdown` package is required (pip install markdown)")

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "_site"

# Ordered: the first entry is the landing page. Missing files are skipped, so a
# tree that has not written a HARDWARE.md yet still publishes cleanly.
PAGES = (
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    "DISCLOSURE_POLICY.md",
    "HARDWARE.md",
    "MANIFEST_NOTES.md",
)

STYLE = """
:root { color-scheme: light dark; --ink:#1b1b1f; --dim:#5b5b66; --rule:#d9d9e0; --paper:#ffffff; --accent:#8a2b06; }
@media (prefers-color-scheme: dark) { :root { --ink:#e8e8ee; --dim:#a0a0ad; --rule:#33333d; --paper:#141418; --accent:#ff9a6b; } }
* { box-sizing: border-box; }
body { margin:0; background:var(--paper); color:var(--ink);
       font:16px/1.65 ui-serif, Georgia, "Times New Roman", serif; }
header { border-bottom:1px solid var(--rule); padding:1.25rem 1.5rem; }
header nav { max-width:52rem; margin:0 auto; display:flex; flex-wrap:wrap; gap:.35rem 1rem;
             font:14px/1.4 ui-sans-serif, system-ui, sans-serif; }
header a { color:var(--dim); text-decoration:none; }
header a:hover, header a[aria-current="page"] { color:var(--accent); }
main { max-width:52rem; margin:0 auto; padding:2.5rem 1.5rem 5rem; }
h1, h2, h3 { line-height:1.25; }
h1 { font-size:1.9rem; }
h2 { margin-top:2.5rem; border-bottom:1px solid var(--rule); padding-bottom:.35rem; }
a { color:var(--accent); }
code, pre { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size:.9em; }
pre { overflow-x:auto; padding:.9rem 1rem; border:1px solid var(--rule); border-radius:6px; }
table { border-collapse:collapse; width:100%; display:block; overflow-x:auto; }
th, td { border:1px solid var(--rule); padding:.45rem .7rem; text-align:left; }
th { font:600 13px/1.4 ui-sans-serif, system-ui, sans-serif; }
footer { border-top:1px solid var(--rule); padding:1.5rem; color:var(--dim);
         font:13px/1.5 ui-sans-serif, system-ui, sans-serif; text-align:center; }
"""


def slug(name: str) -> str:
    stem = pathlib.Path(name).stem
    return "index.html" if name == "README.md" else re.sub(r"[^a-z0-9]+", "-", stem.lower()).strip("-") + ".html"


def title_of(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def page(label: str, body: str, nav: str) -> str:
    return (
        "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{label}</title>\n<style>{STYLE}</style>\n</head>\n<body>\n"
        f"<header><nav>{nav}</nav></header>\n<main>\n{body}\n</main>\n"
        f"<footer>{label} &middot; Soul Forge License v1.0</footer>\n</body>\n</html>\n"
    )


def main() -> int:
    sources = [(name, ROOT / name) for name in PAGES]
    present = [(name, path) for name, path in sources if path.is_file()]
    if not any(name == "README.md" for name, _ in present):
        sys.exit("render_site: no README.md to publish; every publication root must ship one")

    OUT.mkdir(parents=True, exist_ok=True)
    entries = []
    for name, path in present:
        text = path.read_text(encoding="utf-8", errors="replace")
        entries.append((name, slug(name), title_of(text, name), text))

    for name, href, label, text in entries:
        this_nav = "".join(
            f'<a href="{h}" aria-current="page">{lab}</a>'
            if h == href
            else f'<a href="{h}">{lab}</a>'
            for _, h, lab, _ in entries
        )
        body = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])
        (OUT / href).write_text(page(label, body, this_nav), encoding="utf-8")

    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    print(f"render_site: {len(entries)} page(s) -> {OUT}")
    for name, href, _, _ in entries:
        print(f"  {name} -> {href}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
