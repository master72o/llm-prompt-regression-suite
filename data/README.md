# Prompt Regression Test Suite Datasets

This directory contains test case definitions, baseline outputs ($V_1$), and candidate outputs ($V_2$) used to test for prompt regressions in CI/CD.

- `test_cases.json`: Test suite assertions including expected regex patterns, ground truth answers, forbidden terms, JSON formatting requirements, and latency thresholds.
- `baseline_outputs.json`: Execution outputs for Prompt Version 1 (Baseline).
- `candidate_outputs.json`: Execution outputs for Prompt Version 2 (Candidate).
