# Medical Coding AI

Converts clinical notes into validated **ICD-10-CM**, **ICD-10-PCS**, and **HCPCS** billing codes via a 5-agent AI pipeline with full PHI scrubbing, graph-based validation, and FY2026 coding-guideline enforcement.

## Architecture

```
Clinical note
   |
   v
Presidio PHI scrubber (spaCy en_core_web_sm)
   |
   v
Coordinator Agent  (entity extraction & 3-way routing)
   |--> diagnoses        --> ICD-CM Worker   --> ICD-10-CM codes
   |--> procedures       --> ICD-PCS Worker  --> ICD-10-PCS codes
   |--> drugs/supplies   --> HCPCS Worker    --> HCPCS codes
                                  |
                                  v
                         Validation Agent
                         - Excludes1 graph checks
                         - Specificity (leaf-only)
                         - Etiology sequencing
                         - Required additional codes
                         - FY2026 combination-code rules (HTN+HF, HTN+CKD, etc.)
                         - QUERY_REQUIRED flagging
                                  |
                                  v
                  accepted / rejected / query_required + full trace
```

Per-request trace JSON is saved under `traces/` for full observability.

## Setup

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
cp .env.example .env   # add your OPENROUTER/ANTHROPIC_API_KEY
```

## Run

Terminal 1 — FastAPI:
```bash
uvicorn app.main:app --reload --port 8000
```

Terminal 2 — Streamlit UI:
```bash
streamlit run ui/streamlit_app.py
```

Open http://localhost:8501.

## Endpoints

- `POST /code` — body: `{"note": "..."}` → returns codes, validation summary, trace steps
- `GET /health` — liveness check

## Data

Knowledge base lives at `D:/medical_coding_knowledge_base_1/data/`:
- `01_ICD-10-CM` — codes + chapter index + Excludes1/etiology graph
- `02_ICD-10-PCS` — index, tables, flat order file (~73K codes)
- `03_HCPCS_Level_II` — HCPCS Q4 codes + BETOS reference
- `06_Official_Guidelines` — FY2026 coding guidelines (loaded into validator prompt)

All sources load into memory at startup (~150 MB).

## Tests

```bash
pytest tests/test_loaders.py tests/test_tools.py -v          # offline unit tests
pytest tests/test_agents.py -v                                # agent tests (calls LLM)
pytest tests/test_integration.py -v                           # needs server running
pytest                                                        # everything
```

## Phases

| Phase | Tasks | Deliverable |
|---|---|---|
| 1 | 1-13 | Diagnosis pipeline: paste note → ICD-10-CM codes + trace panel |
| 2 | 14-18 | Full pipeline: 5 agents, all 3 code systems |
| 3 | 19-21 | FY2026 guideline rules, QUERY_REQUIRED detection, integration tests |
