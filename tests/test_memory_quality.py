from app.memory import Experience, IEmbedder, SQLiteMemory


class FakeEmbedder:
    model = "test-model"

    def __init__(self, vectors: dict[str, list[float]]) -> None:
        self.vectors = vectors

    def embed(self, text: str) -> list[float]:
        return self.vectors[text]


def test_semantic_search_rejects_weak_matches(monkeypatch) -> None:
    monkeypatch.setattr("app.memory.settings.semantic_min_score", 0.8)
    embedder = FakeEmbedder({
        "strong": [1.0, 0.0],
        "weak": [0.7, 0.7],
        "query": [1.0, 0.0],
    })
    memory = SQLiteMemory(db_path=":memory:", embedder=embedder)

    strong_id = memory.store_experience(Experience(task="strong"))
    memory.store_experience(Experience(task="weak"))

    results = memory.search_experiences("query", limit=5)

    assert [item.id for item in results] == [strong_id]


def test_semantic_search_falls_back_to_keyword_when_no_match(monkeypatch) -> None:
    monkeypatch.setattr("app.memory.settings.semantic_min_score", 0.99)
    embedder = FakeEmbedder({
        "keyword match": [1.0, 0.0],
        "query": [0.0, 1.0],
    })
    memory = SQLiteMemory(db_path=":memory:", embedder=embedder)
    experience_id = memory.store_experience(Experience(task="keyword match"))

    results = memory.search_experiences("keyword", limit=5)

    assert [item.id for item in results] == [experience_id]
