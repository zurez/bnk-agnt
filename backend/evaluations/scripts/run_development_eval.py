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


async def run_agent(input_text: str, model_name: str = None) -> tuple[str, dict]:
    """Run the banking agent and return output + detailed metrics."""
    import time
    start_time = time.time()
    
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
    
    # Extract detailed tool call information
    tool_call_details = []
    tool_calls = []
    
    for msg in result["messages"]:
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            for tc in msg.tool_calls:
                tool_name = tc.get('name') if isinstance(tc, dict) else tc['name']
                tool_args = tc.get('args', {}) if isinstance(tc, dict) else getattr(tc, 'args', {})
                
                if tool_name not in tool_calls:
                    tool_calls.append(tool_name)
                
                tool_call_details.append({
                    "name": tool_name,
                    "args": tool_args,
                    "args_count": len(tool_args) if isinstance(tool_args, dict) else 0
                })
    
    last_message = result["messages"][-1]
    content = last_message.content if hasattr(last_message, 'content') else ""
    
    # Extract token usage if available
    token_usage = {}
    if hasattr(last_message, 'response_metadata'):
        usage = last_message.response_metadata.get('token_usage', {})
        token_usage = {
            "input_tokens": usage.get('prompt_tokens', 0),
            "output_tokens": usage.get('completion_tokens', 0),
            "total_tokens": usage.get('total_tokens', 0)
        }
    
    # Format output to show tool calls
    if tool_calls:
        tools_str = " → ".join(tool_calls)
        if content:
            output = f"{content}\n[Tool Flow: {tools_str}]"
        else:
            output = f"[Tool Flow: {tools_str}]"
    else:
        output = content or "(no response)"
    
    # Calculate execution time
    execution_time = time.time() - start_time
    
    # Compile detailed metrics
    metrics = {
        "tool_calls": tool_calls,
        "tool_call_details": tool_call_details,
        "tool_call_count": len(tool_call_details),
        "token_usage": token_usage,
        "execution_time": execution_time,
        "model": model
    }
    
    return output, metrics



async def run_evaluation(model_name: str = None):
    """Run evaluation with agent metrics using parallel execution."""
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
    
    print(f"\n🤖 Running agent in parallel...")
    
    test_cases = []
    all_metrics_data = []
    
    try:
        # Run all test cases in parallel for speed
        tasks = [
            run_agent(golden.input, model_name=current_model)
            for golden in dataset.goldens
        ]
        
        print(f"  ⚡ Executing {len(tasks)} tests concurrently...")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, (golden, result) in enumerate(zip(dataset.goldens, results)):
            if isinstance(result, Exception):
                print(f"  [{i+1}/{len(dataset.goldens)}] ⚠️ Error: {str(result)[:50]}...")
                actual_output = f"[ERROR: {str(result)}]"
                metrics_data = {
                    "tool_calls": [],
                    "tool_call_details": [],
                    "tool_call_count": 0,
                    "token_usage": {},
                    "execution_time": 0,
                    "model": current_model
                }
            else:
                actual_output, metrics_data = result
                print(f"  [{i+1}/{len(dataset.goldens)}] ✓ {golden.input[:50]}... ({metrics_data['execution_time']:.2f}s)")
            
            # Store metrics for later aggregation
            all_metrics_data.append(metrics_data)
            
            # Merge metadata - add actual tool calls and metrics to golden's metadata
            metadata = golden.additional_metadata.copy() if golden.additional_metadata else {}
            metadata["actual_tool_calls"] = metrics_data["tool_calls"]
            metadata["tool_call_details"] = metrics_data["tool_call_details"]
            metadata["token_usage"] = metrics_data["token_usage"]
            metadata["execution_time"] = metrics_data["execution_time"]
            
            test_case = LLMTestCase(
                input=golden.input,
                actual_output=actual_output,
                expected_output=golden.expected_output,
                context=golden.context,
                additional_metadata=metadata,
            )
            test_cases.append(test_case)
        
        print(f"\n✅ Generated {len(test_cases)} test cases")
        print(f"\n📊 Evaluating...")
        
        results = evaluate(test_cases=test_cases, metrics=metrics)
        
        save_results(results, test_cases, current_model, all_metrics_data)
        
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



def calculate_cost(token_usage: dict, model: str) -> float:
    """Calculate cost based on token usage and model pricing."""
    pricing = {
        "gpt-4o": {"input": 0.0025 / 1000, "output": 0.01 / 1000},
        "gpt-4o-mini": {"input": 0.00015 / 1000, "output": 0.0006 / 1000},
        "gpt-4-turbo": {"input": 0.01 / 1000, "output": 0.03 / 1000},
    }
    
    model_pricing = pricing.get(model, pricing["gpt-4o"])
    input_cost = token_usage.get("input_tokens", 0) * model_pricing["input"]
    output_cost = token_usage.get("output_tokens", 0) * model_pricing["output"]
    
    return input_cost + output_cost


def save_results(results, test_cases, model_name, all_metrics_data=None):
    """Save evaluation results with detailed metrics and test cases."""
    results_file = get_results_path(model_name)
    
    # Aggregate metrics
    aggregated_metrics = {
        "total_tool_calls": 0,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "total_tokens": 0,
        "total_cost": 0.0,
        "avg_execution_time": 0.0,
        "tool_usage_breakdown": {}
    }
    
    if all_metrics_data:
        for metrics in all_metrics_data:
            # Tool calls
            aggregated_metrics["total_tool_calls"] += metrics.get("tool_call_count", 0)
            
            # Token usage
            token_usage = metrics.get("token_usage", {})
            aggregated_metrics["total_input_tokens"] += token_usage.get("input_tokens", 0)
            aggregated_metrics["total_output_tokens"] += token_usage.get("output_tokens", 0)
            aggregated_metrics["total_tokens"] += token_usage.get("total_tokens", 0)
            
            # Cost
            aggregated_metrics["total_cost"] += calculate_cost(token_usage, model_name)
            
            # Execution time
            aggregated_metrics["avg_execution_time"] += metrics.get("execution_time", 0)
            
            # Tool breakdown
            for tool_detail in metrics.get("tool_call_details", []):
                tool_name = tool_detail["name"]
                if tool_name not in aggregated_metrics["tool_usage_breakdown"]:
                    aggregated_metrics["tool_usage_breakdown"][tool_name] = {
                        "count": 0,
                        "total_args": 0
                    }
                aggregated_metrics["tool_usage_breakdown"][tool_name]["count"] += 1
                aggregated_metrics["tool_usage_breakdown"][tool_name]["total_args"] += tool_detail.get("args_count", 0)
        
        # Calculate averages
        num_tests = len(all_metrics_data)
        if num_tests > 0:
            aggregated_metrics["avg_execution_time"] /= num_tests
            aggregated_metrics["avg_tool_calls_per_test"] = aggregated_metrics["total_tool_calls"] / num_tests
    
    # Extract detailed test case information
    test_case_details = []
    for i, test_case in enumerate(test_cases):
        metrics_data = all_metrics_data[i] if all_metrics_data and i < len(all_metrics_data) else {}
        
        # Extract metric results from the test case
        metric_results = []
        if hasattr(results, 'test_results') and i < len(results.test_results):
            test_result = results.test_results[i]
            if hasattr(test_result, 'metrics_data'):
                for metric_data in test_result.metrics_data:
                    metric_results.append({
                        "name": metric_data.name,
                        "score": metric_data.score,
                        "threshold": metric_data.threshold,
                        "success": metric_data.success,
                        "reason": metric_data.reason if hasattr(metric_data, 'reason') else ""
                    })
        
        test_case_details.append({
            "input": test_case.input,
            "actual_output": test_case.actual_output,
            "expected_output": test_case.expected_output,
            "context": test_case.context if test_case.context else [],
            "tool_calls": metrics_data.get("tool_calls", []),
            "execution_time": metrics_data.get("execution_time", 0),
            "metrics": metric_results
        })
    
    results_data = {
        "timestamp": datetime.now().isoformat(),
        "model": model_name,
        "status": "complete",
        "num_test_cases": len(test_cases),
        "results": str(results),
        "aggregated_metrics": aggregated_metrics,
        "test_cases": test_case_details
    }
    
    with open(results_file, 'w') as f:
        json.dump(results_data, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    # Print summary
    if all_metrics_data:
        print(f"\n📊 Metrics Summary:")
        print(f"  Total Tool Calls: {aggregated_metrics['total_tool_calls']}")
        print(f"  Total Tokens: {aggregated_metrics['total_tokens']:,} (Input: {aggregated_metrics['total_input_tokens']:,}, Output: {aggregated_metrics['total_output_tokens']:,})")
        print(f"  Total Cost: ${aggregated_metrics['total_cost']:.4f}")
        print(f"  Avg Execution Time: {aggregated_metrics['avg_execution_time']:.2f}s")



def main():
    parser = argparse.ArgumentParser(description="Run agent evaluation")
    parser.add_argument(
        "--compare-models",
        action="store_true",
        help="Compare all models in config.py"
    )
    parser.add_argument(
        "--model",
        type=str,
        help="Specific model to evaluate"
    )
    
    args = parser.parse_args()
    
    # Suppress RuntimeError warnings during cleanup
    import warnings
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    
    try:
        if args.compare_models:
            print(f"🚀 Multi-Model Comparison")
            print(f"Models: {eval_config.agent_models_to_compare}")
            
            for model in eval_config.agent_models_to_compare:
                print(f"\n>>> EVALUATING: {model} <<<")
                try:
                    asyncio.run(run_evaluation(model_name=model))
                except KeyboardInterrupt:
                    print(f"\n⚠️  Interrupted during {model} evaluation")
                    raise
                except Exception as e:
                    print(f"❌ Failed for {model}: {e}")
                    continue
        elif args.model:
            asyncio.run(run_evaluation(model_name=args.model))
        else:
            asyncio.run(run_evaluation())
    except KeyboardInterrupt:
        print("\n\n⚠️  Evaluation interrupted by user")
        sys.exit(1)
    except RuntimeError as e:
        # Suppress event loop cleanup errors
        if "Event loop is closed" not in str(e):
            raise


if __name__ == "__main__":
    main()
