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
