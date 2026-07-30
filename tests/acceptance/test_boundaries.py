"""Boundary and contract-shape cases beyond the SPEC minimum matrix."""

import pytest

from .test_acceptance import TODO_FIELDS, _assert_todo_shape

# ---------------------------------------------------------------------------
# title boundaries
# ---------------------------------------------------------------------------


def test_create_accepts_minimum_length_title(client):
    response = client.post("/todos", json={"title": "a"})
    assert response.status_code == 201
    data = response.json()
    _assert_todo_shape(data)
    assert data["title"] == "a"
    assert data["completed"] is False


@pytest.mark.parametrize(
    "title",
    [None, 123, [], {}, True],
)
def test_create_rejects_non_string_title(client, title):
    response = client.post("/todos", json={"title": title})
    assert response.status_code == 422
    body = response.json()
    assert "detail" in body


def test_create_ignores_extra_completed_field_and_defaults_false(client):
    response = client.post(
        "/todos",
        json={"title": "Ignore completed", "completed": True},
    )
    assert response.status_code == 201
    data = response.json()
    _assert_todo_shape(data)
    assert data["title"] == "Ignore completed"
    assert data["completed"] is False


# ---------------------------------------------------------------------------
# path id boundaries
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("todo_id", ["abc", "1.5", "null"])
def test_complete_rejects_non_integer_path_id(client, todo_id):
    response = client.patch(f"/todos/{todo_id}/complete")
    assert response.status_code == 422
    assert "detail" in response.json()


@pytest.mark.parametrize("todo_id", ["abc", "1.5", "null"])
def test_delete_rejects_non_integer_path_id(client, todo_id):
    response = client.delete(f"/todos/{todo_id}")
    assert response.status_code == 422
    assert "detail" in response.json()


@pytest.mark.parametrize("todo_id", [0, -1, 9_999_999_999])
def test_complete_nonexistent_integer_ids_return_404(client, todo_id):
    response = client.patch(f"/todos/{todo_id}/complete")
    assert response.status_code == 404
    assert "detail" in response.json()


@pytest.mark.parametrize("todo_id", [0, -1, 9_999_999_999])
def test_delete_nonexistent_integer_ids_return_404(client, todo_id):
    response = client.delete(f"/todos/{todo_id}")
    assert response.status_code == 404
    assert "detail" in response.json()


# ---------------------------------------------------------------------------
# HTTP / payload boundaries
# ---------------------------------------------------------------------------


def test_create_rejects_empty_body(client):
    response = client.post("/todos", content=b"")
    assert response.status_code == 422
    assert "detail" in response.json()


def test_create_rejects_non_json_body(client):
    response = client.post(
        "/todos",
        content=b"title=not-json",
        headers={"Content-Type": "text/plain"},
    )
    assert response.status_code == 422
    assert "detail" in response.json()


def test_create_rejects_malformed_json(client):
    response = client.post(
        "/todos",
        content=b"{not-json",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422
    assert "detail" in response.json()


# ---------------------------------------------------------------------------
# light contract shape
# ---------------------------------------------------------------------------


def test_list_items_match_todo_contract_shape(client):
    client.post("/todos", json={"title": "One"})
    client.post("/todos", json={"title": "Two"})
    response = client.get("/todos")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    for todo in data:
        _assert_todo_shape(todo)
        assert set(todo.keys()) == TODO_FIELDS


def test_error_responses_include_json_detail(client):
    missing = client.post("/todos", json={})
    assert missing.status_code == 422
    assert "detail" in missing.json()

    not_found = client.patch("/todos/99999/complete")
    assert not_found.status_code == 404
    assert "detail" in not_found.json()
