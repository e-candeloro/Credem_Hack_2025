import os
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from pydantic import Field, validator
from pydantic_settings import BaseSettings

# Load .env file if it exists
load_dotenv()


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application
    app_name: str = Field(default="AI HR System", env="APP_NAME")
    version: str = Field(default="1.0.0", env="VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")

    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")

    # Database (for future use)
    database_url: str | None = Field(default=None, env="DATABASE_URL")

    # Security
    secret_key: str = Field(
        default="your-secret-key-change-in-production", env="SECRET_KEY"
    )
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    # External APIs (for future use)
    openai_api_key: str | None = Field(default=None, env="OPENAI_API_KEY")
    llm_api_key: str | None = Field(default=None, env="LLM_API_KEY")
    google_api_key: str | None = Field(default=None, env="GOOGLE_API_KEY")
    vision_llm_api_key: str | None = Field(default=None, env="VISION_LLM_API_KEY")

    # CORS
    allowed_origins: list[str] = Field(
        default=[
            "http://localhost:8501",
            "http://localhost:3000",
            "http://backend:8000",
            "http://ai-hr-backend:8000",
        ],
        env="ALLOWED_ORIGINS",
    )

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    @validator("debug", pre=True)
    def parse_debug(cls, v):
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return v

    @validator("environment")
    def validate_environment(cls, v):
        allowed = ["development", "staging", "production", "test"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
