"""Measure how well the search finds the expected articles: rank of the first hit, hit@k.

A reference names an article, an annex or a part of it, like the start of a chunk id:
"gdpr:art_37" (any chunk of GDPR article 37) or "ai_act:anx_III:pt_4" (point 4 of AI Act annex III).
"""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from compliance_copilot.sources import SOURCES

SOURCE_NAMES = {source.key: source.name for source in SOURCES}
LETTER_SUFFIXES = {"a": "bis", "b": "ter", "c": "quater", "d": "quinquies", "e": "sexies"}
PART_NAMES = {"par": "paragraphe", "def": "définition", "pt": "point", "sec": "section", "part": "partie"}


@dataclass
class Question:
    id: str
    question: str
    expected: list[str]  # the search succeeds if one of these is found
    related: list[str] = field(default_factory=list)  # useful, but not enough to answer alone
    coverage: str = "complet"  # "partiel" when the corpus only holds part of the answer
    note: str = ""


def load_questions(path: Path) -> list[Question]:
    return [Question(**json.loads(line)) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def matches(chunk_id: str, reference: str) -> bool:
    """True if the chunk belongs to the referenced article, annex or part ("gdpr:art_3" ≠ "gdpr:art_37")."""
    return chunk_id == reference or chunk_id.startswith(reference + ":")


def first_hit_rank(result_ids: list[str], expected: list[str]) -> int | None:
    """Rank (from 1) of the first result that belongs to an expected reference, or None."""
    for rank, chunk_id in enumerate(result_ids, start=1):
        if any(matches(chunk_id, reference) for reference in expected):
            return rank
    return None


def hit_at_k(ranks: list[int | None], k: int) -> int:
    """Number of questions whose first expected result is among the k first results."""
    return sum(1 for rank in ranks if rank is not None and rank <= k)


def describe_reference(reference: str) -> str:
    """'gdpr:art_37' → 'RGPD art. 37'; 'ai_act:anx_III:pt_4' → 'AI Act annexe III, point 4'."""
    key, anchor, *parts = reference.split(":")
    article = re.fullmatch(r"art_(\d+)([a-z]?)", anchor)
    if article:
        number, letter = article.groups()
        label = f"art. {number}" + (f" {LETTER_SUFFIXES.get(letter, letter)}" if letter else "")
    else:
        label = f"annexe {anchor.removeprefix('anx_')}"
    for part in parts:
        kind, _, value = part.partition("_")
        label += f", {PART_NAMES.get(kind, kind)} {value.replace('-', ' ')}"
    return f"{SOURCE_NAMES.get(key, key)} {label}"
