"""
Tests for Schema module in LLM Prompt Regression Suite.
"""

from prompt_regression.schema import TestCase, PromptVersion, RegressionType


def test_test_case_parsing():
    data = {
        "test_id": "test_001",
        "name": "Test JSON",
        "prompt_input": {"key": "val"},
        "expected_pattern": "status",
        "ground_truth": "truth",
        "forbidden_terms": ["bad"],
        "require_valid_json": True,
        "max_latency_ms": 1000.0,
    }
    tc = TestCase.from_dict(data)
    assert tc.test_id == "test_001"
    assert tc.require_valid_json is True
    assert tc.max_latency_ms == 1000.0


def test_prompt_version_parsing():
    pv = PromptVersion.from_dict({"version_id": "v1", "prompt_template": "Hello {name}"})
    assert pv.version_id == "v1"
    assert pv.model_name == "gpt-4-turbo"
