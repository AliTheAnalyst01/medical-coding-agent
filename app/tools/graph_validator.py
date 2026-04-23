from app.knowledge_base.graph_loader import load_graph
from app.knowledge_base.icd_index import load_icd_index


def check_excludes1(code_a: str, code_b: str) -> dict:
    data = load_graph()
    if (code_a, code_b) in data["excludes1_set"]:
        return {
            "conflict": True,
            "reason": f"Excludes1: {code_a} and {code_b} are mutually exclusive — cannot be coded together",
        }
    return {"conflict": False, "reason": ""}


def check_excludes2(code_a: str, code_b: str) -> dict:
    data = load_graph()
    G = data["graph"]
    for u, v, d in G.edges(code_a, data=True):
        if v == code_b and d.get("edge_type") == "EXCLUDES2":
            return {
                "note": f"Excludes2: {code_b} is not included in {code_a} but can be coded separately if applicable"
            }
    return {"note": ""}


def check_specificity(code: str) -> dict:
    kb = load_icd_index()
    details = kb["complete"].get(code)
    if not details:
        return {"is_leaf": False, "has_children": False, "children": [], "error": f"{code} not found"}
    children = details.get("children", [])
    return {
        "is_leaf": details.get("is_leaf", False),
        "has_children": len(children) > 0,
        "children": children[:10],
    }


def check_etiology_sequencing(codes: list[str]) -> dict:
    data = load_graph()
    etiology_pairs = data["etiology_pairs"]
    issues = []
    for code in codes:
        if code in etiology_pairs:
            required_first = etiology_pairs[code]
            if required_first not in codes:
                issues.append({
                    "code": code,
                    "requires_first": required_first,
                    "rule": f"Code {required_first} must be sequenced before {code}",
                })
    return {"issues": issues, "valid": len(issues) == 0}


def get_required_additional_codes(code: str) -> list[str]:
    data = load_graph()
    G = data["graph"]
    if code not in G:
        return []
    required = []
    for u, v, d in G.edges(code, data=True):
        if d.get("edge_type") == "USE_ADDITIONAL_CODE":
            required.append(v)
    return required
