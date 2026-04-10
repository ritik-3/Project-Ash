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
    api_server._store = api_server._orchestrator.sqlite_store
    api_server._queue.store = api_server._store
    api_server._scheduler.store = api_server._store
    api_server._worker.store = api_server._store
    api_server._worker.queue = api_server._queue
    api_server._worker.orchestrator = api_server._orchestrator
    return TestClient(api_server.app)


def test_jobs_and_approvals_flow(client: TestClient) -> None:
    created = client.post("/jobs", json={"owner_user_id": "u1", "intent_text": "open github.com"})
    assert created.status_code == 200
    job_id = created.json()["job_id"]

    listed = client.get("/jobs")
    assert listed.status_code == 200
    assert any(item["job_id"] == job_id for item in listed.json()["items"])

    canceled = client.post(f"/jobs/{job_id}/cancel")
    assert canceled.status_code == 200
    assert canceled.json()["status"] == "canceled"


def test_worker_transitions_job_to_waiting_approval_then_executes(client: TestClient) -> None:
    created = client.post("/jobs", json={"owner_user_id": "u1", "intent_text": "draft follow up email"})
    assert created.status_code == 200
    job_id = created.json()["job_id"]

    first_run = client.post("/jobs/run-once")
    assert first_run.status_code == 200

    job_after_first_run = client.get(f"/jobs/{job_id}")
    assert job_after_first_run.status_code == 200
    assert job_after_first_run.json()["status"] == "waiting_approval"

    pending = client.get("/approvals/pending")
    assert pending.status_code == 200
    assert any(item["job_id"] == job_id for item in pending.json()["items"])

    approved = client.post(f"/approvals/{job_id}/approve", json={"decided_by": "tester"})
    assert approved.status_code == 200

    second_run = client.post("/jobs/run-once")
    assert second_run.status_code == 200
    assert second_run.json()["executed"] is True

    job_after_second_run = client.get(f"/jobs/{job_id}")
    assert job_after_second_run.status_code == 200
    assert job_after_second_run.json()["status"] == "completed"
