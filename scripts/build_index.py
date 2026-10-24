"""Embed the chunks of data/processed/chunks.jsonl and store them in the Chroma index (data/index/).

Nothing is recomputed when chunks.jsonl and the embedding model have not changed.
Run scripts/build_corpus.py first.

Usage, from the repository root:
    .venv\\Scripts\\python scripts\\build_index.py [--force]
"""

import argparse
import sys

from compliance_copilot.config import INDEX_DIR, PROCESSED_DIR, load_settings
from compliance_copilot.embeddings import EmbeddingError, make_embedder
from compliance_copilot.index import build_index


def show_progress(done: int, total: int) -> None:
    if done == total or done % 160 == 0:
        print(f"  {done}/{total} chunks…", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Construit l'index de recherche (embeddings + Chroma).")
    parser.add_argument("--force", action="store_true", help="reconstruire même si rien n'a changé")
    args = parser.parse_args()

    chunks_path = PROCESSED_DIR / "chunks.jsonl"
    if not chunks_path.exists():
        print("[ERREUR] data/processed/chunks.jsonl est absent : lancez d'abord scripts\\build_corpus.py.")
        return 1
    settings = load_settings()
    embedder = make_embedder(settings, settings.index_embedding_device)
    print(f"Modèle d'embeddings : {embedder.model} (sur {embedder.device.upper()})")

    try:
        report = build_index(chunks_path, INDEX_DIR, embedder, force=args.force, progress=show_progress)
    except EmbeddingError as error:
        print(f"[ERREUR] {error}")
        return 1

    if report.status == "unchanged":
        print(f"[OK] Index déjà à jour ({report.chunk_count} chunks) : corpus et modèle inchangés, rien à recalculer.")
    else:
        minutes, seconds = divmod(round(report.seconds), 60)
        print(f"[OK] {report.chunk_count} chunks indexés en {minutes} min {seconds:02d} s dans data\\index\\")
    return 0


if __name__ == "__main__":
    sys.exit(main())
