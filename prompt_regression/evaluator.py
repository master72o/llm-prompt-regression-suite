"""
Prompt Evaluator for executing test assertions on model outputs.
"""

import re
import json
from typing import Dict, Any, List
from prompt_regression.schema import TestCase, PromptVersion, EvaluationResult


class PromptEvaluator:
    """Evaluates prompt output against test case criteria and assertions."""

    @staticmethod
    def evaluate_output(
        test_case: TestCase,
        version_id: str,
        output: str,
        latency_ms: float
    ) -> EvaluationResult:
        # 1. JSON Validity Check
        json_valid = True
        if test_case.require_valid_json:
            try:
                json.loads(output.strip())
                json_valid = True
            except Exception:
                json_valid = False

        # 2. Regex Match
        regex_matched = True
        if test_case.expected_pattern:
            try:
                regex_matched = bool(re.search(test_case.expected_pattern, output, re.IGNORECASE | re.DOTALL))
            except Exception:
                regex_matched = False

        # 3. Forbidden Words Check
        forbidden_found = []
        output_lower = output.lower()
        for word in test_case.forbidden_terms:
            if word.lower() in output_lower:
                forbidden_found.append(word)

        # 4. Semantic Similarity against Ground Truth
        if test_case.ground_truth:
            words_out = set(re.findall(r"\w+", output_lower))
            words_gt = set(re.findall(r"\w+", test_case.ground_truth.lower()))
            if not words_gt:
                semantic_similarity = 1.0
            else:
                intersection = words_out.intersection(words_gt)
                semantic_similarity = len(intersection) / max(len(words_gt), 1)
                semantic_similarity = min(1.0, semantic_similarity)
        else:
            semantic_similarity = 1.0

        # 5. Latency Score
        latency_ok = latency_ms <= test_case.max_latency_ms

        # Composite Scoring
        score_components = []
        weights = []

        if test_case.require_valid_json:
            score_components.append(1.0 if json_valid else 0.0)
            weights.append(0.3)

        if test_case.expected_pattern:
            score_components.append(1.0 if regex_matched else 0.0)
            weights.append(0.3)

        score_components.append(0.0 if forbidden_found else 1.0)
        weights.append(0.2)

        score_components.append(semantic_similarity)
        weights.append(0.2)

        total_weight = sum(weights)
        overall_score = sum(s * w for s, w in zip(score_components, weights)) / total_weight if total_weight > 0 else 0.0

        # Pass / Fail criteria
        reasons = []
        if test_case.require_valid_json and not json_valid:
            reasons.append("Failed JSON validation")
        if test_case.expected_pattern and not regex_matched:
            reasons.append("Regex pattern match failed")
        if forbidden_found:
            reasons.append(f"Forbidden terms detected: {forbidden_found}")
        if not latency_ok:
            reasons.append(f"Latency exceeded threshold ({latency_ms:.0f}ms > {test_case.max_latency_ms:.0f}ms)")

        passed = (len(reasons) == 0) and (overall_score >= 0.70)
        pass_reason = "Passed all assertions" if passed else "; ".join(reasons)

        return EvaluationResult(
            test_id=test_case.test_id,
            version_id=version_id,
            output=output,
            passed=passed,
            pass_reason=pass_reason,
            json_valid=json_valid,
            regex_matched=regex_matched,
            forbidden_words_found=forbidden_found,
            semantic_similarity=round(semantic_similarity, 4),
            latency_ms=latency_ms,
            overall_score=round(overall_score, 4),
        )
