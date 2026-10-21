"""Environment checks: Python version and local Ollama server."""

import json
import sys
import urllib.request
from dataclasses import dataclass, field

MIN_PYTHON = (3, 11)


@dataclass(frozen=True)
class PythonCheck:
    ok: bool
    version: str


@dataclass(frozen=True)
class OllamaCheck:
    ok: bool
    version: str | None = None
    models: list[str] = field(default_factory=list)
    error: str | None = None


def check_python_version(version_info: tuple[int, ...] = sys.version_info) -> PythonCheck:
    """Check that the running Python is at least MIN_PYTHON."""
    version = ".".join(str(part) for part in version_info[:3])
    return PythonCheck(ok=tuple(version_info[:2]) >= MIN_PYTHON, version=version)


def _get_json(url: str, timeout: float) -> dict:
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return json.load(response)


def check_ollama(base_url: str, timeout: float = 3.0) -> OllamaCheck:
    """Ask the Ollama server for its version and the list of installed models."""
    base_url = base_url.rstrip("/")
    if not base_url.startswith(("http://", "https://")):
        return OllamaCheck(ok=False, error=f"invalid URL: {base_url!r}")
    try:
        version = _get_json(f"{base_url}/api/version", timeout)["version"]
        tags = _get_json(f"{base_url}/api/tags", timeout)
    # OSError covers network failures (URLError, timeouts); ValueError and KeyError cover bad JSON.
    except (OSError, ValueError, KeyError) as exc:
        return OllamaCheck(ok=False, error=str(exc))
    models = [model["name"] for model in tags.get("models", [])]
    return OllamaCheck(ok=True, version=version, models=models)
