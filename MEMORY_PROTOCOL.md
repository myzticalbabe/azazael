# Azazael Persistent Memory Protocol

## Purpose

This document defines how Codebuff and its sub-agents should use the Azazael persistent
memory system to achieve cross-session learning — getting smarter over time.

## The Problem

Each Codebuff session starts with only a lossy conversation summary. Key decisions,
lessons learned, file changes, and architectural patterns are lost between sessions.
The project HAS a persistent memory database (graph.db) but it was only used for code
structure graphs (nodes, edges, flows, communities) — NOT for session learning.

## The Solution

`workspace/session_memory.db` (SQLite) stores:
- **sessions**: Start/end time, summary, agent model, change counts
- **decisions**: Context, decision made, rationale, outcome
- **file_changes**: File path, change type (created/modified/deleted/moved), description
- **lessons**: Pattern observed, lesson learned, category, confidence score
- **goals**: Pending/in-progress/completed goals tracked across sessions

## How Codebuff Should Use It

### At Session Start

```python
from session_memory import SessionMemory
sm = SessionMemory()
ctx = sm.get_context_for_new_session()
# ctx contains:
#   - recent_sessions: last 5 session summaries
#   - high_confidence_lessons: lessons with confidence >= 0.6
#   - hot_spot_files: files changed in 2+ sessions
#   - pending_goals: uncompleted goals from any session
#   - key_decisions: recent architectural/design decisions
```

Use this context to:
1. Inform coding decisions with past lessons
2. Prioritize pending goals
3. Be cautious with hot-spot files (frequently changed)
4. Avoid repeating past mistakes

### During Session

```python
sm.start_session("Brief description of what this session is about")
sm.record_decision(context, decision, rationale)
sm.record_change(file_path, change_type, description)
sm.record_lesson(pattern, lesson, category, confidence)
sm.set_goal(goal_description, status)
```

### At Session End

```python
sm.end_session(
    summary="What was accomplished",
    total_changes=N,
    goals_completed=M,
    goals_total=K
)
```

## Lesson Categories

- **architecture**: Project structure, module organization, dependencies
- **convention**: Code style, naming, patterns to follow
- **bug_fix**: Bugs found and how they were fixed
- **refactoring**: How code was restructured and why
- **dependency**: Package/library management lessons

## Integration with graph.db

The code structure graph (graph.db via persistent_memory.py) stores nodes, edges,
flows, communities, and risk data. Session memory complements this by storing the
HISTORY of changes and decisions. Together they provide a complete picture.

## Known Pitfalls

1. **File-picker hallucinations**: File-picker agents can return non-existent paths.
   Always verify with `ls` or `find` before acting on file-picker results.

2. **SQLite commit-on-close**: Python's sqlite3 legacy mode does NOT auto-commit on
   connection close. Always ensure `conn.commit()` before `conn.close()`.

3. **Hardcoded dimensions**: UI elements (matrix boxes, banners) should compute
   their dimensions from actual data, not hardcode them.

4. **Verify print statements**: If code prints "Files Generated", verify it actually
   writes the file. Don't trust print statements at face value.

## Database Location

- Session memory: `workspace/session_memory.db`
- Code structure: `workspace/graph.db`

## Maintenance

```bash
# View session memory summary
python3 azazael/src/session_memory.py --summary

# Load context for new session (JSON)
python3 azazael/src/session_memory.py --context

# List lessons
python3 azazael/src/session_memory.py --lessons

# List pending goals
python3 azazael/src/session_memory.py --goals

# Show frequently-changed files
python3 azazael/src/session_memory.py --hot-spots
```
