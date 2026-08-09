"""Interactive CLI for Zero-Agent."""
from __future__ import annotations

from app.agent import Agent
from app.llm import OllamaProvider


def main() -> None:
    agent = Agent(llm=OllamaProvider(), tools=[])

    print("Zero-Agent iniciado. Digite 'sair' para encerrar.")

    while True:
        try:
            user_input = input("\nVocê > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando.")
            break

        if not user_input:
            continue
        if user_input.lower() in {"sair", "exit", "quit"}:
            print("Encerrando.")
            break

        try:
            result = agent.run(user_input)
            print(f"Zero-Agent > {result.response}")
        except Exception as exc:
            print(f"Zero-Agent [ERRO] > {exc}")


if __name__ == "__main__":
    main()
