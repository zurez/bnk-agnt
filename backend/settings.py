"""
Settings configuration for the Bank Agent application.
Loads environment variables and provides typed access to configuration values.
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gpt-4-turbo")
    
    # SambaNova
    SAMBANOVA_API_KEY: str = os.getenv("SAMBANOVA_API_KEY", "")
    
    # Phoenix Tracing
    PHOENIX_ENDPOINT: str = os.getenv("PHOENIX_ENDPOINT", "http://localhost:6006/v1/traces")
    PHOENIX_PROJECT_NAME: str = os.getenv("PHOENIX_PROJECT_NAME", "bank-agent")
    PHOENIX_SPACE_ID: Optional[str] = os.getenv("PHOENIX_SPACE_ID")
    PHOENIX_API_KEY: Optional[str] = os.getenv("PHOENIX_API_KEY")
    
    @classmethod
    def validate(cls) -> None:
        """Validate that required settings are present."""
        if not cls.DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable is required")
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")
    
    @classmethod
    def is_arize_phoenix_enabled(cls) -> bool:
        """Check if Arize Phoenix (cloud) tracing is enabled."""
        return bool(cls.PHOENIX_SPACE_ID and cls.PHOENIX_API_KEY)


# Create a singleton instance
settings = Settings()
