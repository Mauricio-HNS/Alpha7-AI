from collections.abc import Iterator

from app.agent import Agent
from app.evaluation_pipeline import EvaluationPipeline
from app.reflection import ReflectionEngine


class FakeLLM:
    def __init__(self, responses: list[str]) -> None:
        self.responses: Iterator[str] = iter(responses)

    def complete(self, prompt: str, system: str | None = None) -> str:
        return next(self.responses)


def test_pipeline_evaluates_one_agent_attempt_without_retry() -> None:
    llm = FakeLLM(
        [
            '{"action":"respond","action_input":{"answer":"resposta inicial"}}',
            '{"success":true,"score":0.9,"critique":"ok","correction":"","retry":false}',
        ]
    )
    agent = Agent(llm=llm, tools=[])
    pipeline = EvaluationPipeline(agent, ReflectionEngine(llm))

    outcome = pipeline.run("teste")

    assert outcome.result.response == "resposta inicial"
    assert outcome.reflection.success is True
    assert outcome.reflection.score == 0.9
    assert outcome.completed is True


def test_pipeline_does_not_retry_when_judge_requests_correction() -> None:
    llm = FakeLLM(
        [
            '{"action":"respond","action_input":{"answer":"incompleta"}}',
            '{"success":false,"score":0.3,"critique":"faltou informação","correction":"incluir os dados","retry":true}',
        ]
    )
    agent = Agent(llm=llm, tools=[])
    pipeline = EvaluationPipeline(agent, ReflectionEngine(llm))

    outcome = pipeline.run("teste")

    assert outcome.completed is False
    assert outcome.reflection.retry is True
    assert outcome.reflection.correction == "incluir os dados"
