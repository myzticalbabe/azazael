# Funding register — what can actually be qualified for

**Date:** 2026-11-03 (20:19 EST / 2026-11-04 01:19 UTC)
**Subject:** 33 project profiles in `Project_Scribe/profiles/`, 38 distinct funders,
1,155 funder-rows.
**Status:** review complete for the gate question; per-funder verification is
partial and every unverified row is marked. Amounts are the repo's own
`max_amount` strings, not funder-confirmed figures.

---

## 0. The one number that changed the plan

**The NLnet deadline passed 14 hours before this review.**

- Announced cutoff: **3 November 2026, 12:00 noon CET** (= 11:00 UTC = 06:00 EST).
- Measured at review time: 20:19 EST 3 Nov = 01:19 UTC 4 Nov → **14 h past cutoff**.

Board row `NLNET_BATCH_2026-11-03` said "Submit 34 NLnet grant applications before
Nov 3 deadline … Ready for batch submission." Both halves were wrong: the date
had passed, and the profiles were not submittable (see §2). NLnet now runs
odd-month cutoffs; the next one is unverified and must be read off their site
before any new deadline claim is made.

Nothing is lost by this. A cross-join of 33 projects onto 38 funders is the wrong
shape for an application anyway — §1.

---

## 1. What the 1,155 rows actually are

Every profile lists every funder. Measured:

| measure | value |
| --- | --- |
| profiles | 33 |
| distinct funder keys | 38 |
| funder-rows | 1,155 |
| rows that are a distinct (project, funder) *match* justified by scope | not measured — none is documented |
| duplicate key pairs | 3 (`wellcome`/`wellcome_trust`, `google_startups`/`google_startups_ai`, `aws_activate`/`aws_activate_ai`) → ~35 distinct |
| over-cap requests (requested > stated cap) | **0** — the generator does respect caps |
| distinct `equipment_justification` strings | 114 (written per project×funder pair) |

The 0 over-cap result is worth stating plainly: the arithmetic is not the defect.
The defect is that eligibility was never modelled at all, so 1,155 plausible
applications were produced where the honest count is a small number.

---

## 2. Three defects that would have damaged the applications

**(a) Eight referenced artifacts do not exist — in all 33 profiles.**

| reference | missing in |
| --- | --- |
| `pitch_deck` | 33/33 |
| `prototype_video` | 33/33 |
| `proposal` | 33/33 |
| `budget` | 33/33 |
| `timeline` | 33/33 |
| `security_audit` | 3/33 |
| `threat_model` | 3/33 |
| `maintenance_plan` | 3/33 |

A proposal that cites its own budget spreadsheet and that spreadsheet does not
exist is worse than a proposal with no budget.

**(b) Required fields empty in 33/33:** `otherfunding`, `pgp`, `website2`,
`website3`, `website4`, `adoption_metrics`, `budget_breakdown`, `milestones`.
`otherfunding` in particular is a disclosure field — leaving it blank is not a
neutral omission on an application that asks it.

**(c) `entity` is `null` in all 33 profiles.** The JSON carries no entity value,
so the form's entity selector is unset on every submission. The *intent* is
recorded only in board row `NLNET_BATCH_2026-11-03` — "entity=Individual,
organization hidden when Individual, country=US" — which is a note about the
form, not a field the generator fills. This review therefore rests on an
assumption the profiles do not carry: **solo US individual, no registered
entity, no academic affiliation.** The whole eligibility verdict below changes if
that is wrong (§7).

**(d) Unsupported hardware claims.** 114 distinct `equipment_justification`
strings assert A100 / H100 / DGX / RTX 4090 capacity — e.g. *"2× DGX Sparks for
inference"*, *"30,000 H100 80GB GPU-hours"*. Two different things are mixed:
a costed cloud-hours budget line (defensible if priced) and an assertion of
owned capacity (a statement of fact). This machine's documented accelerator is
an **Arc 140T with 7.80 GB** visible to `torch.xpu` — so any "we have 2× A100 /
DGX Spark" reading is false as written. If a funder audits equipment claims, the
exposure is misrepresentation, and this is exactly the failure the
2026-11-03 legal memorandum describes: machine-generated text asserting facts no
human verified.

**(e) Fabricated scope text.** `opensats` override invents "Bitcoin integration …
financial mental health applications"; `freecad_grant` invents "CAD integration
for therapeutic environment modeling". Both funders are scope-limited, and both
inventions were written to make an out-of-scope project look in-scope.

---

## 3. Eligibility tiers

Confidence is per row, not per tier. **`checked` = verified this session against
the funder's own material. `strong` = well-established but not re-read today.
`unverified` = my reading, not checked — do not act on it as fact.**

### Tier A — open to a natural person, no entity required

| funder | cap (repo figure) | confidence | basis / note |
| --- | --- | --- | --- |
| `github_secure_oss` | $10,000 | **checked** | "Anyone who is a current maintainer of an open source project", team of max 2, $6k during + $2k at 6 months + $2k at 12 months. Session cadence ~2–3/yr; next session date not announced. |
| `nlnet` | $50,000 | **strong** | NLnet funds individuals; cutoff just passed (§0). |
| `opensats` | rolling | **strong** | Funds individual developers — but **Bitcoin-scope only**, so the fabricated override in §2(e) is the only reason it is in these profiles. |
| `epic_megagrants` | $150,000 | unverified | Individuals/teams believed eligible; requires Unreal Engine relevance. |
| `raais_foundation`, `catalyst_fund`, `openscience_fund`, `amazon_security`, `openai_researcher`, `anthropic_academic`, `anthropic_claude`, `google_cloud_research`, `ai_grant_oss` | various | unverified | **Do not treat as eligible.** Several of these read as academic- or company-gated on their face; they are listed here only so nothing is silently dropped. |

**Honest count for tier A: 2 rows checked or strong, 1 more plausible, 10 unknown.**
Not "13 funders you qualify for." The three that carry weight are
`github_secure_oss` (checked, maintainer of an OSS project), `nlnet` (individuals
supported, cutoff just passed) and `opensats` (individuals — but Bitcoin scope
only, which is why its override was fabricated).

### Tier B — needs a legal entity or an institutional affiliation (19 keys)

`aws_activate`, `aws_activate_ai`, `google_startups`, `google_startups_ai`,
`microsoft_startups`, `cloudflare_startups`, `nvidia_inception`,
`github_accelerator`, `unicef_venture`, `ai_grant_oss` (moved here on reflection:
AI Grant is for founders/companies), `openai_mental_health`, `one_mind`,
`humanity_ai`, `wellcome`, `wellcome_trust`, `czi_eoss`, `sloan_ai_science`,
`sloan_ospo`, `schmidt_ai_fellowship`, `nvidia_academic`.

Two different gates hide in this one list, and they are not interchangeable:

- **Entity gate** (a company, a 501(c)(3), a registered nonprofit): the credits
  programmes, the accelerators, UNICEF Venture, and most of the foundations.
  This gate is **purchasable or sponsorable** — §4.
- **Affiliation gate** (a university, a PI appointment, a postdoc position):
  `nvidia_academic`, `sloan_ai_science`, `schmidt_ai_fellowship`, and the
  Wellcome awards read this way. This gate is **not purchasable**. No identity
  document, fee or filing satisfies it. These are out unless an affiliation
  exists.

### Tier C — cannot be entered from here, at any price (6 keys)

| funder | bar |
| --- | --- |
| `prototype_fund` | German residency required |
| `open_science_nl` | Dutch institutions |
| `charted_fund` | UK research software engineers |
| `ukomain` | UK |
| `linux_australia` | Australia |
| `freecad_grant` | FreeCAD project scope, not a general fund |

Cost of keeping these six in the profiles: they generate 198 rows of work that
can never be submitted, and they are the ones whose scope pressure produced
fabricated overrides.

---

## 4. The identity question — free, cheap, and not free

The previous section makes "how do I obtain a free identity" the decisive
question, so it is answered here in the order that costs least.

**First: a natural person is already a legal identity, at $0.** You can contract,
invoice, receive a 1099 and be paid by a funder without forming anything. Tier A
is reachable today with no filing at all. What you *cannot* do as a bare
individual is pass a "company / organisation" checkbox, and no amount of
ingenuity changes that — the funder is asking for a legal form, not a document.

**Second: sole proprietor + trade name (~$0 entity, small name fee).** A sole
proprietorship is not formed; it exists by default. A PA fictitious name
registration lets you bank and invoice under a project name. This satisfies
"contractor/vendor" paperwork. It does **not** satisfy "registered company".

**Third: fiscal sponsorship — the actual free entity.** A fiscal host is an
existing 501(c)(3) that receives funds on your project's behalf. Open Collective
and the Open Source Collective work this way: **no formation fee**, you pay a
percentage of money actually raised. This is the only route that makes an
individual legible as a nonprofit without forming one, and it is the correct
answer for open-source funding specifically. Verify the host accepts your project
type and check whether a given funder accepts a fiscally sponsored applicant —
that varies by funder and is not something a host's marketing page settles.

**Fourth: an LLC — $125, not free, and it unlocks the largest bucket.** Measured
from the PA Department of State fee schedule:

| item | cost |
| --- | --- |
| Certificate of Organization (LLC) | **$125**, **waived for qualifying veterans and reservists** |
| foreign LLC registration (out-of-state entity) | $250 |
| EIN | **$0** — IRS, online, minutes |
| annual registration | **at least $340/yr** (recurring; budget it) |
| decennial report | $70 |

So the honest price of tier B's entity gate is **$125 once and ≥$340 every year**,
plus a free EIN — and it is the single highest-leverage decision in this register,
because it converts ~10 credit/accelerator programmes from impossible to
applicable.

**A 501(c)(3) is not free.** Form 1023-EZ is $275 and annual Form 990 filing
follows. Fiscal sponsorship exists precisely so you do not have to buy this.

**What no identity buys:** the affiliation gate in tier B. And there is one hard
constraint to say out loud — **you can publish pseudonymously, but you cannot be
paid pseudonymously.** Every payout path (1099-NEC, W-8BEN, Stripe, GitHub
Sponsors, bounty platforms) terminates in a legal name and a tax ID. The
pseudonymous project identity and the payee identity are separable; the payee
identity is not optional.

---

## 5. Crowdfunding and bug bounty — no gatekeeper, no deadline

These were the other half of the request, and they are the streams that do not
depend on any of §3.

**Bug bounty — best capability fit, no entity, no deadline:**

- **0DIN (Mozilla, GenAI bounty)** — checked: apps scope pays starting $500,
  medium $2,500, high $5,000; open to individual researchers. The genuine fit is
  the existing surface here: multi-provider inference routing, agent frameworks,
  prompt-injection handling, local model serving. This is the highest
  expected-value stream in the register relative to effort.
- **Established platforms** (HackerOne, Bugcrowd, Intigriti, YesWeHack) — open to
  individuals; require identity verification and a tax form, both free.
- **AI/ML OSS bounty programmes** — the landscape moves (platform ownership has
  changed hands); check current status before planning around any specific one.

**Crowdfunding — needs audience, not permission:**

- **GitHub Sponsors** — individual, free to enable, payout needs bank + tax ID.
- **Ko-fi / Patreon / Buy Me a Coffee** — no eligibility gate whatsoever.
- **Kickstarter / Indiegogo** — reward crowdfunding; succeed or fail on audience
  size, and a campaign is a marketing project, not a form.
- **Open Collective** — the fiscal-host route from §4.

The uncomfortable arithmetic: crowdfunding is gated on an audience that these 33
profiles do not show evidence of. `adoption_metrics` is empty in 33/33 profiles
(§2b), which is precisely the field a crowdfunding page lives or dies on. Bug
bounty is gated on skill that demonstrably exists in this tree. That asymmetry
should decide where the next 30 days go.

---

## 6. Next actions, in order

1. **Stop treating the batch as live.** Retire `NLNET_BATCH_2026-11-03` for what
   it was — a missed cutoff — and re-post as a per-project NLnet application for
   the next odd-month cutoff, one project, not 33.
2. **Read the next NLnet cutoff off nlnet.nl** before writing any date.
3. **Pick one project, not 33.** The one with a public repo path that resolves —
   `github.com/myzticalbabe/azazael` is **public and
   `.../tree/main/Project_Nurse_Ratchet` returns HTTP 200**, so the link an
   application depends on is real.
4. **Produce the four documents that are missing everywhere:** `proposal`,
   `budget`, `timeline`, `pitch_deck`. One project's worth. These also unblock
   `adoption_metrics` and `milestones`.
5. **Delete the 114 hardware justifications** and replace with a single costed
   compute budget that states what is owned (Arc 140T, 7.80 GB) and what is
   rented.
6. **Decide the entity question** (§4): $0 natural person for tier A now, versus
   $125 + ≥$340/yr for the tier B bucket. Fiscal sponsorship is the free middle
   path and is the right default for OSS funding.
7. **File one 0DIN report** to test the bounty stream against real effort before
   planning revenue around it.
8. **Strip tier C entirely** (6 funders, 198 rows).

---

## 7. What would make this register wrong

- The subject is not a solo US individual, or already has an entity — then tier B
  collapses into tier A and §4 is moot. Nothing in the profiles settles this.
- Any tier A row marked `unverified` turns out to be company- or
  affiliation-gated. I checked two of thirteen.
- The PA fee schedule changes; the `≥$340` annual figure is read from the DOS fee
  page on this date and is the recurring cost most likely to be underestimated.
- NLnet's next cutoff date — unverified here by design, since guessing it is how
  the row being retired was wrong.

**Expiry: re-measure the numbers in §0, §1 and the fee table before
2026-12-03.** Deadlines and fees both move.

---

## 8. Limits of this review

- Funder eligibility read from search results and the repo's own profile data;
  **two funders verified against their own material, twenty-four not**.
- No funder was contacted; no application was opened to inspect its live form.
- Amounts are the repo's `max_amount` strings. The $10,000 GitHub figure and the
  0DIN tier figures are checked; the rest are unconfirmed.
- PA fees read from the Department of State fee schedule page; no filing was
  attempted.
- Fiscal-host acceptance rules were not tested against any specific funder.
- Nothing here is legal, tax or financial advice.
