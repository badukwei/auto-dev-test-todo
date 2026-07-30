# Cursor Todo API Evaluation

This repository is a small, from-scratch project for evaluating Cursor Agents
on a well-scoped software engineering task.

The implementation is intentionally absent. Cursor should read `AGENTS.md` and
`SPEC.md`, propose a plan, and then build the application.

## Evaluation goal

The project is designed to test whether Cursor can:

- turn a written specification into a working application;
- choose a simple, maintainable project structure;
- implement and test a REST API;
- document setup and usage accurately; and
- verify its own work before delivery;
- delegate work across implementation, review, and verification subagents;
  and
- integrate independent results into one verified delivery.

## Required technology

- Python 3.12
- FastAPI
- SQLAlchemy
- SQLite
- pytest
- Ruff

## Instructions for the evaluator

1. Connect this repository to Cursor and open it in the Agents Window.
2. Start an Agent session locally or in Cursor Cloud.
3. Run `/spec-driven-delivery`.
4. Ask Cursor to read the required documents and complete the Todo API.
5. Review any material questions or blockers raised by the Agent.
6. Assess the result using the acceptance criteria in `SPEC.md`.

The reusable workflow is defined in
`.cursor/commands/spec-driven-delivery.md`. Specialized implementation,
review, and verification roles are defined under `.cursor/agents/`.

Do not add starter application code before the evaluation; creating that code
is part of the task.

## Expected commands after implementation

Cursor must make these commands valid and update this README if the final setup
requires any additional steps:

```bash
python -m pip install -r requirements.txt
uvicorn src.main:app --reload
pytest
ruff check .
```
