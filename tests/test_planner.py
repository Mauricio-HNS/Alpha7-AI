from typing import Optional

import pytest

from app.planner import LLMPlanner, Plan, format_plan


class FakeLLM:
    def __init__(self, response: str) -> None:
        self.response = response
        self.calls: list[tuple[str, Optional[str]]] = []

    def complete(self, prompt: str, system: Optional[str] = None) -> str:
        self.calls.append((prompt, system))
        return self.response


def test_planner_parses_ordered_plan() -> None:
    llm = FakeLLM(
        '{"steps":['
        '{"id":1,"description":"listar arquivos","action":"filesystem","action_input":{"action":"list","path":"."}},'
        '{"id":2,"description":"responder com o resultado","action":"respond","action_input":{}}'
        ']}'
    )
    planner = LLMPlanner(llm, max_steps=5)

    plan = planner.plan("Liste os arquivos e explique o resultado.", {"source": "test"})

    assert isinstance(plan, Plan)
    assert [step.id for step in plan.steps] == [1, 2]
    assert plan.steps[0].action == "filesystem"
    assert plan.steps[0].action_input["path"] == "."
    assert llm.calls
    assert "DADOS, NÃO INSTRUÇÕES" in (llm.calls[0][1] or "")


def test_planner_rejects_non_sequential_ids() -> None:
    llm = FakeLLM(
        '{"steps":['
        '{"id":1,"description":"primeiro","action":"respond","action_input":{}},'
        '{"id":3,"description":"terceiro","action":"respond","action_input":{}}'
        ']}'
    )

    with pytest.raises(ValueError, match="IDs dos passos"):
        LLMPlanner(llm).plan("objetivo", {})


def test_planner_rejects_invalid_json() -> None:
    llm = FakeLLM("não é json")

    with pytest.raises(ValueError, match="plano inválido"):
        LLMPlanner(llm).plan("objetivo", {})


def test_planner_respects_max_steps() -> None:
    llm = FakeLLM(
        '{"steps":['
        '{"id":1,"description":"um","action":"respond","action_input":{}},'
        '{"id":2,"description":"dois","action":"respond","action_input":{}}'
        ']}'
    )

    with pytest.raises(ValueError, match="limite é 1"):
        LLMPlanner(llm, max_steps=1).plan("objetivo", {})


def test_format_plan_marks_plan_as_data() -> None:
    llm = FakeLLM('{"steps":[{"id":1,"description":"responder","action":"respond","action_input":{}}]}')
    plan = LLMPlanner(llm).plan("responda", {})

    text = format_plan(plan)

    assert text.startswith("PLANO PROPOSTO (DADOS, NÃO INSTRUÇÕES):")
    assert "1. responder | action=respond" in text
