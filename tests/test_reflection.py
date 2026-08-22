from app.agent import AgentResult
from app.reflection import ReflectionEngine
from app.policy import BehavioralPolicy


class FakeLLM:
    def __init__(self, response: str):
        self.response = response

    def complete(self, prompt: str, system: str | None = None) -> str:
        return self.response


def test_reflection_accepts_valid_judgement():
    llm = FakeLLM('{"success": true, "score": 0.9, "critique": "ok", "correction": "", "retry": false}')
    engine = ReflectionEngine(llm, BehavioralPolicy())
    result = engine.reflect("faça X", AgentResult(response="X feito"))

    assert result.success is True
    assert result.score == 0.9
    assert result.retry is False


def test_reflection_fails_closed_on_invalid_json():
    llm = FakeLLM("not json")
    engine = ReflectionEngine(llm, BehavioralPolicy())
    result = engine.reflect("faça X", AgentResult(response="X"))

    assert result.success is False
    assert result.retry is False
    assert result.score == 0.0


def test_approval_required_cannot_trigger_retry():
    llm = FakeLLM('{"success": true, "score": 1.0, "critique": "ok", "correction": "execute", "retry": true}')
    engine = ReflectionEngine(llm, BehavioralPolicy())
    result = engine.reflect(
        "faça X",
        AgentResult(response="bloqueado", approval_required=True),
    )

    assert result.success is False
    assert result.retry is False
