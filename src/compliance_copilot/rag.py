"""Answer a question from the passages of the corpus (RAG: Retrieval-Augmented Generation).

The language model only writes the answer. The code numbers the passages, checks the
citations written by the model, builds the list of sources from the metadata and adds the
warning: none of these depend on what the model writes.
"""

import re
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from compliance_copilot.embeddings import Embedder
from compliance_copilot.index import SearchResult, search
from compliance_copilot.llm import ChatModel, Generation

SYSTEM_PROMPT = """Tu es le copilote de conformité : tu aides les PME et les associations à comprendre le RGPD et l'AI Act.

Règles à respecter :
1. Réponds UNIQUEMENT à partir des passages fournis, numérotés [1], [2]… N'utilise aucune autre connaissance.
2. Après chaque affirmation, cite entre crochets le numéro du passage qui la justifie, sous la forme [1] ou [2].
3. Si les passages ne suffisent pas pour répondre, dis-le clairement au lieu d'inventer.
4. N'invente jamais de numéro d'article, de date ni de délai : reprends uniquement ceux qui figurent dans les passages.
5. Écris en français simple, pour une personne qui n'est pas juriste (dirigeant de PME, bénévole d'association), et vouvoie-la.
6. Sois bref : commence par la réponse directe en une ou deux phrases, puis donne l'explication.
7. Ne donne aucun conseil qui ne figure pas dans les passages."""

DISCLAIMER = (
    "Information, pas un conseil juridique : vérifiez les textes officiels cités et, en cas de doute, "
    "demandez l'avis d'un professionnel ou de la CNIL."
)

CHARS_PER_TOKEN = 3  # cautious estimate for French text, to check that the prompt fits in the context
SAFETY_TOKENS = 200
CITATION = re.compile(r"\[([^\[\]\n]{1,30})\]")
CITED_ITEM = re.compile(r"^\s*(\d+)\s*[a-z]?\s*$", re.IGNORECASE)  # "1", "1b" (point b of passage 1)


@dataclass
class CitationCheck:
    cited: list[int]  # passages cited in the answer
    unknown: list[int]  # cited numbers that match no passage, e.g. [9] when 5 passages were given


@dataclass
class Source:
    number: int  # the passage number used in the answer: [1], [2]...
    label: str
    url: str
    version_date: str
    cited: bool


@dataclass
class RagAnswer:
    question: str
    text: str
    passages: list[SearchResult]
    sources: list[Source]
    citations: CitationCheck
    warnings: list[str]
    generation: Generation
    search_seconds: float
    generation_seconds: float


# ---------------------------------------------------------------- citations


def _cited_numbers(content: str) -> list[int] | None:
    """[1], [1, 3], [1b] or [1 et 2] → their numbers; None for other brackets such as [sic]."""
    numbers: list[int] = []
    for item in re.split(r"[,;]| et ", content):
        match = CITED_ITEM.match(item)
        if not match:
            return None
        if int(match.group(1)) not in numbers:
            numbers.append(int(match.group(1)))
    return numbers


def normalize_citations(text: str) -> str:
    """Write every citation as [n]: '[1b]' becomes '[1]', '[2, 3c]' becomes '[2, 3]'."""

    def rewrite(match: re.Match) -> str:
        numbers = _cited_numbers(match.group(1))
        return match.group(0) if numbers is None else "[" + ", ".join(map(str, numbers)) + "]"

    return CITATION.sub(rewrite, text)


class CitationStream:
    """Pass streamed text on to `write`, holding back a '[' until its ']' arrives, so that
    citations are already normalised when they are displayed."""

    MAX_PENDING = 32  # a '[' not closed after this many characters is not a citation

    def __init__(self, write: Callable[[str], None]):
        self.write = write
        self.pending = ""

    def feed(self, piece: str) -> None:
        self.pending += piece
        ready = ""
        while self.pending:
            start = self.pending.find("[")
            if start == -1:
                ready, self.pending = ready + self.pending, ""
                break
            ready, self.pending = ready + self.pending[:start], self.pending[start:]
            end = self.pending.find("]")
            if end == -1:
                if len(self.pending) <= self.MAX_PENDING and "\n" not in self.pending:
                    break  # wait for the end of the citation
                ready, self.pending = ready + self.pending[0], self.pending[1:]
            else:
                ready, self.pending = ready + normalize_citations(self.pending[: end + 1]), self.pending[end + 1 :]
        if ready:
            self.write(ready)

    def close(self) -> None:
        if self.pending:
            self.write(normalize_citations(self.pending))
            self.pending = ""


def check_citations(text: str, passage_count: int) -> CitationCheck:
    cited, unknown = set(), set()
    for match in CITATION.finditer(text):
        for number in _cited_numbers(match.group(1)) or []:
            (cited if 1 <= number <= passage_count else unknown).add(number)
    return CitationCheck(cited=sorted(cited), unknown=sorted(unknown))


# ---------------------------------------------------------------- prompt and sources


def passage_label(metadata: dict) -> str:
    """'RGPD — règlement (UE) 2016/679, article 37, paragraphe 2 : Titre'."""
    kind = "article" if metadata["unit_type"] == "article" else "annexe"
    part = f", {metadata['part']}" if metadata.get("part") else ""
    return f"{metadata['regulation']} — {metadata['regulation_ref']}, {kind} {metadata['number']}{part} : {metadata['title']}"


def build_messages(question: str, passages: list[SearchResult]) -> list[dict]:
    """System prompt, then the numbered passages and the question."""
    numbered = "\n\n".join(f"[{number}] {passage.text}" for number, passage in enumerate(passages, start=1))
    user = f"Passages :\n\n{numbered}\n\nQuestion : {question}"
    return [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user}]


def fit_passages(question: str, passages: list[SearchResult], chat_model: ChatModel) -> list[SearchResult]:
    """Drop the lowest-ranked passages until the prompt and the answer fit in the model context."""
    budget = chat_model.num_ctx - chat_model.max_tokens - SAFETY_TOKENS
    kept = list(passages)
    while len(kept) > 1:
        prompt_chars = sum(len(message["content"]) for message in build_messages(question, kept))
        if prompt_chars / CHARS_PER_TOKEN <= budget:
            break
        kept.pop()
    return kept


def build_sources(passages: list[SearchResult], cited: list[int]) -> list[Source]:
    """The sources come from the metadata of the passages, never from the text of the model."""
    return [
        Source(
            number=number,
            label=passage_label(passage.metadata),
            url=passage.metadata["source_url"],
            version_date=passage.metadata["version_date"],
            cited=number in cited,
        )
        for number, passage in enumerate(passages, start=1)
    ]


# ---------------------------------------------------------------- answer


def answer_question(
    question: str,
    index_dir: Path,
    embedder: Embedder,
    chat_model: ChatModel,
    k: int = 5,
    on_text: Callable[[str], None] | None = None,
) -> RagAnswer:
    """Search the closest passages, have the model write the answer, then check it."""
    start = time.perf_counter()
    found = search(question, index_dir, embedder, k=k)
    search_seconds = time.perf_counter() - start

    passages = fit_passages(question, found, chat_model)
    stream = CitationStream(on_text) if on_text else None
    start = time.perf_counter()
    generation = chat_model.generate(build_messages(question, passages), on_text=stream.feed if stream else None)
    generation_seconds = time.perf_counter() - start
    if stream:
        stream.close()

    text = normalize_citations(generation.text)
    citations = check_citations(text, len(passages))
    warnings = []
    if len(passages) < len(found):
        warnings.append(
            f"{len(found) - len(passages)} passage(s) retiré(s) faute de place dans le contexte du modèle "
            f"(LLM_NUM_CTX = {chat_model.num_ctx})."
        )
    if generation.truncated:
        warnings.append(
            f"Réponse coupée : le modèle a atteint la limite de {chat_model.max_tokens} tokens (LLM_MAX_TOKENS), "
            "la fin de la réponse manque. Posez une question plus précise ou augmentez LLM_MAX_TOKENS dans .env."
        )
    if citations.unknown:
        unknown = ", ".join(f"[{number}]" for number in citations.unknown)
        warnings.append(f"Citation vers un passage inexistant : {unknown} (seuls les passages [1] à [{len(passages)}] ont été fournis).")
    if not citations.cited and not citations.unknown:
        warnings.append("La réponse ne cite aucun passage : elle n'est peut-être pas fondée sur les textes. Vérifiez-la avec les sources.")

    return RagAnswer(
        question=question,
        text=text,
        passages=passages,
        sources=build_sources(passages, citations.cited),
        citations=citations,
        warnings=warnings,
        generation=generation,
        search_seconds=search_seconds,
        generation_seconds=generation_seconds,
    )


def render_footer(answer: RagAnswer) -> str:
    """Sources, warnings and the legal warning, added by the code after every answer."""
    lines = ["Sources citées :"]
    cited = [source for source in answer.sources if source.cited]
    if not cited:
        lines.append("  aucune")
    for source in cited:
        lines += [f"  [{source.number}] {source.label} (version du {source.version_date})", f"      {source.url}"]
    others = [source for source in answer.sources if not source.cited]
    if others:
        lines.append("Passages consultés mais non cités :")
        for source in others:
            lines += [f"  [{source.number}] {source.label}", f"      {source.url}"]
    for warning in answer.warnings:
        lines.append(f"Attention : {warning}")
    lines += ["", DISCLAIMER]
    return "\n".join(lines)
