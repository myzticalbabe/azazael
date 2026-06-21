#!/usr/bin/env python3
"""
Documentation Updater - Updates all paths for C:\\Azazael migration
"""

from pathlib import Path

root = Path.home() / "Desktop" / "Azazael_UNIFIED"

patterns = [
    (Path.home() / "Desktop" / "Azazael_UNIFIED", "C:/Azazael"),
    ("/c/Users/clint/Desktop/Azazael_UNIFIED", "/c/Azazael"),
    ("~/Desktop/Azazael_UNIFIED", "~/Azazael"),
]

updated = []
errors = []

for md in list(root.rglob("*.md")) + list(root.rglob("*.txt")):
    if ".venv" in str(md) or "site-packages" in str(md):
        continue
    try:
        content = md.read_text(encoding="utf-8", errors="ignore")
        original = content
        for old, new in patterns:
            content = content.replace(old, new)
        if content != original:
            md.write_text(content, encoding="utf-8")
            updated.append(str(md.relative_to(root)))
    except Exception as e:
        errors.append((md.name, str(e)[:50]))

print(f"Updated {len(updated)} files:")
for f in updated:
    print(f"  {f}")

if errors:
    print(f"\nErrors ({len(errors)}):")
    for name, err in errors:
        print(f"  {name}: {err}")
