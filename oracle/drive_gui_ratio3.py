"""One-off: drive the already-spawned (Frida-instrumented) G*Power GUI
through the apriori_ratio_3 case (tails=2, d=0.5, alpha=0.05, power=0.8,
ratio=3 -> real G*Power n1=43, n2=127) while the REA Frida hook on
FUN_004a7140's internal power-callback is capturing every bisection
step. Scratch script, not part of the deliverable test suite.
"""
import time

from pywinauto import Application

FIELD_IDS = {
    "tails": "1040", "d": "1021", "alpha": "1022", "power": "1023", "ratio": "1024",
    "out_ncp": "1050", "out_critical_t": "1051", "out_df": "1052",
    "out_n1": "1053", "out_n2": "1054", "out_n_total": "1055", "out_actual_power": "1056",
}
MODE_TEXT = "A priori: Compute required sample size - given α, power, and effect size"
TAILS_TEXT = {2: "Two"}


def wait(s=0.3):
    time.sleep(s)


def main():
    app = Application(backend="uia").connect(title="G*Power 3.1.9.7", timeout=30)
    win = app.window(title="G*Power 3.1.9.7")
    win.wait("visible", timeout=30)
    win.child_window(auto_id="1000", control_type="ComboBox").select("t tests")
    wait()
    win.child_window(auto_id="1001", control_type="ComboBox").select(
        "Means: Difference between two independent means (two groups)")
    wait()
    win.child_window(auto_id="1002", control_type="ComboBox").select(MODE_TEXT)
    wait(0.4)
    win.child_window(auto_id=FIELD_IDS["tails"], control_type="ComboBox").select(TAILS_TEXT[2])
    wait()
    for key, val in (("d", 0.5), ("alpha", 0.05), ("power", 0.8), ("ratio", 3)):
        e = win.child_window(auto_id=FIELD_IDS[key], control_type="Edit")
        e.set_edit_text(str(val))
        wait(0.1)
    win.child_window(auto_id="1009", control_type="Button").click()
    wait(1.0)
    out = {}
    for key in ("ncp", "critical_t", "df", "n1", "n2", "n_total", "actual_power"):
        e = win.child_window(auto_id=FIELD_IDS[f"out_{key}"], control_type="Edit")
        out[key] = e.get_value() if hasattr(e, "get_value") else e.window_text()
    print("GUI_RESULT", out)


if __name__ == "__main__":
    main()
