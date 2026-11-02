#!/usr/bin/env python3
"""quote_norm.py - Quote normalization and basis detection for proof verification.

Provides canonical normalization functions for comparing quotes against raw evidence.
"""

import re
import html
import unicodedata
import sys
from typing import List, Tuple, Optional
from enum import Enum
from dataclasses import dataclass

class QuoteBasis(Enum):
    VERBATIM = "verbatim"
    MARKUP_FLATTENED = "markup-flattened"
    WHITESPACE_NORMALIZED = "whitespace-normalized"
    MARKUP_FLATTENED_MOJIBAKE = "markup-flattened+mojibake"
    SUBSTRING = "substring"  # quote is substring of normalized raw
    FUZZY = "fuzzy"  # high similarity but not exact

@dataclass
class NormalizationResult:
    original: str
    normalized: str
    basis: QuoteBasis
    confidence: float
    details: dict

# ============================================================
# CORE NORMALIZATION FUNCTIONS
# ============================================================

def normalize_unicode(text: str) -> str:
    """Normalize unicode: NFC form, replace compatibility chars."""
    return unicodedata.normalize('NFC', text)

def decode_entities(text: str) -> str:
    """Decode HTML/XML numeric and named entities."""
    # Named entities
    text = html.unescape(text)
    # Numeric entities (&#1234; &#x1F4;)
    text = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), text)
    text = re.sub(r'&#x([0-9a-fA-F]+);', lambda m: chr(int(m.group(1), 16)), text)
    return text

def strip_markup(text: str, keep_content: bool = True) -> str:
    """Strip XML/HTML tags, optionally keeping content."""
    if keep_content:
        # Replace tags with space to preserve word boundaries
        text = re.sub(r'<[^>]+>', ' ', text)
    else:
        text = re.sub(r'<[^>]+>', '', text)
    return text

def normalize_whitespace(text: str, aggressive: bool = False) -> str:
    """Normalize whitespace."""
    # Replace all whitespace sequences with single space
    text = re.sub(r'\s+', ' ', text)
    # Trim
    text = text.strip()
    if aggressive:
        # Also remove spaces around punctuation
        text = re.sub(r'\s+([,.!?;:])', r'\1', text)
        text = re.sub(r'([([{"])\s+', r'\1', text)
        text = re.sub(r'\s+([)\]}"])', r'\1', text)
    return text

def remove_control_chars(text: str) -> str:
    """Remove control characters except newline/tab."""
    return ''.join(ch for ch in text if ch == '\n' or ch == '\t' or ord(ch) >= 32)

def detect_mojibake(text: str) -> Tuple[bool, List[str]]:
    """Detect common mojibake patterns."""
    patterns = [
        # UTF-8 interpreted as Latin-1
        ('Ã©', 'é'), ('Ã¨', 'è'), ('Ã§', 'ç'), ('Ã ', 'à'),
        ('Ã±', 'ñ'), ('Ã¼', 'ü'), ('Ã¶', 'ö'), ('Ã¤', 'ä'),
        ('Ã‰', 'É'), ('Ãˆ', 'È'), ('Ã‡', 'Ç'), ('Ã€', 'À'),
        ('Ã', 'Ñ'), ('Ã', 'Ö'), ('Ã', 'Ä'),
        # Smart quotes
        ('â€œ', '"'), ('â€', '"'), ('â€™', "'"), ('â€"', '—'),
        ("â€˜", "'"), ("â€¢", "•"),
        # Other common
        ("â€", ""), ("â€", ""),
    ]
    found = []
    for bad, good in patterns:
        if bad in text:
            found.append(bad)
    return len(found) > 0, found

def fix_mojibake(text: str) -> str:
    """Fix common mojibake by re-encoding."""
    try:
        # Try: text was UTF-8 decoded as Latin-1
        return text.encode('latin-1').decode('utf-8')
    except Exception as exc:
        note_failure("03_tooling/quote_norm.py", exc)
        pass
    return text

# ============================================================
# MAIN NORMALIZATION PIPELINES
# ============================================================

def pipeline_verbatim(text: str) -> str:
    """Minimal normalization for verbatim matching."""
    return remove_control_chars(text)

def pipeline_markup_flattened(text: str) -> str:
    """Full markup flattening pipeline."""
    text = normalize_unicode(text)
    text = decode_entities(text)
    text = strip_markup(text, keep_content=True)
    text = normalize_whitespace(text)
    text = remove_control_chars(text)
    return text

def pipeline_whitespace_normalized(text: str) -> str:
    """Aggressive whitespace normalization."""
    text = pipeline_markup_flattened(text)
    text = normalize_whitespace(text, aggressive=True)
    return text

def pipeline_markup_flattened_mojibake(text: str) -> Tuple[str, bool]:
    """Markup flattened with mojibake detection/fix."""
    text = pipeline_markup_flattened(text)
    has_mojibake, patterns = detect_mojibake(text)
    if has_mojibake:
        fixed = fix_mojibake(text)
        return fixed, True
    return text, False

# ============================================================
# QUOTE BASIS DETECTION
# ============================================================

def find_quote_in_raw(quote: str, raw: str) -> List[Tuple[int, int, QuoteBasis]]:
    """Find all occurrences of quote in raw with basis detection."""
    matches = []
    
    # Try each pipeline
    pipelines = [
        (QuoteBasis.VERBATIM, pipeline_verbatim),
        (QuoteBasis.MARKUP_FLATTENED, pipeline_markup_flattened),
        (QuoteBasis.WHITESPACE_NORMALIZED, pipeline_whitespace_normalized),
        (QuoteBasis.MARKUP_FLATTENED_MOJIBAKE, lambda t: pipeline_markup_flattened_mojibake(t)[0]),
    ]
    
    for basis, pipeline in pipelines:
        norm_quote = pipeline(quote)
        norm_raw = pipeline(raw)
        
        if not norm_quote:
            continue
            
        # Find all occurrences
        start = 0
        while True:
            idx = norm_raw.find(norm_quote, start)
            if idx == -1:
                break
            matches.append((idx, idx + len(norm_quote), basis))
            start = idx + 1
    
    return matches

def detect_quote_basis(quote: str, raw: str) -> NormalizationResult:
    """Detect the best matching basis for quote in raw."""
    matches = find_quote_in_raw(quote, raw)
    
    if not matches:
        return NormalizationResult(
            original=quote,
            normalized=quote,
            basis=QuoteBasis.FUZZY,
            confidence=0.0,
            details={"matches": 0}
        )
    
    # Prefer verbatim > markup-flattened > whitespace > markup+mojibake
    priority = {
        QuoteBasis.VERBATIM: 4,
        QuoteBasis.MARKUP_FLATTENED: 3,
        QuoteBasis.WHITESPACE_NORMALIZED: 2,
        QuoteBasis.MARKUP_FLATTENED_MOJIBAKE: 1,
    }
    
    best = max(matches, key=lambda m: priority.get(m[2], 0))
    

try:
    from CORE.failure_ledger import note_failure
except ImportError:                               # never break the host
    def note_failure(where, exc=None):
        pass  # ledger missing; the swallow is still named at the call site

    return NormalizationResult(
        original=quote,
        normalized=quote,  # The matched portion would be extracted
        basis=best[2],
        confidence=0.9,  # High confidence for exact match
        details={
            "match_position": best[0],
            "match_length": best[1] - best[0],
            "total_matches": len(matches),
            "all_bases": [m[2].value for m in matches]
        }
    )

def grade_quote_basis(quote: str, raw_content: str) -> QuoteBasis:
    """Quick grading function for verify_proofs integration."""
    result = detect_quote_basis(quote, raw_content)
    return result.basis

# ============================================================
# BATCH PROCESSING
# ============================================================

def normalize_batch(quotes: List[str], raw: str) -> List[NormalizationResult]:
    """Normalize multiple quotes against same raw content."""
    return [detect_quote_basis(q, raw) for q in quotes]

def compute_similarity(a: str, b: str) -> float:
    """Compute Jaccard similarity of word sets."""
    words_a = set(normalize_whitespace(a).lower().split())
    words_b = set(normalize_whitespace(b).lower().split())
    if not words_a or not words_b:
        return 0.0
    return len(words_a & words_b) / len(words_a | words_b)

def find_best_match(quote: str, candidates: List[str]) -> Tuple[int, float]:
    """Find best matching candidate for quote."""
    best_idx = -1
    best_score = 0.0
    for i, cand in enumerate(candidates):
        score = compute_similarity(quote, cand)
        if score > best_score:
            best_score = score
            best_idx = i
    return best_idx, best_score

# ============================================================
# CLI
# ============================================================

def main():
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description='Quote normalization and basis detection')
    parser.add_argument('quote', nargs='?', help='Quote to normalize')
    parser.add_argument('--raw', help='Raw content to match against')
    parser.add_argument('--raw-file', help='File containing raw content')
    parser.add_argument('--pipeline', choices=['verbatim', 'markup', 'whitespace', 'mojibake', 'detect'],
                        default='detect', help='Normalization pipeline')
    parser.add_argument('--batch', help='JSONL file with quotes to process')
    parser.add_argument('-o', '--output', help='Output file')
    parser.add_argument('--json', action='store_true', help='JSON output')
    
    args = parser.parse_args()
    
    if args.batch:
        # Batch process
        with open(args.batch, encoding="utf-8") as f:
            quotes = [json.loads(line).get('quote', '') for line in f if line.strip()]
        
        raw = ""
        if args.raw_file:
            with open(args.raw_file, encoding="utf-8") as f:
                raw = f.read()
        elif args.raw:
            raw = args.raw
        
        results = normalize_batch(quotes, raw)
        
        output = [r.__dict__ for r in results]
        if args.json:
            print(json.dumps(output, indent=2))
        else:
            for r in output:
                print(f"{r['basis']}: {r['original'][:80]}...")
    
    elif args.quote and args.raw:
        # Single quote
        raw = args.raw
        if args.raw_file:
            with open(args.raw_file, encoding="utf-8") as f:
                raw = f.read()
        
        if args.pipeline == 'verbatim':
            result = pipeline_verbatim(args.quote)
        elif args.pipeline == 'markup':
            result = pipeline_markup_flattened(args.quote)
        elif args.pipeline == 'whitespace':
            result = pipeline_whitespace_normalized(args.quote)
        elif args.pipeline == 'mojibake':
            result, _ = pipeline_markup_flattened_mojibake(args.quote)
        elif args.pipeline == 'detect':
            result = detect_quote_basis(args.quote, raw)
        else:
            result = detect_quote_basis(args.quote, raw)
        
        if args.json:
            if hasattr(result, '__dict__'):
                # Convert enum to value for JSON serialization
                d = result.__dict__.copy()
                if 'basis' in d and hasattr(d['basis'], 'value'):
                    d['basis'] = d['basis'].value
                print(json.dumps(d, indent=2))
            else:
                print(json.dumps({"normalized": result}, indent=2))
        else:
            if hasattr(result, 'basis'):
                print(f"Basis: {result.basis.value}")
                print(f"Confidence: {result.confidence}")
                print(f"Details: {result.details}")
            else:
                print(f"Normalized: {result}")
    
    else:
        parser.print_help()
        return 1
    
    return 0

if __name__ == '__main__':
    import json
    sys.exit(main())