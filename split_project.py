#!/usr/bin/env python3
"""
split_project.py — Extract components from src/ into fundable Project_* packages.

Auto-generates: CITATION.cff, CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md,
DISCLOSURE_POLICY.md, funding_targets (35 programs), overrides per program.

Usage:
  python split_project.py --component CORE/compliance --name Project_Compliance
  python split_project.py --priority nlnet,prototype,amazon,charted
  python split_project.py --all
"""

import json, os, sys, time, shutil, argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

SRC_ROOT = Path(__file__).parent / "src"
PROJECTS_ROOT = Path(__file__).parent
SCRIBE_PROFILES = Path(__file__).parent / "Project_Scribe" / "profiles"

# ── Component Registry ──────────────────────────────────────────────────
# Maps component path -> {description, category, grant_targets, keywords}

COMPONENTS = {
    "CORE/compliance": {
        "name": "Project_Compliance",
        "description": "13-component ComplianceOrchestrator: policy engine, formal verifier, state machine, sentinel gates, dual-ledger validation. Enterprise-grade compliance infrastructure.",
        "category": "infrastructure",
        "keywords": ["compliance", "policy-engine", "formal-verification", "state-machine", "sentinel", "dual-ledger"],
        "priority_grants": ["sloan_ospo", "sloan_ai_science", "ai_grant_oss", "enterprise"],
    },
    "CORE/inference": {
        "name": "Project_MultiProviderInference",
        "description": "11-provider unified LLM API: NimClient, InferenceBusPublisher, provider registry, automatic failover, retry/backoff, key masking.",
        "category": "infrastructure",
        "keywords": ["llm", "inference", "multi-provider", "failover", "api-gateway", "retry"],
        "priority_grants": ["ai_grant_oss", "openai_researcher", "anthropic_academic", "github_accelerator"],
    },
    "CORE/parallel": {
        "name": "Project_FreeThreadedRuntime",
        "description": "FreeThreadPool, WorkStealingPool, GIL-free Python 3.14t optimization. Thread-safe collections, benchmark runner, device affinity.",
        "category": "infrastructure",
        "keywords": ["free-threading", "work-stealing", "gil-free", "python-314t", "parallel", "thread-pool"],
        "priority_grants": ["nvidia_academic", "nsf", "python_foundation", "numfocus"],
    },
    "CORE/technique_wiring": {
        "name": "Project_NeuralWiring",
        "description": "System-level neural wiring map: LocalMemoryStore, DataPipelineWorm, DirectMemory, neural subsystems connection map.",
        "category": "ml-core",
        "keywords": ["neural-wiring", "memory-store", "data-pipeline", "direct-memory", "system-wiring"],
        "priority_grants": ["czi_eoss", "openscience_fund", "sloan_ai_science", "nvidia_academic"],
    },
    "DAEMONS/PAMS": {
        "name": "Project_PAMS_Daemon",
        "description": "Persistent AI Memory daemon with heartbeat, health monitoring, stale-record healing, audit trail, MCP server integration.",
        "category": "infrastructure",
        "keywords": ["persistent-memory", "daemon", "heartbeat", "health-monitoring", "mcp", "sqlite"],
        "priority_grants": ["nlnet", "open_source_fund", "mozilla", "openssf"],
    },
    "HORUS": {
        "name": "Project_HORUS_Monitoring",
        "description": "NETWORXZ, PROCESSZ, SystemZ, telemetry, observability, metrics collection, alerting, dashboard infrastructure.",
        "category": "infrastructure",
        "keywords": ["observability", "telemetry", "monitoring", "metrics", "alerting", "system-monitoring"],
        "priority_grants": ["cncf", "datadog", "observability_grants", "linux_foundation"],
    },
    "HYDRA": {
        "name": "Project_HYDRA_MLCluster",
        "description": "Adaptive ML cluster, ML platform management, MetaCluster v2 flat dispatch, parallel execution, work-stealing, thread safety.",
        "category": "ml-core",
        "keywords": ["ml-cluster", "meta-cluster", "adaptive", "distributed", "work-stealing", "hydra"],
        "priority_grants": ["ray", "anyscale", "ml_platform_grants", "distributed_systems"],
    },
    "INTERPRETERS": {
        "name": "Project_PolyglotInterpreters",
        "description": "Go, Node, Rust, Python, PowerShell runners for executing non-Python code within Azazael ecosystem.",
        "category": "infrastructure",
        "keywords": ["polyglot", "interpreters", "go", "node", "rust", "powershell", "code-execution"],
        "priority_grants": ["openjs_foundation", "rust_foundation", "python_foundation", "github_accelerator"],
    },
    "RUST_ACCEL": {
        "name": "Project_RustAccelerator",
        "description": "Rust-Python bridge, pyo3/maturin integration, high-performance Rust extensions for Python.",
        "category": "infrastructure",
        "keywords": ["rust", "pyo3", "maturin", "ffi", "acceleration", "python-extension"],
        "priority_grants": ["rust_foundation", "mozilla", "python_foundation", "github_accelerator"],
    },
    "RUST_WASM": {
        "name": "Project_WASM_Compiler",
        "description": "Python to WebAssembly compilation via Rust, wasm-bindgen, wasmtime integration.",
        "category": "infrastructure",
        "keywords": ["wasm", "webassembly", "rust", "wasm-bindgen", "wasmtime", "compilation"],
        "priority_grants": ["bytecode_alliance", "webassembly_grants", "rust_foundation", "mozilla"],
    },
    "SHARDS": {
        "name": "Project_ShardEngine",
        "description": "Content-addressed sharding, mirror/shatter/forge pipeline, deterministic golden-state hashes, SHARDEX integration.",
        "category": "ml-core",
        "keywords": ["sharding", "content-addressed", "mirror", "forge", "golden-state", "deterministic"],
        "priority_grants": ["protocol_labs", "ipfs", "filecoin", "openscience_fund", "sloan_ai_science"],
    },
    "ML/autodiff": {
        "name": "Project_AutoDiffEngine",
        "description": "Forward/reverse automatic differentiation, backprop, higher-order derivatives (Jacobian/Hessian), mygrad integration.",
        "category": "ml-core",
        "keywords": ["autodiff", "backprop", "jacobian", "hessian", "forward-mode", "reverse-mode", "mygrad"],
        "priority_grants": ["numfocus", "scipy", "nsf", "sloan_ai_science"],
    },
    "ML/nsga": {
        "name": "Project_NSGA_Optimizer",
        "description": "NSGA-II evolutionary optimization, Pareto front, genetic algorithms, EvolutionEngine, per-worm parameter tuning.",
        "category": "ml-core",
        "keywords": ["nsga-ii", "evolutionary", "pareto", "genetic-algorithm", "optimization", "nsga"],
        "priority_grants": ["evolutionary_computation", "gecco", "nsf", "ai_grant_oss"],
    },
    "ML/gosp": {
        "name": "Project_GOSP_Governance",
        "description": "3-script governance system, evidence directories, compliance scripts, governance orchestration.",
        "category": "ml-core",
        "keywords": ["governance", "evidence", "compliance", "orchestration", "policy"],
        "priority_grants": ["open_governance", "linux_foundation", "openssf", "ai_grant_oss"],
    },
    "ML/ml_platforms": {
        "name": "Project_ML_Platform_Integration",
        "description": "LM Studio integration, Q-learning, ONNX, Ray, harness, diagnostics, health monitoring, model analysis.",
        "category": "ml-core",
        "keywords": ["lm-studio", "q-learning", "onnx", "ray", "ml-platform", "diagnostics"],
        "priority_grants": ["anyscale", "ray", "ml_platform_grants", "github_accelerator"],
    },
    "ORCHESTRATION": {
        "name": "Project_EcosystemOrchestrator",
        "description": "ADLP SystemTools, MetaCluster, ecosystem crawler, HORUS monitoring, distributed systems coordination.",
        "category": "infrastructure",
        "keywords": ["orchestration", "meta-cluster", "ecosystem", "distributed", "coordination", "crawler"],
        "priority_grants": ["distributed_systems", "cncf", "anyscale", "sloan_ospo"],
    },
    "PSYCHE": {
        "name": "Project_PSYCHE_Consciousness",
        "description": "Consciousness framework, affect/emotion network, psychological network, rt_agent, rt_channel, compiled inference.",
        "category": "ml-core",
        "keywords": ["consciousness", "affect", "emotion", "psychological-network", "cognitive-science", "rt-agent"],
        "priority_grants": ["templeton", "cognitive_science", "neuroscience", "ai_grant_oss"],
    },
    "CODEX": {
        "name": "Project_CODEX_VideoEngine",
        "description": "Video generation with PIL/ffmpeg, CODEX Studio, CODEX Studio v3.1, scene management, animation patterns, batch generation.",
        "category": "ml-core",
        "keywords": ["video-generation", "pil", "ffmpeg", "codex", "animation", "studio"],
        "priority_grants": ["epic_megagrants", "nvidia_academic", "creative_grants", "github_accelerator"],
    },
    "RENDERING": {
        "name": "Project_Rendering_Pipeline",
        "description": "Puppeteer browser capture, session-specific HTML injection, optimal encoding (HEVC 1080p CRF 26-28), inject-record-encode workflow.",
        "category": "ml-core",
        "keywords": ["rendering", "puppeteer", "browser-capture", "hevc", "encoding", "video"],
        "priority_grants": ["epic_megagrants", "nvidia_academic", "creative_grants"],
    },
    "UTILITIES/BIBL": {
        "name": "Project_BIBL_Bibliographic",
        "description": "421K bibliographic entries, Zotero integration, citation management, academic reference system.",
        "category": "specialized",
        "keywords": ["bibliographic", "zotero", "citation", "academic", "reference", "421k"],
        "priority_grants": ["mellon", "neh", "library_grants", "academic_grants"],
    },
    "UTILITIES/TERENCE": {
        "name": "Project_TERENCE_Oracle",
        "description": "Oracle/verification system, invariant checking, fault detection, oracle suite, compliance verification.",
        "category": "specialized",
        "keywords": ["oracle", "verification", "invariants", "fault-detection", "compliance", "formal-methods"],
        "priority_grants": ["formal_methods", "nasa", "darpa", "nsf", "sloan_ospo"],
    },
    "UTILITIES/POINDEXTER": {
        "name": "Project_POINDEXTER_Indexer",
        "description": "Catalog/indexing system, SKILLS_CATALOG maintenance, inventory reconciliation, numbering conventions.",
        "category": "specialized",
        "keywords": ["indexing", "catalog", "inventory", "reconciliation", "numbering", "skills-catalog"],
        "priority_grants": ["search_infra", "library_grants", "academic_grants", "openssf"],
    },
    "UTILITIES/TARBABY": {
        "name": "Project_TARBABY_FileSearch",
        "description": "File search, forensic file operations, forensic file search, file system forensics.",
        "category": "specialized",
        "keywords": ["file-search", "forensics", "file-operations", "digital-forensics", "search"],
        "priority_grants": ["digital_forensics", "nsf", "library_grants", "academic_grants"],
    },
    "UTILITIES/KLINK": {
        "name": "Project_KLINK_Protocol",
        "description": "Klink protocol implementation, protocol libraries, network protocol libraries.",
        "category": "specialized",
        "keywords": ["klink", "protocol", "network", "protocol-libraries"],
        "priority_grants": ["protocol_labs", "ipfs", "filecoin", "web3_grants"],
    },
    "UTILITIES/Loggers": {
        "name": "Project_Loggers_Telemetry",
        "description": "Structured logging, TELEMETRYZ, METRICZ, HEALTHZ, OPTIMIZ, performance monitoring, session memory.",
        "category": "specialized",
        "keywords": ["logging", "telemetry", "metrics", "health", "performance", "monitoring"],
        "priority_grants": ["observability_grants", "datadog", "new_relic", "cncf"],
    },
    "UTILITIES/PERSEPHONE": {
        "name": "Project_PERSEPHONE_Sync",
        "description": "Environment/sync infrastructure, cross-platform sync, cross-distro sync, environment topology.",
        "category": "specialized",
        "keywords": ["sync", "environment", "cross-platform", "infrastructure", "topology"],
        "priority_grants": ["infrastructure_grants", "cncf", "linux_foundation", "openssf"],
    },
}

# ── Universal Funding Targets (35 programs) ─────────────────────────────
UNIVERSAL_FUNDING_TARGETS = {
    "epic_megagrants": {"max_amount": 150000, "type": "cash_grant", "deadline": "2026-09-04", "priority": "high"},
    "nlnet": {"max_amount": 50000, "type": "cash_grant", "deadline": "2026-11-03", "priority": "high"},
    "github_secure_oss": {"max_amount": 10000, "type": "cash_grant", "deadline": "rolling", "priority": "high"},
    "github_accelerator": {"max_amount": 40000, "type": "program+credits", "deadline": "next_cohort", "priority": "high"},
    "google_cloud_research": {"max_amount": 5000, "type": "cloud_credits", "deadline": "rolling", "priority": "medium"},
    "google_startups_ai": {"max_amount": 350000, "type": "cloud_credits", "deadline": "rolling", "priority": "high"},
    "aws_activate": {"max_amount": 200000, "type": "cloud_credits", "deadline": "rolling", "priority": "high"},
    "microsoft_startups": {"max_amount": 150000, "type": "cloud_credits", "deadline": "rolling", "priority": "high"},
    "cloudflare_startups": {"max_amount": 350000, "type": "cloud_credits", "deadline": "rolling", "priority": "high"},
    "czi_eoss": {"max_amount": 200000, "type": "cash_grant", "deadline": "next_cycle", "priority": "medium"},
    "openscience_fund": {"max_amount": 1000000, "type": "cash_grant", "deadline": "2026-05-11", "priority": "high"},
    "sloan_ospo": {"max_amount": 750000, "type": "cash_grant", "deadline": "loi_cycle", "priority": "medium"},
    "sloan_ai_science": {"max_amount": 400000, "type": "cash_grant", "deadline": "rolling", "priority": "high"},
    "nvidia_academic": {"max_amount": "30000_h100_hrs", "type": "gpu_compute", "deadline": "quarterly", "priority": "high"},
    "nvidia_inception": {"max_amount": "free_credits", "type": "cloud_credits", "deadline": "rolling", "priority": "medium"},
    "aws_activate_ai": {"max_amount": "200000+", "type": "cloud_credits", "deadline": "rolling", "priority": "high"},
    "google_startups": {"max_amount": 350000, "type": "cloud_credits", "deadline": "rolling", "priority": "high"},
    "microsoft_startups": {"max_amount": 150000, "type": "cloud_credits", "deadline": "rolling", "priority": "high"},
    "cloudflare_startups": {"max_amount": 350000, "type": "cloud_credits", "deadline": "rolling", "priority": "high"},
    "github_accelerator": {"max_amount": 40000, "type": "program+credits", "deadline": "next_cohort", "priority": "high"},
    "ai_grant_oss": {"max_amount": 50000, "type": "cash_or_compute", "deadline": "rolling", "priority": "high"},
    "raais_foundation": {"max_amount": "3_month_grant", "type": "cash_grant", "deadline": "rolling", "priority": "medium"},
    "prototype_fund": {"max_amount": 95000, "type": "cash_grant", "deadline": "2026-11-30", "priority": "high"},
    "amazon_security": {"max_amount": 80000, "type": "cash_plus_credits", "deadline": "2026-11-11", "priority": "high"},
    "catalyst_fund": {"max_amount": 50000, "type": "cash_grant", "deadline": "2026-12-31", "priority": "medium"},
    "opensats": {"max_amount": "rolling", "type": "cash_grant", "deadline": "rolling", "priority": "medium"},
    "humanity_ai": {"max_amount": 1000000, "type": "cash_grant", "deadline": "2026-10-21", "priority": "low"},
    "unicef_venture": {"max_amount": 100000, "type": "cash_grant", "deadline": "2026-11-11", "priority": "low"},
    "wellcome_trust": {"max_amount": "large", "type": "cash_grant", "deadline": "rolling", "priority": "low"},
    "open_science_nl": {"max_amount": 15000, "type": "cash_grant", "deadline": "2026-12-10", "priority": "medium"},
    "charted_fund": {"max_amount": 12500, "type": "cash_grant", "deadline": "2026-11-15", "priority": "medium"},
    "ukomain": {"max_amount": 50000, "type": "cash_grant", "deadline": "2026-11-06", "priority": "high"},
    "linux_australia": {"max_amount": "varies", "type": "cash_grant", "deadline": "2026-11-15", "priority": "low"},
    "freecad_grant": {"max_amount": 10000, "type": "cash_grant", "deadline": "2026-11-15", "priority": "low"},
    "anthropic_claude": {"max_amount": "fellow_plus_10k", "type": "fellowship", "deadline": "rolling", "priority": "low"},
    "schmidt_ai_fellowship": {"max_amount": "fellowship", "type": "fellowship", "deadline": "2026-10", "priority": "low"},
    "openai_researcher": {"max_amount": "api_credits", "type": "api_credits", "deadline": "rolling", "priority": "low"},
    "anthropic_academic": {"max_amount": "api_credits", "type": "api_credits", "deadline": "rolling", "priority": "low"},
}

# ── Template Files ──────────────────────────────────────────────────────

CITATION_TEMPLATE = """cff-version: 1.2.0
message: "If you use this software, cite it as below. If you cite a measured figure, cite the commit and the split it came from."
title: "{name}: {description}"
version: "0.1.0"
date-released: "{date}"
license: "CDDL-1.1"
type: software
abstract: >-
  {description}
authors:
  - name: "Azazael Contributors"
keywords:
{keywords}
references:
  - type: software
    title: "Azazael Core"
    notes: "Parent framework providing core infrastructure."
    url: "https://github.com/myzticalbabe/azazael"
"""

CONTRIBUTING_TEMPLATE = """# Contributing to {name}

Thank you for considering a contribution to {name}!

## Quick Start

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-change`
3. Make your changes
4. Run the test suite: `python -m pytest tests/ -v`
5. Submit a pull request

## Code Standards

- **License**: All contributions must be compatible with CDDL-1.1 (the project license)
- **Python**: 3.10+ (stdlib-only preferred, minimal runtime dependencies)
- **Style**: Follow the existing code style in the repository
- **Tests**: New functionality must include tests
- **Documentation**: Update relevant docs with your changes

## What We Accept

- Bug fixes
- Documentation improvements
- New features aligned with the component's purpose
- Performance improvements
- Integration with other Azazael components

## Pull Request Process

1. Ensure all tests pass
2. The maintainers will review and merge

## Reporting Issues

Use the GitHub issue tracker. Please include:
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version)

## Code of Conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

## Security

See [SECURITY.md](SECURITY.md) for reporting security vulnerabilities.

## License

By contributing, you agree that your contributions will be licensed under CDDL-1.1.
"""

CODE_OF_CONDUCT_TEMPLATE = """# Contributor Covenant Code of Conduct

## Our Pledge

We as members, contributors, and leaders pledge to make participation in our
community a harassment-free experience for everyone, regardless of age, body
size, visible or invisible disability, ethnicity, sex characteristics, gender
identity and expression, level of experience, education, socio-economic status,
nationality, personal appearance, race, religion, or sexual identity
and orientation.

We pledge to act and interact in ways that contribute to an open, welcoming,
diverse, inclusive, and healthy community.

## Our Standards

Examples of behavior that contributes to a positive environment for our
community include:

* Demonstrating empathy and kindness toward other people
* Being respectful of differing opinions, viewpoints, and experiences
* Giving and gracefully accepting constructive feedback
* Accepting responsibility and apologizing to those affected by our mistakes,
  and learning from the experience
* Focusing on what is best not just for us as individuals, but for the
  overall community

Examples of unacceptable behavior include:

* The use of sexualized language or imagery, and sexual attention or
  advances of any kind
* Trolling, insulting or derogatory comments, and personal or political attacks
* Public or private harassment
* Publishing others' private information, such as a physical or email
  address, without their explicit permission
* Other conduct which could reasonably be considered inappropriate in a
  professional setting

## Enforcement Responsibilities

Community leaders are responsible for clarifying and enforcing our standards of
acceptable behavior and will take appropriate and fair corrective action in
response to any behavior that they deem inappropriate, threatening, offensive,
or harmful.

Community leaders have the right and responsibility to remove, edit, or reject
comments, commits, code, wiki edits, issues, and other contributions that are
not aligned to this Code of Conduct, and will communicate reasons for
moderation decisions when appropriate.

## Scope

This Code of Conduct applies within all community spaces, and also applies
when an individual is officially representing the community in public spaces.

## Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be
reported to the community leaders responsible for enforcement at
**conduct@azazael.local**. All complaints will be reviewed and investigated
promptly and fairly.

All community leaders are obligated to respect the privacy and security of the
reporter of any incident.

## Enforcement Guidelines

Community leaders will follow these Community Impact Guidelines in determining
the consequences for any action they deem in violation of this Code of Conduct:

### 1. Correction
**Community Impact**: Use of inappropriate language or other behavior deemed
unprofessional or unwelcome in the community.
**Consequence**: A private, written warning from community leaders.

### 2. Warning
**Community Impact**: A violation through a single incident or series of actions.
**Consequence**: A warning with consequences for continued behavior. No
interaction with the people involved for a specified period of time.

### 3. Temporary Ban
**Community Impact**: A serious violation of community standards.
**Consequence**: A temporary ban from any sort of interaction or public
communication with the community for a specified period of time.

### 4. Permanent Ban
**Community Impact**: Demonstrating a pattern of violation of community
standards.
**Consequence**: A permanent ban from any sort of public interaction within
the community.

## Attribution

This Code of Conduct is adapted from the [Contributor Covenant][homepage],
version 2.1, available at
[https://www.contributor-covenant.org/version/2/1/code_of_conduct.html][v2.1].

[homepage]: https://www.contributor-covenant.org
[v2.1]: https://www.contributor-covenant.org/version/2/1/code_of_conduct.html
"""

SECURITY_TEMPLATE = """# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

**Do not report security vulnerabilities via public GitHub issues.**

Instead, please report them via email to **security@azazael.local**.

Include the following information:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Any known workarounds

We will acknowledge receipt within 48 hours and provide a status update
within 5 business days.

## Security Model

{name} is a {category} component with the following security properties:

1. **Minimal dependencies** — stdlib-only where possible
2. **No network access** — unless explicitly required for the component's function
3. **No arbitrary code execution** — does not eval or execute untrusted code
4. **Input validation** — all external inputs validated at boundaries

## Disclosure Policy

We follow coordinated disclosure. Once a vulnerability is confirmed and a
fix is available, we will:

1. Release a patch
2. Publish a security advisory
3. Credit the reporter (unless they request anonymity)

## Scope

This policy covers the component's source code and any bundled dependencies.
"""

DISCLOSURE_TEMPLATE = """# Disclosure Policy

## Purpose

This policy governs how {name} handles sensitive information encountered during
its operation as a {category} component in the Azazael ecosystem.

## What We Do Not Distribute

{name} **does not distribute**:

- Raw primary data from analyzed systems (unless explicitly allowed by license)
- Secrets, API keys, credentials found during operation
- Proprietary algorithms or business logic from analyzed codebases
- Any material about identifiable individuals that is not already public

## What We Do Distribute

- The component **METHOD** (algorithms, patterns, techniques)
- Open-source tooling for {category} operations
- Documentation and examples using synthetic/public data
- Configuration templates

## Handling Sensitive Data

If the component encounters sensitive data (secrets, keys, PII, proprietary code):

1. **Stop** — do not commit, log, or report the sensitive data
2. **Redact** — remove or hash the sensitive identifiers
3. **Report** — notify the project maintainers via security@azazael.local
4. **Verify** — ensure no sensitive data would be distributed

## Attribution

The Contributor Covenant text in CODE_OF_CONDUCT.md is used under
CC BY 4.0 with attribution retained in that file.

## Contact

For questions about this policy, contact **disclosure@azazael.local**.
"""


def format_keywords(keywords: List[str]) -> str:
    return "\n".join(f"  - {k}" for k in keywords)


def build_overrides(component: Dict, name: str) -> Dict:
    """Build program-specific overrides for a component."""
    overrides = {}
    
    # Base overrides for priority grants
    for grant in component.get("priority_grants", []):
        if grant in UNIVERSAL_FUNDING_TARGETS:
            target = UNIVERSAL_FUNDING_TARGETS[grant]
            overrides[grant] = {
                "project_description": component["description"],
                "requested_amount": str(target["max_amount"]).replace("_", " "),
                "equipment_budget": "10000",
                "equipment_justification": f"Hyper-Edge DEV box: RTX 4090 (24GB) + 128GB DDR5 + 4TB NVMe for {name} development.",
            }
    
    # Add nlnet override (always relevant for open source)
    if "nlnet" in UNIVERSAL_FUNDING_TARGETS:
        target = UNIVERSAL_FUNDING_TARGETS["nlnet"]
        overrides["nlnet"] = {
            "project_description": component["description"],
            "call": "Open_Call",
            "website": f"https://github.com/myzticalbabe/azazael/tree/main/{name}",
            "abstract": component["description"],
            "requested_amount": "50000",
            "equipment_budget": "10000",
            "equipment_justification": f"Hyper-Edge DEV box: RTX 4090 (24GB) + 128GB DDR5 + 4TB NVMe for {name}. NLnet NGI0 allows €50K total; €10K equipment.",
            "use": component["description"],
            "comparison": "Unlike monolithic tools, this component is modular, stdlib-only, and composes with the Azazael ecosystem.",
            "challenges": "Ensuring zero-dependency stdlib compatibility across Python versions.",
            "ecosystem": f"Integrates with Azazael core, composes with {len(COMPONENTS)} other extractable components.",
            "experience": "Team has built forensic investigation, code quality, game engine, and ML infrastructure tools.",
            "other_funding": "No other funding currently.",
            "requestor_name": "Clint Oxford",
            "contact_email": "clintonoxford47@gmail.com",
            "organization": "Azazael",
            "country": "US",
            "used_ai": "I have used generative AI in writing this proposal",
            "ai_prompt": f"Used AI for {name} architecture design and component extraction logic.",
            "codebase_used_ai": "yes",
            "entity": "Individual",
        }
    
    return overrides


def create_project(name: str, component: Dict, output_dir: Path) -> None:
    """Create a complete Project_* directory with all metadata files."""
    project_dir = output_dir / name
    project_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    (project_dir / "tools").mkdir(exist_ok=True)
    (project_dir / "tests").mkdir(exist_ok=True)
    (project_dir / "docs").mkdir(exist_ok=True)
    
    # Copy source files if they exist
    src_path = SRC_ROOT / component.get("src_path", "")
    if src_path.exists():
        dst = project_dir / "tools"
        if src_path.is_dir():
            shutil.copytree(src_path, dst / src_path.name, dirs_exist_ok=True)
        else:
            shutil.copy2(src_path, dst / src_path.name)
    
    # Generate metadata
    date = time.strftime("%Y-%m-%d")
    keywords = format_keywords(component["keywords"])
    overrides = build_overrides(component, name)
    
    # CITATION.cff
    citation = CITATION_TEMPLATE.format(
        name=name,
        description=component["description"],
        date=date,
        keywords=keywords,
    )
    (project_dir / "CITATION.cff").write_text(citation)
    
    # CONTRIBUTING.md
    contributing = CONTRIBUTING_TEMPLATE.format(name=name)
    (project_dir / "CONTRIBUTING.md").write_text(contributing)
    
    # CODE_OF_CONDUCT.md
    (project_dir / "CODE_OF_CONDUCT.md").write_text(CODE_OF_CONDUCT_TEMPLATE)
    
    # SECURITY.md
    security = SECURITY_TEMPLATE.format(name=name, category=component["category"])
    (project_dir / "SECURITY.md").write_text(security)
    
    # DISCLOSURE_POLICY.md
    disclosure = DISCLOSURE_TEMPLATE.format(name=name, category=component["category"])
    (project_dir / "DISCLOSURE_POLICY.md").write_text(disclosure)
    
    # Profile JSON for Scribe
    profile = {
        "project_name": name,
        "project_description": component["description"],
        "project_url": f"https://github.com/myzticalbabe/azazael/tree/main/{name}",
        "github_url": f"https://github.com/myzticalbabe/azazael/tree/main/{name}",
        "team_size": 1,
        "funding_amount": "$50,000",
        "contact_name": "Clint Oxford",
        "contact_email": "clintonoxford47@gmail.com",
        "license": "CDDL-1.1",
        "pitch_deck": f"profiles/{name.lower()}_pitch.pdf",
        "prototype_video": f"profiles/{name.lower()}_demo.mp4",
        "github_repo": f"https://github.com/myzticalbabe/azazael/tree/main/{name}",
        "proposal": f"profiles/{name.lower()}_proposal.md",
        "budget": f"profiles/{name.lower()}_budget.xlsx",
        "timeline": f"profiles/{name.lower()}_timeline.md",
        "security_audit": "",
        "threat_model": "",
        "adoption_metrics": "",
        "maintenance_plan": "",
        "budget_breakdown": "",
        "milestones": "",
        "funding_targets": UNIVERSAL_FUNDING_TARGETS,
        "overrides": overrides,
    }
    
    SCRIBE_PROFILES.mkdir(parents=True, exist_ok=True)
    (SCRIBE_PROFILES / f"{name.lower()}_profile.json").write_text(
        json.dumps(profile, indent=2)
    )
    
    print(f"  Created {name} at {project_dir}")
    print(f"  Profile saved to {SCRIBE_PROFILES / f'{name.lower()}_profile.json'}")


def main():
    parser = argparse.ArgumentParser(description="Split Azazael components into fundable Project_* packages")
    parser.add_argument("--component", help="Single component path (e.g., CORE/compliance)")
    parser.add_argument("--name", help="Project name (e.g., Project_Compliance)")
    parser.add_argument("--priority", help="Comma-separated grant priorities (nlnet,prototype,amazon,charted)")
    parser.add_argument("--all", action="store_true", help="Generate all components")
    parser.add_argument("--list", action="store_true", help="List available components")
    parser.add_argument("--output", default=str(PROJECTS_ROOT), help="Output directory")
    
    args = parser.parse_args()
    
    if args.list:
        print("Available components:")
        for path, comp in COMPONENTS.items():
            print(f"  {path:30} -> {comp['name']:30} [{comp['category']}]")
        return 0
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    targets = []
    
    if args.component and args.name:
        # Single component
        if args.component not in COMPONENTS:
            print(f"Unknown component: {args.component}")
            return 1
        comp = COMPONENTS[args.component].copy()
        comp["src_path"] = args.component
        targets.append((args.name, comp))
    
    elif args.priority:
        # Priority grants -> matching components
        priorities = [p.strip() for p in args.priority.split(",")]
        for path, comp in COMPONENTS.items():
            if any(p in comp.get("priority_grants", []) for p in priorities):
                comp_copy = comp.copy()
                comp_copy["src_path"] = path
                targets.append((comp["name"], comp_copy))
    
    elif args.all:
        for path, comp in COMPONENTS.items():
            comp_copy = comp.copy()
            comp_copy["src_path"] = path
            targets.append((comp["name"], comp_copy))
    
    else:
        parser.print_help()
        return 1
    
    print(f"Generating {len(targets)} projects...")
    for name, comp in targets:
        create_project(name, comp, Path(args.output))
    
    print(f"\nDone. {len(targets)} projects created.")
    print(f"Scribe profiles saved to {SCRIBE_PROFILES}")
    return 0


if __name__ == "__main__":
    sys.exit(main())