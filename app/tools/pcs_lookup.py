from app.knowledge_base.pcs_loader import load_pcs


def search_pcs_index(term: str, max_results: int = 10) -> list[dict]:
    data = load_pcs()
    index = data["index"]
    term_lower = term.lower()
    results = []
    for key, value in index.items():
        if term_lower in key.lower():
            results.append({"term": key, "entry": value})
        if len(results) >= max_results:
            break
    return results


def lookup_pcs_table(section: str, body_system: str, operation: str) -> dict | None:
    data = load_pcs()
    tables = data["tables"]
    key = f"{section}{body_system}{operation}"
    return tables.get(key)


def search_pcs_flat(term: str, max_results: int = 10) -> list[dict]:
    data = load_pcs()
    df = data["flat"]
    term_lower = term.lower()
    mask = (
        df["short_desc"].str.lower().str.contains(term_lower, na=False)
        | df["long_desc"].str.lower().str.contains(term_lower, na=False)
    )
    matches = df[mask].head(max_results)
    return matches[["code", "short_desc", "long_desc"]].to_dict(orient="records")
