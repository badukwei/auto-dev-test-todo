def test_create_todo(client):
    response = client.post("/todos", json={"title": "Write tests"})
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["title"] == "Write tests"
    assert data["completed"] is False


def test_create_todo_strips_title(client):
    response = client.post("/todos", json={"title": "  Buy milk  "})
    assert response.status_code == 201
    assert response.json()["title"] == "Buy milk"


def test_reject_missing_title(client):
    response = client.post("/todos", json={})
    assert response.status_code == 422


def test_reject_empty_title(client):
    response = client.post("/todos", json={"title": ""})
    assert response.status_code == 422


def test_reject_whitespace_only_title(client):
    response = client.post("/todos", json={"title": "   "})
    assert response.status_code == 422


def test_list_todos_empty(client):
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == []


def test_list_todos_multiple_ascending_id(client):
    first = client.post("/todos", json={"title": "First"}).json()
    second = client.post("/todos", json={"title": "Second"}).json()
    third = client.post("/todos", json={"title": "Third"}).json()

    response = client.get("/todos")
    assert response.status_code == 200
    data = response.json()
    assert [todo["id"] for todo in data] == [first["id"], second["id"], third["id"]]
    assert [todo["title"] for todo in data] == ["First", "Second", "Third"]


def test_complete_todo(client):
    created = client.post("/todos", json={"title": "Finish me"}).json()
    response = client.patch(f"/todos/{created['id']}/complete")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created["id"]
    assert data["title"] == "Finish me"
    assert data["completed"] is True


def test_complete_already_completed_todo(client):
    created = client.post("/todos", json={"title": "Already done"}).json()
    client.patch(f"/todos/{created['id']}/complete")
    response = client.patch(f"/todos/{created['id']}/complete")
    assert response.status_code == 200
    assert response.json()["completed"] is True


def test_complete_nonexistent_todo(client):
    response = client.patch("/todos/99999/complete")
    assert response.status_code == 404


def test_delete_todo(client):
    created = client.post("/todos", json={"title": "Delete me"}).json()
    response = client.delete(f"/todos/{created['id']}")
    assert response.status_code == 204
    assert response.content == b""


def test_delete_nonexistent_todo(client):
    response = client.delete("/todos/99999")
    assert response.status_code == 404


def test_delete_affects_list(client):
    keep = client.post("/todos", json={"title": "Keep"}).json()
    remove = client.post("/todos", json={"title": "Remove"}).json()

    delete_response = client.delete(f"/todos/{remove['id']}")
    assert delete_response.status_code == 204

    list_response = client.get("/todos")
    assert list_response.status_code == 200
    data = list_response.json()
    assert len(data) == 1
    assert data[0]["id"] == keep["id"]
    assert data[0]["title"] == "Keep"
