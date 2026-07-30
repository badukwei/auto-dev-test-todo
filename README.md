# Devin Todo API Evaluation

This repository is a small, from-scratch project for evaluating Devin on a
well-scoped software engineering task.

The implementation is intentionally absent. Devin should read `AGENTS.md` and
`SPEC.md`, propose a plan, and then build the application.

## Evaluation goal

The project is designed to test whether Devin can:

- turn a written specification into a working application;
- choose a simple, maintainable project structure;
- implement and test a REST API;
- document setup and usage accurately; and
- verify its own work before delivery.

## Required technology

- Python 3.12
- FastAPI
- SQLAlchemy
- SQLite
- pytest
- Ruff

## Instructions for the evaluator

1. Give Devin access to this repository.
2. Start in Ask Mode and ask Devin to read `AGENTS.md` and `SPEC.md`.
3. Review its proposed implementation plan.
4. Switch to Agent Mode and ask it to implement the specification.
5. Assess the result using the acceptance criteria in `SPEC.md`.

Do not add starter application code before the evaluation; creating that code
is part of the task.

## Expected commands after implementation

Devin must make these commands valid and update this README if the final setup
requires any additional steps:

```bash
python -m pip install -r requirements.txt
uvicorn src.main:app --reload
pytest
ruff check .
```
