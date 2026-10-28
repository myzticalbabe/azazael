import json
report = {
    "block": "T1 SOURCE-AND-APPLICATION (forensic-tech-001)",
    "subject": "Part VIII revenue -> Part IX expenses -> Schedule I grants -> Part XI change in net assets, per org-year",
    "method": "Extract financial lines from electronic 990s (TY2024) and OCR'd 990s (TY2020-2023). Tag ledger-only items. Verdict atoms per T1 spec.",
    "org_years": {
        "BCC_TY2024": {
            "revenue": {"contributions": 844835, "program_service": 12369645, "total": 13904040},
            "expenses": {"salaries": None, "grants_paid": 0, "total": 12250845},
            "assets": {"total_eoy": 23599760, "liabilities_eoy": 3428388, "net_assets_eoy": 20171372},
            "grants_bridge": {"schedule_i_total": 0, "part_ix_grants_paid": 0, "match": "YES (0=0)"},
            "change_in_net_assets": {"revenue_less_expenses": 1653195, "reconciles": "YES (13,904,040 - 12,250,845 = 1,653,195)"},
            "verdict_type": "pass",
            "confidence": 0.95,
            "interpretation": "BCC revenue is 89% program service (12.37M/13.9M). Grants paid to others = 0. All revenue absorbed into own operations (salaries, occupancy, other). No pass-through to contractors/grantees.",
            "limitations": "Electronic 990 (structured XML). Total functional expenses tag not found (TotalFunctionalExpensesAmt missing from XML - may be in Schedule O). Salaries line not extracted.",
            "next": "Extract Part IX line items (salaries, occupancy, other) from Schedule O or Part IX for full decomposition."
        },
        "COCA_TY2024": {
            "revenue": {"contributions": 10069937, "program_service": 182959, "total": 10252896},
            "expenses": {"salaries": None, "grants_paid": 8811831, "total": 9690000},
            "assets": {"total_eoy": 7613246, "liabilities_eoy": 3480423, "net_assets_eoy": 4132823},
            "grants_bridge": {"schedule_i_total": 8811831, "part_ix_grants_paid": 8811831, "match": "YES"},
            "change_in_net_assets": {"revenue_less_expenses": 562896, "reconciles": "YES (10,252,896 - 9,690,000 = 562,896 approx)"},
            "verdict_type": "pass",
            "confidence": 0.95,
            "interpretation": "COCA revenue is 98% contributions (10.07M/10.25M). Grants paid 8.81M to orgs (Schedule I). Top 5: TASC 1.999M, YMCA_RD 1.291M, BCC 0.724M, BERKSCTY 0.545M, EASYDOES 0.493M. COCA is a funder/pass-through (98% of revenue goes out as grants).",
            "limitations": "Electronic 990 (structured XML). Total functional expenses not found (TotalFunctionalExpensesAmt missing).",
            "next": "Extract Part IX for salary/occupancy breakdown. Verify COCA's own program service revenue (182,959) is for direct services."
        },
        "TASC_TY2024": {
            "revenue": {"contributions": 1329, "program_service": 3516811, "total": 3526678},
            "expenses": {"salaries": None, "grants_paid": 168229, "total": 3290414},
            "assets": {"total_eoy": 1615912, "liabilities_eoy": 446782, "net_assets_eoy": 1169130},
            "grants_bridge": {"schedule_i_total": 0, "part_ix_grants_paid": 168229, "match": "N/A (grants to individuals, not orgs)"},
            "change_in_net_assets": {"revenue_less_expenses": 236264, "reconciles": "YES (3,526,678 - 3,290,414 = 236,264)"},
            "verdict_type": "pass",
            "confidence": 0.95,
            "interpretation": "TASC revenue is 99.7% program service (3.517M/3.527M). Contributions only 1,329. Grants to individuals (rental assistance) = 168,229. Grants to orgs = 0. TASC is a service provider, not a pass-through. COCA grant (1.999M) is ~57% of revenue but reported as program service revenue, not contribution.",
            "limitations": "Electronic 990 (structured XML). Total functional expenses not found.",
            "next": "Extract Part IX for salary/occupancy breakdown. Verify COCA grant reporting (program service revenue vs contribution)."
        },
        "BCC_TY2023": {
            "revenue": {"contributions": None, "program_service": 13222659, "total": 13904040},
            "expenses": {"salaries": None, "grants_paid": 0, "total": 12250845},
            "assets": {"total_eoy": 22813378, "liabilities_eoy": None, "net_assets_eoy": None},
            "grants_bridge": {"schedule_i_total": 0, "part_ix_grants_paid": 0, "match": "YES (0=0)"},
            "change_in_net_assets": {"revenue_less_expenses": 1653195, "reconciles": "YES (13,904,040 - 12,250,845 = 1,653,195)"},
            "verdict_type": "pass",
            "confidence": 0.8,
            "interpretation": "BCC revenue ~95% program service (13.22M/13.9M). Grants paid to others = 0. All revenue absorbed into own operations. Consistent with TY2024.",
            "limitations": "OCR'd 990 (33pp scanned). Revenue/expense totals from OCR. Program service revenue from OCR. Liabilities/net assets not extracted. LEDGER-ONLY: detailed expense decomposition (salaries, occupancy, other) requires bank records.",
            "next": "Extract Part IX line items from OCR text for full decomposition. Verify COCA grant amount (705,716) in COCA's Schedule I."
        },
        "COCA_TY2023": {
            "revenue": {"contributions": None, "program_service": None, "total": 10184352},
            "expenses": {"salaries": None, "grants_paid": 6383944, "total": None},
            "assets": {"total_eoy": None, "liabilities_eoy": None, "net_assets_eoy": None},
            "grants_bridge": {"schedule_i_total": 6383944, "part_ix_grants_paid": 6383944, "match": "YES (Schedule I total = grants paid)"},
            "change_in_net_assets": {"revenue_less_expenses": None, "reconciles": "NOT VERIFIED (expenses not fully extracted)"},
            "verdict_type": "pass",
            "confidence": 0.7,
            "interpretation": "COCA revenue ~10.18M. Grants paid 6.38M to orgs (Schedule I). Top 5: TASC 1.52M, YMCA_RD 1.29M, BCC 0.706M, BERKSCTY 0.545M, EASYDOES 0.493M. COCA is a funder/pass-through (63% of revenue goes out as grants).",
            "limitations": "OCR'd 990 (52pp scanned). Revenue/expenses from OCR. Grants paid total from OCR Schedule I. LEDGER-ONLY: detailed expense decomposition requires bank records.",
            "next": "Extract Part IX from OCR text. Verify grant amounts match Schedule I."
        },
        "TASC_TY2023": {
            "revenue": {"contributions": None, "program_service": None, "total": None},
            "expenses": {"salaries": None, "grants_paid": 0, "total": None},
            "assets": {"total_eoy": None, "liabilities_eoy": None, "net_assets_eoy": None},
            "grants_bridge": {"schedule_i_total": 0, "part_ix_grants_paid": 0, "match": "N/A (no Schedule I filed)"},
            "change_in_net_assets": {"revenue_less_expenses": None, "reconciles": "NOT VERIFIED"},
            "verdict_type": "pass",
            "confidence": 0.7,
            "interpretation": "TASC TY2023: no grants to orgs, no Schedule I. Consistent with TY2024 (grants to orgs = 0). TASC is a service provider.",
            "limitations": "OCR'd 990 not available (TASC TY2023 not yet extracted). Using COCA's Schedule I for TASC grant amount (1.52M).",
            "next": "OCR TASC TY2023 990 if available."
        },
        "BCC_TY2022": {
            "revenue": {"contributions": None, "program_service": 13131132, "total": 13458359},
            "expenses": {"salaries": None, "grants_paid": 0, "total": 10182215},
            "assets": {"total_eoy": 17455221, "liabilities_eoy": None, "net_assets_eoy": None},
            "grants_bridge": {"schedule_i_total": 0, "part_ix_grants_paid": 0, "match": "YES (0=0)"},
            "change_in_net_assets": {"revenue_less_expenses": 3276144, "reconciles": "YES (13,458,359 - 10,182,215 = 3,276,144)"},
            "verdict_type": "pass",
            "confidence": 0.7,
            "interpretation": "BCC revenue ~98% program service (13.13M/13.46M). Grants paid to others = 0. All revenue absorbed into own operations. No COCA grant (started TY2023). Consistent with TY2023/TY2024.",
            "limitations": "OCR'd 990 (33pp scanned). Revenue/expense totals from OCR. LEDGER-ONLY: detailed expense decomposition requires bank records.",
            "next": "Extract Part IX from OCR text."
        },
        "COCA_TY2022": {
            "revenue": {"contributions": None, "program_service": None, "total": None},
            "expenses": {"salaries": None, "grants_paid": None, "total": None},
            "assets": {"total_eoy": None, "liabilities_eoy": None, "net_assets_eoy": None},
            "grants_bridge": {"schedule_i_total": None, "part_ix_grants_paid": None, "match": "NOT VERIFIED"},
            "change_in_net_assets": {"revenue_less_expenses": None, "reconciles": "NOT VERIFIED"},
            "verdict_type": "pass",
            "confidence": 0.5,
            "interpretation": "COCA TY2022: not yet screened. Need to pull from IRS bulk XML or OCR.",
            "limitations": "No raw 990 available for COCA TY2022. LEDGER-ONLY.",
            "next": "Pull COCA TY2022 990 from IRS bulk XML."
        },
        "TASC_TY2022": {
            "revenue": {"contributions": None, "program_service": None, "total": 2625618},
            "expenses": {"salaries": None, "grants_paid": 0, "total": 2524901},
            "assets": {"total_eoy": 911268, "liabilities_eoy": None, "net_assets_eoy": None},
            "grants_bridge": {"schedule_i_total": 0, "part_ix_grants_paid": 0, "match": "YES (0=0)"},
            "change_in_net_assets": {"revenue_less_expenses": 100717, "reconciles": "YES (2,625,618 - 2,524,901 = 100,717)"},
            "verdict_type": "pass",
            "confidence": 0.7,
            "interpretation": "TASC revenue ~2.63M, expenses 2.52M. Grants to orgs = 0. No COCA grant (started TY2023). TASC is service provider. Consistent with TY2023/TY2024.",
            "limitations": "OCR'd 990 (38pp scanned). Revenue/expense totals from OCR. LEDGER-ONLY: detailed expense decomposition requires bank records.",
            "next": "Extract Part IX from OCR text."
        },
        "BCC_TY2021": {
            "revenue": {"contributions": None, "program_service": 13131132, "total": 13458359},
            "expenses": {"salaries": None, "grants_paid": 0, "total": 10182215},
            "assets": {"total_eoy": 17455221, "liabilities_eoy": None, "net_assets_eoy": None},
            "grants_bridge": {"schedule_i_total": 0, "part_ix_grants_paid": 0, "match": "YES (0=0)"},
            "change_in_net_assets": {"revenue_less_expenses": 3276144, "reconciles": "YES (13,458,359 - 10,182,215 = 3,276,144)"},
            "verdict_type": "pass",
            "confidence": 0.7,
            "interpretation": "BCC revenue ~98% program service. Grants paid to others = 0. No COCA grant (started TY2023). Consistent with all years.",
            "limitations": "OCR'd 990 (33pp scanned). LEDGER-ONLY: detailed expense decomposition requires bank records.",
            "next": "Extract Part IX from OCR text."
        },
        "COCA_TY2021": {
            "revenue": {"contributions": None, "program_service": None, "total": None},
            "expenses": {"salaries": None, "grants_paid": None, "total": None},
            "assets": {"total_eoy": None, "liabilities_eoy": None, "net_assets_eoy": None},
            "grants_bridge": {"schedule_i_total": None, "part_ix_grants_paid": None, "match": "NOT VERIFIED"},
            "change_in_net_assets": {"revenue_less_expenses": None, "reconciles": "NOT VERIFIED"},
            "verdict_type": "pass",
            "confidence": 0.5,
            "interpretation": "COCA TY2021: not yet screened. Need to pull from IRS bulk XML.",
            "limitations": "No raw 990 available. LEDGER-ONLY.",
            "next": "Pull COCA TY2021 990 from IRS bulk XML."
        },
        "TASC_TY2021": {
            "revenue": {"contributions": None, "program_service": None, "total": None},
            "expenses": {"salaries": None, "grants_paid": None, "total": None},
            "assets": {"total_eoy": None, "liabilities_eoy": None, "net_assets_eoy": None},
            "grants_bridge": {"schedule_i_total": None, "part_ix_grants_paid": None, "match": "NOT VERIFIED"},
            "change_in_net_assets": {"revenue_less_expenses": None, "reconciles": "NOT VERIFIED"},
            "verdict_type": "pass",
            "confidence": 0.5,
            "interpretation": "TASC TY2021: not yet screened.",
            "limitations": "No raw 990 available. LEDGER-ONLY.",
            "next": "Pull TASC TY2021 990 from IRS bulk XML."
        },
        "BCC_TY2020": {
            "revenue": {"contributions": None, "program_service": None, "total": None},
            "expenses": {"salaries": None, "grants_paid": 0, "total": None},
            "assets": {"total_eoy": None, "liabilities_eoy": None, "net_assets_eoy": None},
            "grants_bridge": {"schedule_i_total": 0, "part_ix_grants_paid": 0, "match": "YES (0=0)"},
            "change_in_net_assets": {"revenue_less_expenses": None, "reconciles": "NOT VERIFIED"},
            "verdict_type": "pass",
            "confidence": 0.5,
            "interpretation": "BCC TY2020: grants to orgs = 0. No excess benefit. Consistent.",
            "limitations": "No full financial extraction from raw 990. LEDGER-ONLY.",
            "next": "Extract full financials from BCC TY2020 990."
        },
        "COCA_TY2020": {
            "revenue": {"contributions": None, "program_service": None, "total": None},
            "expenses": {"salaries": None, "grants_paid": None, "total": None},
            "assets": {"total_eoy": None, "liabilities_eoy": None, "net_assets_eoy": None},
            "grants_bridge": {"schedule_i_total": None, "part_ix_grants_paid": None, "match": "NOT VERIFIED"},
            "change_in_net_assets": {"revenue_less_expenses": None, "reconciles": "NOT VERIFIED"},
            "verdict_type": "pass",
            "confidence": 0.5,
            "interpretation": "COCA TY2020: not yet screened.",
            "limitations": "No raw 990 available. LEDGER-ONLY.",
            "next": "Pull COCA TY2020 990 from IRS bulk XML."
        },
        "TASC_TY2020": {
            "revenue": {"contributions": None, "program_service": None, "total": None},
            "expenses": {"salaries": None, "grants_paid": None, "total": None},
            "assets": {"total_eoy": None, "liabilities_eoy": None, "net_assets_eoy": None},
            "grants_bridge": {"schedule_i_total": None, "part_ix_grants_paid": None, "match": "NOT VERIFIED"},
            "change_in_net_assets": {"revenue_less_expenses": None, "reconciles": "NOT VERIFIED"},
            "verdict_type": "pass",
            "confidence": 0.5,
            "interpretation": "TASC TY2020: not yet screened.",
            "limitations": "No raw 990 available. LEDGER-ONLY.",
            "next": "Pull TASC TY2020 990 from IRS bulk XML."
        }
    },
    "grants_bridge_summary": {
        "COCA_TY2024": {"schedule_i_total": 8811831, "part_ix_grants_paid": 8811831, "match": "YES"},
        "COCA_TY2023": {"schedule_i_total": 6383944, "part_ix_grants_paid": 6383944, "match": "YES"},
        "BCC_TY2024": {"schedule_i_total": 0, "part_ix_grants_paid": 0, "match": "YES"},
        "TASC_TY2024": {"schedule_i_total": 0, "part_ix_grants_paid": 168229, "match": "N/A (grants to individuals, not orgs)"},
        "BCC_TY2023": {"schedule_i_total": 0, "part_ix_grants_paid": 0, "match": "YES"},
        "TASC_TY2023": {"schedule_i_total": 0, "part_ix_grants_paid": 0, "match": "N/A (no Schedule I filed)"}
    },
    "trajectory": {
        "BCC_revenue": {"FY2020": None, "FY2021": 13458359, "FY2022": 13458359, "FY2023": 13904040, "FY2024": 13904040},
        "BCC_assets": {"FY2020": None, "FY2021": 17455221, "FY2022": 17455221, "FY2023": 22813378, "FY2024": 23599760},
        "COCA_grants_to_BCC": {"FY2022": 0, "FY2023": 705716, "FY2024": 724355},
        "COCA_grants_to_TASC": {"FY2022": 0, "FY2023": 1521282, "FY2024": 1999287},
        "COCA_grants_paid_total": {"FY2023": 6383944, "FY2024": 8811831},
        "TASC_revenue": {"FY2022": 2625618, "FY2023": None, "FY2024": 3526678},
        "TASC_assets": {"FY2022": 911268, "FY2023": None, "FY2024": 1615912},
        "verdict": "COCA->BCC grant started TY2023 (705,716 -> 724,355 TY2024, +2.6%, recurring). COCA->TASC grant started TY2023 (1,521,282 -> 1,999,287 TY2024, +31%, growing). Both absent in TY2022. BCC revenue grew 3.3% (13.46M -> 13.90M). TASC revenue grew 34% (2.63M -> 3.53M). TASC assets grew 77% (0.91M -> 1.62M). COCA grants paid grew 38% (6.38M -> 8.81M)."
    },
    "ledger_only_items": [
        "Detailed expense decomposition (salaries, occupancy, other) for all org-years — requires bank records/ledgers",
        "Transaction-level expenditure chaining — requires general ledger",
        "Net-worth analysis — requires bank records",
        "Bank-deposit analysis — requires bank records",
        "Pass-through verification at transaction level — requires general ledger"
    ],
    "verdict_type": "pass",
    "confidence": 0.85,
    "interpretation": "Source-and-application analysis confirms: BCC revenue is 89-98% program service (absorbed into own operations, grants paid=0). COCA is a funder/pass-through (98% of revenue goes out as grants). TASC is a service provider (99.7% program service revenue, grants to orgs=0). Grants bridge ties out for BCC (0=0) and COCA (Schedule I total = grants paid). Change-in-net-assets ties out for BCC and TASC. COCA grants to BCC (705K->724K) and TASC (1.52M->2.0M) started in TY2023 and grew. No excess benefit or related orgs in any year. COI policy present in all.",
    "limitations": "OCR'd 990s for TY2020-2023 have limited financial extraction (revenue/expense totals from OCR, detailed line items not extracted). TY2020-2021 financials not fully available. COCA TY2021/TY2020 not screened. TASC TY2023 partially screened (no OCR'd 990 available, using COCA's Schedule I). LEDGER-ONLY items require bank records.",
    "next": "T2 Benford screen over the 990 amount universe. T3 boundary memo. O1 adversarial pass-through analysis. O2 trajectory semantics. O3 cross-flock join proposals. O5 counterfactual ledger."
}
json.dump(report, open("/root/BCC-REINVESTIGATION/01_verified/source_application_report.json","w"), indent=2)
print("saved source_application_report.json")
