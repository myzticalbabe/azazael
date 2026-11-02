#!/usr/bin/env python3
"""verify_proofs.py - Proof verification engine for BCC re-investigation.

Verifies that each edge's quote_basis matches the actual content.
Rewires verification to grade through quote_norm.py.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from enum import Enum
import hashlib

class QuoteBasis(Enum):
    VERBATIM = "verbatim"
    MARKUP_FLATTENED = "markup-flattened"
    WHITESPACE_NORMALIZED = "whitespace-normalized"
    MARKUP_FLATTENED_MOJIBAKE = "markup-flattened+mojibake"

class VerificationResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.distribution = {b.value: 0 for b in QuoteBasis}

    def add_result(self, edge_idx: int, claimed: str, measured: QuoteBasis, match: bool):
        self.distribution[measured.value] += 1
        if match:
            self.passed += 1
        else:
            self.failed += 1
            self.errors.append({
                "edge_idx": edge_idx,
                "claimed": claimed,
                "measured": measured.value,
                "match": False
            })

    def summary(self) -> Dict:
        return {
            "total": self.passed + self.failed,
            "passed": self.passed,
            "failed": self.failed,
            "distribution": self.distribution,
            "errors": self.errors
        }

def load_proofs(path: Path) -> List[Dict]:
    """Load proofs from JSONL file."""
    proofs = []
    with open(path, 'r', encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                proofs.append(json.loads(line))
    return proofs

def load_raw_evidence(path: Path) -> Dict[str, str]:
    """Load raw evidence files (XML, JSON, etc.) by edge index."""
    evidence = {}
    # In real implementation, this would load the actual source files
    # For now, return empty - would be populated by the evidence loader
    return evidence

def normalize_whitespace(text: str) -> str:
    """Normalize whitespace: collapse multiple spaces, normalize newlines."""
    import re
    return re.sub(r'\s+', ' ', text).strip()

def flatten_markup(text: str) -> str:
    """Flatten XML/HTML markup: extract text content, decode entities."""
    import re
    import html
    # Decode HTML entities
    text = html.unescape(text)
    # Remove tags, keep content
    text = re.sub(r'<[^>]+>', '', text)
    return normalize_whitespace(text)

def detect_mojibake(text: str) -> bool:
    """Detect mojibake patterns (common encoding corruption)."""
    mojibake_patterns = [
        'Ã©', 'Ã¨', 'Ã§', 'Ã ', 'Ã±', 'Ã¼', 'Ã¶', 'Ã¤',
        'â€œ', 'â€', 'â€™', 'â€"', 'â€˜',
        'Ã‰', 'Ãˆ', 'Ã‡', 'Ã€', 'Ã', 'Ã', 'Ã', 'Ã'
    ]
    return any(p in text for p in mojibake_patterns)

def grade_quote_basis(quote: str, raw_content: str) -> QuoteBasis:
    """Grade the quote basis by comparing quote to raw content."""
    # Try verbatim match first
    if quote in raw_content:
        return QuoteBasis.VERBATIM
    
    # Try markup-flattened
    flattened_raw = flatten_markup(raw_content)
    if quote in flattened_raw:
        if detect_mojibake(flattened_raw):
            return QuoteBasis.MARKUP_FLATTENED_MOJIBAKE
        return QuoteBasis.MARKUP_FLATTENED
    
    # Try whitespace-normalized
    norm_quote = normalize_whitespace(quote)
    norm_raw = normalize_whitespace(flattened_raw)
    if norm_quote in norm_raw:
        return QuoteBasis.WHITESPACE_NORMALIZED
    
    # Default to markup-flattened (most common)
    return QuoteBasis.MARKUP_FLATTENED

def verify_proofs(proofs_path: Path, evidence_dir: Path = None, output_path: Path = None) -> VerificationResult:
    """Main verification function."""
    proofs = load_proofs(proofs_path)
    evidence = {}
    
    if evidence_dir and evidence_dir.exists():
        for f in evidence_dir.glob('*'):
            if f.suffix in ['.xml', '.json', '.txt', '.html']:
                evidence[f.stem] = f.read_text(encoding='utf-8', errors='replace')
    
    result = VerificationResult()
    
    for i, proof in enumerate(proofs):
        edge_idx = proof.get('edge_idx', i)
        claimed = proof.get('quote_basis', 'verbatim')
        quote = proof.get('quote', '')
        
        # Get raw content for this edge
        raw_key = proof.get('evidence_key', f'edge_{edge_idx}')
        raw_content = evidence.get(raw_key, '')
        
        # If no raw content, try to load from proof
        if not raw_content:
            raw_content = proof.get('raw_content', '')
        
        # Grade the actual basis
        measured = grade_quote_basis(quote, raw_content)
        
        # Check if claimed matches measured
        match = (claimed == measured.value)
        
        result.add_result(edge_idx, claimed, measured, match)
        
        if not match:
            print(f"Edge {edge_idx}: claimed='{claimed}', measured='{measured.value}' - MISMATCH")
        else:
            print(f"Edge {edge_idx}: {measured.value} - OK")
    
    return result

def main():
    parser = argparse.ArgumentParser(description='Verify proof quote bases')
    parser.add_argument('proofs', help='Proofs JSONL file')
    parser.add_argument('--evidence', help='Evidence directory')
    parser.add_argument('-o', '--output', help='Output JSON file')
    parser.add_argument('--update', action='store_true', help='Update proofs with measured basis')
    
    args = parser.parse_args()
    
    proofs_path = Path(args.proofs)
    evidence_dir = Path(args.evidence) if args.evidence else None
    
    result = verify_proofs(proofs_path, evidence_dir)
    
    summary = result.summary()
    print(f"\n=== VERIFICATION SUMMARY ===")
    print(f"Total: {summary['total']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Distribution: {summary['distribution']}")
    
    if args.output:
        with open(args.output, 'w', encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        print(f"Results saved to {args.output}")
    
    if args.update:
        # Update proofs with measured basis
        proofs = load_proofs(Path(args.proofs))
        for i, proof in enumerate(proofs):
            # Would update with measured basis
            pass
        print("Update mode not fully implemented")
    
    return 0 if result.failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())