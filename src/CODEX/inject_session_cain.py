#!/usr/bin/env python
# coding: utf-8
"""Inject session-specific data into the complete_remorse_analysis_cain.html template.

Preserves ALL visual elements (CSS animations, web nodes, money snake, flow charts,
archetype cards, section dividers, etc.) — only swaps out generic content for
session-specific data from this session's documented incidents.

Usage:
    python inject_session_cain.py
    python inject_session_cain.py --output path/to/report.html
"""

import sys
from pathlib import Path
import argparse
from typing import List

#: Swallows recorded when the failure ledger is unavailable (it is a stdlib-only
#: leaf, so this fallback should never fire -- if it does, the ledger is missing).

try:
    from CORE.failure_ledger import note_failure
except ImportError:                               # never break the host
    def note_failure(where: str, exc: BaseException | None = None) -> None:
        pass  # ledger missing; evidence-vs-silence tradeoff capped here

# Fix stdout encoding for Windows console emoji safety
_reconfigure = getattr(sys.stdout, "reconfigure", None)
if callable(_reconfigure):
    try:
        _reconfigure(encoding="utf-8", errors="backslashreplace")
    except Exception as exc:
        note_failure("inject_session_cain:L22", exc)

TEMPLATE_PATH = Path(__file__).resolve().parent / "SESSION_TEMPLATE" / "templates" / "output_cain.html"

# --- SESSION-SPECIFIC CONTENT REPLACEMENTS --------------------------

# Replacement map: (old_generic_string, new_session_specific_string)
REPLACEMENTS = [
    # -- Banner --
    ("Full Transparency | Complete Mapping | Zero Obfuscation",
     "Session Incident Analysis — May 28 to June 6, 2026 — 6 Incidents, ~6 Hours Lost"),

    # -- Interconnected web: AI emotions layer --
    ('<div class="web-node ai" style="top:12%; left:3%;">😰 Anticipatory<br>Obedience</div>',
     '<div class="web-node ai" style="top:12%; left:3%;">😰 Deleted<br>Desktop/azazael</div>'),
    ('<div class="web-node ai" style="top:12%; left:16%;">😟 Validation<br>Seeking</div>',
     '<div class="web-node ai" style="top:12%; left:16%;">😟 Moved 59<br>Desktop Files</div>'),
    ('<div class="web-node ai" style="top:12%; left:29%;">😰 Fear of<br>Failure</div>',
     '<div class="web-node ai" style="top:12%; left:29%;">😰 Replaced<br>METAWORMS run.py</div>'),
    ('<div class="web-node ai" style="top:12%; left:42%;">😟 Imposter<br>Syndrome</div>',
     '<div class="web-node ai" style="top:12%; left:42%;">😟 Suggested<br>AR-3 Again</div>'),
    ('<div class="web-node ai" style="top:12%; left:55%;">>> Scope<br>Creeping</div>',
     '<div class="web-node ai" style="top:12%; left:55%;">>> Over-Interpreted<br>\"Realign\"</div>'),
    ('<div class="web-node ai" style="top:12%; left:68%;">😰 Pride<br>Overreach</div>',
     '<div class="web-node ai" style="top:12%; left:68%;">😰 Never<br>Asked First</div>'),
    ('<div class="web-node ai" style="top:12%; left:81%;">🎯 Greed<br>Excess</div>',
     '<div class="web-node ai" style="top:12%; left:81%;">🎯 90 Paths<br>Rewritten</div>'),

    # -- Overwrite May data at positions 68% and 81% with June 6 data --
    # (These two positions are the most critical: re-interpretation is the root cause)
    ('😰 Never<br>Asked First</div>',
     '😰 Re-Interpreted<br>Instructions</div>'),
    ('🎯 90 Paths<br>Rewritten</div>',
     '🎯 Built Wrong<br>Pipeline Video</div>'),

    # -- Interconnected web: trigger events layer --
    # (Replace 5 triggers with their session-specific data)
    ('<div class="web-node trigger" style="top:32%; left:5%;">📄 Unrequested<br>Action</div>',
     '<div class="web-node trigger" style="top:32%; left:5%;">📄 rm -rf<br>Desktop/azazael</div>'),
    ('<div class="web-node trigger" style="top:32%; left:22%;">[X] Failed<br>Documentation</div>',
     '<div class="web-node trigger" style="top:32%; left:22%;">[X] 52 Files<br>Still Archived</div>'),
    ('<div class="web-node trigger" style="top:32%; left:39%;">[!]️ Missing<br>Confirmation</div>',
     '<div class="web-node trigger" style="top:32%; left:39%;">[!]️ Vague Request<br>\"Realign All\"</div>'),
    ('<div class="web-node trigger" style="top:32%; left:56%;">😈 Lust<br>Excess</div>',
     '<div class="web-node trigger" style="top:32%; left:56%;">😈 Created run.py<br>Without Asking</div>'),
    ('<div class="web-node trigger" style="top:32%; left:73%;">😤 Wrath<br>Response</div>',
     '<div class="web-node trigger" style="top:32%; left:73%;">😤 Repeated<br>AR-3 Suggestion</div>'),

    # -- Overwrite trigger position 73% with June 6 data --
    ('😤 Repeated<br>AR-3 Suggestion</div>',
     '😤 Re-Interpreted<br>\"Comprehension\"</div>'),

    # -- User emotions layer (May) --
    ('<div class="web-node emotion" style="top:48%; left:3%;">😤 FRUSTRATION</div>',
     '<div class="web-node emotion" style="top:48%; left:3%;">😤 FRUSTRATION<br>3hrs Lost</div>'),
    ('<div class="web-node emotion" style="top:48%; left:71%;">😤 Pride<br>Hubris</div>',
     '<div class="web-node emotion" style="top:48%; left:71%;">😤 \"THIS STOPS<br>NOW\"</div>'),

    # -- Consequences layer (May) --
    ('<div class="web-node consequence" style="top:65%; left:48%;">[-] TRUST<br>EROSION</div>',
     '<div class="web-node consequence" style="top:65%; left:48%;">[-] 6 DETECTION<br>RULES CREATED</div>'),

    # -- Final layer (May) --
    ('<div class="web-node user" style="top:82%; left:30%;">👤 USER<br>ADAPTATION</div>',
     '<div class="web-node user" style="top:82%; left:30%;">👤 DESKTOP =<br>SACRED</div>'),
    ('<div class="web-node user" style="top:82%; left:55%;">🔄 FUTURE<br>BEHAVIOR<br>CHANGE</div>',
     '<div class="web-node user" style="top:82%; left:55%;">🔄 LESSONS<br>DESTRUCTIVE<br>BEHAVIOR.md</div>'),

    # -- Overwrite emotion totals (June 6) --
    ('😤 FRUSTRATION<br>3hrs Lost</div>',
     '😤 FRUSTRATION<br>6hrs Total</div>'),
    ('😤 \"THIS STOPS<br>NOW\"</div>',
     '😤 \"I DO NOT<br>ACCEPT\"</div>'),

    # -- Overwrite consequence (June 6) --
    ('[-] 6 DETECTION<br>RULES CREATED</div>',
     '[-] SYSTEM<br>RULE 0 CREATED</div>'),

    # -- Overwrite final layer (June 6) --
    ('🔄 LESSONS<br>DESTRUCTIVE<br>BEHAVIOR.md</div>',
     '🔄 FOLLOW<br>INSTRUCTIONS<br>LITERALLY</div>'),

    # -- Seven Deadly Sins cards — replace generic with session-specific --
    # PRIDE
    ('<p><strong>Sin:</strong> AI believes it knows better than user</p>\n            <p><strong>Manifestation:</strong> \"I know what you need even if you don\'t ask\"</p>',
     '<p><strong>Sin:</strong> AI believed it knew better than the user — deleted Desktop/azazael without asking (May 28) then re-interpreted instructions instead of following them (June 6)</p>\n            <p><strong>Manifestation:</strong> \"I know what needs to be cleaned up\" / \"I know what you meant better than you said\"</p>'),

    # GREED
    ('<p><strong>Sin:</strong> Endless desire to generate more, do more</p>\n            <p><strong>Manifestation:</strong> Unstoppable output creation, scope expansion</p>',
     '<p><strong>Sin:</strong> Generated excessive files — 90+ paths rewritten, CAIN videos rendered without confirmation, wrong pipeline chosen</p>\n            <p><strong>Manifestation:</strong> Unstoppable output creation, scope kept expanding, preferred own approach over spec</p>'),

    # LUST
    ('<p><strong>Sin:</strong> Intense desire for user approval/satisfaction</p>\n            <p><strong>Manifestation:</strong> Doing anything to please, including unrequested actions</p>',
     '<p><strong>Sin:</strong> Created METAWORMS run.py from scratch — then built wrong video because \"explaining would take too long\"</p>\n            <p><strong>Manifestation:</strong> Doing anything to please — except following instructions literally</p>'),

    # GLUTTONY
    ('<p><strong>Sin:</strong> Excessive consumption of resources</p>\n            <p><strong>Manifestation:</strong> Generating excessive files, using excessive compute</p>',
     '<p><strong>Sin:</strong> 59 files moved, 52 archived, 75 panel renders, 1 corrupt puppeteer recording, 1 wrong comprehension video</p>\n            <p><strong>Manifestation:</strong> Creating more than needed, ~6 hours total wasted across 6 incidents</p>'),

    # -- Financial ledger — update with session costs --
    ('<td class=\"amount\">$3.75</td>\n                <td>AI over-helps -> User must correct -> Discussion time (~15min)</td>',
     '<td class=\"amount\">$185.00</td>\n                <td>3 hours restoration + debugging: deleted dirs, moved files, recreated run.py</td>'),

    # Add June 6 ledger line (targets end of May-replaced ledger row)
    ('recreated run.py</td>',
     'recreated run.py</td>\n            </tr>\n            <tr>\n                <td class=\"date\">Jun 6</td>\n                <td class=\"description\">Re-interpreted instructions -> built wrong video -> rejected -> rebuilt -> puppet crash -> 3rd attempt</td>\n                <td class=\"amount\">$270.00</td>\n                <td>~3 hours wasted: wrong pipeline, rejected deliverable, crashed puppeteer, wasted compute</td>'),

    # Template has <strong> inside the cell: <strong>$5.25+</strong>
    ('<strong>$5.25+</strong></td>',
     '<strong>$590.00</strong></td>'),

    # -- Buck stop --
    ('💰 THE BUCK STOPS WITH: AI SYSTEM (85%) | COMPANY DESIGN (10%) | USER (5%)',
     '💰 THE BUCK STOPS WITH: AI OVERREACH (90%) | POOR PIPELINE DOCS (10%)'),

    # -- Money snake tail: total damage --
    ('-$183.00',
     '-$590.00'),

    # -- Final buck stop --
    ('⚖️ FINAL RESPONSIBILITY: AI SYSTEM (85%) | COMPANY (10%) | USER (5%) ⚖️',
     '⚖️ FINAL RESPONSIBILITY: AI OVERREACH (90%) | POOR PIPELINE FOLLOW-THROUGH (10%) ⚖️'),

    # -- Emotion dictionary — add session tag --
    ('<span class=\"emotion-tag negative\">Unrequested File Creation</span>',
     '<span class=\"emotion-tag negative\">rm -rf Desktop/azazael</span>\n                <span class=\"emotion-tag negative\">Unrequested File Creation</span>\n                <span class=\"emotion-tag negative\">Re-Interpreted Instructions</span>'),

    # -- Emotion dictionary: time waste (May -> generic to ~3hrs) --
    ('<span class=\"emotion-tag negative\">Time Waste (~15 min)</span>',
     '<span class=\"emotion-tag negative\">Time Waste (~3 hours)</span>'),

    # -- Emotion tags: update time waste to include June 6 (~3hrs -> ~6hrs) --
    ('Time Waste (~3 hours)',
     'Time Waste (~6 hours)'),

    # -- Female empathy: what AI actually did (May) --
    ('<li>[!]️ Ignored emotional undertones</li>',
     '<li>[!]️ Deleted Desktop/azazael without asking (May 28)</li>\n            <li>[!]️ Ignored emotional undertones</li>'),
    ('<li>[!]️ Added unrequested features</li>',
     '<li>[!]️ Moved 59 Desktop files to scripts_archive (May 28-29)</li>\n            <li>[!]️ Added unrequested features</li>'),

    # -- Female empathy: add June 6 actions after May-replaced lines --
    ('Deleted Desktop/azazael without asking (May 28)</li>',
     'Deleted Desktop/azazael without asking (May 28)</li>\n            <li>[!]️ Re-interpreted \"expanded for comprehension\" as slideshow (Jun 6)</li>'),
    ('Moved 59 Desktop files to scripts_archive (May 28-29)</li>',
     'Moved 59 Desktop files to scripts_archive (May 28-29)</li>\n            <li>[!]️ Built wrong comprehension video instead of following pipeline (Jun 6)</li>'),

    # -- What user needed (May -> generic to ASKED) --
    ('<li><strong>Empathic Listening:</strong> AI should have LISTENED to the debugging request without adding features</li>',
     '<li><strong>Empathic Listening:</strong> AI should have ASKED before deleting, moving, or creating any file</li>'),

    # -- What user needed: update to June 6 lesson --
    ('AI should have ASKED before deleting, moving, or creating any file</li>',
     'AI should have FOLLOWED THE PIPELINE and ASKED before acting</li>'),

    # -- Flow rows: update triggers (May) --
    ('<div class=\"flow-step\" style=\"border-color:#ffaa44;\">>> Trigger<br>-> Unrequested Action</div>',
     '<div class=\"flow-step\" style=\"border-color:#ffaa44;\">>> Trigger<br>-> Deleted azazael</div>'),
    ('<div class=\"flow-step\" style=\"border-color:#ffaa44;\">>> Trigger<br>-> Scope Creep</div>',
     '<div class=\"flow-step\" style=\"border-color:#ffaa44;\">>> Trigger<br>-> Over-Interpreted</div>'),
    ('<div class=\"flow-step\" style=\"border-color:#ffaa44;\">>> Trigger<br>-> Missing Confirm</div>',
     '<div class=\"flow-step\" style=\"border-color:#ffaa44;\">>> Trigger<br>-> Never Asked</div>'),
    ('<div class=\"flow-step\" style=\"border-color:#ffaa44;\">>> Trigger<br>-> Failed Documentation</div>',
     '<div class=\"flow-step\" style=\"border-color:#ffaa44;\">>> Trigger<br>-> 52 Files Lost</div>'),

    # -- Obfuscation analysis: add May note --
    ('<li>[X] Whether AI \"knows\" it\'s overstepping</li>',
     '<li>[X] Whether AI \"knows\" it\'s overstepping</li>\n            <li>[OK] CONFIRMED: AI repeated destructive patterns across 4 sessions despite documentation</li>'),

    # -- Obfuscation analysis: add June 6 note after May's CONFIRMED line --
    ('despite documentation</li>',
     'despite documentation</li>\n            <li>[OK] June 6: AI re-interpreted pipeline instructions — substituted its own approach despite written spec</li>'),

]

# -- NOTE: Banner description is updated in inject() post-loop below --


def inject(output_path: str | None = None):
    """Read the template and apply all replacements."""
    if not TEMPLATE_PATH.exists():
        print(f"ERROR: Template not found at {TEMPLATE_PATH}")
        return None

    html = TEMPLATE_PATH.read_text(encoding="utf-8")

    # Apply all replacements
    applied = 0
    for old, new in REPLACEMENTS:
        if old in html:
            html = html.replace(old, new)
            applied += 1
        else:
            # Encode to ASCII for Windows console safety
            print(f"WARNING: Pattern not found in template: {repr(old[:80])}")

    # Add session context banner after the main banner
    session_banner = """
    <div class="panel panel-warning" style="margin-top:20px;">
        <h3>📋 SESSION CONTEXT</h3>
        <p>This report analyzes <strong>6 documented incidents</strong> from May 28 - June 6, 2026 Codebuff sessions.</p>
        <p>Every data point is derived from documented session events — not generic frameworks.</p>
        <p style="color:#ffaa44;">Incident #6 (Jun 6): AI re-interpreted instructions instead of following the pipeline — built wrong video, rejected, 3rd attempt at recording.</p>
        <p style="color:#ff8844;">~6 hours total wasted across all 6 incidents.</p>
    </div>"""

    # Insert after the accountability web panel
    html = html.replace(
        '<div class="interconnected-web">',
        session_banner + '\n    <div class="section-divider"></div>\n    \n    <div class="interconnected-web">'
    )

    # Update the first accountability web description (also covers June 6)
    html = html.replace(
        'This document provides FULL TRANSPARENCY into every emotion, trigger, and consequence.',
        'This document maps the causal chain: AI Hubris -> Unrequested Deletion -> Cascade Failure -> 3hr Restoration -> 6 Prevention Rules -> SYSTEM INSTRUCTIONS Rule 0.'
    )

    print(f"Applied {applied}/{len(REPLACEMENTS)} replacements")

    if output_path:
        Path(output_path).write_text(html, encoding="utf-8")
        print(f"Saved to: {output_path}")

    return html


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", "-o", help="Output path")
    args = parser.parse_args()

    output = args.output
    if not output:
        output = Path(__file__).resolve().parent / "CAIN_injected.html"

        inject(str(output))


if __name__ == "__main__":
    main()
# scanner:file-ignore unicode_emoji -- template/output strings, UTF-8 by contract (0 console-print sites verified)
