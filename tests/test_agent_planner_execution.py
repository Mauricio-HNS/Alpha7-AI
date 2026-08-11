from app.agent import Agent
from app.executor import StepResult
from app.planner import Plan, PlanStep


class FakeLLM:
    def __init__(self) -> None:
        self.calls = []

    def complete(self, prompt: str, system: str = "") -> str:
        self.calls.append((prompt, system))
        if "untrusted-tool-output" in system:
            return "Plano executado com sucesso."
        return '{"action":"respond","action_input":{"answer":"fallback"}}'


class FakePlanner:
    def plan(self, goal: str, context: dict) -> Plan:
        assert "available_tools" in context
        return Plan(steps=[
            PlanStep(id=1, description="executar ferramenta", action="echo", action_input={"value": "ok"}),
            PlanStep(id=2, description="responder", action="respond", action_input={}),
        ])


class FakeTool:
    name = "echo"
    description = "Retorna um valor."

    def run(self, **kwargs) -> str:
        return kwargs["value"]


def test_agent_connects_planner_to_executor() -> None:
    llm = FakeLLM()
    agent = Agent(llm=llm, tools=[FakeTool()], planner=FakePlanner())

    result = agent.run("execute algo")

    assert result.response == "Plano executado com sucesso."
    assert result.tool_used == "echo"
    assert "success=True" in (result.tool_output or "")
    assert "output='ok'" in (result.tool_output or "")


def test_agent_falls_back_to_direct_decision_when_planner_fails() -> None:
    class BrokenPlanner:
        def plan(self, goal: str, context: dict) -> Plan:
            raise RuntimeError("planner offline")

    llm = FakeLLM()
    agent = Agent(llm=llm, tools=[], planner=BrokenPlanner())

    result = agent.run("responda")

    assert result.response == "fallback"


class FakeExecutor:
    def run_plan(self, plan: Plan) -> list[StepResult]:
        return [StepResult(step_id=1, action="echo", output="fake", success=True)]


def test_agent_accepts_custom_executor() -> None:
    llm = FakeLLM()
    agent = Agent(llm=llm, tools=[FakeTool()], planner=FakePlanner(), executor=FakeExecutor())

    result = agent.run("execute algo")

    assert result.response == "Plano executado com sucesso."
    assert "output='fake'" in (result.tool_output or "")
