"""Offline tests for reading and chunking the legal texts, on small excerpts in tests/fixtures/."""

from pathlib import Path

import pytest

from compliance_copilot.corpus import build_chunks, missing_lines, read_amendments
from compliance_copilot.sources import SOURCES

FIXTURES = Path(__file__).parent / "fixtures"
GDPR, AI_ACT = SOURCES
SMALL_LIMIT = 700  # a small chunk size, so that the short excerpts have to be cut


@pytest.fixture(scope="module")
def gdpr_html() -> str:
    return (FIXTURES / "gdpr_sample.xhtml").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def ai_act_html() -> str:
    return (FIXTURES / "ai_act_sample.xhtml").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def all_small_chunks(gdpr_html, ai_act_html):
    return [
        *build_chunks(GDPR, gdpr_html, max_chars=SMALL_LIMIT)[1],
        *build_chunks(AI_ACT, ai_act_html, max_chars=SMALL_LIMIT)[1],
    ]


def test_article_numbers_and_titles(gdpr_html):
    units, _ = build_chunks(GDPR, gdpr_html)

    assert [unit.number for unit in units] == ["1", "4", "37"]  # "Article premier" becomes "1"
    assert [unit.title for unit in units] == [
        "Objet et objectifs",
        "Définitions",
        "Désignation du délégué à la protection des données",
    ]
    assert units[2].chapter == "Chapitre IV — Responsable du traitement et sous-traitant"
    assert units[2].section == "Section 4 — Délégué à la protection des données"


def test_inserted_article_and_annex(ai_act_html):
    units, _ = build_chunks(AI_ACT, ai_act_html)

    assert [(unit.unit_type, unit.number, unit.anchor) for unit in units] == [
        ("article", "4 bis", "art_4a"),
        ("article", "5", "art_5"),
        ("annex", "III", "anx_III"),
    ]
    assert units[2].title == "Systèmes d'IA à haut risque visés à l'article 6, paragraphe 2"


def test_short_article_is_one_chunk(gdpr_html):
    _, chunks = build_chunks(GDPR, gdpr_html)
    article_37 = [chunk for chunk in chunks if chunk.number == "37"]

    assert len(article_37) == 1
    assert article_37[0].id == "gdpr:art_37"
    assert article_37[0].part is None
    assert article_37[0].text.startswith(
        "RGPD — règlement (UE) 2016/679 — Article 37 : Désignation du délégué à la protection des données\n\n1. "
    )


def test_definitions_are_cut_one_by_one(gdpr_html):
    _, chunks = build_chunks(GDPR, gdpr_html, max_chars=SMALL_LIMIT)
    article_4 = [chunk for chunk in chunks if chunk.number == "4"]

    assert [chunk.part for chunk in article_4] == ["définition 1", "définition 2", "définition 3"]
    assert [chunk.id for chunk in article_4] == ["gdpr:art_4:def_1", "gdpr:art_4:def_2", "gdpr:art_4:def_3"]
    assert "«traitement»" in article_4[1].text
    for chunk in article_4:
        assert chunk.text.startswith("RGPD — règlement (UE) 2016/679 — Article 4 : Définitions\n")


def test_long_article_is_cut_by_paragraph_and_keeps_its_origin(gdpr_html):
    _, chunks = build_chunks(GDPR, gdpr_html, max_chars=SMALL_LIMIT)
    article_37 = [chunk for chunk in chunks if chunk.source_url.endswith("#art_37")]

    assert len(article_37) > 1
    assert "paragraphe 2" in [chunk.part for chunk in article_37]
    for chunk in article_37:
        assert chunk.number == "37"
        assert chunk.title == "Désignation du délégué à la protection des données"
        assert chunk.text.startswith("RGPD — règlement (UE) 2016/679 — Article 37 : ")
        assert chunk.part_count == len(article_37)
    # paragraph 1 is cut between its points, and each piece repeats its first sentence
    paragraph_1 = [chunk for chunk in article_37 if chunk.part.startswith("paragraphe 1,")]
    assert len(paragraph_1) == 2
    for chunk in paragraph_1:
        assert "1. Le responsable du traitement et le sous-traitant désignent" in chunk.text


def test_inserted_paragraphs_keep_their_label(ai_act_html):
    _, chunks = build_chunks(AI_ACT, ai_act_html, max_chars=SMALL_LIMIT)
    article_5 = {chunk.id: chunk for chunk in chunks if chunk.number == "5"}

    assert "ai_act:art_5:par_1-ter" in article_5
    assert article_5["ai_act:art_5:par_1-ter"].part == "paragraphe 1 ter"
    assert any(chunk.part.startswith("paragraphe 1 bis") for chunk in article_5.values())
    assert any(chunk.part.startswith("paragraphe 1, point b bis)") for chunk in article_5.values())


def test_annex_is_cut_by_point(ai_act_html):
    _, chunks = build_chunks(AI_ACT, ai_act_html, max_chars=SMALL_LIMIT)
    annex_3 = [chunk for chunk in chunks if chunk.unit_type == "annex"]

    assert [chunk.id for chunk in annex_3][-1] == "ai_act:anx_III:pt_2"
    for chunk in annex_3:
        assert chunk.number == "III"
        assert chunk.chapter is None
        assert chunk.text.startswith("AI Act — règlement (UE) 2024/1689 — Annexe III : Systèmes d'IA à haut risque")
        # the sentence that introduces the list is repeated in every point
        assert "sont les systèmes d'IA répertoriés dans l'un des domaines suivants" in chunk.text


def test_metadata_is_complete(all_small_chunks):
    required = ["id", "regulation", "regulation_ref", "celex", "unit_type", "number", "title", "source_url", "version_date", "text"]

    assert len({chunk.id for chunk in all_small_chunks}) == len(all_small_chunks)
    for chunk in all_small_chunks:
        data = chunk.to_dict()
        assert all(data[key] for key in required), chunk.id
        assert chunk.source_url.startswith("https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:")
        assert "#art_" in chunk.source_url or "#anx_" in chunk.source_url
        assert chunk.version_date in {"2016-05-04", "2026-07-27"}
        assert 1 <= chunk.part_index <= chunk.part_count
        assert chunk.char_count == len(chunk.text)
        if chunk.unit_type == "article":
            assert chunk.chapter


def test_no_text_is_lost(gdpr_html, ai_act_html):
    for source, html in [(GDPR, gdpr_html), (AI_ACT, ai_act_html)]:
        units, chunks = build_chunks(source, html, max_chars=SMALL_LIMIT)
        for unit in units:
            unit_chunks = [chunk for chunk in chunks if chunk.source_url.endswith(f"#{unit.anchor}")]
            assert missing_lines(unit, unit_chunks) == [], unit.anchor


def test_editorial_marks_are_removed(all_small_chunks):
    for chunk in all_small_chunks:
        assert not any(mark in chunk.text for mark in "▼►◄"), chunk.id


def test_read_amendments(ai_act_html):
    amendments = read_amendments(ai_act_html)

    assert amendments[0].startswith("M1 : RÈGLEMENT (UE) 2026/1744")
    assert amendments[1].startswith("C1 : Rectificatif")
