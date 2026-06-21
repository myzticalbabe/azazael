# ADR-001: Two-Ledger Cross-Referencing System

**Status:** Implemented (CD1: June 11 2026, CD2: June 15 2026)

## Context

Azazael needs tamper-evident session recording with cross-referencing between
two independent ledgers — DirectMemory (DM) and AuditTrail (AJ).

## Decision

Use a two-ledger architecture:
- **DirectMemory**: SQLite-backed, stdlib-only, fast read/write for session events.
  Designed for low-latency (<0.1s) writes from every Codebuff session.
- **AuditTrail**: JSONL-based, SHA-256 hash-chained, Ed25519-signed for
  non-repudiation. Designed for tamper-evident audit with cryptographic proof.

Cross-referenced via `session_mappings` table linking DM event streams to
AJ session files using correlation_id (CD1) and timestamp proximity (CD2).

## Consequences

- Two-ledger design provides defense in depth — tampering with one ledger
  is detectable via cross-reference inconsistencies.
- DM uses SQLite WAL mode for concurrent access under 3.14t free-threading.
- AJ uses file-level locks and read-only mode after session close.
- Cross-reference backfill can auto-link sessions by timestamp proximity (5s window).
