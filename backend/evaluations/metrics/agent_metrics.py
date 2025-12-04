"""
Agent evaluation metrics.

Uses GEval for custom criteria evaluation - more reliable than 
agent-specific metrics which require complex tracing data.
"""

from deepeval.metrics import GEval, AnswerRelevancyMetric
from deepeval.test_case import LLMTestCaseParams
from evaluations.config import eval_config


def get_all_agent_metrics():
    """Get evaluation metrics for agent testing."""
    return [
        # Task Completion - Did the agent fulfill the request?
        GEval(
            name="Task Completion",
            criteria="Evaluate if the agent successfully completed the user's banking request",
            evaluation_params=[
                LLMTestCaseParams.INPUT,
                LLMTestCaseParams.ACTUAL_OUTPUT,
                LLMTestCaseParams.EXPECTED_OUTPUT,
            ],
            threshold=eval_config.task_completion_threshold,
        ),
        
        # Tool Usage - Did the agent use appropriate tools?
        GEval(
            name="Tool Usage",
            criteria="Evaluate if the agent called the correct backend and frontend tools for the request. Check if required tools like get_balance, showBalance, get_transactions, showTransactions were used appropriately.",
            evaluation_params=[
                LLMTestCaseParams.INPUT,
                LLMTestCaseParams.ACTUAL_OUTPUT,
            ],
            threshold=eval_config.tool_correctness_threshold,
        ),
        
        # Response Quality - Is the response helpful?
        AnswerRelevancyMetric(
            threshold=0.7,
            include_reason=True,
        ),
    ]
