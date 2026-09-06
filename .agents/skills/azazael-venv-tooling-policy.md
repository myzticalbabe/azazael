---
name: azazael-venv-tooling-policy
description: Dual-venv tooling policy for the Azazael ecosystem — Python 3.14t
  stays the default production stack, while `venv-313-tools/` is the deliberate,
  documented fallback for tools with no cp314t wheel. Lists the verified
  wheel-gap tools, their versions, install target, and the smoke-test pattern
  that proved each one. Proven 2026-09-05; consult before installing any new
  native package on a 3.14t venv.
metadata:
  category: process
---

# azazael-venv-tooling-policy

## Why this exists
Several bleeding-edge data tools ship **sdist-only** (source builds) for Python
3.14/3.14t — there is no `cp314`/`cp314t` wheel. Attempting `pip install` on a
3.14t venv either hangs (sdist compile of e.g. igraph/duckdb) or installs a
package that **segfaults on import** (chromadb, sentence-transformers, and
tornado 6.5.5 on cp314t). This policy prevents wasted hours and documents the
working fallback.

## The policy
1. **3.14t stays the default production stack.** Never abandon it for a tool.
2. **Use 3.13 only when necessary** — i.e., a tool the task genuinely needs has
   no cp314t wheel. Install it into the dedicated fallback venv:
   `C:/Users/clint/venv-313-tools/` (created from Python 3.13.13,
   `AppData/Local/Programs/Python/Python313/python.exe -m venv venv-313-tools`).
3. **Never** attempt an sdist build to force a cp314t install (hangs for
   minutes+); check wheels first or just use the 3.13 venv.
4. **Smoke-test with a real operation**, not just `import`, before declaring a
   tool usable. Record the verification in the session milestone.
5. Run cross-venv scripts with the venv's own interpreter, e.g.
   `PYTHONIOENCODING=utf-8 venv-313-tools/Scripts/python.exe script.py`
   (set PYTHONIOENCODING=utf-8 on Windows or non-ASCII prints raise).

## Verified wheel-gap tool table (2026-09-05)
| Tool | Version | Venv | Verified with |
|------|---------|------|---------------|
| splink | 4.0.17 | venv-313-tools | Full predict path — top matches = true duplicates |
| duckdb | 1.5.5 | venv-313-tools | splink backend (sdist-only on cp314t) |
| igraph | 1.0.0 | venv-313-tools | graph ops |
| kuzu | 0.11.3 | venv-313-tools | embedded DB + get_as_networkx bridge |
| rustworkx | 0.18.1 | venv-313-tools | k-core / pagerank / SSSP benchmark |
| chromadb | 1.5.9 | venv-313-tools | persistent collection add/query (segfaults on cp314t) |
| pyarrow / scipy | latest | venv-313-tools | kuzu result reads / networkx pagerank |
| graphiti-core | 0.30.1 | both | 3.13: full engine + kuzu backend; 3.14t: needs tornado 6.5.8 |
| torch / timesfm | 2.14 / 3.0.1 | venv-314t | TimesFM anomaly pilot (3.14t-native, do NOT move) |

## API gotchas learned (write these down, they cost an hour each)
- **kuzu 0.11.3 python**: `execute()` params are **dicts** with `$name`
  placeholders (lists rejected). Database path is a **file-style** path it
  manages (`~/foo.db`), never a pre-made directory. Read rows with
  `has_next()/get_next()`; `get_as_arrow()` needs pyarrow.
- **rustworkx 0.18**: `pagerank` requires a `PyDiGraph` (make bidirectional);
  `dijkstra_shortest_path_lengths` requires positional `edge_cost_fn`.
- **splink 4.0**: imports live in `splink.backends.duckdb.DuckDBAPI`,
  `splink.comparison_level_library`, `splink.comparison_library`; EM training
  lives under `linker.training`; predict returns a `DuckDBDataFrame` →
  materialize with `.as_pandas_dataframe()`. Set an explicit `probability`
  prior or absolute match scores stay tiny.
- **chromadb**: default embedder downloads all-MiniLM-L6-v2 ONNX on first use
  (~2 min); fine on 3.13.
- **graphiti-core on 3.14t**: reinstall tornado (`pip install -U --force
  tornado`) to fix the import segfault. Full engine needs an embedder/LLM
  client; use a NoopEmbedder stub for persistence validation. The bundled kuzu
  driver is deprecated upstream (graphiti recommends Neo4j/FalkorDB).

## When to prefer 3.14t anyway
Pure-Python work (sklearn TF-IDF, RapidFuzz, pyvis, graphiti in-memory model,
pandas) and the torch/timesfm stack run best on 3.14t. Only hand off the
specific native tool to venv-313-tools; keep the orchestration script on the
3.14t side when possible.
