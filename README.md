# Relay — Multi-Agent Task Solver

Relay turns a complex objective into a plan, sends the work through four specialist agents, and synthesizes an actionable result. The included browser demo works with no credentials; the FastAPI service provides the backend contract for a real deployment.

## Objective

Build a collaborative system that decomposes broad goals, coordinates specialized agents, lets them use SQL and REST tools, tracks progress, and produces one concise decision brief.

## Requirements

- Python 3.11+
- FastAPI and Uvicorn
- A modern browser
- Optional: an LLM API key and an external SQL/HTTP data source

## Run the interface

Serve `dist` with any static server:

```powershell
python -m http.server 3000 --directory dist
```

Open `http://localhost:3000`.

## Run the API

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs are available at `http://127.0.0.1:8000/docs`.

## Architecture

1. **Planner** decomposes the objective.
2. **Researcher** gathers evidence through enabled tools.
3. **Analyst** ranks opportunities and risks.
4. **Synthesizer** produces the final decision brief.

The current orchestrator is deterministic so the repository runs immediately. Replace the worker bodies in `backend/app/orchestrator.py` with your preferred model and tool adapters for production.

The frontend automatically uses the API when both are served together. If the API is unavailable, it switches to its credential-free local demo, which is also what powers the static hosted preview.

## Production container

Build and run the complete interface and API as one service:

```powershell
docker build -t relay .
docker run --rm -p 8000:8000 --env-file .env relay
```

Open `http://localhost:8000`. The container runs as a non-root user and exposes a health check at `/health`.

For a production LLM integration, replace the deterministic worker implementations, store provider keys as deployment secrets, use a durable run store such as PostgreSQL, and move long-running work to a queue-backed worker.

## Test

```powershell
cd backend
pytest
```
