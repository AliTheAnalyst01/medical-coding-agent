from functools import lru_cache
from app.config import DATA_DIR

@lru_cache(maxsize=1)
def load_guidelines() -> str:
    rules_path = DATA_DIR / "06_Official_Guidelines" / "FY2026_ICD10CM_Guidelines_STRUCTURE_AND_KEY_RULES.txt"
    extracted_path = DATA_DIR / "06_Official_Guidelines" / "FY2026_ICD10CM_Official_Coding_Guidelines_EXTRACTED_TEXT.md"

    parts = []
    for path in [rules_path, extracted_path]:
        with open(path, encoding="utf-8") as f:
            parts.append(f.read())

    return "\n\n---\n\n".join(parts)
