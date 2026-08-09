"""
Interface base para ferramentas.

Toda ferramenta precisa expor name, description (usados no prompt de
decisão do agente) e um método run(**kwargs) que efetivamente executa a
ação e retorna uma observação em texto.
"""
from __future__ import annotations

from typing import Any, Protocol


class ITool(Protocol):
    name: str
    description: str

    def run(self, **kwargs: Any) -> str:
        """Executa a ferramenta e retorna o resultado como texto (observação)."""
        ...
