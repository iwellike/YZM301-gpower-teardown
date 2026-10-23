"""'Jev' -- the lightweight family classifier for src/agent/run_eval.py.

Deliberately NOT a lookup table against eval_questions.md's "expected"
column (that would make the eval meaningless). These are keyword/regex
heuristics over the raw question text only; CONTRACT.md section 10 is
honored by refusing to silently turn a category word ("orta etki") into a
number -- those cases are flagged for confirmation instead of guessed.
"""
import re

FAMILIES = ["t2-indep", "t-paired", "anova-oneway", "chi2-contingency",
            "multireg-r2", "ambiguous", "unsupported"]

_UNSUPPORTED_KW = ["makine öğrenmesi", "kümele", "ml ", "machine learning", "cluster"]
_PAIRED_KW = ["aynı hastalarda", "aynı kişilerde", "öncesi ve sonrası", "eşleştirilmiş",
              "before/after", "same patients", "matched pairs"]
_EFFECT_KW = ["etki", "d=", "f=", "w=", "f2", "r²", "r2", "büyük", "orta", "küçük",
              "effect", "medium", "small", "large"]
_ALPHA_POWER_KW = ["α", "alpha", "güç", "güc", "power"]  # güç/gücüm: ç->c softens under suffix
_MULTIREG_KW = ["varyans", "açıkla", "risk faktör", "variance", "explain"]
_CHI2_KW = ["oran", "rate", "response rate"]
_GROUPS_RE = re.compile(r"(üç|dört|beş|three|four|five|\d+)\D{0,25}(grup|kol|arm|group)")
_T2INDEP_KW = ["bağımsız grup", "plasebo", "deney/kontrol", "deney ve kontrol",
               "independent group", "placebo", "experimental/control"]


def classify(question: str):
    """Returns (family, confidence) in [0,1]."""
    q = question.lower()
    if any(k in q for k in _UNSUPPORTED_KW):
        return "unsupported", 0.95
    if any(k in q for k in _PAIRED_KW):
        return "t-paired", 0.85
    has_effect = any(k in q for k in _EFFECT_KW)
    has_alpha_power = any(k in q for k in _ALPHA_POWER_KW)
    if not (has_effect and has_alpha_power):
        return "ambiguous", 0.5
    if any(k in q for k in _MULTIREG_KW):
        return "multireg-r2", 0.85
    if any(k in q for k in _CHI2_KW):
        return "chi2-contingency", 0.8
    if _GROUPS_RE.search(q):
        return "anova-oneway", 0.8
    if any(k in q for k in _T2INDEP_KW):
        return "t2-indep", 0.85
    return "ambiguous", 0.4


_EXPLICIT_D_RE = re.compile(r"d\s*=\s*([0-9.]+)")
_ALPHA_RE = re.compile(r"α\s*=\s*([0-9.]+)")
_POWER_RE = re.compile(r"güç\s*([0-9.]+)|power\s*([0-9.]+)")
_N_RE = re.compile(r"(\d+)\s*hast")


def has_explicit_effect_size(question: str) -> bool:
    return bool(_EXPLICIT_D_RE.search(question))


def extract_numeric_hints(question: str) -> dict:
    """Best-effort extraction of explicit numbers the question already
    states. Returns only what is textually explicit -- never a Cohen's
    category default (that would violate CONTRACT.md section 10)."""
    hints = {}
    m = _EXPLICIT_D_RE.search(question)
    if m:
        hints["d"] = float(m.group(1))
    m = _ALPHA_RE.search(question)
    if m:
        hints["alpha"] = float(m.group(1))
    m = _POWER_RE.search(question)
    if m:
        hints["power"] = float(m.group(1) or m.group(2))
    m = _N_RE.search(question)
    if m:
        hints["n_total_hint"] = int(m.group(1))
    if "iki katı" in question.lower() or "twice" in question.lower():
        hints["ratio"] = 2
    if "tek yönlü" in question.lower() or "one-sided" in question.lower() or "daha iyi" in question.lower() or "better" in question.lower():
        hints["tails"] = 1
    elif "fark olup olmadığı" in question.lower() or "any difference" in question.lower():
        hints["tails"] = 2
    return hints
