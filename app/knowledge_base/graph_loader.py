import json
import pickle
from functools import lru_cache
from app.config import DATA_DIR

@lru_cache(maxsize=1)
def load_graph() -> dict:
    graph_path = DATA_DIR / "07_Graph_Data" / "icd10cm_graph.pickle"
    rels_path = DATA_DIR / "08_Code_Pairings" / "icd10cm_code_relationships.json"

    with open(graph_path, "rb") as f:
        G = pickle.load(f)

    with open(rels_path, encoding="utf-8") as f:
        relationships = json.load(f)

    excludes1_set = frozenset(
        pair
        for r in relationships.get("mutual_exclusions", [])
        for pair in ((r["code_1"], r["code_2"]), (r["code_2"], r["code_1"]))
    )

    etiology_pairs = {
        r["code_1"]: r["code_2"]
        for r in relationships.get("etiology_manifestation_pairs", [])
    }

    return {
        "graph": G,
        "relationships": relationships,
        "excludes1_set": excludes1_set,
        "etiology_pairs": etiology_pairs,
    }
