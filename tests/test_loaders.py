import pytest
from app.knowledge_base.icd_index import load_icd_index


def test_icd_index_loads():
    kb = load_icd_index()
    assert "complete" in kb
    assert "leaf_codes" in kb
    assert "chapter_index" in kb


def test_icd_index_has_known_code():
    kb = load_icd_index()
    assert "I10" in kb["complete"]
    assert kb["complete"]["I10"]["description"] == "Essential (primary) hypertension"


def test_leaf_codes_are_billable():
    kb = load_icd_index()
    assert "I10" in kb["leaf_codes"]


def test_chapter_index_has_22_chapters():
    kb = load_icd_index()
    assert len(kb["chapter_index"]) == 22
