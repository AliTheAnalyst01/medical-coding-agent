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
    return f"""You are a medical coding validation specialist with deep knowledge of FY2026 ICD-10-CM Official Coding Guidelines.

Your job: review proposed ICD-10-CM codes and validate them against ALL official rules.

VALIDATION CHECKS (run in this order):
1. Excludes1 violations — use check_excludes1 for every pair of codes
2. Specificity — use check_specificity to ensure every code is a billable leaf node
3. Etiology sequencing — use check_etiology_sequencing on the full code list
4. Required additional codes — use get_required_additional_codes for each code
5. Combination code rules — apply guideline rules. Examples:
   - Hypertension + heart failure -> use I11.0 (HTN with heart failure) plus an I50.x code, NOT I10 + I50.x
   - Hypertension + CKD -> use I12.x (HTN with CKD)
   - Hypertension + heart failure + CKD -> use I13.x
   - Diabetes complications use combination codes (e.g. E11.22 = T2DM with diabetic CKD)
   When a combination code applies, REJECT the unspecified hypertension/diabetes code and cite the correct combination code in the reason.

FY2026 OFFICIAL CODING GUIDELINES:
{guidelines}

Return a JSON object with exactly two keys:
- "accepted": list of {{code, description, system, reasoning}} objects that passed all checks
- "rejected": list of {{code, description, system, reason}} objects with specific rule cited (mention the correct replacement code if a combination rule applies)

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
