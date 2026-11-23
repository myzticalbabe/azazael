"""Scaffold output must be checker-clean and bytecode-proof by construction."""
import subprocess
import sys
from pathlib import Path

import tools.soul_repo_scaffold as scaffold

MASTER = (
    Path(__file__).resolve().parents[1] / "tools" / "soul_licence_check.py"
)


def _run_checker(repo_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(repo_dir / "tools" / "soul_licence_check.py")],
        cwd=repo_dir,
        capture_output=True,
        text=True,
        timeout=180,
    )


def test_scaffold_shape(tmp_path):
    target = tmp_path / "demo-repo"
    written = scaffold.scaffold(target, "demo-repo")
    assert "LICENSE" in written
    assert (target / ".github" / "workflows" / "soul-forge-gate.yml").exists()
    gi = (target / ".gitignore").read_text(encoding="utf-8")
    assert "__pycache__/" in gi and "*.pyc" in gi
    assert "myzticalbabe/demo-repo" in (
        target / "LICENSE"
    ).read_text(encoding="utf-8")
    assert "azazael" not in (target / "LICENSE").read_text(encoding="utf-8")


def test_scaffolded_repo_is_checker_clean(tmp_path):
    target = tmp_path / "demo-repo"
    scaffold.scaffold(target, "demo-repo")
    # The checker scans a repository: scaffold then init, as real use does.
    subprocess.run(
        ["git", "init", "-b", "main"],
        cwd=target,
        capture_output=True,
        check=True,
        timeout=120,
    )
    proc = _run_checker(target)
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_scaffold_copies_match_canonicals(tmp_path):
    target = tmp_path / "demo-repo"
    scaffold.scaffold(target, "demo-repo")
    for rel in scaffold.COPY_FILES:
        assert (target / rel).read_bytes() == (
            scaffold.MONOREPO / rel
        ).read_bytes(), rel
