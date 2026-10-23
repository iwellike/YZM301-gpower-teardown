"""gpower-clone MCP server (CONTRACT.md section 7, bonus layer).

Single tool, power_analysis. No calculation or validation logic lives
here: every call is forwarded to src.cli.core.run(argv), the exact same
function the CLI's __main__ uses, built from the same --field value
tokens. This makes CLI/MCP equivalence true by construction rather than
by coincidence; tests/test_mcp.py checks it anyway for the 5 t2-indep
public vectors (CONTRACT.md section 7: "Esdegerlik testi zorunlu").
"""
import json

from mcp.server.mcpserver import MCPServer

from src.cli.core import run

server = MCPServer("gpower-clone")

_FIELDS = ["tails", "d", "alpha", "power", "ratio", "beta_alpha_ratio", "n1", "n2"]


@server.tool()
def power_analysis(
    test: str,
    mode: str,
    tails: str | None = None,
    d: str | None = None,
    alpha: str | None = None,
    power: str | None = None,
    ratio: str | None = None,
    beta_alpha_ratio: str | None = None,
    n1: str | None = None,
    n2: str | None = None,
) -> str:
    """Run a gpower-clone power analysis. Same field names and JSON output
    as the CLI (CONTRACT.md section 4); test/mode are required, the rest
    become required or forbidden depending on the chosen mode."""
    local = {"tails": tails, "d": d, "alpha": alpha, "power": power, "ratio": ratio,
              "beta_alpha_ratio": beta_alpha_ratio, "n1": n1, "n2": n2}
    argv = ["--test", test, "--mode", mode]
    for name in _FIELDS:
        value = local[name]
        if value is not None:
            argv += [f"--{name}", str(value)]
    try:
        result, _code = run(argv)
    except Exception as exc:  # noqa: BLE001 - mirror the CLI's own error JSON
        code = getattr(exc, "code", "NO_SOLUTION")
        field = getattr(exc, "field", None)
        message = getattr(exc, "message", str(exc))
        return json.dumps({"error": message, "code": code, "field": field})
    return json.dumps(result)


if __name__ == "__main__":
    server.run()
