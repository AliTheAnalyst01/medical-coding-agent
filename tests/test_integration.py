import httpx
import pytest


BASE_URL = "http://localhost:8000"


@pytest.fixture(scope="module")
def client():
    return httpx.Client(base_url=BASE_URL, timeout=180.0)


def test_health_check(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_simple_hypertension_note(client):
    r = client.post("/code", json={"note": "Patient has essential hypertension."})
    assert r.status_code == 200
    data = r.json()
    codes = [c["code"] for c in data["codes"] if c["status"] == "accepted"]
    assert "I10" in codes


def test_diabetes_with_complication(client):
    r = client.post("/code", json={"note": "Type 2 DM with hyperglycemia and CKD stage 3."})
    assert r.status_code == 200
    data = r.json()
    codes = [c["code"] for c in data["codes"] if c["status"] == "accepted"]
    assert any(c.startswith("E11") for c in codes)


def test_phi_is_scrubbed(client):
    r = client.post(
        "/code",
        json={"note": "John Smith, DOB 01/01/1980, presents with hypertension."},
    )
    assert r.status_code == 200
    data = r.json()
    assert "John Smith" not in data["scrubbed_note"]
    assert "01/01/1980" not in data["scrubbed_note"]


def test_excludes1_conflict_rejected(client):
    r = client.post(
        "/code",
        json={"note": "Patient has both Type 1 diabetes mellitus and Type 2 diabetes mellitus."},
    )
    assert r.status_code == 200
    data = r.json()
    rejected = [c["code"] for c in data["codes"] if c["status"] == "rejected"]
    assert len(rejected) > 0


def test_trace_is_populated(client):
    r = client.post("/code", json={"note": "Patient has hypertension."})
    assert r.status_code == 200
    data = r.json()
    assert len(data["trace_steps"]) > 0
    agents = {s["agent"] for s in data["trace_steps"]}
    assert "icd_cm_worker" in agents
    assert "validator" in agents
