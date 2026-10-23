"""AI agent layer tests (CONTRACT.md section 8): classifier accuracy on
the 10 fictional eval scenarios, and that the agent never fabricates a
number for a categorical effect size (CONTRACT.md section 10 warning).
"""
import json

from src.agent.classifier import classify, has_explicit_effect_size
from src.agent.run_eval import QUESTIONS, run as run_eval, LOG_PATH


def test_classifier_matches_expected_family_for_all_ten():
    for item in QUESTIONS:
        family, _confidence = classify(item["question"])
        assert family == item["expected_family"], item["question"]


def test_categorical_effect_size_has_no_explicit_number():
    # Q1, Q6, Q10 deliberately use a category word ("orta", "küçük-orta"),
    # never a bare number -- the agent must not silently assume d=0.5.
    categorical_ids = {1, 6, 10}
    for item in QUESTIONS:
        if item["id"] in categorical_ids:
            assert not has_explicit_effect_size(item["question"])


def test_run_eval_produces_well_formed_log(tmp_path, monkeypatch):
    run_eval()
    assert LOG_PATH.exists()
    with open(LOG_PATH, encoding="utf-8") as f:
        lines = [json.loads(l) for l in f]
    assert len(lines) == 10
    for entry in lines:
        for key in ("ts", "question", "tool_input", "tool_output", "tokens_in", "tokens_out"):
            assert key in entry
        # Every actual tool call is either backed by an explicit number in
        # the question, or surfaces a real (not fabricated) engine error
        # for a family this sprint doesn't implement.
        if entry["tool_input"] is not None:
            explicit = has_explicit_effect_size(entry["question"])
            is_error = isinstance(entry["tool_output"], dict) and "error" in entry["tool_output"]
            assert explicit or is_error
