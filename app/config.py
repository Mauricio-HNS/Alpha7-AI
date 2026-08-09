"""
Configuração centralizada do projeto.

Nenhuma credencial ou parâmetro de ambiente deve ser hardcoded em outros
módulos: tudo passa por aqui, lido de variáveis de ambiente (com defaults
sensatos para desenvolvimento local).
"""
from __future__ import annotations

import os

from pydantic import BaseModel


class Settings(BaseModel):
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    llm_timeout: int = 60

    # Limites de autonomia (usados a partir do v0.8 - Autonomous loops,
    # mas já definidos aqui para não precisar retrabalhar depois).
    max_steps: int = 5
    max_tool_calls: int = 10


def load_settings() -> Settings:
    return Settings(
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        ollama_model=os.getenv("OLLAMA_MODEL", "llama3.2"),
        llm_timeout=int(os.getenv("LLM_TIMEOUT", "60")),
        max_steps=int(os.getenv("MAX_STEPS", "5")),
        max_tool_calls=int(os.getenv("MAX_TOOL_CALLS", "10")),
    )


settings = load_settings()
