import pytest
from app.tracer import Tracer
from app.agents.icd_cm_worker import run_icd_cm_worker


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
