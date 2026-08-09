"""
Abstração do LLM.

O restante do sistema nunca deve depender diretamente do Ollama (ou de
qualquer outro provedor). Tudo passa pelo protocolo ILLM. Isso permite
trocar o provedor (OpenAI, Anthropic, um transformer local, etc.) sem
tocar no Agent.
"""
from __future__ import annotations

import logging
from typing import Optional, Protocol

import requests

from app.config import settings

logger = logging.getLogger(__name__)


class ILLM(Protocol):
    def complete(self, prompt: str, system: Optional[str] = None) -> str:
        """Envia um prompt (com system prompt opcional) e retorna o texto de resposta."""
        ...


class OllamaProvider:
    """Implementação de ILLM usando um servidor Ollama local (/api/generate)."""

    def __init__(
        self,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> None:
        self.model = model or settings.ollama_model
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.timeout = timeout or settings.llm_timeout

    def complete(self, prompt: str, system: Optional[str] = None) -> str:
        payload: dict = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        if system is not None:
            payload["system"] = system
            # Se o system prompt pede explicitamente JSON, força o Ollama
            # a restringir a saída a JSON válido.
            if "JSON" in system or "json" in system:
                payload["format"] = "json"

        logger.debug("OllamaProvider.complete -> POST %s/api/generate | model=%s", self.base_url, self.model)

        response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")
