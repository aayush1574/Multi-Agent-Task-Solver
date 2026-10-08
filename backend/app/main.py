import asyncio

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import ObjectiveRequest, RunResponse
from .orchestrator import Orchestrator

app = FastAPI(title="Relay Multi-Agent API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
orchestrator = Orchestrator()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/runs", response_model=RunResponse, status_code=202)
async def create_run(request: ObjectiveRequest) -> RunResponse:
    run = orchestrator.create(request)
    asyncio.create_task(orchestrator.execute(run.id, request))
    return run


@app.get("/api/runs/{run_id}", response_model=RunResponse)
async def get_run(run_id: str) -> RunResponse:
    run = orchestrator.runs.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
