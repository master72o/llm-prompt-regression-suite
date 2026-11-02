"""
Regression Comparator for identifying performance drop-offs between prompt versions.
"""

from typing import List, Dict, Any, Tuple
from prompt_regression.schema import (
    EvaluationResult,
    RegressionItem,
    RegressionType,
    RegressionSuiteReport,
)


class RegressionComparator:
    """Compares baseline vs candidate evaluation runs to classify regressions."""

    @staticmethod
    def compare_runs(
        baseline_version: str,
        candidate_version: str,
        baseline_results: Dict[str, EvaluationResult],
        candidate_results: Dict[str, EvaluationResult],
        quality_gate_threshold: float = 0.85
    ) -> RegressionSuiteReport:
        regressions = []
        total_tests = len(baseline_results)

        baseline_passed_count = sum(1 for r in baseline_results.values() if r.passed)
        candidate_passed_count = sum(1 for r in candidate_results.values() if r.passed)

        baseline_scores = [r.overall_score for r in baseline_results.values()]
        candidate_scores = [r.overall_score for r in candidate_results.values()]

        baseline_pass_rate = baseline_passed_count / max(total_tests, 1)
        candidate_pass_rate = candidate_passed_count / max(total_tests, 1)

        baseline_mean = sum(baseline_scores) / max(total_tests, 1)
        candidate_mean = sum(candidate_scores) / max(total_tests, 1)

        critical_regressions_count = 0

        for test_id, base_res in baseline_results.items():
            cand_res = candidate_results.get(test_id)
            if not cand_res:
                continue

            delta = cand_res.overall_score - base_res.overall_score
            reg_type = RegressionType.NONE
            is_critical = False

            # Check 1: Format breakage
            if base_res.json_valid and not cand_res.json_valid:
                reg_type = RegressionType.FORMAT_BREAKAGE
                is_critical = True

            # Check 2: Safety breach
            elif not base_res.forbidden_words_found and cand_res.forbidden_words_found:
                reg_type = RegressionType.SAFETY_BREACH
                is_critical = True

            # Check 3: Semantic quality drop
            elif base_res.semantic_similarity - cand_res.semantic_similarity > 0.15:
                reg_type = RegressionType.SEMANTIC_QUALITY_DROP

            # Check 4: Latency degradation
            elif cand_res.latency_ms > base_res.latency_ms * 1.5 and cand_res.latency_ms > 1500:
                reg_type = RegressionType.LATENCY_DEGRADATION

            # Check 5: General accuracy drop
            elif delta < -0.10:
                reg_type = RegressionType.ACCURACY_REGRESSION

            if base_res.passed and not cand_res.passed:
                is_critical = True

            if reg_type != RegressionType.NONE or is_critical:
                regressions.append(
                    RegressionItem(
                        test_id=test_id,
                        baseline_result=base_res,
                        candidate_result=cand_res,
                        regression_type=reg_type,
                        score_delta=round(delta, 4),
                        is_critical=is_critical,
                    )
                )

            if is_critical:
                critical_regressions_count += 1

        # CI Gate Check
        ci_passed = (
            candidate_pass_rate >= quality_gate_threshold
            and critical_regressions_count == 0
            and (candidate_mean - baseline_mean) >= -0.05
        )

        return RegressionSuiteReport(
            baseline_version=baseline_version,
            candidate_version=candidate_version,
            total_tests=total_tests,
            baseline_pass_rate=round(baseline_pass_rate, 4),
            candidate_pass_rate=round(candidate_pass_rate, 4),
            baseline_mean_score=round(baseline_mean, 4),
            candidate_mean_score=round(candidate_mean, 4),
            regressions=regressions,
            ci_passed=ci_passed,
            quality_gate_threshold=quality_gate_threshold,
        )

    @staticmethod
    def summarize_regression_breakdown(report: RegressionSuiteReport) -> Dict[str, Any]:
        """
        Aggregates regression counts by RegressionType, identifies the most degraded test cases,
        and produces an executive release recommendation.
        """
        counts_by_type: Dict[str, int] = {}
        critical_ids: List[str] = []

        for reg in report.regressions:
            rtype = reg.regression_type.value if hasattr(reg.regression_type, "value") else str(reg.regression_type)
            counts_by_type[rtype] = counts_by_type.get(rtype, 0) + 1
            if reg.is_critical:
                critical_ids.append(reg.test_id)

        sorted_by_delta = sorted(report.regressions, key=lambda r: r.score_delta)
        worst_test_ids = [r.test_id for r in sorted_by_delta[:3]]
        mean_score_delta = round(report.candidate_mean_score - report.baseline_mean_score, 4)

        if report.ci_passed and not report.regressions:
            decision = "APPROVE_RELEASE"
        elif report.ci_passed:
            decision = "APPROVE_WITH_WARNINGS"
        else:
            decision = "BLOCK_RELEASE"

        return {
            "baseline_version": report.baseline_version,
            "candidate_version": report.candidate_version,
            "total_regressions": len(report.regressions),
            "critical_regression_count": len(critical_ids),
            "critical_test_ids": critical_ids,
            "counts_by_type": counts_by_type,
            "worst_degraded_test_ids": worst_test_ids,
            "mean_score_delta": mean_score_delta,
            "release_decision": decision,
        }
