"""Single-attempt evaluation pipeline for v0.6.

This layer connects the existing Agent evaluation with the LLM judge without
adding retries to Agent.run(). Bounded retries remain a v0.7 concern.
"""
from __future__ import annotations

from pydantic import BaseModel

from app.agent import Agent, AgentResult
from app.reflection import ReflectionEngine, ReflectionResult


class EvaluatedRunResult(BaseModel):
    result: AgentResult
    reflection: ReflectionResult
    completed: bool = False


class EvaluationPipeline:
    """Execute exactly one agent attempt and evaluate it with the judge."""

    def __init__(self, agent: Agent, reflector: ReflectionEngine) -> None:
        self.agent = agent
        self.reflector = reflector

    def run(self, task: str) -> EvaluatedRunResult:
        result = self.agent.run(task)
        reflection = self.reflector.reflect(task, result)
        return EvaluatedRunResult(
            result=result,
            reflection=reflection,
            completed=reflection.success,
        )
