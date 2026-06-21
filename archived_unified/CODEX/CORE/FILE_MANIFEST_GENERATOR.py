#!/usr/bin/env python3
"""
File Manifest Generator

Creates JSON manifest of all ecosystem files.
"""

import json
import hashlib
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List


def generate_manifest(base_path: str, output_path: str) -> Dict:
    """Generate file manifest."""
    base = Path(base_path)
    manifest = {
        "manifest_version": "1.0.0",
        "generated": datetime.now().isoformat(),
        "ecosystem": {"name": "Azazael", "version": "2.0.0"},
        "files": [],
    }

    component_map = {
        "Azazael": "Integration",
        "HYDRA": "ML Cluster",
        "WORMZ": "Execution",
        "METAWORMS": "Orchestration",
        "HORUS": "Presentation",
        "TERENCE": "Error Resolution",
        "KLINK": "Command Launcher",
        "SHORTY": "Shortcuts",
        "TARBABY": "Processing",
        "POINDEXTER": "Analysis",
        "PERSEPHONE": "Utilities",
        "TWITLER": "Monitoring",
        "BIBL": "Data",
        "CODEX": "Documentation",
    }

    ecosystem_dirs = [
        "Azazael",
        "HYDRA.py",
        "WORMZ",
        "METAWORMS",
        "HORUS",
        "TERENCE",
        "KLINK",
        "SHORTY",
        "TARBABY",
        "POINDEXTER",
        "PERSEPHONE",
        "TWITLER",
        "BIBL",
        "CODEX",
    ]

    for comp_dir in ecosystem_dirs:
        comp_path = base / comp_dir
        if comp_path.exists():
            for filepath in sorted(comp_path.rglob("*")):
                if filepath.is_file():
                    try:
                        stat = filepath.stat()
                        rel_path = str(filepath.relative_to(base))

                        file_info = {
                            "path": rel_path,
                            "size_bytes": stat.st_size,
                            "modified": datetime.fromtimestamp(
                                stat.st_mtime
                            ).isoformat(),
                            "type": "unknown",
                        }

                        suffix = filepath.suffix.lower()
                        if suffix == ".py":
                            file_info["type"] = "python"
                        elif suffix == ".md":
                            file_info["type"] = "documentation"
                        elif suffix == ".bat":
                            file_info["type"] = "batch"
                        elif suffix == ".ps1":
                            file_info["type"] = "powershell"
                        elif suffix == ".json":
                            file_info["type"] = "json"
                        elif suffix == ".html":
                            file_info["type"] = "html"
                        elif suffix == ".lnk":
                            file_info["type"] = "shortcut"

                        for comp in component_map.keys():
                            if (
                                f"/{comp}/" in rel_path
                                or rel_path.startswith(f"{comp}/")
                                or rel_path == comp
                            ):
                                file_info["component"] = comp
                                break
                        else:
                            file_info["component"] = "Other"

                        if filepath.suffix == ".py":
                            with open(filepath, "rb") as f:
                                file_info["md5"] = hashlib.md5(f.read()).hexdigest()
                            with open(
                                filepath, "r", encoding="utf-8", errors="ignore"
                            ) as f:
                                file_info["lines"] = sum(1 for _ in f)

                        manifest["files"].append(file_info)
                    except Exception as e:
                        print(f"Error processing {filepath}: {e}")

    manifest["statistics"] = {
        "total_files": len(manifest["files"]),
        "total_size_bytes": sum(f["size_bytes"] for f in manifest["files"]),
        "by_type": {},
        "by_component": {},
    }

    for f in manifest["files"]:
        t = f["type"]
        c = f["component"]
        manifest["statistics"]["by_type"][t] = (
            manifest["statistics"]["by_type"].get(t, 0) + 1
        )
        manifest["statistics"]["by_component"][c] = (
            manifest["statistics"]["by_component"].get(c, 0) + 1
        )

    with open(output_path, "w") as f:
        json.dump(manifest, f, indent=2)

    return manifest


if __name__ == "__main__":
    manifest = generate_manifest(
        "C:/Users/clint/Desktop", "C:/Users/clint/Desktop/CODEX/manifest.json"
    )
    print(f"Manifest generated: {manifest['statistics']['total_files']} files")
    print(f"Total size: {manifest['statistics']['total_size_bytes']:,} bytes")
