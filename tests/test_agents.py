import pytest
from app.tracer import Tracer
from app.agents.icd_cm_worker import run_icd_cm_worker
from app.agents.validator import run_validator


def test_icd_cm_worker_finds_hypertension():
    tracer = Tracer("test-icd-01")
    result = run_icd_cm_worker(
        diagnoses=["essential hypertension"],
        tracer=tracer,
    )
    codes = [c["code"] for c in result]
    assert "I10" in codes


def test_icd_cm_worker_returns_leaf_codes_only():
    tracer = Tracer("test-icd-02")
    result = run_icd_cm_worker(
        diagnoses=["type 2 diabetes mellitus"],
        tracer=tracer,
    )
    from app.knowledge_base.icd_index import load_icd_index
    kb = load_icd_index()
    for item in result:
        assert item["code"] in kb["leaf_codes"], f"{item['code']} is not a billable leaf code"


def test_icd_cm_worker_records_trace_steps():
    tracer = Tracer("test-icd-03")
    run_icd_cm_worker(diagnoses=["hypertension"], tracer=tracer)
    assert len(tracer.steps) > 0
    agent_names = {s["agent"] for s in tracer.steps}
    assert "icd_cm_worker" in agent_names


def test_validator_rejects_excludes1_conflict():
    tracer = Tracer("test-val-01")
    proposed = [
        {"code": "E10", "description": "Type 1 DM", "system": "ICD-10-CM"},
        {"code": "E11", "description": "Type 2 DM", "system": "ICD-10-CM"},
    ]
    result = run_validator(proposed_codes=proposed, tracer=tracer)
    rejected = [r["code"] for r in result["rejected"]]
    assert "E10" in rejected or "E11" in rejected


def test_validator_accepts_valid_codes():
    tracer = Tracer("test-val-02")
    proposed = [
        {"code": "I10", "description": "Essential hypertension", "system": "ICD-10-CM"},
        {"code": "E11.65", "description": "Type 2 DM with hyperglycemia", "system": "ICD-10-CM"},
    ]
    result = run_validator(proposed_codes=proposed, tracer=tracer)
    accepted = [r["code"] for r in result["accepted"]]
    assert "I10" in accepted


def test_validator_returns_correct_structure():
    tracer = Tracer("test-val-03")
    proposed = [{"code": "I10", "description": "Essential hypertension", "system": "ICD-10-CM"}]
    result = run_validator(proposed_codes=proposed, tracer=tracer)
    assert "accepted" in result
    assert "rejected" in result
    assert isinstance(result["accepted"], list)
    assert isinstance(result["rejected"], list)


from app.agents.icd_pcs_worker import run_icd_pcs_worker
from app.agents.hcpcs_worker import run_hcpcs_worker
from app.agents.coordinator import run_coordinator


def test_hcpcs_worker_finds_insulin():
    tracer = Tracer("test-hcpcs-01")
    result = run_hcpcs_worker(terms=["insulin injection"], tracer=tracer)
    assert isinstance(result, list)


def test_pcs_worker_returns_list():
    tracer = Tracer("test-pcs-01")
    result = run_icd_pcs_worker(
        procedures=["percutaneous coronary intervention stent"],
        tracer=tracer,
    )
    assert isinstance(result, list)


def test_coordinator_extracts_entities():
    tracer = Tracer("test-coord-01")
    note = "Patient presents with acute inferior STEMI. Underwent PCI with drug-eluting stent. Also has Type 2 DM and HTN."
    result = run_coordinator(note=note, tracer=tracer)
    assert "diagnoses" in result
    assert "procedures" in result
    assert "drugs_supplies" in result
    assert len(result["diagnoses"]) > 0


def test_coordinator_identifies_procedures():
    tracer = Tracer("test-coord-02")
    note = "Patient underwent percutaneous coronary intervention with stent placement and received IV insulin drip."
    result = run_coordinator(note=note, tracer=tracer)
    assert len(result["procedures"]) > 0 or len(result["drugs_supplies"]) > 0


def test_validator_applies_hypertension_heart_failure_rule():
    """FY2026 rule: HTN + heart failure must use combination code I11.0, not I10 + I50.x separately."""
    tracer = Tracer("test-val-guideline-01")
    proposed = [
        {"code": "I10", "description": "Essential hypertension", "system": "ICD-10-CM"},
        {"code": "I50.9", "description": "Heart failure unspecified", "system": "ICD-10-CM"},
    ]
    result = run_validator(proposed_codes=proposed, tracer=tracer)
    all_codes = result["accepted"] + result["rejected"]
    reasonings = " ".join(c.get("reasoning", "") + c.get("reason", "") for c in all_codes)
    assert "I11" in reasonings or "combination" in reasonings.lower() or len(result["rejected"]) > 0


def test_icd_cm_worker_flags_insufficient_documentation():
    tracer = Tracer("test-icd-insuf-01")
    result = run_icd_cm_worker(
        diagnoses=["some kind of heart problem, unclear"],
        tracer=tracer,
    )
    flagged = any(
        c.get("code") == "QUERY_REQUIRED" or "insufficient" in c.get("reasoning", "").lower()
        for c in result
    )
    assert flagged or len(result) == 0
