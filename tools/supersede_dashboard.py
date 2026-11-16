"""Supersede observability dashboard -- static HTML bridging Windows/Linux gaps.

Reads the committed Ubuntu + Kali manifests (numbers carry manifest
provenance; nothing here is hand-typed) and emits one self-contained HTML
file a Windows operator opens in Chrome: estate before/after per distro,
verdict buckets, verify commands, BM checklist.

Usage:
    python tools/supersede_dashboard.py \\
        --ubuntu docs/ENV_SUPERSEDE_MANIFEST.md \\
        --kali docs/KALI_SUPERSEDE_MANIFEST.md \\
        --out docs/supersede_dashboard.html
"""

import argparse
import html
import re
from pathlib import Path


def parse_manifest(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    d: dict = {"file": path.name, "denominators": "", "pip": "",
               "apt": "", "remove_rows": [], "exec_record": ""}
    m = re.search(r"## Denominators: (.+)", text)
    if m:
        d["denominators"] = m.group(1).strip()
    m = re.search(r"## pip_14t: (.+)", text)
    if m:
        d["pip"] = m.group(1).strip()
    m = re.search(r"## apt manual: (.+)", text)
    if m:
        d["apt"] = m.group(1).strip()
    d["remove_rows"] = re.findall(r"^- REMOVE `([^`]+)` -- (.+)$", text, re.M)
    d["keep_rows"] = re.findall(r"^- KEEP `([^`]+)` -- (.+)$", text, re.M)
    m = re.search(r"## Execution record.*?(?=\n## |\Z)", text, re.S)
    if m:
        d["exec_record"] = m.group(0).strip()
    return d


def main() -> None:
    a = argparse.ArgumentParser()
    a.add_argument("--ubuntu", required=True)
    a.add_argument("--kali", required=True)
    a.add_argument("--out", required=True)
    args = a.parse_args()

    ubuntu = parse_manifest(Path(args.ubuntu))
    kali = parse_manifest(Path(args.kali))

    def section(title: str, d: dict) -> str:
        rows = "".join(
            f"<li><code>{html.escape(n)}</code> -- {html.escape(w)}</li>\n"
            for n, w in d["remove_rows"]
        )
        exec_html = html.escape(d["exec_record"]).replace("\n", "<br>\n")
        keeps = "".join(
            f"<li><code>{html.escape(n)}</code> -- {html.escape(w)}</li>\n"
            for n, w in d["keep_rows"]
        )
        keep_section = (
            f"<h3>Curated KEEP -- do not re-litigate ({len(d['keep_rows'])})</h3>"
            f"\n<ul>\n{keeps}</ul>\n" if d["keep_rows"] else ""
        )
        return (
            f"<h2>{title}</h2>\n"
            f"<p><b>Denominators:</b> {html.escape(d['denominators'])}</p>\n"
            f"<p><b>pip_14t:</b> {html.escape(d['pip'])}</p>\n"
            f"<p><b>apt:</b> {html.escape(d['apt'])}</p>\n"
            f"<h3>REMOVE verdicts ({len(d['remove_rows'])})</h3>\n<ul>\n{rows}</ul>\n"
            f"{keep_section}"
            f"<h3>Execution record</h3>\n<p>{exec_html or 'not yet executed'}</p>\n"
        )

    page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Supersede observability dashboard</title>
<style>body{{font-family:sans-serif;max-width:70em;margin:2em auto;padding:0 1em}}
code{{background:#f0f0f0;padding:0 .3em}}li{{margin:.2em 0}}
.warn{{background:#fff3cd;border:1px solid #e0c36a;padding:.8em}}</style>
</head><body>
<h1>Package supersede dashboard (Ubuntu + Kali)</h1>
<p>Source: committed manifests. A verdict names its evidence command;
a row without provenance is narrative.</p>
<div class="warn"><b>Windows operator note:</b> this file is generated on
Windows from WSL-captured manifests. To refresh: re-run the capture probes
in each distro, re-run <code>tools/env_supersede.py --check</code>, re-emit
manifests, then re-run this script. No server needed.</div>
{section("WSL Ubuntu-26.04", ubuntu)}
{section("WSL kali-linux (recon turf)", kali)}
<h2>BM Ubuntu runbook</h2>
<p>See <code>docs/BM_SUPERSEDE_RUNBOOK.md</code> for the bare-metal replay
steps (same tool, same doctrine, BM-owned captures).</p>
<h2>Verify commands (paste into each distro)</h2>
<ul>
<li><code>apt-get check &amp;&amp; dpkg --audit</code> (clean = no output)</li>
<li><code>dpkg -V $(dpkg -l "python3*" | awk '/^ii/{{print $2}}')</code>
(no <code>missing</code> lines = apt files intact)</li>
<li><code>python tools/env_supersede.py --captures &lt;dir&gt; [--scope kali] --check</code>
(<code>remove=0</code> = steady state)</li>
</ul>
</body></html>
"""
    Path(args.out).write_text(page, encoding="utf-8")
    print(f"wrote {args.out} ({len(page)} bytes)")


if __name__ == "__main__":
    main()
