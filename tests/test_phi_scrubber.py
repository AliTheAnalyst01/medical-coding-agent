from app.tools.phi_scrubber import scrub_phi

def test_scrubs_person_name():
    note = "John Smith presented with chest pain."
    result = scrub_phi(note)
    assert "John Smith" not in result
    assert "presented with chest pain" in result

def test_scrubs_date():
    note = "Patient admitted on 04/15/2026 with fever."
    result = scrub_phi(note)
    assert "04/15/2026" not in result
    assert "fever" in result

def test_preserves_clinical_terms():
    note = "Patient has STEMI, Type 2 DM, and hypertension."
    result = scrub_phi(note)
    assert "STEMI" in result
    assert "Type 2 DM" in result
    assert "hypertension" in result

def test_returns_string():
    result = scrub_phi("Normal note with no PHI.")
    assert isinstance(result, str)
