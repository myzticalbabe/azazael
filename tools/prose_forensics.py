#!/usr/bin/env python
# coding: utf-8
"""Measure a public text's prose: the numbers an impression cannot argue with.

WHY A TOOL AND NOT A DESCRIPTION
================================
"The style is repetitive and conversational" is not an audit, it is a mood. This prints the
quantities that make the claim falsifiable -- sentence-length distribution, pronoun balance,
negation and intensifier rates, sentence-initial conjunctions, anaphora -- and writes them as
JSON so two texts can be compared and the comparison re-run by anyone.

WHAT IT REFUSES TO DO
=====================
It does not judge truth, character or intent. It counts surface features of a text it was given.
The attribution question (who wrote/delivered it) is *not* answered here and must be recorded by
the caller: a transcribed speech and a staff-drafted message are different corpora even when they
carry the same name.

USAGE
=====
    python tools/prose_forensics.py --url https://www.whitehouse.gov/remarks/2025/01/the-inaugural-address/ \
        --label inaugural_2025 --out .prose/inaugural_2025.json
    python tools/prose_forensics.py --file .prose/text.txt --label x --out .prose/x.json
    python tools/prose_forensics.py --compare .prose/a.json .prose/b.json

Network access is urllib + stdlib only: this tree has been burned by a dependency before, and a
measurement tool that cannot run offline on saved text is not a tool, it is an outage.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, List, Tuple

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) prose_forensics/1.0 "
              "(text measurement; contact: local)")

PRONOUNS = {
    "first_singular": {"i", "me", "my", "mine", "myself"},
    "first_plural": {"we", "us", "our", "ours", "ourselves"},
    "second": {"you", "your", "yours", "yourself", "yourselves"},
    "third_plural": {"they", "them", "their", "theirs"},
}
NEGATIONS = {"not", "no", "never", "nobody", "nothing", "none", "cannot", "can't", "won't",
             "don't", "doesn't", "didn't", "isn't", "aren't", "wasn't", "weren't", "nor"}
INTENSIFIERS = {"very", "really", "totally", "completely", "absolutely", "extremely", "so",
                "incredibly", "tremendously", "massively", "highly", "deeply"}
DEIXIS = {"now", "today", "tonight", "here", "this", "these", "tomorrow", "yesterday"}
# a closed list, not a parser: an imperative detector that guesses is worse than one that
# under-counts and says so
IMPERATIVES = {"let", "look", "listen", "remember", "think", "imagine", "consider", "believe",
               "mark", "watch", "see", "take", "make", "build", "stop", "keep", "stand", "come",
               "go", "give", "tell", "ask", "be", "do", "never", "don't"}
CONCLUSIVE = {"will", "must", "shall", "going", "gonna", "cannot", "can't"}


class _Text(HTMLParser):
    """Paragraph-aware extraction: a list item and a sentence are not the same sentence."""

    BLOCK = {"p", "br", "div", "h1", "h2", "h3", "h4", "li", "blockquote", "tr"}
    DROP = {"script", "style", "noscript", "nav", "footer", "header"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: List[str] = []
        self.drop = 0

    def handle_starttag(self, tag: str, attrs) -> None:  # type: ignore[no-untyped-def]
        if tag in self.DROP:
            self.drop += 1
        if tag in self.BLOCK:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in self.DROP and self.drop:
            self.drop -= 1
        if tag in self.BLOCK:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.drop:
            self.parts.append(data)


def fetch_text(url: str, timeout: int = 40) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT,
                                                  "Accept": "text/html,*/*"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read()
    charset = response.headers.get_content_charset() or "utf-8"
    html = raw.decode(charset, errors="replace")
    parser = _Text()
    parser.feed(html)
    text = "".join(parser.parts)
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def _syllables(word: str) -> int:
    groups = re.findall(r"[aeiouy]+", word.lower())
    count = len(groups)
    if word.lower().endswith("e") and count > 1:
        count -= 1
    return max(1, count)


STAGE_DIRECTIONS = ("Applause", "Laughter", "Inaudible", "Crosstalk", "Boos", "Cheers",
                     "Chanting", "Chants", "Jeers", "Heckling")


def strip_stage(text: str) -> Tuple[str, int]:
    """Remove transcription cues such as (Applause.) -- they are the room, not the prose.

    Measured on the 2025 inaugural: 56 stage directions in a 179-sentence transcript. Left in,
    they are 56 one-word sentences and every sentence statistic is wrong in the same direction.
    """
    removed = 0
    for cue in STAGE_DIRECTIONS:
        pattern = re.compile(r"\s*\(\s*" + cue + r"\.?\s*\)", re.IGNORECASE)
        text, n = pattern.subn("", text)
        removed += n
    # a bare ALL-CAPS cue on its own line, e.g. "(APPLAUSE)"
    text = re.sub(r"\n\s*\((?:[A-Z][A-Za-z ]{2,20})\.\)\s*\n", "\n", text)
    return text, removed


def measure(text: str, label: str = "", strip_cues: bool = False) -> Dict[str, Any]:
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    cues = 0
    if strip_cues:
        text, cues = strip_stage(text)
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    words = re.findall(r"[A-Za-z][A-Za-z'-]*", text)
    lower = [w.lower() for w in words]
    per_1000 = 1000.0 / max(len(words), 1)

    def rate(bag: set) -> float:
        return round(sum(1 for w in lower if w in bag) * per_1000, 2)

    lengths = [len(re.findall(r"[A-Za-z][A-Za-z'-]*", s)) for s in sentences]
    lengths = [n for n in lengths if n > 0]
    ordered = sorted(lengths)
    median = ordered[len(ordered) // 2] if ordered else 0
    p90 = ordered[int(len(ordered) * 0.9)] if ordered else 0

    initials = [re.findall(r"[A-Za-z']+", s)[:1] for s in sentences]
    initials = [w[0].lower() for w in initials if w]
    runs: List[Tuple[str, int]] = []
    for token in initials:
        if runs and runs[-1][0] == token:
            runs[-1] = (token, runs[-1][1] + 1)
        else:
            runs.append((token, 1))
    longest_run = max((n for _t, n in runs), default=0)

    trigrams: Dict[str, int] = {}
    for i in range(len(lower) - 2):
        key = " ".join(lower[i:i + 3])
        trigrams[key] = trigrams.get(key, 0) + 1
    top_trigrams = sorted(trigrams.items(), key=lambda kv: (-kv[1], kv[0]))[:8]

    counts: Dict[str, int] = {}
    for w in lower:
        counts[w] = counts.get(w, 0) + 1
    stop = {"the", "a", "an", "to", "of", "and", "in", "that", "is", "it", "we", "i", "our",
            "will", "be", "for", "on", "as", "this", "are", "with", "you", "they", "not", "at",
            "have", "has", "was", "from", "by", "but", "or", "so", "all", "their"}
    content = [(w, c) for w, c in counts.items() if w not in stop and len(w) > 2]
    content.sort(key=lambda kv: (-kv[1], kv[0]))

    syllables = sum(_syllables(w) for w in lower)
    asl = (len(words) / len(sentences)) if sentences else 0.0
    asw = (syllables / len(words)) if words else 1.0
    flesch = 206.835 - 1.015 * asl - 84.6 * asw

    return {
        "label": label or "unnamed",
        "words": len(words),
        "sentences": len(sentences),
        "stage_directions_removed": cues,
        "unique_words": len(counts),
        "type_token_ratio": round(len(counts) / max(len(words), 1), 4),
        "hapax_ratio": round(sum(1 for c in counts.values() if c == 1) / max(len(counts), 1), 4),
        "sentence_len": {"mean": round(asl, 2), "median": median, "p90": p90,
                         "max": max(lengths) if lengths else 0,
                         "pct_under_9": round(100.0 * sum(1 for n in lengths if n <= 8)
                                              / max(len(lengths), 1), 1),
                         "pct_over_39": round(100.0 * sum(1 for n in lengths if n >= 40)
                                              / max(len(lengths), 1), 1)},
        "pronouns_per_1000": {group: rate(bag) for group, bag in PRONOUNS.items()},
        "negation_per_1000": rate(NEGATIONS),
        "intensifier_per_1000": rate(INTENSIFIERS),
        "deixis_per_1000": rate(DEIXIS),
        "modals_per_1000": rate(CONCLUSIVE),
        "very_count": counts.get("very", 0),
        "superlatives": {"most": counts.get("most", 0),
                         "greatest": counts.get("greatest", 0),
                         "best": counts.get("best", 0),
                         "ever": counts.get("ever", 0)},
        "sentence_initial": {
            "and": initials.count("and"), "but": initials.count("but"),
            "so": initials.count("so"), "but_pct": round(100.0 * initials.count("but")
                                                        / max(len(initials), 1), 1),
            "longest_same_starter_run": longest_run,
        },
        "imperatives": {"count": sum(1 for w in initials if w in IMPERATIVES),
                        "share_pct": round(100.0 * sum(1 for w in initials if w in IMPERATIVES)
                                           / max(len(initials), 1), 1)},
        "punctuation": {"em_dash": text.count("\u2014"), "hyphen_dash": text.count(" -- "),
                        "parentheses": text.count("("), "questions": text.count("?"),
                        "exclamations": text.count("!")},
        "flesch_reading_ease": round(flesch, 1),
        "top_content_words": content[:12],
        "top_trigrams": top_trigrams,
        "first_sentence": sentences[0] if sentences else "",
        "last_sentence": sentences[-1] if sentences else "",
    }


def show(result: Dict[str, Any]) -> None:
    print("%s: %d words, %d sentences, mean %.2f / median %d / p90 %d"
          % (result["label"], result["words"], result["sentences"],
             result["sentence_len"]["mean"], result["sentence_len"]["median"],
             result["sentence_len"]["p90"]))
    print("  %.1f%% of sentences <= 8 words, %.1f%% >= 40; TTR %.3f"
          % (result["sentence_len"]["pct_under_9"], result["sentence_len"]["pct_over_39"],
             result["type_token_ratio"]))
    pronouns = ", ".join("%s %s" % (k, v) for k, v in result["pronouns_per_1000"].items())
    print("  per 1000 words: %s" % pronouns)
    print("  negation %s, intensifier %s, deixis %s, modals %s, very x%d"
          % (result["negation_per_1000"], result["intensifier_per_1000"],
             result["deixis_per_1000"], result["modals_per_1000"], result["very_count"]))
    print("  sentence-initial: and %d, but %d (%s%%), longest same-starter run %d"
          % (result["sentence_initial"]["and"], result["sentence_initial"]["but"],
             result["sentence_initial"]["but_pct"],
             result["sentence_initial"]["longest_same_starter_run"]))
    print("  Flesch %.1f; top words %s"
          % (result["flesch_reading_ease"],
             ", ".join("%s(%d)" % (w, c) for w, c in result["top_content_words"][:8])))


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Measure the prose of a public text.")
    parser.add_argument("--url", default="")
    parser.add_argument("--file", default="")
    parser.add_argument("--label", default="")
    parser.add_argument("--out", default="")
    parser.add_argument("--strip-stage", action="store_true",
                        help="remove (Applause.) style cues before measuring",
                        )
    parser.add_argument("--compare", nargs="*", default=[])
    parser.add_argument("--start-after", default="",
                        help="begin after this literal marker (refuses if absent)")
    parser.add_argument("--end-before", default="",
                        help="end before this literal marker (refuses if absent)")
    args = parser.parse_args(argv)

    if args.compare:
        loaded = [json.loads(Path(p).read_text(encoding="utf-8")) for p in args.compare]
        print("%-22s %6s %6s %6s %6s %6s %6s %6s" % ("text", "words", "mean", "we", "i",
                                                     "not", "intens", "flesch"))
        for result in loaded:
            print("%-22s %6d %6.2f %6.1f %6.1f %6.1f %6.1f %6.1f"
                  % (result["label"], result["words"], result["sentence_len"]["mean"],
                     result["pronouns_per_1000"]["first_plural"],
                     result["pronouns_per_1000"]["first_singular"],
                     result["negation_per_1000"], result["intensifier_per_1000"],
                     result["flesch_reading_ease"]))
        return 0

    if args.file:
        text = Path(args.file).read_text(encoding="utf-8")
    elif args.url:
        text = fetch_text(args.url)
    else:
        parser.print_help()
        return 2

    # Trimming is explicit and refusable. Site chrome (nav, title, date, footer) is prose too,
    # and measuring it as if it were the speech is exactly the kind of quiet miscount that makes
    # a number untrustworthy. If a marker is missing, stop rather than measure everything.
    for marker, before in ((args.start_after, False), (args.end_before, True)):
        if not marker:
            continue
        index = text.find(marker)
        if index < 0:
            print("REFUSED: marker %r is not in the fetched text -- not measuring the whole page"
                  % marker, file=sys.stderr)
            return 3
        text = text[index + len(marker):] if not before else text[:index]
    result = measure(text, args.label or args.file or args.url, strip_cues=args.strip_stage)
    show(result)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=1), encoding="utf-8")
        print("wrote %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
