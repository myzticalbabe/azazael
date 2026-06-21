# coding: utf-8
"""
PYTHON MANAGER - Multi-Installation Handler for Azazael
Manages all 18 Python installations on the system
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class PythonInstallation:
    path: str
    version: str
    version_tuple: tuple
    category: str
    is_default: bool = False
    is_azazael_venv: bool = False


class PythonManager:
    VERSION = "1.0.0"

    # All known Python installations
    INSTALLATIONS = {
        "C:/Python314/python.exe": {"ver": "3.14.3", "cat": "SYSTEM"},
        "C:/Program Files/Python311/python.exe": {"ver": "3.11.9", "cat": "SYSTEM"},
        "C:/ProgramData/chocolatey/bin/python3.14.exe": {
            "ver": "3.14.3",
            "cat": "SYSTEM",
        },
        "C:/Program Files/DeepFaceLab/_internal/python-3.6.8/python.exe": {
            "ver": "3.6.8",
            "cat": "SYSTEM",
        },
        "C:/Users/clint/anaconda3/python.exe": {"ver": "3.13.9", "cat": "ANACONDA"},
        "C:/Users/clint/anaconda3/envs/df-env/python.exe": {
            "ver": "3.10.19",
            "cat": "ANACONDA",
        },
        "C:/Users/clint/.venv/Scripts/python.exe": {
            "ver": "3.11.14",
            "cat": "AZAEAZEL",
        },
        "C:/Users/clint/Desktop/Azazael_UNIFIED/.venv/Scripts/python.exe": {
            "ver": "3.11.14",
            "cat": "AZAEAZEL",
            "azazael": True,
        },
        "C:/Users/clint/Desktop/Azazael_UNIFIED/CODEX/.venv/Scripts/python.exe": {
            "ver": "3.11.14",
            "cat": "AZAEAZEL",
            "azazael": True,
        },
        "C:/Users/clint/Desktop/Azazael_BACKUP_20260212_060745/CODEX/.venv/Scripts/python.exe": {
            "ver": "3.11.14",
            "cat": "AZAEAZEL",
        },
        "C:/Users/clint/.local/bin/python3.11.exe": {"ver": "3.11.14", "cat": "UV"},
        "C:/Users/clint/AppData/Roaming/uv/python/cpython-3.11.14-windows-x86_64-none/python.exe": {
            "ver": "3.11.14",
            "cat": "UV",
        },
        "C:/Users/clint/AppData/Roaming/uv/python/cpython-3.11-windows-x86_64-none/python.exe": {
            "ver": "3.11.8",
            "cat": "UV",
        },
        "C:/Users/clint/AppData/Roaming/uv/python/.temp/.tmpraG7Kw/python/python.exe": {
            "ver": "3.11.8",
            "cat": "UV",
        },
        "C:/Users/clint/restored_venv/Scripts/python.exe": {
            "ver": "3.13.9",
            "cat": "UV",
        },
        "C:/Users/clint/AppData/Local/Programs/AI Playground/resources/OpenVINO/ovms/python/python.exe": {
            "ver": "3.12.10",
            "cat": "AI_PLAYGROUND",
        },
        "C:/Users/clint/.lmstudio/extensions/backends/vendor/_amphibian/app-harmony-win-x86@7/Scripts/python.exe": {
            "ver": "3.11.9",
            "cat": "LM_STUDIO",
        },
        "C:/Users/clint/.lmstudio/extensions/backends/vendor/_amphibian/cpython3.11-win-x86@6/python.exe": {
            "ver": "3.11.9",
            "cat": "LM_STUDIO",
        },
        "C:/Users/clint/Downloads/DeepFaceLab/DeepFaceLab_DirectX12/_internal/python-3.6.8/python.exe": {
            "ver": "3.6.8",
            "cat": "DEEPFACELAB",
        },
    }

    def __init__(self):
        self.root = Path(__file__).parent.parent.parent
        self.installations: Dict[str, PythonInstallation] = {}
        self._discover_installations()

    def _parse_version(self, ver: str) -> tuple:
        parts = ver.split(".")
        return tuple(int(p) for p in parts[:3])

    def _discover_installations(self):
        """Scan for all Python installations."""
        for path, info in self.INSTALLATIONS.items():
            p = Path(path.replace("/", os.sep))
            if p.exists():
                is_azazael = info.get("azazael", False)
                inst = PythonInstallation(
                    path=path,
                    version=info["ver"],
                    version_tuple=self._parse_version(info["ver"]),
                    category=info["cat"],
                    is_azazael_venv=is_azazael,
                )
                self.installations[path] = inst

    def get_default(self) -> Optional[PythonInstallation]:
        """Get the default Python (current interpreter)."""
        current = sys.executable
        if current in self.installations:
            self.installations[current].is_default = True
            return self.installations[current]
        return None

    def get_azazael_venv(self) -> Optional[PythonInstallation]:
        """Get the primary Azazael venv."""
        azazael_path = "C:/Users/clint/Desktop/Azazael_UNIFIED/.venv/Scripts/python.exe"
        return self.installations.get(azazael_path)

    def get_by_version(self, major: int, minor: int = None) -> List[PythonInstallation]:
        """Get all installations matching version."""
        results = []
        for inst in self.installations.values():
            if inst.version_tuple[0] == major:
                if minor is None or inst.version_tuple[1] == minor:
                    results.append(inst)
        return results

    def get_by_category(self, category: str) -> List[PythonInstallation]:
        """Get all installations in a category."""
        return [i for i in self.installations.values() if i.category == category]

    def get_all_categories(self) -> List[str]:
        """Get all categories."""
        return list(set(i.category for i in self.installations.values()))

    def configure_environment(self):
        """Configure environment for Azazael."""
        azazael_path = self.root

        if str(azazael_path) not in sys.path:
            sys.path.insert(0, str(azazael_path))

        os.environ["AZAEAZEL_ROOT"] = str(azazael_path)
        os.environ["PYTHON_MANAGER_ACTIVE"] = "1"

        print(f"[PythonManager] Configured for {azazael_path}")

    def print_inventory(self):
        """Print all installations."""
        print("=" * 70)
        print(f"PYTHON MANAGER v{self.VERSION}")
        print("=" * 70)
        print()

        default = self.get_default()
        azazael = self.get_azazael_venv()

        if default:
            print(f"Current (default): {default.path}")
            print(f"  Version: {default.version}")
            print()

        if azazael:
            print(f"Azazael venv: {azazael.path}")
            print(f"  Version: {azazael.version}")
            print()

        for cat in sorted(self.get_all_categories()):
            insts = self.get_by_category(cat)
            print(f"{cat} ({len(insts)}):")
            for inst in insts:
                marker = " [DEFAULT]" if inst.is_default else ""
                marker += " [AZAEAZEL]" if inst.is_azazael_venv else ""
                print(f"  {inst.path}{marker}")
                print(f"    Version: {inst.version}")
            print()

        print("=" * 70)
        print(f"Total: {len(self.installations)} installations")
        print("=" * 70)

    def save_inventory(self, filename: str = "PYTHON_INVENTORY.json"):
        """Save inventory to JSON."""
        inventory = {
            "timestamp": "2026-02-13",
            "total": len(self.installations),
            "default": self.get_default().path if self.get_default() else None,
            "azazael_venv": self.get_azazael_venv().path
            if self.get_azazael_venv()
            else None,
            "installations": [
                {
                    "path": inst.path,
                    "version": inst.version,
                    "category": inst.category,
                    "is_default": inst.is_default,
                    "is_azazael_venv": inst.is_azazael_venv,
                }
                for inst in self.installations.values()
            ],
        }

        with open(self.root / filename, "w") as f:
            import json

            json.dump(inventory, f, indent=2)

        print(f"[OK] Inventory saved to {filename}")


def main():
    manager = PythonManager()
    manager.configure_environment()
    manager.print_inventory()
    manager.save_inventory()


if __name__ == "__main__":
    main()
