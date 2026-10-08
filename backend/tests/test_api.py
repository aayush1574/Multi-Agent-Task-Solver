from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_health() -> None:
    assert client.get("/health").json() == {"status": "ok"}


def test_objective_validation() -> None:
    response = client.post("/api/runs", json={"objective": "too short"})
    assert response.status_code == 422


def test_create_run() -> None:
    response = client.post("/api/runs", json={"objective": "Analyze quarterly sales performance and propose actions."})
    assert response.status_code == 202
    assert response.json()["status"] in {"queued", "running"}


def test_missing_run() -> None:
    response = client.get("/api/runs/R-NOTFOUND")
    assert response.status_code == 404


def test_serverless_run_completes_before_response(monkeypatch) -> None:
    monkeypatch.setenv("VERCEL", "1")
    response = client.post(
        "/api/runs",
        json={"objective": "Create a concise market validation plan for a new product."},
    )
    assert response.status_code == 202
    assert response.json()["status"] == "completed"
