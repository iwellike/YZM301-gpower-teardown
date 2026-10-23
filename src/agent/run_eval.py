"""AI agent layer (CONTRACT.md section 8, bonus). Runs the 10 fictional
research scenarios from eval_questions.md through the 'Jev' classifier
(src/agent/classifier.py) and, when confidence is high enough and the
required numbers are explicit (not a Cohen's category word), calls the
MCP tool for the actual computation -- the agent never computes power
itself. Every call (or abstention) is logged to logs/agent_calls.jsonl in
the exact schema CONTRACT.md section 8 specifies.

Only t2-indep is implemented this sprint (README.md), so questions
classified into the other four families correctly surface the engine's
own UNSUPPORTED error when the tool is called -- that is the real,
honest state of this solo K1 submission, not a scripted success.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from src.agent.classifier import classify, extract_numeric_hints, has_explicit_effect_size
from src.mcp.server import power_analysis

ROOT = Path(__file__).resolve().parents[2]
LOG_PATH = ROOT / "logs" / "agent_calls.jsonl"

CONFIDENCE_THRESHOLD = 0.75

QUESTIONS = [
    {
        "id": 1, "expected_family": "t2-indep",
        "question": "Yeni bir ağrı kesicinin plasebodan daha iyi olduğunu göstermek "
                     "istiyorum. Orta büyüklükte bir etki bekliyorum, α=0.05, güç 0.80. "
                     "Kaç hastaya ihtiyacım var?",
    },
    {
        "id": 2, "expected_family": "t-paired",
        "question": "Aynı hastalarda tedavi öncesi ve sonrası tansiyonu "
                     "karşılaştıracağım, fark olup olmadığını (yön iddia etmeden) test "
                     "edeceğim. Küçük-orta bir etki, α=0.05, güç 0.90.",
    },
    {
        "id": 3, "expected_family": "anova-oneway",
        "question": "Üç farklı tedavi kolunu (A, B, C) karşılaştıracağım, en az ikisi "
                     "arasında fark olup olmadığına bakacağım. Orta etki büyüklüğü, "
                     "α=0.05, güç 0.95.",
    },
    {
        "id": 4, "expected_family": "chi2-contingency",
        "question": "Yeni tedaviye yanıt oranı ile standart tedaviye yanıt oranını 2x2 "
                     "bir tabloda karşılaştırmak istiyorum, orta etki, α=0.05, güç 0.80.",
    },
    {
        "id": 5, "expected_family": "multireg-r2",
        "question": "Üç risk faktörünün (yaş, kilo, sigara) hastalık riskindeki "
                     "varyansı ne kadar açıkladığını göstermek istiyorum, orta etki "
                     "(R²≈0.13), α=0.05, güç 0.80.",
    },
    {
        "id": 6, "expected_family": "t2-indep",
        "question": "Elimde 60 hasta var, yarısı ilaç yarısı plasebo aldı; orta "
                     "büyüklükte bir etki varsa bunu yakalama gücüm nedir?",
    },
    {
        "id": 7, "expected_family": "ambiguous",
        "question": "Hastalarımı iki gruba ayırıp bir anket puanını karşılaştıracağım "
                     "ama kaç kişi gerektiğini bilmiyorum, bana standart bir sayı "
                     "söyler misin?",
    },
    {
        "id": 8, "expected_family": "unsupported",
        "question": "Hastaların genetik profiline göre 5 farklı tedaviye verdikleri "
                     "yanıtı makine öğrenmesiyle kümeleyip kaç kümeye ihtiyacım "
                     "olduğunu bulmak istiyorum.",
    },
    {
        "id": 9, "expected_family": "t2-indep",
        "question": "İki bağımsız grupta (deney/kontrol) ortalama iyileşme süresini "
                     "karşılaştıracağım, etkinin büyük olduğunu düşünüyorum (d=0.8), "
                     "tek yönlü, α=0.01, güç 0.90, kontrol grubunun deney grubunun iki "
                     "katı olmasını planlıyorum.",
    },
    {
        "id": 10, "expected_family": "chi2-contingency",
        "question": "Dört tedavi grubunda yan etki görülme oranlarını karşılaştırıp "
                     "aralarında fark olup olmadığına bakacağım, etkiyi küçük-orta "
                     "varsayıyorum, standart α ve güç kullanacağım.",
    },
]


def run():
    LOG_PATH.parent.mkdir(exist_ok=True)
    log_f = open(LOG_PATH, "w", encoding="utf-8")
    correct = 0
    calibrated_total = 0
    calibrated_correct = 0

    for item in QUESTIONS:
        q = item["question"]
        family, confidence = classify(q)
        is_correct = family == item["expected_family"]
        correct += is_correct
        if confidence >= CONFIDENCE_THRESHOLD:
            calibrated_total += 1
            calibrated_correct += is_correct

        tool_input = None
        tool_output = None
        clarification_needed = None

        if confidence >= CONFIDENCE_THRESHOLD and family not in ("ambiguous", "unsupported"):
            if not has_explicit_effect_size(q) and family != "t2-indep":
                # Other families aren't implemented this sprint anyway; skip
                # the tool call and record why, rather than guess params.
                clarification_needed = "etki büyüklüğü sayısal verilmemiş (kategori kelimesi) + bu aile bu sprintte uygulanmadı"
            elif not has_explicit_effect_size(q):
                clarification_needed = ("etki büyüklüğü 'orta/küçük/büyük' gibi bir kategori, sayı "
                                         "değil -- CONTRACT.md §10 uyarısı: sessizce 0.5 varsayılmadı, "
                                         "araştırmacıya sorulması gerekir")
            else:
                hints = extract_numeric_hints(q)
                tool_input = {"test": family, **hints}
                if family == "t2-indep" and "d" in hints:
                    kwargs = {"test": "t2-indep", "mode": "a-priori",
                              "tails": str(hints.get("tails", 2)),
                              "d": str(hints["d"]),
                              "alpha": str(hints.get("alpha", 0.05)),
                              "power": str(hints.get("power", 0.8)),
                              "ratio": str(hints.get("ratio", 1))}
                    tool_input = kwargs
                    tool_output = json.loads(power_analysis(**kwargs))
                else:
                    # Family understood but not implemented this sprint
                    # (t-paired/anova-oneway/chi2-contingency/multireg-r2):
                    # call the tool anyway to log the real, honest error.
                    kwargs = {"test": family, "mode": "a-priori"}
                    tool_input = kwargs
                    tool_output = json.loads(power_analysis(**kwargs))

        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "question": q,
            "jev_label": family,
            "jev_confidence": confidence,
            "clarification_needed": clarification_needed,
            "tool_input": tool_input,
            "tool_output": tool_output,
            "tokens_in": 0,
            "tokens_out": 0,
        }
        log_f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    log_f.close()

    print(f"Jev doğruluk (10 soru): {correct}/10")
    if calibrated_total:
        print(f"Güven>={CONFIDENCE_THRESHOLD} dediği {calibrated_total} sorudan "
              f"{calibrated_correct} doğru (kalibre doğruluk %{100*calibrated_correct/calibrated_total:.0f})")
    print(f"Log: {LOG_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    run()
