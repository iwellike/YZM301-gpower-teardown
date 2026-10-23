"""
G*Power 3.1.9.7 - t2-indep (two independent means) oracle toplayici.

G*Power'in calisiyor ve 'G*Power 3.1.9.7' basligiyla acik olmasini bekler.
pywinauto (UIA backend) ile Test family/Statistical test/Type of power analysis
kombo kutularini ve girdi alanlarini doldurur, Calculate'a basar, cikti
alanlarini okur ve pencerenin ekran goruntusunu alir.

Kullanim:
    python collect_vectors.py
Cikti:
    oracle/t2_indep_vectors.csv
    oracle/screenshots/<vector_id>.png
"""
import csv
import sys
import io
import time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

from pywinauto import Application
from pywinauto.keyboard import send_keys

HERE = Path(__file__).parent
SHOT_DIR = HERE / "screenshots"
SHOT_DIR.mkdir(exist_ok=True)
CSV_PATH = HERE / "t2_indep_vectors.csv"

MODE_TEXT = {
    "a-priori": "A priori: Compute required sample size - given α, power, and effect size",
    "post-hoc": "Post hoc: Compute achieved power - given α, sample size, and effect size",
    "compromise": "Compromise: Compute implied α & power - given β/α ratio, sample size, and effect size",
    "criterion": "Criterion: Compute required α - given power, effect size, and sample size",
    "sensitivity": "Sensitivity: Compute required effect size - given α, power, and sample size",
}
TAILS_TEXT = {1: "One", 2: "Two"}

# auto_id haritasi mod'a gore degisir; a-priori icin gozlemlenen id'ler asagidaki
# gibidir (bkz. prompts/ ve LEDGER.md'deki GUI kesif notlari). Diger modlarda
# cikti/girdi id'leri degisebilir; once_per_mode ile tazeleniyoruz.
FIELD_IDS_APRIORI = {
    "tails": "1040", "d": "1021", "alpha": "1022", "power": "1023", "ratio": "1024",
    "out_ncp": "1050", "out_critical_t": "1051", "out_df": "1052",
    "out_n1": "1053", "out_n2": "1054", "out_n_total": "1055", "out_actual_power": "1056",
}
FIELD_IDS_POSTHOC = {
    "tails": "1040", "d": "1021", "alpha": "1022", "n1": "1023", "n2": "1024",
    "out_ncp": "1050", "out_critical_t": "1051", "out_df": "1052", "out_power": "1053",
}

VECTORS = [
    # --- a-priori: CONTRACT.md orneğiyle dogrulama (tam eslesme beklenir) ---
    {"id": "apriori_contract_check", "mode": "a-priori", "tails": 1, "d": 0.5, "alpha": 0.05, "power": 0.95, "ratio": 1},
    # --- a-priori: kuyruk ---
    {"id": "apriori_2tail_medium", "mode": "a-priori", "tails": 2, "d": 0.5, "alpha": 0.05, "power": 0.95, "ratio": 1},
    # --- a-priori: etki buyuklugu uclari ---
    {"id": "apriori_d_tiny", "mode": "a-priori", "tails": 2, "d": 0.01, "alpha": 0.05, "power": 0.80, "ratio": 1},
    {"id": "apriori_d_huge", "mode": "a-priori", "tails": 2, "d": 5.0, "alpha": 0.05, "power": 0.80, "ratio": 1},
    {"id": "apriori_d_small_cohen", "mode": "a-priori", "tails": 2, "d": 0.2, "alpha": 0.05, "power": 0.80, "ratio": 1},
    {"id": "apriori_d_large_cohen", "mode": "a-priori", "tails": 2, "d": 0.8, "alpha": 0.05, "power": 0.80, "ratio": 1},
    # --- a-priori: alpha varyasyonu ---
    {"id": "apriori_alpha_001", "mode": "a-priori", "tails": 2, "d": 0.5, "alpha": 0.01, "power": 0.80, "ratio": 1},
    {"id": "apriori_alpha_010", "mode": "a-priori", "tails": 2, "d": 0.5, "alpha": 0.10, "power": 0.80, "ratio": 1},
    # --- a-priori: power varyasyonu ---
    {"id": "apriori_power_80", "mode": "a-priori", "tails": 2, "d": 0.5, "alpha": 0.05, "power": 0.80, "ratio": 1},
    {"id": "apriori_power_90", "mode": "a-priori", "tails": 2, "d": 0.5, "alpha": 0.05, "power": 0.90, "ratio": 1},
    {"id": "apriori_power_99", "mode": "a-priori", "tails": 2, "d": 0.5, "alpha": 0.05, "power": 0.99, "ratio": 1},
    {"id": "apriori_power_near_alpha", "mode": "a-priori", "tails": 2, "d": 0.5, "alpha": 0.05, "power": 0.06, "ratio": 1},
    # --- a-priori: esit olmayan oran ---
    {"id": "apriori_ratio_2", "mode": "a-priori", "tails": 2, "d": 0.5, "alpha": 0.05, "power": 0.80, "ratio": 2},
    {"id": "apriori_ratio_0_5", "mode": "a-priori", "tails": 2, "d": 0.5, "alpha": 0.05, "power": 0.80, "ratio": 0.5},
    {"id": "apriori_ratio_3", "mode": "a-priori", "tails": 2, "d": 0.5, "alpha": 0.05, "power": 0.80, "ratio": 3},
    {"id": "apriori_ratio_10", "mode": "a-priori", "tails": 2, "d": 0.5, "alpha": 0.05, "power": 0.80, "ratio": 10},
    {"id": "apriori_ratio_0_1", "mode": "a-priori", "tails": 2, "d": 0.5, "alpha": 0.05, "power": 0.80, "ratio": 0.1},
    # --- ek kombinasyonlar (cesitlilik icin) ---
    {"id": "apriori_mix1", "mode": "a-priori", "tails": 1, "d": 0.3, "alpha": 0.05, "power": 0.85, "ratio": 1.5},
    {"id": "apriori_mix2", "mode": "a-priori", "tails": 2, "d": 0.7, "alpha": 0.01, "power": 0.90, "ratio": 1},
    {"id": "apriori_mix3", "mode": "a-priori", "tails": 1, "d": 0.4, "alpha": 0.10, "power": 0.95, "ratio": 2},
    {"id": "apriori_mix4", "mode": "a-priori", "tails": 2, "d": 1.2, "alpha": 0.05, "power": 0.80, "ratio": 1},
    {"id": "apriori_mix5", "mode": "a-priori", "tails": 2, "d": 0.5, "alpha": 0.05, "power": 0.975, "ratio": 1},
    {"id": "apriori_mix6", "mode": "a-priori", "tails": 1, "d": 0.5, "alpha": 0.001, "power": 0.80, "ratio": 1},
    {"id": "apriori_mix7", "mode": "a-priori", "tails": 2, "d": 0.5, "alpha": 0.05, "power": 0.80, "ratio": 4},
    {"id": "apriori_mix8", "mode": "a-priori", "tails": 2, "d": 0.15, "alpha": 0.05, "power": 0.80, "ratio": 1},
    {"id": "apriori_mix9", "mode": "a-priori", "tails": 1, "d": 0.6, "alpha": 0.05, "power": 0.80, "ratio": 0.75},
    {"id": "apriori_mix10", "mode": "a-priori", "tails": 2, "d": 0.5, "alpha": 0.2, "power": 0.80, "ratio": 1},
    {"id": "apriori_mix11", "mode": "a-priori", "tails": 2, "d": 2.5, "alpha": 0.05, "power": 0.80, "ratio": 1},
    {"id": "apriori_mix12", "mode": "a-priori", "tails": 2, "d": 0.5, "alpha": 0.05, "power": 0.80, "ratio": 1.25},
]


def wait(sec=0.25):
    time.sleep(sec)


def connect():
    app = Application(backend="uia").connect(title="G*Power 3.1.9.7")
    return app.window(title="G*Power 3.1.9.7")


def ensure_t2_indep(win):
    win.child_window(auto_id="1000", control_type="ComboBox").select("t tests")
    wait()
    win.child_window(auto_id="1001", control_type="ComboBox").select(
        "Means: Difference between two independent means (two groups)"
    )
    wait()


def set_mode(win, mode):
    win.child_window(auto_id="1002", control_type="ComboBox").select(MODE_TEXT[mode])
    wait(0.4)


def set_edit(win, auto_id, value):
    e = win.child_window(auto_id=auto_id, control_type="Edit")
    e.set_edit_text(str(value))
    wait(0.1)


def get_edit(win, auto_id):
    e = win.child_window(auto_id=auto_id, control_type="Edit")
    # window_text() pencere/kontrol ADINI dondurebilir (orn. "Parameter 11");
    # gercek deger icin UIA ValuePattern (get_value) kullanilmali.
    return e.get_value() if hasattr(e, "get_value") else e.window_text()


def screenshot(win, name):
    img = win.capture_as_image()
    img.save(str(SHOT_DIR / f"{name}.png"))


def run_apriori(win, v):
    win.child_window(auto_id=FIELD_IDS_APRIORI["tails"], control_type="ComboBox").select(TAILS_TEXT[v["tails"]])
    wait()
    set_edit(win, FIELD_IDS_APRIORI["d"], v["d"])
    set_edit(win, FIELD_IDS_APRIORI["alpha"], v["alpha"])
    set_edit(win, FIELD_IDS_APRIORI["power"], v["power"])
    set_edit(win, FIELD_IDS_APRIORI["ratio"], v["ratio"])
    win.child_window(auto_id="1009", control_type="Button").click()
    wait(0.5)
    out = {
        "ncp": get_edit(win, FIELD_IDS_APRIORI["out_ncp"]),
        "critical_t": get_edit(win, FIELD_IDS_APRIORI["out_critical_t"]),
        "df": get_edit(win, FIELD_IDS_APRIORI["out_df"]),
        "n1": get_edit(win, FIELD_IDS_APRIORI["out_n1"]),
        "n2": get_edit(win, FIELD_IDS_APRIORI["out_n2"]),
        "n_total": get_edit(win, FIELD_IDS_APRIORI["out_n_total"]),
        "actual_power": get_edit(win, FIELD_IDS_APRIORI["out_actual_power"]),
    }
    return out


def main():
    win = connect()
    ensure_t2_indep(win)

    rows = []
    current_mode = None
    for v in VECTORS:
        if v["mode"] != current_mode:
            set_mode(win, v["mode"])
            current_mode = v["mode"]
        try:
            if v["mode"] == "a-priori":
                out = run_apriori(win, v)
            else:
                raise NotImplementedError(f"mode {v['mode']} henuz eklenmedi")
        except Exception as e:
            print(f"[HATA] {v['id']}: {e}", file=sys.stderr)
            continue

        screenshot(win, v["id"])
        row = {"id": v["id"], "mode": v["mode"], **{f"in_{k}": val for k, val in v.items() if k not in ("id", "mode")}, **{f"out_{k}": val for k, val in out.items()}}
        rows.append(row)
        print(v["id"], "->", out)

    if rows:
        fieldnames = list(rows[0].keys())
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"\n{len(rows)} vektor yazildi -> {CSV_PATH}")


if __name__ == "__main__":
    main()
