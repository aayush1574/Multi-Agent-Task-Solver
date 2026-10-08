import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .models import ObjectiveRequest, RunResponse
from .orchestrator import Orchestrator

orchestrator = Orchestrator()


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    for task in list(orchestrator.tasks.values()):
        task.cancel()


app = FastAPI(title="Relay Multi-Agent API", version="1.0.0", lifespan=lifespan)
allowed_origins = [value.strip() for value in os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
).split(",") if value.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_error(_: Request, __: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": "Unexpected server error"})


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/runs", response_model=RunResponse, status_code=202)
async def create_run(request: ObjectiveRequest) -> RunResponse:
    run = orchestrator.create(request)
    # Serverless platforms may freeze the process as soon as a response is
    # returned, so finish short demo runs inside the request on Vercel.
    if os.getenv("VERCEL"):
        await orchestrator.execute(run.id, request)
    else:
        orchestrator.start(run.id, request)
    return run


@app.get("/api/runs/{run_id}", response_model=RunResponse)
async def get_run(run_id: str) -> RunResponse:
    run = orchestrator.runs.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


frontend_dir = Path(__file__).resolve().parents[2] / "dist"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
