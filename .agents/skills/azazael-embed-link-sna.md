---
name: azazael-embed-link-sna
description: Lead-layer network analysis over the investigation corpus — real
  embeddings (chromadb all-MiniLM) vs TF-IDF to isolate the 211 embedding-only
  implied connections, SNA hubs (degree + PageRank via rustworkx), the pyvis
  lead viewer, and the hubs-vs-gap-anchor cross-check. Proven 2026-09-05; run
  after any corpus doc set changes.
metadata:
  category: process
---

# azazael-embed-link-sna

## Purpose
Exact grep and TF-IDF both miss semantically-implied document links (different
words, same relationship). This pattern surfaces the connections only real
embeddings find, ranks the docs that generate the most leads, and anchors them
to INVESTIGATION_GAPS numbers so the lead layer is queryable.

## Pipeline (venv-313-tools — chromadb/sklearn are cp314t-blocked)
1. **Index**: `bcc_chroma_index.py` — persistent chromadb collection over root
   corpus docs (96 docs / 568 chunks, default all-MiniLM-L6-v2; first run
   downloads the model ~2 min).
2. **Diff**: `bcc_embed_tfidf_diff.py` — top-3 other-doc neighbors per doc from
   embeddings vs TF-IDF cosine; pairs found by both, embeddings-only (the new
   leads), and TF-IDF-only. Sep-5 result: 62 both / **211 embeddings-only** /
   226 TF-IDF-only.
3. **SNA**: `bcc_embed_link_sna.py` — undirected graph of the embedding-only
   pairs; hubs by degree AND rustworkx PageRank (PyDiGraph required). Sep-5:
   386 edges, one 90-doc cohesive component, k-core 7; hubs =
   EXPANDED_EVIDENCE, AUDIT_REPORT, LEGAL_OVERSIGHT_ANGLE,
   HARM_EVIDENCE_MASTER, RECUSAL_EVIDENCE.
4. **Viewer**: pyvis HTML (`BCC_EMBED_LINK_VIEWER.html`, hubs orange) — always
   prepend `<!DOCTYPE html>`/viewport and re-run the structural audit; verify
   render with `chrome --headless=new --dump-dom file://... | grep -c vis-network`.
5. **Anchor**: `BCC_HUB_GAP_ANCHOR.html` maps each hub to INVESTIGATION_GAPS
   numbers. Gotcha: the gaps doc is narrative — section-walk extraction yields
   few gap→topic pairs (Sep-5: only #2/#24/#43 extractable); hubs anchor to
   those topics by token overlap. Anchor lines inserted into hub docs
   (`<p class="hub-gap-anchor">`) must be re-audited.

## Key gotchas
- rustworkx `pagerank` needs a **PyDiGraph** (make bidirectional); its result is
  a `CentralityMapping` — index by node, don't `.get()`.
- chromadb queries return metadatas/distances lists; dedupe self-doc hits.
- Adding anchor `<p>` lines to corpus HTMLs is safe for the structural audit
  (JS balance unaffected) but re-run `audit_html.py` on every touched doc.

## Related
- `azazael-venv-tooling-policy` (chromadb/rustworkx wheel-gap rules)
- `aoa-artifact-cross-check` (truth-across-surfaces verification pattern)