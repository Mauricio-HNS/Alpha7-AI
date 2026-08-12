from typing import Optional

from app.agent import Agent
from app.evaluator import Evaluation, ReflectiveEvaluator, SimpleEvaluator


class FakeLLM:
    def __init__(self, responses: list[str]) -> None:
        self.responses = list(responses)
        self.calls: list[tuple[str, Optional[str]]] = []

    def complete(self, prompt: str, system: Optional[str] = None) -> str:
        self.calls.append((prompt, system))
        return self.responses.pop(0)


class FakeTool:
    name = "filesystem"
    description = "fake"

    def run(self, **kwargs) -> str:
        return "real tool output"


def test_direct_response_is_success_with_moderate_importance() -> None:
    evaluator = SimpleEvaluator()
    result = evaluator.evaluate(task="oi", tool_used=None, tool_output=None, response="Olá!")
    assert result.success is True
    assert result.importance == 0.4


def test_successful_tool_use_is_high_importance() -> None:
    evaluator = SimpleEvaluator()
    result = evaluator.evaluate("task", "filesystem", "data", "answer")
    assert result.success is True
    assert result.importance == 0.7


def test_failed_tool_use_is_low_importance() -> None:
    evaluator = SimpleEvaluator()
    result = evaluator.evaluate(
        "task", "filesystem", "Erro ao executar a ferramenta 'filesystem': failure", "error"
    )
    assert result.success is False
    assert result.importance == 0.3


def test_reflective_evaluator_parses_structured_result() -> None:
    llm = FakeLLM(['{"success":false,"evaluation":"resposta incompleta","importance":0.6}'])
    evaluator = ReflectiveEvaluator(llm)
    result = evaluator.evaluate("task", "filesystem", "data", "bad answer")
    assert result == Evaluation(success=False, evaluation="resposta incompleta", importance=0.6)


def test_reflective_evaluator_falls_back_on_invalid_json() -> None:
    llm = FakeLLM(["invalid"])
    evaluator = ReflectiveEvaluator(llm)
    result = evaluator.evaluate("task", "filesystem", "data", "answer")
    assert result.success is True
    assert result.importance == 0.7


def test_agent_reflects_once_after_failed_evaluation() -> None:
    llm = FakeLLM(
        [
            '{"action":"filesystem","action_input":{}}',
            "first answer",
            '{"success":false,"evaluation":"answer incomplete","importance":0.5}',
            "corrected answer",
            '{"success":true,"evaluation":"answer corrected","importance":0.9}',
        ]
    )
    agent = Agent(llm=llm, tools=[FakeTool()], evaluator=ReflectiveEvaluator(llm))
    result = agent.run("do the task")
    assert result.reflected is True
    assert result.response == "corrected answer"
    assert result.evaluation is not None
    assert result.evaluation.success is True
    assert len(llm.calls) == 5


def test_simple_evaluator_remains_deterministic() -> None:
    evaluator = SimpleEvaluator()
    result = evaluator.evaluate("task", None, None, "answer")
    assert result.success is True
    assert result.importance == 0.4
