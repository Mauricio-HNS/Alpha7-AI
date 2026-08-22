from typing import Any, Optional

from app.agent import Agent
from app.executor import ToolExecutor
from app.planner import Plan, PlanStep
from app.policy import BehavioralPolicy


class FakeLLM:
    def __init__(self, responses: list[str]) -> None:
        self.responses = list(responses)
        self.calls: list[tuple[str, Optional[str]]] = []

    def complete(self, prompt: str, system: Optional[str] = None) -> str:
        self.calls.append((prompt, system))
        return self.responses.pop(0)


class FakeTool:
    name = "filesystem"
    description = "fake filesystem"

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def run(self, **kwargs: Any) -> str:
        self.calls.append(kwargs)
        return "arquivo.txt"


class FakePlanner:
    def __init__(self, plan: Plan) -> None:
        self.plan_value = plan

    def plan(self, goal: str, context: dict[str, Any]) -> Plan:
        return self.plan_value


def test_agent_executes_planned_steps_through_executor() -> None:
    tool = FakeTool()
    planner = FakePlanner(
        Plan(
            steps=[
                PlanStep(
                    id=1,
                    description="listar arquivos",
                    action="filesystem",
                    action_input={"action": "list", "path": "."},
                )
            ]
        )
    )
    llm = FakeLLM(["Encontrei arquivo.txt."])
    agent = Agent(
        llm=llm,
        tools=[tool],
        planner=planner,
        executor=ToolExecutor({tool.name: tool}),
    )

    result = agent.run("Liste os arquivos.")

    assert tool.calls == [{"action": "list", "path": "."}]
    assert result.tool_used == "filesystem"
    assert result.plan_results[0].success is True
    assert result.tool_output == "step 1 (filesystem): arquivo.txt"
    assert result.response == "Encontrei arquivo.txt."
    assert len(llm.calls) == 1


def test_agent_checks_policy_before_each_planned_action() -> None:
    tool = FakeTool()
    planner = FakePlanner(
        Plan(
            steps=[
                PlanStep(
                    id=1,
                    description="listar arquivos",
                    action="filesystem",
                    action_input={"action": "list", "path": "."},
                )
            ]
        )
    )
    agent = Agent(
        llm=FakeLLM([]),
        tools=[tool],
        planner=planner,
        executor=ToolExecutor({tool.name: tool}),
        policy=BehavioralPolicy(require_approval_for_tools=["filesystem"]),
    )

    result = agent.run("Liste os arquivos.")

    assert result.approval_required is True
    assert "aprovação explícita" in result.response
    assert tool.calls == []
