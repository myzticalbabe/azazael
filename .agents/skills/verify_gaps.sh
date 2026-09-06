#!/bin/bash
# verify_gaps.sh — Post-session gap-count consistency check
# Canonical: 50 total, 10 resolved, 40 open (as of Gap #50 addition, Aug 1 2026)
# 34 checks across 14+ investigation files
# Usage: bash .agents/skills/verify_gaps.sh

echo "=== GAP COUNT VERIFICATION (34 checks) ==="
echo ""

PASS=0
FAIL=0

check() {
  local file=$1
  local pattern=$2
  local label=$3
  if grep -qE "$pattern" "$file" 2>/dev/null; then
    echo "  ✅ $label"
    ((PASS++))
  else
    echo "  ❌ FAIL: $label NOT found in $file"
    ((FAIL++))
  fi
}

check_not() {
  local file=$1
  local pattern=$2
  local label=$3
  if grep -qE "$pattern" "$file" 2>/dev/null; then
    echo "  ❌ STALE: $label FOUND in $file — remove it!"
    grep -nE "$pattern" "$file"
    ((FAIL++))
  else
    echo "  ✅ $label"
    ((PASS++))
  fi
}

# =============================================================================
# CANONICAL COUNTS: 40 open, 10 resolved, 50 total
# =============================================================================
echo "Canonical counts (must be: 40 open, 10 resolved, 50 total)"
echo ""

# --- 1-6: INVESTIGATION_GAPS.html (canonical source) ---
echo "INVESTIGATION_GAPS.html (canonical):"
check "INVESTIGATION_GAPS.html" "40 open" "Gaps file says 40 open"
check "INVESTIGATION_GAPS.html" "10 resolved" "Gaps file says 10 resolved"
check_not "INVESTIGATION_GAPS.html" "39 open" "No stale 39 open reference"
check_not "INVESTIGATION_GAPS.html" "42 open" "No stale 42 open reference"
check "INVESTIGATION_GAPS.html" "50 total" "Gaps file says 50 total"
check_not "INVESTIGATION_GAPS.html" "49 total" "No stale 49 total reference"
echo ""

# --- 7-8: INVESTIGATION_GAPS.html medium-gap sub-count ---
echo "INVESTIGATION_GAPS.html (medium-gap sub-count):"
check "INVESTIGATION_GAPS.html" "14 Open" "Medium header says 14 Open"
check_not "INVESTIGATION_GAPS.html" "13 open.*medium" "No stale 13 open medium count"
echo ""

# --- 9-10: HIDDEN_NETWORK.html ---
echo "HIDDEN_NETWORK.html:"
check "HIDDEN_NETWORK.html" "40 open" "HIDDEN_NETWORK says 40 open"
check "HIDDEN_NETWORK.html" "10 resolved" "HIDDEN_NETWORK says 10 resolved"
echo ""

# --- 11: LEGAL_REFERRAL_MEMO.html ---
echo "LEGAL_REFERRAL_MEMO.html:"
check "LEGAL_REFERRAL_MEMO.html" "40 open" "LEGAL_REFERRAL_MEMO says 40 open"
echo ""

# --- 12-14: STRATEGY_OVERVIEW.html ---
echo "STRATEGY_OVERVIEW.html:"
check "STRATEGY_OVERVIEW.html" "40 open" "STRATEGY_OVERVIEW says 40 open"
check "STRATEGY_OVERVIEW.html" "10 resolved" "STRATEGY_OVERVIEW says 10 resolved"
check_not "STRATEGY_OVERVIEW.html" "39 of 49" "No stale 39 of 49 reference"
echo ""

# --- 15-16: COMPLAINT_LETTER.html ---
echo "COMPLAINT_LETTER.html:"
check "COMPLAINT_LETTER.html" "40 of 50 gaps remain open" "COMPLAINT_LETTER says 40 of 50"
check_not "COMPLAINT_LETTER.html" "39 of 49" "No stale 39 of 49 reference"
echo ""

# --- 17-18: COMPLAINT_LETTER_REDACTED.html ---
echo "COMPLAINT_LETTER_REDACTED.html:"
check "COMPLAINT_LETTER_REDACTED.html" "40 of 50 gaps remain open" "REDACTED says 40 of 50"
check_not "COMPLAINT_LETTER_REDACTED.html" "39 of 49" "No stale 39 of 49 reference"
echo ""

# --- 19: COMPLAINT_AGENCY_LETTER.txt ---
echo "COMPLAINT_AGENCY_LETTER.txt:"
check "COMPLAINT_AGENCY_LETTER.txt" "40 of 50 gaps remain open" "AGENCY_LETTER says 40 of 50"
echo ""

# --- 20: EVIDENCE_LOCATIONS.html ---
echo "EVIDENCE_LOCATIONS.html:"
check "EVIDENCE_LOCATIONS.html" "40 open gaps mapped" "EVIDENCE_LOCATIONS says 40 open"
echo ""

# --- 21: CRITICAL_GAP_EXECUTION_CHECKLIST.html ---
echo "CRITICAL_GAP_EXECUTION_CHECKLIST.html:"
check "CRITICAL_GAP_EXECUTION_CHECKLIST.html" "40 open" "CHECKLIST says 40 open"
echo ""

# --- 22-24: README.md ---
echo "README.md:"
check "README.md" "40 of 50 gaps open" "README says 40 of 50"
check "README.md" "50 gaps" "README says 50 gaps"
check_not "README.md" "39 of 49" "No stale 39 of 49 reference"
echo ""

# --- 25-27: MOLTBOOK_AGENT_SETUP.html ---
echo "MOLTBOOK_AGENT_SETUP.html:"
check "MOLTBOOK_AGENT_SETUP.html" "50 gaps identified" "MOLTBOOK says 50 gaps identified"
check "MOLTBOOK_AGENT_SETUP.html" "40 open" "MOLTBOOK says 40 open"
check "MOLTBOOK_AGENT_SETUP.html" "10 resolved" "MOLTBOOK says 10 resolved"
echo ""

# --- 28: .agents/skills/investigation-document-construction.md ---
echo ".agents/skills/investigation-document-construction.md:"
check ".agents/skills/investigation-document-construction.md" "50 gaps" "Skills doc says 50 gaps"
echo ""

# --- 29: FUNDING_REVIEW.html ---
echo "FUNDING_REVIEW.html:"
check_not "FUNDING_REVIEW.html" "39 open|42 open|49 gap" "No stale gap counts (39/42/49)"
echo ""

# --- 30: CCBHC_REGIME_CHANGE.html ---
echo "CCBHC_REGIME_CHANGE.html:"
check_not "CCBHC_REGIME_CHANGE.html" "39 open|42 open|49 gap" "No stale gap counts (39/42/49)"
echo ""

# --- 31: CONSOLIDATED_SCROLL.html ---
echo "CONSOLIDATED_SCROLL.html:"
check_not "CONSOLIDATED_SCROLL.html" "39 open|42 open|49 gap" "No stale gap counts (39/42/49)"
echo ""

# --- 32: FORENSIC_EXTRACTION_BLUEPRINT.html ---
echo "FORENSIC_EXTRACTION_BLUEPRINT.html:"
check "FORENSIC_EXTRACTION_BLUEPRINT.html" "125 awards" "FORENSIC_BLUEPRINT says 125 awards (not 51)"
echo ""

# --- 33: IRS_WHISTLEBLOWER_FORM_211.html ---
echo "IRS_WHISTLEBLOWER_FORM_211.html:"
check_not "IRS_WHISTLEBLOWER_FORM_211.html" "39 open|42 open|49 gap" "No stale gap counts (39/42/49)"
echo ""

# --- 34: CC_CONTACTS_MASTER.html ---
echo "CC_CONTACTS_MASTER.html:"
check "CC_CONTACTS_MASTER.html" "46" "CC_CONTACTS_MASTER has 46+ contact count"
echo ""

# =============================================================================
echo "=========================================="
echo "RESULTS: $PASS passed, $FAIL failed"
echo "=========================================="

if [ $FAIL -gt 0 ]; then
  echo ""
  echo "⚠ GAP-COUNT DRIFT DETECTED — fix stale references before committing."
  exit 1
fi

echo ""
echo "✅ All $PASS checks passed — zero stale references across all files."
exit 0
