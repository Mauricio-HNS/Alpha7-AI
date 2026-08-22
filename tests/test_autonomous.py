from app.agent import AgentResult
from app.autonomous import AutonomousRunner
from app.reflection import ReflectionResult


class FakeAgent:
    def __init__(self):
        self.calls = []

    def run(self, task: str) -> AgentResult:
        self.calls.append(task)
        return AgentResult(response=f"resposta {len(self.calls)}")


class FakeReflector:
    def __init__(self, reflections):
        self.reflections = iter(reflections)

    def reflect(self, task: str, result: AgentResult) -> ReflectionResult:
        return next(self.reflections)


def test_success_on_first_attempt_does_not_retry():
    agent = FakeAgent()
    reflector = FakeReflector([
        ReflectionResult(success=True, score=1.0, critique="ok", retry=False)
    ])
    runner = AutonomousRunner(agent, reflector, max_iterations=5)

    result = runner.run("faça X")

    assert len(agent.calls) == 1
    assert result.completed is True
    assert len(result.attempts) == 1


def test_failed_attempt_retries_with_correction():
    agent = FakeAgent()
    reflector = FakeReflector([
        ReflectionResult(success=False, score=0.2, critique="faltou teste", correction="rode os testes", retry=True),
        ReflectionResult(success=True, score=1.0, critique="ok", correction="", retry=False),
    ])
    runner = AutonomousRunner(agent, reflector, max_iterations=3)

    result = runner.run("implemente X")

    assert len(agent.calls) == 2
    assert "rode os testes" in agent.calls[1]
    assert result.completed is True


def test_iteration_budget_stops_loop():
    agent = FakeAgent()
    reflector = FakeReflector([
        ReflectionResult(success=False, score=0.0, critique="falhou", correction="tente de novo", retry=True),
        ReflectionResult(success=False, score=0.0, critique="falhou", correction="tente de novo", retry=True),
    ])
    runner = AutonomousRunner(agent, reflector, max_iterations=2)

    result = runner.run("faça X")

    assert len(agent.calls) == 2
    assert result.completed is False
    assert len(result.attempts) == 2
