import json
from datetime import datetime
from typing import Any
from app.config import TRACES_DIR

TRACES_DIR = TRACES_DIR  # module-level name so tests can monkeypatch it

class Tracer:
    def __init__(self, request_id: str):
        self.request_id = request_id
        self.steps: list[dict] = []
        self._started_at = datetime.utcnow().isoformat()

    def record(
        self,
        agent: str,
        tool: str,
        input_data: Any,
        output_data: Any,
        duration_ms: int,
    ) -> dict:
        step = {
            "agent": agent,
            "tool": tool,
            "input": input_data,
            "output": output_data,
            "duration_ms": duration_ms,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.steps.append(step)
        return step

    def save(
        self,
        input_note: str,
        final_codes: list[dict],
        rejected_codes: list[dict],
        tokens_used: int,
    ) -> str:
        total_ms = sum(s["duration_ms"] for s in self.steps)
        payload = {
            "request_id": self.request_id,
            "timestamp": self._started_at,
            "input_note": input_note,
            "steps": self.steps,
            "final_codes": final_codes,
            "rejected_codes": rejected_codes,
            "total_duration_ms": total_ms,
            "tokens_used": tokens_used,
        }
        TRACES_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        filename = TRACES_DIR / f"{ts}_req_{self.request_id}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, default=str)
        return str(filename)
