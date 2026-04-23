from app.knowledge_base.icd_index import load_icd_index


def search_icd10cm(term: str, max_results: int = 20) -> list[dict]:
    kb = load_icd_index()
    term_lower = term.lower()
    results = []
    for code, data in kb["complete"].items():
        if code not in kb["leaf_codes"]:
            continue
        desc = data.get("description", "").lower()
        inclusion = " ".join(data.get("inclusion_terms", [])).lower()
        if term_lower in desc or term_lower in inclusion:
            results.append({
                "code": code,
                "description": data["description"],
                "is_leaf": data["is_leaf"],
            })
        if len(results) >= max_results:
            break
    return results


def get_code_details(code: str) -> dict | None:
    kb = load_icd_index()
    data = kb["complete"].get(code)
    if data is None:
        return None
    # Ensure the code key is present in the returned dict
    if "code" not in data:
        return {"code": code, **data}
    return data


def get_children(code: str) -> list[str]:
    kb = load_icd_index()
    data = kb["complete"].get(code)
    if not data:
        return []
    return data.get("children", [])


def filter_by_chapter(chapter_number: int) -> list[str]:
    kb = load_icd_index()
    chapter_key = str(chapter_number)
    return kb["chapter_index"].get(chapter_key, [])
