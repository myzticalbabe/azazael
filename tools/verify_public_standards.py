#!/usr/bin/env python3
"""Verify a repository meets PROFESSIONAL_PUBLIC_STANDARDS.md

Negative controls (run with --negative-control):
  - empty directory: should fail all governance/workflows/templates
  - directory with only README.md: should fail governance/workflows/templates
  - directory with missing cross-repo table: should fail cross_repo_table
"""

import sys
import tempfile
from pathlib import Path

REQUIRED_GOVERNANCE = [
    "README.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    "CITATION.cff",
    "DISCLOSURE_POLICY.md",
    "NOTICE",
    "PUBLIC_MANIFEST.json",
    "HARDWARE.md",
    "MANIFEST_NOTES.md",
    "requiem.py",
    "certification.json",
]

REQUIRED_WORKFLOWS = [
    ".github/workflows/ci.yml",
    ".github/workflows/pages-deploy.yml",
]

REQUIRED_TEMPLATES = [
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/feature_request.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/PULL_REQUEST_TEMPLATE.md",
]

REQUIRED_CROSS_REPO = [
    "azazael",
    "azazael-core",
    "nurse-ratchet",
    "esquire-admissibility",
    "cradle",
    "jaeger",
    "madi",
    "grantforge",
    "krampus",
    "shardex",
    "flaming-sword",
    "hydra-mlcluster",
    "persephone-sync",
    "scribe",
    "ecosystem-orchestrator",
    "codex-video-engine",
    "eliza",
    "EveUnleashed",
    "wasm-education",
    "myzticalbabe.github.io",
]


def verify_repo(repo_path: Path) -> dict:
    repo_path = Path(repo_path).resolve()
    if not repo_path.exists():
        return {"ok": False, "error": f"Path does not exist: {repo_path}"}

    results = {
        "repo": str(repo_path),
        "governance": {},
        "workflows": {},
        "templates": {},
        "cross_repo_table": False,
        "missing": [],
    }

    # Check governance files
    for f in REQUIRED_GOVERNANCE:
        path = repo_path / f
        exists = path.exists()
        results["governance"][f] = exists
        if not exists:
            results["missing"].append(f"governance:{f}")

    # Check workflows
    for f in REQUIRED_WORKFLOWS:
        path = repo_path / f
        exists = path.exists()
        results["workflows"][f] = exists
        if not exists:
            results["missing"].append(f"workflow:{f}")

    # Check templates
    for f in REQUIRED_TEMPLATES:
        path = repo_path / f
        exists = path.exists()
        results["templates"][f] = exists
        if not exists:
            results["missing"].append(f"template:{f}")

    # Check cross-repo table in README
    readme = repo_path / "README.md"
    if readme.exists():
        content = readme.read_text(encoding="utf-8", errors="ignore")
        missing_repos = [r for r in REQUIRED_CROSS_REPO if r not in content]
        results["cross_repo_table"] = len(missing_repos) == 0
        if missing_repos:
            results["missing"].append(f"cross_repo_table: missing {len(missing_repos)} repos")
    else:
        results["missing"].append("governance:README.md")

    results["ok"] = len(results["missing"]) == 0
    return results


def run_negative_controls() -> bool:
    """Run negative controls: known-bad fixtures that should FAIL verification.

    Returns True if all negative controls correctly fail (verifier is working).
    Returns False if any negative control incorrectly passes (verifier is broken).
    """
    print("\n=== NEGATIVE CONTROLS ===")
    all_passed = True

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Control 1: Empty directory should fail everything
        empty_dir = tmp / "empty"
        empty_dir.mkdir()
        result = verify_repo(empty_dir)
        if result["ok"]:
            print(f"  FAIL: empty directory incorrectly PASSED")
            all_passed = False
        else:
            print(f"  PASS: empty directory correctly FAILED ({len(result['missing'])} missing)")

        # Control 2: Only README.md should fail governance/workflows/templates
        readme_only = tmp / "readme_only"
        readme_only.mkdir()
        (readme_only / "README.md").write_text("# Test\n")
        result = verify_repo(readme_only)
        if result["ok"]:
            print(f"  FAIL: readme-only directory incorrectly PASSED")
            all_passed = False
        else:
            missing_gov = [m for m in result["missing"] if m.startswith("governance:")]
            missing_wf = [m for m in result["missing"] if m.startswith("workflow:")]
            missing_tmpl = [m for m in result["missing"] if m.startswith("template:")]
            if missing_gov and missing_wf and missing_tmpl:
                print(f"  PASS: readme-only correctly FAILED (gov:{len(missing_gov)} wf:{len(missing_wf)} tmpl:{len(missing_tmpl)})")
            else:
                print(f"  FAIL: readme-only missing expected failures: {result['missing']}")
                all_passed = False

        # Control 3: Complete repo but missing cross-repo table
        cross_repo_missing = tmp / "cross_repo_missing"
        cross_repo_missing.mkdir()
        for f in REQUIRED_GOVERNANCE:
            (cross_repo_missing / f).write_text("# placeholder\n")
        (cross_repo_missing / ".github" / "workflows").mkdir(parents=True)
        for f in REQUIRED_WORKFLOWS:
            (cross_repo_missing / f).write_text("# placeholder\n")
        (cross_repo_missing / ".github" / "ISSUE_TEMPLATE").mkdir(parents=True)
        for f in REQUIRED_TEMPLATES:
            (cross_repo_missing / f).write_text("# placeholder\n")
        (cross_repo_missing / "README.md").write_text("# Test Repo\n\nNo cross-repo table here.\n")
        result = verify_repo(cross_repo_missing)
        if result["ok"]:
            print(f"  FAIL: missing cross-repo table incorrectly PASSED")
            all_passed = False
        elif not result["cross_repo_table"]:
            print(f"  PASS: missing cross-repo table correctly FAILED")
        else:
            print(f"  FAIL: missing cross-repo table but cross_repo_table=True: {result}")
            all_passed = False

    return all_passed


def main():
    if len(sys.argv) < 2:
        print("Usage: python verify_public_standards.py <repo-path> [--negative-control]")
        sys.exit(1)

    if sys.argv[1] == "--negative-control":
        ok = run_negative_controls()
        if ok:
            print("\n=== ALL NEGATIVE CONTROLS PASSED ===")
            sys.exit(0)
        else:
            print("\n=== NEGATIVE CONTROLS FAILED ===")
            sys.exit(1)

    repo_path = sys.argv[1]
    result = verify_repo(repo_path)

    print(f"\n=== VERIFICATION: {result['repo']} ===")
    if result.get("error"):
        print(f"ERROR: {result['error']}")
        sys.exit(1)

    # Governance
    gov_ok = sum(1 for v in result["governance"].values() if v)
    gov_total = len(result["governance"])
    print(f"\nGovernance: {gov_ok}/{gov_total}")
    for f, ok in result["governance"].items():
        status = "[OK]" if ok else "[MISSING]"
        print(f"  {status} {f}")

    # Workflows
    wf_ok = sum(1 for v in result["workflows"].values() if v)
    wf_total = len(result["workflows"])
    print(f"\nWorkflows: {wf_ok}/{wf_total}")
    for f, ok in result["workflows"].items():
        status = "[OK]" if ok else "[MISSING]"
        print(f"  {status} {f}")

    # Templates
    tmpl_ok = sum(1 for v in result["templates"].values() if v)
    tmpl_total = len(result["templates"])
    print(f"\nTemplates: {tmpl_ok}/{tmpl_total}")
    for f, ok in result["templates"].items():
        status = "[OK]" if ok else "[MISSING]"
        print(f"  {status} {f}")

    # Cross-repo table
    status = "[OK]" if result["cross_repo_table"] else "[MISSING]"
    print(f"\nCross-repo table: {status}")

    # Summary
    if result["ok"]:
        print(f"\n{'='*50}")
        print("PASS -- Repository meets all professional standards")
        print(f"{'='*50}")
        sys.exit(0)
    else:
        print(f"\n{'='*50}")
        print(f"FAIL -- {len(result['missing'])} missing items:")
        print(f"{'='*50}")
        for m in result["missing"]:
            print(f"  - {m}")
        sys.exit(1)


if __name__ == "__main__":
    main()