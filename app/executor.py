"""
Executor - responsável por executar os passos de um Plan (v0.5) usando as
ferramentas registradas no Agent.

O Executor não decide o que fazer (isso é papel do Planner) e não avalia o
resultado final (isso é papel do Evaluator); ele só executa um passo por vez
e reporta o que aconteceu. Falha em um passo interrompe o plano (fail-fast);
repasse de falhas parciais e replanejamento ficam para um incremento futuro
(ver PROJECT_CONTEXT.md, seção v0.5).
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
        """Executa um único passo de um plano e retorna o resultado."""
        ...

    def run_plan(self, plan: Plan) -> list[StepResult]:
        """Executa os passos de um plano em ordem, parando na primeira falha."""
        ...


class ToolExecutor:
    """Executor real: roda cada PlanStep usando as ferramentas do Agent."""

    def __init__(self, tools: dict[str, ITool]) -> None:
        self.tools = tools

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
        for step in plan.steps:
            result = self.execute(step)
            results.append(result)
            if not result.success:
                logger.warning(
                    "EXECUTOR | plano interrompido no passo %d (falha); "
                    "replanejamento e falhas parciais ficam para incremento futuro",
                    step.id,
                )
                break
        return results
