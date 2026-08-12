"""
Executor - executa planos com limites explícitos de segurança.

O Executor não decide nem avalia; ele executa passos ordenados e reporta
resultados. Limites de passos e chamadas de ferramentas evitam loops ou
workflows acidentalmente grandes enquanto o projeto evolui para autonomia.
"""
from __future__ import annotations

import logging
from typing import Optional, Protocol

from pydantic import BaseModel

from app.planner import Plan, PlanStep
from app.tools.base import ITool

logger = logging.getLogger(__name__)


class StepResult(BaseModel):
    step_id: int
    action: str
    output: Optional[str] = None
    success: bool
    error: Optional[str] = None


class IExecutor(Protocol):
    def execute(self, step: PlanStep) -> StepResult:
        """Executa um único passo de um plano."""
        ...

    def run_plan(self, plan: Plan) -> list[StepResult]:
        """Executa um plano respeitando os limites configurados."""
        ...


class ToolExecutor:
    """Executor real com limites de passos e chamadas de ferramentas."""

    def __init__(
        self,
        tools: dict[str, ITool],
        max_steps: int = 5,
        max_tool_calls: int = 10,
    ) -> None:
        self.tools = tools
        self.max_steps = max(1, min(max_steps, 10))
        self.max_tool_calls = max(1, max_tool_calls)

    def execute(self, step: PlanStep) -> StepResult:
        if step.action == "respond":
            logger.info("EXECUTOR | step=%d action=respond (sem ferramenta a executar)", step.id)
            return StepResult(step_id=step.id, action=step.action, output=None, success=True)

        tool = self.tools.get(step.action)
        if tool is None:
            error = f"Ferramenta '{step.action}' não existe."
            logger.warning("EXECUTOR | step=%d %s", step.id, error)
            return StepResult(step_id=step.id, action=step.action, success=False, error=error)

        try:
            output = tool.run(**step.action_input)
            logger.info("EXECUTOR | step=%d action=%s output=%r", step.id, step.action, output)
            return StepResult(step_id=step.id, action=step.action, output=output, success=True)
        except Exception as exc:
            error = str(exc)
            logger.exception("EXECUTOR | step=%d action=%s falhou", step.id, step.action)
            return StepResult(step_id=step.id, action=step.action, success=False, error=error)

    def run_plan(self, plan: Plan) -> list[StepResult]:
        results: list[StepResult] = []
        tool_calls = 0

        if len(plan.steps) > self.max_steps:
            error = f"Plano excede o limite de {self.max_steps} passos."
            logger.warning("EXECUTOR | %s", error)
            return [StepResult(step_id=plan.steps[0].id, action="plan", success=False, error=error)]

        for step in plan.steps:
            if step.action != "respond" and tool_calls >= self.max_tool_calls:
                error = f"Limite de {self.max_tool_calls} chamadas de ferramentas atingido."
                logger.warning("EXECUTOR | step=%d %s", step.id, error)
                results.append(StepResult(step_id=step.id, action=step.action, success=False, error=error))
                break

            if step.action != "respond":
                tool_calls += 1

            result = self.execute(step)
            results.append(result)
            if not result.success:
                logger.warning("EXECUTOR | plano interrompido no passo %d (falha)", step.id)
                break

        return results
