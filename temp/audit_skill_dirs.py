import sys, pathlib
sys.stdout.reconfigure(encoding="utf-8")

skills_dir = pathlib.Path("C:/Users/clint/.agents/skills")
dirs = sorted([d for d in skills_dir.iterdir() if d.is_dir()])

print(f"Total directories: {len(dirs)}")

with_skill = 0
orphaned = []
empty = []

for d in dirs:
    skill_md = d / "SKILL.md"
    files = list(d.iterdir())
    
    if skill_md.exists():
        with_skill += 1
    else:
        if not files:
            empty.append(d.name)
        else:
            orphaned.append((d.name, [f.name for f in files]))

print(f"Directories WITH SKILL.md: {with_skill}")
print(f"Directories WITHOUT SKILL.md: {len(dirs) - with_skill}")

if empty:
    print(f"\n  EMPTY directories ({len(empty)}):")
    for name in empty:
        print(f"    {name}")

if orphaned:
    print(f"\n  ORPHANED directories (no SKILL.md but have files) ({len(orphaned)}):")
    for name, files in orphaned:
        print(f"    {name}: {files}")

if not empty and not orphaned:
    print("\n  ✅ All directories have valid SKILL.md — no orphaned directories")

# Size summary
sizes = [(d.name, (d / "SKILL.md").stat().st_size) for d in dirs if (d / "SKILL.md").exists()]
sizes.sort(key=lambda x: x[1], reverse=True)

total = sum(s for _, s in sizes)
print(f"\nTotal SKILL.md content: {total:,} bytes across {len(sizes)} files")
if sizes:
    print(f"Largest:  {sizes[0][0]} ({sizes[0][1]:,} bytes)")
    print(f"Smallest: {sizes[-1][0]} ({sizes[-1][1]:,} bytes)")
