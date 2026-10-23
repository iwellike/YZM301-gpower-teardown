"""gpower-clone CLI for the t2-indep test family. Thin wrapper around
src.engine.t2_indep: parses CONTRACT.md's --field value arguments, validates
them per CONTRACT.md section 5, calls the engine, and prints the CLI's
JSON contract (section 2.3/2.4). No calculation logic lives here.
"""
import json
import platform
import sys

from src.engine import t2_indep as engine

CONTRACT_VERSION = "1.0.0"
TEAM_NAME = "melike-tikir-k1"

FIELD_TYPES = {
    "tails": "int", "d": "float", "alpha": "float", "power": "float",
    "ratio": "float", "beta_alpha_ratio": "float", "n1": "int", "n2": "int",
}

MODE_INPUTS = {
    "a-priori": ["tails", "d", "alpha", "power", "ratio"],
    "post-hoc": ["tails", "d", "alpha", "n1", "n2"],
    "compromise": ["tails", "d", "beta_alpha_ratio", "n1", "n2"],
    "criterion": ["tails", "d", "power", "n1", "n2"],
    "sensitivity": ["tails", "alpha", "power", "n1", "n2"],
}


class CliError(Exception):
    def __init__(self, code, field, message):
        super().__init__(message)
        self.code = code
        self.field = field
        self.message = message


def _parse_field(name, raw):
    kind = FIELD_TYPES[name]
    if kind == "int":
        try:
            if "." in raw or "e" in raw.lower():
                raise ValueError
            val = int(raw)
        except ValueError:
            raise CliError("INVALID_VALUE", name, f"{name} tam sayı olmalı")
    else:
        try:
            val = float(raw)
        except ValueError:
            raise CliError("INVALID_VALUE", name, f"{name} sayı olmalı")
    _check_range(name, val)
    return val


def _check_range(name, val):
    ok = True
    if name == "tails":
        ok = val in (1, 2)
    elif name in ("alpha", "power"):
        ok = 0 < val < 1
    elif name in ("d", "ratio", "beta_alpha_ratio"):
        ok = val > 0
    elif name in ("n1", "n2"):
        ok = val >= 2
    if not ok:
        raise CliError("OUT_OF_RANGE", name, f"{name} geçerli aralığın dışında")


def _parse_argv(argv):
    args = {}
    i = 0
    while i < len(argv):
        tok = argv[i]
        if not tok.startswith("--"):
            raise CliError("INVALID_VALUE", None, f"Beklenmeyen argüman: {tok}")
        name = tok[2:]
        if i + 1 >= len(argv):
            raise CliError("MISSING_PARAM", name, f"--{name} için değer verilmedi")
        args[name] = argv[i + 1]
        i += 2
    return args


def run(argv):
    if "--version" in argv:
        return {"contract_version": CONTRACT_VERSION, "name": TEAM_NAME,
                "engine": f"python {platform.python_version()}"}, 0

    args = _parse_argv(argv)

    test = args.pop("test", None)
    mode = args.pop("mode", None)
    if test is None:
        raise CliError("MISSING_PARAM", "test", "--test verilmedi")
    if mode is None:
        raise CliError("MISSING_PARAM", "mode", "--mode verilmedi")
    if test != "t2-indep":
        raise CliError("UNSUPPORTED", "test", f"Desteklenmeyen test: {test}")
    if mode not in MODE_INPUTS:
        raise CliError("UNSUPPORTED", "mode", f"Desteklenmeyen mod: {mode}")

    required = MODE_INPUTS[mode]
    for name in args:
        if name not in required:
            raise CliError("UNKNOWN_PARAM", name, f"{name} bu modla ilgisiz")
    for name in required:
        if name not in args:
            raise CliError("MISSING_PARAM", name, f"--{name} verilmedi")

    parsed = {name: _parse_field(name, args[name]) for name in required}

    if mode in ("a-priori", "sensitivity") and parsed["power"] <= parsed["alpha"]:
        raise CliError("INCONSISTENT", "power", "Power, alpha değerinden büyük olmalı")

    try:
        if mode == "a-priori":
            result = engine.solve_a_priori(parsed["d"], parsed["alpha"], parsed["power"],
                                            parsed["tails"], parsed["ratio"])
        elif mode == "post-hoc":
            result = engine.solve_post_hoc(parsed["d"], parsed["alpha"], parsed["n1"],
                                            parsed["n2"], parsed["tails"])
        elif mode == "compromise":
            result = engine.solve_compromise(parsed["d"], parsed["beta_alpha_ratio"],
                                              parsed["n1"], parsed["n2"], parsed["tails"])
        elif mode == "criterion":
            result = engine.solve_criterion(parsed["d"], parsed["power"], parsed["n1"],
                                             parsed["n2"], parsed["tails"])
        else:
            result = engine.solve_sensitivity(parsed["alpha"], parsed["power"],
                                               parsed["n1"], parsed["n2"], parsed["tails"])
    except engine.EngineError as exc:
        raise CliError(exc.code, exc.field, exc.message)

    if "critical_t" in result:
        result["critical"] = result["critical_t"]  # ödev metnindeki örnek anahtar adıyla uyum (CONTRACT.md 4.3)
    return result, 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    try:
        result, code = run(argv)
    except CliError as exc:
        print(json.dumps({"error": exc.message, "code": exc.code, "field": exc.field}))
        return 1 if exc.code == "NO_SOLUTION" else 2
    print(json.dumps(result))
    return code
