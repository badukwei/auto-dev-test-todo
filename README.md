# Todo REST API

Minimal Todo REST API built with FastAPI, SQLAlchemy, and SQLite.

## Prerequisites

- Python 3.12+

## Installation

```bash
python -m pip install -r requirements.txt
```

## Run the API

```bash
uvicorn src.main:app --reload
```

The API listens on `http://127.0.0.1:8000`. Interactive docs are available at
[`/docs`](http://127.0.0.1:8000/docs).

Data is stored in a local SQLite file (`todos.db`) and persists across restarts.

## Example requests

```bash
# Create a todo
curl -s -X POST http://127.0.0.1:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Write tests"}'

# List todos
curl -s http://127.0.0.1:8000/todos

# Mark a todo complete
curl -s -X PATCH http://127.0.0.1:8000/todos/1/complete

# Delete a todo
curl -s -o /dev/null -w "%{http_code}\n" -X DELETE http://127.0.0.1:8000/todos/1
```

## Tests and lint

```bash
pytest
ruff check .
```

### Test layers

| Layer | Location | What it covers |
| --- | --- | --- |
| Implementation | `tests/test_todos.py` | Endpoint happy paths and SPEC error cases via TestClient |
| Acceptance | `tests/acceptance/` | SPEC black-box checks, boundary inputs, light response contracts |
| E2E | `tests/e2e/` | Real `uvicorn` process, real HTTP, file SQLite lifecycle and restart |

`pytest` runs all layers by default. To run only process-level e2e tests:

```bash
pytest -m e2e
```

To skip e2e (faster local loops):

```bash
pytest -m "not e2e"
```
