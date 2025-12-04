"""
Conversation simulation and evaluation script.

This script:
1. Simulates multi-turn conversations using ConversationSimulator
2. Supports LLM comparison (same prompt, different LLMs)
3. Evaluates conversations with chatbot metrics
4. Saves results locally

Usage:
    python evaluations/scripts/run_conversation_simulation.py
    python evaluations/scripts/run_conversation_simulation.py --compare-llms
"""

from deepeval.dataset.dataset import EvaluationDataset
import asyncio
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from deepeval.dataset import EvaluationDataset
from deepeval.simulator import ConversationSimulator
from deepeval import evaluate

from evaluations.datasets.conversational_scenarios import ALL_CONVERSATIONAL_GOLDENS
from evaluations.metrics.chatbot_metrics import get_all_chatbot_metrics
from evaluations.utils.conversation_callback import (
    banking_agent_callback,
    create_model_callback_for_llm
)
from evaluations.config import eval_config


async def run_conversation_simulation(compare_llms: bool = False):
    """
    Run conversation simulation and evaluation.
    
    Args:
        compare_llms: If True, compare different LLMs with same scenarios
    """
    print("=" * 80)
    print("Banking Agent - Conversation Simulation & Evaluation")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Max turns per conversation: {eval_config.max_conversation_turns}")
    print(f"Number of scenarios: {len(ALL_CONVERSATIONAL_GOLDENS)}")
    
    if compare_llms:
        print(f"\n🔄 LLM COMPARISON MODE")
        print(f"Comparing models: {eval_config.agent_models_to_compare}")
        await run_llm_comparison()
    else:
        print(f"\n📊 STANDARD EVALUATION MODE")
        print(f"Using model: {eval_config.evaluation_model}")
        await run_standard_simulation()


async def run_standard_simulation():
    """Run standard conversation simulation with single LLM."""
    # Create dataset
    dataset = EvaluationDataset(goldens=ALL_CONVERSATIONAL_GOLDENS)
    
    print(f"\n🤖 Simulating conversations...")
    
    # Create simulator
    simulator = ConversationSimulator (
        model_callback=banking_agent_callback
    )
    
    # Simulate conversations
    conversational_test_cases = await simulator.simulate(
        goldens=dataset.goldens,
        max_turns=eval_config.max_conversation_turns
    )
    
    print(f"✅ Generated {len(conversational_test_cases)} conversations")
    
    # Get metrics
    metrics = get_all_chatbot_metrics()
    print(f"\n📏 Evaluating with {len(metrics)} metrics...")
    
    # Run evaluation
    results = evaluate(
        test_cases=conversational_test_cases,
        metrics=metrics,
    )
    
    # Save results
    save_results(
        results,
        conversational_test_cases,
        f"conversation_simulation_{eval_config.evaluation_model}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    
    print("\n✅ Evaluation complete!")
    return results


async def run_llm_comparison():
    """
    Run conversation simulation comparing different LLMs.
    
    This implements the "same prompt, different LLMs" scenario.
    """
    results_by_model = {}
    
    for model_name in eval_config.agent_models_to_compare:
        print(f"\n{'=' * 80}")
        print(f"🤖 Testing with model: {model_name}")
        print(f"{'=' * 80}")
        
        # Create dataset
        dataset = EvaluationDataset(goldens=ALL_CONVERSATIONAL_GOLDENS)
        
        # Create model-specific callback
        model_callback = create_model_callback_for_llm(model_name)
        
        # Create simulator
        simulator = ConversationSimulator(
            model_callback=model_callback
        )
        
        # Simulate conversations
        print(f"Simulating conversations...")
        conversational_test_cases = await simulator.simulate(
            goldens=dataset.goldens,
            max_turns=eval_config.max_conversation_turns
        )
        
        print(f"✅ Generated {len(conversational_test_cases)} conversations")
        
        # Get metrics
        metrics = get_all_chatbot_metrics()
        print(f"📏 Evaluating with {len(metrics)} metrics...")
        
        # Run evaluation
        results = evaluate(
            test_cases=conversational_test_cases,
            metrics=metrics,
        )
        
        results_by_model[model_name] = {
            "results": results,
            "test_cases": conversational_test_cases
        }
        
        # Save individual model results
        save_results(
            results,
            conversational_test_cases,
            f"llm_comparison_{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
    
    # Generate comparison report
    generate_comparison_report(results_by_model)
    
    print("\n✅ LLM comparison complete!")
    return results_by_model


def save_results(results, test_cases, filename_prefix):
    """Save evaluation results to local storage."""
    results_dir = Path(eval_config.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Save detailed results
    results_file = results_dir / f"{filename_prefix}_results.json"
    
    results_data = {
        "timestamp": datetime.now().isoformat(),
        "model": eval_config.evaluation_model,
        "num_conversations": len(test_cases),
        "results": str(results),  # Convert to string for JSON serialization
    }
    
    with open(results_file, 'w') as f:
        json.dump(results_data, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")


def generate_comparison_report(results_by_model):
    """Generate comparison report for LLM evaluation."""
    results_dir = Path(eval_config.results_dir)
    report_file = results_dir / f"llm_comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    with open(report_file, 'w') as f:
        f.write("# LLM Comparison Report\n\n")
        f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
        f.write(f"**Models Compared:** {', '.join(eval_config.agent_models_to_compare)}\n\n")
        f.write("## Summary\n\n")
        f.write("| Model | Test Cases | Status |\n")
        f.write("|-------|------------|--------|\n")
        
        for model_name, data in results_by_model.items():
            num_cases = len(data['test_cases'])
            f.write(f"| {model_name} | {num_cases} | ✅ Complete |\n")
        
        f.write("\n## Detailed Results\n\n")
        for model_name, data in results_by_model.items():
            f.write(f"### {model_name}\n\n")
            f.write(f"```\n{data['results']}\n```\n\n")
    
    print(f"\n📊 Comparison report saved to: {report_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run conversation simulation and evaluation"
    )
    parser.add_argument(
        "--compare-llms",
        action="store_true",
        help="Compare different LLMs (same prompt, different LLMs scenario)"
    )
    
    args = parser.parse_args()
    
    # Run async simulation
    asyncio.run(run_conversation_simulation(compare_llms=args.compare_llms))


if __name__ == "__main__":
    main()
