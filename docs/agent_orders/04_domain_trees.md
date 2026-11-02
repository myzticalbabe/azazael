## DOMAIN TREES — add a domain by declaration, never by forking the renderer

**Standing order, 2026-10-31.** The per-environment atlas answers "what is in this
directory". Domain questions are not directory questions: the RULES layer is half
code and half canon, GOSP is three scripts plus evidence dirs, edge0 lives outside
the repo. So a domain is a **declaration** in `azazael/tools/domain_trees.py`
(`DOMAINS`), and the census reads only what that declaration names.

```bash
python azazael/tools/domain_trees.py --list              # declared domains
python azazael/tools/domain_trees.py --check             # table: totals per domain
python azazael/tools/domain_trees.py --domain sentinel   # one atlas
python azazael/tools/domain_trees.py                     # all + forest_manifest.json
```

Output goes to `~/yggdrasil_forest/`: one `domain_atlas_<domain>.json` per domain
plus `forest_manifest.json`, which holds one **render descriptor** per domain.

**The interop contract is the atlas schema.** A domain atlas has the same keys as
an environment atlas (`trees`, `classes`, `worms`, `edges`, `totals`), so
`yggdrasil_forest/render_tree.py --descriptor <descriptor.json>` draws any domain
with **no code change**. Verified 2026-10-31: the sentinel descriptor rendered
300/300 frames, 0 misses. A new domain is a new declaration plus a descriptor; if
you find yourself editing the renderer to draw a domain, you have taken the wrong
route.

**Declared domains (measured, 2026-10-31):**

| domain | trees | modules | lines | classes | worms | rules |
| --- | --- | --- | --- | --- | --- | --- |
| sentinel (rules dev) | 12 | 50 | 39 600 | 42 | 0 | 66 |
| cain | 8 | 94 | 37 635 | 43 | 0 | 0 |
| eve_rani | 2 | 22 | 5 936 | 55 | 0 | 0 |
| hives (swarm) | 2 | 151 | 74 752 | 417 | 206 | 0 |
| gosp | 5 | 3 | 357 | 1 | 0 | 0 |
| ml (shards/modules) | 2 | 50 | 17 470 | 104 | 0 | 0 |
| shards (repository) | 2 | 4 | 1 125 | 0 | 0 | 0 |
| edge0 | 5 | 161 | 30 802 | 142 | 0 | 0 |

**What the numbers do not mean — read before quoting them:**

- `cross_root_edges_resolved: false` in every atlas. Each declared root is scanned
  on its own, so `edges.tree_pairs` is the **sum of per-root values** and
  undercounts coupling between roots of one domain. Do not quote a domain's edge
  count as its coupling.
- **A flat root is one limb.** `src/SHARDS` and `src/ML` hold files directly with
  no package dirs; before the fix they scanned as zero trees and the shard
  repository rendered empty while holding real code.
- **Canon limbs report `kind: "canon"` with `rules` and `lines`, and 0 classes by
  design.** "0 cls" on `MANDATES` is not an empty file — it is text, and its size
  is 66 rules.
- **A skill is a directory holding `SKILL.md`, not a `*.md` file.** `.agents/skills`
  is 204 shard dirs + 37 loose md; counting markdown alone read the repository as
  37 items.
- `classes.total` can exceed the sum shown across limbs when a root carries classes
  in subpackages that never became top-level trees. Both numbers are real; they
  answer different questions.

**Separate clips, per environment and per domain.** An environment forest
(`YGGDRASIL_FOREST_<ENV>.mp4`) and a domain tree (`render_tree.py` with a domain
descriptor) are different deliverables and must not be merged into one clip that
implies a domain figure was measured on one environment. If a domain tree is
rendered from a different environment's tree, the descriptor's `atlas` field must
say which — the atlas path is the provenance.
