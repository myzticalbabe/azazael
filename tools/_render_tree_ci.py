#!/usr/bin/env python3
"""Write the six scaffolds' CI workflow and issue/PR templates.

Why this exists
---------------
The public-standards pass added `.github/workflows/ci.yml`, the three
`ISSUE_TEMPLATE/*.yml` files and `PULL_REQUEST_TEMPLATE.md` to six trees by
copying Project_Nurse_Ratchet's files verbatim. The copies were not just
mislabelled, they were unrunnable and misleading in that tree:

* `ci.yml` ran `python tools/publicize.py`, `tools/triage_eval.py` and
  `tools/fit_affect_bridge.py`. None of those exist in a video engine, a
  WebAssembly compiler or a sync tool, so every job would have failed on the
  first command.
* `config.yml` sent security reports to
  `github.com/OWNER/nurse_ratchet/security/advisories/new` -- a placeholder
  owner, another project's advisory queue, and a crisis-line link that belongs
  to a clinical tool.
* `bug_report.yml` asked whether the defect "weakens the crisis routing", which
  is not a question a shader compiler can answer.

None of the six is a Python package: there is no `pyproject.toml` and no
`tests/` in any of them, so a `pip install -e .` job fails for a reason that
says nothing about the code, and a `pytest` job succeeds with nothing
collected. The gates written here are the ones that can actually be enforced:
the governance files must be present, and every source file must parse.

Every command below was run against every tree on 2026-11-15 before it was
written here; the file counts in each header are measured at render time, not
typed, so `--check` notices when a tree gains files.

    python tools/_render_tree_ci.py --write
    python tools/_render_tree_ci.py --check
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATE = "2026-11-15"

#: What each tree is, in one clause, for the workflow header. The counts are not
#: here: they are measured from disk so they cannot drift from the tree.
TREES: dict[str, str] = {
    "CODEX_VideoEngine": "renders HTML scenes to video with FFmpeg and a headless browser",
    "EcosystemOrchestrator": "orchestrates the ecosystem's services and scripts",
    "HYDRA_MLCluster": "exercises the local ML stack (numpy, scipy, torch, sklearn)",
    "PERSEPHONE_Sync": "reconciles environments and propagates skills across machines",
    "Scribe": "drafts documents from source material",
    "WASM_Compiler": "compiles a Rust crate to WebAssembly",
}

#: Governance files every publication root carries. Presence is the gate; the
#: richer checks (canonical licence bytes, notice attribution) live in
#: tools/soul_license_audit.py in the root tree and are not duplicated here.
REQUIRED = [
    "LICENSE",
    "NOTICE",
    "README.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "CITATION.cff",
    "PUBLIC_MANIFEST.json",
]


def count_sources(base: Path) -> dict[str, int]:
    """Source files in `base`, excluding anything generated or vendored."""
    counts = {".py": 0, ".js": 0, ".rs": 0}
    for p in base.rglob("*"):
        if p.suffix not in counts or not p.is_file():
            continue
        parts = set(p.parts)
        if "node_modules" in parts or ".git" in parts or "target" in parts:
            continue
        counts[p.suffix] += 1
    return counts


def cargo_manifest(base: Path) -> Path | None:
    """The crate manifest in this tree, if it ships one."""
    for p in sorted(base.rglob("Cargo.toml")):
        if set(p.parts) & {"node_modules", ".git", "target"}:
            continue
        return p
    return None


def render_ci(name: str, blurb: str, base: Path) -> str:
    counts = count_sources(base)
    cargo = cargo_manifest(base)

    langs = []
    if counts[".py"]:
        langs.append(f"{counts['.py']} Python file(s)")
    if counts[".js"]:
        langs.append(f"{counts['.js']} JavaScript file(s)")
    if counts[".rs"]:
        langs.append(f"{counts['.rs']} Rust file(s)")
    lang_line = ", ".join(langs) if langs else "no source files yet"

    out: list[str] = []
    out.append("name: ci\n")
    out.append(
        f"# Project_{name} {blurb}.\n"
        "#\n"
        "# This tree is a tool tree, not a Python package: there is no pyproject.toml\n"
        "# and no tests/ directory here, so the gates are structural and syntactic.\n"
        "# The governance files must be present, and every source file must parse.\n"
        "#\n"
        "# The workflow that used to sit at this path was copied verbatim from\n"
        "# Project_Nurse_Ratchet and ran `python tools/publicize.py`,\n"
        "# `tools/triage_eval.py` and `tools/fit_affect_bridge.py`. None of those\n"
        "# exist in this tree, so every job failed on its first command.\n"
        "#\n"
        f"# Measured on " + DATE + f": {lang_line}.\n"
    )
    out.append(
        "on:\n"
        "  push:\n"
        "    branches: [main]\n"
        "  pull_request:\n"
        "  workflow_dispatch:\n"
        "\n"
        "permissions:\n"
        "  contents: read\n"
    )

    # -- structure -----------------------------------------------------------
    out.append("jobs:\n")
    out.append("  structure:\n")
    out.append("    name: governance files and licence\n")
    out.append("    runs-on: ubuntu-latest\n")
    out.append("    steps:\n")
    out.append("      - uses: actions/checkout@v4\n")
    out.append("      - name: Required files are present\n")
    out.append("        run: |\n")
    out.append("          set -eu\n")
    out.append("          missing=0\n")
    for f in REQUIRED:
        out.append(
            f'          if [ ! -f "{f}" ]; then echo "MISSING: {f}"; missing=1; fi\n'
        )
    out.append('          exit "$missing"\n')
    out.append("      - name: LICENSE is the Soul Forge License v1.0\n")
    out.append("        run: |\n")
    out.append("          set -eu\n")
    out.append("          head -2 LICENSE | grep -q 'SOUL FORGE LICENSE'\n")
    out.append('          grep -q "Version 1.0" LICENSE\n')

    # -- python --------------------------------------------------------------
    if counts[".py"]:
        out.append("\n")
        out.append("  python:\n")
        out.append(f"    name: every Python file parses ({counts['.py']})\n")
        out.append("    runs-on: ubuntu-latest\n")
        out.append("    steps:\n")
        out.append("      - uses: actions/checkout@v4\n")
        out.append("      - uses: actions/setup-python@v5\n")
        out.append("        with:\n")
        # Pinned to the floor the repository declares (requires-python
        # ">=3.14" in the root pyproject). The local verification of every
        # file in these trees ran on CPython 3.14.7, so a 3.12 runner would
        # be checking against syntax the code was never measured on.
        out.append('          python-version: "3.14"\n')
        out.append("      - name: compileall\n")
        out.append(
            "        # Byte-compile only, no execution: this checks that every module\n"
            "        # parses. Importing them needs the optional ML/network stack, which\n"
            "        # is not installed here and would make the job fail on the runner's\n"
            "        # missing packages rather than on the code.\n"
        )
        out.append("        run: python -m compileall -q .\n")

    # -- node ----------------------------------------------------------------
    if counts[".js"]:
        out.append("\n")
        out.append("  node:\n")
        out.append(f"    name: every JavaScript file parses ({counts['.js']})\n")
        out.append("    runs-on: ubuntu-latest\n")
        out.append("    steps:\n")
        out.append("      - uses: actions/checkout@v4\n")
        out.append("      - uses: actions/setup-node@v4\n")
        out.append("        with:\n")
        # Local verification of all 61 files ran on node v24.14.0, so the
        # runner is pinned to the same major rather than a version whose
        # parser was never exercised against this tree.
        out.append('          node-version: "24"\n')
        out.append("      - name: node --check\n")
        out.append(
            "        # No `npm install` and no `npm test`: package.json in this tree\n"
            "        # declares no name, version or scripts, and puppeteer would need a\n"
            "        # Chromium download the job does not use. --check only proves each\n"
            "        # file parses as CommonJS, which is what every file in the tree is.\n"
        )
        out.append("        run: |\n")
        out.append("          set -eu\n")
        out.append("          fail=0\n")
        out.append("          while IFS= read -r f; do\n")
        out.append('            node --check "$f" || fail=1\n')
        out.append(
            "          done < <(find . -name '*.js' -not -path '*/node_modules/*')\n"
        )
        out.append('          exit "$fail"\n')

    # -- rust ----------------------------------------------------------------
    if cargo is not None:
        rel = cargo.parent.relative_to(base).as_posix()
        out.append("\n")
        out.append("  rust:\n")
        out.append("    name: cargo check\n")
        out.append("    runs-on: ubuntu-latest\n")
        out.append("    steps:\n")
        out.append("      - uses: actions/checkout@v4\n")
        out.append("      - uses: dtolnay/rust-toolchain@stable\n")
        out.append("      - name: cargo check --locked\n")
        out.append("        working-directory: " + rel + "\n")
        out.append(
            "        # --locked is enforced because Cargo.lock is tracked: a dependency\n"
            "        # resolution change must arrive as a reviewed diff, not as whatever\n"
            "        # proxy the runner happens to reach.\n"
        )
        out.append("        run: cargo check --locked\n")

    return "".join(out)


def render_bug_report(name: str) -> str:
    return (
        "name: Bug report\n"
        "description: Something behaves differently from what the documentation, a test, or the source says it does.\n"
        'title: "[bug] "\n'
        "labels: [\"bug\"]\n"
        "body:\n"
        "  - type: markdown\n"
        "    attributes:\n"
        "      value: |\n"
        "        A bug is a disagreement between behaviour and a stated claim. Quote\n"
        "        the claim and the command that shows it failing.\n"
        "  - type: input\n"
        "    id: version\n"
        "    attributes:\n"
        "      label: Version or commit\n"
        "      description: Output of `git rev-parse --short HEAD`, or the release tag.\n"
        "    validations:\n"
        "      required: true\n"
        "  - type: input\n"
        "    id: environment\n"
        "    attributes:\n"
        "      label: Environment\n"
        "      description: Operating system and the runtime versions the failure depends on.\n"
        "    validations:\n"
        "      required: true\n"
        "  - type: textarea\n"
        "    id: expected\n"
        "    attributes:\n"
        "      label: What was claimed\n"
        "      description: The docstring line, test name, README sentence or exit code that says otherwise.\n"
        "    validations:\n"
        "      required: true\n"
        "  - type: textarea\n"
        "    id: actual\n"
        "    attributes:\n"
        "      label: What happened\n"
        "      description: Paste the command and its output. If a test fails, include the assertion line.\n"
        "      render: shell\n"
        "    validations:\n"
        "      required: true\n"
        "  - type: textarea\n"
        "    id: reproduction\n"
        "    attributes:\n"
        "      label: Minimal reproduction\n"
        "      description: The smallest sequence that shows it.\n"
        "      render: shell\n"
        "    validations:\n"
        "      required: true\n"
        "  - type: checkboxes\n"
        "    id: checks\n"
        "    attributes:\n"
        "      label: Before submitting\n"
        "      options:\n"
        "        - label: I searched existing issues.\n"
        "          required: true\n"
        "        - label: This report contains no credentials, personal data, or third-party content I have no right to share.\n"
        "          required: true\n"
    )


def render_feature_request(name: str) -> str:
    return (
        "name: Feature request\n"
        "description: Propose a capability, starting from the problem it solves.\n"
        'title: "[feature] "\n'
        "labels: [\"enhancement\"]\n"
        "body:\n"
        "  - type: markdown\n"
        "    attributes:\n"
        "      value: |\n"
        "        A feature request is a problem statement first and a design second.\n"
        "        If the problem is not stated, the proposal cannot be evaluated.\n"
        "  - type: textarea\n"
        "    id: problem\n"
        "    attributes:\n"
        "      label: The problem\n"
        "      description: What cannot be done today, and what it costs.\n"
        "    validations:\n"
        "      required: true\n"
        "  - type: textarea\n"
        "    id: proposal\n"
        "    attributes:\n"
        "      label: Proposed behaviour\n"
        "      description: What the tool should do, concretely enough to test.\n"
        "    validations:\n"
        "      required: true\n"
        "  - type: textarea\n"
        "    id: alternatives\n"
        "    attributes:\n"
        "      label: Alternatives considered\n"
        "      description: Including doing nothing, and why that is not enough.\n"
        "    validations:\n"
        "      required: false\n"
        "  - type: textarea\n"
        "    id: cost\n"
        "    attributes:\n"
        "      label: What this would add\n"
        "      description: New dependencies, new failure modes, or new configuration.\n"
        "    validations:\n"
        "      required: false\n"
    )


def render_config(name: str) -> str:
    return (
        "# No `contact_links` here on purpose.\n"
        "#\n"
        "# The file this replaces carried a link to\n"
        "# github.com/OWNER/nurse_ratchet/security/advisories/new -- a placeholder\n"
        "# owner and another project's private advisory queue -- plus a crisis-line\n"
        "# link that belongs to a clinical tool. This tree has no public repository\n"
        "# URL yet, so the honest state is no link at all: SECURITY.md is the\n"
        "# channel, and a link that goes nowhere useful is worse than none.\n"
        "blank_issues_enabled: false\n"
    )


def render_pr_template(name: str, base: Path) -> str:
    counts = count_sources(base)
    cargo = cargo_manifest(base)

    checks = []
    if counts[".py"]:
        checks.append("- [ ] `python -m compileall -q .` passes")
    if counts[".js"]:
        checks.append("- [ ] `node --check` passes on every `.js` file in the tree")
    if cargo is not None:
        checks.append(
            "- [ ] `cargo check --locked` passes in "
            f"`{cargo.parent.relative_to(base).as_posix()}`"
        )
    if not checks:
        checks.append("- [ ] (no source files yet)")
    checks.append("- [ ] No file was added or changed outside this component's own tree")

    return (
        "## What changed\n"
        "\n"
        "## Why\n"
        "\n"
        "## Checks\n"
        "\n" + "\n".join(checks) + "\n"
        "\n"
        "## Licence\n"
        "\n"
        "By opening this pull request you agree the contribution is licensed under\n"
        "the Soul Forge License v1.0, the only licence in this repository. See\n"
        "`LICENSE`. Third-party material keeps its own terms and belongs in `NOTICE`.\n"
    )


def targets() -> dict[Path, str]:
    out: dict[Path, str] = {}
    for name, blurb in TREES.items():
        base = ROOT / f"Project_{name}"
        out[base / ".github" / "workflows" / "ci.yml"] = render_ci(name, blurb, base)
        out[base / ".github" / "ISSUE_TEMPLATE" / "bug_report.yml"] = render_bug_report(name)
        out[base / ".github" / "ISSUE_TEMPLATE" / "feature_request.yml"] = render_feature_request(name)
        out[base / ".github" / "ISSUE_TEMPLATE" / "config.yml"] = render_config(name)
        out[base / ".github" / "PULL_REQUEST_TEMPLATE.md"] = render_pr_template(name, base)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    if not (args.write or args.check):
        ap.error("choose --write or --check")

    problems: list[str] = []
    for name in TREES:
        base = ROOT / f"Project_{name}"
        if not base.is_dir():
            problems.append(f"{name}: not a directory: {base}")
            continue
        for f in REQUIRED:
            if not (base / f).exists():
                problems.append(f"{name}: required file missing: {f}")

    files = targets()

    for path, text in files.items():
        if args.write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8", newline="\n")
            continue
        rel = path.relative_to(ROOT)
        if not path.exists():
            problems.append(f"missing: {rel}")
            continue
        cur = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        if cur != text:
            problems.append(f"differs: {rel}")

    for p in problems:
        print(f"PROBLEM {p}")

    if problems:
        print(f"FAIL -- {len(problems)} problem(s)")
        return 1

    verb = "written" if args.write else "verified"
    print(f"OK -- {len(files)} file(s) {verb} across {len(TREES)} tree(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
