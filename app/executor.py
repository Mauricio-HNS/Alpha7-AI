"""
Stub da interface de execução (Executor).

Sem lógica real ainda. No v0.1, a execução de uma única ferramenta
acontece diretamente em Agent._act_and_respond (ver app/agent.py). Um
Executor dedicado - capaz de rodar múltiplos passos de um plano, lidar
com falhas parciais e retries - passa a fazer sentido a partir do v0.3,
quando existir um Planner de verdade produzindo múltiplos passos.
"""
from __future__ import annotations

from typing import Any, Protocol


class IExecutor(Protocol):
    def execute(self, step: dict[str, Any]) -> Any:
        """Executa um único passo de um plano e retorna o resultado."""
        ...
