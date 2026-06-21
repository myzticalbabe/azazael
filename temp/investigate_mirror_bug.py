import sys, pathlib
sys.stdout.reconfigure(encoding="utf-8")

AZAZAEL = pathlib.Path("C:/Users/clint/azazael")

# 1. Check skills directory
skills_dir = AZAZAEL / "skills"
print("=== azazael/skills/ directory ===")
if skills_dir.is_dir():
    files = sorted(skills_dir.glob("*.md"))
    for f in files:
        print(f"  {f.name}: {f.stat().st_size} bytes")
    print(f"  Total: {len(files)} .md files")
else:
    print("  DIRECTORY NOT FOUND")
print()

# 2. Check shim file specifically
shim = skills_dir / "azazael-mandates.md"
print(f"azazael-mandates.md exists: {shim.exists()}")
if shim.exists():
    print(f"  Size: {shim.stat().st_size} bytes")
    print(f"  Content preview: {shim.read_text('utf-8')[:300]}")
else:
    print("  SHIM FILE DOES NOT EXIST - this may be the root cause!")
print()

# 3. Check .agents/skills/azazael-mandates/ directory and SKILL.md
target_dir = pathlib.Path("C:/Users/clint/.agents") / "skills" / "azazael-mandates"
print(f".agents/skills/azazael-mandates/ exists: {target_dir.exists()}")
if target_dir.exists():
    contents = [f.name for f in target_dir.iterdir()]
    print(f"  Contents: {contents}")
    skill_md = target_dir / "SKILL.md"
    print(f"  SKILL.md exists: {skill_md.exists()}")
    if skill_md.exists():
        print(f"  SKILL.md size: {skill_md.stat().st_size} bytes")
    else:
        print("  *** SKILL.md IS MISSING - directory exists but file doesn't! ***")
else:
    print("  Directory does not exist")
print()

# 4. Try to import and run the functions directly
sys.path.insert(0, str(AZAZAEL / "src" / "SCRIPTS"))
try:
    from sync_skills import _mirror_root_file, _get_shim_frontmatter, _build_mirror_content
    
    project_root = pathlib.Path("C:/Users/clint")
    
    # Test _get_shim_frontmatter
    fm = _get_shim_frontmatter("azazael-mandates", project_root)
    print(f"_get_shim_frontmatter() => {repr(fm[:80] + '...') if fm else 'EMPTY STRING'}")
    print(f"  Frontmatter length: {len(fm)} chars")
    
    # Test _build_mirror_content
    source = AZAZAEL / "MANDATES.md"
    print(f"\nMANDATES.md source: {source}")
    print(f"  Exists: {source.exists()}")
    if source.exists():
        print(f"  Size: {source.stat().st_size} bytes")
    
    combined = _build_mirror_content(source, "azazael-mandates", project_root)
    print(f"\n_build_mirror_content() => {len(combined)} bytes")
    print(f"  First 200 bytes: {combined[:200]}")
    
    # Test _mirror_root_file with dry_run to see what it says
    print("\n=== Running _mirror_root_file(dry_run=True) ===")
    result = _mirror_root_file(source, "azazael-mandates", project_root, verbose=True, dry_run=True)
    print(f"  Result: {result}")
    
except Exception as e:
    print(f"ERROR during function test: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
