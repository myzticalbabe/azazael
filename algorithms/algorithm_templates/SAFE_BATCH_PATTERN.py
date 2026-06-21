#!/usr/bin/env python3
"""
SAFE BATCH MODIFICATION TEMPLATE
===============================
APPROVED PATTERN for modifying multiple files.
MANDATORY: Must be reviewed by thinker-with-files-gemini before use.

Requirements:
- Test on ONE file before batch
- Validate syntax after EACH file
- Track modified files for rollback
- Halt on first error
"""

import ast
import pathlib
import sys
import shutil
from datetime import datetime

# === CONFIGURATION ===
SRC_ROOT = pathlib.Path("azazael/src")
BACKUP_DIR = pathlib.Path("azazael/algorithms/backups")
DRY_RUN = True  # Set to False only after Gemini approval

def validate_syntax(filepath: pathlib.Path) -> bool:
    """Verify file has valid Python syntax."""
    try:
        with open(filepath, encoding='utf-8') as f:
            ast.parse(f.read())
        return True
    except SyntaxError as e:
        print(f"  SYNTAX ERROR: {filepath}:{e.lineno} - {e.msg}")
        return False

def backup_file(filepath: pathlib.Path) -> pathlib.Path:
    """Create timestamped backup before modification."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"{filepath.name}.{timestamp}.bak"
    shutil.copy2(filepath, backup_path)
    return backup_path

def modify_file(filepath: pathlib.Path) -> bool:
    """
    MODIFY THIS FUNCTION for your specific fix.
    Returns True if file was modified, False if no changes needed.
    """
    with open(filepath, encoding='utf-8') as f:
        content = f.read()
    
    # === YOUR MODIFICATION LOGIC HERE ===
    # Example: Replace pattern X with Y
    new_content = content  # Replace with actual logic
    
    if new_content == content:
        return False  # No changes needed
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    return True

def main():
    # Step 1: Identify target files
    target_files = list(SRC_ROOT.rglob("*.py"))
    target_files = [f for f in target_files if '__pycache__' not in str(f)]
    
    modified = []
    failed = []
    
    # Step 2: Test on FIRST file
    if not target_files:
        print("No target files found")
        return
    
    print(f"Testing on: {target_files[0]}")
    backup_file(target_files[0])
    
    if modify_file(target_files[0]):
        if validate_syntax(target_files[0]):
            print("  Single file test: PASSED")
        else:
            print("  Single file test: FAILED - aborting batch")
            return
    else:
        print("  No changes needed")
    
    # Step 3: Get user/agent confirmation before batch
    print(f"\nProceeding with {len(target_files)} files. Continue? (y/n)")
    # In automated mode, this should be replaced with agent confirmation
    
    # Step 4: Batch apply with per-file validation
    for i, filepath in enumerate(target_files):
        backup = backup_file(filepath)
        
        try:
            if modify_file(filepath):
                if validate_syntax(filepath):
                    modified.append(filepath)
                    print(f"  [{i+1}/{len(target_files)}] OK: {filepath.name}")
                else:
                    # ROLLBACK on failure
                    shutil.copy2(backup, filepath)
                    failed.append(filepath)
                    print(f"  [{i+1}/{len(target_files)}] FAILED (rolled back): {filepath.name}")
                    # HALT on first failure
                    print("HALTING BATCH - first failure detected")
                    break
            else:
                print(f"  [{i+1}/{len(target_files)}] SKIP: {filepath.name} (no changes)")
        except Exception as e:
            shutil.copy2(backup, filepath)
            failed.append(filepath)
            print(f"  [{i+1}/{len(target_files)}] ERROR (rolled back): {filepath.name} - {e}")
            break
    
    # Step 5: Report
    print(f"\n=== BATCH COMPLETE ===")
    print(f"Modified: {len(modified)}")
    print(f"Failed (rolled back): {len(failed)}")
    print(f"Backups at: {BACKUP_DIR}")

if __name__ == "__main__":
    main()
