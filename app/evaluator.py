"""
Stub da interface de avaliação (Evaluator).

Sem lógica real ainda. Avaliar a qualidade de um resultado (sucesso,
falha, qualidade da solução, necessidade de nova tentativa) é o alvo do
v0.4, depois que existirem múltiplos passos (Planner/Executor) para
avaliar. No v0.1, o agente não se autoavalia - apenas executa e responde.
"""
from __future__ import annotations

from typing import Any, Protocol


class IEvaluator(Protocol):
    def evaluate(self, task: str, result: Any) -> dict[str, Any]:
        """Avalia o resultado de uma tarefa e retorna um veredito estruturado."""
        ...
