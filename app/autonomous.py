"""Bounded autonomous loop: execute, reflect, correct, and retry."""
from __future__ import annotations

from pydantic import BaseModel, Field

from app.agent import Agent, AgentResult
from app.reflection import ReflectionEngine, ReflectionResult


class AutonomousAttempt(BaseModel):
    number: int
    result: AgentResult
    reflection: ReflectionResult


class AutonomousRunResult(BaseModel):
    response: str
    attempts: list[AutonomousAttempt] = Field(default_factory=list)
    completed: bool = False


class AutonomousRunner:
    """Runs the Agent with a strict iteration budget.

    The runner never edits model weights. Learning remains an explicit,
    approved-data/training pipeline outside the execution loop.
    """

    def __init__(self, agent: Agent, reflector: ReflectionEngine, max_iterations: int = 5) -> None:
        self.agent = agent
        self.reflector = reflector
        self.max_iterations = max(1, max_iterations)

    def run(self, task: str) -> AutonomousRunResult:
        attempts: list[AutonomousAttempt] = []
        current_task = task

        for number in range(1, self.max_iterations + 1):
            result = self.agent.run(current_task)
            reflection = self.reflector.reflect(task, result)
            attempts.append(AutonomousAttempt(number=number, result=result, reflection=reflection))

            if reflection.success or result.approval_required or not reflection.retry:
                return AutonomousRunResult(
                    response=result.response,
                    attempts=attempts,
                    completed=reflection.success,
                )

            correction = reflection.correction.strip()
            if not correction:
                return AutonomousRunResult(response=result.response, attempts=attempts, completed=False)

            current_task = (
                f"Tarefa original:\n{task}\n\n"
                f"Correção determinada pelo judge para a próxima tentativa:\n{correction}\n\n"
                "Execute novamente a tarefa aplicando somente essa correção."
            )

        return AutonomousRunResult(
            response=attempts[-1].result.response,
            attempts=attempts,
            completed=False,
        )
