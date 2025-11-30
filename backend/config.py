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
    
    # Intent Classifier
    intent_classifier_model: str = "sambanova"
    intent_classifier_url: str = "https://api.sambanova.ai/v1/chat/completions"
    
    # Transfer Limits
    max_transfer_amount: float = 1_000_000.0  # AED
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Observability
    phoenix_project_name: str = "bank-agent"
    phoenix_collector_endpoint: str = "http://localhost:6006/v1/traces"
    
    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


settings = Settings()
