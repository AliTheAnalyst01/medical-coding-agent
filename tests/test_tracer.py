import json
from pathlib import Path
from app.tracer import Tracer

def test_tracer_records_steps():
    t = Tracer(request_id="test001")
    step = t.record("coordinator", "extract_medical_entities", {"note": "HTN"}, {"diagnoses": ["HTN"]}, 120)
    assert len(t.steps) == 1
    assert step is t.steps[0]
    assert step["agent"] == "coordinator"
    assert step["tool"] == "extract_medical_entities"
    assert step["duration_ms"] == 120

def test_tracer_saves_to_disk(tmp_path, monkeypatch):
    import app.tracer as tracer_module
    monkeypatch.setattr(tracer_module, "TRACES_DIR", tmp_path)
    t = Tracer(request_id="test002")
    t.record("icd_cm_worker", "search_icd10cm", "hypertension", ["I10"], 80)
    path = t.save(
        input_note="Patient has HTN",
        final_codes=[{"code": "I10", "status": "accepted"}],
        rejected_codes=[],
        tokens_used=500,
    )
    assert Path(path).exists()
    with open(path) as f:
        data = json.load(f)
    assert data["request_id"] == "test002"
    assert len(data["steps"]) == 1
    assert data["final_codes"][0]["code"] == "I10"
