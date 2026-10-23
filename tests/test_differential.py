"""Differential tests against real G*Power output.

1. oracle/public_vectors.jsonl: the 25 vectors from CONTRACT.md section 9
   (public/known). Only the 5 t2-indep rows are in scope for this sprint.
2. oracle/t2_indep_vectors.csv: 29 a-priori vectors collected directly from
   the G*Power 3.1.9.7 GUI (oracle/collect_vectors.py), including boundary
   and unequal-ratio cases that are NOT in the public set.

CONTRACT.md section 6 ("Kapı") requires >=90% exact n1/n2/n_total match on
the hidden a-priori vectors. ASSUMPTIONS.md section 1 documents that our
ceil()-based rounding rule (REA-confirmed in LEDGER.md) hits 100% on
ratio=1 and ~79% overall on this practice set; the floor below is a
regression guard, not a claim of meeting the contract gate.
"""
import csv
import json
from pathlib import Path

import pytest

from src.engine import t2_indep as engine

ROOT = Path(__file__).resolve().parents[1]
TOL = 1e-6


def close(a, b, tol=TOL):
    return abs(a - b) <= tol or abs(a - b) <= tol * max(abs(a), abs(b), 1.0)


def _load_public_vectors():
    rows = []
    with open(ROOT / "oracle" / "public_vectors.jsonl") as f:
        for line in f:
            row = json.loads(line)
            if row["input"]["test"] == "t2-indep":
                rows.append(row)
    return rows


MODE_SOLVERS = {
    "a-priori": lambda i: engine.solve_a_priori(i["d"], i["alpha"], i["power"], i["tails"], i["ratio"]),
    "post-hoc": lambda i: engine.solve_post_hoc(i["d"], i["alpha"], i["n1"], i["n2"], i["tails"]),
    "compromise": lambda i: engine.solve_compromise(i["d"], i["beta_alpha_ratio"], i["n1"], i["n2"], i["tails"]),
    "criterion": lambda i: engine.solve_criterion(i["d"], i["power"], i["n1"], i["n2"], i["tails"]),
    "sensitivity": lambda i: engine.solve_sensitivity(i["alpha"], i["power"], i["n1"], i["n2"], i["tails"]),
}


@pytest.mark.parametrize("row", _load_public_vectors(), ids=lambda r: r["id"])
def test_public_vector(row):
    result = MODE_SOLVERS[row["input"]["mode"]](row["input"])
    for key, expected in row["expected"].items():
        got = result[key]
        if key in ("n1", "n2", "n_total", "df"):
            assert got == expected, f"{row['id']}.{key}: got {got} expected {expected}"
        else:
            assert close(got, expected), f"{row['id']}.{key}: got {got} expected {expected}"


def test_practice_oracle_n_match_rate():
    path = ROOT / "oracle" / "t2_indep_vectors.csv"
    rows = list(csv.DictReader(open(path)))
    matches = 0
    for row in rows:
        r = engine.solve_a_priori(
            d=float(row["in_d"]), alpha=float(row["in_alpha"]),
            power=float(row["in_power"]), tails=int(row["in_tails"]),
            ratio=float(row["in_ratio"]),
        )
        if (r["n1"], r["n2"], r["n_total"]) == (
            int(row["out_n1"]), int(row["out_n2"]), int(row["out_n_total"]),
        ):
            matches += 1
    rate = matches / len(rows)
    # Regression guard, not the CONTRACT.md 90% gate (see ASSUMPTIONS.md 1).
    assert rate >= 0.70, f"N match rate dropped to {rate:.1%} (was ~79.3%)"


def test_practice_oracle_decimal_fields_self_consistent():
    """Whatever n1/n2 the engine picks, its own ncp/critical_t/actual_power
    must be internally consistent (catches formula regressions even on the
    ~20% of rows where the rounded N legitimately differs from G*Power's)."""
    path = ROOT / "oracle" / "t2_indep_vectors.csv"
    rows = list(csv.DictReader(open(path)))
    for row in rows:
        tails, d, alpha = int(row["in_tails"]), float(row["in_d"]), float(row["in_alpha"])
        r = engine.solve_a_priori(d=d, alpha=alpha, power=float(row["in_power"]),
                                   tails=tails, ratio=float(row["in_ratio"]))
        assert close(r["ncp"], engine.ncp(r["n1"], r["n2"], d))
        assert close(r["actual_power"], engine.actual_power(r["n1"], r["n2"], d, alpha, tails))
