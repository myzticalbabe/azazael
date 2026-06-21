# AZAZAEL Full Wiring — Next Steps & TODO

**Technical Roadmap — Complete Ecosystem Wiring**  
**Python 3.14.5t Free-Threading | Windows 11 + WSL2 Ubuntu 26.04 snapshot 4**  
**Generated: 2026-05-28 | Based on: PAMS insights #15-#33, codebase deep scan, config audit**

---

## Executive Summary

This document synthesizes **33 PAMS insights**, a **complete codebase scan** (250+ files), **config.yaml audit**, and the **thinker-with-files-gemini deep analysis** into a single prioritized, executable wiring roadmap.

### Why This Matters

AZAZAEL is documented as a free-threading multi-agent ecosystem but the codebase reality diverges significantly:

| What is Documented | Reality | Severity |
|---|---|---|
| FreeThreadedAgent base class | **Does not exist** (0 matches in codebase) | CRITICAL |
| MemoryBus inter-agent comms | **Does not exist** (0 matches) | CRITICAL |
| AgentPool with PAMS wiring | Uses raw ThreadPoolExecutor everywhere | CRITICAL |
| Single IS_FREE_THREADED | Defined inline in **4+ files** (PAMS insight #26) | HIGH |
| freethread_utils.py shared lib | Only in llama-server/unified/, hardcodes True | HIGH |
| All agents log to PAMS | **Only 2 callers** of PamsRecorder total (#28) | HIGH |
| config.yaml free-threading path | Points to **wrong executable** (/Roaming/uv/...) | MEDIUM |
