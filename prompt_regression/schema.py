"""
Data Schemas for LLM Prompt Regression Suite.
"""

from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List


class RegressionType(str, Enum):
    FORMAT_BREAKAGE = "Format_Breakage"
    SEMANTIC_QUALITY_DROP = "Semantic_Quality_Drop"
    SAFETY_BREACH = "Safety_Breach"
    LATENCY_DEGRADATION = "Latency_Degradation"
    ACCURACY_REGRESSION = "Accuracy_Regression"
    NONE = "None"


@dataclass
class TestCase:
    __test__ = False

    test_id: str
    name: str
    prompt_input: Dict[str, Any]
    expected_pattern: Optional[str] = None
    ground_truth: Optional[str] = None
    forbidden_terms: List[str] = field(default_factory=list)
    require_valid_json: bool = False
    max_latency_ms: float = 2000.0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TestCase":
        return cls(
            test_id=data["test_id"],
            name=data.get("name", data["test_id"]),
            prompt_input=data.get("prompt_input", {}),
            expected_pattern=data.get("expected_pattern"),
            ground_truth=data.get("ground_truth"),
            forbidden_terms=data.get("forbidden_terms", []),
            require_valid_json=data.get("require_valid_json", False),
            max_latency_ms=data.get("max_latency_ms", 2000.0),
        )


@dataclass
class PromptVersion:
    version_id: str
    prompt_template: str
    model_name: str
    temperature: float = 0.0
    max_tokens: int = 512

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PromptVersion":
        return cls(
            version_id=data["version_id"],
            prompt_template=data["prompt_template"],
            model_name=data.get("model_name", "gpt-4-turbo"),
            temperature=data.get("temperature", 0.0),
            max_tokens=data.get("max_tokens", 512),
        )


@dataclass
class EvaluationResult:
    test_id: str
    version_id: str
    output: str
    passed: bool
    pass_reason: str
    json_valid: bool
    regex_matched: bool
    forbidden_words_found: List[str]
    semantic_similarity: float
    latency_ms: float
    overall_score: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_id": self.test_id,
            "version_id": self.version_id,
            "output": self.output,
            "passed": bool(self.passed),
            "pass_reason": self.pass_reason,
            "json_valid": bool(self.json_valid),
            "regex_matched": bool(self.regex_matched),
            "forbidden_words_found": self.forbidden_words_found,
            "semantic_similarity": round(self.semantic_similarity, 4),
            "latency_ms": round(self.latency_ms, 2),
            "overall_score": round(self.overall_score, 4),
        }


@dataclass
class RegressionItem:
    test_id: str
    baseline_result: EvaluationResult
    candidate_result: EvaluationResult
    regression_type: RegressionType
    score_delta: float
    is_critical: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_id": self.test_id,
            "regression_type": self.regression_type.value if isinstance(self.regression_type, RegressionType) else str(self.regression_type),
            "score_delta": round(self.score_delta, 4),
            "is_critical": bool(self.is_critical),
            "baseline": self.baseline_result.to_dict(),
            "candidate": self.candidate_result.to_dict(),
        }


@dataclass
class RegressionSuiteReport:
    baseline_version: str
    candidate_version: str
    total_tests: int
    baseline_pass_rate: float
    candidate_pass_rate: float
    baseline_mean_score: float
    candidate_mean_score: float
    regressions: List[RegressionItem]
    ci_passed: bool
    quality_gate_threshold: float = 0.85
