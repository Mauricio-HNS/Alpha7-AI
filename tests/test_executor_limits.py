from app.executor import ToolExecutor
from app.planner import Plan, PlanStep


class FakeTool:
    name = "filesystem"
    description = "fake"

    def __init__(self) -> None:
        self.calls = 0

    def run(self, **kwargs) -> str:
        self.calls += 1
        return "ok"


def test_executor_enforces_tool_call_limit() -> None:
    tool = FakeTool()
    executor = ToolExecutor({"filesystem": tool}, max_steps=5, max_tool_calls=2)
    plan = Plan(steps=[
        PlanStep(id=1, description="one", action="filesystem"),
        PlanStep(id=2, description="two", action="filesystem"),
        PlanStep(id=3, description="three", action="filesystem"),
    ])

    results = executor.run_plan(plan)

    assert [result.success for result in results] == [True, True, False]
    assert "limite de 2 chamadas" in results[-1].error
    assert tool.calls == 2


def test_executor_rejects_plan_over_step_limit_before_execution() -> None:
    tool = FakeTool()
    executor = ToolExecutor({"filesystem": tool}, max_steps=2, max_tool_calls=10)
    plan = Plan(steps=[
        PlanStep(id=1, description="one", action="filesystem"),
        PlanStep(id=2, description="two", action="filesystem"),
        PlanStep(id=3, description="three", action="respond"),
    ])

    results = executor.run_plan(plan)

    assert len(results) == 1
    assert results[0].success is False
    assert "excede o limite de 2 passos" in results[0].error
    assert tool.calls == 0
