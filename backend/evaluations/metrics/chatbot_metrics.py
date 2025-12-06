"""
Chatbot evaluation metrics for multi-turn conversations.

These metrics evaluate:
- Turn-level: Relevancy and knowledge retention
- Conversation-level: Completeness
"""

from deepeval.metrics import (
    TurnRelevancyMetric,
    KnowledgeRetentionMetric,
    ConversationCompletenessMetric,
    AnswerRelevancyMetric,
    HallucinationMetric,
)
from deepeval.test_case import LLMTestCaseParams
from evaluations.config import eval_config


def get_turn_level_metrics():
    """Get metrics for evaluating individual turns in a conversation."""
    return [
        TurnRelevancyMetric(
            threshold=eval_config.turn_relevancy_threshold,
            include_reason=True,
        ),
        KnowledgeRetentionMetric(
            threshold=eval_config.knowledge_retention_threshold,
            include_reason=True,
        ),
    ]


def get_conversation_level_metrics():
    """Get metrics for evaluating entire conversations."""
    return [
        ConversationCompletenessMetric(
            threshold=eval_config.conversation_completeness_threshold,
            include_reason=True,
        ),
    ]


def get_banking_specific_metrics():
    """Get banking-specific metrics using available deepeval metrics."""
    return [
        # Answer relevancy for banking queries
        AnswerRelevancyMetric(
            threshold=0.7,
            include_reason=True,
        ),
        # Hallucination detection for financial accuracy
        HallucinationMetric(
            threshold=0.9,  # High threshold - we want minimal hallucination
            include_reason=True,
        ),
    ]


def get_all_chatbot_metrics():
    """Get all chatbot evaluation metrics."""
    return (
        get_turn_level_metrics() +
        get_conversation_level_metrics() +
        get_banking_specific_metrics()
    )
