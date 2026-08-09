from unittest.mock import MagicMock, patch

import pytest

from app.memory import OllamaEmbedder


def _response(body: dict) -> MagicMock:
    response = MagicMock()
    response.json.return_value = body
    response.raise_for_status.return_value = None
    return response


@patch("app.memory.requests.post")
def test_ollama_embedder_parses_embed_response(mock_post: MagicMock) -> None:
    mock_post.return_value = _response({"embeddings": [[0.1, 0.2, 0.3]]})

    embedder = OllamaEmbedder(model="bge-m3:latest", base_url="http://localhost:11434")
    result = embedder.embed("memória semântica")

    assert result == [0.1, 0.2, 0.3]
    mock_post.assert_called_once_with(
        "http://localhost:11434/api/embed",
        json={"model": "bge-m3:latest", "input": "memória semântica"},
        timeout=60,
    )


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"embeddings": []},
        {"embeddings": [None]},
        {"embeddings": [[]]},
        {"embeddings": [["not-a-number"]]},
        {"embeddings": [[float("inf")]]},
    ],
)
@patch("app.memory.requests.post")
def test_ollama_embedder_rejects_invalid_responses(mock_post: MagicMock, body: dict) -> None:
    mock_post.return_value = _response(body)

    with pytest.raises(ValueError):
        OllamaEmbedder().embed("teste")
