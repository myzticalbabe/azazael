# cython: boundscheck=False, wraparound=False, cdivision=True
"""Native kernel: the scoring heart of the dream agreement replay.

Same contract as the pythran draft (_replay_kernel.py): parallel int columns
over PAIRED guesses/answers, per-rung aggregation. Cython generates plain C
against the CPython headers on this box, so it builds where the pythran
headers cannot (MSVC 14.51 rejects them; no clang-cl on box).

Pairing stays in Python (native_replay.pair_columns); scoring is native here.
"""
from libc.stdint cimport int64_t


def score_pairs(list pred_rung, list pred_kind, list ans_rung, list ans_ok,
                int n_rungs):
    cdef Py_ssize_t n = len(pred_rung)
    cdef Py_ssize_t i
    cdef int64_t hits = 0
    cdef long r
    cdef int pk, ok, ar, pr
    rung_pairs = [0] * n_rungs
    rung_hits = [0] * n_rungs
    for i in range(n):
        pr = pred_rung[i]
        pk = pred_kind[i]
        ar = ans_rung[i]
        ok = ans_ok[i]
        if pk == 0:
            won = (ar == pr) and (ok == 1)
        else:
            won = ((pk == 1) == (ok == 1)) and (pr < 0 or ar == pr)
        if won:
            hits += 1
        r = pr
        if 0 <= r < n_rungs:
            rung_pairs[r] += 1
            if won:
                rung_hits[r] += 1
    return int(hits), int(n), rung_pairs, rung_hits
