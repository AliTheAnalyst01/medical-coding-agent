import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.tracer import Tracer
from app.tools.phi_scrubber import scrub_phi
from app.agents.icd_cm_worker import run_icd_cm_worker
from app.agents.icd_pcs_worker import run_icd_pcs_worker
from app.agents.hcpcs_worker import run_hcpcs_worker
from app.agents.coordinator import run_coordinator
from app.agents.validator import run_validator
from app.knowledge_base.icd_index import load_icd_index
from app.knowledge_base.graph_loader import load_graph
from app.knowledge_base.guidelines_loader import load_guidelines
from app.knowledge_base.pcs_loader import load_pcs
from app.knowledge_base.hcpcs_loader import load_hcpcs


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading ICD-10-CM index...")
    load_icd_index()
    print("Loading graph and relationships...")
    load_graph()
    print("Loading guidelines...")
    load_guidelines()
    print("Loading PCS data...")
    load_pcs()
    print("Loading HCPCS data...")
    load_hcpcs()
    print("All knowledge bases loaded. Ready.")
    yield


app = FastAPI(title="Medical Coding AI", lifespan=lifespan)


class NoteRequest(BaseModel):
    note: str


class CodeResponse(BaseModel):
    request_id: str
    scrubbed_note: str
    codes: list[dict]
    validation_summary: dict
    trace_steps: list[dict]


@app.post("/code", response_model=CodeResponse)
async def code_note(request: NoteRequest):
    if not request.note.strip():
        raise HTTPException(status_code=400, detail="Note cannot be empty")

    request_id = uuid.uuid4().hex[:8]
    tracer = Tracer(request_id)

    # Step 1: PHI scrubbing
    scrubbed = scrub_phi(request.note)

    # Step 2: Coordinator extracts entities
    entities = run_coordinator(note=scrubbed, tracer=tracer)

    # Step 3: Run workers per category
    icd_codes: list[dict] = []
    pcs_codes: list[dict] = []
    hcpcs_codes: list[dict] = []

    if entities["diagnoses"]:
        icd_codes = run_icd_cm_worker(diagnoses=entities["diagnoses"], tracer=tracer)
        for c in icd_codes:
            c["system"] = "ICD-10-CM"

    if entities["procedures"]:
        pcs_codes = run_icd_pcs_worker(procedures=entities["procedures"], tracer=tracer)
        for c in pcs_codes:
            c["system"] = "ICD-10-PCS"

    if entities["drugs_supplies"]:
        hcpcs_codes = run_hcpcs_worker(terms=entities["drugs_supplies"], tracer=tracer)
        for c in hcpcs_codes:
            c["system"] = "HCPCS"

    all_proposed = icd_codes + pcs_codes + hcpcs_codes

    # Step 4: Validation (ICD-10-CM only — graph covers ICD)
    validation = run_validator(proposed_codes=icd_codes, tracer=tracer)
    accepted_icd = validation.get("accepted", [])
    rejected_icd = validation.get("rejected", [])

    for c in accepted_icd:
        c["status"] = "accepted"
    for c in rejected_icd:
        c["status"] = "rejected"
    for c in pcs_codes + hcpcs_codes:
        c["status"] = "accepted"

    all_codes = accepted_icd + rejected_icd + pcs_codes + hcpcs_codes
    accepted_all = [c for c in all_codes if c.get("status") == "accepted"]
    rejected_all = [c for c in all_codes if c.get("status") == "rejected"]

    tracer.save(
        input_note=request.note,
        final_codes=accepted_all,
        rejected_codes=rejected_all,
        tokens_used=0,
    )

    return CodeResponse(
        request_id=request_id,
        scrubbed_note=scrubbed,
        codes=all_codes,
        validation_summary={
            "total_proposed": len(all_proposed),
            "accepted": len(accepted_all),
            "rejected": len(rejected_all),
            "rejection_reasons": [f"{r['code']}: {r.get('reason', '')}" for r in rejected_all],
        },
        trace_steps=tracer.steps,
    )


@app.get("/health")
async def health():
    return {"status": "ok"}
