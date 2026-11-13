# KNOBS AUDIT — 2026-11-07

## Premise
"We use retro-fitted paradigms instead of creating to fit new realities."
Every hardcoded paradigm choice MUST have a knob. A paradigm without a knob is a fossil.

---

## 1. CURRENT DECLARED KNOBS (36 leaves in defaults.json)

| Section | Knob | Type | Current | Notes |
|---------|------|------|---------|-------|
| `ast_audit` | enabled | bool | true | |
| `golden_arrow` | enabled, strict, timeout_s, workers | bool/bool/int/int | true/false/360/6 | |
| `deep_dive` | enabled, forensics, web_search, web_timeout_s, max_queries | bool/bool/bool/int/int | true/true/true/20/3 | |
| `fallback` | on_error, record | str/str | record-and-continue/logs/deep_dive.json | |
| `preflight` | disk_floor_gb | float | 2.0 | |
| `retention` | composite_eviction | bool | false | |
| `hyper_edge` | reading_audit, settings_shadow, leg_ledger, head_audit, truncation, ctypes_restype, claim_agreement, agreement_floor, agreement_rung_floor, kernel, kernel_timeout_s, strict, leg_timeout_s | 13 bools/floats/ints | various | |
| `reading_audit` | min_coverage | float | 0.0 | |
| `head_audit` | max_state_age_days | int | 0 | |
| `settings_shadow` | readers | list[str] | ["read_default","setting","get_default"] | |
| `arena` | endpoint, quote_chars, max_tokens, workers, quorum, timeout_s | str/int/int/int/float/int | various | |

**Total: 36 leaf knobs**

---

## 2. HARDCODED PARADIGMS NEEDING KNOBS (The "New Reality")

### 2.1 Runtime / Interpreter Paradigm
**Current**: Hardcoded to py316t in session_start, gate, tools
**Needed knobs**:
```json
"runtime": {
  "interpreter": "py316t",           // py316t | py315t | py314t | auto
  "gil_sidecar": true,               // use GIL wrapper for incompatible pkgs
  "freethreaded_required": true,     // fail if not freethreaded
  "venv_path": "C:/Azazael/.venvs/py316t",
  "python_exe": "C:/Azazael/.venvs/py316t/Scripts/python.exe"
}
```

### 2.2 MCP Stack Topology
**Current**: Hardcoded ports (8765 daemon, 8766 floor), floor proxy mandatory
**Needed knobs**:
```json
"mcp_stack": {
  "daemon_port": 8765,
  "floor_port": 8766,
  "floor_enabled": true,
  "floor_upstream_wait_s": 30,
  "floor_origin": "logon",           // logon | pams | manual
  "lanes_route_through_floor": true
}
```

### 2.3 Training / Evolution Paradigm (E2R-1..E2R-9)
**Current**: Hardcoded in trainer.py, CLI defaults
**Needed knobs**:
```json
"evolution": {
  "mode": "live",                    // live | simulated | hybrid
  "population_size": 8,
  "generations": 20,
  "convergence_eps": 0.005,
  "convergence_window": 3,
  "lillith_enabled": true,
  "lillith_warmup_gens": 3,
  "lillith_stall_eps": 0.001,
  "adversary_saturation": true,      // E2R-6: saturate adversary not population
  "dream_hit_target": 0.95,
  "inheritance_mode": "persist",     // persist | reseed
  "parser_autopatch": false          // E2R-8: never auto-patch parsers
}
```

### 2.4 Verification / Proof Standards (Flock Canon)
**Current**: Hardcoded tier thresholds (A/B/C/D), flock assignments
**Needed knobs**:
```json
"verification": {
  "tier_thresholds": {
    "A_primary": "raw+sha+quote+identity",
    "B_index": "identity+universe",
    "C_secondary": "paired_with_A_or_B",
    "D_snippet": "lead_only"
  },
  "flock_assignments": "auto",       // auto | manual | mixed
  "universe_label_required": true,
  "negative_proof_standard": "universe_free=CUT",
  "fetch_log_mode": "append_only"    // never overwrite
}
```

### 2.5 Web / Fetch Provider Chain
**Current**: Hardcoded chain (StackExchange -> DuckDuckGo -> curl_cffi -> playwright)
**Needed knobs**:
```json
"fetch": {
  "provider_chain": ["stackexchange", "duckduckgo", "curl_cffi", "playwright"],
  "curl_cffi_impersonation": "chrome120",
  "playwright_headless": true,
  "archive_replay": true,
  "js_challenge_handling": true,
  "timeout_s": 30,
  "max_redirects": 5
}
```

### 2.6 GPU / Compute Backend
**Current**: Hardcoded to CPU/XPU detection in onnx_integration
**Needed knobs**:
```json
"compute": {
  "backend_priority": ["xpu", "cuda", "cpu"],
  "torch_build_from_source": false,
  "ipex_enabled": false,
  "level_zero_enabled": false,
  "xpu_device_id": 0,
  "memory_fraction": 0.9
}
```

### 2.6 WSL / Remote Environment Integration
**Current**: Hardcoded WSL probes, 9P bridge warnings
**Needed knobs**:
```json
"wsl": {
  "enabled": true,
  "distro": "Ubuntu-26.04",
  "kali_distro": "kali-linux",
  "bridge_mode": "local",            // local | 9p | ssh
  "sync_method": "robocopy",         // robocopy | rsync | git
  "probe_timeout_s": 10,
  "graph_build_local_only": true
}
```

### 2.7 Memory / Persistence Strategy
**Current**: Three stores (PMB, Engram, PAMS) with different protocols
**Needed knobs**:
```json
"memory": {
  "primary": "pmb",                  // pmb | engram | pams
  "pmb_workspace": "personal",
  "pmb_recall_floor": 0.70,
  "pmb_recall_min_best": 0.89,
  "engram_project": "azazael",
  "engram_all_projects": true,
  "pams_enabled": true,
  "pams_user_id": "clint",
  "pams_model_id": "mcp-client"
}
```

### 2.8 Gate Strictness Modes
**Current**: Mixed advisory/blocking, some tools ignore
**Needed knobs**:
```json
"gates": {
  "mcp_startup": "blocking",         // blocking | advisory
  "evidence_gate": "blocking",
  "hyper_edge": "advisory",          // strict=false in config
  "commit_hook": "blocking",
  "settings_shadow": "advisory",
  "reading_audit": "advisory",
  "head_audit": "advisory",
  "leg_ledger": "advisory"
}
```

### 2.9 Agent / Lane Coordination
**Current**: Board-based, hardcoded lane names, push_hook semantics
**Needed knobs**:
```json
"coordination": {
  "board_enabled": true,
  "valid_lanes": ["kilo", "freebuff", "opencode"],
  "claim_lease_seconds": 1800,
  "max_claim_limit": 10,
  "push_hook_enabled": true,
  "dispatch_non_reasoning": true     // push mechanical work to owning lane
}
```

### 2.10 Rendering / Visualization
**Current**: Hardcoded Chrome/Puppeteer, frame index from URL
**Needed knobs**:
```json
"render": {
  "engine": "chrome",                // chrome | firefox | puppeteer
  "frame_index_source": "url",       // url | clock | manual
  "chrome_profile_per_frame": true,
  "absolute_output_paths": true,
  "verify_frame_count": true,
  "verify_hashes": 3,
  "output_format": "mp4"
}
```

---

## 3. GAPS IN CURRENT DEFAULTS_PROFILE

The `DEFAULTS` dict in `defaults_profile.py` (lines 115-170) is missing ALL sections from 2.1-2.10 above.

### 3.1 Immediate Action Required
Add these sections to `DEFAULTS` and `config/defaults.json`:

```json
{
  "runtime": { ... },
  "mcp_stack": { ... },
  "evolution": { ... },
  "verification": { ... },
  "fetch": { ... },
  "compute": { ... },
  "wsl": { ... },
  "memory": { ... },
  "gates": { ... },
  "coordination": { ... },
  "render": { ... }
}
```

### 3.2 Environment Overlays
Create `config/defaults.windows.json`, `config/defaults.wsl.json`, `config/defaults.kali.json` for per-environment tuning.

### 3.3 Validation
Run `python tools/defaults_profile.py --check` after additions — must validate shapes and bounds for all new knobs.

---

## 4. AUDIT CHECKLIST

| Category | Declared | Used in Code | Missing Knob | Priority |
|----------|----------|--------------|--------------|----------|
| Runtime | 0 | 15+ | runtime.* | CRITICAL |
| MCP Stack | 2 (ports) | 8+ | mcp_stack.* | CRITICAL |
| Evolution | 4 (hyper_edge) | 20+ | evolution.* | HIGH |
| Verification | 0 | 12+ | verification.* | HIGH |
| Fetch | 0 | 10+ | fetch.* | HIGH |
| Compute | 0 | 6+ | compute.* | MEDIUM |
| WSL | 0 | 5+ | wsl.* | MEDIUM |
| Memory | 3 (pmb) | 8+ | memory.* | MEDIUM |
| Gates | 2 (strict) | 10+ | gates.* | MEDIUM |
| Coordination | 1 (lease) | 6+ | coordination.* | LOW |
| Render | 0 | 4+ | render.* | LOW |

**Total estimated new knobs: ~80-100 leaves**

---

## 5. IMPLEMENTATION ORDER

1. **Phase 1 (this session)**: `runtime`, `mcp_stack`, `memory` — unblock current work
2. **Phase 2 (next)**: `evolution`, `gates`, `coordination` — control paradigm selection
3. **Phase 3**: `verification`, `fetch`, `compute`, `wsl` — external integrations
4. **Phase 4**: `render` — visualization pipeline

---

## 6. VERIFICATION COMMAND

```bash
python C:/Azazael/azazael/tools/defaults_profile.py --show
# Must show all new sections with their knobs

python C:/Azazael/azazael/tools/defaults_profile.py --check
# Must exit 0 (valid shapes/bounds)

python C:/Azazael/azazael/tools/settings_shadow.py
# Must show 0 orphan_knob, 0 bypass_reader, 0 fallback_drift
```

---

## 7. DECLARATION

**Every hardcoded value in this tree that represents a paradigm choice is a defect.**
This audit is the minimum set to make the "new reality" configurable.
No new code should introduce a paradigm without its knob.