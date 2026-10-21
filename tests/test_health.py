"""Offline tests for the environment checks: they never contact a real Ollama server."""

import urllib.error

from compliance_copilot import health


def test_current_python_is_supported():
    assert health.check_python_version().ok


def test_old_python_is_rejected():
    result = health.check_python_version((3, 10, 0))

    assert not result.ok
    assert result.version == "3.10.0"


def test_ollama_reachable(monkeypatch):
    fake_responses = {
        "http://localhost:11434/api/version": {"version": "0.40.7"},
        "http://localhost:11434/api/tags": {"models": [{"name": "bge-m3:latest"}]},
    }
    monkeypatch.setattr(health, "_get_json", lambda url, timeout: fake_responses[url])

    result = health.check_ollama("http://localhost:11434/")

    assert result.ok
    assert result.version == "0.40.7"
    assert result.models == ["bge-m3:latest"]


def test_ollama_unreachable(monkeypatch):
    def refuse_connection(url, timeout):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr(health, "_get_json", refuse_connection)

    result = health.check_ollama("http://localhost:11434")

    assert not result.ok
    assert "connection refused" in result.error
