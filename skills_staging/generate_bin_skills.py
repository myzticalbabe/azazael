#!/usr/bin/env python3
"""Generate formal callable skills for binary/CLI tools.

Reads binary_manifest.py (BIN_TOOLS), probes installed tools for their live
version, and writes one skill per tool to the staging output dir.

Skill prefix: azazael-bin- (avoids collision with azazael-pkg-* / azazael-pkg314t-*).
"""

import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from binary_manifest import BIN_TOOLS  # noqa: E402

OUT_DIR = os.path.join(HERE, "bin_skills")


def _strip_ansi(s: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", s)


VERSION_HINTS = {
    "nuclei": ["-version"],
    "john": [[], "--list=build-info"],
    "trufflehog": ["version"],
    "dnsx": ["-version"],
    "naabu": ["-version"],
    "gitleaks": ["--version"],
    "trufflehog": ["--version"],
}


def detect_version(name: str) -> str:
    """Best-effort version detection for installed tools."""
    if not shutil.which(name):
        return "not installed"
    attempts = VERSION_HINTS.get(name, []) + [
        ["--version"], ["-version"], ["-V"], ["version"], [],
    ]
    for args in attempts:
        try:
            r = subprocess.run([name, *args], capture_output=True,
                               text=True, timeout=15)
            out = _strip_ansi(r.stdout or r.stderr).strip().splitlines()
            # prefer lines that actually mention version
            version_lines = [l for l in out if re.search(r"version|v\d+\.\d+", l, re.I)]
            candidates = version_lines or out
            for line in candidates:
                line = line.strip()
                # strip noise prefixes like [INF]
                line = re.sub(r"^\[[A-Za-z]+\]\s*", "", line)
                if not line or re.match(r"^[A-Za-z ]+:?\s*$", line):
                    continue
                # skip banner art (mostly underscores/slashes), python tracebacks,
                # usage noise, and generic error lines
                if re.match(r"^[_/\\\s]+$", line):
                    continue
                if re.search(r"\bline \d+, in <module>|File \"|from \w+(\.\w+)+ import", line):
                    continue
                if "ModuleNotFoundError" in line or "ImportError" in line:
                    return "installed (CLI broken - missing Python deps)"
                if "could not run" in line or "Traceback" in line \
                        or "command not found" in line or "Usage:" in line \
                        or line.startswith("flag provided") \
                        or "unknown shorthand flag" in line \
                        or "expected command" in line or "unknown short flag" in line \
                        or "unknown command" in line:
                    continue
                return line[:90]
            # all lines were noise (banner-only tools like dnsx/naabu/nuclei)
            if out and version_lines:
                return version_lines[0].strip()[:90]
        except Exception:
            continue
    return "installed (version unknown)"


# Tools whose names collide with an unrelated binary on PATH; always mark NOT INSTALLED.
NOT_INSTALLED_OVERRIDE = {"httpx"}  # /usr/bin/httpx is the Python CLI, not ProjectDiscovery

# Tools where --version detection is noisy (banner art, Windows CLI warnings, unknown flags).
# value is (display_version, installed_bool)
VERSION_OVERRIDE = {
    "theHarvester": ("v0.6.4 (source clone, /root/osint-tools/theHarvester)", True),
    "phoneinfoga": ("2.11.0", True),
    "osintgram": ("master (clone, /root/osint-tools/Osintgram)", True),
    "social-analyzer": ("master (clone, /root/osint-tools/social-analyzer)", True),
    "ghunt": ("v2.15.0 (clone, /root/osint-tools/GHunt)", True),
    "ollama": ("0.32.15 (WSL + Windows, Vulkan/Arc GPU enabled)", True),
    "spiderfoot": ("4.0.0", True),
    "sherlock": ("v0.16.0", True),
    "maigret": ("0.6.4", True),
    "mitmproxy": ("11.x (Kali 3.13 backend)", True),
    "seclists": ("2026.1 (data package at /usr/share/seclists)", True),
}


# Tools available via clones in /root/osint-tools — treat as installed (invoked via python3 main.py)
CLONE_INVOKE = {
    "osintgram": "cd /root/osint-tools/Osintgram && python3 main.py",
    "social-analyzer": "cd /root/osint-tools/social-analyzer && node app.js",
    "ghunt": "cd /root/osint-tools/GHunt && python3 ghunt.py",
}


def render(tool: dict) -> str:
    name = tool["name"]
    summary = tool["summary"]
    install = tool["install"]
    if name in NOT_INSTALLED_OVERRIDE:
        version = "not installed"
        is_installed = False
    elif name in VERSION_OVERRIDE:
        version, is_installed = VERSION_OVERRIDE[name]
    else:
        version = detect_version(name) if name in tool.get("installed_names", [name]) else "not installed"
        is_installed = "not installed" not in version

    lines = []
    lines.append("---")
    lines.append(f"name: azazael-bin-{name}")
    lines.append(f"description: Callable skill for {name} — {summary}")
    lines.append("metadata:")
    lines.append("  category: " + tool["category"])
    lines.append("  project: azazael")
    lines.append("  priority: medium")
    lines.append("---")
    lines.append("")
    lines.append(f"# {name}")
    lines.append("")
    lines.append(f"> {summary}")
    lines.append("")

    lines.append("## Identity")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("|-------|-------|")
    lines.append(f"| Tool | `{name}` |")
    lines.append(f"| Version | `{version}` |")
    lines.append(f"| Status | {'INSTALLED' if is_installed else 'NOT INSTALLED — install first'} |")
    lines.append("")
    lines.append("## Install")
    lines.append("")
    lines.append(f"```bash")
    lines.append(install)
    lines.append("```")
    lines.append("")

    lines.append("## EXECUTE — canonical invocations")
    lines.append("")
    for title, cmd in tool["examples"]:
        lines.append(f"**{title}:**")
        lines.append("")
        lines.append("```bash")
        lines.append(cmd)
        lines.append("```")
        lines.append("")

    lines.append("## Verify")
    lines.append("")
    lines.append("```bash")
    if name in CLONE_INVOKE:
        lines.append(f"{CLONE_INVOKE[name]} --help | head -10")
    elif is_installed:
        lines.append(f"{name} --help | head -20")
    else:
        lines.append(f"command -v {name} && echo '{name} installed OK'")
    lines.append("```")
    lines.append("")
    if name in CLONE_INVOKE:
        lines.append("## Invoke")
        lines.append("")
        lines.append("Not a PATH binary — run via the project clone:")
        lines.append("")
        lines.append("```bash")
        lines.append(CLONE_INVOKE[name])
        lines.append("```")
        lines.append("")
    lines.append("## Related")
    lines.append("")
    lines.append("- Part of the Azazael binary-tool skill set (`azazael-bin-*`)")
    lines.append("- See SKILLS_CATALOG.md for the full skill inventory")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    only = sys.argv[1] if len(sys.argv) > 1 else None
    written = 0
    for tool in BIN_TOOLS:
        if only and tool["name"] != only:
            continue
        path = os.path.join(OUT_DIR, f"azazael-bin-{tool['name']}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(render(tool))
        written += 1
    print(f"Wrote {written} skill(s) to {OUT_DIR}")


if __name__ == "__main__":
    main()
