"""
Evaluation configuration for DeepEval.

This module configures evaluation settings including:
- OpenAI LLM configuration
- Metric thresholds
- Dataset paths
- Results storage
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load .env from evaluations directory
load_dotenv(Path(__file__).parent / ".env")


class EvaluationConfig(BaseSettings):
    """Configuration for DeepEval evaluations."""
    
    # Disable Confident AI cloud integration
    confident_api_key: Optional[str] = None
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Default evaluation LLM
    evaluation_model: str = "gpt-4o"
    
    # OpenAI models to compare
    agent_models_to_compare: list[str] = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"]
    
    # Metric Thresholds
    plan_quality_threshold: float = 0.7
    plan_adherence_threshold: float = 0.7
    tool_correctness_threshold: float = 0.8
    argument_correctness_threshold: float = 0.8
    task_completion_threshold: float = 0.8
    step_efficiency_threshold: float = 0.6
    turn_relevancy_threshold: float = 0.7
    knowledge_retention_threshold: float = 0.7
    conversation_coherence_threshold: float = 0.7
    conversation_completeness_threshold: float = 0.8
    
    # Dataset Paths
    datasets_dir: str = "evaluations/datasets"
    results_dir: str = "evaluations/results"
    
    # Conversation Simulation
    max_conversation_turns: int = 10
    num_simulations_per_scenario: int = 1
    
    # User ID for testing
    test_user_id: str = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"
    
    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Global config instance
eval_config = EvaluationConfig()

# Ensure API key is set in environment for deepeval
if eval_config.openai_api_key and "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = eval_config.openai_api_key

