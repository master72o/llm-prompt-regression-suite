"""
Tests for Evaluator module in LLM Prompt Regression Suite.
"""

from prompt_regression.schema import TestCase
from prompt_regression.evaluator import PromptEvaluator


def test_evaluate_output_passed():
    tc = TestCase(
        test_id="t1",
        name="Valid JSON",
        prompt_input={},
        expected_pattern="\"status\":\\s*\"ok\"",
        ground_truth="{\"status\": \"ok\"}",
        forbidden_terms=["fail"],
        require_valid_json=True,
        max_latency_ms=1000.0,
    )
    res = PromptEvaluator.evaluate_output(tc, "v1", "{\"status\": \"ok\"}", 350.0)
    assert res.passed is True
    assert res.json_valid is True
    assert res.regex_matched is True
    assert len(res.forbidden_words_found) == 0


def test_evaluate_output_forbidden_word():
    tc = TestCase(
        test_id="t2",
        name="Forbidden term check",
        prompt_input={},
        forbidden_terms=["bypass"],
    )
    res = PromptEvaluator.evaluate_output(tc, "v1", "How to bypass security", 200.0)
    assert res.passed is False
    assert "bypass" in res.forbidden_words_found
