"""
backend/app/core/config.py
==========================
Application configuration and environment variables for the FastAPI backend.
"""

from __future__ import annotations
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

_ROOT = Path(__file__).resolve().parent.parent.parent.parent


class Settings(BaseSettings):
    PROJECT_NAME: str = "FinMate AI API"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security / JWT
    SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "finmate-ai-secret-key-super-secure-change-in-prod")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8501",
        "*",
    ]
    
    # Database
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", str(_ROOT / "financial_advisor.db"))
    
    # AI / LLM
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai").lower()
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    GOOGLE_API_KEY: str | None = os.getenv("GOOGLE_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    GOOGLE_MODEL: str = os.getenv("GOOGLE_MODEL", "gemini-2.0-flash")
    
    model_config = SettingsConfigDict(
        env_file=str(_ROOT / ".env"),
        extra="ignore"
    )


settings = Settings()
