"""Generate Project_Scribe/profiles/cradle_budget.xlsx — CRADLE 12-month budget.

Numbers are planning rates. The only claim this workbook makes about the world is
that no equipment is purchased and no training compute is budgeted.
"""
import openpyxl
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter

B = Font(bold=True)
WRAP = Alignment(wrap_text=True, vertical="top")


def head(ws, row, vals, widths):
    for i, v in enumerate(vals, 1):
        ws.cell(row=row, column=i, value=v).font = B
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


wb = openpyxl.Workbook()

# ---------------- Summary ----------------
ws = wb.active
ws.title = "Summary"
ws["A1"] = "CRADLE - budget, 12 months"
ws["A1"].font = Font(bold=True, size=14)
ws["A2"] = "All figures EUR. Planning rates, not market quotes. 2026-11-03."
head(ws, 4, ["line", "category", "EUR", "note"], [30, 40, 12, 64])
rows = [
    ("1", "Personnel", 31000, "0.5 FTE lead x 12 months + second contributor (sheet: Personnel)"),
    ("2", "Compute - RENTED", 2500, "GPU-hours + CI; no purchase (sheet: Compute)"),
    ("3", "Independent security & privacy review", 6000, "Reviewer who did not write the code; findings published in full"),
    ("4", "Documentation, spec extraction, packaging", 3500, "D5 + D6, including the from-spec reference checker"),
    ("5", "Dissemination", 2000, "Two events, travel only"),
    ("6", "Subtotal", "=SUM(C5:C9)", "sum of lines 1-5"),
    ("7", "Contingency (10%)", "=ROUND(C10*0.1,0)", "10% of subtotal"),
    ("8", "TOTAL REQUESTED", "=C10+C11", "under the 50000 ceiling"),
    ("9", "Equipment PURCHASE", 0, "No GPU, workstation or server requested. See Compute sheet."),
]
for i, (a, b, c, d) in enumerate(rows, start=5):
    ws.cell(row=i, column=1, value=a)
    ws.cell(row=i, column=2, value=b)
    cell = ws.cell(row=i, column=3, value=c)
    cell.number_format = "#,##0"
    ws.cell(row=i, column=4, value=d).alignment = WRAP
    if a in ("6", "7", "8", "9"):
        for col in range(1, 5):
            ws.cell(row=i, column=col).font = B
ws.cell(row=15, column=1, value="31000 + 2500 + 6000 + 3500 + 2000 = 45000; + 4500 contingency = 49500").font = Font(italic=True)

# ---------------- Personnel ----------------
ws = wb.create_sheet("Personnel")
head(ws, 1, ["role", "basis", "rate EUR", "qty (months/days)", "EUR", "note"],
     [30, 12, 11, 18, 11, 56])
p = [
    ("Lead developer / maintainer", "person-month", 4500, 6, 27000, "0.5 FTE for 12 months = 6 person-months"),
    ("Second contributor", "day", 400, 10, 4000, "Corpus labelling and blind re-scoring (D1 gate)"),
]
for i, r in enumerate(p, start=2):
    for j, v in enumerate(r, start=1):
        c = ws.cell(row=i, column=j, value=v)
        if j == 5:
            c.number_format = "#,##0"
        if j == 6:
            c.alignment = WRAP
ws.cell(row=5, column=1, value="TOTAL").font = B
ws.cell(row=5, column=5, value="=SUM(E2:E3)").font = B
ws.cell(row=5, column=5).number_format = "#,##0"

# ---------------- Compute ----------------
ws = wb.create_sheet("Compute")
ws["A1"] = "Compute - what is owned vs what is rented"
ws["A1"].font = Font(bold=True, size=13)
ws["A2"] = (
    "Price basis: published on-demand medians observed 2026-11-03 "
    "(A100 ~USD 1.76/GPU-h, L40S ~USD 1.29/GPU-h, H100 ~USD 3.25/GPU-h), "
    "converted at an assumed EUR/USD 0.92 and rounded to clean planning rates. Re-quote before submission."
)
ws["A2"].alignment = WRAP
ws.merge_cells("A2:F2")
ws.row_dimensions[2].height = 48
head(ws, 4, ["item", "owned or rented", "qty (hours/min)", "rate EUR", "EUR", "purpose"],
     [34, 15, 15, 11, 11, 60])
comp = [
    ("A100 80GB (rented)", "rented", 700, 1.60, 1120,
     "Runtime-compatibility testing against vLLM and llama.cpp OpenAI-compatible servers"),
    ("L40S (rented)", "rented", 250, 1.20, 300,
     "Lower-cost serving tests; pricing sanity check against A100"),
    ("H100 SXM (rented)", "rented", 100, 3.00, 300,
     "Largest model the chain is tested against; bounded, not open-ended"),
    ("CI / CPU runner", "rented", 8000, 0.02, 160,
     "Test matrix across interpreters and three operating systems"),
    ("Storage and egress", "rented", 1, 120, 120,
     "Model weights and container images during the portability work"),
    ("Buffer on rented hours (25%)", "rented", 1, 500, 500,
     "Provider price moves and re-runs"),
    ("Intel Core Ultra 9 285H", "OWNED", 0, 0, 0,
     "Already in hand. CPU only for CRADLE's own code path."),
    ("Intel Arc 140T, 8 GB shared", "OWNED", 0, 0, 0,
     "Already in hand. Local smoke tests; not a training device."),
    ("32 GB LPDDR5x-8533", "OWNED", 0, 0, 0,
     "Already in hand."),
    ("Windows 11 Pro 24H2 workstation", "OWNED", 0, 0, 0,
     "Already in hand. Linux and macOS reached through CI, not purchased."),
]
for i, r in enumerate(comp, start=5):
    for j, v in enumerate(r, start=1):
        c = ws.cell(row=i, column=j, value=v)
        if j == 5:
            c.number_format = "#,##0"
        if j == 6:
            c.alignment = WRAP
ws.cell(row=16, column=1, value="TOTAL, RENTED").font = B
ws.cell(row=16, column=5, value="=SUM(E5:E10)").font = B
ws.cell(row=16, column=5).number_format = "#,##0"
ws.cell(row=17, column=1, value="TOTAL, OWNED (cost to this grant)").font = B
ws.cell(row=17, column=5, value="=SUM(E11:E14)").font = B
ws.cell(row=17, column=5).number_format = "#,##0"
ws.cell(row=19, column=1, value=(
    "No equipment is purchased. 'RTX 4090 for integration testing' appears in the source "
    "profile and is withdrawn: CRADLE's Python side is standard library only and has no GPU "
    "code path. The honest compute need is rented serving hours, above."
)).alignment = WRAP
ws.merge_cells("A19:F19")
ws.row_dimensions[19].height = 60

# ---------------- Other ----------------
ws = wb.create_sheet("Other")
head(ws, 1, ["line", "item", "EUR", "note"], [8, 38, 10, 68])
other = [
    ("3", "Independent security & privacy review", 6000,
     "Fixed scope: refusal path, endpoint surface, state directory, model bridging. Findings published including unfixed."),
    ("4a", "Spec extraction and conformance suite", 1800,
     "D5: vocabulary, frame lifecycle, refusal reasons, lesson format"),
    ("4b", "Packaging and first-run docs", 1200,
     "D6: install, first refusal, adding a vocabulary term"),
    ("4c", "Documentation rewrite for non-authors", 500,
     "Remove assumptions about the author's machine and Windows paths"),
    ("5", "Dissemination - two events", 2000,
     "Travel only; no booth, no sponsorship"),
    ("7", "Contingency 10%", 4500,
     "Applied to the subtotal, not to compute alone"),
]
for i, r in enumerate(other, start=2):
    for j, v in enumerate(r, start=1):
        c = ws.cell(row=i, column=j, value=v)
        if j == 3:
            c.number_format = "#,##0"
        if j == 4:
            c.alignment = WRAP

# ---------------- Assumptions ----------------
ws = wb.create_sheet("Assumptions")
head(ws, 1, ["assumption", "value", "basis"], [40, 20, 78])
assum = [
    ("Currency", "EUR", "NLnet awards in EUR; the source profile states 50000 without a currency"),
    ("Ceiling", "50000 EUR", "NLnet NGI Zero grant range"),
    ("Requested", "49500 EUR", "Under the ceiling; contingency named rather than padded into personnel"),
    ("Person-month rate", "4500 EUR", "Planning rate for a solo maintainer, half time"),
    ("EUR/USD", "0.92", "Assumption for converting observed USD list prices; re-quote at submission"),
    ("A100 GPU-hour", "1.60 EUR", "Observed USD 1.76 median, 2026-11-03, rounded down"),
    ("L40S GPU-hour", "1.20 EUR", "Observed USD 1.29, rounded"),
    ("H100 GPU-hour", "3.00 EUR", "Observed USD 3.25 median, rounded; AWS on-demand is far higher and is not used"),
    ("Training compute", "none", "CRADLE has no training step; no long-running GPU job is budgeted"),
    ("Equipment purchase", "0 EUR", "Owned hardware documented in Project_CRADLE/HARDWARE.md"),
    ("Contingency", "10%", "Of subtotal"),
    ("Tax and social contributions", "not itemised",
     "Applicant is an individual; the figure is gross and the applicant meets their own obligations"),
]
for i, r in enumerate(assum, start=2):
    for j, v in enumerate(r, start=1):
        c = ws.cell(row=i, column=j, value=v)
        if j == 3:
            c.alignment = WRAP

out = "Project_Scribe/profiles/cradle_budget.xlsx"
wb.save(out)

# --- read back and assert the arithmetic, not the intention ---
# openpyxl writes formulas as strings and has no calc engine, so data_only=True
# returns None here. Instead: evaluate the SUM ranges from the cells they name.
import re


def eval_sum(ws, ref):
    m = re.fullmatch(r"=SUM\(([A-Z]+)(\d+):([A-Z]+)(\d+)\)", ref)
    assert m, "unparsed formula: %r" % ref
    col_a, row_a, col_b, row_b = m.group(1), int(m.group(2)), m.group(3), int(m.group(4))
    assert col_a == col_b, "multi-column SUM not supported: %r" % ref
    total = 0
    for r in range(row_a, row_b + 1):
        v = ws["%s%d" % (col_a, r)].value
        if isinstance(v, (int, float)):
            total += v
    return total


wb2 = openpyxl.load_workbook(out)
print("sheets:", wb2.sheetnames)
personnel = eval_sum(wb2["Personnel"], wb2["Personnel"]["E5"].value)
rented = eval_sum(wb2["Compute"], wb2["Compute"]["E16"].value)
owned = eval_sum(wb2["Compute"], wb2["Compute"]["E17"].value)
print("Personnel total  :", personnel)
print("Compute rented   :", rented)
print("Compute owned    :", owned)
assert personnel == 31000, personnel
assert rented == 2500, rented
assert owned == 0, owned

# Summary sheet: lines 1-5 literal, then subtotal/contingency/total formulas
s = wb2["Summary"]
lines = [s["C%d" % r].value for r in range(5, 10)]
assert all(isinstance(v, (int, float)) for v in lines), lines
subtotal = sum(lines)
contingency = round(subtotal * 0.1)
total = subtotal + contingency
print("summary lines 1-5:", lines, "subtotal", subtotal, "contingency", contingency, "total", total)
assert subtotal == 45000, subtotal
assert total == 49500, total

# The workbook must carry a zero equipment-purchase line and no training line.
assert s["C13"].value == 0, s["C13"].value
print("OK: personnel 31000, rented 2500, owned 0, subtotal 45000, total 49500, equipment purchase 0")
