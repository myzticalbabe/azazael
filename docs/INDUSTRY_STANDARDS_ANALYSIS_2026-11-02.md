# Industry Standards Analysis — 2026-11-02
**Baseline captured at git rev 28911db (2026-11-02 17:55:13)**

---

## Executive Summary

| Standard | Applicability | Current State | Gap Severity |
|----------|---------------|---------------|--------------|
| NIST AI RMF 1.0 | HIGH | Partial — governance exists, measurement weak | HIGH |
| NIST SP 800-218 SSDF | HIGH | Partial — secure dev practices exist, no formal attestation | HIGH |
| ISO/IEC 42001 | MEDIUM | No AI management system | CRITICAL |
| ISO/IEC 25010 | MEDIUM | Quality attributes measured ad-hoc | HIGH |
| SLSA Provenance | HIGH | Level 0 (no provenance) | CRITICAL |
| SPDX/CycloneDX SBOM | HIGH | NONE | CRITICAL |
| OWASP Top 10 for LLM | HIGH | No LLM-specific controls | CRITICAL |
| CISA SSDF | HIGH | Partial overlap with existing gates | HIGH |

**Overall: The tree has strong internal gates but lacks external standard compliance artifacts and formal management systems.**

---

## 1. NIST AI RMF 1.0 (AI Risk Management Framework)

### Core Functions Assessment

| Function | Sub-function | Current State | Evidence |
|----------|--------------|---------------|----------|
| **GOVERN** | AI policies established | PARTIAL | `SYSTEM_INSTRUCTIONS.md` (RULEs 0A-0Z-C), `MANDATES.md` (37 rules) |
| | Accountability structures | PARTIAL | Board claim/lease/retire system; lane isolation |
| | Risk management integration | PARTIAL | Pre-commit gates, preflight_all, supervisor verdict |
| **MAP** | AI system context | NONE | No AI system inventory or context documentation |
| | Risk identification | PARTIAL | `tools/error_resolution.py`, `tools/anti_pattern_gate.py` |
| **MEASURE** | Quantitative metrics | PARTIAL | golden_arrow (6662 tests), basedpyright (53 errors), prose_forensics |
| | Continuous monitoring | PARTIAL | `tools/mcp_startup_gate.py`, `tools/preflight_all.py` |
| **MANAGE** | Risk prioritization | PARTIAL | Board task queue, supervisor verdict |
| | Incident response | PARTIAL | `tools/error_resolution.py` decision tree |

**Gap:** No formal AI system inventory, no risk tolerance criteria, no third-party AI component tracking.

---

## 2. NIST SP 800-218 SSDF (Secure Software Development Framework)

### Practices Assessment

| Practice Group | Practice | Current State | Evidence |
|----------------|----------|---------------|----------|
| **Prepare Organization** | Define security requirements | PARTIAL | `SYSTEM_INSTRUCTIONS.md`, `MANDATES.md`, `SOP.md` |
| | Implement roles/responsibilities | PARTIAL | Lane system (kilo/freebuff/opencode), board ownership |
| | Implement supporting toolchains | PARTIAL | `tools/` (gates, scanners, auditors), basedpyright |
| **Protect Software** | Protect code integrity | STRONG | `git` signed commits not enforced; `staged_scanner_gate` |
| | Protect software integrity | PARTIAL | `staged_scanner_gate.py` (PASS), `anti_pattern_gate.py` (PASS) |
| | Secure build process | WEAK | No SLSA, no reproducible builds, no SBOM |
| **Produce Well-Secured Software** | Design secure software | PARTIAL | `tools/preflight_all.py` gates, `SOP.md` |
| | Review/analyze code | STRONG | `golden_arrow.py` (499 files), `deep_dive.py` |
| | Test software security | PARTIAL | `tests/` (6662 tests), `deep_dive.py` evidence gate |
| **Respond to Vulnerabilities** | Monitor/identify vulnerabilities | WEAK | No CVE monitoring, no dependency scanning |
| | Respond to vulnerabilities | WEAK | No formal process; `tools/error_resolution.py` only |

**Critical Gap:** No SBOM, no dependency vulnerability scanning, no SLSA provenance.

---

## 3. ISO/IEC 42001 (AI Management System)

### Clause Assessment

| Clause | Requirement | Current State | Gap |
|--------|-------------|---------------|-----|
| 4. Context | Understanding organization & AI role | NONE | No AI system scope defined |
| 5. Leadership | AI policy, roles, commitment | PARTIAL | RULEs exist but no formal policy |
| 6. Planning | AI risk assessment, objectives | PARTIAL | `tools/error_resolution.py` only |
| 7. Support | Resources, competence, awareness | WEAK | No AI-specific training/competence |
| 8. Operation | AI risk assessment, treatment | PARTIAL | `tools/error_resolution.py` decision tree |
| 9. Performance | Monitoring, measurement, audit | PARTIAL | Gates + supervisor verdict |
| 10. Improvement | Nonconformity, corrective action | PARTIAL | `tools/error_resolution.py`, anti-pattern ratchet |

**Verdict:** No AI management system exists. Would require formal policy, risk framework, competence matrix, and documented processes.

---

## 4. ISO/IEC 25010 (Quality Model)

### Quality Characteristics Assessment

| Characteristic | Sub-characteristic | Current Measurement | Gap |
|----------------|-------------------|---------------------|-----|
| **Functional Suitability** | Completeness, correctness | `golden_arrow`: 6662 passed / 19 failed | 19 failures = correctness gap |
| **Performance Efficiency** | Time behavior, resource use | `deep_dive` AST audit (9s), `golden_arrow` (525s) | No SLA/SLO defined |
| **Compatibility** | Coexistence, interoperability | MCP servers (8/8 reachable), cross-lane board | No formal compatibility testing |
| **Usability** | Learnability, operability | Lane prompts, board CLI, `docs/` | No usability testing |
| **Reliability** | Maturity, availability, fault tolerance | MCP startup gate (9/9), supervisor (GO) | No MTBF/MTTR metrics |
| **Security** | Confidentiality, integrity, authenticity | Gates, staged scan, anti-pattern | No formal security testing |
| **Maintainability** | Modularity, reusability, analyzability | `tools/ast_audit.py` (3819 files, 0 syntax errors) | 112 bare-except, 2676 orphan modules |
| **Portability** | Adaptability, installability | Python 3.14t/3.15t, cross-env (Win/WSL/Kali) | No container/SBOM for portability |

**Overall:** Strong on functional correctness (via gates), weak on formal quality attributes and SLAs.

---

## 5. SLSA Provenance + SPDX/CycloneDX SBOM

| Level | Requirement | Current State | Gap |
|-------|-------------|---------------|-----|
| **SLSA 1** | Build process documented | NONE | No build provenance |
| **SLSA 2** | Tamper-resistant build | NONE | No provenance |
| **SLSA 3** | Hardened build | NONE | — |
| **SLSA 4** | Reproducible, hermetic | NONE | — |
| **SPDX 2.3** | SBOM exists | NONE | No SBOM file found |
| **CycloneDX** | SBOM exists | NONE | No SBOM file found |
| **Provenance** | Build attestation | NONE | No attestation |

**Critical:** Zero provenance artifacts. No `sbom.json`, `sbom.spdx.json`, `slsa-provenance.intoto.jsonl`, or similar.

---

## 6. OWASP Top 10 for LLM Applications (2023/2025)

| Risk | Current Controls | Gap |
|------|------------------|-----|
| **LLM01: Prompt Injection** | `tools/preflight_all.py` gates, but no prompt sanitization | NO prompt injection detection |
| **LLM02: Insecure Output Handling** | Gates on outputs, but no output validation | NO output validation gate |
| **LLM03: Training Data Poisoning** | No training pipeline in this tree | N/A (no training) |
| **LLM04: Model Denial of Service** | No rate limiting on MCP servers | NO DoS protection |
| **LLM05: Supply Chain Vulnerabilities** | No SBOM, no dependency scanning | CRITICAL |
| **LLM06: Sensitive Information Disclosure** | `.gitignore`, `pams_promote_guard` (bus telemetry) | No secrets scanning in CI |
| **LLM07: Insecure Plugin Design** | MCP server tool validation exists | Partial — `pmb_prepare` validates |
| **LLM08: Excessive Agency** | Lane system isolates agents | Partial — no per-lane budget |
| **LLM09: Overreliance** | Supervisor verdict, gates required | Partial — "acceptance language forbidden" (RULE 0B) |
| **LLM10: Model Theft** | No model deployment in this tree | N/A |

**Critical:** 6/10 risks have no controls.

---

## 7. CISA Secure Software Development Framework (SSDF)

| Practice | Current State | Evidence |
|----------|---------------|----------|
| **PO.1** Define security requirements | PARTIAL | `SYSTEM_INSTRUCTIONS.md`, `MANDATES.md` |
| **PO.2** Implement roles/responsibilities | PARTIAL | Lane system, board ownership |
| **PO.3** Implement supporting toolchains | STRONG | `tools/` gates, basedpyright, `deep_dive` |
| **PO.4** Define security requirements for suppliers | NONE | No supplier management |
| **PS.1** Protect code integrity | PARTIAL | `git` + staged scanner |
| **PS.2** Protect software integrity | PARTIAL | `staged_scanner_gate` (PASS) |
| **PS.3** Secure build process | NONE | No SLSA, no reproducible builds |
| **PW.1** Design secure software | PARTIAL | Preflight gates, SOP |
| **PW.2** Review/analyze code | STRONG | `golden_arrow`, `deep_dive` |
| **PW.3** Test software security | PARTIAL | 6662 tests, evidence gate |
| **RV.1** Monitor/identify vulnerabilities | NONE | No dependency scanning |
| **RV.2** Respond to vulnerabilities | NONE | No process |

**Overall:** Strong on code review/testing (PW.2), weak on supply chain (PO.4, PS.3, RV.1, RV.2).

---

## 8. Baseline vs. Target Delta

| Metric | Baseline (2026-11-02) | Target (Industry Minimum) | Delta |
|--------|----------------------|---------------------------|-------|
| Test pass rate | 99.7% (6662/6681) | 100% (zero tolerance) | -0.3% |
| Type-check errors | 53 errors | 0 errors | -53 |
| SBOM | NONE | SPDX 2.3 + CycloneDX | MISSING |
| SLSA Level | 0 | Level 1 minimum | MISSING |
| AI System Inventory | NONE | Required (ISO 42001) | MISSING |
| AI Risk Assessment | AD-HOC | Formal (NIST AI RMF) | MISSING |
| LLM Risk Controls | 4/10 covered | 10/10 required | -6 |
| SBOM Generation | NONE | Automated in CI | MISSING |
| Dependency Scanning | NONE | Required (CISA SSDF) | MISSING |
| Security Testing | PARTIAL | Required (OWASP LLM) | PARTIAL |

---

## 9. Recommended Immediate Actions (Priority Order)

1. **Generate SBOM** (CycloneDX + SPDX) — enables all downstream compliance
2. **Implement SLSA Level 1** — build provenance for every artifact
3. **Add dependency vulnerability scanning** — `pip-audit`, `cargo audit`, `npm audit`
4. **Define AI System Inventory** — scope all AI/ML components per ISO 42001
5. **Formal AI Risk Assessment** — apply NIST AI RMF MAP/MEASURE functions
6. **Implement OWASP LLM Top 10 controls** — prompt injection, output validation, supply chain
7. **Add CVE monitoring** — GitHub Dependabot or equivalent
8. **Define quality SLAs** — ISO 25010 attributes with measurable targets
9. **Implement receipt requirement (G2)** — command, exit_code, stdout_sha256 per claim
10. **Add volume budget (D5)** — per-lane write budget enforcement

---

## 10. Evidence Commands (All Reproducible)

```bash
# Test baseline
python C:/Azazael/azazael/tools/golden_arrow.py --status

# Type-check baseline
python C:/Azazael/azazael/tools/type_check_gate.py

# Deep dive forensics
python C:/Azazael/azazael/tools/deep_dive.py --forensics

# MCP stack verification
python C:/Azazael/azazael/tools/mcp_startup_gate.py --fix
python C:/Azazael/azazael/tools/mcp_eight_verify.py --fast

# Guard inventory
cat C:/Azazael/azazael/docs/SUBAGENT_GUARDS_2026-11-02.md

# Supervisor verdict
python C:/Azazael/azazael/tools/supervisor_mcp.py

# Board stats
python C:/Users/clint/_board.py stats freebuff
python C:/Users/clint/_board.py stats kilo
python C:/Users/clint/_board.py stats opencode
```

---

**Report generated:** 2026-11-02 17:55 UTC  
**Baseline file:** `C:/Azazael/azazael/docs/INDUSTRY_STANDARDS_BASELINE_2026-11-02.json`  
**This analysis is the BEFORE snapshot. Re-run after next session to compute delta.**