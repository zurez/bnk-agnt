"""Centralized configuration management using Pydantic Settings."""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "postgresql://localhost@127.0.0.1:5432/banking_demo"
    
    # API Keys
    openai_api_key: Optional[str] = None
    sambanova_api_key: Optional[str] = None
    allow_user_keys: bool = False
    require_user_keys: bool = False
    
    # Intent Classifier
    intent_classifier_model_provider: str = "sambanova"
    intent_classifier_model: str = "Qwen3-32B"
    intent_classifier_url: str = "https://api.sambanova.ai/v1/chat/completions"
    
    # OpenAI
    default_model: str = "gpt-4-turbo"
    
    # Transfer Limits
    max_transfer_amount: float = 1_000_000.0  # AED
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Observability
    phoenix_project_name: str = "bank-agent"
    phoenix_collector_endpoint: str = "http://localhost:6006/v1/traces"
    phoenix_api_key: Optional[str] = None
    phoenix_space_id: Optional[str] = None
    arize_endpoint: str = "https://otlp.eu-west-1a.arize.com/v1/traces"
    

    default_currency: str = "AED"
    bank_name: str = "Phoenix Digital Bank"

    max_message_length: int = 2000

    sambanova_max_tokens: int = 1500
    sambanova_reasoning_temperature: float = 0.6
    sambanova_reasoning_top_p: float = 0.95
    sambanova_standard_top_p: float = 0.01

    def is_arize_phoenix_enabled(self) -> bool:
        return bool(self.phoenix_api_key and self.phoenix_space_id)
    
    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


settings = Settings()
