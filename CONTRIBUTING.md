# Contributing to Azazael

## How to Add a New Event Type

Both DirectMemory (DM) and AuditTrail (AJ) share a canonical event vocabulary.
To add a new event type, follow these steps:

### Step 1: Add the type to the shared vocabulary

In `src/CORE/direct_memory.py`, add to `_V` dict:

```python
_V = {
    ...
    "NEW_EVENT": "new_event",
}
```

In `src/CORE/audit_trail.py`, add to `EVENT_VOCAB` dict:

```python
EVENT_VOCAB = {
    ...
    "NEW_EVENT": "new_event",
}
```

### Step 2: Add a convenience method to DirectMemory

In `src/CORE/direct_memory.py`, add a method like:

```python
def new_event(self, param1: str, param2: int = 0) -> int:
    return self.record(self._V["NEW_EVENT"], {
        "action": f"new_event: {param1}",
        "param1": param1,
        "param2": param2,
    }, tags=["custom-category"])
```

### Step 3: Add an audit function

In `src/CORE/audit_trail.py`, add a function like:

```python
def audit_new_event(param1: str, param2: int = 0) -> str:
    _ensure_session()
    return _append_line({
        "ts": datetime.datetime.now().isoformat(timespec="seconds"),
        "type": "new_event",
        "param1": param1,
        "param2": param2,
    })
```

### Step 4: Export from `__init__.py`

Add both functions to `src/CORE/__init__.py`:

```python
from CORE.direct_memory import DirectMemory  # method is on the class
from CORE.audit_trail import audit_new_event

__all__.extend(["audit_new_event"])
```

## Coding Conventions

- **Stdlib-first**: Prefer stdlib over external dependencies. Only add dependencies
  when absolutely necessary (e.g., `psutil` for system monitoring).
- **Thread safety**: All SQLite access must use `check_same_thread=False` and
  WAL mode for concurrent read/write under 3.14t free-threading.
- **No circular imports**: DirectMemory must never import from CORE modules
  (it's a bootstrap module). InferencePool may import from CORE but only
  from `freethreading.py`.
- **Docstrings**: All public methods must have docstrings with Args/Returns.
- **Tests**: Every new method must have a corresponding test in `tests/`.

## Test Organization

| Directory             | Purpose                                    |
|-----------------------|--------------------------------------------|
| `tests/`              | All test files                             |
| `tests/test_dm_*.py`  | DirectMemory tests                        |
| `tests/test_ip_*.py`  | InferencePool tests                       |
| `tests/test_audit*.py`| Audit trail tests                         |
| `tests/test_cli.py`   | CLI integration tests                     |
| `tests/test_stress.py`| Concurrency stress tests                  |
| `tests/test_perf*.py` | Performance threshold tests               |
| `tests/test_fuzz.py`  | Fuzz/randomized input tests               |
| `tests/test_property*`| Property-based tests (Hypothesis)         |
| `tests/test_mutation*`| Mutation/edge case tests                  |

## Running Tests

```bash
# Run all tests
python3.14t -m pytest tests/ -v

# Run specific test suite
python3.14t -m pytest tests/test_session_mappings.py tests/test_inference_pool.py -v

# Run with coverage
python3.14t -m pytest --cov=src tests/ -v
```

## Pull Request Checklist

- [ ] New event types added to BOTH `_V` (DM) and `EVENT_VOCAB` (AJ)
- [ ] Convenience method added to DirectMemory
- [ ] Audit function added to audit_trail.py
- [ ] Exported from `__init__.py`
- [ ] Tests written and passing
- [ ] Docstrings added
- [ ] CHANGELOG.md updated
