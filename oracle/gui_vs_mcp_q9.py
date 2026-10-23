"""One real, timed MCP-vs-GUI comparison for AGENT_COST.md, using eval
question 9 (the only one of the 10 with fully explicit numeric params:
tails=1, d=0.8, alpha=0.01, power=0.9, ratio=2). Requires G*Power already
running (reuses oracle/collect_vectors.py's pywinauto field IDs).
"""
import sys
import io
import time
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from pywinauto import Application

sys.path.insert(0, ".")
from src.mcp.server import power_analysis

FIELD_IDS = {
    "tails": "1040", "d": "1021", "alpha": "1022", "power": "1023", "ratio": "1024",
    "out_ncp": "1050", "out_critical_t": "1051", "out_df": "1052",
    "out_n1": "1053", "out_n2": "1054", "out_n_total": "1055", "out_actual_power": "1056",
}
MODE_TEXT = "A priori: Compute required sample size - given α, power, and effect size"
TAILS_TEXT = {1: "One", 2: "Two"}


def wait(s=0.25):
    time.sleep(s)


def run_mcp():
    t0 = time.perf_counter()
    out = power_analysis(test="t2-indep", mode="a-priori", tails="1", d="0.8",
                          alpha="0.01", power="0.9", ratio="2")
    t1 = time.perf_counter()
    return json.loads(out), t1 - t0


def run_gui():
    t0 = time.perf_counter()
    app = Application(backend="uia").connect(title="G*Power 3.1.9.7")
    win = app.window(title="G*Power 3.1.9.7")
    win.child_window(auto_id="1000", control_type="ComboBox").select("t tests")
    wait()
    win.child_window(auto_id="1001", control_type="ComboBox").select(
        "Means: Difference between two independent means (two groups)")
    wait()
    win.child_window(auto_id="1002", control_type="ComboBox").select(MODE_TEXT)
    wait(0.4)
    win.child_window(auto_id=FIELD_IDS["tails"], control_type="ComboBox").select(TAILS_TEXT[1])
    wait()
    for key, val in (("d", 0.8), ("alpha", 0.01), ("power", 0.9), ("ratio", 2)):
        e = win.child_window(auto_id=FIELD_IDS[key], control_type="Edit")
        e.set_edit_text(str(val))
        wait(0.1)
    win.child_window(auto_id="1009", control_type="Button").click()
    wait(0.5)
    out = {}
    for key in ("ncp", "critical_t", "df", "n1", "n2", "n_total", "actual_power"):
        e = win.child_window(auto_id=FIELD_IDS[f"out_{key}"], control_type="Edit")
        out[key] = e.get_value() if hasattr(e, "get_value") else e.window_text()
    img = win.capture_as_image()
    img.save("docs/gui_vs_mcp_q9.png")
    t1 = time.perf_counter()
    return out, t1 - t0


if __name__ == "__main__":
    mcp_out, mcp_time = run_mcp()
    print("MCP:", mcp_out, f"{mcp_time*1000:.1f}ms")
    gui_out, gui_time = run_gui()
    print("GUI:", gui_out, f"{gui_time:.2f}s")

    with open("docs/gui_vs_mcp_q9.json", "w", encoding="utf-8") as f:
        json.dump({"question_id": 9, "mcp": {"output": mcp_out, "seconds": mcp_time},
                    "gui": {"output": gui_out, "seconds": gui_time}}, f, indent=2, ensure_ascii=False)
