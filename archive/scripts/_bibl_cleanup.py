#!/usr/bin/env python3
"""
_bibl_cleanup.py — Clean self-referential entries from BIBL files.

Self-referential entries are those whose Source field points to the BIBL file
containing the entry itself (e.g., in E.md, entries where *Source: BIBL/E.md).
These are circular references — they don't point to actual source code.

REANALYSIS_DISCOVERIES.md findings:
  - P.md: 257 self-ref entries deleted (54%), 296K→254K
  - E.md: 41,507 self-ref entries, 332K lines, 12.7MB
  - F.md: 366,957 self-ref entries, 2.9M lines, 65MB
  - Total recoverable: 412,056 circular entries across all BIBL files

Usage:
  python _bibl_cleanup.py E          # dry-run E.md, show stats
  python _bibl_cleanup.py E --apply  # clean E.md with backup
  python _bibl_cleanup.py F          # dry-run F.md (slow — 65MB)
  python _bibl_cleanup.py F --apply  # clean F.md with backup
  python _bibl_cleanup.py --all      # dry-run all BIBL files
"""
import os, sys, re, shutil, argparse
from pathlib import Path
from datetime import datetime

BIBL_DIR = Path(__file__).resolve().parent / "src" / "ORCHESTRATION" / "BIBL"
BACKUP_DIR = BIBL_DIR / "backups"


def parse_entries(content: str, letter: str):
    """Parse BIBL content into entries. Returns list of (is_self_ref, entry_text, name)."""
    # Split on ## headers (entries start with ## Name)
    raw_entries = re.split(r'\n(?=## )', content)
    
    results = []
    for chunk in raw_entries:
        chunk = chunk.strip()
        if not chunk:
            continue
        
        # Extract entry name from header
        name_match = re.match(r'## (.+)', chunk)
        name = name_match.group(1).strip() if name_match else "?"
        
        # Extract source: format is `*Source: `category` | File: path*`
        source_match = re.search(r'\*Source:\s*(.+?)(?:\n|$)', chunk)
        source_raw = source_match.group(1).strip() if source_match else ""
        
        # Parse the compound format: `category` | File: path
        # Example: `markdown_header` | File: C:\Users\clint\azazael\src\ORCHESTRATION\BIBL\E.md
        source_file = ""
        source_category = ""
        if source_raw:
            file_match = re.search(r'\|\s*File:\s*(.+?)\s*$', source_raw)
            if file_match:
                source_file = file_match.group(1).strip()
            cat_match = re.match(r'`([^`]+)`', source_raw)
            if cat_match:
                source_category = cat_match.group(1)
        
        # Classification: self-ref = source file IS the BIBL file being processed
        is_self_ref = False
        if source_file:
            # Strip trailing markdown formatting characters (*, _)
            source_file = source_file.rstrip('*_')
            # Normalize both paths for comparison
            src_norm = source_file.replace('\\', '/').lower()
            bib_norm = f"bibl/{letter.lower()}.md"
            is_self_ref = (
                src_norm.endswith(bib_norm) or
                src_norm.endswith(f"/{bib_norm}")
            )
        
        source = source_file  # For display in stats
        
        results.append((is_self_ref, chunk, name, source))
    
    return results


def safe_print(msg: str):
    """Print safely, replacing unprintable characters."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('ascii', errors='replace').decode('ascii'))


def clean_file(letter: str, dry_run: bool = True, verbose: bool = False):
    """Clean self-referential entries from a BIBL file."""
    filepath = BIBL_DIR / f"{letter}.md"
    
    if not filepath.exists():
        safe_print(f"ERROR: {filepath} not found")
        return None
    
    # Read file
    content = filepath.read_text(encoding="utf-8", errors="replace")
    original_size = len(content)
    original_lines = content.count('\n') + 1
    
    # Parse entries
    entries = parse_entries(content, letter)
    
    self_ref_entries = [(name, source) for is_sr, _, name, source in entries if is_sr]
    legit_entries = [chunk for is_sr, chunk, _, _ in entries if not is_sr]
    
    # Build cleaned content: all text before first entry + legit entries
    # Find first ## header
    first_header = re.search(r'\n## ', content)
    if first_header:
        preamble = content[:first_header.start()]
    else:
        preamble = content  # No ## headers — entire file is preamble
    
    cleaned = preamble + "\n\n" + "\n\n".join(legit_entries) + "\n"
    cleaned_size = len(cleaned)
    cleaned_lines = cleaned.count('\n') + 1
    
    # Stats
    stats = {
        "file": f"{letter}.md",
        "original_size": original_size,
        "original_lines": original_lines,
        "total_entries": len(entries),
        "self_ref_entries": len(self_ref_entries),
        "legit_entries": len(legit_entries),
        "self_ref_pct": round(len(self_ref_entries) / max(len(entries), 1) * 100, 1),
        "cleaned_size": cleaned_size,
        "cleaned_lines": cleaned_lines,
        "size_reduction": original_size - cleaned_size,
        "size_reduction_pct": round((original_size - cleaned_size) / max(original_size, 1) * 100, 1),
    }
    
    if dry_run:
        print(f"\n  [DRY-RUN] {letter}.md")
        print(f"  {'='*50}")
        print(f"  Original: {original_size:,} bytes, {original_lines:,} lines")
        print(f"  Total entries: {len(entries):,}")
        print(f"  Self-referential: {len(self_ref_entries):,} ({stats['self_ref_pct']}%)")
        print(f"  Legitimate: {len(legit_entries):,}")
        print(f"  Would delete: {len(self_ref_entries):,} entries")
        print(f"  Projected size: {cleaned_size:,} bytes ({stats['size_reduction_pct']}% reduction)")
        print(f"  Bytes removed: {stats['size_reduction']:,}")
        
        if verbose and self_ref_entries:
            print(f"\n  Sample self-ref entries (first 10):")
            for name, source in self_ref_entries[:10]:
                print(f"    - {name} (source: {source})")
    else:
        # Create backup
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        backup_path = BACKUP_DIR / f"{letter}.md.bak"
        backup_path.write_text(content, encoding="utf-8")
        print(f"  Backup: {backup_path}")
        
        # Write cleaned content
        filepath.write_text(cleaned, encoding="utf-8")
        
        print(f"\n  [APPLIED] {letter}.md")
        print(f"  {'='*50}")
        print(f"  Deleted: {len(self_ref_entries):,} self-referential entries ({stats['self_ref_pct']}%)")
        print(f"  Kept: {len(legit_entries):,} legitimate entries")
        print(f"  Size: {original_size:,} → {cleaned_size:,} bytes ({stats['size_reduction_pct']}% reduction)")
        print(f"  Lines: {original_lines:,} → {cleaned_lines:,}")
        print(f"  Backup: {backup_path}")
    
    return stats


def main():
    parser = argparse.ArgumentParser(description="Clean self-referential BIBL entries")
    parser.add_argument("letter", nargs="?", help="BIBL file letter to clean (e.g., E, F)")
    parser.add_argument("--apply", action="store_true", help="Actually apply changes (creates backup)")
    parser.add_argument("--all", action="store_true", help="Clean all BIBL letter files")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show sample entries")
    
    args = parser.parse_args()
    
    if args.all:
        letters = sorted(set(
            f.stem for f in BIBL_DIR.glob("[A-Z].md")
        ))
        print(f"BIBL Cleanup — {'DRY-RUN' if not args.apply else 'APPLY'} mode")
        print(f"Directory: {BIBL_DIR}")
        print(f"Targets: {len(letters)} files: {', '.join(letters)}")
        
        all_stats = []
        for letter in letters:
            stats = clean_file(letter, dry_run=not args.apply, verbose=args.verbose)
            if stats:
                all_stats.append(stats)
        
        # Summary
        total_self = sum(s["self_ref_entries"] for s in all_stats)
        total_reduction = sum(s["size_reduction"] for s in all_stats)
        print(f"\n  {'='*50}")
        print(f"  ALL FILES SUMMARY ({'DRY-RUN' if not args.apply else 'APPLIED'}):")
        print(f"  Total self-ref entries: {total_self:,}")
        print(f"  Total bytes recoverable: {total_reduction:,}")
        return
    
    if not args.letter:
        parser.print_help()
        print("\nExamples:")
        print("  python _bibl_cleanup.py E           # dry-run E.md")
        print("  python _bibl_cleanup.py E --apply   # clean E.md with backup")
        print("  python _bibl_cleanup.py F           # dry-run F.md (65MB)")
        return
    
    letter = args.letter.upper()
    stats = clean_file(letter, dry_run=not args.apply, verbose=args.verbose)


if __name__ == "__main__":
    main()
