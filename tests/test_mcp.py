"""CLI/MCP equivalence (CONTRACT.md section 7: zorunlu for the 5 t2-indep
public vectors). Both call src.cli.core.run, so this mostly guards against
the MCP wrapper itself introducing a discrepancy (argv construction, type
coercion), not against engine drift -- that's covered by test_differential.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.mcp.server import power_analysis

ROOT = Path(__file__).resolve().parents[1]


def _load_t2indep_public_vectors():
    rows = []
    with open(ROOT / "oracle" / "public_vectors.jsonl") as f:
        for line in f:
            row = json.loads(line)
            if row["input"]["test"] == "t2-indep":
                rows.append(row)
    return rows


def _cli_output(input_dict):
    args = ["--test", input_dict["test"], "--mode", input_dict["mode"]]
    for k, v in input_dict.items():
        if k in ("test", "mode"):
            continue
        args += [f"--{k}", str(v)]
    proc = subprocess.run([sys.executable, "-m", "src.cli", *args],
                           cwd=ROOT, capture_output=True, text=True, timeout=10)
    return proc.stdout.strip()


@pytest.mark.parametrize("row", _load_t2indep_public_vectors(), ids=lambda r: r["id"])
def test_cli_mcp_equivalence(row):
    cli_out = _cli_output(row["input"])
    mcp_kwargs = {k: str(v) for k, v in row["input"].items()}
    mcp_out = power_analysis(**mcp_kwargs)
    assert json.loads(cli_out) == json.loads(mcp_out), (cli_out, mcp_out)


def test_mcp_error_shape_matches_cli():
    cli_out = _cli_output({"test": "t2-indep", "mode": "a-priori", "tails": "1",
                            "d": "0.5", "alpha": "0", "power": "0.95", "ratio": "1"})
    mcp_out = power_analysis(test="t2-indep", mode="a-priori", tails="1", d="0.5",
                              alpha="0", power="0.95", ratio="1")
    assert json.loads(cli_out) == json.loads(mcp_out)
