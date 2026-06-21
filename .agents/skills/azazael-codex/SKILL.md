---
name: azazael-codex
description: Azazael CODEX systems — video generation with PIL/ffmpeg, PAMS/MemoryBus memory systems, session audit trails, event publishing patterns.
metadata:
  category: codex
  project: azazael
---
# Azazael CODEX — Video & Memory Systems

## Video Generation Pipeline

### Status
| Capability | Status |
|-----------|--------|
| PIL frame generation | ✅ Working (13.7 fps, 96KB/frame @ 1920×1080) |
| ffmpeg for .mp4 | ❌ Not installed (needs `winget install ffmpeg`) |
| Scrolling video generator | ⚠️ Retained in VIDEOS/, requires ffmpeg |
| Archived superseded scripts | ✅ 14 scripts → `G:\AZAZAEL\CODEX_VIDEOS\` |

### Video Scripts (Remaining — 6 files)
In `azazael/src/CODEX/VIDEOS/`:
- `create_scrolling_video.py` — Main scrolling video generator (HTML → frames → mp4)
- Other active scripts retained

### PIL Frame Generation Pattern
```python
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1920, 1080
img = Image.new('RGB', (WIDTH, HEIGHT), color='#0a0a1a')
draw = ImageDraw.Draw(img)
font = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 28)
draw.text((100, 100), 'CODEX', fill='#00ff88', font=font)
img.save('frame.png', 'PNG')
```

### When ffmpeg is installed
```bash
ffmpeg -framerate 30 -i frame_%04d.png -c:v libx264 -pix_fmt yuv420p output.mp4
```

## Memory Systems

### PamsRecorder — `PamsRecorder.py` (p=3, 30s)
- Session-level audit trail
- Records events with timestamps, metadata
- Used by all cluster operations
- Pattern: `PamsRecorder.record_event("event.name", metadata={...})`

### MemoryBus — `MemoryBus.py` (p=3, 30s)
- Pub/sub event bus for cross-worm communication
- Publish lifecycle events: cluster.execute.start, cluster.execute.complete
- Subscribers can react to events asynchronously
- Pattern: `memory_bus.publish("event.name", data={...})`

### Dual Recording Pattern
Cluster operations record to BOTH PamsRecorder and MemoryBus:
- **PAMS** = Audit trail (persistent, structured)
- **MemoryBus** = Pub/sub (real-time, decoupled)

When adding new cluster operations, always record to both:
```python
# In cluster execute method:
self._record("cluster.execute.start", {"worms": len(configs)})
self._mem_bus.publish("cluster.execute.start", {"count": len(configs)})
# ... execute ...
self._record("cluster.execute.complete", {"results": results})
self._mem_bus.publish("cluster.execute.complete", {"results": results})
```

## Session Metrics
| Metric | Value |
|--------|-------|
| PAMS events recorded | 44 |
| PAMS records | 44 |
| MemoryBus publications | 1 (test) |
| PIL frame generation speed | 13.7 fps |

## Related Skills
- `azazael-mermaid` — Mermaid graph generation patterns
- `azazael-worms` — Full worm catalog (MemoryBus, PamsRecorder are p=3 utility worms)
- `azazael-worms-core` — orchestration + utility + diagnostic worms

## G:\ Drive Archive
```
G:\AZAZAEL\
├── CODEX_VIDEOS\          # 14 superseded video scripts
└── frames\                # Test frame output directory
```
