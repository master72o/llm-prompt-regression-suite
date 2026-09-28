"""
Tests for Comparator module in LLM Prompt Regression Suite.
"""

from prompt_regression.schema import TestCase, EvaluationResult
from prompt_regression.evaluator import PromptEvaluator
from prompt_regression.comparator import RegressionComparator


def test_compare_runs_no_regression():
    tc = TestCase(
        test_id="t1",
        name="T1",
        prompt_input={},
        require_valid_json=True,
    )
    res_b = PromptEvaluator.evaluate_output(tc, "v1", "{\"a\": 1}", 300.0)
    res_c = PromptEvaluator.evaluate_output(tc, "v2", "{\"a\": 1}", 310.0)

    report = RegressionComparator.compare_runs(
        "v1", "v2", {"t1": res_b}, {"t1": res_c}, quality_gate_threshold=0.85
    )
    assert report.ci_passed is True
    assert report.candidate_pass_rate == 1.0


def test_compare_runs_format_breakage_regression():
    tc = TestCase(
        test_id="t1",
        name="T1",
        prompt_input={},
        require_valid_json=True,
    )
    res_b = PromptEvaluator.evaluate_output(tc, "v1", "{\"a\": 1}", 300.0)
    res_c = PromptEvaluator.evaluate_output(tc, "v2", "invalid json", 310.0)

    report = RegressionComparator.compare_runs(
        "v1", "v2", {"t1": res_b}, {"t1": res_c}, quality_gate_threshold=0.85
    )
    assert report.ci_passed is False
    assert len(report.regressions) == 1
    assert report.regressions[0].is_critical is True
