"""
Zero-Agent v0.1 - CLI mínima.

Fluxo: usuário digita um pedido -> Agent decide (via LLM) se responde
direto ou usa a FileSystemTool -> executa -> responde.

Requer um servidor Ollama rodando localmente (ver README.md).
"""
from __future__ import annotations

from app.agent import Agent
from app.config import settings
from app.evaluator import SimpleEvaluator
from app.llm import OllamaProvider
from app.logging_config import setup_logging
from app.memory import SQLiteMemory
from app.tools.filesystem import FileSystemTool


def build_agent() -> Agent:
    llm = OllamaProvider(model=settings.ollama_model, base_url=settings.ollama_base_url)
    tools = [FileSystemTool(root_dir=".")]
    memory = SQLiteMemory(db_path=settings.memory_db_path)
    evaluator = SimpleEvaluator()
    return Agent(llm=llm, tools=tools, memory=memory, evaluator=evaluator)


def main() -> None:
    setup_logging()
    agent = build_agent()

    print("Zero-Agent v0.1")
    print(f"Modelo: {settings.ollama_model} | Ollama: {settings.ollama_base_url}")
    print("Digite 'sair' para encerrar.\n")

    while True:
        try:
            user_input = input("Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not user_input:
            continue
        if user_input.lower() in {"sair", "exit", "quit"}:
            break

        result = agent.run(user_input)
        print(f"\nAgent: {result.response}\n")
        if result.tool_used:
            print(f"[ferramenta usada: {result.tool_used}]\n")


if __name__ == "__main__":
    main()
