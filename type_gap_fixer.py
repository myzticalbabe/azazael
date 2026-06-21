#!/usr/bin/env python3
"""Gemini-architected type-gap fixer for azazael/src/.

Fixes bare Dict/List/Tuple/Set/Optional/Any type annotations
in files where `from typing import ...` was commented out.
RULE 0G: Design by Gemini, execution by Buffy.
"""
import os
import re
from pathlib import Path

def fix_type_gaps():
    target_dir = Path("src/")
    if not target_dir.exists():
        print(f"Directory {target_dir} not found. Please run from azazael/")
        return

    py_files = list(target_dir.rglob("*.py"))
    fixed_count = 0

    for path in py_files:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        modified = False
        needs_any = False
        has_any_import = False
        new_lines = []

        for line in lines:
            # Track 'Any' imports
            if re.search(r'^from typing import.*?\bAny\b', line):
                has_any_import = True

            # Leave pure comments untouched
            if line.strip().startswith("#"):
                new_lines.append(line)
                continue

            original_line = line
            parts = line.split("#", 1)
            code = parts[0]

            # 1. Clean up imports but DO NOT touch the "removed" comment
            if re.search(r'^from typing import', code):
                for word in ['Dict', 'List', 'Tuple', 'Set', 'Optional']:
                    code = re.sub(r'\b' + word + r'\b,?\s*', '', code)
                
                # Cleanup trailing commas and empty imports
                code = re.sub(r',\s*$', '', code.strip())
                if code == "from typing import":
                    code = ""  # Remove empty import line
                else:
                    code += "\n" if original_line.endswith("\n") else ""

            # 2. Fix nested Optional[X] -> X | None dynamically
            while "Optional[" in code:
                start = code.find("Optional[")
                brackets = 0
                end = -1
                for i in range(start + 8, len(code)):
                    if code[i] == "[":
                        brackets += 1
                    elif code[i] == "]":
                        brackets -= 1
                        if brackets == 0:
                            end = i
                            break
                if end != -1:
                    inner = code[start+9:end]
                    code = code[:start] + f"{inner} | None" + code[end+1:]
                else:
                    break  # Malformed, don't infinite loop

            # 3. Standard bare type replacements (native Python 3.9+)
            code = re.sub(r'\bDict\b', 'dict', code)
            code = re.sub(r'\bList\b', 'list', code)
            code = re.sub(r'\bTuple\b', 'tuple', code)
            code = re.sub(r'\bSet\b', 'set', code)

            # Re-attach inline comments untouched
            new_line = code + ("#" + parts[1] if len(parts) > 1 else "")
            
            if new_line != original_line:
                modified = True

            new_lines.append(new_line)

            # 4. Check if bare 'Any' is left over
            if re.search(r'\bAny\b', code):
                needs_any = True

        # Insert 'from typing import Any' if actively used but not imported
        if needs_any and not has_any_import:
            # Find safe insertion index (after docstring/future imports)
            insert_idx = 0
            for i, l in enumerate(new_lines):
                if l.startswith("import ") or l.startswith("from "):
                    insert_idx = i
                    break
            new_lines.insert(insert_idx, "from typing import Any\n")
            modified = True

        if modified:
            with open(path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            fixed_count += 1
            print(f"Fixed: {path}")

    print(f"\nDone. Fixed type gaps in {fixed_count} Python files.")

if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    fix_type_gaps()
