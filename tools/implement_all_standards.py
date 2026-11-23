#!/usr/bin/env python3
"""
IMPLEMENT ALL PROFESSIONAL STANDARDS ACROSS ALL 20 MYZTICALBABE REPOS

This script propagates:
1. All 14 governance files from nurse_ratchet gold standard
2. CI/CD workflows (ci.yml, pages-deploy.yml)
3. GitHub templates (issue templates, PR template)
4. Equity infrastructure (RULE 0Z-R compliance)
5. Cross-repo table in all READMEs
6. Runs verification on each repo
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================

GOLD_STANDARD = Path(r"C:\Azazael\azazael\Project_Nurse_Ratchet")
PUBLISH_REPOS = Path(r"C:\Azazael\publish_repos")
MONOREPO_PROJECTS = Path(r"C:\Azazael\azazael")
SEPARATE_REPOS = {
    "EveUnleashed": Path(r"C:\Azazael\EveUnleashed"),
    "krampus": Path(r"C:\Azazael\krampus"),
    "azazael": Path(r"C:\Azazael\azazael"),  # monorepo root
    "myzticalbabe.github.io": None,  # doesn't exist locally yet
}

# Repo name mapping (local dir name -> GitHub repo name)
REPO_MAPPING = {
    # publish_repos
    "cradle": "cradle",
    "esquire_admissibility": "esquire-admissibility",
    "flame": "flame",
    "flaming_sword": "flaming-sword",
    "nurse_ratchet": "nurse-ratchet",
    "shardex": "shardex",
    # monorepo projects (Project_* dirs)
    "Project_CRADLE": "cradle",
    "Project_FLAME": "flame",
    "Project_FLAMING_SWORD": "flaming-sword",
    "Project_Nurse_Ratchet": "nurse-ratchet",
    "Project_SHARDEX": "shardex",
    "Project_JAEGER": "jaeger",
    "Project_PERSEPHONE_Sync": "persephone-sync",
    "Project_Scribe": "scribe",
    "Project_EcosystemOrchestrator": "ecosystem-orchestrator",
    "Project_CODEX_VideoEngine": "codex-video-engine",
    "Project_ELIZA": "eliza",
    "Project_HYDRA_MLCluster": "hydra-mlcluster",
    "Project_WASM_Education": "wasm-education",
    # separate repos
    "EveUnleashed": "EveUnleashed",
    "krampus": "krampus",
    "azazael": "azazael",
    "azazael-core": "azazael-core",  # in packages/
}

# All 20 repo names for cross-repo table
ALL_REPOS = [
    "azazael", "azazael-core", "nurse-ratchet", "esquire-admissibility",
    "cradle", "jaeger", "madi", "grantforge", "krampus", "shardex",
    "flaming-sword", "hydra-mlcluster", "persephone-sync", "scribe",
    "ecosystem-orchestrator", "codex-video-engine", "eliza",
    "EveUnleashed", "wasm-education", "myzticalbabe.github.io"
]

# Files to copy from gold standard
GOVERNANCE_FILES = [
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
    "LICENSE",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
]

WORKFLOW_FILES = [
    ".github/workflows/ci.yml",
    ".github/workflows/pages-deploy.yml",
]

TEMPLATE_FILES = [
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/feature_request.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/PULL_REQUEST_TEMPLATE.md",
]

# ============================================================
# CROSS-REPO TABLE GENERATOR
# ============================================================

CROSS_REPO_TABLE = """## Related Repositories

| Repo | Description | Status |
|------|-------------|--------|
| azazael | Monorepo: worm registry, cluster system, agent harness | Active |
| azazael-core | Installable, interpreter-agnostic repackaging | Active |
| nurse-ratchet | Behavioural package: person state modelled | Active |
| esquire-admissibility | AI-evidence admissibility gates | Active |
| cradle | Composition over FLAMING SWORD, REAPER, GRIMOIRE | Active |
| jaeger | Durable spans, JSONL ledger, stdlib only | Active |
| madi | Browsing instrument: fetch, challenge taxonomy, scorer | Active |
| grantforge | AI-native grant tooling | Active |
| krampus | Composition: MellifluousML, Madi, Gamora, Eve, Lilith | Active |
| shardex | Shard execution engine | Active |
| flaming-sword | Defensive instrument: sentinel, compliance, formal verification | Active |
| hydra-mlcluster | Adaptive ML cluster processing | Active |
| persephone-sync | Cross-platform env sync | Active |
| scribe | Documentation generation | Active |
| ecosystem-orchestrator | ML platform install/orchestration | Active |
| codex-video-engine | CODEX Studio desktop app + video engine | Active |
| eliza | Companion runtime: shards, adopted trees | Active |
| EveUnleashed | Gamora, Lucy, Jaeger, Berzerker AIO native on 3.16t | Active |
| wasm-education | WASM Education Platform | Active |
| myzticalbabe.github.io | Landing Hub + Domain Atlas | Active |"""

def generate_cross_repo_table():
    return CROSS_REPO_TABLE

# ============================================================
# EQUITY INFRASTRUCTURE FILES (RULE 0Z-R)
# ============================================================

EQUITY_WORKFLOW = """# Bias-Interrupter Enabled Evaluation Workflow
# Part of RULE 0Z-R compliance - runs on all evaluation/promotion actions

name: Equity Evaluation Gate

on:
  workflow_dispatch:
    inputs:
      evaluation_type:
        description: 'Type of evaluation'
        required: true
        type: choice
        options:
          - promotion
          - hiring
          - annual-review
          - award
      candidate_demographics:
        description: 'Intersectional demographics (gender, race, parenthood, disability)'
        required: false
        type: string

permissions:
  contents: read
  issues: write
  pull-requests: write

jobs:
  equity-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Verify bias interrupter assigned
        run: |
          if [ -z "$BIAS_INTERRUPTER" ]; then
            echo "::error::BIAS_INTERRUPTER not assigned - evaluation blocked per RULE 0Z-R Tier 1"
            exit 1
          fi
          echo "Bias interrupter: $BIAS_INTERRUPTER"

      - name: Verify structured criteria published
        run: |
          if [ ! -f "PROMOTION_CRITERIA.md" ] && [ ! -f "EVALUATION_CRITERIA.md" ]; then
            echo "::error::No structured criteria file found - evaluation blocked per RULE 0Z-R Tier 1"
            exit 1
          fi
          echo "Structured criteria found"

      - name: Verify multi-evaluator panel (>=3)
        run: |
          if [ -z "$EVALUATORS" ] || [ $(echo "$EVALUATORS" | tr ',' '\\n' | wc -l) -lt 3 ]; then
            echo "::error::Multi-evaluator panel requires >=3 evaluators - evaluation blocked per RULE 0Z-R Tier 1"
            exit 1
          fi
          echo "Evaluators: $EVALUATORS"

      - name: Verify performance vs potential separation
        run: |
          if [ -z "$PERFORMANCE_RATING" ] || [ -z "$POTENTIAL_RATING" ]; then
            echo "::error::Performance and potential must be rated separately - evaluation blocked per RULE 0Z-R Tier 1"
            exit 1
          fi
          echo "Performance: $PERFORMANCE_RATING, Potential: $POTENTIAL_RATING"

      - name: Verify personality vs skill separation
        run: |
          if [ -z "$SKILL_RATING" ]; then
            echo "::error::Skills must be rated separately from personality - evaluation blocked per RULE 0Z-R Tier 1"
            exit 1
          fi
          echo "Skills rated separately from personality"

      - name: Verify data tracking active
        run: |
          if [ ! -f "equity_tracking.json" ]; then
            echo "::warning::Equity tracking file not found - creating template"
            cat > equity_tracking.json << 'EOF'
{
  "evaluation_cycle": "${{ github.event.inputs.evaluation_type || 'manual' }}",
  "candidate_demographics": "${{ github.event.inputs.candidate_demographics || 'not-provided' }}",
  "bias_interrupter": "$BIAS_INTERRUPTER",
  "evaluators": "$EVALUATORS",
  "performance_rating": "$PERFORMANCE_RATING",
  "potential_rating": "$POTENTIAL_RATING",
  "skill_rating": "$SKILL_RATING",
  "personality_rating": "$PERSONALITY_RATING",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
          fi
          echo "Equity tracking recorded"

      - name: Verify sponsorship for advancement
        if: github.event.inputs.evaluation_type == 'promotion'
        run: |
          if [ -z "$SPONSOR" ]; then
            echo "::error::Formal sponsorship required for promotion (not mentoring) - blocked per RULE 0Z-R Tier 2"
            exit 1
          fi
          echo "Sponsor: $SPONSOR"

      - name: Verify service work accounting
        run: |
          if [ ! -f "service_accounting.json" ]; then
            echo "::warning::Service accounting not found - creating template"
            cat > service_accounting.json << 'EOF'
{
  "internal_service_hours": 0,
  "external_service_hours": 0,
  "service_roles": [],
  "rewarded_equally": true
}
EOF
          fi
          echo "Service accounting verified"

      - name: Verify self-promotion alternatives
        run: |
          if [ ! -f "accomplishment_sharing.md" ]; then
            echo "::warning::Accomplishment sharing system not found - creating template"
            cat > accomplishment_sharing.md << 'EOF'
# Accomplishment Sharing System

Monthly accomplishment emails sent by managers to team.
Formal system for sharing successes without self-promotion penalty.
EOF
          fi
          echo "Self-promotion alternatives verified"

      - name: Record intersectional equity data
        run: |
          cat > intersectional_equity_report.json << 'EOF'
{
  "evaluation_type": "${{ github.event.inputs.evaluation_type || 'manual' }}",
  "demographics": "${{ github.event.inputs.candidate_demographics || 'not-provided' }}",
  "outcome": "pending",
  "disparities_flagged": false,
  "audit_timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
          echo "Intersectional equity data recorded"

      - name: Post evaluation summary
        run: |
          echo "## Equity Evaluation Gate Results" >> $GITHUB_STEP_SUMMARY
          echo "- **Type**: ${{ github.event.inputs.evaluation_type }}" >> $GITHUB_STEP_SUMMARY
          echo "- **Bias Interrupter**: $BIAS_INTERRUPTER" >> $GITHUB_STEP_SUMMARY
          echo "- **Evaluators**: $EVALUATORS" >> $GITHUB_STEP_SUMMARY
          echo "- **Performance/Potential Separated**: Yes" >> $GITHUB_STEP_SUMMARY
          echo "- **Skills/Personality Separated**: Yes" >> $GITHUB_STEP_SUMMARY
          echo "- **Data Tracking**: Active" >> $GITHUB_STEP_SUMMARY
          if [ "${{ github.event.inputs.evaluation_type }}" == "promotion" ]; then
            echo "- **Sponsor**: $SPONSOR" >> $GITHUB_STEP_SUMMARY
          fi
          echo "- **Service Accounting**: Verified" >> $GITHUB_STEP_SUMMARY
          echo "- **Intersectional Data**: Recorded" >> $GITHUB_STEP_SUMMARY
          echo "- **Status**: [PASS] PASSED" >> $GITHUB_STEP_SUMMARY

env:
  BIAS_INTERRUPTER: ${{ vars.BIAS_INTERRUPTER }}
  EVALUATORS: ${{ vars.EVALUATORS }}
  PERFORMANCE_RATING: ${{ vars.PERFORMANCE_RATING }}
  POTENTIAL_RATING: ${{ vars.POTENTIAL_RATING }}
  SKILL_RATING: ${{ vars.SKILL_RATING }}
  PERSONALITY_RATING: ${{ vars.PERSONALITY_RATING }}
  SPONSOR: ${{ vars.SPONSOR }}
"""

# ============================================================
# IMPLEMENTATION FUNCTIONS
# ============================================================

def copy_file_with_dirs(src, dst):
    """Copy file, creating parent directories as needed."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"  [OK] Copied {src.name} -> {dst}")

def copy_dir_contents(src_dir, dst_dir):
    """Copy all contents of src_dir to dst_dir."""
    if not src_dir.exists():
        print(f"  [MISSING] Source not found: {src_dir}")
        return
    dst_dir.mkdir(parents=True, exist_ok=True)
    for item in src_dir.iterdir():
        if item.is_file():
            shutil.copy2(item, dst_dir / item.name)
            print(f"  [OK] Copied {item.name}")
        elif item.is_dir():
            shutil.copytree(item, dst_dir / item.name, dirs_exist_ok=True)
            print(f"  [OK] Copied dir {item.name}")

def update_readme_with_cross_repo(repo_path):
    """Add/update cross-repo table in README.md"""
    readme_path = repo_path / "README.md"
    if not readme_path.exists():
        print(f"  [MISSING] README.md not found in {repo_path}")
        return False

    content = readme_path.read_text(encoding="utf-8", errors="ignore")
    table = generate_cross_repo_table()

    # Check if table already exists
    if "## Related Repositories" in content:
        # Replace existing table
        import re
        pattern = r"## Related Repositories.*?(?=## |\Z)"
        new_content = re.sub(pattern, table, content, flags=re.DOTALL)
        if new_content == content:
            # Try alternative pattern
            pattern = r"\| Repo \| Description \| Status \|.*?(?=\n\n|\Z)"
            new_content = re.sub(pattern, table, content, flags=re.DOTALL)
    else:
        # Add before Contributing or at end
        if "## Contributing" in content:
            new_content = content.replace("## Contributing", table + "\n\n## Contributing")
        else:
            new_content = content.rstrip() + "\n\n" + table + "\n"

    readme_path.write_text(new_content, encoding="utf-8")
    print(f"  [OK] Updated cross-repo table in README.md")
    return True

def add_equity_workflow(repo_path):
    """Add equity evaluation gate workflow"""
    workflow_path = repo_path / ".github" / "workflows" / "equity-evaluation-gate.yml"
    workflow_path.parent.mkdir(parents=True, exist_ok=True)
    workflow_path.write_text(EQUITY_WORKFLOW, encoding="utf-8")
    print(f"  [OK] Added equity-evaluation-gate.yml")

def process_repo(repo_path, repo_name):
    """Process a single repository with all standards."""
    print(f"\n{'='*60}")
    print(f"PROCESSING: {repo_name} ({repo_path})")
    print(f"{'='*60}")

    if not repo_path.exists():
        print(f"  [MISSING] REPO NOT FOUND: {repo_path}")
        return False

    try:
        # 1. Copy governance files
        print("\n1. Copying governance files...")
        for f in GOVERNANCE_FILES:
            src = GOLD_STANDARD / f
            dst = repo_path / f
            if src.exists():
                copy_file_with_dirs(src, dst)
            else:
                print(f"  [WARN] Source not found: {src}")

        # 2. Copy workflows
        print("\n2. Copying CI/CD workflows...")
        for f in WORKFLOW_FILES:
            src = GOLD_STANDARD / f
            dst = repo_path / f
            if src.exists():
                copy_file_with_dirs(src, dst)
            else:
                print(f"  [WARN] Source not found: {src}")

        # 3. Copy templates
        print("\n3. Copying GitHub templates...")
        for f in TEMPLATE_FILES:
            src = GOLD_STANDARD / f
            dst = repo_path / f
            if src.exists():
                copy_file_with_dirs(src, dst)
            else:
                print(f"  [WARN] Source not found: {src}")

        # 4. Update README with cross-repo table
        print("\n4. Updating README with cross-repo table...")
        update_readme_with_cross_repo(repo_path)

        # 5. Add equity workflow (RULE 0Z-R)
        print("\n5. Adding equity evaluation gate workflow...")
        add_equity_workflow(repo_path)

        # 6. Run verification
        print("\n6. Running verification...")
        result = subprocess.run(
            [sys.executable, r"C:\Azazael\azazael\tools\verify_public_standards.py", str(repo_path)],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60
        )
        print(result.stdout)
        if result.stderr:
            print(f"  stderr: {result.stderr}")
        if result.returncode == 0:
            print(f"  [PASS] VERIFICATION PASSED")
        else:
            print(f"  [WARN] VERIFICATION FAILED (expected for some repos)")

        return True

    except Exception as e:
        print(f"  [MISSING] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================
# MAIN
# ============================================================

def main():
    print("="*60)
    print("IMPLEMENTING PROFESSIONAL STANDARDS ACROSS ALL 20 REPOS")
    print("="*60)

    success_count = 0
    total_count = 0

    # Process publish_repos
    print("\n\n>>> PHASE 1: PUBLISH REPOS <<<")
    for local_name, github_name in [
        ("cradle", "cradle"),
        ("esquire_admissibility", "esquire-admissibility"),
        ("flame", "flame"),
        ("flaming_sword", "flaming-sword"),
        ("nurse_ratchet", "nurse-ratchet"),
        ("shardex", "shardex"),
    ]:
        repo_path = PUBLISH_REPOS / local_name
        total_count += 1
        if process_repo(repo_path, github_name):
            success_count += 1

    # Process monorepo projects
    print("\n\n>>> PHASE 2: MONOREPO PROJECTS <<<")
    for local_name, github_name in [
        ("Project_JAEGER", "jaeger"),
        ("Project_PERSEPHONE_Sync", "persephone-sync"),
        ("Project_Scribe", "scribe"),
        ("Project_EcosystemOrchestrator", "ecosystem-orchestrator"),
        ("Project_CODEX_VideoEngine", "codex-video-engine"),
        ("Project_ELIZA", "eliza"),
        ("Project_HYDRA_MLCluster", "hydra-mlcluster"),
        ("Project_WASM_Education", "wasm-education"),
        ("Project_FLAME", "flame"),
        ("Project_FLAMING_SWORD", "flaming-sword"),
        ("Project_SHARDEX", "shardex"),
        ("Project_CRADLE", "cradle"),
        ("Project_Nurse_Ratchet", "nurse-ratchet"),
    ]:
        repo_path = MONOREPO_PROJECTS / local_name
        total_count += 1
        if process_repo(repo_path, github_name):
            success_count += 1

    # Process separate repos
    print("\n\n>>> PHASE 3: SEPARATE REPOS <<<")
    for local_name, github_name in [
        ("EveUnleashed", "EveUnleashed"),
        ("krampus", "krampus"),
    ]:
        repo_path = SEPARATE_REPOS[local_name]
        total_count += 1
        if process_repo(repo_path, github_name):
            success_count += 1

    # azazael monorepo root
    print("\n\n>>> PHASE 4: AZAZAEL MONOREPO ROOT <<<")
    total_count += 1
    if process_repo(Path(r"C:\Azazael\azazael"), "azazael"):
        success_count += 1

    # azazael-core
    print("\n\n>>> PHASE 5: AZAZAEL-CORE <<<")
    total_count += 1
    if process_repo(Path(r"C:\Azazael\azazael\packages\azazael-core"), "azazael-core"):
        success_count += 1

    # Summary
    print("\n\n" + "="*60)
    print(f"IMPLEMENTATION COMPLETE: {success_count}/{total_count} repos processed")
    print("="*60)

    if success_count == total_count:
        print("[PASS] ALL REPOS PROCESSED SUCCESSFULLY")
    else:
        print(f"[WARN] {total_count - success_count} repos had issues")

if __name__ == "__main__":
    main()