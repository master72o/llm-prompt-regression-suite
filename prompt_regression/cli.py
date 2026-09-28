"""
CLI Interface for LLM Prompt Regression Suite.
"""

import argparse
import sys
import json
from prompt_regression.schema import TestCase, EvaluationResult
from prompt_regression.evaluator import PromptEvaluator
from prompt_regression.comparator import RegressionComparator
from prompt_regression.visualizer import Visualizer
from prompt_regression.report_generator import ReportGenerator


def main():
    parser = argparse.ArgumentParser(description="LLM Prompt Regression Suite CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    run_parser = subparsers.add_parser("run", help="Run prompt regression evaluation")
    run_parser.add_argument("--test-cases", required=True, help="Path to JSON test cases")
    run_parser.add_argument("--baseline", required=True, help="Path to baseline outputs JSON")
    run_parser.add_argument("--candidate", required=True, help="Path to candidate outputs JSON")
    run_parser.add_argument("--threshold", type=float, default=0.85, help="CI Quality Gate threshold (default: 0.85)")
    run_parser.add_argument("--output-dir", default="results", help="Directory to save JSON/CSV results")
    run_parser.add_argument("--report-path", default="reports/prompt_regression_report.md", help="Path to save Markdown report")
    run_parser.add_argument("--figures-dir", default="reports/figures", help="Directory to save figure plots")

    args = parser.parse_args()

    if args.command == "run":
        print(f"Loading test cases from: {args.test_cases}")
        with open(args.test_cases, "r", encoding="utf-8") as f:
            tc_raw = json.load(f)
        test_cases = [TestCase.from_dict(tc) for tc in tc_raw]

        print(f"Loading baseline outputs from: {args.baseline}")
        with open(args.baseline, "r", encoding="utf-8") as f:
            baseline_raw = json.load(f)

        print(f"Loading candidate outputs from: {args.candidate}")
        with open(args.candidate, "r", encoding="utf-8") as f:
            candidate_raw = json.load(f)

        baseline_results = {}
        for tc in test_cases:
            b_item = baseline_raw.get(tc.test_id, {})
            out = b_item.get("output", "")
            lat = b_item.get("latency_ms", 500.0)
            baseline_results[tc.test_id] = PromptEvaluator.evaluate_output(tc, "v1_baseline", out, lat)

        candidate_results = {}
        for tc in test_cases:
            c_item = candidate_raw.get(tc.test_id, {})
            out = c_item.get("output", "")
            lat = c_item.get("latency_ms", 500.0)
            candidate_results[tc.test_id] = PromptEvaluator.evaluate_output(tc, "v2_candidate", out, lat)

        print("Comparing baseline vs candidate runs...")
        report = RegressionComparator.compare_runs(
            "v1_baseline", "v2_candidate", baseline_results, candidate_results, quality_gate_threshold=args.threshold
        )

        print(f"\nRegression Report Summary:")
        print(f"  Baseline Pass Rate:  {report.baseline_pass_rate*100:.1f}% (Mean Score: {report.baseline_mean_score:.4f})")
        print(f"  Candidate Pass Rate: {report.candidate_pass_rate*100:.1f}% (Mean Score: {report.candidate_mean_score:.4f})")
        print(f"  Detected Regressions: {len(report.regressions)}")
        print(f"  CI Quality Gate:      {'PASSED' if report.ci_passed else 'FAILED'}")

        print(f"\nExporting results to: {args.output_dir}")
        ReportGenerator.export_results(report, args.output_dir)

        print(f"Generating visualizations in: {args.figures_dir}")
        Visualizer.generate_all_figures(report, args.figures_dir)

        print(f"Generating markdown report at: {args.report_path}")
        ReportGenerator.generate_markdown_report(report, args.report_path)

        if not report.ci_passed:
            print("\n❌ CI Quality Gate Failed due to regressions or low pass rate!")
            sys.exit(1)
        else:
            print("\n✅ CI Quality Gate Passed successfully!")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
