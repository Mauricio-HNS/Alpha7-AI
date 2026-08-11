from typing import Optional

import pytest

from app.agent import Agent
from app.executor import ToolExecutor
from app.planner import Plan, PlanStep


class FakeLLM:
    def __init__(self, response: str) -> None:
        self.response = response

    def complete(self, prompt: str, system: Optional[str] = None) -> str:
        return self.response


class FakeTool:
    name = "filesystem"
    description = "fake"

    def run(self, **kwargs) -> str:
        return "ok"


def test_agent_rejects_unknown_tool_action() -> None:
    llm = FakeLLM('{"action":"shell","action_input":{}}')
    agent = Agent(llm=llm, tools=[FakeTool()])

    result = agent.run("execute shell")

    assert result.tool_used is None
    assert "não está disponível" in result.response


def test_agent_rejects_oversized_input() -> None:
    llm = FakeLLM('{"action":"respond","action_input":{"answer":"ok"}}')
    agent = Agent(llm=llm, tools=[])

    result = agent.run("x" * 12_001)

    assert "excede o limite" in result.response


def test_executor_validates_plan_sequence() -> None:
    executor = ToolExecutor({"filesystem": FakeTool()})
    invalid_plan = Plan(
        steps=[PlanStep(id=2, description="bad", action="filesystem", action_input={})]
    )

    with pytest.raises(ValueError, match="sequenciais"):
        executor.run_plan(invalid_plan)


def test_executor_enforces_tool_call_limit() -> None:
    executor = ToolExecutor({"filesystem": FakeTool()}, max_tool_calls=1)
    plan = Plan(
        steps=[
            PlanStep(id=1, description="first", action="filesystem", action_input={}),
            PlanStep(id=2, description="second", action="filesystem", action_input={}),
        ]
    )

    results = executor.run_plan(plan)

    assert results[0].success is True
    assert results[1].success is False
    assert "Limite de 1" in (results[1].error or "")
