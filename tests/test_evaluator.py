from app.evaluator import SimpleEvaluator


def test_direct_response_is_success_with_moderate_importance() -> None:
    evaluator = SimpleEvaluator()
    result = evaluator.evaluate(task="oi", tool_used=None, tool_output=None, response="Olá!")

    assert result.success is True
    assert result.importance == 0.4
    assert "sem uso de ferramenta" in result.evaluation.lower()


def test_successful_tool_use_is_high_importance() -> None:
    evaluator = SimpleEvaluator()
    result = evaluator.evaluate(
        task="Liste os arquivos do projeto.",
        tool_used="filesystem",
        tool_output="README.md\nmain.py",
        response="Os arquivos são README.md e main.py.",
    )

    assert result.success is True
    assert result.importance == 0.7
    assert "filesystem" in result.evaluation


def test_failed_tool_use_is_low_importance() -> None:
    evaluator = SimpleEvaluator()
    result = evaluator.evaluate(
        task="Liste os arquivos do projeto.",
        tool_used="filesystem",
        tool_output="Erro ao executar a ferramenta 'filesystem': disco indisponível",
        response="Houve um erro.",
    )

    assert result.success is False
    assert result.importance == 0.3
    assert "Falha" in result.evaluation
