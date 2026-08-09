

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
    assert [result.task for result in results] == ["Python web backend", "Java backend"]
    assert len(embedder.calls) == 4


def test_semantic_search_falls_back_to_keyword_when_embedding_fails() -> None:
    class BrokenEmbedder:
        model = "bge-m3"
        def embed(self, text: str) -> list[float]:
            raise RuntimeError("Ollama indisponível")
    memory = SQLiteMemory(db_path=":memory:", embedder=BrokenEmbedder())
    memory.store_experience(Experience(task="arquivos do projeto", success=True))