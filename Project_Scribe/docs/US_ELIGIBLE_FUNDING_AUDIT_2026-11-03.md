# US-eligible funding routes for Project Nurse Ratchet — audited 2026-11-03

Written because NLnet's Horizon Europe rule (measured: `Project_Scribe/data/eligible_countries.json`,
180 countries, **United States absent**) closes the two programmes Scribe was pointed at. This is
the audit of what is actually left for a **US individual**, with the verification state of each
claim stated rather than implied.

Columns: **fit** is the assistant's judgement of whether the funder's own stated purpose covers a
mental-health continuity tool — it is not a funder's ruling. **verified** names what was read and
what could not be read.

## Routes

| route | what it funds | US individual? | amount | deadline | verified | fit |
| --- | --- | --- | --- | --- | --- | --- |
| **NLnet OIS / Restack / CodeSupply** | privacy, open internet infrastructure | **No** — Horizon Europe 60% rule | €5k–€50k | 2027-01-03 | page + country list parsed, gate exercised in `scribe.py` | n/a — excluded |
| **Open Technology Fund — Internet Freedom Fund** | circumvention tech, censorship measurement, digital-security ecosystem | **Yes** — "individuals or organizations"; pays USD | $10k–$900k, ideal ask $50k–$200k, ≤24 months | rolling | page read 2026-11-03 (200) | **poor** — mandate is internet freedom under repression; a relapse-continuity counsellor is not a circumvention tool |
| **Emergent Ventures (Mercatus)** | "ambitious people", low-overhead, no deliverables schedule | **Yes**, 13+ | $1k–$50k, no typical range | rolling | application form exists (200, JS-only); **mercatus.org returns 403**; "13+" from the primary form's own text, "global" only from aggregators | **good** — no topic carve-out, individuals, rolling |
| **GitHub Secure Open Source Fund** | supply-chain security of critical OSS, 3-week security education | **Yes** — individual maintainers or small teams | historically ~$10k/project | "Apply now" live, sessions run in cohorts | repo page read 2026-11-03 (200) | **poor** — the project is not a dependency others build on |
| **Bounties (HackerOne / Bugcrowd / huntr)** | disclosed vulnerabilities in *the vendor's* product | yes, if the vendor's programme is open | $50–$10k+ per accepted report | per programme | **UNVERIFIED** — no programme terms read this session | **none for this codebase** — a bounty pays for a finding in someone else's software; this tree is not a target |

## What the audit actually establishes

1. **The equipment question is answered by the funders' own documents, not by the pitch.** OTF's
   page names categories (technology development, applied research, digital-security ecosystem)
   and none of them is "buy hardware". EV states explicitly that there is "NO typical grant range
   or average award amount — funding is project specific", which is the one route where an
   equipment line is not excluded up front.
2. **The two funds whose purpose is closest to software ask what it is a dependency *for*.**
   GitHub SOSF funds security of things other software relies on. Nurse Ratchet is currently an
   application, not a dependency, so this route needs the project to become something others
   import before the fund's purpose fits.
3. **Bounties are not a funding route for one's own project.** They pay for findings against a
   vendor's software, under that vendor's terms. Nothing measured here suggests otherwise, and no
   programme terms were read — so this line is UNVERIFIED, not refuted.
4. **A US individual is eligible for more than NLnet, but for smaller sums.** The ceiling of the
   only genuinely fitting route found (EV) is below the equipment figures a clinic-grade
   deployment implies.

## Open gaps (not to be read as closed)

- **mercatus.org is 403 from this host.** EV's topic scope, cohort cadence and any exclusion of
  for-profit or medical claims are **unverified**. The application is a TFA form rendered by
  JavaScript, so **Scribe cannot dry-run it** — the page-level error learning that works on
  NLnet's static form has nothing to attach to here.
- No state-level or federal route was audited (SBIR/STTR are institution-shaped; a US individual
  applying needs an entity). That is a separate audit and is not begun.
- Crowdfunding, fiscal sponsorship and hardware-donation programmes were not audited at all.
- No route above was contacted. Nothing here is an offer, an eligibility ruling, or a decision by
  any funder.

## Reproduce

```
# NLnet eligibility gate, exercised both ways
python Project_Scribe/scribe.py --dry-run-all --profile profiles/nurse_ratchet_profile.json \
    --country "United States"        # 0 ok | 3 unexercised | 2 skipped | 0 error
python Project_Scribe/scribe.py --dry-run-all --profile profiles/nurse_ratchet_profile.json \
    --country "Netherlands"          # negative control: page loads and fills

# what the gate is reading
python -c "import json;d=json.load(open('Project_Scribe/data/eligible_countries.json'));\
print(len(d['horizon_europe']), 'United States' in d['horizon_europe'])"   # 180 False
```
