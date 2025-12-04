# LLM Evaluation Setup

Uses [DeepEval](https://deepeval.com) to test the banking agent across OpenAI models.

## Quick Start

```bash
# 1. Set your API key
echo "OPENAI_API_KEY=sk-..." > evaluations/.env

# 2. Run evaluation
python evaluations/scripts/run_development_eval.py

# 3. Compare models (gpt-4o vs gpt-4o-mini)
python evaluations/scripts/run_development_eval.py --compare-models

# 4. Generate HTML report
python evaluations/scripts/generate_report.py --latest
```

---

## Structure

```
evaluations/
├── .env                 # API keys
├── config.py            # Model config & thresholds
├── scripts/
│   ├── run_development_eval.py  # Main evaluation script
│   └── generate_report.py       # HTML report generator
├── datasets/
│   └── banking_scenarios.py     # Test cases
├── metrics/
│   └── agent_metrics.py         # Evaluation metrics
└── results/                     # Output JSON & HTML
```

---

## Metrics

| Metric | What it Measures | Threshold |
|--------|------------------|-----------|
| **PlanQuality** | Does the agent form a logical plan? | 0.7 |
| **PlanAdherence** | Does execution follow the plan? | 0.7 |
| **ToolCorrectness** | Are the right tools selected? | 0.8 |
| **ArgumentCorrectness** | Are tool arguments valid? | 0.8 |
| **TaskCompletion** | Is the user's request fulfilled? | 0.8 |
| **StepEfficiency** | Minimal steps to complete? | 0.6 |

---

## Configuration

Edit `config.py`:

```python
# Models to compare
agent_models_to_compare = ["gpt-4o", "gpt-4o-mini"]

# Adjust thresholds
task_completion_threshold = 0.8
```
