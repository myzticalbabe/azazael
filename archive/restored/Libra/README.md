# Libra — High-Performance Legal Automation Engine

**Pro Se Litigation Framework for Pennsylvania Commonwealth & United States Federal Courts**

Libra combines ALL functionally working aspects of the **Tigger** high-performance native engine into a unified legal automation platform for Pro Se litigants. Built for maximal concurrent filings across federal and state courts.

---

## Overview

Libra is a Python-based legal automation engine that leverages Tigger's proven high-performance architecture:

- **Native Filing Registry** (Rust pyo3 extension) — O(1) lookups for 20+ filing types
- **Concurrent Filing Engine** — asyncio-powered parallel filing across multiple courts
- **Court Rules Engine** — PA Commonwealth & US Federal Court rules database
- **Document Generator** — court-compliant legal document generation with proper captions
- **Litigation Orchestrator** — maximal mandamus, discovery, and deposition campaigns
- **CLI Interface** — full command-line control for all operations
- **Thread-Safe** — Python 3.14t free-threaded ready
- **Graceful Fallback** — pure Python when native extension unavailable

## Quick Start

```bash
cd Desktop/Libra
pip install -e .

# Show ecosystem info
libra info

# View filing registry statistics
libra stats

# Search for filing types
libra search mandamus

# Look up court information
libra court ed_pa

# Generate a complaint template
libra template COMPLAINT_CIVIL

# Run performance benchmarks
libra bench
```

## Commands

| Command | Description |
|---------|-------------|
| `libra stats` | Filing registry statistics |
| `libra search <query>` | Search filing types |
| `libra template <type>` | Generate legal document |
| `libra court <id>` | Look up court information |
| `libra docket <action>` | Manage case docket |
| `libra bench` | Run performance benchmarks |
| `libra info` | Show ecosystem overview |

## Court Coverage

### Federal Courts
- **Third Circuit Court of Appeals** (3d Cir.)
- **Eastern District of Pennsylvania** (E.D. Pa.) — Philadelphia, Allentown, Reading
- **Middle District of Pennsylvania** (M.D. Pa.) — Scranton, Harrisburg, Williamsport
- **Western District of Pennsylvania** (W.D. Pa.) — Pittsburgh, Erie, Johnstown

### Pennsylvania Commonwealth Courts
- **Supreme Court of Pennsylvania** (Pa.)
- **Superior Court of Pennsylvania** (Pa. Super.)
- **Commonwealth Court of Pennsylvania** (Pa. Cmwlth.)
- **Court of Common Pleas** (C.P.) — all 60 judicial districts

## Filing Types

| Category | Types |
|----------|-------|
| **Mandamus** | Federal Mandamus (28 U.S.C. § 1361), PA Mandamus (42 Pa.C.S. § 761) |
| **Discovery** | Interrogatories, RFPs, RFAs, Deposition Notices, Subpoenas |
| **Motions** | Summary Judgment, Compel Discovery, TRO, Preliminary Injunction, Extension, Reconsideration |
| **Appeals** | Notice of Appeal, Appellant's Brief |
| **Habeas** | Habeas Corpus Petition (§ 2241, 2254, 2255) |
| **Administrative** | Certificate of Service, Civil Cover Sheet JS-44 |
| **IFP** | Federal IFP (28 U.S.C. § 1915), PA IFP (Pa.R.C.P. 240) |

## Architecture

```
Libra/
├── libra/
│   ├── __init__.py              # Package init, filing registry, auto-discovery
│   ├── cli.py                   # CLI interface (7 commands)
│   ├── filing_registry.py       # O(1) filing type registry with indexes
│   ├── court_rules.py           # Court rules engine & Pro Se guidelines
│   ├── document_generator.py    # Legal document generation with captions
│   ├── concurrent_filer.py      # Async concurrent filing engine
│   └── litigation.py            # Core litigation orchestrator
├── data/
│   ├── filing_types.json        # 20 filing types across 9 categories
│   ├── pa_courts.json           # PA Commonwealth court data
│   ├── federal_courts.json      # US Federal Court data (PA districts)
│   └── templates/               # Document templates (future)
├── native/
│   └── filing_manifest/         # Rust pyo3 extension (from Tigger)
│       ├── Cargo.toml
│       └── src/lib.rs
├── tests/
├── docs/
├── pyproject.toml
└── README.md
```

## Performance

Built on Tigger's native engine, Libra achieves:

- **Cold-start discovery**: ~5 ms (vs ~1.2s pure Python)
- **Single filing lookup**: ~1 µs (O(1) HashMap)
- **Category filtering**: instantaneous (pre-built indexes)
- **Search**: sub-millisecond (case-insensitive HashMap scan)
- **Concurrent filing**: 10+ filings processed in parallel

## Pro Se Resources

- Federal Pro Se Guide: https://www.uscourts.gov/pro-se
- PACER: https://pacer.uscourts.gov (1-800-676-6856)
- PA Pro Se Guide: https://www.pacourts.us/learn/representing-yourself
- PA Legal Aid Network: 1-800-322-7572
- Federal Rules: https://www.law.cornell.edu/rules/frcp

## Requirements

- Python >= 3.12
- Optional: Rust 1.95+ (for native filing_manifest extension)
- Optional: Maturin (for building the Rust wheel)

## License

MIT License — Created 2026

---

*Built on Tigger's high-performance architecture. Libra est iustitia.*
