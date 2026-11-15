#!/usr/bin/env python3
"""Verify a repository meets PROFESSIONAL_PUBLIC_STANDARDS.md"""

import sys
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


def main():
    if len(sys.argv) < 2:
        print("Usage: python verify_public_standards.py <repo-path>")
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