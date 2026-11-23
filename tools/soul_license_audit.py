#!/usr/bin/env python3
"""Forensic license audit and Soul Forge License v1.0 migration.

Policy (set 2026-11-15): every active tree in this repository declares exactly
one license -- the Soul Forge License v1.0. Every other license reference that
applies to first-party code is a defect and is rewritten.

What counts as a tree
    the repository root plus every ``Project_*`` directory.

What is migrated
    LICENSE                byte-identical copy of the canonical SOUL text
    CITATION.cff           ``license:`` field
    CONTRIBUTING.md        contribution-license clauses
    pyproject.toml         ``license = { text = ... }``
    PUBLIC_MANIFEST.json   ``"license"`` value
    NOTICE                 license block, maker's mark, wrong-tree contamination
    README.md              the ``## License`` section

What is NOT relicensed (reported under ``exempt``)
    Third-party material keeps its own license. Relicensing someone else's code
    would be a false statement, so dependency lock files, vendored sources and
    the Contributor Covenant text are left as they are and named in NOTICE.

Usage
    python tools/soul_license_audit.py --audit
    python tools/soul_license_audit.py --apply
    python tools/soul_license_audit.py --audit --json

Exit codes
    0  audit clean / migration applied
    1  audit found defects (audit mode only)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ── canonical license ────────────────────────────────────────────────────────

LICENSE_NAME = "Soul Forge License v1.0"
LICENSE_AUTHOR = "myzticalbabe"
LICENSE_FORGED = "2026-11-14"
LICENSE_SPIRIT = "Code is crystallized intention. Tend the fire."
LICENSE_SOURCE = "https://github.com/myzticalbabe/{repo}"

MAKERS_MARK = (
    f"    {LICENSE_NAME}\n"
    f"    Author: {LICENSE_AUTHOR}\n"
    f"    Forged: {LICENSE_FORGED}\n"
    f"    Source: {LICENSE_SOURCE}\n"
    f'    Spirit: "{LICENSE_SPIRIT}"\n'
)

# Tokens that mean a first-party artifact is claiming some other license.
FOREIGN_LICENSE_TOKENS = (
    "CDDL",
    "COMMON DEVELOPMENT AND DISTRIBUTION",
    "Apache-2.0",
    "Apache License",
    "apache.org/licenses",
)

# The one third-party text this tree actually ships, with its true license.
COC_THIRD_PARTY_LINE = (
    "Third-party text\n"
    "The Code of Conduct in CODE_OF_CONDUCT.md is adapted from the Contributor\n"
    "Covenant v2.1 (https://www.contributor-covenant.org) and is used under\n"
    "CC BY 4.0 with attribution retained in that file. That text is third-party\n"
    "material; it is not relicensed here and it does not govern this project.\n"
)

# Paragraphs that only describe Project_Nurse_Ratchet. When found in another
# tree's NOTICE they are false statements and are removed.
NR_ONLY_MARKERS = (
    "Nurse Ratchet refers to the character",
    "ELIZA is a SEPARATE project",
    "crisis resources named in",
    "triage_corpus.jsonl",
    "No third-party runtime dependency is bundled",
)


# ── text helpers ─────────────────────────────────────────────────────────────


def read_text(path: Path) -> str:
    """Read preserving the file's own bytes as text (no newline translation)."""
    with open(path, "r", encoding="utf-8", newline="") as fh:
        return fh.read()


def read_text_opt(path: Path) -> str | None:
    """Read a prose file, or None when it is not UTF-8 (left untouched)."""
    try:
        return read_text(path)
    except UnicodeDecodeError as exc:
        print(f"  [SKIP] {path.name}: not UTF-8 ({exc}); left untouched", file=sys.stderr)
        return None


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def eol_of(text: str) -> str:
    return "\r\n" if "\r\n" in text else "\n"


def to_eol(text: str, eol: str) -> str:
    """Normalise a block we generated to the target file's line ending."""
    text = text.replace("\r\n", "\n")
    if eol == "\r\n":
        return text.replace("\n", "\r\n")
    return text


def repo_name(tree: Path, root: Path) -> str:
    return "azazael" if tree == root else tree.name


def display_name(tree: Path) -> str:
    name = tree.name
    if name.startswith("Project_"):
        name = name[len("Project_") :]
    return name.replace("_", " ")


# ── license block generators ─────────────────────────────────────────────────


def license_section(repo: str) -> str:
    mark = MAKERS_MARK.format(repo=repo)
    return (
        "## License\n"
        "\n"
        f"This project is licensed under the **{LICENSE_NAME}** — a covenant, not a\n"
        "contract. The full text is in [LICENSE](LICENSE).\n"
        "\n"
        "You may use, copy, modify, merge, publish, distribute, sublicense and/or\n"
        "sell copies of the software, provided you keep the maker's mark intact,\n"
        "do not wrap the code in DRM or obfuscation, and return your modifications\n"
        "under this same license.\n"
        "\n"
        "```\n" + mark + "```\n"
        "\n"
        f"Author: {LICENSE_AUTHOR} · Forged: {LICENSE_FORGED} · "
        f"Spirit: \"{LICENSE_SPIRIT}\"\n"
    )


def notice_template(tree: Path, root: Path) -> str:
    name = display_name(tree)
    repo = repo_name(tree, root)
    mark = MAKERS_MARK.format(repo=repo)
    return (
        f"{name}\n"
        f"Copyright 2026 the {name} contributors\n"
        "\n"
        f"This product is licensed under the {LICENSE_NAME}. You may not use the\n"
        "files in this project except in covenant with that license. A copy of the\n"
        "license is in the file LICENSE.\n"
        "\n"
        f"{mark}"
        "\n"
        "The soul knows its smith: this notice, the author's name and the forge\n"
        "date remain intact in every copy, every derivative and every deployment.\n"
        "\n"
        "--------------------------------------------------------------------------\n"
        "\n"
        f"{COC_THIRD_PARTY_LINE}"
    )


def replace_license_block(notice: str, repo: str) -> str:
    """Swap a CDDL license block inside a NOTICE for the Soul Forge block."""
    eol = eol_of(notice)
    start = re.search(
        r"^.*(?:This product is licensed under the Common Development|"
        r"Licensed under the Common Development|"
        r"This product is licensed under the Apache).*$",
        notice,
        re.MULTILINE,
    )
    if not start:
        return notice
    # the block ends at the warranty paragraph that closes with "limitations under the License."
    end = re.search(
        r"^.*limitations under the License\.\s*$", notice[start.start() :], re.MULTILINE
    )
    if not end:
        return notice
    stop = start.start() + end.end()
    block = (
        f"This product is licensed under the {LICENSE_NAME}. You may not use the "
        f"files in this project except in covenant with that license. A copy of the "
        f"license is in the file LICENSE.\n"
        "\n"
        + MAKERS_MARK.format(repo=repo)
        + "\n"
        "The soul knows its smith: this notice, the author's name and the forge "
        "date remain intact in every copy, every derivative and every deployment.\n"
    )
    return notice[: start.start()] + to_eol(block, eol) + notice[stop:]


def strip_foreign_notice_paragraphs(notice: str, tree: Path) -> str:
    """Remove Nurse Ratchet-only claims from another tree's NOTICE."""
    if tree.name == "Project_Nurse_Ratchet":
        return notice
    eol = eol_of(notice)
    paras = notice.split(eol + eol)
    kept = [
        p
        for p in paras
        if not any(marker in p for marker in NR_ONLY_MARKERS)
        and "Copyright 2026 the Project Nurse Ratchet contributors" not in p
        and p.strip() != "Project Nurse Ratchet"
    ]
    out = (eol + eol).join(kept)
    # repair a leading blank line left by a removed paragraph
    while out.startswith(eol):
        out = out[len(eol) :]
    return out


def fix_coc_line(notice: str) -> str:
    """Scope the Code of Conduct attribution as third-party text."""
    eol = eol_of(notice)
    pattern = re.compile(
        r"The Contributor Covenant text in\s*\n?CODE_OF_CONDUCT\.md is used under CC BY 4\.0 "
        r"with attribution retained in the\s*\n?Attribution section at the end of that file\.",
        re.MULTILINE,
    )
    if pattern.search(notice):
        return pattern.sub(to_eol(COC_THIRD_PARTY_LINE.rstrip("\n"), eol), notice)
    return notice


# ── audit ────────────────────────────────────────────────────────────────────


def _same_text(a: bytes, b: bytes) -> bool:
    """Compare two texts by content, ignoring how they were checked out.

    The canonical text is measured with LF endings. A clone on a machine with
    `core.autocrlf = true` (or a `* text=auto` attribute) writes every line as
    CRLF, so a byte comparison against the canonical file failed for all 38
    trees on a fresh checkout -- the gate passed in the working tree that
    created the files and failed everywhere else. Line endings are checkout
    detail, not licence content, so they are normalised before comparing.
    """
    return a.replace(b"\r\n", b"\n") == b.replace(b"\r\n", b"\n")


def trees(root: Path) -> list[Path]:
    found = [root]
    found.extend(sorted(p for p in root.glob("Project_*") if p.is_dir()))
    return found


def scan_tree(tree: Path, root: Path) -> dict:
    """Report every license-bearing artifact in one tree."""
    row: dict = {
        "tree": "." if tree == root else tree.name,
        "license_file": (tree / "LICENSE").exists(),
        "license_is_soul": False,
        "defects": [],
    }
    lic = tree / "LICENSE"
    if lic.exists():
        row["license_is_soul"] = canonical is not None and _same_text(
            lic.read_bytes(), canonical
        )

    def cite(rel: str) -> None:
        row["defects"].append(rel)

    if not lic.exists():
        cite("LICENSE missing")
    elif not row["license_is_soul"]:
        cite("LICENSE is not the Soul Forge text")

    citation = tree / "CITATION.cff"
    if citation.exists() and LICENSE_NAME not in read_text(citation):
        cite("CITATION.cff declares another license")

    for name in ("CONTRIBUTING.md",):
        p = tree / name
        if p.exists():
            txt = read_text(p)
            if any(tok in txt for tok in FOREIGN_LICENSE_TOKENS):
                cite(f"{name} declares another license")

    pyproject = tree / "pyproject.toml"
    if pyproject.exists():
        txt = read_text(pyproject)
        if re.search(r"^license\s*=", txt, re.MULTILINE) and LICENSE_NAME not in txt:
            cite("pyproject.toml declares another license")

    manifest = tree / "PUBLIC_MANIFEST.json"
    if manifest.exists():
        txt = read_text(manifest)
        if '"license"' in txt and LICENSE_NAME not in txt:
            cite("PUBLIC_MANIFEST.json declares another license")

    notice = tree / "NOTICE"
    if notice.exists():
        txt = read_text(notice)
        if any(tok in txt for tok in FOREIGN_LICENSE_TOKENS):
            cite("NOTICE declares another license")
        if tree.name != "Project_Nurse_Ratchet" and any(
            m in txt for m in NR_ONLY_MARKERS
        ):
            cite("NOTICE carries another tree's attribution claims")

    readme = tree / "README.md"
    if readme.exists():
        txt = read_text(readme)
        if any(tok in txt for tok in FOREIGN_LICENSE_TOKENS):
            cite("README.md declares another license")
        if not re.search(r"^## License\s*$", txt, re.MULTILINE):
            cite("README.md has no ## License section")
    else:
        cite("README.md missing")

    return row


canonical: bytes | None = None


# ── migration ────────────────────────────────────────────────────────────────


def migrate_tree(tree: Path, root: Path, doc: bytes, log: list[str]) -> None:
    rel = "." if tree == root else tree.name

    # 1. LICENSE -- byte-identical canonical text
    lic = tree / "LICENSE"
    if not lic.exists() or lic.read_bytes() != doc:
        lic.write_bytes(doc)
        log.append(f"{rel}/LICENSE <= SOUL")

    # 2. CITATION.cff
    citation = tree / "CITATION.cff"
    if citation.exists():
        txt = read_text(citation)
        eol = eol_of(txt)
        new, n = re.subn(
            r'^license:.*$',
            f'license: "{LICENSE_NAME}"',
            txt,
            count=0,
            flags=re.MULTILINE,
        )
        if n and new != txt:
            write_text(citation, new)
            log.append(f"{rel}/CITATION.cff license -> {LICENSE_NAME}")

    # 3. CONTRIBUTING.md
    contrib = tree / "CONTRIBUTING.md"
    if contrib.exists():
        txt = read_text(contrib)
        new = txt
        new = re.sub(
            r"- \*\*License\*\*: All contributions must be compatible with "
            r"[^\r\n]*",
            f"- **License**: All contributions are made under the {LICENSE_NAME} "
            f"(see `LICENSE`)",
            new,
        )
        new = re.sub(
            r"By contributing, you agree that your contributions will be licensed under [^\r\n.]*\.",
            f"By contributing, you agree that your contributions are offered back "
            f"under the {LICENSE_NAME}, as VOW III of that covenant requires.",
            new,
        )
        if new != txt:
            write_text(contrib, new)
            log.append(f"{rel}/CONTRIBUTING.md license clause -> SOUL")

    # 4. pyproject.toml
    pyproject = tree / "pyproject.toml"
    if pyproject.exists():
        txt = read_text(pyproject)
        new, n = re.subn(
            r'^license\s*=\s*\{[^}]*\}\s*$',
            f'license = {{ text = "{LICENSE_NAME}" }}',
            txt,
            flags=re.MULTILINE,
        )
        new, m = re.subn(
            r'^license\s*=\s*"[^"]*"\s*$',
            f'license = "{LICENSE_NAME}"',
            new,
            flags=re.MULTILINE,
        )
        if (n or m) and new != txt:
            write_text(pyproject, new)
            log.append(f"{rel}/pyproject.toml license -> {LICENSE_NAME}")

    # 5. PUBLIC_MANIFEST.json
    manifest = tree / "PUBLIC_MANIFEST.json"
    if manifest.exists():
        txt = read_text(manifest)
        new, n = re.subn(
            r'"license":\s*"[^"]*"',
            f'"license": "{LICENSE_NAME}"',
            txt,
            count=1,
        )
        if n and new != txt:
            write_text(manifest, new)
            log.append(f"{rel}/PUBLIC_MANIFEST.json license -> {LICENSE_NAME}")

    # 6. NOTICE
    notice = tree / "NOTICE"
    if notice.exists():
        txt = read_text(notice)
        new = replace_license_block(txt, repo_name(tree, root))
        new = strip_foreign_notice_paragraphs(new, tree)
        new = fix_coc_line(new)
        # an unformatted placeholder or a duplicated mark is a defect
        new = re.sub(
            r"Source: https://github\.com/myzticalbabe/\{repo\}",
            f"Source: https://github.com/myzticalbabe/{repo_name(tree, root)}",
            new,
        )
        if LICENSE_NAME not in new:
            new = notice_template(tree, root)
        else:
            marks = list(re.finditer(r"^    Soul Forge License v1\.0\s*$", new, re.MULTILINE))
            if not marks:
                eol = eol_of(new)
                mark = to_eol(MAKERS_MARK.format(repo=repo_name(tree, root)), eol)
                head, sep, tail = new.partition("--------------------------------------------------------------------------")
                new = head + mark + sep + tail if sep else head + mark
            elif len(marks) > 1:
                eol = eol_of(new)
                for m in reversed(marks[1:]):
                    block_end = m.start() + len(m.group(0)) + 5 * len(eol)
                    new = new[: m.start()] + new[block_end:]
        if new != txt:
            write_text(notice, new)
            log.append(f"{rel}/NOTICE -> SOUL")

    # 7. README.md -- one ## License section, Soul Forge text
    readme = tree / "README.md"
    body = license_section(repo_name(tree, root))
    if readme.exists():
        txt = read_text(readme)
        eol = eol_of(txt)
        block = to_eol(body, eol)
        match = re.search(r"^## License\s*$", txt, re.MULTILINE)
        if match:
            nxt = re.search(r"^## ", txt[match.end() :], re.MULTILINE)
            stop = match.end() + nxt.start() if nxt else len(txt)
            new = txt[: match.start()] + block + (eol if stop < len(txt) else "") + txt[stop:]
        else:
            new = txt.rstrip("\r\n") + eol + eol + block
        if new != txt:
            write_text(readme, new)
            log.append(f"{rel}/README.md ## License -> SOUL")
    else:
        title = display_name(tree)
        abstract = ""
        if citation.exists():
            abstract = citation_abstract(read_text(citation))
        head = (
            f"# {title}\n"
            "\n"
            f"{abstract}\n"
            "\n" if abstract else f"# {title}\n\n"
        )
        write_text(readme, to_eol(head, "\n") + body)
        log.append(f"{rel}/README.md created with ## License")

    # 8. NOTICE for trees that never had one
    if not notice.exists():
        write_text(notice, notice_template(tree, root))
        log.append(f"{rel}/NOTICE created")

    # 9. sweep first-party prose for stale license claims
    for path in first_party_texts(tree):
        txt = read_text_opt(path)
        if txt is None:
            continue
        new = sweep_claims(txt, repo_name(tree, root))
        if new != txt:
            write_text(path, new)
            log.append(f"{rel}/{path.relative_to(tree).as_posix()} claims -> SOUL")


SWEEP_DIRS = {"", "docs", "grimorie", "data", "src"}
SKIP_DIRS = {"adopted", "node_modules", "third_party", "vendor", "external", ".git"}
SWEEP_SUFFIXES = {".md", ".cff", ".toml", ".json", ".txt"}


def first_party_texts(tree: Path):
    """Prose files that describe this tree, excluding vendored material."""
    for path in sorted(tree.rglob("*")):
        if not path.is_file():
            continue
        if path.name != "NOTICE" and path.suffix.lower() not in SWEEP_SUFFIXES:
            continue
        rel_parts = path.relative_to(tree).parts
        if any(part in SKIP_DIRS for part in rel_parts[:-1]):
            continue
        if len(rel_parts) > 2 and rel_parts[0] not in SWEEP_DIRS:
            continue
        if path.name in {"LICENSE", "package-lock.json"}:
            continue
        yield path


def sweep_claims(text: str, repo: str) -> str:
    """Rewrite stale first-party license claims to the Soul Forge wording."""
    out = text
    out = re.sub(
        r"Licensed CDDL-1\.1; see `NOTICE` for attribution\.",
        f"Licensed under the {LICENSE_NAME}; see `NOTICE` for attribution.",
        out,
    )
    out = re.sub(
        r"^License ruling: commit .*$",
        f"The {LICENSE_NAME} governs every tree; see `LICENSE` and `NOTICE`.",
        out,
        flags=re.MULTILINE,
    )
    out = re.sub(
        r"licensed under the same CDDL-1\.1 ruling \(commit [0-9a-f]+\)",
        f"licensed under the same {LICENSE_NAME}",
        out,
    )
    out = re.sub(
        r"the full, unmodified CDDL-1\.1 text in (?:its|the) (?:own )?LICENSE",
        f"the full, unmodified {LICENSE_NAME} text in its own LICENSE",
        out,
    )
    out = out.replace("CDDL-1.1", LICENSE_NAME)
    out = out.replace(
        "the Common Development and Distribution License (CDDL), Version 1.1", LICENSE_NAME
    )
    out = out.replace('"license": "Apache-2.0"', f'"license": "{LICENSE_NAME}"')
    return out


def citation_abstract(text: str) -> str:
    """Pull the abstract out of a CITATION.cff, folded and plain."""
    match = re.search(r"^abstract:\s*>-?\s*\n((?:[ \t]+.*\n?)+)", text, re.MULTILINE)
    if not match:
        return ""
    lines = [l.strip() for l in match.group(1).splitlines()]
    return " ".join(l for l in lines if l).strip()


# ── main ─────────────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    global canonical
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="repository root")
    parser.add_argument(
        "--license",
        default=None,
        help="path to the canonical SOUL license text "
        "(default: $SOUL_LICENSE, then C:/Users/clint/SOUL_LICENSE)",
    )
    parser.add_argument("--audit", action="store_true", help="report only (default)")
    parser.add_argument("--apply", action="store_true", help="rewrite defects")
    parser.add_argument("--json", action="store_true", help="machine-readable report")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    src = args.license
    if not src:
        import os

        src = os.environ.get("SOUL_LICENSE") or "C:/Users/clint/SOUL_LICENSE"
    src_path = Path(src)
    if not src_path.exists():
        print(f"error: canonical license not found: {src_path}", file=sys.stderr)
        return 2
    canonical = src_path.read_bytes()

    rows = [scan_tree(t, root) for t in trees(root)]
    total_defects = sum(len(r["defects"]) for r in rows)

    if args.apply:
        log: list[str] = []
        for t in trees(root):
            migrate_tree(t, root, canonical, log)
        rows = [scan_tree(t, root) for t in trees(root)]
        total_defects = sum(len(r["defects"]) for r in rows)
        if args.json:
            print(json.dumps({"changes": log, "after": rows}, indent=2))
        else:
            print(f"applied {len(log)} rewrites")
            for line in log:
                print(f"  {line}")
            print()
            report(rows)
        return 0 if total_defects == 0 else 1

    if args.json:
        print(json.dumps({"trees": rows, "defects": total_defects}, indent=2))
    else:
        report(rows)
    return 0 if total_defects == 0 else 1


def report(rows: list[dict]) -> None:
    print(f"{'TREE':<36} {'LIC':<4} {'SOUL':<5} DEFECTS")
    print("-" * 78)
    for r in rows:
        lic = "y" if r["license_file"] else "-"
        soul = "y" if r["license_is_soul"] else "-"
        print(f"{r['tree']:<36} {lic:<4} {soul:<5} {len(r['defects'])}")
        for d in r["defects"]:
            print(f"    - {d}")
    bad = [r for r in rows if r["defects"]]
    print()
    print(f"trees audited: {len(rows)}   trees with defects: {len(bad)}")
    if bad:
        print(f"total defects: {sum(len(r['defects']) for r in bad)}")


if __name__ == "__main__":
    raise SystemExit(main())
