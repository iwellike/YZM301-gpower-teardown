"""Empirically derives and verifies the a-priori N rounding rule for t2-indep
against oracle/t2_indep_vectors.csv. See ASSUMPTIONS.md section 1 for the
hypotheses tested. Implements the current (best-found) rule: n1=ceil(x)
from the continuous power-equation root; for ratio=1, n2=n1 trivially; for
ratio!=1, n2=round_half_up(ratio*x) with a safety increment if that ever
undershoots the target power. Confirmed via live GPowerNT.exe post-hoc
cross-check (LEDGER.md section 2c: at fixed n1, both n2=127 and n2=128
clear the power target, yet G*Power picks the nearer-to-continuous 127,
not the smaller one) -- raised oracle matches 24/30 -> 25/30. The
remaining 5/30 misses are not a rounding-rule or distribution-math problem
(both were independently verified correct); they trace to GPowerNT.exe's
own bisection converging to a slightly different continuous root than
scipy's brentq, which replicating fully would require bit-for-bit
reproducing GPowerNT.exe's internal search -- out of scope.
"""
import csv
import math
from scipy import stats
from scipy.optimize import brentq


def actual_power(n1, n2, d, alpha, tails):
    df = n1 + n2 - 2
    if df <= 0:
        return 0.0
    ncp = d * math.sqrt(n1 * n2 / (n1 + n2))
    if tails == 1:
        tcrit = stats.t.ppf(1 - alpha, df)
        return stats.nct.sf(tcrit, df, ncp)
    tcrit = stats.t.ppf(1 - alpha / 2, df)
    return stats.nct.sf(tcrit, df, ncp) + stats.nct.cdf(-tcrit, df, ncp)


def continuous_n1(d, alpha, power, tails, ratio, lo=2.0):
    f = lambda x: actual_power(x, x * ratio, d, alpha, tails) - power
    flo = f(lo)
    if flo >= 0:
        return lo
    good_hi, hi = lo, lo * 2
    for _ in range(300):
        fhi = f(hi)
        if math.isnan(fhi):
            hi = (good_hi + hi) / 2.0
            continue
        if flo * fhi <= 0:
            return brentq(f, good_hi if flo * f(good_hi) <= 0 else lo, hi, xtol=1e-13, rtol=1e-15)
        good_hi, hi = hi, hi * 2
    raise RuntimeError("no bracket found")


def solve_n1_n2(d, alpha, power, tails, ratio):
    x = continuous_n1(d, alpha, power, tails, ratio)
    n1 = max(math.ceil(x), 1)
    if ratio == 1:
        n2 = n1
    else:
        n2 = max(math.floor(ratio * x + 0.5), 1)
        while actual_power(n1, n2, d, alpha, tails) < power:
            n2 += 1
    return n1, n2


if __name__ == "__main__":
    rows = list(csv.DictReader(open("oracle/t2_indep_vectors.csv")))
    ok = 0
    for row in rows:
        tails, d, alpha, power, ratio = (
            int(row["in_tails"]), float(row["in_d"]), float(row["in_alpha"]),
            float(row["in_power"]), float(row["in_ratio"]),
        )
        n1_act, n2_act, nt_act = int(row["out_n1"]), int(row["out_n2"]), int(row["out_n_total"])
        n1, n2 = solve_n1_n2(d, alpha, power, tails, ratio)
        nt = n1 + n2
        match = (n1, n2, nt) == (n1_act, n2_act, nt_act)
        ok += match
        print(f"{row['id']:28s} {'OK' if match else 'MISMATCH':9s} got=({n1},{n2},{nt}) expected=({n1_act},{n2_act},{nt_act})")
    print(f"\n{ok}/{len(rows)} exact n1/n2/n_total matches ({100*ok/len(rows):.1f}%)")
