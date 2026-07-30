# AGENTS.md

## Project purpose

This is a minimal Todo REST API used to evaluate an AI coding agent. Read
`SPEC.md` completely before planning or changing code.

## Required stack

- Python 3.12
- FastAPI
- SQLAlchemy
- SQLite
- pytest
- Ruff

Do not replace these technologies or add major frameworks without approval.

## Project structure

- `src/` — application code
- `tests/` — automated tests
- `SPEC.md` — product requirements and acceptance criteria
- `README.md` — human-facing setup and usage documentation

Keep the structure small. Add modules only when they create a clear separation
of responsibilities.

## Required commands

The finished repository must support:

```bash
python -m pip install -r requirements.txt
uvicorn src.main:app --reload
pytest
ruff check .
```

## Development rules

- Implement only the behavior described in `SPEC.md`.
- Do not add authentication, Docker, a frontend, cloud services, or deployment
  configuration.
- Do not perform unrelated refactors or add speculative abstractions.
- Validate all external input.
- Use appropriate HTTP status codes and consistent JSON responses.
- Add automated tests for every endpoint and important error case.
- Keep tests isolated; one test must not depend on data created by another.
- Update `README.md` so its instructions match the actual implementation.
- Do not mark the task complete unless the full test suite and Ruff checks pass.

## Delivery requirements

At completion:

1. Run the full test suite.
2. Run the lint check.
3. Report the exact commands and results.
4. Summarize the files changed and key implementation choices.
5. State any remaining limitations or assumptions.
