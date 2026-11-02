# Hardware Requirements — Project FLAMING_SWORD

## Reference Platform (Development & Validation)

This project was **developed and validated exclusively on:**

| Component | Specification |
|-----------|---------------|
| **CPU** | Intel Core Ultra 9 285H (16 cores, 22 threads) |
| **iGPU** | Intel Arc 140T (8 GB shared VRAM) |
| **RAM** | 32 GB LPDDR5x-8533 (dual channel) |
| **OS** | Windows 11 Pro 24H2 (build 26100) |
| **Python** | 3.14.7 (free-threaded) / 3.15.0rc3 (free-threaded) |
| **Git** | 2.47+ (for sweep land step) |

## Component Architecture

```
FLAMING_SWORD (sword.py)     → sweeps codebase: find → queue → fix → prove → land
defender.py                  → prompt → frame with acceptance/evidence/defends
sentinel.py                  → REAPER: refuses frames with unresolved claims
memory_bridge.py             → GRIMOIRE: writes/reads lessons from failures
chain_server.py              → HTTP endpoint (OpenAI-compatible /ask)
```

## Performance Baseline (This Hardware)

| Operation | Metric | Notes |
|-----------|--------|-------|
| `python sword.py --selftest` | < 2s | 13 assertions, 98 passed |
| `python defender.py --intent "..." --target tools/sword.py` | < 1s | Frame generation |
| `python sentinel.py --claim "..."` | < 0.5s | Claim resolution |
| `python chain_server.py --model-url ...` | — | Requires external model server |

## CARPE DIEMIC CREATIVE LICENCE {CDCL}

> **Developers have a Carpe Diem Creative Licence {CDCL} to freely modify this code for their interests.**

### What You Can Modify Freely

- **Frame schema** (`defender.py`): Add/remove fields for your workflow
- **Claim vocabulary** (`sentinel.py`): Define what "resolved" means for your project
- **Lesson format** (`memory_bridge.py`): Adapt the JSONL structure
- **HTTP contract** (`chain_server.py`): Extend `/ask` or add endpoints
- **Sweep policy** (`sword.py`): Change queue ordering, acceptance criteria

### What Requires Calibration

- **Git operations**: `sword.py` land step needs `git` on PATH; on non-Windows, adjust `creationflags`
- **Model server**: `chain_server.py` expects OpenAI-compatible `/v1`; test with your provider
- **State directory**: All tools write to `cwd/state/`; ensure writable

### Self-Test as Calibration

```bash
python tools/sword.py --selftest
# Should print: "SELFTEST 13/13 passed"
```

If it fails, the failure tells you what assumption broke on your hardware.

## Porting to Other Platforms

| Platform | Changes Needed |
|----------|----------------|
| Linux/macOS | Remove `CREATE_NO_WINDOW`, `CREATE_NEW_PROCESS_GROUP` from subprocess calls |
| No Git | Disable `--land` in sweep; use `--dry-run` |
| Different Python | 3.10+ works; free-threaded (3.14t/3.15t) enables true parallelism in `sword.py` |

## License

Apache-2.0 — see `LICENSE` and `NOTICE`.

---

*Generated 2026-11-02. Your hardware will differ — that's the point of {CDCL}.*