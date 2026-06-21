---
name: azazael-operating-protocols
description: Operating protocols for Codebuff/AI agents working on Azazael — 11 followups mandate, max parallel agent execution, proactive skill creation, full tool arsenal usage, create skills on-the-fly
metadata:
  category: workflow
  project: azazael
  priority: critical
  auto_load: true
  version: 1.0.0
  created: 2026-06-14
---

# Azazael Operating Protocols

> **Codified:** June 14, 2026
> **Purpose:** Permanent operating directives for all AI agents working on the Azazael project.
> **Violation:** Any deviation from these protocols must be recorded as an ERROR_LOG entry.

---

## 1. 11 Followups Mandate

After EVERY assistant response that completes a task, provide exactly **11 followup suggestions** using the `suggest_followups` tool.

- **Do not** provide fewer than 11 unless the tool rejects it
- **Do not** provide more than 11
- Each followup should be distinct and actionable
- Cover different areas: diagnostics, fixes, new features, audits, skill creation, etc.
- Label each suggestion with a short (<30 char) label

## 2. Maximum Parallel Agent Velocity (RULE 0Z-F Mandate)

**RULE 0Z-F mandates: ALL independent work items in ONE spawn_agents call. Never sequentialize by default.**

When executing any task:

1. **Identify ALL independent sub-tasks** that can run in parallel
2. **Batch ALL parallel work into ONE spawn_agents call** — never spawn one agent, wait, then spawn another
3. **Spawn the maximum feasible number** of agents concurrently (up to platform limit)
4. **Use 2-6 file-pickers** simultaneously for context gathering
5. **Use 2-5 code-searchers** simultaneously for codebase queries
6. **Use 3-8 bashers** simultaneously for diagnostics and verification
7. **Batch tool calls aggressively** — if it doesn't have a dependency, run it now
8. **Never "serialize by default"** — the default assumption is parallel; only sequentialize on hard dependency

### Memory Anchor for AP-ZF-1 (Sequential Default Override)

When planning work, ask: "Can these run in parallel?" If yes: ONE spawn_agents call. NEVER sequential.

### Parallel Execution Guidelines

| Phase | Typical Agents | Purpose |
|-------|---------------|---------|
| Context gathering | 4-10 agents (file-picker, code-searcher, basher) | Read files, search codebase, run diagnostics |
| Implementation | 2-6 agents (basher, str_replace/write_file) | Apply fixes, create files. ALL independent edits in parallel. |
| Verification | 3-8 agents (basher, code-reviewer) | Run tests, typecheck, review. ALL in ONE call. |

## 3. Proactive Skill Loading

Before any task:

1. **Identify all relevant skills** from the SKILLS_CATALOG.md
2. **Load them before starting** using `skill("skill-name")`
3. **Minimum loading**: Always load `azazael-error-prevention` before any code edits
4. **Always load** skills related to the domain being worked on

## 4. On-the-Fly Skill Creation

Create new skills **without needing a prompt** when you identify:

- **Recurring patterns** — any pattern you've used 2+ times
- **Knowledge gaps** — information you had to research that's not codified
- **Anti-patterns** — mistakes that should be prevented in the future
- **Architecture decisions** — why things are structured a certain way
- **Tool usage** — how to use specific tools/APIs effectively
- **Integration knowledge** — how components connect

### Skill Creation Format

```markdown
---
name: azazael-skill-name
description: One-line description of the skill's purpose
metadata:
  category: [workflow|architecture|quality|domain|deployment|algorithm]
  project: azazael
  priority: [critical|high|standard|low]
  auto_load: true|false
  version: 1.0.0
  created: YYYY-MM-DD
---

# Skill Title

> **Context:** Why this skill exists
> **Replaces:** Any prior knowledge sources

## Core Knowledge

The essential information.

## Usage Patterns

How to use this.

## Anti-Patterns

What NOT to do.

## Related Skills

- `skill-name` — why related
```

### After Creating a Skill

1. Run `sync_skills.py` to propagate to `.agents/skills/`
2. Update `SKILLS_CATALOG.md` with the new entry
3. Record to DirectMemory: `dm.skill_loaded("azazael-skill-name")`

## 5. Full Tool Arsenal

Use every available tool - never rely on just one approach:

- **`gravity_index`** — For researching and selecting third-party services (databases, auth, payments, hosting, AI, etc.)
- **`researcher_web`** — For web research and finding documentation
- **`researcher_docs`** — For reading technical docs of major libraries
- **`browser_use`** — For testing web apps in Chrome (requires Chrome installed)
- **`read_url`** — For fetching and extracting page text from URLs
- **`tmux_cli`** — For testing CLI applications interactively
- **`file_picker`** — For fuzzy-finding files by topic
- **`code_searcher`** — For regex-based source code search
- **`basher`** — For running terminal commands and diagnostics
- **`read_files`** — For reading file contents
- **`str_replace`** / **`write_file`** — For editing files
- **`list_directory`** / **`glob`** — For exploring directory structure
- **`ask_user`** — For asking the user questions/choices
- **`render_ui`** — For interactive UI widgets (buttons)
- **`spawn_agents`** — For spawning specialized agents
- **`suggest_followups`** — For suggesting next actions

## 6. Minimum Agent Spawns

| Task Type | Minimum Agents | Required Types |
|-----------|---------------|----------------|
| Simple edit (<10 lines) | 1 basher | Verify the edit |
| Complex feature (>50 lines) | 4+ agents | Context + implement + verify + review |
| Diagnostic | 2+ agents | Run + verify |
| File creation | 1 code-reviewer | After creation |
| Multi-file change | 3+ agents | Context + implement + search-fix + verify + review |

## 7. Verification Before Edit

Before ANY `str_replace` or `write_file`:

1. **Read the file first** — never edit without reading
2. **Scan for anti-patterns** — Unicode emoji in Windows, backslash f-strings, `os.system`, `C:\` hardcoded paths
3. **Check for existing lock patterns** — use the same threading pattern as neighboring code
4. **Verify import exists** — don't add imports for non-existent modules

## 7. Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| **Providing < 11 followups** | User explicitly mandated 11 — fewer violates RULE 0Z-B | Always count to 11; if stuck, add diagnostic, audit, or skill-creation suggestions |
| **Running agents sequentially** | Wastes parallel capacity — increases wall-clock time by 2-5x | Identify independent tasks and batch them in a single `spawn_agents` call |
| **Editing without reading first** | Guarantees wrong context — str_replace will fail on mismatched whitespace | Always `read_files` or `list_directory` before any edit |
| **Not creating a skill when needed** | Knowledge is lost between sessions — forces re-researching | Create a skill if you: researched something, found a pattern, fixed a bug, or learned an API |
| **Hardcoding paths** | Breaks on different machines; causes Error #49+ patterns | Use `Path(__file__).resolve()` or os.path.join for all paths |
| **Using os.system()** | Not thread-safe, no error handling, shell injection risk | Use `subprocess.run()` with check=True |
| **Inline Python with for loops** | Python -c doesn't support multi-line control flow | Use triple-quoted strings or write a temp script file |
| **Assuming GIL serialization** | Breaks under Python 3.14t free-threading | Always use explicit locks for shared state mutations |

## 8. Session Recording

Every session must:

1. Initialize DirectMemory at start: `dm = DirectMemory()` or `get_dm()`
2. Record file reads: `dm.file_read(paths, description)`
3. Record skill loads: `dm.skill_loaded("skill-name")`
4. Record file edits: `dm.file_edit(path, description, lines_changed=N)`
5. Record milestones: `dm.milestone(title, details)`
6. Call `dm.end(summary)` at session end

## Related Skills

- `azazael-eleven-followups` — RULE 0Z-B 11 followups mandate
- `azazael-error-prevention` — Anti-pattern catalog
- `azazael-sop` — Standard operating procedures
- `azazael-mandates` — All 36 RULE mandates
- `azazael-direct-memory` — DirectMemory session recording API
