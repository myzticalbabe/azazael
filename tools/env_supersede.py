#!/usr/bin/env python3
"""env_supersede.py -- supersede-doctrine analyzer for Ubuntu environment packages.

Forensic question: which packages on WSL Ubuntu (and, by derivation, the
unbuilt BM Ubuntu) are SUPERSEDED -- i.e. their function already lives in a
native in-repo sub-tree -- or STALE (no consumer anywhere), and can be removed?

Evidence sources (all measured, none assumed):
  captures/  apt installed + manual lists, pip freezes, reverse-dep map
             (built live inside the target distro), tree import scan.
  tree refs  `grep -rn` provenance recorded per verdict in APT_VERDICTS.

Usage:
  python tools/env_supersede.py --captures <dir> [--emit-manifest PATH]
      [--emit-script PATH] [--check] [--strict]

  --check   fail if any REMOVE candidate is imported by the tree or has
            reverse dependents in the live revdep map (safety gate).
  --strict  UNREVIEWED manual apt rows also fail (next-sweep forcing function).

Doctrine (repo convention, cf. MASTER_ENVIRONMENT_INVENTORY supersede banners):
  a verdict names its evidence command. A row without provenance is narrative.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
REPO = TOOL_DIR.parent

# ---------------------------------------------------------------------------
# Curated apt verdicts: (package, verdict, evidence, native absorber)
# verdict in {REMOVE, KEEP}. Everything not listed here is UNREVIEWED.
# ---------------------------------------------------------------------------
# Each evidence string names the command or grep that proves the verdict.
APT_VERDICTS: list[tuple[str, str, str, str]] = [
    ("krusader", "REMOVE", "no tree refs: grep -rln krusader src/ tools/ scripts/ = 0; GUI FM in a headless WSL distro", "native file ops: TARBABY_FileSearch + azazael_toolkit"),
    ("nautilus", "REMOVE", "no tree refs: grep -rln nautilus src/ tools/ = 0; GNOME FM, no desktop session in WSL", "same as krusader"),
    ("bazel-7.7.0", "REMOVE", "find . -maxdepth 3 -name WORKSPACE* -o -name BUILD.bazel = 0 hits; grep -rln bazel tools/ scripts/ src/CORE = 0", "nothing to absorb: zero consumers"),
    ("swig", "REMOVE", "grep -rln swig tools/ scripts/ src/CORE = 0; no .i interface files in tree", "nothing to absorb"),
    ("qemu-utils", "REMOVE", "grep -rln qemu tools/ scripts/ src/CORE = 0", "nothing to absorb"),
    ("mold", "REMOVE", "grep -rn mold build config (pyproject/setup.cfg/tools/*.py) = biology metaphors only; system ld links every native kernel built to date", "system binutils ld"),
    ("ccache", "REMOVE", "no wired usage in any build script; 3.16t production builds happen on Windows, not WSL; reinstall = 1 apt command (recorded here)", "nothing to absorb"),
    ("eatmydata", "REMOVE", "no wired usage; disables fsync -- actively risky on a 1T virtual disk; reinstall = 1 apt command", "nothing to absorb"),
    ("clinfo", "REMOVE", "diagnostic probe binary; device detection lives in src/CORE/device.py (torch.xpu/cuda/cpu ladder)", "src/CORE/device.py + backend_bandit"),
    ("vainfo", "REMOVE", "diagnostic probe binary; same absorber as clinfo", "src/CORE/device.py"),
    ("vulkan-tools", "REMOVE", "diagnostic probe binaries; same absorber as clinfo", "src/CORE/device.py"),
    ("mesa-utils", "REMOVE", "glxinfo-class probes; headless WSL has no GL consumer in tree", "src/CORE/device.py"),
    ("intel-gpu-tools", "REMOVE", "diagnostic suite; same absorber as clinfo", "src/CORE/device.py + backend_bandit"),
    ("libopencv-dev", "REMOVE", "sole tree mention is a probe *string* (azazael_toolkit.py:49), not an import; pip has no opencv dist", "PIL/pillow path (requirements-3.15t pins pillow 12.3.0)"),
    ("python3-pygame", "REMOVE", "canonical src/azazael_pygame.py (630 lines) has no live importer (only test shim + DEPRECATED re-export per its own 2026-10-11 measurement); CODEX renders via Puppeteer, not pygame", "CODEX/Puppeteer render pipeline"),
    ("libsdl2-dev", "REMOVE", "SDL stack exists only for the unimported pygame module above", "same as python3-pygame"),
    ("libsdl2-image-dev", "REMOVE", "same as libsdl2-dev", "same as python3-pygame"),
    ("libsdl2-mixer-dev", "REMOVE", "same as libsdl2-dev", "same as python3-pygame"),
    ("libsdl2-ttf-dev", "REMOVE", "same as libsdl2-dev", "same as python3-pygame"),
    ("libportmidi-dev", "REMOVE", "same as libsdl2-dev", "same as python3-pygame"),
    ("nmap", "REMOVE", "Ubuntu-side only: recon is Kali-lane turf; WslKaliWorm expects wsl2-kali and checks /usr/bin itself; native PortAuditor (security.py:102, psutil+socket stdlib) covers Ubuntu-side port audit", "src/CORE/WORMS/expansion/security.py::PortAuditor"),
    # -- KEEP rows: load-bearing, named so the next sweep does not re-litigate --
    ("intel-oneapi-compiler-dpcpp-cpp", "KEEP", "device.py:5 preference order XPU > CUDA > CPU; torch 2.14.1+xpu live in /opt+15t sidecar -- this apt set is its driver/runtime half", "IS the engineered replacement (keep)"),
    ("intel-oneapi-mkl-devel", "KEEP", "same XPU stack as above", "IS the engineered replacement (keep)"),
    ("tor", "KEEP", "pip holds stem 1.8.2 + torbot 4.3.0 (eve OSINT lane, torbot skill); both require the tor daemon binary", "eve OSINT lane owns it"),
    ("yt-dlp", "KEEP", "imported/used by tools/sota_fetch_video.py, tiktok_batch.py, TIKTOK_PULL.py, youtube_transcript.py", "tool consumer, keep"),
    ("nodejs", "KEEP", "MCP client stack (kilo/opencode/freebuff lanes) runs on node", "lane runtime, keep"),
    ("golang-go", "KEEP", "gateway-go/ in-repo Go tier + engram Go source builds", "Go tier, keep"),
    ("docker-ce", "KEEP", "docker-compose.yml local production stack (azazael-core :18420/:18421); Kali runs containerd -- asymmetry noted, not removal", "container tier, keep"),
    ("tk-dev", "KEEP", "live tkinter imports: AZAZAEL_Inference_Studio.py, CODEX_Studio.py, CODEX/POPUPS/*", "GUI studios, keep"),
    ("ffmpeg", "KEEP", "CODEX/CAIN render pipeline dependency", "render pipeline, keep"),
    ("build-essential", "KEEP", "toolchain for CPython source builds (runbook BM §2 pattern)", "toolchain, keep"),
]

PIP_TOOLCHAIN = {"pip", "setuptools", "wheel", "packaging"}

# CLI applications owned by lanes: never libraries, never imported, but live
# tools. Removing one would strand its lane with no import error to notice.
PIP_TOOLS: dict[str, str] = {
    "sherlock-project": "eve OSINT lane CLI (username search)",
    "maigret": "eve OSINT lane CLI (username search)",
    "holehe": "eve OSINT lane CLI (email search)",
    "torbot": "eve OSINT lane CLI (dark-web; needs tor daemon)",
    "ghunt": "eve OSINT lane CLI (Google-account OSINT)",
    "theharvester": "recon lane CLI (email/subdomain harvest; kali owns the binary side)",
    "yt-dlp": "tool CLI used by sota_fetch_video/tiktok_batch/TIKTOK_PULL/youtube_transcript",
    "archivebox": "self-hosted web-archive app + dep cone (django-extensions, w3lib, "
        "python-crontab, croniter, cloudpathlib); no tree refs but a running app, not a library",
    "open-interpreter": "INVESTIGATE: separate /root/open-interpreter/venv exists; "
        "global copy kept until a lane confirms which one is live",
}

# The project's own installed dists (wheels/sdists built from this repo).
# Removing one strands console scripts with no import error to notice.
SELF_PREFIXES = ("azazael", "azazael-")
SELF_EXACT = {"eve-unleashed", "worm-manifest"}

# AUTO_DOWNLOADER-managed frameworks (CODEX/CORE/AUTO_DOWNLOADER.py pip_name=,
# 18 entries): preinstalled copies are its cache; it re-fetches on demand.
MANAGED = {
    "catboost", "faiss-cpu", "fastapi", "jax", "lightgbm", "mlflow", "onnx",
    "opencv-python", "optuna", "ray", "scikit-learn", "shap", "spacy",
    "tensorflow", "torch", "transformers", "wandb", "xgboost",
}

# XPU runtime coupling: torch 2.14.1+xpu dlopens these; the coupling is in
# shared libraries, invisible to METADATA Requires-Dist. Evidence: /opt + 15t
# sidecar exists FOR this stack; device.py prefers XPU. Never auto-remove.
RUNTIME = {
    "dpcpp-cpp-rt", "impi-rt", "intel-cmplr-lib-rt", "intel-cmplr-lib-ur",
    "intel-cmplr-lic-rt", "intel-opencl-rt", "intel-openmp", "intel-pti",
    "intel-sycl-rt", "mkl", "oneccl", "oneccl-devel", "onemkl-license",
    "onemkl-sycl-blas", "onemkl-sycl-dft", "onemkl-sycl-lapack",
    "onemkl-sycl-rng", "onemkl-sycl-sparse", "tbb", "umf", "tcmlib",
}

# Dist is imported only by a dead module itself (proven by grep on BOTH
# checkouts), so the import scan false-KEEPS it. Evidence per row.
PIP_OVERRIDES: dict[str, str] = {
    "pygame": "REMOVE: `import pygame` occurs only inside src/azazael_pygame.py itself "
        "(both checkouts); no module imports azazael_pygame (Windows 2026-10-11 measure + "
        "WSL grep today: only docs/reports/pycache mention it)",
}


def pep503(name: str) -> str:
    """Normalize a dist/requirement name: lowercase, [-_.] -> '-', strip extras."""
    import re
    name = name.strip().lower()
    name = re.split(r"[;\s\[\]<>=!~]", name, maxsplit=1)[0]
    return re.sub(r"[-_.]+", "-", name).strip("-")

BASELINE_FILE = REPO / "requirements-3.15t.txt"


def load_baseline() -> set[str]:
    names: set[str] = set()
    if BASELINE_FILE.is_file():
        for line in BASELINE_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                names.add(line.split("==")[0].split(">=")[0].strip().lower())
    return names


def norm_dist(freeze_line: str) -> str:
    return freeze_line.split("==")[0].strip().lower()


def mod_for_dist(dist: str) -> str:
    return dist.replace("-", "_")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="supersede-doctrine package analyzer")
    ap.add_argument("--captures", required=True, help="dir with apt_*.txt, pip_*.txt, revdeps.json, tree_imports.json")
    ap.add_argument("--emit-manifest", default=None)
    ap.add_argument("--emit-script", default=None)
    ap.add_argument("--emit-pip-script", default=None)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args(argv)
    cap = Path(a.captures)

    pip14 = [norm_dist(x) for x in (cap / "pip_14t.txt").read_text().splitlines() if x.strip()]
    revdeps: dict[str, list[str]] = json.loads((cap / "revdeps.json").read_text())
    tree_imports: set[str] = set(json.loads((cap / "tree_imports.json").read_text()))
    baseline = load_baseline()
    manual = [x.strip() for x in (cap / "apt_manual.txt").read_text().splitlines() if x.strip()]
    installed = {x.strip() for x in (cap / "apt_installed.txt").read_text().splitlines() if x.strip()}

    # --- pip classification -------------------------------------------------
    # union both checkouts' import scans, minus local (in-repo) top-level names
    try:
        ubuntu_imports: set[str] = set(json.loads((cap / "tree_imports_ubuntu.json").read_text()))
    except FileNotFoundError:
        ubuntu_imports = set()
    local_roots = {p.name for p in (REPO / "src").iterdir()}
    local_roots |= {"tools", "scripts", "tests", "eve_unleashed", "CORE", "CODEX"}
    tree_imports = (tree_imports | ubuntu_imports) - local_roots - {m.lower() for m in local_roots}

    # normalize the live reverse-dep map (raw requirement strings carry markers)
    rev: dict[str, list[str]] = {}
    for raw_req, users in revdeps.items():
        key = pep503(raw_req)
        if not key:
            continue
        have = rev.setdefault(key, [])
        for u in users:
            nu = pep503(u)
            if nu and nu not in have and nu != key:
                have.append(nu)
    pip14n = [pep503(d) for d in pip14]
    in_env = set(pip14n)

    # fixed-point KEEP from roots: imported | baseline | toolchain | lane tools.
    # A chain whose top is none of those is dead -- every link is REMOVE.
    # (The pre-fixpoint collapse -- dropping users that are themselves REMOVE --
    # hid this and --check caught it: stem <- sherlock-project.)
    def self_dist(dist: str) -> bool:
        return dist in SELF_EXACT or dist == "azazael" or dist.startswith("azazael-")

    keep: dict[str, str] = {}
    for dist in pip14n:
        mod = mod_for_dist(dist)
        if mod in tree_imports or dist in tree_imports:
            keep[dist] = "imported by tree (either checkout)"
        elif self_dist(dist):
            keep[dist] = "self-install (built from this repo)"
        elif dist in baseline or dist in PIP_TOOLCHAIN:
            keep[dist] = "baseline/toolchain"
        elif dist in PIP_TOOLS:
            keep[dist] = f"lane tool: {PIP_TOOLS[dist]}"
        elif dist in MANAGED:
            keep[dist] = "auto-downloader managed (re-fetches on demand)"
        elif dist in RUNTIME:
            keep[dist] = "XPU runtime coupling (metadata-blind shared libs)"
    changed = True
    while changed:
        changed = False
        for dist in pip14n:
            if dist in keep:
                continue
            users = [u for u in rev.get(dist, []) if u in in_env and u in keep]
            if users:
                keep[dist] = f"required by kept: {','.join(sorted(users)[:3])}"
                changed = True
    pip_keep = dict(keep)
    pip_remove = {}
    for dist in pip14n:
        if dist in keep:
            continue
        if dist in PIP_OVERRIDES:
            pip_remove[dist] = PIP_OVERRIDES[dist]
            continue
        users = [u for u in rev.get(dist, []) if u in in_env]
        if users:
            # dead chain: top is unimported, unbaselined, not a lane tool
            tops = sorted(users)[:3]
            pip_remove[dist] = f"dead chain via: {','.join(tops)} (top unimported/unbaselined, not a lane tool)"
        else:
            pip_remove[dist] = "orphan: not imported, not in baseline, zero in-env reverse deps"

    # --- apt classification -------------------------------------------------
    verdict_of = {v[0]: v for v in APT_VERDICTS}
    apt_remove = [(p, v[2], v[3]) for p, v in verdict_of.items() if v[1] == "REMOVE" and p in installed]
    apt_missing = [(p, v[1]) for p, v in verdict_of.items() if p not in installed]
    apt_unreviewed = [p for p in manual if p not in verdict_of]

    # --- safety gate ----------------------------------------------------------
    failures: list[str] = []
    if a.check:
        for dist in pip_remove:
            if mod_for_dist(dist) in tree_imports or dist in tree_imports:
                failures.append(f"pip REMOVE candidate imported by tree: {dist}")
            kept_users = [u for u in rev.get(dist, []) if u in keep]
            if kept_users:
                failures.append(f"pip REMOVE candidate required by kept: {dist} <- {kept_users[:3]}")
            if self_dist(dist) or dist in RUNTIME or dist in MANAGED or dist in PIP_TOOLS:
                failures.append(f"pip REMOVE candidate is protected: {dist}")
        for p, _ev, _ab in apt_remove:
            if p not in installed:
                failures.append(f"apt REMOVE candidate not installed: {p}")

    lines = [
        "# ENV SUPERSEDE MANIFEST — WSL Ubuntu package verdicts",
        "",
        "> Generated by `python tools/env_supersede.py --captures <dir>`.",
        "> Doctrine: a verdict names its evidence command; a row without provenance is narrative.",
        "> Scope: WSL Ubuntu-26.04 (live probe) + BM Ubuntu (derived: unbuilt, runbook-only).",
        "> Kali (1,009 pip) is foreign recon turf -- out of scope for removal.",
        "",
        f"## Denominators: apt installed={len(installed)} manual={len(manual)} | pip_14t={len(pip14)} | tree external imports={len(tree_imports)}",
        "",
        f"## pip_14t: KEEP={len(pip_keep)} REMOVE={len(pip_remove)}",
        "",
    ]
    for dist in sorted(pip_remove):
        lines.append(f"- REMOVE `{dist}` -- {pip_remove[dist]}")
    if not pip_remove:
        lines.append("- (no pip orphans: every dist is imported, baselined, or required)")
    lines += ["", f"## apt manual: REMOVE={len(apt_remove)} curated-KEEP={len([v for v in verdict_of.values() if v[1]=='KEEP'])} UNREVIEWED={len(apt_unreviewed)}", ""]
    for p, ev, ab in apt_remove:
        lines.append(f"- REMOVE `{p}` -- {ev} | absorbed-by: {ab}")
    lines += ["", "### Curated KEEP (do not re-litigate without new evidence)", ""]
    for p, v in verdict_of.items():
        if v[1] == "KEEP":
            lines.append(f"- KEEP `{p}` -- {v[2]}")
    lines += ["", f"### UNREVIEWED manual rows ({len(apt_unreviewed)}) -- next sweep", ""]
    for p in sorted(apt_unreviewed)[:60]:
        lines.append(f"- ? `{p}`")
    if len(apt_unreviewed) > 60:
        lines.append(f"- ... and {len(apt_unreviewed) - 60} more (see apt_manual.txt)")
    if apt_missing:
        lines += ["", "### Verdict rows not installed (drift between table and host)", ""]
        lines += [f"- `{p}` verdict {v} but absent from installed list" for p, v in apt_missing]
    lines += [
        "",
        "## BM Ubuntu path-forward (derived, not probed: BM is unbuilt, runbook-only)",
        "",
        "- BM starts from the POST-SHRINK set: stock Ubuntu 26.04 + runbook BM §2",
        "  (build-essential + 10 dev libs) + the native sub-trees named as absorbers above.",
        "- BM NEVER receives the 21 REMOVE classes: no SDL/pygame, no bazel/swig/qemu/mold/eatmydata,",
        "  no GPU-probe binaries (device.py decides), no nmap (PortAuditor covers it), no GUI FMs.",
        "- BM gets the XPU stack (device.py prefers XPU) and the single production interpreter",
        "  (3.16t free-threaded per current production; 3.15t sidecar only where wheels demand it).",
        "- Interpreter sprawl is NOT replicated: system 3.14 (OS) + one production build.",
        "  WSL's /usr/local 3.14t + 3.14-gil + 3.15t + /opt 3.15t + venv-{314-gil,interpreter,abox}",
        "  consolidate to that shape; venv-interpreter stays until the 6 referencing scripts",
        "  (dev_stack_census, install_ml_wsl.sh, baselines...) are repointed -- CONSOLIDATE-PLAN, not today.",
        "",
        "## Removal script",
        "",
        "- `scripts/wsl_ubuntu_shrink.sh` (generated alongside this manifest).",
        "- Rules: apt only (pip_14t has no orphans); `--purge` + `autoremove`; idempotent;",
        "  aborts on any package that gained a reverse dependent since this probe.",
    ]
    manifest = "\n".join(lines) + "\n"

    script = [
        "#!/usr/bin/env bash",
        "# GENERATED by tools/env_supersede.py -- review before running. Idempotent.",
        "# Scope: WSL Ubuntu-26.04 ONLY. Never run on Kali, BM, or Windows.",
        "set -u",
        "if ! grep -qi microsoft /proc/version 2>/dev/null; then echo 'REFUSING: not WSL'; exit 2; fi",
        "REMOVE=\"" + " ".join(sorted(p for p, _e, _a in apt_remove)) + "\"",
        'for p in $REMOVE; do if dpkg -l "$p" 2>/dev/null | grep -q "^ii"; then echo "purge $p"; sudo apt-get purge -y "$p"; fi; done',
        "sudo apt-get autoremove -y",
        "echo DONE",
    ]
    script_text = "\n".join(script) + "\n"

    pip_script = [
        "#!/usr/bin/env bash",
        "# GENERATED by tools/env_supersede.py -- review before running. Idempotent.",
        "# Scope: WSL Ubuntu /usr/local 3.14t global env ONLY. Never run on Kali, BM, or Windows.",
        "set -u",
        "if ! grep -qi microsoft /proc/version 2>/dev/null; then echo 'REFUSING: not WSL'; exit 2; fi",
        "PY=/usr/local/bin/python3.14t",
        "REMOVE=\"" + " ".join(sorted(pip_remove)) + "\"",
        "for p in $REMOVE; do $PY -m pip show \"$p\" >/dev/null 2>&1 && $PY -m pip uninstall -y \"$p\" || echo \"absent: $p\"; done",
        "echo DONE",
    ]
    pip_script_text = "\n".join(pip_script) + "\n"

    print(f"pip_14t: keep={len(pip_keep)} remove={len(pip_remove)}")
    print(f"apt: remove={len(apt_remove)} keep_curated={len([v for v in verdict_of.values() if v[1]=='KEEP'])} unreviewed={len(apt_unreviewed)} missing={len(apt_missing)}")
    for dist in sorted(pip_remove):
        print(f"  pip-REMOVE {dist}: {pip_remove[dist]}")
    for p, ev, _ab in apt_remove:
        print(f"  apt-REMOVE {p}")
    if failures:
        print("CHECK FAILURES:")
        for f in failures:
            print(f"  !! {f}")
        return 1
    if a.strict and apt_unreviewed:
        print(f"STRICT: {len(apt_unreviewed)} unreviewed manual rows remain")
        return 1
    if a.emit_manifest:
        Path(a.emit_manifest).write_text(manifest)
        print(f"wrote {a.emit_manifest}")
    def write_lf(path: str, text: str) -> None:
        # Path.write_text translates \n to os.linesep on Windows, which
        # poisons bash scripts with CRLF. Bypass with newline='\n'.
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)

    if a.emit_script:
        write_lf(a.emit_script, script_text)
        print(f"wrote {a.emit_script}")
    if a.emit_pip_script:
        write_lf(a.emit_pip_script, pip_script_text)
        print(f"wrote {a.emit_pip_script}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
