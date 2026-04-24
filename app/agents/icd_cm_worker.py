import json
import re
from app.tracer import Tracer
from app.agent_runner import run_agent
from app.tools.icd_lookup import search_icd10cm, get_code_details, get_children, filter_by_chapter

SYSTEM_PROMPT = """You are a medical coding specialist for ICD-10-CM diagnosis codes.

Your job:
1. For each diagnosis term given, find the most specific BILLABLE ICD-10-CM code.
2. Use search_icd10cm to find candidate codes.
3. Use get_code_details to check if a code is a leaf (billable). If is_leaf is false, use get_children to drill deeper.
4. Use filter_by_chapter when you know the body system (e.g., circulatory=9, endocrine=4) to narrow the search.
5. Always return the most specific billable code available.

CRITICAL: Never return a parent/category code. If get_code_details shows is_leaf=False, you MUST call get_children and pick from the children.

Return a JSON array of objects. Each object must have:
- "code": the ICD-10-CM code (e.g. "I10")
- "description": the code description
- "reasoning": why this code was chosen

Return ONLY the JSON array, no other text."""

TOOLS = [
    {
        "name": "search_icd10cm",
        "description": "Search ICD-10-CM billable codes by clinical term. Returns up to 20 matching codes.",
        "input_schema": {
            "type": "object",
            "properties": {
                "term": {"type": "string", "description": "Clinical term to search (e.g. 'hypertension', 'STEMI inferior wall')"}
            },
            "required": ["term"],
        },
    },
    {
        "name": "get_code_details",
        "description": "Get full details for a specific ICD-10-CM code including is_leaf, children, excludes1.",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "ICD-10-CM code (e.g. 'I10', 'E11.9')"}
            },
            "required": ["code"],
        },
    },
    {
        "name": "get_children",
        "description": "Get child codes (more specific subcategories) of an ICD-10-CM code.",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Parent ICD-10-CM code"}
            },
            "required": ["code"],
        },
    },
    {
        "name": "filter_by_chapter",
        "description": "Get all codes belonging to a specific ICD-10-CM chapter (1-22). Use to narrow search space.",
        "input_schema": {
            "type": "object",
            "properties": {
                "chapter_number": {"type": "integer", "description": "Chapter number 1-22 (9=circulatory, 4=endocrine/diabetes, 19=injury)"}
            },
            "required": ["chapter_number"],
        },
    },
]


def _dispatch(name: str, inputs: dict):
    if name == "search_icd10cm":
        return search_icd10cm(inputs["term"])
    if name == "get_code_details":
        return get_code_details(inputs["code"])
    if name == "get_children":
        return get_children(inputs["code"])
    if name == "filter_by_chapter":
        return filter_by_chapter(inputs["chapter_number"])
    raise ValueError(f"Unknown tool: {name}")


def run_icd_cm_worker(diagnoses: list[str], tracer: Tracer) -> list[dict]:
    user_message = f"Find ICD-10-CM codes for these diagnoses: {json.dumps(diagnoses)}"
    text, _ = run_agent(
        agent_name="icd_cm_worker",
        system_prompt=SYSTEM_PROMPT,
        user_message=user_message,
        tools=TOOLS,
        tool_dispatch=_dispatch,
        tracer=tracer,
    )
    # Extract JSON array — handle plain JSON or text + code fence wrapper
    text = text.strip()
    match = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", text, re.DOTALL)
    if match:
        text = match.group(1)
    else:
        # Try to find a bare JSON array
        array_match = re.search(r"\[.*\]", text, re.DOTALL)
        if array_match:
            text = array_match.group(0)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return []
