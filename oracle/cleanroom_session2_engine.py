# Clean-room reimplementation of G*Power's "t2-indep" (two independent means
# t-test) calculation engine, built only from the CONTRACT.md interface spec
# and standard noncentral-t power theory (Cohen 1988). No decompiled/reversed
# code was consulted.
#
# a-priori rounding rule for ratio != 1 (the one underspecified part of the
# contract): we solve the continuous-n1 equation (treating n2 = ratio*n1 as
# a real number) with brentq to get a close starting point, then do an
# integer search upward from just below that root for the SMALLEST integer
# n1 such that n2 = ceil(ratio * n1) yields actual_power >= the requested
# power. This is the standard textbook approach named directly in the task
# spec, it guarantees the contract's invariant (actual_power >= power), and
# ceiling n2 from the exact ratio (rather than rounding n1 again afterwards)
# keeps the allocation ratio as close to the requested one as an integer
# sample size allows.

import math
from scipy import stats
from scipy.optimize import brentq


def _crit_t(tails, alpha, df):
    if tails == 1:
        return stats.t.ppf(1 - alpha, df)
    return stats.t.ppf(1 - alpha / 2, df)


def _ncp(d, n1, n2):
    return d * math.sqrt(n1 * n2 / (n1 + n2))


def _power(critical_t, df, ncp, tails):
    if tails == 1:
        return 1 - stats.nct.cdf(critical_t, df, ncp)
    return (1 - stats.nct.cdf(critical_t, df, ncp)) + stats.nct.cdf(-critical_t, df, ncp)


def solve_post_hoc(tails, d, alpha, n1, n2):
    df = n1 + n2 - 2
    ncp = _ncp(d, n1, n2)
    crit = _crit_t(tails, alpha, df)
    power = _power(crit, df, ncp, tails)
    return {"ncp": ncp, "critical_t": crit, "df": df, "power": power}


def solve_criterion(tails, d, power, n1, n2):
    df = n1 + n2 - 2
    ncp = _ncp(d, n1, n2)

    def f(alpha):
        return _power(_crit_t(tails, alpha, df), df, ncp, tails) - power

    alpha = brentq(f, 1e-12, 1 - 1e-12, xtol=1e-14, rtol=1e-14)
    crit = _crit_t(tails, alpha, df)
    return {"ncp": ncp, "critical_t": crit, "df": df, "alpha": alpha}


def solve_compromise(tails, d, beta_alpha_ratio, n1, n2):
    df = n1 + n2 - 2
    ncp = _ncp(d, n1, n2)

    def beta_of_alpha(alpha):
        crit = _crit_t(tails, alpha, df)
        return 1 - _power(crit, df, ncp, tails)

    def f(alpha):
        return beta_of_alpha(alpha) - beta_alpha_ratio * alpha

    alpha = brentq(f, 1e-12, 1 - 1e-12, xtol=1e-14, rtol=1e-14)
    beta = beta_of_alpha(alpha)
    crit = _crit_t(tails, alpha, df)
    power = 1 - beta
    return {"ncp": ncp, "critical_t": crit, "df": df, "alpha": alpha, "beta": beta, "power": power}


def solve_sensitivity(tails, alpha, power, n1, n2):
    df = n1 + n2 - 2
    crit = _crit_t(tails, alpha, df)
    scale = math.sqrt(n1 * n2 / (n1 + n2))

    def f(ncp):
        return _power(crit, df, ncp, tails) - power

    ncp = brentq(f, 0.0, 1000.0, xtol=1e-14, rtol=1e-14)
    d = ncp / scale
    return {"ncp": ncp, "critical_t": crit, "df": df, "d": d}


def solve_a_priori(tails, d, alpha, power, ratio):
    def power_cont(n1c):
        n2c = ratio * n1c
        df = n1c + n2c - 2
        ncp = _ncp(d, n1c, n2c)
        crit = _crit_t(tails, alpha, df)
        return _power(crit, df, ncp, tails)

    def f(n1c):
        return power_cont(n1c) - power

    lo, hi = 2.0, 4.0
    if f(lo) >= 0:
        root = lo
    else:
        while f(hi) < 0:
            hi *= 2
            if hi > 1e9:
                raise RuntimeError("NO_SOLUTION")
        root = brentq(f, lo, hi, xtol=1e-10, rtol=1e-12)

    def achieved_power(n1_int, n2_int):
        df = n1_int + n2_int - 2
        ncp = _ncp(d, n1_int, n2_int)
        crit = _crit_t(tails, alpha, df)
        return _power(crit, df, ncp, tails), ncp, crit, df

    n1_try = max(2, int(math.floor(root)) - 5)
    for _ in range(100000):
        n2_try = max(2, math.ceil(ratio * n1_try))
        p, ncp, crit, df = achieved_power(n1_try, n2_try)
        if p >= power:
            return {
                "ncp": ncp,
                "critical_t": crit,
                "df": df,
                "n1": n1_try,
                "n2": n2_try,
                "n_total": n1_try + n2_try,
                "actual_power": p,
            }
        n1_try += 1
    raise RuntimeError("NO_SOLUTION")


if __name__ == "__main__":
    def approx(a, b, tol=1e-6):
        return abs(a - b) <= tol or (b != 0 and abs(a - b) / abs(b) <= tol)

    # 1) a-priori
    r = solve_a_priori(tails=1, d=0.5, alpha=0.05, power=0.95, ratio=1)
    assert r["n1"] == 88 and r["n2"] == 88 and r["n_total"] == 176 and r["df"] == 174
    assert approx(r["ncp"], 3.3166248)
    assert approx(r["critical_t"], 1.6536580)
    assert approx(r["actual_power"], 0.9514254)

    # 2) post-hoc
    r = solve_post_hoc(tails=1, d=0.5, alpha=0.05, n1=88, n2=88)
    assert r["df"] == 174
    assert approx(r["ncp"], 3.3166248)
    assert approx(r["critical_t"], 1.6536580)
    assert approx(r["power"], 0.9514254)

    # 3) compromise
    r = solve_compromise(tails=1, d=0.5, beta_alpha_ratio=1, n1=88, n2=88)
    assert r["df"] == 174
    assert approx(r["ncp"], 3.3166248)
    assert approx(r["critical_t"], 1.6606859)
    assert approx(r["alpha"], 0.0492887)
    assert approx(r["beta"], 0.0492887)
    assert approx(r["power"], 0.9507113)

    # 4) criterion
    r = solve_criterion(tails=1, d=0.5, power=0.95, n1=88, n2=88)
    assert r["df"] == 174
    assert approx(r["ncp"], 3.3166248)
    assert approx(r["critical_t"], 1.6676050)
    assert approx(r["alpha"], 0.0485965)

    # 5) sensitivity
    r = solve_sensitivity(tails=1, alpha=0.05, power=0.95, n1=88, n2=88)
    assert r["df"] == 174
    assert approx(r["ncp"], 3.3025887)
    assert approx(r["critical_t"], 1.6536580)
    assert approx(r["d"], 0.4978840)

    print("ALL 5 REFERENCE VECTORS PASSED")
