"""t2-indep (t tests: Means - Difference between two independent means) power
analysis engine. Pure calculation, no I/O or CLI concerns.

Formulas (CONTRACT.md 4.1, verified against the 5 public oracle vectors in
CONTRACT.md section 9):
    df = n1 + n2 - 2
    ncp = d * sqrt(n1*n2/(n1+n2))
    critical_t = t.ppf(1-alpha, df)      (tails == 1)
                 t.ppf(1-alpha/2, df)    (tails == 2)
    actual_power = P(reject H0) under the noncentral t distribution with
                   noncentrality ncp.

The a-priori sample-size search and its ceil()-based rounding are described
in LEDGER.md section 2/4 (REA evidence, GPowerNT.exe 0x4a7140) and
ASSUMPTIONS.md section 1 (empirical verification against
oracle/t2_indep_vectors.csv: exact for ratio=1, ~79% exact for ratio!=1).
"""
import math

from scipy import stats
from scipy.optimize import brentq


class EngineError(Exception):
    def __init__(self, code, field, message):
        super().__init__(message)
        self.code = code
        self.field = field
        self.message = message


def df(n1, n2):
    return n1 + n2 - 2


def ncp(n1, n2, d):
    return d * math.sqrt(n1 * n2 / (n1 + n2))


def critical_t(dfree, alpha, tails):
    if tails == 1:
        return stats.t.ppf(1 - alpha, dfree)
    return stats.t.ppf(1 - alpha / 2, dfree)


def actual_power(n1, n2, d, alpha, tails):
    dfree = df(n1, n2)
    if dfree <= 0:
        return 0.0
    nc = ncp(n1, n2, d)
    tcrit = critical_t(dfree, alpha, tails)
    if tails == 1:
        return float(stats.nct.sf(tcrit, dfree, nc))
    return float(stats.nct.sf(tcrit, dfree, nc) + stats.nct.cdf(-tcrit, dfree, nc))


def _continuous_n1(d, alpha, power, tails, ratio, lo=2.0):
    """Continuous root of actual_power(x, ratio*x) == power, treating n1=x.
    Clamped at lo if the target power is already met at the floor."""
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
            lo_b = good_hi if flo * f(good_hi) <= 0 else lo
            return brentq(f, lo_b, hi, xtol=1e-13, rtol=1e-15)
        good_hi, hi = hi, hi * 2
    raise EngineError("NO_SOLUTION", None, "a-priori N araması yakınsamadı")


def solve_a_priori(d, alpha, power, tails, ratio):
    x = _continuous_n1(d, alpha, power, tails, ratio)
    n1 = max(math.ceil(x), 2)
    n2 = max(math.ceil(ratio * x), 2)
    dfree = df(n1, n2)
    return {
        "ncp": ncp(n1, n2, d),
        "critical_t": critical_t(dfree, alpha, tails),
        "df": dfree,
        "n1": n1,
        "n2": n2,
        "n_total": n1 + n2,
        "actual_power": actual_power(n1, n2, d, alpha, tails),
    }


def solve_post_hoc(d, alpha, n1, n2, tails):
    dfree = df(n1, n2)
    return {
        "ncp": ncp(n1, n2, d),
        "critical_t": critical_t(dfree, alpha, tails),
        "df": dfree,
        "power": actual_power(n1, n2, d, alpha, tails),
    }


def _beta_given_alpha(n1, n2, d, alpha, tails):
    dfree = df(n1, n2)
    nc = ncp(n1, n2, d)
    tcrit = critical_t(dfree, alpha, tails)
    if tails == 1:
        return float(stats.nct.cdf(tcrit, dfree, nc))
    return float(stats.nct.cdf(tcrit, dfree, nc) - stats.nct.cdf(-tcrit, dfree, nc))


def solve_compromise(d, beta_alpha_ratio, n1, n2, tails):
    f = lambda a: _beta_given_alpha(n1, n2, d, a, tails) - beta_alpha_ratio * a
    try:
        alpha = brentq(f, 1e-12, 1 - 1e-12, xtol=1e-14, rtol=1e-15)
    except ValueError as exc:
        raise EngineError("NO_SOLUTION", None, "compromise modunda kök bulunamadı") from exc
    dfree = df(n1, n2)
    beta = _beta_given_alpha(n1, n2, d, alpha, tails)
    return {
        "ncp": ncp(n1, n2, d),
        "critical_t": critical_t(dfree, alpha, tails),
        "df": dfree,
        "alpha": alpha,
        "beta": beta,
        "power": 1 - beta,
    }


def solve_criterion(d, power, n1, n2, tails):
    f = lambda a: actual_power(n1, n2, d, a, tails) - power
    try:
        alpha = brentq(f, 1e-12, 1 - 1e-12, xtol=1e-14, rtol=1e-15)
    except ValueError as exc:
        raise EngineError("NO_SOLUTION", None, "criterion modunda kök bulunamadı") from exc
    dfree = df(n1, n2)
    return {
        "ncp": ncp(n1, n2, d),
        "critical_t": critical_t(dfree, alpha, tails),
        "df": dfree,
        "alpha": alpha,
    }


def solve_sensitivity(alpha, power, n1, n2, tails):
    f = lambda d: actual_power(n1, n2, d, alpha, tails) - power
    try:
        d = brentq(f, 1e-9, 1e4, xtol=1e-13, rtol=1e-15)
    except ValueError as exc:
        raise EngineError("NO_SOLUTION", None, "sensitivity modunda kök bulunamadı") from exc
    dfree = df(n1, n2)
    return {
        "ncp": ncp(n1, n2, d),
        "critical_t": critical_t(dfree, alpha, tails),
        "df": dfree,
        "d": d,
    }
