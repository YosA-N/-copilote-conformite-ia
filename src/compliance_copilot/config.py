"""Application settings, read from environment variables and the local .env file."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_LLM_MODEL = "ministral-3:3b"
DEFAULT_EMBEDDING_MODEL = "bge-m3"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


@dataclass(frozen=True)
class Settings:
    ollama_base_url: str
    llm_model: str
    embedding_model: str


def load_settings() -> Settings:
    """Load settings from .env (if present), falling back to the defaults above."""
    load_dotenv()
    return Settings(
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL).rstrip("/"),
        llm_model=os.getenv("LLM_MODEL", DEFAULT_LLM_MODEL),
        embedding_model=os.getenv("EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL),
    )
