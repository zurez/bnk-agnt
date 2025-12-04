"""
Development evaluation script for agent benchmarking.

Usage:
    python evaluations/scripts/run_development_eval.py
    python evaluations/scripts/run_development_eval.py --compare-models
"""

import asyncio
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from deepeval.dataset import EvaluationDataset
from deepeval import evaluate
from deepeval.test_case import LLMTestCase

from evaluations.datasets.banking_scenarios import ALL_SINGLE_TURN_GOLDENS
from evaluations.metrics.agent_metrics import get_all_agent_metrics
from evaluations.config import eval_config

from bankbot.graph import graph
from langchain_core.messages import HumanMessage


# Mock frontend actions for evaluation
MOCK_FRONTEND_ACTIONS = [
    {"name": "showBalance", "description": "Display balance"},
    {"name": "showBeneficiaries", "description": "Display beneficiaries"},
    {"name": "showSpending", "description": "Display spending"},
    {"name": "showTransactions", "description": "Display transactions"},
    {"name": "showTransferForm", "description": "Display transfer form"},
    {"name": "showPendingTransfers", "description": "Display pending transfers"},
    {"name": "showAddBeneficiaryForm", "description": "Display add beneficiary form"},
]


def get_results_path(model_name: str, suffix: str = "") -> Path:
    """Get the path for results file."""
    results_dir = Path(eval_config.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    filename = f"eval_{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{suffix}"
    return results_dir / f"{filename}.json"


def save_partial_results(test_cases: list, model_name: str, error: str = None):
    """Save partial results in case of error."""
    results_file = get_results_path(model_name, "_partial")
    
    results_data = {
        "timestamp": datetime.now().isoformat(),
        "model": model_name,
        "status": "partial",
        "error": error,
        "num_test_cases": len(test_cases),
        "test_cases": [
            {
                "input": tc.input,
                "actual_output": tc.actual_output,
                "expected_output": tc.expected_output,
            }
            for tc in test_cases
        ],
    }
    
    with open(results_file, 'w') as f:
        json.dump(results_data, f, indent=2)
    
    print(f"\n💾 Partial results saved to: {results_file}")


async def run_agent(input_text: str, model_name: str = None) -> str:
    """Run the banking agent and return output."""
    model = model_name or eval_config.evaluation_model
    
    state = {
        "messages": [HumanMessage(content=input_text)],
        "user_id": eval_config.test_user_id,
        "model_name": model,
        "openai_api_key": eval_config.openai_api_key,
        "copilotkit": {"actions": MOCK_FRONTEND_ACTIONS},
    }
    
    config = {
        "configurable": {"thread_id": f"eval_{datetime.now().timestamp()}"},
        "recursion_limit": 50
    }
    
    result = await graph.ainvoke(state, config)
    last_message = result["messages"][-1]
    
    return last_message.content if hasattr(last_message, 'content') else str(last_message)


async def run_evaluation(model_name: str = None):
    """Run evaluation with agent metrics."""
    current_model = model_name or eval_config.evaluation_model
    
    print("=" * 80)
    print("Banking Agent - Evaluation")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Model: {current_model}")
    print(f"Test cases: {len(ALL_SINGLE_TURN_GOLDENS)}")
    
    dataset = EvaluationDataset(goldens=ALL_SINGLE_TURN_GOLDENS)
    metrics = get_all_agent_metrics()
    print(f"\n📏 Using {len(metrics)} metrics")
    
    print(f"\n🤖 Running agent...")
    
    test_cases = []
    
    try:
        for i, golden in enumerate(dataset.goldens):
            print(f"  [{i+1}/{len(dataset.goldens)}] {golden.input[:50]}...")
            
            try:
                actual_output = await run_agent(golden.input, model_name=current_model)
            except Exception as e:
                print(f"    ⚠️ Agent error: {e}")
                actual_output = f"[ERROR: {str(e)}]"
            
            test_case = LLMTestCase(
                input=golden.input,
                actual_output=actual_output,
                expected_output=golden.expected_output,
                context=golden.context,
            )
            test_cases.append(test_case)
        
        print(f"\n✅ Generated {len(test_cases)} test cases")
        print(f"\n📊 Evaluating...")
        
        results = evaluate(test_cases=test_cases, metrics=metrics)
        
        save_results(results, test_cases, current_model)
        
        print(f"\n✅ Evaluation complete for {current_model}!")
        return results
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️ Interrupted! Saving {len(test_cases)} completed test cases...")
        save_partial_results(test_cases, current_model, "User interrupted")
        raise
        
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        print(f"Saving {len(test_cases)} completed test cases...")
        save_partial_results(test_cases, current_model, str(e))
        raise


def save_results(results, test_cases, model_name):
    """Save evaluation results."""
    results_file = get_results_path(model_name)
    
    results_data = {
        "timestamp": datetime.now().isoformat(),
        "model": model_name,
        "status": "complete",
        "num_test_cases": len(test_cases),
        "results": str(results),
    }
    
    with open(results_file, 'w') as f:
        json.dump(results_data, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")


def main():
    parser = argparse.ArgumentParser(description="Run agent evaluation")
    parser.add_argument(
        "--compare-models",
        action="store_true",
        help="Compare all models in config.py"
    )
    
    args = parser.parse_args()
    
    if args.compare_models:
        print(f"🚀 Multi-Model Comparison")
        print(f"Models: {eval_config.agent_models_to_compare}")
        
        for model in eval_config.agent_models_to_compare:
            print(f"\n>>> EVALUATING: {model} <<<")
            try:
                asyncio.run(run_evaluation(model_name=model))
            except Exception as e:
                print(f"❌ Failed for {model}: {e}")
                continue
    else:
        asyncio.run(run_evaluation())


if __name__ == "__main__":
    main()
