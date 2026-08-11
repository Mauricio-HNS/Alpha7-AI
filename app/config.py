"""Centralized application configuration."""
from __future__ import annotations

import os

from pydantic import BaseModel, Field, field_validator


class Settings(BaseModel):
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gemma3:latest"
    embedding_model: str = "bge-m3:latest"
    llm_timeout: int = Field(default=60, ge=1, le=600)
    max_steps: int = Field(default=5, ge=1, le=10)
    max_tool_calls: int = Field(default=10, ge=1, le=100)
    memory_db_path: str = "data/memory.db"
    semantic_min_score: float = Field(default=0.35, ge=-1.0, le=1.0)
    max_input_chars: int = Field(default=12_000, ge=1_000, le=100_000)
    max_context_chars: int = Field(default=20_000, ge=1_000, le=100_000)

    @field_validator("ollama_base_url")
    @classmethod
    def validate_base_url(cls, value: str) -> str:
        value = value.strip().rstrip("/")
        if not value.startswith(("http://", "https://")):
            raise ValueError("OLLAMA_BASE_URL deve começar com http:// ou https://")
        return value

    @field_validator("ollama_model", "embedding_model")
    @classmethod
    def validate_model_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Nome do modelo não pode ser vazio")
        return value


def _env_int(name: str, default: str) -> int:
    return int(os.getenv(name, default))


def load_settings() -> Settings:
    return Settings(
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        ollama_model=os.getenv("OLLAMA_MODEL", "gemma3:latest"),
        embedding_model=os.getenv("EMBEDDING_MODEL", "bge-m3:latest"),
        llm_timeout=_env_int("LLM_TIMEOUT", "60"),
        max_steps=_env_int("MAX_STEPS", "5"),
        max_tool_calls=_env_int("MAX_TOOL_CALLS", "10"),
        memory_db_path=os.getenv("MEMORY_DB_PATH", "data/memory.db"),
        semantic_min_score=float(os.getenv("SEMANTIC_MIN_SCORE", "0.35")),
        max_input_chars=_env_int("MAX_INPUT_CHARS", "12000"),
        max_context_chars=_env_int("MAX_CONTEXT_CHARS", "20000"),
    )


settings = load_settings()
