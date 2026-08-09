from typing import Optional

from app.agent import Agent


class FakeLLM:
    """LLM fake: retorna respostas pré-definidas em sequência, uma por chamada."""

    def __init__(self, responses: list[str]) -> None:
        self._responses = list(responses)
        self.calls: list[tuple[str, Optional[str]]] = []

    def complete(self, prompt: str, system: Optional[str] = None) -> str:
        self.calls.append((prompt, system))
        return self._responses.pop(0)


class FakeTool:
    name = "filesystem"
    description = "Ferramenta fake para testes."

    def __init__(self, fixed_output: str) -> None:
        self.fixed_output = fixed_output
        self.called_with: Optional[dict] = None

    def run(self, **kwargs) -> str:
        self.called_with = kwargs
        return self.fixed_output


def test_agent_responds_directly_without_tool() -> None:
    decision = '{"action": "respond", "action_input": {"answer": "Olá, tudo bem!"}, "reasoning": "saudação simples"}'
    llm = FakeLLM(responses=[decision])
    agent = Agent(llm=llm, tools=[])

    result = agent.run("oi, tudo bem?")

    assert result.response == "Olá, tudo bem!"
    assert result.tool_used is None
    assert len(llm.calls) == 1


def test_agent_uses_tool_and_produces_final_answer() -> None:
    decision = (
        '{"action": "filesystem", "action_input": {"action": "list", "path": "."}, '
        '"reasoning": "usuário pediu para listar arquivos"}'
    )
    final_answer = "Os arquivos deste projeto são: app/, tests/, README.md."

    llm = FakeLLM(responses=[decision, final_answer])
    tool = FakeTool(fixed_output="app/\ntests/\nREADME.md")
    agent = Agent(llm=llm, tools=[tool])

    result = agent.run("Liste os arquivos deste projeto.")

    assert result.tool_used == "filesystem"
    assert tool.called_with == {"action": "list", "path": "."}
    assert result.tool_output == "app/\ntests/\nREADME.md"
    assert result.response == final_answer
    assert len(llm.calls) == 2


def test_agent_degrades_gracefully_on_invalid_json() -> None:
    llm = FakeLLM(responses=["isso não é um JSON válido"])
    agent = Agent(llm=llm, tools=[])

    result = agent.run("qualquer coisa")

    assert result.response == "isso não é um JSON válido"
    assert result.tool_used is None


def test_agent_handles_tool_execution_error() -> None:
    decision = '{"action": "filesystem", "action_input": {"action": "list", "path": "."}}'
    final_answer = "Houve um erro ao acessar os arquivos."

    llm = FakeLLM(responses=[decision, final_answer])

    class BrokenTool:
        name = "filesystem"
        description = "Ferramenta que sempre falha."

        def run(self, **kwargs) -> str:
            raise RuntimeError("disco indisponível")

    agent = Agent(llm=llm, tools=[BrokenTool()])
    result = agent.run("Liste os arquivos deste projeto.")

    assert result.tool_used == "filesystem"
    assert "Erro ao executar a ferramenta" in result.tool_output
    assert result.response == final_answer
