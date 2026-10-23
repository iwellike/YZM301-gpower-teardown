"""
Olcek-kahini: statsmodels ile t2-indep (iki bagimsiz ortalama) icin 500+
sistematik vektor uretir. Bu, G*Power'in GERCEK ciktisi degildir (kahin
G*Power'in kendisidir, bkz. CONTRACT.md) -- yalnizca BUYUK OLCEKTE hesap
dogrulugunu test etmek icin ikinci bir bagimsiz kaynaktir.

Onemli bulgu (ödev notu c): statsmodels N'yi KESIRLI dondurur
(solve_power ile), G*Power ise yukari yuvarlar (REA ile dogrulanacak).
Bu script her iki degeri de kaydeder; fark ayri bir sutunda raporlanir.
"""
import csv
import itertools
import math
from pathlib import Path

from statsmodels.stats.power import TTestIndPower

HERE = Path(__file__).parent
OUT = HERE / "statsmodels_scale_vectors.csv"

analysis = TTestIndPower()

TAILS = [1, 2]
D_VALUES = [0.1, 0.2, 0.3, 0.5, 0.8, 1.0, 1.5, 2.0]
ALPHAS = [0.01, 0.05, 0.10]
POWERS = [0.80, 0.90, 0.95, 0.99]
RATIOS = [1.0, 0.5, 2.0, 1.5]


def alternative_for(tails):
    return "two-sided" if tails == 2 else "larger"


def main():
    rows = []
    for tails, d, alpha, power, ratio in itertools.product(TAILS, D_VALUES, ALPHAS, POWERS, RATIOS):
        alt = alternative_for(tails)
        try:
            n1_frac = analysis.solve_power(
                effect_size=d, alpha=alpha, power=power, ratio=ratio, alternative=alt
            )
        except Exception as e:
            rows.append({
                "tails": tails, "d": d, "alpha": alpha, "power": power, "ratio": ratio,
                "statsmodels_n1_fractional": None, "ceil_n1": None, "ceil_n2": None,
                "error": str(e),
            })
            continue

        n1_ceil = math.ceil(n1_frac)
        n2_ceil = math.ceil(n1_frac * ratio)
        rows.append({
            "tails": tails, "d": d, "alpha": alpha, "power": power, "ratio": ratio,
            "statsmodels_n1_fractional": n1_frac,
            "ceil_n1": n1_ceil, "ceil_n2": n2_ceil,
            "ceil_n_total": n1_ceil + n2_ceil,
            "error": "",
        })

    fieldnames = list(rows[0].keys())
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} vektor yazildi -> {OUT}")


if __name__ == "__main__":
    main()
