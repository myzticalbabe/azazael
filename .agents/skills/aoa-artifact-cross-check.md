---
name: aoa-artifact-cross-check
description: Verify AOA's arm map is truthful across all four surfaces at once —
  the live registry, AOA_AUDIT_MAP.md §3, the rebuilt diagrams (AOA_STRUCTURE/
  AOA_DISCLOSURE HTML), and the audit JSON (aoa_audit_*.json). Proven 2026-09-02
  (9 arms / 71 caps consistent everywhere); run after any arm change or rebuild.
metadata:
  category: process
  projects: aoa
  priority: high
  audit_date: 2026-09-02
  auto_load: false
---

# AOA Artifact Cross-Check — Four-Surface Consistency

## Why

AOA's arm topology (arm ids, categories, priorities, capability counts, capability
NAMES) is rendered into four separate artifacts: the source registry, the
`AOA_AUDIT_MAP.md` table, the mermaid diagrams in the rebuilt HTML, and the
`aoa_audit_*.json` snapshot. They can drift independently — a builder that reads
statics, a hand-edited map, a stale JSON. The cross-check proves all four tell the
same story against ONE ground truth: the live registry.

## Ground truth

```python
import sys; sys.path.insert(0, 'src/AOA')
for mod in ('arms.azazael_arm', 'arms.codex_arm', 'arms.eve_arm', 'arms.libra_arm',
            'arms.support_arms', 'arms.kali_arm'):
    __import__(mod)
from core.arm_registry import ArmRegistry
reg = ArmRegistry().list_arms()          # per-arm: arm_id, name, category, priority, capabilities
```

## The four checks

1. **Audit map §3** (`output/aoa_atlas/AOA_AUDIT_MAP.md`) — parse the markdown
   table rows (arm / category / pri / caps cell). PITFALL: the caps cell is a
   comma-separated NAME LIST (e.g. `discover_worms, run_cluster, …`), not an
   integer — only kali uses the `get_status + **39 tool**` phrasing. Count list
   items, don't `int()` the cell.
2. **Rebuilt diagrams** (`src/AOA/AOA_STRUCTURE.html` +
   `AOA_DISCLOSURE.html`) — parse `ID["Name - N caps" - Priority P]` nodes.
   AOA_STRUCTURE uses the `Priority` suffix; AOA_DISCLOSURE is FLAT (`Name - N
   caps`, no priority, orchestrator carries `(N arms · M capabilities)`). Two
   parsers, one comparison.
3. **Audit JSON** (`output/aoa_atlas/aoa_audit_*.json` map block) — per-arm
   entries carry capability name lists; totals block includes `kali_by_family`.
   Compare NAMES (sorted) not just counts — the JSON's extra fidelity catches
   renames the diagrams would miss.
4. **Totals** — every surface's summary (9 arms / 71 caps / 4Q / 5S / kali_tools
   39) must equal the registry sums; `kali_by_family` recomputed from
   `KALI_TOOLS` must match the JSON exactly.

## After any arm change or rebuild

1. Rebuild the HTML through `build.py` / `build_disclosure.py` (registry-driven —
   they snapshot live once imported).
2. Re-run the four-surface comparison; expect ZERO inconsistencies.
3. Update the audit JSON map block (or re-run whatever generated it) so its
   snapshot isn't stale — a JSON that disagrees with the registry is worse than
   no JSON.

## Anti-patterns

- `int()` on a name-list cell → false inconsistency (all caps read as 0/None).
- Comparing counts when the JSON carries names — renames pass silently.
- Trusting one surface (e.g. the map) over the registry — the registry is the
  only source of truth; artifacts describe it.
- Forgetting `kali` is `get_status + 39 tools` = 40 caps, and the family
  breakdown must sum to 39.

## See also

- `html-render-verification` — checks the diagrams RENDER (0 console errors);
  this skill checks they're TRUTHFUL. Run both after a rebuild.
- `aoa-architecture` (#1223) — the 9-arm / 71-cap map this check validates.
- `aoa-html-builder` (#1226) — the builders whose outputs are the diagram surface.
- `aoa-kali-arm` (#1247) — the kali arm (s6/40) is the highest-count surface here.