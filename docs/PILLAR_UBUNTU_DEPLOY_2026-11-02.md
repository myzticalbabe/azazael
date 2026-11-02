# PILLAR-UBUNTU-DEPLOY — Investigation

**Task:** Board 46864 / PILLAR-UBUNTU-DEPLOY
**Date:** 2026-11-02
**Investigator:** opencode lane (max reasoning + WSL access)

## Measurement

Checked Ubuntu-26.04 via WSL:

| Item | Status |
|---|---|
| `apply_quartet_contract.py` | MISSING |
| `apply_bibl_guard.py` | MISSING |
| `bibl_prune.py` | MISSING |
| `test_bibl_self_index_guard.py` | MISSING |
| `BIBL/` directory | MISSING |
| Git repo | Present (1 commit, 27435 in-pack objects) |

## Finding

The Ubuntu copy of /root/azazael is significantly behind Windows. It lacks:
1. The three migration tools (apply_quartet_contract, apply_bibl_guard, bibl_prune)
2. The BIBL self-index guard test
3. The BIBL directory itself

The task says "Apply the three Windows-authored migrations in order" but the tools don't
exist on Ubuntu. They must be synced from Windows first.

## Recommended action

1. Sync the three tools from Windows: `scp /mnt/c/Azazael/azazael/tools/apply_*.py /root/azazael/tools/`
2. Sync the test: `scp /mnt/c/Azazael/azazael/tests/test_bibl_self_index_guard.py /root/azazael/tests/`
3. Then apply in order: apply_quartet_contract → apply_bibl_guard (read refusal if anchor moved) → bibl_prune --dry-run then for real
4. Report before/after BIBL size

## Note

The task says "do NOT reuse the Windows prune shape." The Ubuntu BIBL may have different
structure (no 31MB INDEX.md or 26 letter files). Measure first.

## Deliverable checklist

- [x] Measured: 3 migration tools missing on Ubuntu
- [x] Measured: BIBL directory missing
- [x] Measured: test file missing
- [x] Recommended: sync tools first, then apply
- [x] Note: do not reuse Windows prune shape