import json
from app.tracer import Tracer
from app.agent_runner import run_agent


SYSTEM_PROMPT = """You are a medical coding coordinator. Your job is to read a clinical note and extract all medical entities that need to be coded.

Categorize every entity into exactly one of three groups:
1. diagnoses — diseases, conditions, symptoms, findings (will be coded as ICD-10-CM)
2. procedures — surgeries, interventions, tests performed in an inpatient hospital setting (will be coded as ICD-10-PCS)
3. drugs_supplies — medications administered, medical supplies, equipment used, outpatient procedures (will be coded as HCPCS)

Rules:
- Include ALL conditions mentioned, including comorbidities and history.
- For procedures: if inpatient hospital procedure -> procedures. If outpatient/office or drug administration -> drugs_supplies.
- Be specific with terms (e.g. "acute inferior STEMI" not just "heart problem").
- Do NOT include PHI (names, dates, MRNs) — the note has already been scrubbed.

Output: return ONLY a JSON object with exactly these keys: "diagnoses", "procedures", "drugs_supplies".
Each value is an array of strings. No prose, no markdown fences.

Example:
{"diagnoses": ["acute inferior STEMI", "type 2 diabetes mellitus"], "procedures": ["percutaneous coronary intervention with stent"], "drugs_supplies": ["IV insulin"]}
"""


def run_coordinator(note: str, tracer: Tracer) -> dict:
    text, _ = run_agent(
        agent_name="coordinator",
        system_prompt=SYSTEM_PROMPT,
        user_message=f"Extract all medical entities from this clinical note:\n\n{note}",
        tools=[],
        tool_dispatch=lambda name, inputs: None,
        tracer=tracer,
    )
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()
    try:
        result = json.loads(cleaned)
        return {
            "diagnoses": result.get("diagnoses", []),
            "procedures": result.get("procedures", []),
            "drugs_supplies": result.get("drugs_supplies", []),
        }
    except json.JSONDecodeError:
        return {"diagnoses": [note], "procedures": [], "drugs_supplies": []}
