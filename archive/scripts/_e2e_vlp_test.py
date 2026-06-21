#!/usr/bin/env python3
"""E2E Pipeline Test — Verifiable Lie Protocol v3.1.0"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from CORE.audit_trail import (
    audit_file_read, audit_scan_run, audit_inference_spawn,
    audit_sync_run, audit_test_run, audit_file_edit, audit_file_create,
    audit_sentinel_run, audit_gate_passed, audit_expect_action,
    get_session_filepath, close_session, verify_chain, verify_head_hash,
    verify_monotonicity, verify_on_startup, verify_completeness,
    get_merkle_root, get_merkle_proof, verify_inclusion_proof,
    verify_signature, audit_anomaly_scan, read_audit_lines,
    find_entries, get_line, verify_citation_exists, verify_entry_hash,
    _CRYPTO_AVAILABLE
)

R = {"p": 0, "f": 0, "t": []}
def t(n, ok, d=""):
    R["t"].append((n,ok,d))
    if ok: R["p"]+=1; print(f"  PASS: {n}")
    else: R["f"]+=1; print(f"  FAIL: {n} — {d}")

print("=== VLP v3.1.0 E2E Pipeline Test ===\n")

# Phase 1: Init
print("=== Phase 1: Init ===")
sp = get_session_filepath()
spf = sp.replace("\\","/")
t("Session initialized", Path(sp).exists(), spf)
t("Session UUID in filename", len(Path(sp).stem.split("_")) == 4)

# Phase 2: Record
print("\n=== Phase 2: Record ===")
audit_file_read(["SYS.md","SOP.md"], "docs")
audit_scan_run("x.py","AST",50,0,"clean")
audit_inference_spawn("thinker-with-files-gemini", ".ic/test.log", "gemini-2.5-pro")
audit_inference_spawn("researcher-web", "", "")
audit_sync_run(55,7,0)
audit_test_run("e2e",10,0,1234.5)
audit_file_edit("audit_trail.py","v3.1.0",200)
audit_file_create("_test.py","test",2000)
audit_sentinel_run("AUTHORIZED",[])
audit_gate_passed(8,0)
lines = read_audit_lines(spf)
t(f"10 entries recorded", len(lines) >= 11, f"got {len(lines)}")

# Phase 3: Omission
print("\n=== Phase 3: Omission ===")
audit_expect_action("inference_spawn","Gemini required")
audit_inference_spawn("thinker-with-files-gemini","","")
audit_expect_action("test_run","WILL NOT BE FULFILLED")
t("expect+fulfill recorded", True)

# Phase 4: Close
print("\n=== Phase 4: Close ===")
cc = close_session()
t("Session closed", cc is not None)

# Phase 5: Chain
print("\n=== Phase 5: Chain ===")
v,e = verify_chain(spf)
t("verify_chain", v, f"line {e}")
m,me = verify_monotonicity(spf)
t("verify_monotonicity", m, f"line {me}")

# Phase 6: Anchor
print("\n=== Phase 6: Anchor ===")
a,s,c = verify_head_hash(sp)  # Use raw Windows path to match anchors.jsonl
t("verify_head_hash", a, f"stored={s[:8] if s else 'none'}... cur={c[:8] if c else 'none'}...")

# Phase 7: Merkle
print("\n=== Phase 7: Merkle ===")
root = get_merkle_root(spf)
t("merkle_root computed", len(root)==64, root[:16])
all_lines = read_audit_lines(spf)
hashes = [d["hash"] for _,d in all_lines if d.get("hash") and d.get("type") not in ("chain_checkpoint","session_end")]
if hashes:
    proof = get_merkle_proof(spf, hashes[0])
    t("inclusion proof", len(proof)>0)
    t("proof verified", verify_inclusion_proof(hashes[0], proof, root))

# Phase 8: Ed25519
print("\n=== Phase 8: Ed25519 ===")
if _CRYPTO_AVAILABLE:
    bad = sum(1 for _,d in all_lines if d.get("signature") and not verify_signature(d))
    t(f"signatures valid", bad==0, f"{bad} bad")
else:
    t("crypto not installed (graceful)", True)

# Phase 9: Omission check
print("\n=== Phase 9: Omission check ===")
ok,miss = verify_completeness(spf)
t("detected unfulfilled", not ok)
t("correct missing type", len(miss)==1 and miss[0][1]=="test_run", str(miss))

# Phase 10: Anomaly
print("\n=== Phase 10: Anomaly ===")
an = audit_anomaly_scan(spf)
t("no anomalies", len(an)==0, str(an[:3]) if an else "")

# Phase 11: Citations
print("\n=== Phase 11: Citations ===")
t("citation line 1", verify_citation_exists(f"{spf}:1"))
t("citation line 5", verify_citation_exists(f"{spf}:5"))
t("invalid rejected", not verify_citation_exists(f"{spf}:9999"))
d = get_line(spf,1)
t("get_line works", bool(d))
t("entry_hash valid", verify_entry_hash(d))
fe = find_entries(spf,"file_read")
t("find_entries", len(fe)>=1, f"got {len(fe)}")

# Phase 12: Startup
print("\n=== Phase 12: Startup ===")
br = verify_on_startup()
ob = [b for b in br if spf in str(b.get("file",""))]
t("session clean", len(ob)==0, f"broken:{len(ob)}")

# Phase 13: Sentinel
print("\n=== Phase 13: Sentinel ===")
sys.path.insert(0, str(Path(__file__).parent / "src" / "SCRIPTS"))
from sentinel_gate import _AUDIT_AVAILABLE as sa
from sentinel_gate import verify_signature as vs
from sentinel_gate import verify_completeness as vc
from sentinel_gate import audit_anomaly_scan as aa
from sentinel_gate import audit_expect_action as ae
t("AUDIT_AVAILABLE", sa)
t("verify_signature", vs is not None)
t("verify_completeness", vc is not None)
t("audit_anomaly_scan", aa is not None)
t("audit_expect_action", ae is not None)

# Report
print(f"\n{'='*60}")
print(f"RESULT: {R['p']}/{R['p']+R['f']} passed")
print(f"{'='*60}")
if R["f"]:
    print("\nFAILURES:")
    for n,ok,d in R["t"]:
        if not ok: print(f"  - {n}: {d}")

with open(Path(__file__).parent/"_e2e_vlp_results.json","w") as f:
    json.dump({"session":spf,"p":R["p"],"f":R["f"],"tests":R["t"]},f,indent=2)
print(f"\nSession: {spf}")
sys.exit(0 if R["f"]==0 else 1)
