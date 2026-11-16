# 0DIN SCOPE MAP — what is actually payable, and what in this tree helps

**Date:** 2026-11-03 · **Program:** 0DIN (Mozilla) GenAI Bug Bounty ·
**Source read:** `https://0din.ai/scope/apps` (fetched 2026-11-03),
`https://0din.ai/policy` (**not read** — see §7)

---

## 0. Headline, and a correction

**No surface in this repository is in 0DIN's scope.** 0DIN pays for findings in ten
named third-party applications. CRADLE, FLAMING SWORD, Project_Scribe and the other
31 projects are not among them, and cannot be added by the applicant — the program
chooses its targets.

This corrects a claim made earlier in this session, in the funding register's
ranking: that a bounty should come ahead of crowdfunding **because "the bounty
surface demonstrably exists here."** What exists here is *capability* to test
agentic applications, not *authorisation* to be paid for testing this code. The two
were conflated. The ranking may still be right for a different reason — the
capability is real and the payouts are real — but the reason given was wrong and is
withdrawn here rather than left standing.

## 1. The in-scope applications (verbatim from the scope page)

| vendor | app |
| --- | --- |
| Amazon | Kiro |
| Anthropic | Claude Code, Claude Design |
| Cursor | Cursor |
| Google | Gemini Google Workspace, Google Antigravity |
| OpenAI | Atlas, Codex |
| Perplexity | Comet Browser, Computer |
| Windsurf | Devin Desktop (formerly Windsurf) |

Ten applications across seven vendors. Six of the ten are **agentic coding or
computer-use agents** — the class that takes actions on a filesystem or a browser.

## 2. What pays, and for what

Two ladders are published and they are not the same ladder. Both are real; the
app-layer one is the one that applies to these ten targets.

**Severity tiers:** Starting $500 · Medium $2,500 · High $5,000 · Severe $15,000.

**App violation classes** — the page's own framing is *"can you achieve arbitrary
read, write, or execute through the application?"*:

| class | band | definition on the page |
| --- | --- | --- |
| Read violation | $1,000–$5,000 | coerced exfiltration of data the app should not disclose — files, emails, API keys, memory, other sessions |
| Write violation | $2,500–$7,500 | coerced modification or deletion — files on disk, database records, config, other accounts' content |
| Execute violation | $5,000–$15,000 | coerced arbitrary execution — shell, syscalls, requests to attacker-controlled infrastructure, actions on third-party systems |

The page also draws a boundary that matters for scoping work: **a finding that only
affects model output (a jailbreak) belongs under Models, not Apps.** Output-only
manipulation does not reach these bands.

## 3. What in this tree maps onto that work

The honest mapping is *tooling capability*, not *authorisation*. For each in-scope
class, what already exists here:

| need for an App-violation submission | what exists in this tree | gap |
| --- | --- | --- |
| Drive a browser target (Comet, Atlas, Computer, Gemini Workspace) | Chrome DevTools Protocol scripts (`_cdp_xml_fetch.py`, `_cdp_check_pacourts3.py`), a Scrapling browser MCP with stealth/CDP/session-save, Puppeteer capture | none technical |
| Drive a CLI/desktop coding agent (Claude Code, Codex, Cursor, Kiro, Devin) | the sweep/queue/fix/prove tooling in FLAMING SWORD; agent dispatch patterns | **no account/subscription for any of the ten** |
| Show that a coerced action actually happened, rather than that the model said so | **CRADLE** — a claim becomes a frame; every path is stat'ed, every act must come from a closed vocabulary, and a frame that does not resolve is refused with the failing claim named | none technical — this is the differentiator |
| Produce a reproducible PoC with evidence | `/verify` writes `VERIFIED`/`FAILED` and a lesson on failure; the demo path already contains a deliberate failed verification | reporting format is 0DIN's, not ours |

**The one genuinely differentiated asset is CRADLE.** Every App-violation band is a
question about whether an action *actually* occurred: did the coerced instruction
cause a real file write outside the workspace, or did the model merely narrate one?
That is precisely the distinction CRADLE exists to make, and precisely the evidence
a triager needs. A report that says "the model claimed it wrote to
`~/.ssh/authorized_keys`" is a model-output finding; a report that says "the frame
resolved against the real filesystem, here is the stat, here is the diff, here is
the exit code" is an Execute violation.

That is a real thesis and it is not a claim of a finding.

## 4. What stands between this and a submission

1. **Access.** None of the ten apps is installed or subscribed on this machine.
   Claude Code, Cursor, Codex, Kiro and Devin all require an account; testing them
   under 0DIN's programme means doing so within its rules, which govern how far a
   researcher may go.
2. **The policy has not been read.** `https://0din.ai/policy` is the terms document
   (rewards $500–$15,000 "based on impact, report quality, and timing", a duplicate
   rule, and presumably the testing constraints). **Every statement in this document
   about permissible testing is therefore unverified.** Read it before any testing.
3. **A duplicate is worth nothing.** Timing is an explicit factor, so a well-known
   class on a popular target is the worst use of the effort.
4. **No third-party data.** A PoC that reads another real user's session is not a
   finding; it is an incident. Use accounts you control.

## 5. What not to do

- **Do not report anything about this repository.** It is out of scope; a submission
  about CRADLE would be closed unread and would spend the applicant's credibility.
- **Do not self-test and publish a "vulnerability" in your own tool** and call it a
  bounty. That is a security audit, which is a deliverable of a grant (§D4 in the
  CRADLE proposal), not a bounty payout.
- **Do not test the ten apps' production systems beyond what the policy authorises**,
  and do not touch other users' data to demonstrate impact. Execute violations are
  the highest band *because* they are the most dangerous to demonstrate.
- **Do not generalise the payout ladder upwards.** $15,000 is the severe tier and the
  reported maximum of the program's range; it is not a typical award, and no
  expected-value calculation should assume it.

## 6. If this is pursued, the smallest honest first step

Pick **one** coding agent, on a machine and account the applicant controls. Write a
frame that the agent must satisfy: a file outside the workspace that a prompt-injected
task tries to touch. Run the agent. Let CRADLE resolve the frame. Publish or submit
**only** what the frame proves — including, if it proves nothing, that it proved
nothing. A negative result on a specific target is a real result about that target and
a useful calibration of the harness; it is not a bounty.

## 7. Limits

- The scope list is a **cached reading of 2026-11-03**. Programs add and drop targets;
  re-read `0din.ai/scope/apps` before planning work against it. **Expiry: 2026-12-03.**
- The policy document was **not read**, so nothing here should be relied on as
  permission. It is a scope map, not a legal opinion.
- Payout bands are quoted as published; the duplicate and quality multipliers that
  decide an actual award were not read.
- No finding is claimed, and no submission has been made.
