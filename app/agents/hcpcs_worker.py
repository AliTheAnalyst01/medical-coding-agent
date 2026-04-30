import json
from app.tracer import Tracer
from app.agent_runner import run_agent
from app.tools.hcpcs_lookup import search_hcpcs, get_hcpcs_details, get_betos_category


SYSTEM_PROMPT = """You are a medical coding specialist for HCPCS Level II codes (drugs, supplies, equipment, outpatient procedures).

For each term:
1. Use search_hcpcs to find matching codes.
2. Use get_hcpcs_details to confirm the right code.
3. Use get_betos_category to classify the type of service if needed.

Note: HCPCS Level I codes (5-digit numeric like 92928) represent outpatient procedures (CPT-equivalent).
HCPCS Level II codes (letter + 4 digits like J1815) represent drugs, supplies, equipment.

Return a JSON array of objects with keys: "code", "description", "reasoning".
Return ONLY the JSON array, no surrounding prose.
"""

TOOLS = [
    {
        "name": "search_hcpcs",
        "description": "Search HCPCS codes by clinical term (drug name, supply type, procedure description).",
        "input_schema": {
            "type": "object",
            "properties": {"term": {"type": "string"}},
            "required": ["term"],
        },
    },
    {
        "name": "get_hcpcs_details",
        "description": "Get full details for a specific HCPCS code.",
        "input_schema": {
            "type": "object",
            "properties": {"code": {"type": "string"}},
            "required": ["code"],
        },
    },
    {
        "name": "get_betos_category",
        "description": "Get the BETOS service category for a BETOS code (e.g. 'M1A'=Office visit new).",
        "input_schema": {
            "type": "object",
            "properties": {"betos_code": {"type": "string"}},
            "required": ["betos_code"],
        },
    },
]


def _dispatch(name: str, inputs: dict):
    if name == "search_hcpcs":
        return search_hcpcs(inputs["term"])
    if name == "get_hcpcs_details":
        return get_hcpcs_details(inputs["code"])
    if name == "get_betos_category":
        return get_betos_category(inputs["betos_code"])
    return f"Unknown tool: {name}"


def run_hcpcs_worker(terms: list[str], tracer: Tracer) -> list[dict]:
    if not terms:
        return []
    user_message = f"Find HCPCS codes for these drugs/supplies/procedures: {json.dumps(terms)}"
    text, _ = run_agent(
        agent_name="hcpcs_worker",
        system_prompt=SYSTEM_PROMPT,
        user_message=user_message,
        tools=TOOLS,
        tool_dispatch=_dispatch,
        tracer=tracer,
    )
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return []
