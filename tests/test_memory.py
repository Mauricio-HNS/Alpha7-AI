import pytest
from pydantic import ValidationError

from app.memory import Experience, SQLiteMemory


@pytest.fixture
def memory() -> SQLiteMemory:
    return SQLiteMemory(db_path=":memory:")


def test_schema_is_created(memory: SQLiteMemory) -> None:
    tables = memory._conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='experiences'").fetchall()
    assert len(tables) == 1
    columns = {row[1] for row in memory._conn.execute("PRAGMA table_info(experiences)")}
    assert {"embedding", "embedding_model"}.issubset(columns)


def test_store_experience_returns_id(memory: SQLiteMemory) -> None:
    exp_id = memory.store_experience(Experience(task="Liste os arquivos do projeto.", tool="filesystem", success=True))
    assert isinstance(exp_id, int)
    assert exp_id > 0


def test_get_experience_roundtrip(memory: SQLiteMemory) -> None:
    exp = Experience(task="Liste os arquivos do projeto.", action="filesystem", tool="filesystem",
                      input={"action": "list", "path": "."}, result="README.md\nmain.py\napp/\ntests/",
                      evaluation="success", success=True, importance=0.7, metadata={"source": "test"})
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
    memory.store_experience(Experience(task="Liste os arquivos do projeto.", result="README.md, main.py", success=True))
    memory.store_experience(Experience(task="Qual a previsão do tempo?", result="Não sei, sem ferramenta de clima.", success=False))
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
    with pytest.raises(ValidationError):
        Experience(result="algo aconteceu", success=True)  # type: ignore[call-arg]


def test_success_defaults_to_none_when_not_evaluated(memory: SQLiteMemory) -> None:
    exp_id = memory.store_experience(Experience(task="Tarefa ainda não avaliada"))
    loaded = memory.get_experience(exp_id)
    assert loaded is not None
    assert loaded.success is None


def test_each_memory_instance_has_isolated_in_memory_db() -> None:
    mem_a = SQLiteMemory(db_path=":memory:")
    mem_b = SQLiteMemory(db_path=":memory:")
    mem_a.store_experience(Experience(task="Só existe em A", success=True))
    assert mem_a.search_experiences("existe") != []
    assert mem_b.search_experiences("existe") == []


class FakeEmbedder:
    model = "fake-bge-m3"

    def __init__(self, vectors: dict[str, list[float]]) -> None:
        self.vectors = vectors
        self.calls: list[str] = []

    def embed(self, text: str) -> list[float]:
        self.calls.append(text)
        return self.vectors[text]


def test_semantic_search_uses_embeddings_and_cosine_similarity() -> None:
    vectors = {
        "Python web backend": [1.0, 0.0],
        "Java backend": [0.8, 0.2],
        "receita de bolo": [0.0, 1.0],
        "desenvolvimento API web": [0.95, 0.05],
    }
    embedder = FakeEmbedder(vectors)
    memory = SQLiteMemory(db_path=":memory:", embedder=embedder)
    memory.store_experience(Experience(task="Python web backend"))
    memory.store_experience(Experience(task="Java backend"))
    memory.store_experience(Experience(task="receita de bolo"))
    results = memory.search_experiences("desenvolvimento API web")
    assert [result.task for result in results] == ["Python web backend", "Java backend", "receita de bolo"]
    assert len(embedder.calls) == 4


def test_semantic_search_falls_back_to_keyword_when_embedding_fails() -> None:
    class BrokenEmbedder:
        model = "bge-m3"
        def embed(self, text: str) -> list[float]:
            raise RuntimeError("Ollama indisponível")
    memory = SQLiteMemory(db_path=":memory:", embedder=BrokenEmbedder())
    memory.store_experience(Experience(task="arquivos do projeto", success=True))
    results = memory.search_experiences("arquivos")
    assert len(results) == 1
    assert results[0].task == "arquivos do projeto"


def test_semantic_search_falls_back_when_database_has_only_legacy_rows() -> None:
    class UnusedEmbedder:
        model = "bge-m3"
        def embed(self, text: str) -> list[float]:
            return [1.0, 0.0]
    memory = SQLiteMemory(db_path=":memory:")
    memory.store_experience(Experience(task="arquivos antigos do projeto"))
    memory.embedder = UnusedEmbedder()
    results = memory.search_experiences("arquivos")
    assert len(results) == 1
    assert results[0].task == "arquivos antigos do projeto"


def test_semantic_embedding_is_persisted() -> None:
    embedder = FakeEmbedder({"tarefa semântica": [0.6, 0.8]})
    memory = SQLiteMemory(db_path=":memory:", embedder=embedder)
    exp_id = memory.store_experience(Experience(task="tarefa semântica"))
    row = memory._conn.execute("SELECT embedding, embedding_model FROM experiences WHERE id = ?", (exp_id,)).fetchone()
    assert row is not None
    assert row["embedding_model"] == "fake-bge-m3"
    assert row["embedding"] == "[0.6, 0.8]"
