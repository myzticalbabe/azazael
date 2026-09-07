#!/usr/bin/env python3
"""Regenerate SKILLS_CATALOG.md from the canonical azazael/skills/ directory.

Preserves: header, curated Loading Order, historical "New Skills"/"Skills Updated"
sections from the existing catalog.
Regenerates: the Skill Quick Reference tables (Core + Package) covering ALL
canonical skills, numbered sequentially.
Appends: a "New Skills - Created 2026-08-23" section for the package batches.
"""

import os
import re
import sys

AZAZAEL_DIR = "/root/azazael"
SKILLS_DIR = os.path.join(AZAZAEL_DIR, "skills")
CATALOG = os.path.join(AZAZAEL_DIR, "SKILLS_CATALOG.md")

# Curated categories for legacy-format skills that lack frontmatter category,
# sourced from the pre-regeneration catalog (June 2026 edition).
LEGACY_CATEGORIES = {
    "azazael-6api-analysis": "Neural",
    "azazael-codex-studio": "Specialized",
    "azazael-codex-video": "Specialized",
    "azazael-curative": "Architecture",
    "azazael-eve-unleashed": "Specialized",
    "azazael-evolutionary-optimization": "Neural",
    "azazael-gemini-injection": "Gemini",
    "azazael-gemini-mandate": "Gemini",
    "azazael-gemini-protocol": "Gemini",
    "azazael-inference-providers": "Neural",
    "azazael-mypy-fix-patterns": "Quality",
    "azazael-no-permission-language": "Process",
    "azazael-nsga2-testing": "Neural",
    "azazael-packaging": "Deployment",
    "azazael-platform-deploy": "Deployment",
    "azazael-python3.14-ml": "Neural",
    "azazael-standalone": "Deployment",
    "azazael-standalone-audit": "Deployment",
    "azazael-sync-kali": "Infrastructure",
    "azazael-system-wiring": "Neural",
    "azazael-wsl-canonical": "Infrastructure",
}

def make_header(n_core: int, n_kali: int, n_314t: int, n_bin: int) -> str:
    total = n_core + n_kali + n_314t + n_bin
    return f"""# AZAZAEL SKILLS CATALOG
# Complete Inventory of Codebuff Skills for the Azazael Project

> Generated: May 29, 2026
> Last Updated: August 23, 2026 — regenerated to inventory ALL {total:,} canonical skills (core + Kali + 3.14t package + binary-tool skills)
> Purpose: Single source of truth for all available Azazael skills

---

## Inventory Summary

| Metric | Count |
|--------|-------|
| Total canonical skills | {total:,} |
| Core skills (non-package) | {n_core} |
| Package skills (Kali 3.13 env, `azazael-pkg-*`) | {n_kali} |
| Package skills (Azazael 3.14t env, `azazael-pkg314t-*`) | {n_314t} |
| Binary-tool skills (`azazael-bin-*`) | {n_bin} |

---"""


def frontmatter(path: str) -> dict:
    raw = open(path, encoding="utf-8", errors="replace").read()
    m = re.match(r"^---\s*\n(.*?)\n---", raw, re.S)
    info = {
        "name": os.path.basename(path)[:-3],
        "category": LEGACY_CATEGORIES.get(os.path.basename(path)[:-3], "?"),
        "description": "",
    }
    if not m:
        # Legacy format: filename stem is the name (matches sync dir naming);
        # parse category/description from content lines.
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        for l in lines:
            if l.startswith("# "):
                continue
            if l.startswith("**Category:**"):
                info["category"] = l.split(":", 1)[1].strip().strip("*").strip()
            elif l.startswith("**Priority:") or l.startswith(">") \
                    or l.startswith("**Dependencies:") or l.startswith("**Description:"):
                if l.startswith("**Description:"):
                    info["description"] = l.split(":", 1)[1].strip()[:160]
                continue
            elif not info["description"]:
                info["description"] = l[:160]
                break
        return info
    body = m.group(1)
    for key in ("name", "description"):
        mm = re.search(rf"^{key}:\s*(.+)$", body, re.M)
        if mm:
            info[key] = mm.group(1).strip()
    mm = re.search(r"^  category:\s*(.+)$", body, re.M)
    if mm:
        info["category"] = mm.group(1).strip()
    return info


def load_skills() -> list:
    out = []
    for f in sorted(os.listdir(SKILLS_DIR)):
        if not f.endswith(".md"):
            continue
        info = frontmatter(os.path.join(SKILLS_DIR, f))
        out.append(info)
    return out


def short(desc: str, limit: int = 110) -> str:
    desc = desc.replace("|", "/").strip()
    return desc if len(desc) <= limit else desc[: limit - 3] + "..."


def build_table(skills: list, start_num: int) -> tuple:
    lines = ["| # | Skill | Category | Description |", "|---|-------|----------|-------------|"]
    for i, s in enumerate(skills, start=start_num):
        lines.append(f"| {i} | `{s['name']}` | {s['category']} | {short(s['description'])} |")
    return lines, start_num + len(skills)


def main() -> None:
    skills = load_skills()
    core = sorted(
        (s for s in skills if not s["name"].startswith(("azazael-pkg", "azazael-bin-"))),
        key=lambda s: (s["category"], s["name"]),
    )
    pkgs_kali = sorted(
        (s for s in skills if s["name"].startswith("azazael-pkg-") and not s["name"].startswith("azazael-pkg314t-")),
        key=lambda s: s["name"],
    )
    pkgs_314t = sorted(
        (s for s in skills if s["name"].startswith("azazael-pkg314t-")),
        key=lambda s: s["name"],
    )
    bins = sorted(
        (s for s in skills if s["name"].startswith("azazael-bin-")),
        key=lambda s: s["name"],
    )

    # Preserve historical sections from the ORIGINAL pre-regeneration catalog
    # (SKILLS_CATALOG.md.bak). Everything after the old Quick Reference section
    # header is kept verbatim; the old table itself is dropped.
    hist = []
    bak = CATALOG + ".bak"
    src = bak if os.path.exists(bak) else CATALOG
    old = open(src, encoding="utf-8", errors="replace").read()
    idx = old.find("## Skill Quick Reference")
    if idx != -1:
        rest = old[idx:]
        # drop the old table: from "## Skill Quick Reference" to the next "## "
        nxt = rest.find("\n## ", 10)
        if nxt != -1:
            hist = rest[nxt:].strip()

    lines = []
    lines.append(make_header(len(core), len(pkgs_kali), len(pkgs_314t), len(bins)))
    lines.append("")
    lines.append(f"## Skill Quick Reference — Core Skills (1-{len(core)})")
    tbl, n = build_table(core, 1)
    lines.extend(tbl)
    lines.append("")
    lines.append(f"## Skill Quick Reference — Kali Package Skills ({n}-{n + len(pkgs_kali) - 1})")
    tbl, n = build_table(pkgs_kali, n)
    lines.extend(tbl)
    lines.append("")
    lines.append(f"## Skill Quick Reference — 3.14t Package Skills ({n}-{n + len(pkgs_314t) - 1})")
    tbl, n = build_table(pkgs_314t, n)
    lines.extend(tbl)
    lines.append("")
    lines.append(f"## Skill Quick Reference — Binary Tool Skills ({n}-{n + len(bins) - 1})")
    tbl, n = build_table(bins, n)
    lines.extend(tbl)
    lines.append("")
    lines.append("## New Skills — Created August 23, 2026")
    lines.append("")
    lines.append("| Skill | Path | Purpose | Priority |")
    lines.append("|-------|------|---------|----------|")
    lines.append(f"| `azazael-pkg-*` ({len(pkgs_kali)}) | `skills/azazael-pkg-*.md` | Callable skills for Kali Python 3.13.12 system packages — CLI entry points + Python API invocation patterns. Generated from `importlib.metadata` (see `skills_staging/generate_kali_pkg_skills.py`). | Merged |")
    lines.append(f"| `azazael-pkg314t-*` ({len(pkgs_314t)}) | `skills/azazael-pkg314t-*.md` | Callable skills for the Azazael Python 3.14.6 (3.14t) environment — CLI entry points + Python API invocation patterns. Generated from `importlib.metadata` (see `skills_staging/generate_kali_pkg_skills.py`). | Merged |")
    lines.append(f"| `azazael-bin-*` ({len(bins)}) | `skills/azazael-bin-*.md` | Callable skills for binary/CLI tools (Kali binaries + OSINT + AI/ML) — canonical invocations with live version/status. Generated from `skills_staging/binary_manifest.py` + `generate_bin_skills.py`. | Merged |")
    lines.append("")
    if hist:
        lines.append("---")
        lines.append("")
        lines.append(hist)

    with open(CATALOG, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Wrote {len(skills)} skills to catalog (core {len(core)}, kali {len(pkgs_kali)}, 3.14t {len(pkgs_314t)}, bin {len(bins)})")


if __name__ == "__main__":
    main()
