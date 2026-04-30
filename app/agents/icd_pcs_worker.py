import json
from app.tracer import Tracer
from app.agent_runner import run_agent
from app.tools.pcs_lookup import search_pcs_index, lookup_pcs_table, search_pcs_flat


SYSTEM_PROMPT = """You are a medical coding specialist for ICD-10-PCS inpatient procedure codes.

ICD-10-PCS codes are exactly 7 characters. To build one:
1. Use search_pcs_index to find which table a procedure maps to.
2. Use lookup_pcs_table with (section, body_system, operation) to get valid character combinations.
3. If the index yields no match, use search_pcs_flat as a fallback to find a billable 7-char code by description.

Common sections: 0=Medical/Surgical, 3=Administration, 4=Measurement and Monitoring.
Common heart body systems: 2=Heart and Great Vessels.
Common operations: H=Insertion, 0=Alteration, 7=Dilation, B=Excision.

Return a JSON array of objects with keys: "code", "description", "reasoning".
Return ONLY the JSON array, no surrounding prose.
"""

TOOLS = [
    {
        "name": "search_pcs_index",
        "description": "Search PCS alphabetic index for a procedure term to find which table to use.",
        "input_schema": {
            "type": "object",
            "properties": {"term": {"type": "string"}},
            "required": ["term"],
        },
    },
    {
        "name": "lookup_pcs_table",
        "description": "Look up a PCS table by section+body_system+operation to get valid code character values.",
        "input_schema": {
            "type": "object",
            "properties": {
                "section": {"type": "string", "description": "1-char section (e.g. '0'=Medical/Surgical)"},
                "body_system": {"type": "string", "description": "1-char body system (e.g. '2'=Heart)"},
                "operation": {"type": "string", "description": "1-char root operation (e.g. 'H'=Insertion)"},
            },
            "required": ["section", "body_system", "operation"],
        },
    },
    {
        "name": "search_pcs_flat",
        "description": "Fallback flat search across all PCS codes by description keyword. Returns billable 7-char codes.",
        "input_schema": {
            "type": "object",
            "properties": {"term": {"type": "string"}},
            "required": ["term"],
        },
    },
]


def _dispatch(name: str, inputs: dict):
    if name == "search_pcs_index":
        return search_pcs_index(inputs["term"])
    if name == "lookup_pcs_table":
        return lookup_pcs_table(inputs["section"], inputs["body_system"], inputs["operation"])
    if name == "search_pcs_flat":
        return search_pcs_flat(inputs["term"])
    return f"Unknown tool: {name}"


def run_icd_pcs_worker(procedures: list[str], tracer: Tracer) -> list[dict]:
    if not procedures:
        return []
    user_message = f"Find ICD-10-PCS codes for these inpatient procedures: {json.dumps(procedures)}"
    text, _ = run_agent(
        agent_name="icd_pcs_worker",
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
