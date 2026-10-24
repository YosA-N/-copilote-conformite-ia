"""Offline tests for the answer pipeline, with the fake embedding model and the fake language model."""

from conftest import FakeChatModel

from compliance_copilot.rag import (
    DISCLAIMER,
    SYSTEM_PROMPT,
    CitationStream,
    answer_question,
    build_messages,
    check_citations,
    normalize_citations,
    render_footer,
)
from compliance_copilot.index import search

QUESTION = "Dois-je désigner un délégué ?"


def test_prompt_gives_the_rules_and_numbers_the_passages_in_order(index_dir, fake_embedder):
    passages = search("désignation délégué", index_dir, fake_embedder, k=3)

    system, user = build_messages(QUESTION, passages)

    assert system["role"] == "system" and system["content"] == SYSTEM_PROMPT
    assert "UNIQUEMENT" in SYSTEM_PROMPT and "N'invente jamais" in SYSTEM_PROMPT
    assert user["content"].startswith("Passages :\n\n[1] RGPD — règlement (UE) 2016/679 — Article 37")
    assert user["content"].index("[1] ") < user["content"].index("[2] ") < user["content"].index("[3] ")
    assert user["content"].endswith(f"Question : {QUESTION}")


def test_citation_variants_are_written_as_plain_numbers():
    text = "Oui [1b], voir [2, 3c] et [1][2]. Mais [sic] et [lien](https://exemple.fr) ne changent pas."

    assert normalize_citations(text) == "Oui [1], voir [2, 3] et [1][2]. Mais [sic] et [lien](https://exemple.fr) ne changent pas."


def test_streamed_citations_are_normalised_even_when_cut_in_pieces():
    shown = []
    stream = CitationStream(shown.append)

    for piece in ["Oui [", "1", "b] et [2", "c]. Fin"]:
        stream.feed(piece)
    stream.close()

    assert "".join(shown) == "Oui [1] et [2]. Fin"


def test_citation_check_finds_unknown_passages():
    check = check_citations("Oui [1]. Selon [9], non [2, 3].", passage_count=5)

    assert check.cited == [1, 2, 3]
    assert check.unknown == [9]


def test_sources_come_from_the_metadata_not_from_the_model(index_dir, fake_embedder):
    model = FakeChatModel(reply="Selon l'article 99 du règlement, oui [1b].")

    answer = answer_question("désignation délégué", index_dir, fake_embedder, model, k=3)

    assert answer.text == "Selon l'article 99 du règlement, oui [1]."
    first = answer.sources[0]
    assert first.cited and first.number == 1
    assert first.label == "RGPD — règlement (UE) 2016/679, article 37 : Désignation du délégué à la protection des données"
    assert first.url.endswith("#art_37") and first.version_date == "2016-05-04"
    assert not any("99" in source.label for source in answer.sources)
    assert [source.cited for source in answer.sources] == [True, False, False]


def test_every_answer_gets_the_legal_warning(index_dir, fake_embedder):
    for reply in ["Oui [1].", "Je ne sais pas."]:
        answer = answer_question(QUESTION, index_dir, fake_embedder, FakeChatModel(reply=reply))
        assert render_footer(answer).endswith(DISCLAIMER)
        assert DISCLAIMER.startswith("Information, pas un conseil juridique")


def test_problems_are_reported_to_the_user(index_dir, fake_embedder):
    no_citation = answer_question(QUESTION, index_dir, fake_embedder, FakeChatModel(reply="Oui, sans doute."))
    unknown = answer_question(QUESTION, index_dir, fake_embedder, FakeChatModel(reply="Oui [9]."))
    truncated = answer_question(QUESTION, index_dir, fake_embedder, FakeChatModel(reply="Oui [1], et", truncated=True))

    assert any("ne cite aucun passage" in warning for warning in no_citation.warnings)
    assert any("[9]" in warning for warning in unknown.warnings)
    assert any("Réponse coupée" in warning and "700" in warning for warning in truncated.warnings)
    assert "Attention : Réponse coupée" in render_footer(truncated)


def test_passages_that_do_not_fit_in_the_context_are_dropped(index_dir, fake_embedder):
    small_model = FakeChatModel(num_ctx=1800, max_tokens=300)

    answer = answer_question(QUESTION, index_dir, fake_embedder, small_model, k=5)

    assert 1 <= len(answer.passages) < 5
    assert any("retiré(s) faute de place" in warning for warning in answer.warnings)
    assert small_model.messages[1]["content"].count("\n\n[") == len(answer.passages)  # only the kept passages are sent


def test_answer_is_streamed_and_timed(index_dir, fake_embedder):
    shown = []

    answer = answer_question(QUESTION, index_dir, fake_embedder, FakeChatModel(reply="Oui [1b] et [2]."), on_text=shown.append)

    assert "".join(shown) == "Oui [1] et [2]."
    assert answer.search_seconds >= 0 and answer.generation_seconds >= 0
    assert answer.generation.tokens_per_second == 20.0
