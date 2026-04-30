import json
import pandas as pd
from functools import lru_cache
from app.config import DATA_DIR


@lru_cache(maxsize=1)
def load_pcs() -> dict:
    index_path = DATA_DIR / "02_ICD-10-PCS" / "icd10pcs_index_2021.json"
    tables_path = DATA_DIR / "02_ICD-10-PCS" / "icd10pcs_tables_2021.json"
    flat_path = DATA_DIR / "02_ICD-10-PCS" / "icd10pcs_order_2014.tsv"

    with open(index_path, encoding="utf-8") as f:
        index = json.load(f)

    with open(tables_path, encoding="utf-8") as f:
        tables = json.load(f)

    flat_df = pd.read_csv(
        flat_path,
        sep="\t",
        header=None,
        names=["order", "code", "billable", "short_desc", "long_desc"],
        dtype=str,
    ).fillna("")

    return {"index": index, "tables": tables, "flat": flat_df}
