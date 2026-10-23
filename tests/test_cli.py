"""CLI contract tests (CONTRACT.md section 2): stdout is single-line JSON,
exit codes, error code/field correctness. Runs the CLI as a real
subprocess to catch anything a direct-import test would miss (stdout-only
output, exit codes).
"""
import json
import subprocess
import sys

ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]


def run_cli(*args):
    proc = subprocess.run(
        [sys.executable, "-m", "src.cli", *args],
        cwd=ROOT, capture_output=True, text=True, timeout=10,
    )
    return proc


def test_version():
    proc = run_cli("--version")
    assert proc.returncode == 0
    out = json.loads(proc.stdout.strip())
    assert out["contract_version"] == "1.0.0"
    assert "name" in out and "engine" in out


def test_success_single_line_json_exit_0():
    proc = run_cli("--test", "t2-indep", "--mode", "a-priori", "--tails", "1",
                    "--d", "0.5", "--alpha", "0.05", "--power", "0.95", "--ratio", "1")
    assert proc.returncode == 0
    lines = proc.stdout.strip().splitlines()
    assert len(lines) == 1
    out = json.loads(lines[0])
    assert out["n1"] == 88 and out["n2"] == 88 and out["n_total"] == 176
    assert isinstance(out["n1"], int)


def test_missing_param():
    proc = run_cli("--test", "t2-indep", "--mode", "a-priori", "--tails", "1",
                    "--d", "0.5", "--alpha", "0.05", "--ratio", "1")
    assert proc.returncode == 2
    out = json.loads(proc.stdout.strip())
    assert out["code"] == "MISSING_PARAM" and out["field"] == "power"


def test_unknown_param():
    proc = run_cli("--test", "t2-indep", "--mode", "post-hoc", "--tails", "1",
                    "--d", "0.5", "--alpha", "0.05", "--n1", "88", "--n2", "88",
                    "--power", "0.9")
    assert proc.returncode == 2
    out = json.loads(proc.stdout.strip())
    assert out["code"] == "UNKNOWN_PARAM" and out["field"] == "power"


def test_out_of_range_alpha_zero():
    proc = run_cli("--test", "t2-indep", "--mode", "a-priori", "--tails", "1",
                    "--d", "0.5", "--alpha", "0", "--power", "0.95", "--ratio", "1")
    assert proc.returncode == 2
    out = json.loads(proc.stdout.strip())
    assert out["code"] == "OUT_OF_RANGE" and out["field"] == "alpha"


def test_out_of_range_negative_d():
    proc = run_cli("--test", "t2-indep", "--mode", "a-priori", "--tails", "1",
                    "--d", "-0.5", "--alpha", "0.05", "--power", "0.95", "--ratio", "1")
    assert proc.returncode == 2
    out = json.loads(proc.stdout.strip())
    assert out["code"] == "OUT_OF_RANGE" and out["field"] == "d"


def test_invalid_value_non_integer_tails():
    proc = run_cli("--test", "t2-indep", "--mode", "a-priori", "--tails", "1.5",
                    "--d", "0.5", "--alpha", "0.05", "--power", "0.95", "--ratio", "1")
    assert proc.returncode == 2
    out = json.loads(proc.stdout.strip())
    assert out["code"] == "INVALID_VALUE" and out["field"] == "tails"


def test_inconsistent_power_not_greater_than_alpha():
    proc = run_cli("--test", "t2-indep", "--mode", "a-priori", "--tails", "1",
                    "--d", "0.5", "--alpha", "0.5", "--power", "0.3", "--ratio", "1")
    assert proc.returncode == 2
    out = json.loads(proc.stdout.strip())
    assert out["code"] == "INCONSISTENT" and out["field"] == "power"


def test_unsupported_test():
    proc = run_cli("--test", "anova-oneway", "--mode", "a-priori", "--f", "0.25",
                    "--alpha", "0.05", "--power", "0.95", "--groups", "5")
    assert proc.returncode == 2
    out = json.loads(proc.stdout.strip())
    assert out["code"] == "UNSUPPORTED" and out["field"] == "test"


def test_unsupported_mode():
    proc = run_cli("--test", "t2-indep", "--mode", "bogus-mode")
    assert proc.returncode == 2
    out = json.loads(proc.stdout.strip())
    assert out["code"] == "UNSUPPORTED" and out["field"] == "mode"


def test_deterministic_output():
    args = ("--test", "t2-indep", "--mode", "a-priori", "--tails", "1",
            "--d", "0.5", "--alpha", "0.05", "--power", "0.95", "--ratio", "1")
    out1 = run_cli(*args).stdout
    out2 = run_cli(*args).stdout
    assert out1 == out2
