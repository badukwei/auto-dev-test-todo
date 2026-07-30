"""Process-level end-to-end tests against a real uvicorn server."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest

from .conftest import start_e2e_server, stop_e2e_server

pytestmark = pytest.mark.e2e


def test_todo_lifecycle_over_real_http(e2e_client: httpx.Client) -> None:
    created = e2e_client.post("/todos", json={"title": "E2E task"})
    assert created.status_code == 201
    todo = created.json()
    assert todo["title"] == "E2E task"
    assert todo["completed"] is False
    todo_id = todo["id"]

    listed = e2e_client.get("/todos")
    assert listed.status_code == 200
    assert any(item["id"] == todo_id for item in listed.json())

    completed = e2e_client.patch(f"/todos/{todo_id}/complete")
    assert completed.status_code == 200
    assert completed.json()["completed"] is True

    completed_again = e2e_client.patch(f"/todos/{todo_id}/complete")
    assert completed_again.status_code == 200
    assert completed_again.json()["completed"] is True

    deleted = e2e_client.delete(f"/todos/{todo_id}")
    assert deleted.status_code == 204
    assert deleted.content == b""

    after_delete = e2e_client.get("/todos")
    assert after_delete.status_code == 200
    assert after_delete.json() == []


def test_data_persists_across_process_restart(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    workdir = tmp_path / "persist"
    workdir.mkdir()
    db_path = workdir / "todos.db"

    process_a, base_url_a = start_e2e_server(workdir, repo_root)
    try:
        with httpx.Client(base_url=base_url_a, timeout=5.0) as client:
            created = client.post("/todos", json={"title": "Survive process death"})
            assert created.status_code == 201
            todo = created.json()
            todo_id = todo["id"]
            assert todo["completed"] is False
    finally:
        stop_e2e_server(process_a)

    assert db_path.is_file()

    process_b, base_url_b = start_e2e_server(workdir, repo_root)
    try:
        with httpx.Client(base_url=base_url_b, timeout=5.0) as client:
            listed = client.get("/todos")
            assert listed.status_code == 200
            data = listed.json()
            assert len(data) == 1
            assert data[0]["id"] == todo_id
            assert data[0]["title"] == "Survive process death"
            assert data[0]["completed"] is False
    finally:
        stop_e2e_server(process_b)
