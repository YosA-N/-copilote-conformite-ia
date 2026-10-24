"""Search index: the chunks and their embeddings, stored in a local Chroma database.

The index folder (data/index/) holds the Chroma files and manifest.json, which records what
the index was built from: the fingerprint (SHA-256) of chunks.jsonl and the embedding model.
An unchanged corpus is therefore never embedded twice.
"""

import hashlib
import json
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings

from compliance_copilot.embeddings import Embedder

COLLECTION_NAME = "chunks"
MANIFEST_NAME = "manifest.json"
BATCH_SIZE = 16  # chunks sent to the embedding model at once


class IndexNotReadyError(RuntimeError):
    """The index is missing or does not match the configuration; the message says what to do."""


@dataclass
class BuildReport:
    status: str  # "built" or "unchanged"
    chunk_count: int
    seconds: float


@dataclass
class SearchResult:
    rank: int
    score: float  # cosine similarity between the question and the chunk: 1 = same meaning
    id: str
    text: str
    metadata: dict


def load_chunks(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_manifest(index_dir: Path) -> dict | None:
    path = index_dir / MANIFEST_NAME
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def _client(index_dir: Path):
    # Chroma sends anonymous usage statistics unless told not to: everything stays local here.
    return chromadb.PersistentClient(path=str(index_dir), settings=ChromaSettings(anonymized_telemetry=False))


def open_collection(index_dir: Path):
    """The Chroma collection of an index that has already been built."""
    return _client(index_dir).get_collection(COLLECTION_NAME, embedding_function=None)


def _metadata(chunk: dict) -> dict:
    """Chunk fields stored next to its vector; Chroma rejects None, so empty fields are left out."""
    return {key: value for key, value in chunk.items() if key not in ("id", "text") and value is not None}


def build_index(
    chunks_path: Path,
    index_dir: Path,
    embedder: Embedder,
    force: bool = False,
    progress: Callable[[int, int], None] | None = None,
) -> BuildReport:
    """Embed every chunk and store it in Chroma, unless the corpus and the model are unchanged."""
    chunks = load_chunks(chunks_path)
    if not chunks:
        raise ValueError(f"{chunks_path} ne contient aucun chunk.")
    fingerprint = {"corpus_sha256": file_sha256(chunks_path), "embedding_model": embedder.model}
    manifest = read_manifest(index_dir)
    if not force and manifest and all(manifest.get(key) == value for key, value in fingerprint.items()):
        return BuildReport("unchanged", manifest["chunk_count"], 0.0)

    start = time.perf_counter()
    index_dir.mkdir(parents=True, exist_ok=True)
    (index_dir / MANIFEST_NAME).unlink(missing_ok=True)  # an interrupted build must not look complete
    client = _client(index_dir)
    if COLLECTION_NAME in {collection.name for collection in client.list_collections()}:
        client.delete_collection(COLLECTION_NAME)  # on Windows, deleting the folder itself fails while it is open
    collection = client.create_collection(
        name=COLLECTION_NAME,
        configuration={"hnsw": {"space": "cosine"}},
        embedding_function=None,  # vectors always come from our embedder, never from a model Chroma would download
    )
    dimension = 0
    for first in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[first : first + BATCH_SIZE]
        vectors = embedder.embed([chunk["text"] for chunk in batch])
        dimension = len(vectors[0])
        collection.add(
            ids=[chunk["id"] for chunk in batch],
            embeddings=vectors,
            documents=[chunk["text"] for chunk in batch],
            metadatas=[_metadata(chunk) for chunk in batch],
        )
        if progress:
            progress(first + len(batch), len(chunks))
    seconds = time.perf_counter() - start

    manifest = {
        **fingerprint,
        "chunk_count": len(chunks),
        "dimension": dimension,
        "built_at": datetime.now().isoformat(timespec="seconds"),
        "build_seconds": round(seconds, 1),
    }
    (index_dir / MANIFEST_NAME).write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return BuildReport("built", len(chunks), seconds)


def search(question: str, index_dir: Path, embedder: Embedder, k: int = 5) -> list[SearchResult]:
    """The k chunks closest to the question, best first."""
    manifest = read_manifest(index_dir)
    if manifest is None:
        raise IndexNotReadyError("L'index n'existe pas encore : lancez d'abord scripts\\build_index.py.")
    if manifest["embedding_model"] != embedder.model:
        raise IndexNotReadyError(
            f"L'index a été construit avec le modèle {manifest['embedding_model']}, mais .env demande "
            f"{embedder.model} : relancez scripts\\build_index.py."
        )
    vector = embedder.embed([question])[0]
    found = open_collection(index_dir).query(query_embeddings=[vector], n_results=k, include=["documents", "metadatas", "distances"])
    rows = zip(found["ids"][0], found["documents"][0], found["metadatas"][0], found["distances"][0])
    return [
        SearchResult(rank=rank, score=1 - distance, id=chunk_id, text=text, metadata=metadata)
        for rank, (chunk_id, text, metadata, distance) in enumerate(rows, start=1)
    ]
