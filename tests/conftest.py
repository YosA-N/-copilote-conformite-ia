"""Shared test helpers: a fake embedding model and a small corpus, so that tests never need Ollama."""

import hashlib
import json
import math
import re
from pathlib import Path

import pytest

from compliance_copilot.corpus import build_chunks
from compliance_copilot.index import build_index
from compliance_copilot.llm import Generation
from compliance_copilot.sources import SOURCES

FIXTURES = Path(__file__).parent / "fixtures"


class FakeEmbedder:
    """Deterministic embeddings: each word adds 1 to one of DIMENSIONS slots, chosen by its hash.

    Texts that share words get close vectors, which is enough to test the order of the results.
    """

    DIMENSIONS = 256

    def __init__(self, model: str = "fake-embedder"):
        self.model = model
        self.calls = 0  # number of embed() calls, to check that nothing is recomputed

    def embed(self, texts: list[str]) -> list[list[float]]:
        self.calls += 1
        vectors = []
        for text in texts:
            vector = [0.0] * self.DIMENSIONS
            for word in re.findall(r"\w+", text.lower()):
                vector[int(hashlib.sha256(word.encode("utf-8")).hexdigest(), 16) % self.DIMENSIONS] += 1.0
            norm = math.sqrt(sum(value * value for value in vector)) or 1.0
            vectors.append([value / norm for value in vector])
        return vectors


class FakeChatModel:
    """Writes a fixed answer, in pieces of 3 characters, like a streamed model would."""

    def __init__(self, reply: str = "Oui [1].", truncated: bool = False, num_ctx: int = 8192, max_tokens: int = 700):
        self.model = "fake-llm"
        self.reply = reply
        self.truncated = truncated
        self.num_ctx = num_ctx
        self.max_tokens = max_tokens
        self.messages: list[dict] = []  # what the model received, to check the prompt

    def generate(self, messages, on_text=None) -> Generation:
        self.messages = messages
        for start in range(0, len(self.reply), 3):
            if on_text:
                on_text(self.reply[start : start + 3])
        return Generation(self.reply, prompt_tokens=100, completion_tokens=10, seconds=0.5, tokens_per_second=20.0, truncated=self.truncated)


@pytest.fixture
def fake_embedder() -> FakeEmbedder:
    return FakeEmbedder()


@pytest.fixture
def other_model_embedder() -> FakeEmbedder:
    return FakeEmbedder(model="other-model")


@pytest.fixture
def chunks_file(tmp_path) -> Path:
    """chunks.jsonl built from the small EUR-Lex excerpts of tests/fixtures/ (6 chunks)."""
    lines = []
    for source, name in zip(SOURCES, ["gdpr_sample.xhtml", "ai_act_sample.xhtml"]):
        _, chunks = build_chunks(source, (FIXTURES / name).read_text(encoding="utf-8"))
        lines.extend(json.dumps(chunk.to_dict(), ensure_ascii=False) for chunk in chunks)
    path = tmp_path / "chunks.jsonl"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


@pytest.fixture
def index_dir(chunks_file, tmp_path, fake_embedder) -> Path:
    """A temporary Chroma index of the 6 chunks, built with the fake embedding model."""
    path = tmp_path / "index"
    build_index(chunks_file, path, fake_embedder)
    return path
