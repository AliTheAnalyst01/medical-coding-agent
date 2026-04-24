import json
import re
from app.tracer import Tracer
from app.agent_runner import run_agent
from app.tools.graph_validator import (
    check_excludes1,
    check_specificity,
    check_etiology_sequencing,
    get_required_additional_codes,
)
from app.knowledge_base.guidelines_loader import load_guidelines


def _build_system_prompt() -> str:
    guidelines = load_guidelines()
    return f"""You are a medical coding validation specialist.

Your job: review proposed ICD-10-CM codes and validate them against official rules.

For each pair of codes, use check_excludes1 to detect Excludes1 violations.
Use check_specificity to ensure every code is a billable leaf node (not a category header).
Use check_etiology_sequencing to verify etiology codes are sequenced first.
Use get_required_additional_codes to find any missing mandatory codes.

FY2026 OFFICIAL CODING GUIDELINES (apply these rules):
{guidelines[:3000]}

Return a JSON object with exactly two keys:
- "accepted": list of {{code, description, system, reasoning}} objects that passed validation
- "rejected": list of {{code, description, system, reason}} objects that failed

Return ONLY the JSON object, no other text."""


TOOLS = [
    {
        "name": "check_excludes1",
        "description": "Check if two ICD-10-CM codes have an Excludes1 relationship (mutually exclusive — cannot both be coded).",
        "input_schema": {
            "type": "object",
            "properties": {
                "code_a": {"type": "string"},
                "code_b": {"type": "string"},
            },
            "required": ["code_a", "code_b"],
        },
    },
    {
        "name": "check_specificity",
        "description": "Check if an ICD-10-CM code is a billable leaf node. If not, returns child codes to choose from.",
        "input_schema": {
            "type": "object",
            "properties": {"code": {"type": "string"}},
            "required": ["code"],
        },
    },
    {
        "name": "check_etiology_sequencing",
        "description": "Check if a list of codes has correct etiology/manifestation sequencing.",
        "input_schema": {
            "type": "object",
            "properties": {
                "codes": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["codes"],
        },
    },
    {
        "name": "get_required_additional_codes",
        "description": "Get any additional codes that MUST be coded alongside a given code.",
        "input_schema": {
            "type": "object",
            "properties": {"code": {"type": "string"}},
            "required": ["code"],
        },
    },
]


def _dispatch(name: str, inputs: dict):
    if name == "check_excludes1":
        return check_excludes1(inputs["code_a"], inputs["code_b"])
    if name == "check_specificity":
        return check_specificity(inputs["code"])
    if name == "check_etiology_sequencing":
        return check_etiology_sequencing(inputs["codes"])
    if name == "get_required_additional_codes":
        return get_required_additional_codes(inputs["code"])
    raise ValueError(f"Unknown tool: {name}")


def _extract_json_object(text: str) -> dict:
    """Extract JSON object from response, handling markdown code fences."""
    text = text.strip()
    # Try fenced block first
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    # Try bare JSON object
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    raise json.JSONDecodeError("No JSON object found", text, 0)


def run_validator(proposed_codes: list[dict], tracer: Tracer) -> dict:
    user_message = f"Validate these proposed medical codes:\n{json.dumps(proposed_codes, indent=2)}"
    text, _ = run_agent(
        agent_name="validator",
        system_prompt=_build_system_prompt(),
        user_message=user_message,
        tools=TOOLS,
        tool_dispatch=_dispatch,
        tracer=tracer,
    )
    try:
        return _extract_json_object(text)
    except (json.JSONDecodeError, Exception):
        return {"accepted": proposed_codes, "rejected": [], "parse_error": text[:200]}
