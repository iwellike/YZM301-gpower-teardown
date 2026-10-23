"""One-off probe: for the known-mismatch apriori_ratio_3 oracle row
(tails=2, d=0.5, alpha=0.05, power=0.8, ratio=3 -> n1=43, n2=127),
read the real a-priori output AND the real post-hoc output at n1=43,
n2=128 (one more than G*Power's own a-priori answer), to check whether
128 also satisfies the power target (which would show G*Power picked
127 deliberately, not because 128 fails) or whether G*Power's own power
calc at (43,128) differs from scipy's. Scratch script, not a deliverable.
"""
import sys
import time
import json

from pywinauto import Application

FIELD_IDS_APRIORI = {
    "tails": "1040", "d": "1021", "alpha": "1022", "power": "1023", "ratio": "1024",
    "out_ncp": "1050", "out_critical_t": "1051", "out_df": "1052",
    "out_n1": "1053", "out_n2": "1054", "out_n_total": "1055", "out_actual_power": "1056",
}
MODE_APRIORI = "A priori: Compute required sample size - given α, power, and effect size"
MODE_POSTHOC = "Post hoc: Compute achieved power - given α, sample size, and effect size"
TAILS_TEXT = {1: "One", 2: "Two"}


def wait(s=0.3):
    time.sleep(s)


def read_outputs(win, keys):
    out = {}
    for key in keys:
        e = win.child_window(auto_id=FIELD_IDS_APRIORI[f"out_{key}"], control_type="Edit")
        out[key] = e.get_value() if hasattr(e, "get_value") else e.window_text()
    return out


def main():
    app = Application(backend="uia").connect(title="G*Power 3.1.9.7", timeout=30)
    win = app.window(title="G*Power 3.1.9.7")
    win.wait("visible", timeout=30)
    win.child_window(auto_id="1000", control_type="ComboBox").select("t tests")
    wait()
    win.child_window(auto_id="1001", control_type="ComboBox").select(
        "Means: Difference between two independent means (two groups)")
    wait()

    # --- a-priori probe ---
    win.child_window(auto_id="1002", control_type="ComboBox").select(MODE_APRIORI)
    wait(0.4)
    win.child_window(auto_id=FIELD_IDS_APRIORI["tails"], control_type="ComboBox").select(TAILS_TEXT[2])
    wait()
    for key, val in (("d", 0.5), ("alpha", 0.05), ("power", 0.8), ("ratio", 3)):
        e = win.child_window(auto_id=FIELD_IDS_APRIORI[key], control_type="Edit")
        e.set_edit_text(str(val))
        wait(0.1)
    win.child_window(auto_id="1009", control_type="Button").click()
    wait(1.0)
    apriori_out = read_outputs(win, ("ncp", "critical_t", "df", "n1", "n2", "n_total", "actual_power"))
    print("APRIORI_RATIO3", apriori_out)

    # --- post-hoc probes: n1=43 with n2=127 (oracle's own answer) AND n2=128 ---
    win.child_window(auto_id="1002", control_type="ComboBox").select(MODE_POSTHOC)
    wait(0.4)
    win.child_window(auto_id="1040", control_type="ComboBox").select(TAILS_TEXT[2])
    wait()
    posthoc_ids = {"d": "1021", "alpha": "1022", "n1": "1023", "n2": "1024"}
    posthoc_out_ids = {"ncp": "1050", "critical_t": "1051", "df": "1052", "power": "1053"}

    def run_posthoc(n1, n2):
        for key, val in (("d", 0.5), ("alpha", 0.05), ("n1", n1), ("n2", n2)):
            e = win.child_window(auto_id=posthoc_ids[key], control_type="Edit")
            e.set_edit_text(str(val))
            wait(0.1)
        win.child_window(auto_id="1009", control_type="Button").click()
        wait(0.6)
        out = {}
        for key, aid in posthoc_out_ids.items():
            e = win.child_window(auto_id=aid, control_type="Edit")
            out[key] = e.get_value() if hasattr(e, "get_value") else e.window_text()
        return out

    posthoc_127 = run_posthoc(43, 127)
    print("POSTHOC_43_127", posthoc_127)
    posthoc_128 = run_posthoc(43, 128)
    print("POSTHOC_43_128", posthoc_128)
    posthoc_out = {"n1_43_n2_127": posthoc_127, "n1_43_n2_128": posthoc_128}

    with open("docs/probe_ratio3.json", "w", encoding="utf-8") as f:
        json.dump({"apriori_ratio3": apriori_out, "posthoc_43_128_raw": posthoc_out}, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
