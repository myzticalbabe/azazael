# Cosmos snapshot 2026-10-28 (MS4)

In-repo versioned copy of the BCC cosmos build outputs, which live (unversioned)
at `C:/Users/clint/BCC_COSMOS/`. If that path is lost or edited, this snapshot
plus `scripts/bcc_cosmos_build.py` reproduces the R5 regen state.

- Source dir: `C:/Users/clint/BCC_COSMOS/` (+ `cosmos/` subdir)
- Build: `python scripts/bcc_cosmos_build.py` (run 2026-10-28, 27 nodes / 68 edges)
- Provenance: `cosmos_manifest.json` (build manifest), `bcc_network_sna_true.json`
  (TRUE_SNA layer), two-sphere HTML renders, graph JS.
- Integrity: `SHA256SUMS` in this dir (bare filenames). Verify with
  `sha256sum -c SHA256SUMS` from this dir.
- Note: graph counts here are cosmos-enumeration; the proof-layer re-derivation
  (G12) is still pending before any count is cited.
