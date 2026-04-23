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


from app.knowledge_base.graph_loader import load_graph

def test_graph_loads():
    data = load_graph()
    assert "graph" in data
    assert "relationships" in data
    assert "excludes1_set" in data
    assert "etiology_pairs" in data

def test_graph_has_nodes():
    data = load_graph()
    G = data["graph"]
    assert G.number_of_nodes() > 90000

def test_relationships_has_mutual_exclusions():
    data = load_graph()
    rels = data["relationships"]
    assert "mutual_exclusions" in rels
    assert len(rels["mutual_exclusions"]) > 5000

def test_excludes1_set_built():
    data = load_graph()
    assert "excludes1_set" in data
    assert len(data["excludes1_set"]) > 5000

def test_excludes1_set_is_bidirectional():
    data = load_graph()
    s = data["excludes1_set"]
    pair = next(iter(s))
    assert (pair[1], pair[0]) in s

from app.knowledge_base.guidelines_loader import load_guidelines

def test_guidelines_load():
    text = load_guidelines()
    assert isinstance(text, str)
    assert len(text) > 5000

def test_guidelines_contain_key_rules():
    text = load_guidelines()
    assert "Excludes1" in text
    assert "principal diagnosis" in text.lower()
