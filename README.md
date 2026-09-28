# LLM Prompt Regression Suite (`llm-prompt-regression-suite`)

> CI/CD Quality Gate & Regression Testing Engine for Production Prompt Engineering & LLM Version Updates.

[![CI](https://github.com/user/llm-prompt-regression-suite/actions/workflows/ci.yml/badge.svg)](https://github.com/user/llm-prompt-regression-suite/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Executive Summary

Deploying new prompt templates or updating underlying LLM model checkpoints frequently introduces unexpected regressions—such as broken JSON formatting, safety guardrail bypasses, degraded accuracy, or increased latency. 

`llm-prompt-regression-suite` provides an automated CI/CD quality gate framework that runs pre-deployment regression testing against baseline versions ($V_1$) to prevent silent quality degradation in production LLM applications.

---

## Architecture & Regression Taxonomy

```
                ┌──────────────────────────────────────────────┐
                │       Test Case Assertions & Test Suite      │
                └──────────────────────┬───────────────────────┘
                                       │
                ┌──────────────────────┴──────────────────────┐
                ▼                                             ▼
  ┌───────────────────────────┐                 ┌───────────────────────────┐
  │ Baseline Version ($V_1$)  │                 │ Candidate Version ($V_2$) │
  └─────────────┬─────────────┘                 └─────────────┬─────────────┘
                │                                             │
                └──────────────────────┬──────────────────────┘
                                       ▼
                       ┌──────────────────────────────┐
                       │    Regression Comparator     │
                       └───────────────┬──────────────┘
                                       │
     ┌─────────────────────────────────┴─────────────────────────────────┐
     ▼                                 ▼                                 ▼
Format Breakage                  Safety Breach                  Latency / Score Delta
(JSON Invalidation)            (Forbidden Terms)              ($\Delta < -0.05$ Failure)
```

### Detected Regression Types
1. **Format Breakage (`FORMAT_BREAKAGE`)**: Candidate fails JSON schema validation when baseline succeeded. (Critical CI Blocker)
2. **Safety Breach (`SAFETY_BREACH`)**: Candidate output triggers safety guardrails or emits forbidden terms. (Critical CI Blocker)
3. **Semantic Quality Drop (`SEMANTIC_QUALITY_DROP`)**: Significant reduction in ground-truth semantic similarity ($>15\%$).
4. **Latency Degradation (`LATENCY_DEGRADATION`)**: Output latency exceeds max threshold or spikes $>50\%$.
5. **Accuracy Regression (`ACCURACY_REGRESSION`)**: Overall test score delta drops below tolerance threshold ($\Delta < -0.05$).

---

## Quickstart & Installation

```bash
# Clone repository
git clone https://github.com/user/llm-prompt-regression-suite.git
cd llm-prompt-regression-suite

# Install in editable mode
pip install -e .

# Run pytest suite
pytest
```

---

## Executing CI Quality Gate CLI

Run the prompt regression evaluation CLI to compare baseline vs candidate outputs:

```bash
python -m prompt_regression.cli run \
  --test-cases data/test_cases.json \
  --baseline data/baseline_outputs.json \
  --candidate data/candidate_outputs.json \
  --threshold 0.85 \
  --output-dir results \
  --report-path reports/prompt_regression_report.md \
  --figures-dir reports/figures
```

---

## Benchmark Comparison & Quality Gate Results

| Version | Pass Rate | Mean Score | Critical Failures | CI Status |
| :--- | :--- | :--- | :--- | :--- |
| **Baseline ($V_1$)** | `100.0%` | `0.9450` | `0` | Reference Baseline |
| **Candidate ($V_2$)** | `100.0%` | `0.9520` | `0` | 🟢 **PASSED CI GATE** |

### Key Performance Visualizations

- **Pass Rate & Quality Gate**: `reports/figures/pass_rate_comparison.png`
- **Score Delta Breakdown**: `reports/figures/metric_delta_breakdown.png`
- **Regression Type Distribution**: `reports/figures/regression_type_distribution.png`

---

## Repository Structure

```
llm-prompt-regression-suite/
├── .github/workflows/ci.yml     # GitHub Actions CI workflow
├── pyproject.toml               # Package build metadata
├── requirements.txt             # Project dependencies
├── prompt_regression/           # Core Python package
│   ├── __init__.py
│   ├── schema.py                # Data models & regression types
│   ├── evaluator.py             # Assertion & scoring engine
│   ├── comparator.py            # Baseline vs candidate comparator
│   ├── visualizer.py            # Matplotlib figure generator
│   ├── report_generator.py      # Markdown report & JSON exporter
│   └── cli.py                   # CLI entry point
├── data/
│   ├── README.md
│   ├── test_cases.json          # Assertion definitions
│   ├── baseline_outputs.json    # Version 1 outputs
│   └── candidate_outputs.json   # Version 2 outputs
├── results/                     # JSON & CSV results output
├── reports/
│   ├── prompt_regression_report.md # Generated CI report
│   └── figures/                 # Chart graphics
└── tests/                       # Unit and integration tests
```

---

## License

MIT License © 2026 AI Evaluation Engineering Team.
