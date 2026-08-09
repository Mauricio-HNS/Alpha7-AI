"""
Evaluator - avaliação básica de resultados.

Escopo deste incremento (v0.2, 2/2): um avaliador simples e determinístico
(sem chamar o LLM), que só determina success/evaluation/importance a
partir do resultado observável de uma execução real do Agent. Nada de
avaliação sofisticada ainda (isso é v0.6 - Evaluation/Reflection no
roadmap).
"""
from __future__ import annotations

from typing import Optional, Protocol

from pydantic import BaseModel

# Marcador usado pelo Agent (app/agent.py) para sinalizar falha na
# execução de uma ferramenta. Mantido aqui para o evaluator reconhecer
# falhas sem precisar de outro canal de comunicação entre os dois módulos.
TOOL_ERROR_MARKER = "Erro ao executar a ferramenta"


class Evaluation(BaseModel):
    success: bool
    evaluation: str
    importance: float


class IEvaluator(Protocol):
    def evaluate(
        self,
        task: str,
        tool_used: Optional[str],
        tool_output: Optional[str],
        response: str,
    ) -> Evaluation:
        """Avalia o resultado de uma execução real e retorna um veredito estruturado."""
        ...


class SimpleEvaluator:
    """Implementação determinística de IEvaluator.

    Regras (deliberadamente simples):
    - Sem ferramenta usada (resposta direta) -> success=True, importance
      moderada (não sabemos se a resposta estava correta, só que o agente
      respondeu sem erro de execução).
    - Ferramenta usada e a observação contém o marcador de erro do Agent
      -> success=False, importance baixa.
    - Ferramenta usada com sucesso -> success=True, importance alta (uma
      ação real e bem-sucedida vale mais para recuperação futura do que
      uma resposta direta).
    """

    def evaluate(
        self,
        task: str,
        tool_used: Optional[str],
        tool_output: Optional[str],
        response: str,
    ) -> Evaluation:
        if tool_used is None:
            return Evaluation(
                success=True,
                evaluation="Resposta direta fornecida, sem uso de ferramenta.",
                importance=0.4,
            )

        if tool_output is not None and tool_output.startswith(TOOL_ERROR_MARKER):
            return Evaluation(
                success=False,
                evaluation=f"Falha ao executar a ferramenta '{tool_used}': {tool_output}",
                importance=0.3,
            )

        return Evaluation(
            success=True,
            evaluation=f"Ferramenta '{tool_used}' executada com sucesso.",
            importance=0.7,
        )
