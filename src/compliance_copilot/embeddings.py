"""Turn texts into vectors (embeddings), behind one small interface.

The model is chosen in .env (EMBEDDING_MODEL). OllamaEmbedder is the only implementation for
now; another backend only needs a `model` name and an `embed()` method (see Embedder).
"""

import json
import urllib.error
import urllib.request
from typing import Protocol

from compliance_copilot.config import Settings

DEVICES = ("gpu", "cpu")


class Embedder(Protocol):
    model: str

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one vector per text, in the same order."""
        ...


class EmbeddingError(RuntimeError):
    """An embedding request failed; the message can be shown to the user as is."""


class OllamaEmbedder:
    """Embeddings computed by the local Ollama server (POST /api/embed), sent in batches."""

    def __init__(self, base_url: str, model: str, device: str = "gpu", batch_size: int = 16, timeout: float = 600):
        if device not in DEVICES:
            raise ValueError(f"device doit valoir {' ou '.join(DEVICES)}, pas {device!r}")
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.device = device
        self.batch_size = batch_size
        self.timeout = timeout

    def _request_body(self, texts: list[str]) -> dict:
        body = {"model": self.model, "input": texts, "truncate": False}  # fail rather than cut a long text
        if self.device == "cpu":
            body["options"] = {"num_gpu": 0}  # no layer on the graphics card
        return body

    def _post(self, texts: list[str]) -> list[list[float]]:
        request = urllib.request.Request(
            f"{self.base_url}/api/embed",
            data=json.dumps(self._request_body(texts)).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                vectors = json.load(response)["embeddings"]
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            hint = f" Avez-vous lancé « ollama pull {self.model} » ?" if "not found" in detail else ""
            raise EmbeddingError(f"Ollama a refusé la demande (HTTP {error.code}) : {detail}.{hint}") from error
        except (urllib.error.URLError, TimeoutError) as error:
            raise EmbeddingError(f"Ollama ne répond pas sur {self.base_url} ({error}). Lancez l'application Ollama.") from error
        if len(vectors) != len(texts):
            raise EmbeddingError(f"Ollama a renvoyé {len(vectors)} vecteurs pour {len(texts)} textes.")
        return vectors

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = []
        for start in range(0, len(texts), self.batch_size):
            vectors.extend(self._post(texts[start : start + self.batch_size]))
        return vectors


def make_embedder(settings: Settings, device: str) -> OllamaEmbedder:
    """The embedder configured in .env; device is "gpu" or "cpu"."""
    return OllamaEmbedder(settings.ollama_base_url, settings.embedding_model, device)
