from unittest.mock import MagicMock, patch

from app.llm import OllamaProvider


def _mock_response(json_body: dict) -> MagicMock:
    mock_resp = MagicMock()
    mock_resp.json.return_value = json_body
    mock_resp.raise_for_status.return_value = None
    return mock_resp


@patch("app.llm.requests.post")
def test_complete_returns_response_text(mock_post: MagicMock) -> None:
    mock_post.return_value = _mock_response({"response": "olá!"})

    provider = OllamaProvider(model="llama3.2", base_url="http://localhost:11434")
    result = provider.complete(prompt="oi")

    assert result == "olá!"
    mock_post.assert_called_once()
    called_url = mock_post.call_args.args[0]
    assert called_url == "http://localhost:11434/api/generate"


@patch("app.llm.requests.post")
def test_complete_sends_system_prompt(mock_post: MagicMock) -> None:
    mock_post.return_value = _mock_response({"response": "{}"})

    provider = OllamaProvider(model="llama3.2", base_url="http://localhost:11434")
    provider.complete(prompt="oi", system="Responda em JSON")

    payload = mock_post.call_args.kwargs["json"]
    assert payload["system"] == "Responda em JSON"
    assert payload["format"] == "json"


@patch("app.llm.requests.post")
def test_complete_without_system_has_no_format_forced(mock_post: MagicMock) -> None:
    mock_post.return_value = _mock_response({"response": "olá"})

    provider = OllamaProvider(model="llama3.2", base_url="http://localhost:11434")
    provider.complete(prompt="oi")

    payload = mock_post.call_args.kwargs["json"]
    assert "format" not in payload
