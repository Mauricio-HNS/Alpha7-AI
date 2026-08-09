import sqlite3

import pytest
from pydantic import ValidationError

from app.memory import Experience, SQLiteMemory


@pytest.fixture
def memory() -> SQLiteMemory:
    return SQLiteMemory(db_path=":memory:")


def test_schema_is_created(memory: SQLiteMemory) -> None:
    tables = memory._conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='experiences'"
    ).fetchall()
    assert len(tables) == 1


def test_store_experience_returns_id(memory: SQLiteMemory) -> None:
    exp = Experience(task="Liste os arquivos do projeto.", tool="filesystem", success=True)
    exp_id = memory.store_experience(exp)
    assert isinstance(exp_id, int)
    assert exp_id > 0


def test_get_experience_roundtrip(memory: SQLiteMemory) -> None:
    exp = Experience(
        task="Liste os arquivos do projeto.",
        action="filesystem",
        tool="filesystem",
        input={"action": "list", "path": "."},
        result="README.md\nmain.py\napp/\ntests/",
        evaluation="success",
        success=True,
        importance=0.7,
        metadata={"source": "test"},
    )
    exp_id = memory.store_experience(exp)

    loaded = memory.get_experience(exp_id)

    assert loaded is not None
    assert loaded.id == exp_id
    assert loaded.task == exp.task
    assert loaded.tool == "filesystem"
    assert loaded.input == {"action": "list", "path": "."}
    assert loaded.result == exp.result
    assert loaded.success is True
    assert loaded.importance == 0.7
    assert loaded.metadata == {"source": "test"}


def test_get_experience_not_found_returns_none(memory: SQLiteMemory) -> None:
    assert memory.get_experience(9999) is None


def test_search_finds_relevant_experience_by_keyword(memory: SQLiteMemory) -> None:
    memory.store_experience(
        Experience(task="Liste os arquivos do projeto.", result="README.md, main.py", success=True)
    )
    memory.store_experience(
        Experience(task="Qual a previsão do tempo?", result="Não sei, sem ferramenta de clima.", success=False)
    )

    results = memory.search_experiences("arquivos do projeto")

    assert len(results) >= 1
    assert "arquivos" in results[0].task.lower()


def test_search_ranks_more_relevant_first(memory: SQLiteMemory) -> None:
    memory.store_experience(Experience(task="Liste os arquivos do projeto.", success=True))
    memory.store_experience(Experience(task="Liste os arquivos e leia o README do projeto.", success=True))

    results = memory.search_experiences("arquivos README projeto")

    assert results[0].task == "Liste os arquivos e leia o README do projeto."


def test_search_on_empty_memory_returns_empty_list(memory: SQLiteMemory) -> None:
    assert memory.search_experiences("qualquer coisa") == []


def test_search_with_empty_query_returns_empty_list(memory: SQLiteMemory) -> None:
    memory.store_experience(Experience(task="Liste os arquivos do projeto.", success=True))
    assert memory.search_experiences("   ") == []


def test_experience_without_task_is_rejected() -> None:
    # task é obrigatório: uma "experiência" sem task não representa nada que
    # realmente aconteceu, então a validação deve barrar isso na criação.
    with pytest.raises(ValidationError):
        Experience(result="algo aconteceu", success=True)  # type: ignore[call-arg]


def test_success_defaults_to_none_when_not_evaluated(memory: SQLiteMemory) -> None:
    exp = Experience(task="Tarefa ainda não avaliada")
    exp_id = memory.store_experience(exp)
    loaded = memory.get_experience(exp_id)
    assert loaded is not None
    assert loaded.success is None


def test_each_memory_instance_has_isolated_in_memory_db() -> None:
    mem_a = SQLiteMemory(db_path=":memory:")
    mem_b = SQLiteMemory(db_path=":memory:")

    mem_a.store_experience(Experience(task="Só existe em A", success=True))

    assert mem_a.search_experiences("existe") != []
    assert mem_b.search_experiences("existe") == []
