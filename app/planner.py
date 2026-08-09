"""
Stub da interface de planejamento (Planner).

Sem lógica real ainda. No v0.1, a decisão de "responder direto vs usar
ferramenta" é simples o suficiente para viver dentro do próprio Agent
(ver app/agent.py). Um Planner de verdade - capaz de decompor um
objetivo em múltiplos passos e reavaliar o plano - é o alvo do v0.3.
"""
from __future__ import annotations

from typing import Any, Protocol


class IPlanner(Protocol):
    def plan(self, goal: str, context: dict[str, Any]) -> list[dict[str, Any]]:
        """Recebe um objetivo e retorna uma lista ordenada de passos planejados."""
        ...
