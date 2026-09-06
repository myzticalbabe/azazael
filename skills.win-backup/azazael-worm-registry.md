---
name: azazael-worm-registry
description: Full API reference for worm_registry.py — @register_worm, WORM_REGISTRY, discover_worms() with progress_callback, SpawnDiversityEngine, category helpers, and cross-platform optimization patterns.
metadata:
  category: architecture
  project: azazael
  priority: high
---

# Azazael Worm Registry — Full API Reference

## Core File: `CORE/worm_registry.py`

## Key Global Objects

```python
WORM_REGISTRY: Dict[str, Dict]  # {worm_name: {category, priority, cooldown, class, ...}}
_registry_lock: threading.RLock  # Thread-safe registry access
_discovery_done: bool            # True after discover_worms() completes
```

## Decorator: `@register_worm`

### Signature
```python
@register_worm(
    category: str = "utility",          # One of 18 categories
    priority: int = 5,                  # 1-10, higher = more important
    cooldown_seconds: float = 30.0,     # Min seconds between spawns
    description: str = "",              # Human-readable description
    tags: Optional[Set[str]] = None,    # Optional tags for filtered selection
)
```

### Registration Metadata
Each registered worm stores:
| Key | Type | Description |
|-----|------|-------------|
| `class` | type | The actual worm class |
| `module` | str | Module name (e.g., `CORE.WORMS.SYSTEMZ`) |
| `category` | str | One of the 18 categories |
| `priority` | int | 1-10 spawn priority |
| `cooldown_seconds` | float | Minimum time between spawns |
| `description` | str | First line of docstring |
| `registered_at` | str | ISO timestamp of registration |
| `spawn_count` | int | Incremented on each spawn |
| `last_spawned` | str or None | ISO timestamp of last spawn |
| `tags` | set | Tags for filtered selection |
| `source_file` | str | Path to source file (from `inspect.getfile`) |
| `version` | str | From `cls.VERSION` or `"0.0.0"` |

## Auto-Discovery: `discover_worms()`

### Signature
```python
def discover_worms(
    worms_dir: Optional[str] = None,
    progress_callback: Optional[Callable[[int, int, str], None]] = None,
) -> int:
    """
    Args:
        worms_dir: Path to WORMS directory (default: CORE/WORMS).
        progress_callback: Optional callback(processed, total, module_name)
            called BEFORE each module is imported. Not called for already-
            registered modules. Use for CLI progress display.
            Signature: callback(processed: int, total: int, module_name: str)

    Returns: Number of newly discovered worm classes.
    """
```

### Callback Behavior
- `processed`: Position in the full sorted file list (includes skipped modules)
- `total`: Total discoverable `.py` files (excludes `_`-prefixed and `.`-prefixed files)
- `module_name`: Module name being imported (e.g., `"SYSTEMZ"`)
- Fires only for modules that pass the pre-import `registered_files` set check
- Recommended usage in CLI:
  ```python
  def _progress(p, t, n):
      print(f"\r  [discover] {p}/{t} - {n}", file=sys.stderr, end="", flush=True)
  discover_worms(progress_callback=_progress)
  print(file=sys.stderr)  # newline after progress
  ```

### Performance Characteristics
| Scenario | Time | Notes |
|----------|------|-------|
| Cold start (first call) | ~0.7s | 95 worms across 18 categories |
| Warm call (second+) | ~0.0008s | 1060x speedup from `registered_files` set |
| With progress callback | Same as cold | Callback adds negligible overhead |

### Discovery Algorithm
1. **Pre-compute `registered_files` set** — `os.path.basename()` on all existing `WORM_REGISTRY` source files (O(1) lookup, uses `if info.get("source_file")` filter to avoid empty strings)
2. **Build `py_files` list once** — Single `os.listdir()` iteration with sorting
3. **For each file**: Skip if in `registered_files` (set lookup) → fire callback → `importlib.import_module()` → check post-import registry for auto-registered classes → scan `dir(module)` for classes with `VERSION` attribute
4. **Auto-categorize** new worms using heuristics (`_guess_category`, `_guess_priority`, `_guess_cooldown`)

### Cross-Platform Path Handling
```python
# CORRECT — os.path.basename() handles both / and \\ on all platforms:
registered_files = {
    os.path.basename(info.get("source_file", ""))
    for info in WORM_REGISTRY.values()
    if info.get("source_file")
}

# WRONG — split(os.sep)[-1] fails on Windows when __file__ uses forward slashes:
registered_files = {
    info.get("source_file", "").split(os.sep)[-1]  # BUG on Windows!
    for info in WORM_REGISTRY.values()
}
```

## SpawnDiversityEngine

### Constructor
```python
engine = SpawnDiversityEngine()
```

### Key Methods

#### `record_spawn(worm_type, category, priority, reason="")`
Record a spawn event for diversity tracking. Thread-safe (uses `threading.Lock`). Prunes history to last 1000 records.

#### `pick_next_spawn(fleet_status=None, worm_types_override=None) -> Optional[Dict]`
Pick the best next worm type to spawn. Returns `{"type", "priority", "reason", "category"}` or `None`. Features:
- **Cooldown enforcement**: Each type has minimum time between spawns
- **Category rotation**: Never same category consecutively
- **Staleness bonus**: Up to 5.0 bonus for never-spawned worms
- **Time-based patterns**: Different profiles based on hour of day
- **Fleet status integration**: CPU, error rate, failed count

#### `pick_diverse_batch(count, fleet_status=None) -> List[Dict]`
Pick a diverse batch of `count` worm types, each from different categories.

#### `get_staleness_report(worm_types_override=None) -> List[Dict]`
Report of all worm types sorted by staleness (never-spawned first).

### Scoring Formula
```
score = priority * 2.0  +  staleness_bonus * 3.0  +  time_bonus * 1.5  +  fleet_bonus * 2.0
```

### Time-Based Patterns
| Time | Categories Favored | Bonus |
|------|-------------------|-------|
| 06:00–12:00 (Morning) | monitor, sync | +2.0 / +1.0 |
| 12:00–18:00 (Afternoon) | analysis, optimization, diagnostic | +2.0 / +2.0 / +1.5 |
| 18:00–22:00 (Evening) | defense, diagnostic | +2.0 |
| 22:00–06:00 (Night) | repair, sync, orchestration, optimization | +2.0 / +1.5 |

## Convenience Functions

```python
get_worms_by_category(category: str) -> Dict[str, Dict]
# Get all worms in a category.

get_all_categories() -> Set[str]
# Get all unique categories in the registry.

get_unspawned_worms() -> List[str]
# List worm types that have never been spawned.

mark_spawned(worm_type: str)
# Increment spawn count, set last_spawned timestamp. Thread-safe.

reset_registry()
# Clear registry (for testing). Thread-safe.
```

## Category Heuristics

`_guess_category()` uses keyword matching against class and module names:

| Keywords | Returns |
|----------|---------|
| DIAG, SCAN, INSPECT | `"diagnostic"` |
| ANALYSIS, ANALYZE, REVERSE | `"analysis"` |
| ERROR, HEALTH, HEAL, REPAIR, DEFENSE | `"defense"` |
| OPTIMIZE, OPTIMIZ, TRIM, PRUNE | `"optimization"` |
| ORCHESTRATE, ORCHESTRA, META, HYDRA | `"orchestration"` |
| SYNC, CLOCK, TIME | `"sync"` |
| SYSTEM, PROCESS, DISK, NETWORK, NET, MONITOR | `"monitor"` |
| CLUSTER, FLEET, POOL, SPAWN | `"orchestration"` |
| (no match) | `"utility"` |

## Thread Safety Design

| Component | Mechanism | Why |
|-----------|-----------|-----|
| WORM_REGISTRY writes | `threading.RLock()` | Safe concurrent registration |
| SpawnDiversityEngine | `threading.Lock()` | Per-instance lock for history |
| `discover_worms()` | Called on main thread only | `importlib.import_module()` NOT thread-safe under 3.14t |
| `mark_spawned()` | `_registry_lock` | Atomic counter increment + timestamp |

## Performance Benchmarks

| Operation | Time | Notes |
|-----------|------|-------|
| `discover_worms()` cold | ~1.0s | 95 worms, 36 modules |
| `discover_worms()` warm | ~0.8ms | 1060x speedup from `os.path.basename()` fix |
| `WORM_REGISTRY.get()` | ~0.1μs | Dict lookup |
| `get_worms_by_category()` | ~1μs | Dict comprehension over registry |
| `pick_next_spawn()` | ~50μs | Linear scan over 95 worms |
| `get_staleness_report()` | ~100μs | Scan + sort |

## Key Optimization History

### Lesson #30 (June 3, 2026) — 1060x warm speedup
- **Bug**: `split(os.sep)[-1]` on Windows doesn't match forward-slash paths from `inspect.getfile()`
- **Fix**: `os.path.basename()` handles both `/` and `\` on all platforms
- **Result**: Warm `discover_worms()` went from ~1.0s to ~0.0008s

### Additional Optimizations
- Attribute checks (`startswith('_')`, `endswith('Config')`) moved BEFORE `getattr()` to avoid unnecessary attribute access
- Single `os.listdir()` iteration (built `py_files` list once instead of twice)
- Stored `_guess_category()` result to avoid double call
- Added `if info.get("source_file")` filter to prevent empty-string set entries
- Added optional `progress_callback` parameter for CLI progress display

## Usage Examples

### Basic Registration
```python
from CORE.worm_registry import register_worm

@register_worm(category="diagnostic", priority=7, cooldown_seconds=30)
class NetworkDiag:
    VERSION = "1.0.0"
    
    def execute(self):
        return {"status": "ok"}
```

### CLI Discovery with Progress
```python
import sys
from CORE.worm_registry import discover_worms, WORM_REGISTRY

def _progress(p, t, n):
    print(f"\r  [discover] {p}/{t} - {n}", file=sys.stderr, end="", flush=True)

count = discover_worms(progress_callback=_progress)
print(file=sys.stderr)
print(f"Discovered {count} new worms, {len(WORM_REGISTRY)} total")
```

### Spawn Diversity Engine
```python
from CORE.worm_registry import SpawnDiversityEngine

engine = SpawnDiversityEngine()

# Pick the next best worm to spawn
pick = engine.pick_next_spawn()
if pick:
    print(f"Spawn {pick['type']} — {pick['reason']}")

# Record spawns
engine.record_spawn("SYSTEMZ", "monitor", 8, "scheduled")

# Get diversity batch
batch = engine.pick_diverse_batch(3)
for b in batch:
    print(f"  {b['type']} ({b['category']}) — {b['reason']}")

# Check staleness
for item in engine.get_staleness_report()[:5]:
    print(f"  {item['type']}: {item['hours_since_last']}h since last spawn")
```

## Related Skills
- `azazael-worms` — Full 95-worm catalog, 18 categories
- `azazael-worms-core` — orchestration, utility, diagnostic (15 worms)
- `azazael-worms-monitor` — monitor, profiling, telemetry (16 worms)
- `azazael-worms-security` — security, config, backup (15 worms)
- `azazael-worms-devops` — container, communication, migration (15 worms)
- `azazael-worms-data` — learning, ml, analysis, visualization, sync (16 worms)
- `azazael-clusters` — ClusterWORMZ, NatureClusters, MetaCluster consumers
- `azazael-threading` — 3.14t threading patterns, lock-free queues
- `azazael-parallel` — FreeThreadPool, work-stealing, batch collection
