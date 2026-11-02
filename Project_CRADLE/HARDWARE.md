# Hardware Requirements — Project CRADLE

## Reference Platform (Development & Validation)

This project was **developed and validated exclusively on:**

| Component | Specification |
|-----------|---------------|
| **CPU** | Intel Core Ultra 9 285H (16 cores, 22 threads) |
| **iGPU** | Intel Arc 140T (8 GB shared VRAM) |
| **RAM** | 32 GB LPDDR5x-8533 (dual channel) |
| **OS** | Windows 11 Pro 24H2 (build 26100) |
| **Python** | 3.14.7 (free-threaded) / 3.15.0rc3 (free-threaded) |

## Component Architecture

CRADLE is a **composition launcher** — it vendors or discovers four parts:

| Part | Vendored Path | External Fallback | Role |
|------|---------------|-------------------|------|
| defender | `tools/defender.py` | `../Project_FLAMING_SWORD/tools/defender.py` | Frame generation |
| sentinel | `tools/sentinel.py` | `../Project_FLAMING_SWORD/tools/sentinel.py` | REAPER — claim refusal |
| memory | `tools/memory_bridge.py` | `../Project_FLAMING_SWORD/tools/memory_bridge.py` | GRIMOIRE — lesson storage |
| server | `tools/chain_server.py` | `../Project_FLAMING_SWORD/tools/chain_server.py` | HTTP endpoint |

## CARPE DIEMIC CREATIVE LICENCE {CDCL}

> **Developers have a Carpe Diem Creative Licence {CDCL} to freely modify this code for their interests.**

### What You Can Modify Freely

- **Part discovery** (`_part_path`): Change vendored vs external priority
- **Doctor checks**: Add/remove readiness probes for your environment
- **Demo flow**: The deliberate failure in `demo()` is a teaching tool — change the target
- **GRIMOIRE reader**: `grimoire()` output format is yours to redesign
- **Server passthrough**: `serve()` forwards args to `chain_server.py` — extend as needed

### Standalone vs Composed

| Mode | Description | How to Achieve |
|------|-------------|----------------|
| **Standalone** | CRADLE runs with vendored tools only | Delete `../Project_FLAMING_SWORD` |
| **Composed** | CRADLE uses external FLAMING_SWORD | Keep sibling project; doctor shows "vendored (external)" |

Run `python cradle.py --doctor` to see which mode you're in.

### Self-Test as Calibration

```bash
python cradle.py --doctor
# Should show: READY (standalone): 5 chain part(s) not installed
# Or: READY. next: python cradle.py --demo
```

If `--demo` fails, the failure tells you what assumption broke on your hardware.

## Hardware Dependencies

| Dependency | Why | Porting |
|------------|-----|---------|
| `git` on PATH | `--land` in sword.py | Remove/substitute for non-git VCS |
| Model server (Ollama/OpenAI-compatible) | `--serve` needs `--model-url` | Any OpenAI-compatible `/v1` endpoint |
| Writable `cwd/state/` | GRIMOIRE/frame storage | Ensure permissions |

## Supported Python Versions

| Version | Status | Notes |
|---------|--------|-------|
| 3.10+ | Compatible | `importlib.util`, `dataclasses`, `pathlib` |
| 3.14t | Recommended | Free-threaded; vendored tools benefit |
| 3.15t | Recommended | Current development target |

## License

Apache-2.0 — see `LICENSE` and `NOTICE`.

---

*Generated 2026-11-02. Your composition will differ — that's the point of {CDCL}.*