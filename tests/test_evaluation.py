"""Offline tests for the retrieval measures and for the file of test questions."""

import re

from compliance_copilot.config import EVAL_DIR
from compliance_copilot.evaluation import describe_reference, first_hit_rank, hit_at_k, load_questions, matches

REFERENCE = re.compile(r"^(gdpr|ai_act):(art_\d+[a-z]?|anx_[IVXLC]+)(:[\w-]+)*$")


def test_a_reference_matches_its_whole_article_and_nothing_else():
    assert matches("gdpr:art_37", "gdpr:art_37")
    assert matches("gdpr:art_12:par_3", "gdpr:art_12")
    assert matches("ai_act:anx_III:pt_4", "ai_act:anx_III")
    assert not matches("gdpr:art_37", "gdpr:art_3")
    assert not matches("gdpr:art_3", "gdpr:art_37")
    assert not matches("ai_act:anx_III:pt_4", "ai_act:anx_III:pt_1")


def test_first_hit_rank_and_hit_at_k():
    results = ["gdpr:art_38", "gdpr:art_37:par_1", "gdpr:art_39"]

    assert first_hit_rank(results, ["gdpr:art_37"]) == 2
    assert first_hit_rank(results, ["gdpr:art_30", "gdpr:art_39"]) == 3
    assert first_hit_rank(results, ["gdpr:art_30"]) is None
    ranks = [1, 2, None, 6, 5]
    assert hit_at_k(ranks, 1) == 1
    assert hit_at_k(ranks, 5) == 3


def test_describe_reference():
    assert describe_reference("gdpr:art_37") == "RGPD art. 37"
    assert describe_reference("ai_act:art_4a") == "AI Act art. 4 bis"
    assert describe_reference("ai_act:anx_III:pt_4") == "AI Act annexe III, point 4"
    assert describe_reference("gdpr:art_12:par_3") == "RGPD art. 12, paragraphe 3"


def test_questions_file_is_well_formed():
    questions = load_questions(EVAL_DIR / "questions_v0.jsonl")

    assert len(questions) == 10
    assert len({question.id for question in questions}) == 10
    for question in questions:
        assert question.question.strip()
        assert question.expected, question.id
        assert all(REFERENCE.match(ref) for ref in question.expected + question.related), question.id
        assert question.coverage in {"complet", "partiel"}
