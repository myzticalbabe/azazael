# Azazael Cross-Reference System — Quickstart Tutorial

## 1. Initialize a Session

```python
from CORE.direct_memory import DirectMemory
dm = DirectMemory()
dm.file_read(["MEMORIES.md"], "Start tutorial")
dm.skill_loaded("tutorial")
```

## 2. Record Events

```python
dm.file_edit("main.py", "Fix bug", lines_changed=3)
dm.test_run("pytest", passed=10, failed=0)
dm.milestone("Phase 1 complete", {"tasks": 5})
```

## 3. Link an Audit Session

```python
dm.link_audit_session(".audit/session_tutorial.jsonl",
                       audit_session_id="abc-123",
                       mapping_type="manual",
                       notes="Tutorial link")
```

## 4. Query Cross-References

```python
# Get all mappings for this session
mappings = dm.list_mappings()
for m in mappings:
    print(m["audit_filepath"], m["confidence"])

# Cross-ledger JOIN query
results = DirectMemory.query_cross_reference(dm_session_id=dm.session_id)
```

## 5. Run Backfill

```python
result = DirectMemory.cross_reference_ledgers()
print(f"Linked: {result['new_links']} new sessions")
```

## 6. View Summary

```python
summary = DirectMemory.get_mapping_summary()
print(summary)
```

## 7. Using the CLI

```bash
# View system status
python -m CORE.azazael_ctl status

# Run backfill
python -m CORE.azazael_ctl crossref backfill

# List mappings
python -m CORE.azazael_ctl crossref list

# Interactive browser
python -m CORE.azazael_ctl crossref interactive
```

## 8. Generate Dashboard

```bash
python -m CORE.xref_dashboard
# Opens xref_dashboard.html in browser
```

## 9. End Your Session

```python
dm.end({"summary": "Tutorial complete"})
```
