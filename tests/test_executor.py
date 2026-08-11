from typing import Optional

import pytest

from app.executor import ToolExecutor
from app.planner import Plan, PlanStep


class FakeTool:
    def __init__(self, name: str, output: str = "", error: Optional[Exception] = None) -> None:
        self.name = name
        self.description = "Ferramenta fake para testes."
        self.output = output
        self.error = error
        self.called_with: Optional[dict] = None

    def run(self, **kwargs) -> str:
        self.called_with = kwargs
        if self.error is not None:
            raise self.error
        return self.output


def test_executor_runs_tool_step_and_returns_output() -> None:
    tool = FakeTool("filesystem", output="app/\ntests/")
    executor = ToolExecutor(tools={"filesystem": tool})
    step = PlanStep(id=1, description="listar arquivos", action="filesystem", action_input={"action": "list", "path": "."})

    result = executor.execute(step)

    assert result.success is True
    assert result.output == "app/\ntests/"
    assert tool.called_with == {"action": "list", "path": "."}


def test_executor_respond_step_requires_no_tool() -> None:
    executor = ToolExecutor(tools={})
    step = PlanStep(id=1, description="responder diretamente", action="respond", action_input={})

    result = executor.execute(step)

    assert result.success is True
    assert result.output is None


def test_executor_returns_failure_for_unknown_tool() -> None:
    executor = ToolExecutor(tools={})
    step = PlanStep(id=1, description="usar ferramenta inexistente", action="shell", action_input={})

    result = executor.execute(step)

    assert result.success is False
    assert "shell" in result.error


def test_executor_captures_tool_exception_as_failure() -> None:
    tool = FakeTool("filesystem", error=RuntimeError("disco indisponível"))
    executor = ToolExecutor(tools={"filesystem": tool})
    step = PlanStep(id=1, description="ler arquivo", action="filesystem", action_input={"action": "read", "path": "x"})

    result = executor.execute(step)

    assert result.success is False
    assert "disco indisponível" in result.error


def test_run_plan_executes_steps_in_order() -> None:
    tool = FakeTool("filesystem", output="ok")
    executor = ToolExecutor(tools={"filesystem": tool})
    plan = Plan(
        steps=[
            PlanStep(id=1, description="listar", action="filesystem", action_input={}),
            PlanStep(id=2, description="responder", action="respond", action_input={}),
        ]
    )

    results = executor.run_plan(plan)

    assert [r.step_id for r in results] == [1, 2]
    assert all(r.success for r in results)


def test_run_plan_stops_on_first_failure() -> None:
    tool = FakeTool("filesystem", error=RuntimeError("falhou"))
    executor = ToolExecutor(tools={"filesystem": tool})
    plan = Plan(
        steps=[
            PlanStep(id=1, description="passo que falha", action="filesystem", action_input={}),
            PlanStep(id=2, description="nunca deveria rodar", action="respond", action_input={}),
        ]
    )

    results = executor.run_plan(plan)

    assert len(results) == 1
    assert results[0].success is False
