"""Golden-vector and boundary tests for src.engine.t2_indep.

Golden vectors come from CONTRACT.md section 9 (public, non-hidden).
Boundary cases come from SPEC.md section A (tiny/huge d, power near alpha,
unequal ratio) and ASSUMPTIONS.md (rounding rule limitations).
"""
import math

import pytest

from src.engine import t2_indep as engine

TOL = 1e-6


def close(a, b, tol=TOL):
    return abs(a - b) <= tol or abs(a - b) <= tol * max(abs(a), abs(b), 1.0)


def test_a_priori_contract_example():
    r = engine.solve_a_priori(d=0.5, alpha=0.05, power=0.95, tails=1, ratio=1)
    assert r["n1"] == 88 and r["n2"] == 88 and r["n_total"] == 176
    assert r["df"] == 174
    assert close(r["ncp"], 3.3166248)
    assert close(r["critical_t"], 1.6536580)
    assert close(r["actual_power"], 0.9514254)


def test_post_hoc_contract_example():
    r = engine.solve_post_hoc(d=0.5, alpha=0.05, n1=88, n2=88, tails=1)
    assert r["df"] == 174
    assert close(r["ncp"], 3.3166248)
    assert close(r["critical_t"], 1.6536580)
    assert close(r["power"], 0.9514254)


def test_compromise_contract_example():
    r = engine.solve_compromise(d=0.5, beta_alpha_ratio=1, n1=88, n2=88, tails=1)
    assert close(r["ncp"], 3.3166248)
    assert close(r["critical_t"], 1.6606859)
    assert close(r["alpha"], 0.0492887)
    assert close(r["beta"], 0.0492887)
    assert close(r["power"], 0.9507113)


def test_criterion_contract_example():
    r = engine.solve_criterion(d=0.5, power=0.95, n1=88, n2=88, tails=1)
    assert close(r["ncp"], 3.3166248)
    assert close(r["critical_t"], 1.6676050)
    assert close(r["alpha"], 0.0485965)


def test_sensitivity_contract_example():
    r = engine.solve_sensitivity(alpha=0.05, power=0.95, n1=88, n2=88, tails=1)
    assert close(r["ncp"], 3.3025887)
    assert close(r["critical_t"], 1.6536580)
    assert close(r["d"], 0.4978840)


def test_a_priori_tiny_effect_size_no_hang():
    # SPEC.md A: d -> 0 must not overflow/hang, must give a (large) finite N
    r = engine.solve_a_priori(d=0.01, alpha=0.05, power=0.8, tails=2, ratio=1)
    assert r["n1"] > 1000
    assert math.isfinite(r["n_total"])


def test_a_priori_huge_effect_size_small_valid_n():
    r = engine.solve_a_priori(d=5.0, alpha=0.05, power=0.8, tails=2, ratio=1)
    assert r["df"] >= 1
    assert r["n1"] >= 2 and r["n2"] >= 2


def test_a_priori_power_near_alpha_clamps_to_minimum():
    # SPEC.md A: degenerate power barely above alpha -> CONTRACT.md section 5
    # floor (n1,n2 >= 2) must hold, never a crash or n<2.
    r = engine.solve_a_priori(d=0.5, alpha=0.05, power=0.06, tails=2, ratio=1)
    assert r["n1"] >= 2 and r["n2"] >= 2


@pytest.mark.parametrize("ratio", [0.1, 0.5, 2, 3, 10])
def test_a_priori_unequal_ratio_respects_allocation_direction(ratio):
    r = engine.solve_a_priori(d=0.5, alpha=0.05, power=0.8, tails=2, ratio=ratio)
    # ratio = n2/n1 by CONTRACT.md 4.1; direction must hold even though the
    # exact rounded integers can be off by one (ASSUMPTIONS.md section 1).
    if ratio > 1:
        assert r["n2"] > r["n1"]
    elif ratio < 1:
        assert r["n1"] > r["n2"]
    assert r["n1"] >= 2 and r["n2"] >= 2


def test_ncp_formula_matches_definition():
    assert close(engine.ncp(88, 88, 0.5), 0.5 * math.sqrt(88 * 88 / 176))


def test_df_is_n1_plus_n2_minus_2():
    assert engine.df(48, 96) == 142
