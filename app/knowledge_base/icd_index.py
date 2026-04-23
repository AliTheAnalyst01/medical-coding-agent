import json
from functools import lru_cache
from app.config import DATA_DIR


@lru_cache(maxsize=1)
def load_icd_index() -> dict:
    """Load ICD-10-CM knowledge base indices.

    Returns a dictionary with:
    - complete: Full ICD-10-CM code tree (all 98k+ codes)
    - leaf_codes: Set of billable leaf codes for O(1) lookup
    - chapter_index: Map of chapter numbers to lists of codes in that chapter

    The @lru_cache decorator ensures files are loaded only once, regardless
    of how many times this function is called.

    Returns:
        dict: Knowledge base with complete codes, leaf codes set, and chapter index
    """
    complete_path = DATA_DIR / "01_ICD-10-CM" / "icd10cm_complete.json"
    leaf_path = DATA_DIR / "01_ICD-10-CM" / "icd10cm_leaf_billable_only.json"
    chapter_path = DATA_DIR / "01_ICD-10-CM" / "icd10cm_chapter_index.json"

    # Load complete ICD-10-CM codes dictionary
    with open(complete_path, encoding="utf-8") as f:
        complete = json.load(f)

    # Load leaf/billable codes and convert to set for O(1) lookup
    with open(leaf_path, encoding="utf-8") as f:
        leaf_raw = json.load(f)
    leaf_codes = set(leaf_raw.keys())

    # Load chapter index mapping
    with open(chapter_path, encoding="utf-8") as f:
        chapter_index = json.load(f)

    return {
        "complete": complete,
        "leaf_codes": leaf_codes,
        "chapter_index": chapter_index,
    }
