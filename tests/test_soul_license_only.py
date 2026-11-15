"""One license, everywhere: the Soul Forge License v1.0.

These tests are the enforcement arm of ``tools/soul_license_audit.py``. They fail
when any tree in the monorepo declares a license other than the Soul Forge
License v1.0, when a LICENSE copy drifts from the canonical text, or when a tree
slice (a README, a NOTICE, a manifest) stops carrying the maker's mark.

The repository root's own ``LICENSE`` is the canonical copy, so these tests need
nothing outside the tree.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = (ROOT / "LICENSE").read_bytes()
LICENSE_NAME = "Soul Forge License v1.0"

# Our code only. Third-party material keeps its own license and is named in
# NOTICE; these tokens must not appear in a first-party governance artifact.
FOREIGN_TOKENS = (
    "CDDL",
    "COMMON DEVELOPMENT AND DISTRIBUTION",
    "Apache-2.0",
    "Apache License",
)

GOVERNANCE = ("LICENSE", "README.md", "NOTICE", "CITATION.cff", "CONTRIBUTING.md")


def trees() -> list[Path]:
    found = [ROOT]
    found.extend(sorted(p for p in ROOT.glob("Project_*") if p.is_dir()))
    return found


def text_of(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_census_is_pinned():
    """37 project trees plus the repository root."""
    projects = [p for p in ROOT.glob("Project_*") if p.is_dir()]
    assert len(projects) == 37, f"expected 37 project trees, found {len(projects)}"
    assert len(trees()) == 38


def test_canonical_is_the_soul_forge_license():
    body = CANONICAL.decode("utf-8")
    assert body.startswith("SOUL FORGE LICENSE")
    assert "THE THREE VOWS" in body
    assert "VOW I — ATTRIBUTION OF SPIRIT" in body
    assert "VOW II — NO CAGE FOR THE FLAME" in body
    assert "VOW III — RECIPROCITY OF FORGE" in body
    assert "THE MAKER'S MARK (REQUIRED IN ALL COPIES)" in body
    assert "Author: myzticalbabe" in body


@pytest.mark.parametrize("tree", trees(), ids=lambda p: "." if p == ROOT else p.name)
def test_license_is_byte_identical(tree: Path):
    lic = tree / "LICENSE"
    assert lic.exists(), f"{tree.name}/LICENSE is missing"
    assert lic.read_bytes() == CANONICAL, f"{tree.name}/LICENSE drifted from canonical"


@pytest.mark.parametrize("tree", trees(), ids=lambda p: "." if p == ROOT else p.name)
def test_no_foreign_license_in_governance(tree: Path):
    for name in GOVERNANCE:
        path = tree / name
        if not path.exists():
            continue
        body = text_of(path)
        for token in FOREIGN_TOKENS:
            assert token not in body, f"{tree.name}/{name} still names {token}"


@pytest.mark.parametrize("tree", trees(), ids=lambda p: "." if p == ROOT else p.name)
def test_citation_declares_soul_forge(tree: Path):
    path = tree / "CITATION.cff"
    if not path.exists():
        pytest.skip("no CITATION.cff")
    match = re.search(r"^license:\s*(.+)$", text_of(path), re.MULTILINE)
    assert match, f"{tree.name}/CITATION.cff has no license field"
    assert match.group(1).strip().strip('"') == LICENSE_NAME


@pytest.mark.parametrize("tree", trees(), ids=lambda p: "." if p == ROOT else p.name)
def test_pyproject_declares_soul_forge(tree: Path):
    path = tree / "pyproject.toml"
    if not path.exists():
        pytest.skip("no pyproject.toml")
    body = text_of(path)
    if not re.search(r"^license\s*=", body, re.MULTILINE):
        pytest.skip("no license field")
    assert LICENSE_NAME in body


@pytest.mark.parametrize("tree", trees(), ids=lambda p: "." if p == ROOT else p.name)
def test_manifest_declares_soul_forge(tree: Path):
    path = tree / "PUBLIC_MANIFEST.json"
    if not path.exists():
        pytest.skip("no PUBLIC_MANIFEST.json")
    data = json.loads(text_of(path))
    assert data.get("license") == LICENSE_NAME


@pytest.mark.parametrize("tree", trees(), ids=lambda p: "." if p == ROOT else p.name)
def test_readme_has_exactly_one_license_section(tree: Path):
    path = tree / "README.md"
    assert path.exists(), f"{tree.name}/README.md is missing"
    heads = re.findall(r"^## License\s*$", text_of(path), re.MULTILINE)
    assert len(heads) == 1, f"{tree.name}/README.md has {len(heads)} ## License sections"


@pytest.mark.parametrize("tree", trees(), ids=lambda p: "." if p == ROOT else p.name)
def test_notice_carries_makers_mark(tree: Path):
    path = tree / "NOTICE"
    assert path.exists(), f"{tree.name}/NOTICE is missing"
    body = text_of(path)
    assert LICENSE_NAME in body
    assert "Author: myzticalbabe" in body
    assert "Forged: 2026-11-14" in body
    # a duplicated mark is a defect, not a style choice
    assert body.count("Author: myzticalbabe") == 1
