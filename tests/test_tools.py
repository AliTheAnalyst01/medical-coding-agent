import pytest
from app.tools.icd_lookup import (
    search_icd10cm,
    get_code_details,
    get_children,
    filter_by_chapter,
)

def test_search_returns_results_for_hypertension():
    results = search_icd10cm("hypertension")
    codes = [r["code"] for r in results]
    assert "I10" in codes

def test_search_returns_results_for_diabetes():
    results = search_icd10cm("type 2 diabetes")
    codes = [r["code"] for r in results]
    assert any(c.startswith("E11") for c in codes)

def test_get_code_details_known_code():
    details = get_code_details("I10")
    assert details["code"] == "I10"
    assert details["is_leaf"] is True
    assert "hypertension" in details["description"].lower()

def test_get_code_details_unknown_returns_none():
    assert get_code_details("ZZZZZ") is None

def test_get_children_returns_list():
    children = get_children("E11")
    assert isinstance(children, list)
    assert len(children) > 0
    assert any("E11." in c for c in children)

def test_filter_by_chapter_circulatory():
    codes = filter_by_chapter(9)  # Chapter 9 = circulatory
    assert "I10" in codes
    assert len(codes) > 1000


from app.tools.graph_validator import (
    check_excludes1,
    check_specificity,
    check_etiology_sequencing,
    get_required_additional_codes,
)

def test_check_excludes1_detects_conflict():
    # Type 1 DM and Type 2 DM are mutually exclusive (E10 and E11 are in excludes1_set)
    result = check_excludes1("E10", "E11")
    assert result["conflict"] is True
    assert "Excludes1" in result["reason"]

def test_check_excludes1_no_conflict():
    # HTN and DM can coexist
    result = check_excludes1("I10", "E11.9")
    assert result["conflict"] is False

def test_check_specificity_leaf_code():
    result = check_specificity("I10")
    assert result["is_leaf"] is True
    assert result["has_children"] is False

def test_check_specificity_non_leaf():
    result = check_specificity("E11")
    assert result["is_leaf"] is False
    assert result["has_children"] is True

def test_get_required_additional_codes_returns_list():
    result = get_required_additional_codes("E11.40")
    assert isinstance(result, list)


from app.tools.pcs_lookup import search_pcs_index, search_pcs_flat
from app.tools.hcpcs_lookup import search_hcpcs, get_hcpcs_details, get_betos_category


def test_search_pcs_flat_bypass():
    results = search_pcs_flat("bypass")
    assert isinstance(results, list)
    assert len(results) > 0


def test_search_hcpcs_insulin():
    results = search_hcpcs("insulin")
    assert isinstance(results, list)
    assert len(results) > 0


def test_get_hcpcs_details_returns_dict():
    result = get_hcpcs_details("J1815")
    assert isinstance(result, dict)


def test_get_betos_category_returns_string():
    result = get_betos_category("M1A")
    assert isinstance(result, str)
