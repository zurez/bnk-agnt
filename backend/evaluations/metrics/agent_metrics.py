"""
Agent evaluation metrics.

Uses GEval for custom criteria evaluation and custom ToolFlowMetric
for validating tool call sequences.
"""

from deepeval.metrics import GEval, AnswerRelevancyMetric
from deepeval.test_case import LLMTestCaseParams
from evaluations.config import eval_config
from evaluations.metrics.tool_flow_metric import ToolFlowMetric


def get_all_agent_metrics():
    """Get evaluation metrics for agent testing."""
    return [
        # Tool Flow - Primary metric for tool-based agent
        # Validates that the agent called the expected sequence of tools
        ToolFlowMetric(
            threshold=0.8,
            strict_order=False  # Just check all required tools are called
        ),
        
        # Task Completion - Did the agent fulfill the request?
        # Updated to account for tool-based responses
        GEval(
            name="Task Completion",
            criteria="Evaluate if the agent successfully completed the user's banking request by calling the appropriate tools and/or providing a helpful response. Tool calls in the format [Tool Flow: ...] indicate successful actions.",
            evaluation_params=[
                LLMTestCaseParams.INPUT,
                LLMTestCaseParams.ACTUAL_OUTPUT,
                LLMTestCaseParams.EXPECTED_OUTPUT,
            ],
            threshold=eval_config.task_completion_threshold,
        ),
        
        # Response Quality - Is the response helpful?
        AnswerRelevancyMetric(
            threshold=0.7,
            include_reason=True,
        ),
    ]

