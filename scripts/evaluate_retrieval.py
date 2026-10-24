"""Measure the search on the test questions: hit@1, hit@5 and, for each question, the rank of
the first expected article.

The rank is looked for among the DEPTH first passages; further away, the article counts as
« non trouvé ». Run scripts/build_index.py first.

Usage, from the repository root:
    .venv\\Scripts\\python scripts\\evaluate_retrieval.py [--questions eval\\questions_v0.jsonl]
"""

import argparse
import sys
from pathlib import Path

from compliance_copilot.config import EVAL_DIR, INDEX_DIR, PROCESSED_DIR, load_settings
from compliance_copilot.embeddings import EmbeddingError, make_embedder
from compliance_copilot.evaluation import describe_reference, first_hit_rank, hit_at_k, load_questions, matches
from compliance_copilot.index import IndexNotReadyError, SearchResult, load_chunks, search

DEPTH = 20
SHOWN_WHEN_MISSED = 3


def describe_result(result: SearchResult) -> str:
    """'RGPD art. 12, paragraphe 3' or 'AI Act annexe III, point 4'."""
    meta = result.metadata
    kind = "art." if meta["unit_type"] == "article" else "annexe"
    part = f", {meta['part']}" if meta.get("part") else ""
    return f"{meta['regulation']} {kind} {meta['number']}{part}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Mesure hit@1 et hit@5 sur les questions de test.")
    parser.add_argument("--questions", type=Path, default=EVAL_DIR / "questions_v0.jsonl")
    args = parser.parse_args()
    questions = load_questions(args.questions)

    # every expected article must exist in the corpus, otherwise the measure means nothing
    chunk_ids = [chunk["id"] for chunk in load_chunks(PROCESSED_DIR / "chunks.jsonl")]
    unknown = sorted({ref for q in questions for ref in q.expected + q.related if not any(matches(i, ref) for i in chunk_ids)})
    if unknown:
        print(f"[ERREUR] Références absentes du corpus : {', '.join(unknown)}")
        return 1

    settings = load_settings()
    embedder = make_embedder(settings, settings.query_embedding_device)
    ranks: list[int | None] = []
    print(f"{len(questions)} questions, rang cherché parmi les {DEPTH} premiers passages\n")
    for question in questions:
        try:
            results = search(question.question, INDEX_DIR, embedder, k=DEPTH)
        except (IndexNotReadyError, EmbeddingError) as error:
            print(f"[ERREUR] {error}")
            return 1
        rank = first_hit_rank([result.id for result in results], question.expected)
        ranks.append(rank)
        status = f"rang {rank}" if rank else "non trouvé"
        partial = "  (réponse seulement partielle dans le corpus)" if question.coverage == "partiel" else ""
        print(f"{question.id}  {status:<11} {question.question}{partial}")
        print(f"     attendu : {' ou '.join(describe_reference(ref) for ref in question.expected)}")
        if rank is None or rank > 5:
            found = " · ".join(
                f"{result.rank}. {describe_result(result)} ({result.score:.3f})" for result in results[:SHOWN_WHEN_MISSED]
            )
            print(f"     trouvés : {found}")

    total = len(questions)
    print(f"\nhit@1 : {hit_at_k(ranks, 1)}/{total}   (l'article attendu arrive en premier)")
    print(f"hit@5 : {hit_at_k(ranks, 5)}/{total}   (l'article attendu est dans les 5 premiers passages)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
