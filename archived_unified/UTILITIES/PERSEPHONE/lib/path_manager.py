# coding: utf-8
"""
Path Manager for PERSEPHONE.

Advanced path handling for cross-platform development.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass


@dataclass
class PathInfo:
    """Path information container."""

    name: str
    windows: str
    wsl: str
    exists: bool = False


class PathManager:
    """Manage cross-platform paths for Azazael and PERSEPHONE."""

    def __init__(self):
        self.paths: Dict[str, PathInfo] = {}
        self._register_default_paths()

    def _register_default_paths(self):
        """Register default paths."""
        self.register(
            "azazael",
            "C:\\Users\\clint\\Desktop\\Azazael",
            "/mnt/c/Users/clint/Desktop/Azazael",
        )
        self.register(
            "persephone",
            "C:\\Users\\clint\\Desktop\\PERSEPHONE",
            "/mnt/c/Users/clint/Desktop/PERSEPHONE",
        )
        self.register("wsa", "\\\\wsl$Ubuntu\\home\\", "/home/")
        self.register(
            "desktop", "C:\\Users\\clint\\Desktop", "/mnt/c/Users/clint/Desktop"
        )
        self.register(
            "documents", "C:\\Users\\clint\\Documents", "/mnt/c/Users/clint/Documents"
        )

    def register(self, name: str, windows: str, wsl: str):
        """Register a path for cross-platform access."""
        exists = Path(windows).exists() or Path(wsl).exists()
        self.paths[name] = PathInfo(name, windows, wsl, exists)

    def get(self, name: str, platform: str = None) -> Optional[PathInfo]:
        """Get path information by name."""
        return self.paths.get(name)

    def to_wsl(self, windows_path: str) -> str:
        """Convert Windows path to WSL path."""
        if len(windows_path) >= 2 and windows_path[1] == ":":
            drive = windows_path[0].lower()
            return f"/mnt/{drive}{windows_path[2:]}".replace("\\", "/")
        return windows_path

    def to_windows(self, wsl_path: str) -> str:
        """Convert WSL path to Windows path."""
        if wsl_path.startswith("/mnt/"):
            drive = wsl_path[5].upper()
            return f"{drive}:{wsl_path[6:]}".replace("/", "\\")
        return wsl_path

    def detect(self, name: str) -> Optional[PathInfo]:
        """Detect if a path exists and update status."""
        if name in self.paths:
            info = self.paths[name]
            info.exists = Path(info.windows).exists() or Path(info.wsl).exists()
        return self.get(name)

    def list_all(self) -> List[PathInfo]:
        """List all registered paths."""
        return list(self.paths.values())

    def sync_paths(self) -> Dict[str, bool]:
        """Sync all paths and return existence status."""
        results = {}
        for name, info in self.paths.items():
            info.exists = Path(info.windows).exists() or Path(info.wsl).exists()
            results[name] = info.exists
        return results


if __name__ == "__main__":
    pm = PathManager()
    for info in pm.list_all():
        print(f"{info.name}: {'[OK]' if info.exists else '[MISSING]'} {info.windows}")
