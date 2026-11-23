# PROFESSIONAL-GRADE PUBLIC ADOPTION STANDARDS

**Canonical Source**: C:/Azazael/azazael/PROFESSIONAL_PUBLIC_STANDARDS.md
**Applies To**: All 20 myzticalbabe repositories (main + extracted)
**Gold Standard Template**: Project_Nurse_Ratchet (C:/Azazael/azazael/Project_Nurse_Ratchet/)
**Landing Hub**: myzticalbabe.github.io (separate repo, special rules)
**Effective Date**: 2026-11-14

---

## MANDATORY FILE CHECKLIST — Every Repository Must Have

### Governance Files (14 files)
```
README.md                    # Comprehensive: overview, install, usage, arch, license, related, contributing, links
LICENSE                      # SOUL FORGE v1.0 (or CDDL-1.1 for nurse-ratchet)
CONTRIBUTING.md              # Contribution guidelines
CHANGELOG.md                 # Keep a changelog format
CODE_OF_CONDUCT.md           # Contributor Covenant v2.1
SECURITY.md                  # Security policy with reporting channel
CITATION.cff                 # Citation File Format v1.2.0
DISCLOSURE_POLICY.md         # What ships vs never ships, enforcement gate
NOTICE                       # Copyright, license ruling, attribution notes
PUBLIC_MANIFEST.json         # Allowlist manifest with never_ship globs + deny_substrings
HARDWARE.md                  # Reference platform + porting guide + CDCL
MANIFEST_NOTES.md            # Why allowlist, layout, regeneration commands
requiem.py                   # Stdlib-only crash recorder (copy to any codebase root)
certification.json           # Auditor-grade requirements with evidence gates
```

### CI/CD Workflows (2 files minimum)
```
.github/workflows/ci.yml          # Multi-version test matrix, materialisation gate
.github/workflows/pages-deploy.yml # GitHub Pages deployment
```

### GitHub Configuration
```
.github/ISSUE_TEMPLATE/bug_report.yml
.github/ISSUE_TEMPLATE/feature_request.yml
.github/ISSUE_TEMPLATE/config.yml
.github/PULL_REQUEST_TEMPLATE.md
```

### GitHub Metadata (Set via Settings → General)
- **Description**: One-sentence project summary
- **Topics/Tags**: 5-10 relevant topics
- **Website**: Landing hub URL or demo URL
- **Discussions**: Enabled

---

## REPRODUCTION PROCEDURE

### Step 1: Copy Gold Standard Files
```bash
# From Project_Nurse_Ratchet to target repo
cp Project_Nurse_Ratchet/CODE_OF_CONDUCT.md <target>/
cp Project_Nurse_Ratchet/SECURITY.md <target>/
cp Project_Nurse_Ratchet/CITATION.cff <target>/
cp Project_Nurse_Ratchet/DISCLOSURE_POLICY.md <target>/
cp Project_Nurse_Ratchet/NOTICE <target>/
cp Project_Nurse_Ratchet/HARDWARE.md <target>/
cp Project_Nurse_Ratchet/MANIFEST_NOTES.md <target>/
cp Project_Nurse_Ratchet/requiem.py <target>/
cp Project_Nurse_Ratchet/certification.json <target>/
cp Project_Nurse_Ratchet/PUBLIC_MANIFEST.json <target>/
# Edit PUBLIC_MANIFEST.json for target project specifics
```

### Step 2: Create/Update CI Workflow
```yaml
# .github/workflows/ci.yml - template from Project_Nurse_Ratchet
name: ci
on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.10", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Materialise public tree (if applicable)
        run: python tools/publicize.py
      - name: Install
        run: |
          python -m pip install --upgrade pip
          python -m pip install -e ".[dev]"
      - name: Verify public tree
        run: python tools/publicize.py --check
      - name: Unit tests
        run: python -m pytest -q
```

### Step 3: Create Pages Deploy Workflow
```yaml
# .github/workflows/pages-deploy.yml
name: Pages Deploy
on:
  push:
    branches: [main]
  workflow_dispatch:
permissions:
  contents: read
  pages: write
  id-token: write
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/configure-pages@v4
      - name: Build docs/site
        run: <project-specific-build-command>
      - uses: actions/upload-pages-artifact@v3
        with:
          path: <output-directory>
  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/deploy-pages@v4
```

### Step 4: Configure GitHub Repository Settings
```bash
# Via GitHub UI or API:
# 1. Settings → General → Description + Topics + Website
# 2. Settings → Features → Discussions (enable)
# 3. Settings → Branches → Branch protection rules (main branch)
# 4. Settings → Security → Dependabot alerts + CodeQL (enable)
```

### Step 5: Add Issue/PR Templates
```bash
# Copy from Project_Nurse_Ratchet/.github/
cp -r Project_Nurse_Ratchet/.github/ISSUE_TEMPLATE <target>/.github/
cp Project_Nurse_Ratchet/.github/PULL_REQUEST_TEMPLATE.md <target>/.github/
```

---

## LANDING HUB SPECIAL RULES (myzticalbabe.github.io)

This repo serves ONLY as GitHub Pages deployment target. It must ALSO have:

```
README.md                    # Document the landing hub purpose + atlas index
LICENSE                      # SOUL FORGE v1.0
CONTRIBUTING.md              # How to update atlas data
CHANGELOG.md                 # Deployment history
CODE_OF_CONDUCT.md           # Contributor Covenant
SECURITY.md                  # Security policy
.github/workflows/pages-deploy.yml  # Already exists
.github/workflows/ci.yml     # Validate atlas JSON schema
Topics:                      # landing-hub, atlas, domain-visualization, forest-index
Description:                 # "YGGDRASIL Forest Index - Interactive domain atlas for myzticalbabe ecosystem"
```

---

## WASM-EDUCATION SPECIAL FIXES

This repo has excellent README but missing GitHub About metadata:

```bash
# Set via GitHub Settings → General:
Description: "Cognitive & Semantic Learning Platform — WebAssembly-powered educational modules for cognitive science, computational neuroscience, graph theory, and educational psychology."
Topics: wasm, webassembly, education, cognitive-science, neuroscience, graph-theory, rust, go, tinygo, interactive-learning
Website: https://myzticalbabe.github.io/wasm-education/
```

Then add governance files from gold standard.

---

## VERIFICATION GATE — Run Before Any Release

```bash
# In target repo root:
python tools/publicize.py --check          # Verify manifest allowlist
python tools/nurse_ratchet_release_gate.py --check  # Or project-specific release gate
python -m pytest -q                         # All tests pass
# Check GitHub Pages deployed successfully
# Verify GitHub About shows description + topics
# Verify Discussions tab exists
# Verify branch protection on main
# Verify Dependabot + CodeQL enabled
```

---

## MAINTENANCE PROTOCOL

### When Adding a New Repository
1. Clone gold standard files from Project_Nurse_Ratchet
2. Customize PUBLIC_MANIFEST.json, CITATION.cff, HARDWARE.md, certification.json
3. Add CI/Pages workflows
4. Configure GitHub Settings
5. Run verification gate
6. Add to cross-repo table in ALL READMEs

### When Standards Evolve
1. Update Project_Nurse_Ratchet first (gold standard)
2. Update this document (PROFESSIONAL_PUBLIC_STANDARDS.md)
3. Propagate to all 20 repos via script
4. Run verification gate on each
5. Record in PMB + Engram

### Cross-Repo Table Maintenance
Every README.md must contain this table (update when repos added/removed):

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
| myzticalbabe.github.io | Landing Hub + Domain Atlas | Active |

---

## EVIDENCE BASIS

- **Gold Standard**: Project_Nurse_Ratchet has 14/14 governance files + release gate enforcement
- **Gap Analysis**: 2026-11-14 audit of all 25 myzticalbabe repos (20 main + 5 archived forks)
- **Critical Gaps Found**: 3 (landing hub metadata, wasm-education About, 19/20 missing community files)
- **Standards Codified**: This document + PMB goal #2006 + Engram architecture record

---

## REPRODUCIBILITY COMMAND

```bash
# One-command verification of any repo against standards
python tools/verify_public_standards.py <repo-path>
# Returns: PASS / FAIL with missing file list
```

The verification tool must check all 14 governance files, 2 workflows, GitHub metadata, and cross-repo table presence.

---

**This document is the single source of truth. Update it, then propagate. Never hand-edit generated files — fix the source and regenerate.**