"""One-sided exact lower confidence bound for a recall figure.

The crisis router's recall is currently reported as three point estimates
(0.83 / 0.83 / 0.18). A point estimate is not a floor: with 100 statements,
0.83 and 0.80 are the same observation, so a funder cannot tell whether the
router clears a safety bar. This computes the Clopper-Pearson exact one-sided
lower bound, which is the conservative bound, and the Wilson bound next to it
so the gap between them is visible rather than hidden.

Usage:
    python tools/recall_bound.py 83 100
    python tools/recall_bound.py 83 100 --size-for 0.80

Stdlib only. No scipy: the exact bound is a bisection on the binomial tail.
"""
import math
import sys


def binomial_tail_ge(k: int, n: int, p: float) -> float:
    """P(X >= k) for X ~ Binomial(n, p)."""
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    if p <= 0.0:
        return 0.0
    if p >= 1.0:
        return 1.0
    total = 0.0
    for i in range(k, n + 1):
        total += math.comb(n, i) * (p ** i) * ((1.0 - p) ** (n - i))
    return min(1.0, max(0.0, total))


def clopper_pearson_lower(k: int, n: int, alpha: float = 0.05) -> float:
    """Exact one-sided lower bound: the p where P(X >= k | p) == alpha."""
    if n <= 0:
        raise ValueError("n must be positive")
    if k < 0 or k > n:
        raise ValueError(f"k={k} is not a count of successes in n={n}")
    if k == 0:
        return 0.0
    if k == n:
        return alpha ** (1.0 / n)
    lo, hi = 0.0, k / n
    for _ in range(200):
        mid = (lo + hi) / 2
        if binomial_tail_ge(k, n, mid) > alpha:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def wilson_lower(k: int, n: int, z: float = 1.6448536269514722) -> float:
    """Wilson score lower bound, for comparison with the exact one."""
    if n <= 0:
        raise ValueError("n must be positive")
    p = k / n
    denom = 1.0 + z * z / n
    centre = p + z * z / (2 * n)
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return max(0.0, (centre - margin) / denom)


def n_needed_for_floor(observed: float, floor: float, alpha: float = 0.05) -> int:
    """Smallest n whose exact lower bound clears `floor` at this observed rate."""
    for n in range(10, 200001):
        if clopper_pearson_lower(round(observed * n), n, alpha) >= floor:
            return n
    return -1


def self_test() -> None:
    """Assert the defining equation, not remembered constants.

    A table of expected numbers written from memory tests the author's memory
    rather than the code: the first version of this function carried three
    remembered values, and two of them were wrong while the implementation was
    right. The properties below cannot be satisfied by a broken bound.
    """
    failures = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        print(f"  [selftest] {name}: {'ok' if ok else 'FAIL ' + detail}")
        if not ok:
            failures.append(name)

    # 1. The bound is the p at which the observed result has probability alpha.
    for k, n in ((50, 100), (83, 100), (18, 100), (415, 500)):
        p = clopper_pearson_lower(k, n, 0.05)
        tail = binomial_tail_ge(k, n, p)
        check(f"defining equation k={k} n={n}", abs(tail - 0.05) < 1e-9,
              f"tail={tail!r} at p={p!r}")

    # 2. All successes has a closed form: alpha ** (1/n).
    check("closed form k=n", abs(clopper_pearson_lower(100, 100) - 0.05 ** 0.01) < 1e-12,
          str(clopper_pearson_lower(100, 100)))

    # 3. Monotone in k: more successes cannot lower the bound.
    b = [clopper_pearson_lower(k, 200) for k in (40, 80, 120, 160)]
    check("monotone in k", all(x < y for x, y in zip(b, b[1:])), str([round(x, 4) for x in b]))

    # 4. A larger sample at the same rate tightens the bound (raises it).
    check("tightens with n", clopper_pearson_lower(415, 500) > clopper_pearson_lower(83, 100),
          f"{clopper_pearson_lower(415, 500):.4f} vs {clopper_pearson_lower(83, 100):.4f}")

    # 5. Exact is the conservative one: it must not exceed Wilson.
    check("exact <= wilson", all(clopper_pearson_lower(k, 100) <= wilson_lower(k, 100)
                                  for k in (18, 50, 83, 99)), "")

    # 6. Negative control: an impossible count must be refused, not clamped to 1.0.
    for bad_k, bad_n in ((120, 100), (-1, 100), (5, 0)):
        try:
            clopper_pearson_lower(bad_k, bad_n)
            check(f"refuses k={bad_k} n={bad_n}", False, "no error raised")
        except ValueError:
            check(f"refuses k={bad_k} n={bad_n}", True)

    print(f"  [selftest] {'clean' if not failures else str(len(failures)) + ' failure(s)'}")
    sys.exit(1 if failures else 0)


def main(argv):
    if "--selftest" in argv:
        self_test()
    args = [a for a in argv[1:] if not a.startswith("--")]
    if len(args) < 2:
        print(__doc__)
        return 2
    k, n = int(args[0]), int(args[1])
    if k > n:
        print(f"k={k} exceeds n={n}: recall cannot be above 1.0")
        return 2
    alpha = 0.05
    print(f"observed recall : {k}/{n} = {k / n:.4f}")
    print(f"exact lower 95% : {clopper_pearson_lower(k, n, alpha):.4f}   (Clopper-Pearson, one-sided)")
    print(f"wilson lower 95%: {wilson_lower(k, n):.4f}   (closed form, less conservative)")
    if "--size-for" in argv:
        floor = float(argv[argv.index("--size-for") + 1])
        need = n_needed_for_floor(k / n, floor, alpha)
        print(f"holdout size for a lower bound >= {floor:.2f} at this rate: n = {need}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
