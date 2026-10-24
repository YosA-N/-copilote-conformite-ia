"""Offline tests for the Ollama embedder: the HTTP calls never leave the test."""

import io
import json
import urllib.error

import pytest

from compliance_copilot import embeddings
from compliance_copilot.embeddings import EmbeddingError, OllamaEmbedder

BASE_URL = "http://localhost:11434"


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close()


@pytest.fixture
def sent_bodies(monkeypatch) -> list[dict]:
    """Record the request bodies; answer with one vector per text, whose first value is the text length."""
    bodies = []

    def fake_urlopen(request, timeout):
        body = json.loads(request.data)
        bodies.append(body)
        vectors = [[float(len(text)), 1.0] for text in body["input"]]
        return FakeResponse(json.dumps({"embeddings": vectors}).encode("utf-8"))

    monkeypatch.setattr(embeddings.urllib.request, "urlopen", fake_urlopen)
    return bodies


def test_texts_are_sent_in_batches_and_come_back_in_order(sent_bodies):
    embedder = OllamaEmbedder(BASE_URL, "bge-m3", batch_size=2)

    vectors = embedder.embed(["a", "bb", "ccc", "dddd", "eeeee"])

    assert [len(body["input"]) for body in sent_bodies] == [2, 2, 1]
    assert [vector[0] for vector in vectors] == [1, 2, 3, 4, 5]
    for body in sent_bodies:
        assert body["model"] == "bge-m3"
        assert body["truncate"] is False  # a text that is too long must fail, not be cut silently


def test_cpu_device_keeps_the_model_off_the_graphics_card(sent_bodies):
    OllamaEmbedder(BASE_URL, "bge-m3", device="cpu").embed(["question"])
    OllamaEmbedder(BASE_URL, "bge-m3", device="gpu").embed(["question"])

    assert sent_bodies[0]["options"] == {"num_gpu": 0}
    assert "options" not in sent_bodies[1]


def test_unknown_device_is_rejected():
    with pytest.raises(ValueError):
        OllamaEmbedder(BASE_URL, "bge-m3", device="tpu")


def test_unreachable_ollama_gives_a_clear_error(monkeypatch):
    def refuse(request, timeout):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr(embeddings.urllib.request, "urlopen", refuse)

    with pytest.raises(EmbeddingError, match="Ollama ne répond pas"):
        OllamaEmbedder(BASE_URL, "bge-m3").embed(["question"])


def test_missing_model_suggests_pulling_it(monkeypatch):
    def not_found(request, timeout):
        body = io.BytesIO(b'{"error":"model \\"bge-m3\\" not found, try pulling it first"}')
        raise urllib.error.HTTPError(request.full_url, 404, "Not Found", {}, body)

    monkeypatch.setattr(embeddings.urllib.request, "urlopen", not_found)

    with pytest.raises(EmbeddingError, match="ollama pull bge-m3"):
        OllamaEmbedder(BASE_URL, "bge-m3").embed(["question"])
