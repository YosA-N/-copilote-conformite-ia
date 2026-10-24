"""Generate text with a language model (LLM), behind one small interface.

The model and its settings are chosen in .env (LLM_MODEL, LLM_NUM_CTX, LLM_NUM_GPU...).
OllamaChatModel is the only implementation for now; another backend only needs the
attributes and the generate() method of ChatModel.
"""

import json
import re
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from compliance_copilot.config import Settings

OUT_OF_MEMORY = re.compile(r"out of memory|unable to allocate|cudamalloc|more system memory", re.IGNORECASE)


@dataclass
class Generation:
    text: str
    prompt_tokens: int
    completion_tokens: int
    seconds: float  # whole call, model loading included
    tokens_per_second: float  # writing speed of the answer
    truncated: bool  # stopped by the max_tokens limit, so the end of the answer is missing


class ChatModel(Protocol):
    model: str
    num_ctx: int  # context size in tokens: prompt + answer must fit in it
    max_tokens: int

    def generate(self, messages: list[dict], on_text: Callable[[str], None] | None = None) -> Generation:
        """Answer the conversation; on_text receives each piece of text as soon as it is written."""
        ...


class LLMError(RuntimeError):
    """A generation request failed; the message can be shown to the user as is."""


class OllamaChatModel:
    """Chat with a model served by the local Ollama server (POST /api/chat, streamed)."""

    def __init__(
        self,
        base_url: str,
        model: str,
        num_ctx: int = 8192,
        num_gpu: int | None = None,
        temperature: float = 0.1,
        max_tokens: int = 700,
        timeout: float = 900,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.num_ctx = num_ctx
        self.num_gpu = num_gpu
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout

    def _request_body(self, messages: list[dict]) -> dict:
        options = {"temperature": self.temperature, "num_ctx": self.num_ctx, "num_predict": self.max_tokens}
        if self.num_gpu is not None:
            options["num_gpu"] = self.num_gpu
        return {"model": self.model, "messages": messages, "stream": True, "options": options}

    def _explain(self, detail: str) -> str:
        """Turn an Ollama error into a message that says what to do."""
        if "not found" in detail:
            return f"Le modèle {self.model} n'est pas installé dans Ollama ({detail}). Lancez « ollama pull {self.model} »."
        if OUT_OF_MEMORY.search(detail):
            if self.num_gpu is None:
                gpu = "choix d'Ollama"
            else:
                gpu = "toutes" if self.num_gpu >= 99 else str(self.num_gpu)
            return (
                f"Mémoire insuffisante pour le modèle {self.model} (contexte de {self.num_ctx} tokens, couches sur la "
                f"carte graphique : {gpu}). Dans le fichier .env, baissez LLM_NUM_CTX (par exemple 6144 ou 4096) ou "
                "LLM_NUM_GPU (par exemple 20), ou laissez LLM_NUM_GPU vide pour laisser Ollama choisir (plus lent), "
                f"puis relancez. Détail d'Ollama : {detail}"
            )
        return f"Ollama a renvoyé une erreur : {detail}"

    def generate(self, messages: list[dict], on_text: Callable[[str], None] | None = None) -> Generation:
        request = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(self._request_body(messages)).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        pieces: list[str] = []
        final: dict = {}
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                for line in response:  # one JSON object per line while the answer is written
                    if not line.strip():
                        continue
                    data = json.loads(line)
                    if "error" in data:
                        raise LLMError(self._explain(data["error"]))
                    piece = data.get("message", {}).get("content", "")
                    if piece:
                        pieces.append(piece)
                        if on_text:
                            on_text(piece)
                    if data.get("done"):
                        final = data
        except urllib.error.HTTPError as error:
            body = error.read().decode("utf-8", errors="replace")
            try:
                detail = json.loads(body).get("error", body)
            except ValueError:
                detail = body
            raise LLMError(self._explain(f"HTTP {error.code} : {detail}")) from error
        except (urllib.error.URLError, TimeoutError) as error:
            raise LLMError(f"Ollama ne répond pas sur {self.base_url} ({error}). Lancez l'application Ollama.") from error

        completion_tokens = final.get("eval_count", 0)
        writing_seconds = final.get("eval_duration", 0) / 1e9
        return Generation(
            text="".join(pieces),
            prompt_tokens=final.get("prompt_eval_count", 0),
            completion_tokens=completion_tokens,
            seconds=final.get("total_duration", 0) / 1e9,
            tokens_per_second=completion_tokens / writing_seconds if writing_seconds else 0.0,
            truncated=final.get("done_reason") == "length",
        )


def make_chat_model(settings: Settings) -> OllamaChatModel:
    """The language model configured in .env."""
    return OllamaChatModel(
        settings.ollama_base_url,
        settings.llm_model,
        num_ctx=settings.llm_num_ctx,
        num_gpu=settings.llm_num_gpu,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens,
    )
