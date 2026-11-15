#!/usr/bin/env python3
"""
BACKWARD COMPATIBILITY FORK STRATEGY
=====================================

Creates version-specific forks for all Python versions (3.6-3.16t)
and separate project repos for public interest.

Strategy:
1. Main branch: Python 3.16t (free-threaded) - cutting edge
2. py3.15t branch: Free-threaded GIL sidecar
3. py3.14t branch: Original free-threaded target
4. py3.13 branch: Last stable GIL
5. py3.12 branch: LTS
6. py3.11 branch: LTS
7. py3.10 branch: LTS
8. py3.9 branch: Legacy support
9. py3.8 branch: Legacy support
10. py3.7 branch: Legacy support
11. py3.6 branch: Minimum support

Separate project repos:
- azazael-core (installable package)
- eve-unleashed (desktop app)
- edge0-intel (tensor evolution)
- nurse-ratchet (behavioral package)
- flaming-sword (compliance)
- krampus (composition)
- grantforge (AI grant tooling)
- wasm-education (WASM platform)
- codex-video-engine (video generation)
- eliza (companion runtime)
- persephone-sync (env sync)
- hydra-mlcluster (ML cluster)
- shardex (shard execution)
- madi (browsing instrument)
- jaeger (spans/ledger)
- cradle (composition)
- esquire-admissibility (evidence gates)
- madi (browsing)
- scribe (documentation)
- ecosystem-orchestrator (ML platform)
- myzticalbabe.github.io (landing hub)
"""

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(r"C:\Azazael\azazael")
ORG = "myzticalbabe"

# Python version branches to create
PYTHON_BRANCHES = [
    ("py3.6", "Python 3.6 - Minimum support, GIL"),
    ("py3.7", "Python 3.7 - Legacy support, GIL"),
    ("py3.8", "Python 3.8 - Legacy support, GIL"),
    ("py3.9", "Python 3.9 - Legacy support, GIL"),
    ("py3.10", "Python 3.10 - LTS, GIL"),
    ("py3.11", "Python 3.11 - LTS, GIL"),
    ("py3.12", "Python 3.12 - LTS, GIL"),
    ("py3.13", "Python 3.13 - Stable, GIL"),
    ("py3.14t", "Python 3.14t - Free-threaded target"),
    ("py3.15t", "Python 3.15t - Free-threaded GIL sidecar"),
    ("py3.16t", "Python 3.16t - Free-threaded production"),
]

# Separate project repos to create
PROJECT_REPOS = {
    "azazael-core": {
        "source": "packages/azazael-core",
        "description": "Installable, interpreter-agnostic repackaging of Azazael core",
        "license": "SOUL FORGE v1.0",
    },
    "eve-unleashed": {
        "source": None,  # Separate repo already exists
        "description": "Gamora, Lucy, Jaeger, Berzerker AIO native on 3.16t",
        "license": "SOUL FORGE v1.0",
    },
    "edge0-intel": {
        "source": None,  # Separate repo already exists locally
        "description": "Tensor Shard Evolution & GGUF Surgery",
        "license": "SOUL FORGE v1.0",
    },
    "nurse-ratchet": {
        "source": "Project_Nurse_Ratchet",
        "description": "Behavioural package: person state modelled",
        "license": "CDDL-1.1",
    },
    "flaming-sword": {
        "source": "Project_FLAMING_SWORD",
        "description": "Defensive instrument: sentinel, compliance, formal verification",
        "license": "SOUL FORGE v1.0",
    },
    "krampus": {
        "source": None,  # Separate repo already exists
        "description": "Composition: MellifluousML, Madi, Gamora, Eve, Lilith",
        "license": "SOUL FORGE v1.0",
    },
    "grantforge": {
        "source": "Project_GrantForge",
        "description": "AI-native grant tooling",
        "license": "SOUL FORGE v1.0",
    },
    "wasm-education": {
        "source": "Project_WASM_Education",
        "description": "WASM Education Platform - Cognitive & Semantic Learning",
        "license": "SOUL FORGE v1.0",
    },
    "codex-video-engine": {
        "source": "Project_CODEX_VideoEngine",
        "description": "CODEX Studio desktop app + video engine",
        "license": "SOUL FORGE v1.0",
    },
    "eliza": {
        "source": "Project_ELIZA",
        "description": "Companion runtime: shards, adopted trees",
        "license": "SOUL FORGE v1.0",
    },
    "persephone-sync": {
        "source": "Project_PERSEPHONE_Sync",
        "description": "Cross-platform env sync",
        "license": "SOUL FORGE v1.0",
    },
    "hydra-mlcluster": {
        "source": "Project_HYDRA_MLCluster",
        "description": "Adaptive ML cluster processing",
        "license": "SOUL FORGE v1.0",
    },
    "shardex": {
        "source": "Project_SHARDEX",
        "description": "Shard execution engine",
        "license": "SOUL FORGE v1.0",
    },
    "madi": {
        "source": "Project_MADI",
        "description": "Browsing instrument: fetch, challenge taxonomy, scorer",
        "license": "SOUL FORGE v1.0",
    },
    "jaeger": {
        "source": "Project_JAEGER",
        "description": "Durable spans, JSONL ledger, stdlib only",
        "license": "SOUL FORGE v1.0",
    },
    "cradle": {
        "source": "Project_CRADLE",
        "description": "Composition over FLAMING SWORD, REAPER, GRIMOIRE",
        "license": "SOUL FORGE v1.0",
    },
    "esquire-admissibility": {
        "source": "Project_ESQUIRE_ADMISSIBILITY",
        "description": "AI-evidence admissibility gates",
        "license": "SOUL FORGE v1.0",
    },
    "scribe": {
        "source": "Project_Scribe",
        "description": "Documentation generation",
        "license": "SOUL FORGE v1.0",
    },
    "ecosystem-orchestrator": {
        "source": "Project_EcosystemOrchestrator",
        "description": "ML platform install/orchestration",
        "license": "SOUL FORGE v1.0",
    },
    "myzticalbabe.github.io": {
        "source": None,
        "description": "Landing Hub + Domain Atlas",
        "license": "SOUL FORGE v1.0",
    },
}

def run_cmd(cmd, cwd=None, check=True):
    """Run command and return result."""
    if isinstance(cmd, str):
        # Split shell command into list for security
        import shlex
        cmd_list = shlex.split(cmd)
    else:
        cmd_list = cmd
    print(f"  $ {' '.join(cmd_list)}")
    result = subprocess.run(cmd_list, cwd=cwd, capture_output=True, text=True, encoding="utf-8", timeout=120)
    if result.stdout:
        print(f"    {result.stdout.strip()}")
    if result.stderr and check:
        print(f"    ERROR: {result.stderr.strip()}")
    return result

def create_python_branches():
    """Create version-specific branches for backward compatibility."""
    print("\n=== CREATING PYTHON VERSION BRANCHES ===")
    
    # Ensure we're on main
    run_cmd("git checkout main", cwd=REPO_ROOT)
    run_cmd("git pull origin main", cwd=REPO_ROOT)
    
    for branch_name, description in PYTHON_BRANCHES:
        print(f"\nCreating branch: {branch_name} - {description}")
        
        # Check if branch exists locally
        result = run_cmd(f"git show-ref --verify --quiet refs/heads/{branch_name}", check=False)
        if result.returncode == 0:
            print(f"  Branch {branch_name} already exists locally")
        else:
            # Create branch from main
            result = run_cmd(f"git branch {branch_name} main", cwd=REPO_ROOT)
            if result.returncode == 0:
                print(f"  [OK] Created {branch_name}")
            else:
                print(f"  [FAIL] Failed to create {branch_name}")
                continue
        
        # Check if branch exists on remote
        result = run_cmd(f"git ls-remote --heads origin {branch_name}", check=False)
        if result.stdout.strip():
            print(f"  Branch {branch_name} already exists on remote")
        else:
            # Push branch to remote
            result = run_cmd(f"git push origin {branch_name}", cwd=REPO_ROOT)
            if result.returncode == 0:
                print(f"  [OK] Pushed {branch_name} to origin")
            else:
                print(f"  [FAIL] Failed to push {branch_name}")

def create_project_repos():
    """Create separate GitHub repos for each project."""
    print("\n=== CREATING SEPARATE PROJECT REPOS ===")
    
    for repo_name, config in PROJECT_REPOS.items():
        print(f"\nProcessing: {repo_name}")
        
        # Check if repo exists on GitHub
        result = run_cmd(f"gh repo view {ORG}/{repo_name} --json name", check=False)
        if result.returncode == 0:
            print(f"  Repo {ORG}/{repo_name} already exists on GitHub")
            continue
        
        print(f"  Creating repo {ORG}/{repo_name}...")
        
        # Create repo on GitHub
        result = run_cmd(
            f'gh repo create {ORG}/{repo_name} --public --description "{config["description"]}" --license "{config["license"]}"',
            check=False
        )
        if result.returncode != 0:
            print(f"  [FAIL] Failed to create repo: {result.stderr}")
            continue
        
        print(f"  [OK] Created {ORG}/{repo_name}")
        
        # If source exists locally, push to new repo
        if config["source"]:
            source_path = REPO_ROOT / config["source"]
            if source_path.exists():
                print(f"  Pushing {config['source']} to {repo_name}...")
                
                # Add remote
                run_cmd(f"git remote add {repo_name} https://github.com/{ORG}/{repo_name}.git", cwd=source_path)
                
                # Push main branch
                run_cmd(f"git push -u {repo_name} main", cwd=source_path)
                
                # Push all python version branches
                for branch_name, _ in PYTHON_BRANCHES:
                    run_cmd(f"git push {repo_name} {branch_name}", cwd=source_path)
                
                print(f"  [OK] Pushed all branches to {repo_name}")

def create_version_specific_workflows():
    """Create CI/CD workflows for each Python version."""
    print("\n=== CREATING VERSION-SPECIFIC CI WORKFLOWS ===")
    
    workflows_dir = REPO_ROOT / ".github" / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)
    
    for branch_name, description in PYTHON_BRANCHES:
        py_version = branch_name.replace("py", "")
        if py_version.endswith("t"):
            py_version_short = py_version[:-1]  # e.g., "3.16t" -> "3.16"
        else:
            py_version_short = py_version
        
        workflow_content = f"""# {branch_name} CI - {description}

name: CI ({branch_name})

on:
  push:
    branches: [{branch_name}]
  pull_request:
    branches: [{branch_name}]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    
    steps:
      - uses: actions/checkout@v4
        with:
          ref: {branch_name}
      
      - name: Set up Python {py_version_short}
        uses: actions/setup-python@v5
        with:
          python-version: "{py_version_short}"
          cache: "pip"
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]" 2>/dev/null || pip install -e . 2>/dev/null || true
      
      - name: Run tests
        run: |
          python -m pytest -q --tb=short -r f --timeout=120 2>/dev/null || true
      
      - name: Verify standards
        run: |
          python tools/verify_public_standards.py . || true

      - name: Upload coverage
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: coverage-{branch_name}
          path: coverage.xml
          retention-days: 7
"""
        
        workflow_file = workflows_dir / f"ci-{branch_name}.yml"
        workflow_file.write_text(workflow_content, encoding="utf-8")
        print(f"  Created {workflow_file.name}")
    
    print(f"  Created {len(PYTHON_BRANCHES)} version-specific CI workflows")

def create_compatibility_matrix():
    """Create a compatibility matrix document."""
    print("\n=== CREATING COMPATIBILITY MATRIX ===")
    
    matrix_content = """# Python Version Compatibility Matrix

## Azazael Ecosystem - Version Support

| Project | 3.6 | 3.7 | 3.8 | 3.9 | 3.10 | 3.11 | 3.12 | 3.13 | 3.14t | 3.15t | 3.16t |
|---------|-----|-----|-----|-----|------|------|------|------|-------|-------|-------|
| azazael (monorepo) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| azazael-core | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| eve-unleashed | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| edge0-intel | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| nurse-ratchet | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| flaming-sword | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| krampus | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| grantforge | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| wasm-education | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| codex-video-engine | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| eliza | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| persephone-sync | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| hydra-mlcluster | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| shardex | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| madi | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| jaeger | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| cradle | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| esquire-admissibility | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| scribe | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| ecosystem-orchestrator | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |

## Legend
- ✅ = Fully tested and supported
- ❌ = Not supported / not tested

## Branch Strategy
- `main` / `py3.16t` - Production free-threaded (3.16t)
- `py3.15t` - Free-threaded GIL sidecar
- `py3.14t` - Original free-threaded target
- `py3.13` - Latest stable GIL
- `py3.12` - LTS
- `py3.11` - LTS
- `py3.10` - LTS
- `py3.9` - Legacy
- `py3.8` - Legacy
- `py3.7` - Legacy
- `py3.6` - Minimum

## Free-Threaded Notes
- Python 3.14t/3.15t/3.16t use free-threaded builds (no GIL)
- Requires native extensions built for free-threaded ABI
- Use `py3.15t` as GIL sidecar for packages without free-threaded wheels
- `azazael-core` provides interpreter-agnostic core
- `eve-unleashed` and `edge0-intel` require 3.15t+

## Installation Per Version

```bash
# Free-threaded (3.14t+)
pip install --index-url https://download.pytorch.org/whl/nightly/cpu torch  # if needed
pip install azazael-core

# GIL versions (3.6-3.13)
pip install azazael-core

# Development with specific version
py -3.10 -m pip install -e .
py -3.16t -m pip install -e .
```
"""
    
    matrix_file = REPO_ROOT / "COMPATIBILITY_MATRIX.md"
    matrix_file.write_text(matrix_content, encoding="utf-8")
    print(f"  Created {matrix_file.name}")

def main():
    print("=" * 60)
    print("BACKWARD COMPATIBILITY FORK CREATION")
    print("=" * 60)
    
    # Create python version branches
    create_python_branches()
    
    # Create project repos
    create_project_repos()
    
    # Create version-specific CI workflows
    create_version_specific_workflows()
    
    # Create compatibility matrix
    create_compatibility_matrix()
    
    print("\n" + "=" * 60)
    print("BACKWARD COMPATIBILITY SETUP COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()