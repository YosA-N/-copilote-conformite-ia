"""Offline tests for the Ollama chat model: the HTTP calls never leave the test."""

import io
import json
import urllib.error

import pytest

from compliance_copilot import llm
from compliance_copilot.config import optional_int
from compliance_copilot.llm import LLMError, OllamaChatModel

BASE_URL = "http://localhost:11434"
MESSAGES = [{"role": "user", "content": "Dois-je désigner un DPO ?"}]


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close()


def streamed(*objects: dict) -> FakeResponse:
    """What Ollama sends while it writes: one JSON object per line."""
    return FakeResponse("".join(json.dumps(item) + "\n" for item in objects).encode("utf-8"))


END = {"done": True, "done_reason": "stop", "prompt_eval_count": 100, "eval_count": 10, "eval_duration": 500_000_000, "total_duration": 2_000_000_000}


@pytest.fixture
def sent_bodies(monkeypatch) -> list[dict]:
    bodies = []

    def fake_urlopen(request, timeout):
        bodies.append(json.loads(request.data))
        return streamed({"message": {"content": "Bon"}, "done": False}, {"message": {"content": "jour [1]"}, "done": False}, END)

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    return bodies


def fail_with(monkeypatch, error: Exception) -> None:
    def fake_urlopen(request, timeout):
        raise error

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)


def http_error(code: int, message: str) -> urllib.error.HTTPError:
    return urllib.error.HTTPError(f"{BASE_URL}/api/chat", code, "error", {}, io.BytesIO(json.dumps({"error": message}).encode()))


def test_streamed_answer_is_assembled_with_its_statistics(sent_bodies):
    pieces = []
    model = OllamaChatModel(BASE_URL, "ministral-3:3b", num_ctx=8192, num_gpu=99, temperature=0.1, max_tokens=700)

    generation = model.generate(MESSAGES, on_text=pieces.append)

    assert pieces == ["Bon", "jour [1]"]
    assert generation.text == "Bonjour [1]"
    assert (generation.prompt_tokens, generation.completion_tokens) == (100, 10)
    assert generation.tokens_per_second == 20.0
    assert generation.truncated is False
    body = sent_bodies[0]
    assert body["stream"] is True
    assert body["options"] == {"temperature": 0.1, "num_ctx": 8192, "num_predict": 700, "num_gpu": 99}


def test_empty_num_gpu_lets_ollama_decide(sent_bodies):
    OllamaChatModel(BASE_URL, "ministral-3:3b", num_gpu=None).generate(MESSAGES)

    assert "num_gpu" not in sent_bodies[0]["options"]
    assert optional_int("") is None and optional_int("20") == 20


def test_answer_stopped_by_the_length_limit_is_marked_as_truncated(monkeypatch):
    monkeypatch.setattr(llm.urllib.request, "urlopen", lambda request, timeout: streamed({**END, "done_reason": "length"}))

    assert OllamaChatModel(BASE_URL, "ministral-3:3b").generate(MESSAGES).truncated is True


def test_unreachable_ollama_gives_a_clear_error(monkeypatch):
    fail_with(monkeypatch, urllib.error.URLError("connection refused"))

    with pytest.raises(LLMError, match="Ollama ne répond pas"):
        OllamaChatModel(BASE_URL, "ministral-3:3b").generate(MESSAGES)


def test_missing_model_suggests_pulling_it(monkeypatch):
    fail_with(monkeypatch, http_error(404, 'model "ministral-3:3b" not found, try pulling it first'))

    with pytest.raises(LLMError, match="ollama pull ministral-3:3b"):
        OllamaChatModel(BASE_URL, "ministral-3:3b").generate(MESSAGES)


def test_out_of_memory_explains_which_settings_to_lower(monkeypatch):
    fail_with(monkeypatch, http_error(500, "llama runner process has terminated: CUDA error: out of memory"))

    with pytest.raises(LLMError) as error:
        OllamaChatModel(BASE_URL, "ministral-3:3b", num_ctx=8192, num_gpu=99).generate(MESSAGES)

    assert "Mémoire insuffisante" in str(error.value)
    assert "LLM_NUM_CTX" in str(error.value) and "LLM_NUM_GPU" in str(error.value)


def test_error_sent_in_the_middle_of_the_stream(monkeypatch):
    monkeypatch.setattr(
        llm.urllib.request,
        "urlopen",
        lambda request, timeout: streamed({"message": {"content": "Oui"}, "done": False}, {"error": "unable to allocate CUDA0 buffer"}),
    )

    with pytest.raises(LLMError, match="LLM_NUM_CTX"):
        OllamaChatModel(BASE_URL, "ministral-3:3b").generate(MESSAGES)
