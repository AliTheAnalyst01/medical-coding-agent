from app.knowledge_base.hcpcs_loader import load_hcpcs


def _resolve_columns(df):
    code_col = "HCPCS" if "HCPCS" in df.columns else df.columns[1]
    if "DESCRIPTION" in df.columns:
        desc_col = "DESCRIPTION"
    elif "LONG_DESCRIPTION" in df.columns:
        desc_col = "LONG_DESCRIPTION"
    else:
        desc_col = df.columns[2]
    return code_col, desc_col


def search_hcpcs(term: str, max_results: int = 15) -> list[dict]:
    data = load_hcpcs()
    df = data["codes"]
    code_col, desc_col = _resolve_columns(df)
    term_lower = term.lower()
    mask = df[desc_col].str.lower().str.contains(term_lower, na=False)
    matches = df[mask].head(max_results)
    return (
        matches[[code_col, desc_col]]
        .rename(columns={code_col: "code", desc_col: "description"})
        .to_dict(orient="records")
    )


def get_hcpcs_details(code: str) -> dict:
    data = load_hcpcs()
    df = data["codes"]
    code_col, _ = _resolve_columns(df)
    match = df[df[code_col] == code]
    if match.empty:
        return {"error": f"Code {code} not found"}
    return match.iloc[0].to_dict()


def get_betos_category(betos_code: str) -> str:
    data = load_hcpcs()
    df = data["betos"]
    if df.empty:
        return "BETOS reference not available"
    col = df.columns[0]
    match = df[df[col] == betos_code]
    if match.empty:
        return f"BETOS code {betos_code} not found"
    return str(match.iloc[0].to_dict().get(df.columns[1], ""))
