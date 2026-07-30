"""Black-box acceptance tests derived from SPEC.md (not implementer tests)."""

import hashlib
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base, get_db
from src.main import app

from .conftest import DEV_DB_PATH

TODO_FIELDS = {"id", "title", "completed"}


def _assert_todo_shape(payload: dict) -> None:
    assert set(payload.keys()) == TODO_FIELDS
    assert isinstance(payload["id"], int)
    assert isinstance(payload["title"], str)
    assert isinstance(payload["completed"], bool)


def _file_fingerprint(path: Path) -> tuple[bool, str | None, int | None]:
    if not path.exists():
        return False, None, None
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return True, digest, path.stat().st_size


def _client_for_sqlite_file(db_path: Path) -> tuple[TestClient, object]:
    """Return a TestClient bound to an on-disk SQLite URL (for restart tests)."""
    url = f"sqlite:///{db_path}"
    engine = create_engine(url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app), engine


# ---------------------------------------------------------------------------
# AC1 / Create — POST /todos
# ---------------------------------------------------------------------------


def test_create_todo_returns_201_with_generated_id_and_completed_false(client):
    response = client.post("/todos", json={"title": "Write tests"})
    assert response.status_code == 201
    data = response.json()
    _assert_todo_shape(data)
    assert data["title"] == "Write tests"
    assert data["completed"] is False
    assert data["id"] >= 1


def test_create_rejects_missing_title_with_422(client):
    assert client.post("/todos", json={}).status_code == 422


def test_create_rejects_empty_title_with_422(client):
    assert client.post("/todos", json={"title": ""}).status_code == 422


def test_create_rejects_whitespace_only_title_with_422(client):
    assert client.post("/todos", json={"title": "   "}).status_code == 422
    assert client.post("/todos", json={"title": "\t\n"}).status_code == 422


def test_create_response_does_not_expose_sqlalchemy_state(client):
    data = client.post("/todos", json={"title": "Clean response"}).json()
    _assert_todo_shape(data)
    for forbidden in ("_sa_instance_state", "metadata", "registry"):
        assert forbidden not in data


# ---------------------------------------------------------------------------
# AC1 / List — GET /todos
# ---------------------------------------------------------------------------


def test_list_returns_200_empty_array_when_no_todos(client):
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == []
    assert isinstance(response.json(), list)


def test_list_returns_todos_in_ascending_id_order(client):
    titles = ["Alpha", "Beta", "Gamma"]
    created_ids = [
        client.post("/todos", json={"title": title}).json()["id"] for title in titles
    ]
    response = client.get("/todos")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3
    assert [todo["id"] for todo in data] == sorted(created_ids)
    assert [todo["id"] for todo in data] == created_ids
    for todo in data:
        _assert_todo_shape(todo)


# ---------------------------------------------------------------------------
# AC1 / Complete — PATCH /todos/{id}/complete
# ---------------------------------------------------------------------------


def test_complete_existing_todo_sets_completed_true(client):
    created = client.post("/todos", json={"title": "Finish me"}).json()
    response = client.patch(f"/todos/{created['id']}/complete")
    assert response.status_code == 200
    data = response.json()
    _assert_todo_shape(data)
    assert data["id"] == created["id"]
    assert data["title"] == "Finish me"
    assert data["completed"] is True


def test_complete_already_completed_todo_is_idempotent(client):
    created = client.post("/todos", json={"title": "Done twice"}).json()
    first = client.patch(f"/todos/{created['id']}/complete")
    second = client.patch(f"/todos/{created['id']}/complete")
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["completed"] is True
    assert second.json()["completed"] is True
    assert second.json()["id"] == created["id"]
    assert second.json()["title"] == "Done twice"


def test_complete_nonexistent_todo_returns_404(client):
    response = client.patch("/todos/99999/complete")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# AC1 / Delete — DELETE /todos/{id}
# ---------------------------------------------------------------------------


def test_delete_existing_todo_returns_204_empty_body(client):
    created = client.post("/todos", json={"title": "Delete me"}).json()
    response = client.delete(f"/todos/{created['id']}")
    assert response.status_code == 204
    assert response.content == b""


def test_delete_nonexistent_todo_returns_404(client):
    assert client.delete("/todos/99999").status_code == 404


def test_delete_removes_todo_from_subsequent_list(client):
    keep = client.post("/todos", json={"title": "Keep"}).json()
    remove = client.post("/todos", json={"title": "Remove"}).json()
    assert client.delete(f"/todos/{remove['id']}").status_code == 204

    listed = client.get("/todos").json()
    assert len(listed) == 1
    assert listed[0]["id"] == keep["id"]
    assert listed[0]["title"] == "Keep"
    assert all(todo["id"] != remove["id"] for todo in listed)


# ---------------------------------------------------------------------------
# AC2 — Persistence across restarts (on-disk SQLite)
# ---------------------------------------------------------------------------


def test_data_persists_across_engine_restart(tmp_path):
    """Simulate an application restart by disposing one engine and opening another."""
    db_path = tmp_path / "acceptance.db"

    client_a, engine_a = _client_for_sqlite_file(db_path)
    with client_a:
        created = client_a.post("/todos", json={"title": "Survive restart"}).json()
        assert created["completed"] is False
        todo_id = created["id"]
    engine_a.dispose()
    app.dependency_overrides.clear()

    client_b, engine_b = _client_for_sqlite_file(db_path)
    with client_b:
        response = client_b.get("/todos")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == todo_id
        assert data[0]["title"] == "Survive restart"
        assert data[0]["completed"] is False

        completed = client_b.patch(f"/todos/{todo_id}/complete")
        assert completed.status_code == 200
        assert completed.json()["completed"] is True
    engine_b.dispose()
    app.dependency_overrides.clear()

    client_c, engine_c = _client_for_sqlite_file(db_path)
    with client_c:
        after_restart = client_c.get("/todos").json()
        assert len(after_restart) == 1
        assert after_restart[0]["completed"] is True
        assert after_restart[0]["id"] == todo_id
    engine_c.dispose()
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# AC2 — Test isolation (must not alter development database)
# ---------------------------------------------------------------------------


def test_acceptance_client_does_not_alter_development_database(client):
    before = _file_fingerprint(DEV_DB_PATH)

    client.post("/todos", json={"title": "Isolation probe"})
    client.get("/todos")
    created = client.post("/todos", json={"title": "To complete"}).json()
    client.patch(f"/todos/{created['id']}/complete")
    client.delete(f"/todos/{created['id']}")

    after = _file_fingerprint(DEV_DB_PATH)
    assert after == before, (
        "Acceptance tests must use an isolated database and must not alter "
        f"the development database at {DEV_DB_PATH}"
    )


def test_file_backed_acceptance_db_does_not_alter_development_database(tmp_path):
    before = _file_fingerprint(DEV_DB_PATH)
    client, engine = _client_for_sqlite_file(tmp_path / "isolated.db")
    try:
        with client:
            client.post("/todos", json={"title": "Temp file db only"})
            client.get("/todos")
    finally:
        engine.dispose()
        app.dependency_overrides.clear()
    after = _file_fingerprint(DEV_DB_PATH)
    assert after == before


# ---------------------------------------------------------------------------
# AC5 / Documentation — README documents required workflow
# ---------------------------------------------------------------------------


def test_readme_documents_prerequisites_install_run_test_and_lint():
    readme = Path("README.md").read_text(encoding="utf-8")
    assert "Python 3.12" in readme or "Python 3.12+" in readme
    assert "pip install -r requirements.txt" in readme
    assert "uvicorn src.main:app" in readme
    assert "pytest" in readme
    assert "ruff check ." in readme


# ---------------------------------------------------------------------------
# AC6 — No unrelated API surface beyond the four specified endpoints
# ---------------------------------------------------------------------------


def test_only_specified_todo_endpoints_are_exposed():
    methods_by_path: dict[str, set[str]] = {}
    for route in app.routes:
        if not hasattr(route, "methods") or not route.path.startswith("/todos"):
            continue
        methods = route.methods - {"HEAD", "OPTIONS"}
        methods_by_path.setdefault(route.path, set()).update(methods)

    expected = {
        "/todos": {"GET", "POST"},
        "/todos/{todo_id}/complete": {"PATCH"},
        "/todos/{todo_id}": {"DELETE"},
    }
    assert methods_by_path == expected
