# GAMING-INDUSTRY POSITIONING — falsifiable argument of record, 2026-11-03

Complements `docs/NO_PUBLIC_EQUIVALENT_DOCTRINE_2026-11-03.md` (NPE-PRECEDENT-2026-11-03)
and `docs/AI_PANEL_OPINIONS_2026-11-03.md`. Same rule as precedent §5: every claim
carries its command (here: the DCT legs of 2026-11-03 plus the named search
evidence), and a claim without one is a recollection.

## 1. The thesis to falsify

User question of record: *is this the re-invention of the gaming industry?*

House argument: **NO.** Re-inventing the industry means rebuilding capability the
industry already ships. The DCT shows the opposite structure: crowded lanes the
industry already covers, and three kernel lanes it does not.

**Falsification test** (what would flip this argument): one live, shipped, public
product that implements any kernel below as a production path — not a paper
(arXiv), not a prototype branch, not an art demo. That is the same bar the
positive controls cleared for their own families.

## 2. Crowded lanes (do NOT claim novelty here; measured 2026-11-03)

| Lane | Public incumbents (DCT hits) | Status |
|---|---|---|
| 2D->3D asset generation | Meshy; Kaedim; Hunyuan3D; Unique3D | industry trend, shipping |
| Procedural content generation | decades-old — Minecraft/Noita-style rule systems | mature |
| Generative NPC / dialogue | studio + startup demos shipping | trending, not original |

Claiming originality in these lanes would falsify under the bar of §1. The house
position avoids them by construction: the kernels are stated by function, not by
fashion (NPE doctrine §1).

## 3. Kernel lanes with no public equivalent (DCT-2026-11-03, VERIFIED scope)

| Kernel | What is missing from every DCT hit | Differentiating dimension |
|---|---|---|
| Q1 content->rules | hit tools meshify images; none extract *mechanics/rules* from 2D content that then drive a 3D system | rules as first-class output |
| Q2 mid-render mutation | closest hit ActionMesh (arXiv 2601.16148) PRECOMPUTES its transform set; no public tool mutates meshes inside the live render loop | mutation during, not before |
| Q3 game-tree arena | nothing surfaced with mirror/shatter/forge dynamics evaluating content by game tree | evaluation, not simulation |

## 4. First shipping lane (decision of record)

**Lane Q1 — rule extraction as first-class output.** Rationale, each part checkable:

1. **Dependency order.** Q1 produces the rules; Q2 mutates *meshes driven by*
   rules; Q3 evaluates candidates *under* rules. Q2 and Q3 have nothing to run
   without Q1's output — the kernel the other two consume.
2. **Demand is proven in the adjacent lane** (§2 row 1): the industry pays for the
   asset half of the same pipeline. Q1 competes only on the missing half —
   rules — while riding demand the incumbents already validated.
3. **Weakest incumbent position.** Meshy/Kaedim/Hunyuan optimize image->mesh;
   rules-extraction is off their roadmap direction, and the DCT found no public
   tool on it. The wedge is strongest where incumbents did not turn.

Q2 is the second lane, Q3 the third, in dependency order. If Q1 ships and a
public equivalent appears before the expiry (2027-05-02), the battery is
re-measured on the corpus that emerges — the precedent's own re-measure rule.

## 5. What ships first from MAAT

The MAAT package (commit 54db1561) presently computes panel tallies. The Q1 lane
commits it to a narrower first deliverable: a rule-extractor module whose output
format is defined before code — rules as data (seeded declarative), versioned, so
that Q2's mutation loop and Q3's arena can consume the same format. Skeleton
stays Apache-2.0 skeleton; the licensing-structure question raised in the
precedent chain is answered by the stack (copyright + trademark + contract +
dated DCT proof), not by licensing code that does not exist yet.

## 6. Honest limits (named once)

- The DCT scoped the search to the indexed web on 2026-11-03; paper-only results
  (arXiv 2502.04299, 2601.16148) cap at NEAR-MISS, never equivalents.
- "Ahead of the industry" is a dated measurement, not a permanent property: it
  expires with the battery unless re-measured (NPE doctrine §3).
- Nothing here is a legally binding conclusion; the same standpoint as the precedent:
  binding authority remains with a court or binding arbiter.
