"""Safe execution of validated Zero-Agent plans."""
from __future__ import annotations

import logging
from typing import Optional, Protocol

from pydantic import BaseModel

from app.config import settings
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
        """Executa os passos em ordem, parando na primeira falha."""
        ...


class ToolExecutor:
    """Executor fail-fast com limite explícito de chamadas de ferramenta."""

    def __init__(self, tools: dict[str, ITool], max_tool_calls: Optional[int] = None) -> None:
        self.tools = tools
        configured_limit = settings.max_tool_calls if max_tool_calls is None else max_tool_calls
        if configured_limit < 1:
            raise ValueError("max_tool_calls deve ser positivo")
        self.max_tool_calls = configured_limit

    def execute(self, step: PlanStep) -> StepResult:
        if step.action == "respond":
            logger.info("EXECUTOR | step=%d action=respond", step.id)
            return StepResult(step_id=step.id, action=step.action, output=None, success=True)

        tool = self.tools.get(step.action)
        if tool is None:
            logger.warning("EXECUTOR | step=%d action_unavailable", step.id)
            return StepResult(
                step_id=step.id,
                action=step.action,
                success=False,
                error="Ferramenta indisponível.",
            )

        try:
            output = tool.run(**step.action_input)
            if not isinstance(output, str):
                output = str(output)
            logger.info(
                "EXECUTOR | step=%d action=%s output_chars=%d",
                step.id,
                step.action,
                len(output),
            )
            return StepResult(step_id=step.id, action=step.action, output=output, success=True)
        except Exception:
            # Full exception details remain available to server-side logging only.
            # Never propagate exception text because it may contain paths, credentials,
            # connection strings, provider responses, or other implementation details.
            logger.exception("EXECUTOR | step=%d action=%s failed", step.id, step.action)
            return StepResult(
                step_id=step.id,
                action=step.action,
                success=False,
                error="A execução da ferramenta falhou.",
            )

    def run_plan(self, plan: Plan) -> list[StepResult]:
        plan.validate_sequence()
        results: list[StepResult] = []
        tool_calls = 0

        for step in plan.steps:
            if step.action != "respond":
                if tool_calls >= self.max_tool_calls:
                    error = f"Limite de {self.max_tool_calls} chamadas de ferramenta atingido."
                    results.append(
                        StepResult(step_id=step.id, action=step.action, success=False, error=error)
                    )
                    logger.warning("EXECUTOR | tool_call_limit_reached")
                    break
                tool_calls += 1

            result = self.execute(step)
            results.append(result)
            if not result.success:
                logger.warning("EXECUTOR | plan_stopped step=%d", step.id)
                break

        return results
