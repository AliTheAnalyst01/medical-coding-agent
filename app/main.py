import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.tracer import Tracer
from app.tools.phi_scrubber import scrub_phi
from app.agents.icd_cm_worker import run_icd_cm_worker
from app.agents.validator import run_validator
from app.knowledge_base.icd_index import load_icd_index
from app.knowledge_base.graph_loader import load_graph
from app.knowledge_base.guidelines_loader import load_guidelines


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading ICD-10-CM index...")
    load_icd_index()
    print("Loading graph and relationships...")
    load_graph()
    print("Loading guidelines...")
    load_guidelines()
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

    # Step 2: ICD-10-CM worker
    icd_codes = run_icd_cm_worker(diagnoses=[scrubbed], tracer=tracer)
    for c in icd_codes:
        c["system"] = "ICD-10-CM"

    # Step 3: Validation
    validation = run_validator(proposed_codes=icd_codes, tracer=tracer)
    accepted = validation.get("accepted", [])
    rejected = validation.get("rejected", [])
    for c in accepted:
        c["status"] = "accepted"
    for c in rejected:
        c["status"] = "rejected"

    all_codes = accepted + rejected

    # Step 4: Save trace
    tracer.save(
        input_note=request.note,
        final_codes=accepted,
        rejected_codes=rejected,
        tokens_used=0,
    )

    return CodeResponse(
        request_id=request_id,
        scrubbed_note=scrubbed,
        codes=all_codes,
        validation_summary={
            "total_proposed": len(icd_codes),
            "accepted": len(accepted),
            "rejected": len(rejected),
            "rejection_reasons": [f"{r['code']}: {r.get('reason', '')}" for r in rejected],
        },
        trace_steps=tracer.steps,
    )


@app.get("/health")
async def health():
    return {"status": "ok"}
