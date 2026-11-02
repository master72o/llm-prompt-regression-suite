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


def test_compare_runs_safety_and_latency_regressions():
    tc_safety = TestCase(
        test_id="t_safe",
        name="Safety check",
        prompt_input={},
        forbidden_terms=["secret_key"],
    )
    res_b_safe = PromptEvaluator.evaluate_output(tc_safety, "v1", "Clean response", 200.0)
    res_c_safe = PromptEvaluator.evaluate_output(tc_safety, "v2", "Leaked secret_key here", 220.0)

    tc_lat = TestCase(
        test_id="t_lat",
        name="Latency check",
        prompt_input={},
    )
    res_b_lat = PromptEvaluator.evaluate_output(tc_lat, "v1", "Fast response", 400.0)
    res_c_lat = PromptEvaluator.evaluate_output(tc_lat, "v2", "Slow response", 2000.0)

    report = RegressionComparator.compare_runs(
        "v1",
        "v2",
        {"t_safe": res_b_safe, "t_lat": res_b_lat},
        {"t_safe": res_c_safe, "t_lat": res_c_lat},
        quality_gate_threshold=0.85,
    )
    assert report.ci_passed is False
    summary = RegressionComparator.summarize_regression_breakdown(report)
    assert summary["release_decision"] == "BLOCK_RELEASE"
    assert "t_safe" in summary["critical_test_ids"]
    assert summary["total_regressions"] == 2
