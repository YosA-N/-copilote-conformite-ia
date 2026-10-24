"""Offline tests for the search index, with the fake embedding model and a temporary Chroma database."""

import pytest

from compliance_copilot.index import IndexNotReadyError, build_index, open_collection, read_manifest, search


def test_build_stores_every_chunk_with_its_metadata(chunks_file, tmp_path, fake_embedder):
    index_dir = tmp_path / "index"

    report = build_index(chunks_file, index_dir, fake_embedder)

    assert (report.status, report.chunk_count) == ("built", 6)
    stored = open_collection(index_dir).get(ids=["gdpr:art_37"], include=["metadatas", "documents"])
    metadata = stored["metadatas"][0]
    assert metadata["regulation"] == "RGPD"
    assert metadata["unit_type"] == "article"
    assert metadata["number"] == "37"
    assert metadata["title"] == "Désignation du délégué à la protection des données"
    assert metadata["chapter"] == "Chapitre IV — Responsable du traitement et sous-traitant"
    assert metadata["source_url"].endswith("#art_37")
    assert metadata["version_date"] == "2016-05-04"
    assert "part" not in metadata  # empty fields are left out: Chroma refuses None
    assert stored["documents"][0].startswith("RGPD — règlement (UE) 2016/679 — Article 37")
    assert read_manifest(index_dir)["chunk_count"] == 6


def test_unchanged_corpus_is_not_embedded_again(chunks_file, tmp_path, fake_embedder):
    index_dir = tmp_path / "index"
    build_index(chunks_file, index_dir, fake_embedder)
    calls_after_first_build = fake_embedder.calls

    report = build_index(chunks_file, index_dir, fake_embedder)

    assert report.status == "unchanged"
    assert fake_embedder.calls == calls_after_first_build


def test_changed_corpus_or_model_rebuilds_the_index(chunks_file, tmp_path, fake_embedder, other_model_embedder):
    index_dir = tmp_path / "index"
    build_index(chunks_file, index_dir, fake_embedder)
    lines = chunks_file.read_text(encoding="utf-8").splitlines()
    chunks_file.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")  # one chunk less

    assert build_index(chunks_file, index_dir, fake_embedder).status == "built"
    assert open_collection(index_dir).count() == 5

    assert build_index(chunks_file, index_dir, other_model_embedder).status == "built"
    assert read_manifest(index_dir)["embedding_model"] == "other-model"


def test_search_returns_the_closest_chunks_first(chunks_file, tmp_path, fake_embedder):
    index_dir = tmp_path / "index"
    build_index(chunks_file, index_dir, fake_embedder)

    # the fake model only counts words: the question uses words that only article 37 contains
    results = search("désignation délégué", index_dir, fake_embedder, k=3)

    assert [result.rank for result in results] == [1, 2, 3]
    assert results[0].id == "gdpr:art_37"
    assert results[0].metadata["source_url"].endswith("#art_37")
    scores = [result.score for result in results]
    assert scores == sorted(scores, reverse=True)
    assert all(-1 <= score <= 1 for score in scores)


def test_search_refuses_an_index_built_with_another_model(chunks_file, tmp_path, fake_embedder, other_model_embedder):
    index_dir = tmp_path / "index"
    build_index(chunks_file, index_dir, fake_embedder)

    with pytest.raises(IndexNotReadyError, match="other-model"):
        search("DPO", index_dir, other_model_embedder)


def test_search_without_index_says_what_to_do(tmp_path, fake_embedder):
    with pytest.raises(IndexNotReadyError, match="build_index"):
        search("DPO", tmp_path / "missing", fake_embedder)
