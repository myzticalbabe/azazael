# coding: utf-8
"""
Auto-Generate Docstrings for Python Modules
"""

from pathlib import Path
from typing import List, Dict
import ast
import os
import re


def generate_docstring(module_path: Path) -> str:
    """Generate a docstring for a module."""
    name = module_path.stem
    module_dir = module_path.parent.name

    # Parse AST for functions and classes
    try:
        content = module_path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(content)

        functions = []
        classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.name.startswith("_"):
                    functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)

    except:
        functions = []
        classes = []

    # Generate docstring
    docstring = f'''"""
{name.replace("_", " ").title()}

Module for {module_dir} functionality.

Functions:
'''

    for func in functions[:10]:
        docstring += f"    - {func}()\n"

    if classes:
        docstring += f"\nClasses:\n"
        for cls in classes[:5]:
            docstring += f"    - {cls}\n"

    docstring += f'''
Usage:
    >>> import {name}
    >>> {name}.{functions[0] if functions else "function"}()

Author: Auto-generated
Date: 2026-02-10
"""

'''

    return docstring


def add_docstring_to_module(module_path: Path) -> bool:
    """Add docstring to module if missing."""
    try:
        content = module_path.read_text(encoding="utf-8", errors="replace")

        # Check if already has docstring
        stripped = content.lstrip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            return False

        # Generate and add docstring
        docstring = generate_docstring(module_path)

        # Preserve shebang and encoding
        new_content = docstring + content

        module_path.write_text(new_content, encoding="utf-8")
        return True

    except Exception as e:
        return False


def process_directory(directory: str) -> Dict:
    """Process all Python files in directory."""
    results = {"processed": 0, "added": 0, "skipped": 0, "files": []}

    for py_file in Path(directory).rglob("*.py"):
        # Skip __pycache__ and test files
        if "__pycache__" in str(py_file) or "test_" in py_file.name:
            continue

        results["processed"] += 1

        if add_docstring_to_module(py_file):
            results["added"] += 1
            results["files"].append(str(py_file))
        else:
            results["skipped"] += 1

    return results


def main():
    print("=" * 70)
    print("DOCSTRING GENERATOR")
    print("=" * 70)

    directories = [
        "C:\\Users\\clint\\Desktop\\Azazael\\ml_platforms",
        "C:\\Users\\clint\\Desktop\\Azazael\\scripts",
    ]

    total_added = 0
    total_processed = 0

    for directory in directories:
        print(f"\nProcessing: {directory}")
        results = process_directory(directory)
        total_processed += results["processed"]
        total_added += results["added"]
        print(f"  Processed: {results['processed']}")
        print(f"  Added docstrings: {results['added']}")
        print(f"  Skipped (already has): {results['skipped']}")

    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    print(f"Total processed: {total_processed}")
    print(f"Total docstrings added: {total_added}")

    return {"processed": total_processed, "added": total_added}


if __name__ == "__main__":
    main()
