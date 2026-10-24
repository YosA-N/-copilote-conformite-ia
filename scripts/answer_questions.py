"""Ask the copilot every test question and write the raw answers to eval/answers_v0.md.

The answers are written as they come, without any change, so that a person can review them.
The same pipeline as scripts/ask.py is used. Run scripts/build_index.py first.

Usage, from the repository root:
    .venv\\Scripts\\python scripts\\answer_questions.py
"""

import json
import sys
import urllib.request
from datetime import datetime

from compliance_copilot.config import EVAL_DIR, INDEX_DIR, load_settings
from compliance_copilot.embeddings import EmbeddingError, make_embedder
from compliance_copilot.evaluation import describe_reference, first_hit_rank, load_questions
from compliance_copilot.index import IndexNotReadyError
from compliance_copilot.llm import LLMError, make_chat_model
from compliance_copilot.rag import RagAnswer, answer_question, render_footer
from compliance_copilot.sources import SOURCES

QUESTION_FILES = ["questions_v0.jsonl", "questions_offtopic_v0.jsonl"]
OUTPUT = EVAL_DIR / "answers_v0.md"


def ollama_version(base_url: str) -> str:
    try:
        with urllib.request.urlopen(f"{base_url}/api/version", timeout=5) as response:
            return json.load(response)["version"]
    except (OSError, ValueError, KeyError):
        return "inconnue"


def quoted(text: str) -> str:
    """The answer as a Markdown quote, line by line, without any other change."""
    return "\n".join(f"> {line}" if line else ">" for line in text.splitlines())


def section(question, answer: RagAnswer) -> list[str]:
    generation = answer.generation
    passage_ids = [passage.id for passage in answer.passages]
    if question.expected:
        rank = first_hit_rank(passage_ids, question.expected)
        expected = " ou ".join(describe_reference(ref) for ref in question.expected)
        found = f"passage [{rank}]" if rank else "absent des passages donnés au modèle"
        expectation = f"Article attendu : {expected} — {found}."
    else:
        expectation = "Question hors sujet : aucun article attendu, la réponse devrait dire que les passages ne suffisent pas."
    return [
        f"## {question.id} — {question.question}",
        "",
        expectation,
        "",
        "### Réponse du copilote",
        "",
        quoted(answer.text),
        "",
        "### Sources, contrôles et avertissement (ajoutés par le code)",
        "",
        "```text",
        render_footer(answer),
        "```",
        "",
        f"Temps : recherche {answer.search_seconds:.1f} s · génération {answer.generation_seconds:.1f} s "
        f"({generation.prompt_tokens} tokens lus, {generation.completion_tokens} écrits, {generation.tokens_per_second:.1f} tokens/s)",
        "",
    ]


def main() -> int:
    settings = load_settings()
    embedder = make_embedder(settings, settings.query_embedding_device)
    chat_model = make_chat_model(settings)
    questions = [question for name in QUESTION_FILES for question in load_questions(EVAL_DIR / name)]

    sections, summary = [], []
    for question in questions:
        print(f"{question.id} : {question.question}", flush=True)
        try:
            answer = answer_question(question.question, INDEX_DIR, embedder, chat_model)
        except (IndexNotReadyError, EmbeddingError, LLMError) as error:
            print(f"[ERREUR] {error}")
            return 1
        sections += section(question, answer)
        alerts = "; ".join(answer.warnings) if answer.warnings else "—"
        cited = ", ".join(f"[{number}]" for number in answer.citations.cited) or "aucune"
        summary.append(
            f"| {question.id} | {question.question} | {cited} | {alerts} | "
            f"{answer.search_seconds + answer.generation_seconds:.0f} s |"
        )
        print(f"     {answer.search_seconds + answer.generation_seconds:.0f} s, citations {cited}", flush=True)

    versions = ", ".join(f"{source.name} du {source.version_date}" for source in SOURCES)
    gpu = "toutes" if settings.llm_num_gpu and settings.llm_num_gpu >= 99 else settings.llm_num_gpu or "choix d'Ollama"
    header = [
        "# Réponses du copilote — v0",
        "",
        f"Générées le {datetime.now():%d/%m/%Y à %H:%M} par `scripts/answer_questions.py`, **sans aucune retouche**, pour relecture.",
        "",
        f"- Génération : `{settings.llm_model}` via Ollama {ollama_version(settings.ollama_base_url)} — température "
        f"{settings.llm_temperature}, contexte {settings.llm_num_ctx} tokens, couches sur la carte graphique : {gpu}, "
        f"{settings.llm_max_tokens} tokens au plus par réponse",
        f"- Recherche : `{settings.embedding_model}` (sur {settings.query_embedding_device.upper()}), 5 passages par question",
        f"- Corpus : versions consolidées {versions}",
        "- Questions : `eval/questions_v0.jsonl` (10) et `eval/questions_offtopic_v0.jsonl` (2, hors sujet)",
        "",
        "| # | Question | Citations | Alertes du code | Temps total |",
        "|---|---|---|---|---|",
        *summary,
        "",
    ]
    OUTPUT.write_text("\n".join(header + sections), encoding="utf-8")
    print(f"\n[OK] {len(questions)} réponses écrites dans eval\\answers_v0.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
