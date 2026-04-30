import pandas as pd
from functools import lru_cache
from app.config import DATA_DIR


@lru_cache(maxsize=1)
def load_hcpcs() -> dict:
    codes_path = DATA_DIR / "03_HCPCS_Level_II" / "hcpcs_2019_Q4_all_codes.csv"
    betos_path = DATA_DIR / "03_HCPCS_Level_II" / "BETOS_TB_reference_table.csv"

    codes_df = pd.read_csv(codes_path, dtype=str).fillna("")
    betos_df = pd.read_csv(betos_path, dtype=str).fillna("")

    return {"codes": codes_df, "betos": betos_df}
