import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

import project_ash.api.server as api_server
from project_ash.orchestrator import AssistantOrchestrator


@pytest.fixture
def client(tmp_path):
    api_server._orchestrator = AssistantOrchestrator(
        log_dir=tmp_path,
        sqlite_db_path=tmp_path / "ash_memory.db",
        ollama_model=None,
    )
    return TestClient(api_server.app)


def test_status_and_plan(client: TestClient) -> None:
    status = client.get("/status")
    assert status.status_code == 200
    assert status.json()["status"] == "ready"
    assert "runtime" in status.json()

    plan = client.post("/plan", json={"text": "open github.com"})
    assert plan.status_code == 200
    assert plan.json()["steps"][0]["action"] == "open_website"


def test_execute_and_history(client: TestClient, monkeypatch) -> None:
    monkeypatch.setattr(
        "project_ash.executor.open_website_with_playwright",
        lambda url: f"Opened website with Playwright: {url}",
    )

    executed = client.post("/execute", json={"text": "open github.com", "confirmed": True})
    assert executed.status_code == 200
    assert executed.json()["success"] is True

    history = client.post("/history", json={"query": "github", "limit": 5})
    assert history.status_code == 200
    assert len(history.json()["items"]) >= 1


def test_execute_confirmation_gate(client: TestClient) -> None:
    blocked = client.post("/execute", json={"text": "draft follow up email", "confirmed": False})
    assert blocked.status_code == 200
    assert blocked.json()["success"] is False
    assert "Confirmation required" in blocked.json()["summary"]


def test_execute_with_plan_payload(client: TestClient) -> None:
    plan = client.post("/plan", json={"text": "open github.com"}).json()
    executed = client.post("/execute", json={"plan": plan, "confirmed": True})
    assert executed.status_code == 200
    assert "success" in executed.json()
