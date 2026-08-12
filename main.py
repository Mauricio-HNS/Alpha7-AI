"""Zero-Agent CLI."""
from __future__ import annotations

from app.agent import Agent
from app.config import settings
from app.evaluator import SimpleEvaluator
from app.executor import ToolExecutor
from app.llm import OllamaProvider
from app.logging_config import setup_logging
from app.memory import OllamaEmbedder, SQLiteMemory
from app.planner import LLMPlanner
from app.tools.filesystem import FileSystemTool


def build_agent() -> Agent:
    llm = OllamaProvider(model=settings.ollama_model, base_url=settings.ollama_base_url)
    embedder = OllamaEmbedder(
        model=settings.embedding_model,
        base_url=settings.ollama_base_url,
    )
    tools = [FileSystemTool(root_dir=".")]
    memory = SQLiteMemory(db_path=settings.memory_db_path, embedder=embedder)
    evaluator = SimpleEvaluator()
    planner = LLMPlanner(llm, max_steps=settings.max_steps)
    executor = ToolExecutor({tool.name: tool for tool in tools})
    return Agent(
        llm=llm,
        tools=tools,
        memory=memory,
        evaluator=evaluator,
        planner=planner,
        executor=executor,
    )


def main() -> None:
    setup_logging()
    agent = build_agent()

    print("Zero-Agent v0.5")
    print(
        f"Modelo: {settings.ollama_model} | Embeddings: {settings.embedding_model} | "
        f"Ollama: {settings.ollama_base_url}"
    )
    print("Planner + Executor: enabled")
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
        if result.plan_results:
            for step in result.plan_results:
                status = "OK" if step.success else "FAILED"
                print(f"[step {step.step_id}: {step.action} -> {status}]")
            print()
        elif result.tool_used:
            print(f"[ferramenta usada: {result.tool_used}]\n")


if __name__ == "__main__":
    main()
