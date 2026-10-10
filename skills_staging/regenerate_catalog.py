#!/usr/bin/env python3
"""Regenerate SKILLS_CATALOG.md from the canonical azazael/skills/ directory.

Preserves: header and historical sections after the Quick Reference tables
("New Skills"/"Skills Updated"/etc.) from the existing catalog. Note: no
Loading Order section exists to preserve (absent since the Sep-29 regen; a
curated order would be kept verbatim if re-added — corrected 2026-10-10).
Regenerates: the Skill Quick Reference tables (Core + Package) covering ALL
canonical skills, numbered sequentially.
Appends: a "New Skills - Created 2026-08-23" section for the package batches.
"""

import os
import re
import sys
from pathlib import Path

# Windows port (2026-09-29): resolve from this file's location instead of the
# hardcoded WSL path. Override with AZAZAEL_DIR env var if needed.
AZAZAEL_DIR = Path(
    os.environ.get("AZAZAEL_DIR", Path(__file__).resolve().parent.parent)
)
SKILLS_DIR = AZAZAEL_DIR / "skills"
CATALOG = AZAZAEL_DIR / "SKILLS_CATALOG.md"

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
    "azazael-release-gate": "Process",
    "azazael-secure-push": "Security",
    "azazael-sync-kali": "Infrastructure",
    "azazael-system-wiring": "Neural",
    "azazael-wsl-canonical": "Infrastructure",
}

def make_header(n_core: int, n_kali: int, n_314t: int, n_bin: int) -> str:
    import datetime
    total = n_core + n_kali + n_314t + n_bin
    today = datetime.date.today().isoformat()
    return f"""# AZAZAEL SKILLS CATALOG
# Complete Inventory of Codebuff Skills for the Azazael Project

> Generated: May 29, 2026
> Last Updated: {today} — regenerated from canonical `skills/*.md` ({total:,} skills: core + Kali + 3.14t package + binary-tool)
> Purpose: Single source of truth for all available Azazael skills
> Source of truth: `skills/` (canonical flat .md) mirrored to `.agents/skills/<name>/SKILL.md`. Table rows below are generated, never hand-edited.

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
    # Filename stem is the identity (matches sync dir naming). Three legacy
    # files (azazael_314t_master, azazael_314t_optimum,
    # azazael_insights_2026-05-28) declare dash-form `name:` in frontmatter
    # that matches nothing on disk — stem wins (fixed 2026-09-29).
    stem = Path(path).stem
    m = re.match(r"^---\s*\n(.*?)\n---", raw, re.S)
    info = {
        "name": stem,
        "category": LEGACY_CATEGORIES.get(stem, "?"),
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
    mm = re.search(r"^description:\s*(.+)$", body, re.M)
    if mm:
        info["description"] = mm.group(1).strip()
    mm = re.search(r"^  category:\s*(.+)$", body, re.M)
    if mm:
        info["category"] = mm.group(1).strip()
    return info


def load_skills() -> list:
    out = []
    for f in sorted(os.listdir(SKILLS_DIR)):
        if not f.endswith(".md"):
            continue
        info = frontmatter(str(Path(SKILLS_DIR) / f))
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

    # Preserve historical sections from the CURRENT catalog (which carries the
    # Sep-14 recount notes and Sep-16 reconciliation). Fall back to the
    # pre-regeneration backup only if the catalog itself is missing.
    # Everything after the old Quick Reference section header is kept
    # verbatim; the old table itself is dropped.
    hist = []
    bak = Path(str(CATALOG) + ".bak")
    src = CATALOG if Path(CATALOG).exists() else bak
    old = open(src, encoding="utf-8", errors="replace").read()
    idx = old.find("## Skill Quick Reference")
    if idx != -1:
        rest = old[idx:]
        # Drop ALL old Quick Reference tables (core + Kali + 3.14t + bin),
        # not just the first: split into ## sections and keep every section
        # whose header is not a Quick Reference table. (2026-09-29 fix: the
        # old code kept the 2nd-4th tables as "history", duplicating rows.)
        parts = re.split(r"(?m)^(?=## )", rest)
        kept = [p for p in parts if not p.startswith("## Skill Quick Reference")]
        hist = "\n".join(p.rstrip() for p in kept).strip()

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
    # No appended batch summary: the preserved history below already carries
    # the "New Skills - Created August 23, 2026" batch record. Appending a
    # second copy caused adjacent duplicate sections (fixed 2026-09-29).
    if hist:
        lines.append("---")
        lines.append("")
        lines.append(hist)

    with open(CATALOG, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Wrote {len(skills)} skills to catalog (core {len(core)}, kali {len(pkgs_kali)}, 3.14t {len(pkgs_314t)}, bin {len(bins)})")


if __name__ == "__main__":
    main()
