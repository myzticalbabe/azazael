# FISCAL HOST vs PA LLC, TESTED AGAINST THE GATED FUNDERS

**Date:** 2026-11-03 · **Question:** the register identified a set of funders that
require a legal entity. Of the two affordable routes to one — a fiscal host (a
percentage of funds raised) and a registered LLC (a fee, then an annual one) — which
actually opens those funders, and what does each cost?

**Source of the funder list:** `docs/FUNDING_REGISTER_2026-11-03.md` §3.
**Source of the PA fees:** the same register §4, measured from the PA Department of
State fee schedule.

---

## 0. The answer in five lines

1. **Both routes are real, and they open *different* doors.** They are not
   substitutes: a fiscal host makes you legible as a *nonprofit*; an LLC makes you
   legible as a *company*. Most gated funders want one specific shape.
2. **Neither route buys the second gate.** Six of the gated keys require a
   university or PI affiliation. No filing, fee or host confers that.
3. **The cheapest correct move today is to spend nothing.** The two funders this
   project can actually be submitted to (`nlnet`, `github_secure_oss`) are open to a
   natural person. No entity is on the critical path.
4. **If one must be chosen before a specific application exists, the LLC is the more
   convertible asset** — it is the applicant's own, it never expires for
   non-payment of a percentage, and it satisfies the larger count of gates.
5. **A fiscal host is cheaper only while you raise little** and stops being cheap at
   volume; an LLC is a fixed cost that gets cheaper per dollar as awards grow.

## 1. First, a defect in the list being tested

The register's Tier B heading says **"19 keys"**. The list under it contains **20**:

`aws_activate`, `aws_activate_ai`, `google_startups`, `google_startups_ai`,
`microsoft_startups`, `cloudflare_startups`, `nvidia_inception`,
`github_accelerator`, `unicef_venture`, `ai_grant_oss`, `openai_mental_health`,
`one_mind`, `humanity_ai`, `wellcome`, `wellcome_trust`, `czi_eoss`,
`sloan_ai_science`, `sloan_ospo`, `schmidt_ai_fellowship`, `nvidia_academic`.

`ai_grant_oss` is also named in Tier A's list of ten unknowns, so it is
**double-classified**: it appears as both "open to an individual, unverified" and
"needs an entity". It cannot be both. This document treats it as gated (the stricter
reading) and counts **20 gated keys**, and records the contradiction rather than
quietly picking the tidier number.

## 2. Two gates, and only one is for sale

| gate | what it demands | purchasable? | who |
| --- | --- | --- | --- |
| **Entity gate** | a company, a 501(c)(3), or a registered nonprofit | **yes** — form it, or be sponsored by one | credits programmes, accelerators, venture funds, most foundations |
| **Affiliation gate** | a university, a PI appointment, a postdoc position, an institutional signatory | **no** | `nvidia_academic`, `sloan_ai_science`, `schmidt_ai_fellowship`, `wellcome`, `wellcome_trust` |

Five keys in the list are affiliation-gated. They are **out on both routes** and no
amount of this comparison changes that. `wellcome`/`wellcome_trust` are counted here
as one requirement met twice, not two opportunities.

## 3. The routes, priced

| route | one-off | recurring | legal shape it presents | owned by applicant |
| --- | --- | --- | --- | --- |
| **Natural person** | $0 | $0 | individual | yes |
| **Sole prop + PA fictitious name** | fee **not verified this session** | $0 | individual trading under a name | yes |
| **Fiscal host** (Open Collective / Open Source Collective) | $0 formation | **a percentage of funds actually raised** — the exact rate was **not verified this session** | nonprofit project under a host's 501(c)(3) | **no** — the host holds the funds and is the applicant of record |
| **PA LLC** | **$125** (waived for qualifying veterans/reservists) + **$0** EIN | **≥$340/yr** annual registration; **$70** decennial | company | yes |
| **501(c)(3)** | $275 (1023-EZ) + filing | annual Form 990 | charity | yes |

Three figures above are deliberately marked unverified. The register measured the PA
fees; it did not read the fiscal hosts' current percentage, and neither did this
document. **A percentage that decides the comparison must be read from the host, not
recalled.**

## 4. Does the route actually open the funder?

The distinction that decides the comparison: **a fiscal sponsee is a nonprofit
project; an LLC is a company.** Startup credits and accelerator programmes ask for
the second. Foundations and charities ask for the first.

| funder | gate it states | fiscal host | PA LLC | confidence |
| --- | --- | --- | --- | --- |
| `aws_activate` | startup/company for credits | ✗ not a company | ✓ | plausible, unverified |
| `aws_activate_ai` | as above | ✗ | ✓ | plausible, unverified |
| `google_startups` | startup, company | ✗ | ✓ | plausible, unverified |
| `google_startups_ai` | startup, company | ✗ | ✓ | plausible, unverified |
| `microsoft_startups` | startup, company | ✗ | ✓ | plausible, unverified |
| `cloudflare_startups` | startup, company | ✗ | ✓ | plausible, unverified |
| `nvidia_inception` | startup, company | ✗ | ✓ | plausible, unverified |
| `github_accelerator` | company/team, equity-free accelerator | ✗ | ✓ | plausible, unverified |
| `unicef_venture` | registered for-profit startup, young company | ✗ | ✓ | plausible, unverified |
| `ai_grant_oss` | founders/companies | ✗ | ✓ | unverified |
| `openai_mental_health` | org (company or nonprofit) | ✓ | ✓ | **unverified** — either may pass |
| `one_mind` | company, accelerator-style | ✗ | ✓ | unverified |
| `humanity_ai` | org | ✓ | ✓ | unverified |
| `czi_eoss` | institution / nonprofit | ✓ | ✗ | plausible, unverified |
| `sloan_ospo` | institution, OSPO context | ✓ | ✗ | plausible, unverified |
| `nvidia_academic` | **academic affiliation** | ✗ | ✗ | **not purchasable** |
| `sloan_ai_science` | **academic affiliation** | ✗ | ✗ | **not purchasable** |
| `schmidt_ai_fellowship` | **academic/PI** | ✗ | ✗ | **not purchasable** |
| `wellcome` | **institutional signatory** | ✗ | ✗ | **not purchasable** |
| `wellcome_trust` | **institutional signatory** | ✗ | ✗ | **not purchasable** |

Tally: **LLC-shaped 11 · nonprofit-shaped 3 · either 3 · neither 5** (of 20, one key
counted twice as `wellcome`/`wellcome_trust` is one requirement).

**The important correction to the register's framing:** its §4 says the entity gate
"converts ~10 credit/accelerator programmes from impossible to applicable". That is
true for the **LLC** and **not** for a fiscal host. A fiscal host does not open the
credits programmes — they want a company. A host opens the two or three foundation
keys, which are also the ones with the longest review cycles.

## 5. Cost over three years

Assumed awards, since a percentage host is proportional and an LLC is not:

| scenario | fiscal host | LLC | cheaper |
| --- | --- | --- | --- |
| nothing raised | $0 | $125 + $340 × 3 = **$1,145** | host |
| $5,000 raised once | 5,000 × (host %, unverified) | $1,145 | depends on the % — at 10% the host is $500 |
| $20,000 raised | at 10%: $2,000 | $1,145 | **LLC** |
| $50,000 raised (an NLnet award) | at 10%: $5,000 | $1,145 | **LLC by ~$3,855** |

The crossover is real and early: **a host is cheaper only while the money is small.**
The percentage also applies to money raised through channels the host does not open,
which is the part that is easy to overlook.

## 6. The decision rule

**Spend nothing now.** The two submissions this project can actually make this
quarter — NLnet (individuals) and GitHub Secure OSS (any current maintainer) — need
no entity. Forming anything before an application exists is paying an annual fee to
keep a checkbox available.

**Then, in this order:**

1. **If the next real application is a foundation/charity gate** (`czi_eoss`,
   `sloan_ospo`, or `openai_mental_health` if it turns out nonprofit-only): approach
   a fiscal host. Cost is proportional; nothing is spent if nothing is raised.
   Confirm in writing that the specific funder accepts a fiscally sponsored
   applicant — hosts' marketing pages do not settle this, and it varies by funder.
2. **If the next real application is a credits or accelerator programme** (the 11
   LLC-shaped keys): the host is the wrong instrument. Either form the LLC
   ($125 + ≥$340/yr) or skip those funders — many credits programmes are worth
   service credits, not cash, and are not worth an annual filing to reach.
3. **Never form anything for the affiliation-gated five.** They are unreachable
   from here at any price, and the register's own tier C already excludes six more
   on jurisdiction.

## 7. What neither route fixes

- **Payout identity.** A host does not make a payout pseudonymous; the host still
  requires a legal name and a tax ID for the individual behind the project. The
  register already says this and it stays true.
- **The profiles.** `entity` is `null` in all 33 profiles regardless of this
  decision. Whichever route is chosen, the field stays unset until the profile
  generator is fixed — and the NLnet form's entity selector is a **select**, so an
  unset value is an unfilled required field, not a default.

## 8. Limits

- Every "plausible, unverified" row above is a reading of how these programmes
  usually work, **not** a reading of their current terms. Before any application,
  the funder's own page decides the answer; this table only orders the search.
- The fiscal hosts' percentages were not measured. The comparison in §5 is therefore
  a formula with one unknown, and the crossover point moves with it.
- A fiscal host may decline the project; the route is an application, not a purchase.
- PA fees are as recorded in the register on 2026-11-03 and can change; the $125
  veteran/reservist waiver has conditions that were not read.
- This is not legal or tax advice, and no filing has been made.

**Expiry: 2027-01-03** — the funder classifications and every fee above must be
re-read before they are used to justify spending money.
