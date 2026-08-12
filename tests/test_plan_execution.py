from typing import Optional

from app.agent import Agent
from app.executor import ToolExecutor
from app.planner import Plan, PlanStep


class FakeLLM:
    def __init__(self, responses: list[str]) -> None:
        self.responses = list(responses)
        self.calls: list[tuple[str, Optional[str]]] = []

    def complete(self, prompt: str, system: Optional[str] = None) -> str:
        self.calls.append((prompt, system))
        return self.responses.pop(0)


class FakePlanner:
    def __init__(self, plan: Plan) -> None:
        self.plan_value = plan

    def plan(self, goal: str, context: dict) -> Plan:
        return self.plan_value


class FakeTool:
    name = "filesystem"
    description = "Fake filesystem tool."

    def __init__(self) -> None:
        self.calls: list[dict] = []

    def run(self, **kwargs) -> str:
        self.calls.append(kwargs)
        return "README.md\napp/\ntests/"


def test_planner_and_executor_complete_a_workflow() -> None:
    plan = Plan(
        steps=[
            PlanStep(
                id=1,
                description="listar arquivos",
                action="filesystem",
                action_input={"action": "list", "path": "."},
            ),
            PlanStep(
                id=2,
                description="concluir",
                action="respond",
                action_input={},
            ),
        ]
    )
    llm = FakeLLM(["O plano foi executado e os arquivos foram encontrados."])
    tool = FakeTool()
    planner = FakePlanner(plan)
    executor = ToolExecutor({tool.name: tool})
    agent = Agent(llm=llm, tools=[tool], planner=planner, executor=executor)

    result = agent.run("Liste os arquivos do projeto e conclua.")

    assert result.response == "O plano foi executado e os arquivos foram encontrados."
    assert result.plan == plan
    assert len(result.plan_results) == 2
    assert result.plan_results[0].success is True
    assert result.plan_results[1].success is True
    assert tool.calls == [{"action": "list", "path": "."}]
    assert len(llm.calls) == 1


def test_executor_failure_is_reported_to_final_model() -> None:
    plan = Plan(
        steps=[
            PlanStep(
                id=1,
                description="listar arquivos",
                action="filesystem",
                action_input={"action": "list", "path": "."},
            ),
            PlanStep(
                id=2,
                description="não deve executar",
                action="filesystem",
                action_input={"action": "list", "path": "./missing"},
            ),
        ]
    )

    class BrokenTool(FakeTool):
        def run(self, **kwargs) -> str:
            raise RuntimeError("disco indisponível")

    llm = FakeLLM(["A execução falhou no primeiro passo."])
    tool = BrokenTool()
    agent = Agent(
        llm=llm,
        tools=[tool],
        planner=FakePlanner(plan),
        executor=ToolExecutor({tool.name: tool}),
    )

    result = agent.run("Execute o plano.")

    assert result.response == "A execução falhou no primeiro passo."
    assert len(result.plan_results) == 1
    assert result.plan_results[0].success is False
    assert "disco indisponível" in (result.plan_results[0].error or "")
