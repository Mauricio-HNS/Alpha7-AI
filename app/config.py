"""Centralized application configuration."""
from __future__ import annotations

import os

from pydantic import BaseModel


class Settings(BaseModel):
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    embedding_model: str = "bge-m3"
    llm_timeout: int = 60
    max_steps: int = 5
    max_tool_calls: int = 10
    memory_db_path: str = "data/memory.db"


def load_settings() -> Settings:
    return Settings(
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        ollama_model=os.getenv("OLLAMA_MODEL", "llama3.2"),
        embedding_model=os.getenv("EMBEDDING_MODEL", "bge-m3"),
        llm_timeout=int(os.getenv("LLM_TIMEOUT", "60")),
        max_steps=int(os.getenv("MAX_STEPS", "5")),
        max_tool_calls=int(os.getenv("MAX_TOOL_CALLS", "10")),
        memory_db_path=os.getenv("MEMORY_DB_PATH", "data/memory.db"),
    )


settings = load_settings()
