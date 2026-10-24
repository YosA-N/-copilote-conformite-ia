"""Show the passages of the corpus closest to a question (no answer is generated yet).

Run scripts/build_index.py first.

Usage, from the repository root:
    .venv\\Scripts\\python scripts\\search.py "Dois-je désigner un DPO ?" [-k 5]
"""

import argparse
import sys

from compliance_copilot.config import INDEX_DIR, load_settings
from compliance_copilot.embeddings import EmbeddingError, make_embedder
from compliance_copilot.index import IndexNotReadyError, SearchResult, search

EXCERPT_CHARS = 160


def describe(result: SearchResult) -> str:
    """'RGPD, article 37 : Désignation du délégué…' or 'AI Act, annexe III, point 4 : …'."""
    meta = result.metadata
    kind = "article" if meta["unit_type"] == "article" else "annexe"
    part = f", {meta['part']}" if meta.get("part") else ""
    return f"{meta['regulation']}, {kind} {meta['number']}{part} : {meta['title']}"


def excerpt(result: SearchResult) -> str:
    """Beginning of the passage, without the header line that every chunk starts with."""
    body = result.text.split("\n\n", 1)[-1].replace("\n", " ")
    return body if len(body) <= EXCERPT_CHARS else body[:EXCERPT_CHARS].rsplit(" ", 1)[0] + " …"


def main() -> int:
    parser = argparse.ArgumentParser(description="Cherche les passages les plus proches d'une question.")
    parser.add_argument("question", nargs="+", help="la question, de préférence entre guillemets")
    parser.add_argument("-k", type=int, default=5, help="nombre de passages à afficher (5 par défaut)")
    args = parser.parse_args()
    question = " ".join(args.question)

    settings = load_settings()
    embedder = make_embedder(settings, settings.query_embedding_device)
    try:
        results = search(question, INDEX_DIR, embedder, k=args.k)
    except (IndexNotReadyError, EmbeddingError) as error:
        print(f"[ERREUR] {error}")
        return 1

    print(f"Question : {question}\n")
    for result in results:
        print(f"{result.rank}. score {result.score:.3f} — {describe(result)}")
        print(f"   {result.metadata['source_url']}")
        print(f"   « {excerpt(result)} »\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
