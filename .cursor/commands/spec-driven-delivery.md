# Spec-Driven Delivery

Deliver the application described in `SPEC.md` by coordinating the
`implementer`, `reviewer`, and `verifier` subagents.

## Inputs

Before planning or delegating work, read these files completely:

- `AGENTS.md` — repository rules and required commands
- `SPEC.md` — product behavior and acceptance criteria
- `README.md` — current setup and usage documentation

If a material requirement is ambiguous or contradictory, ask the user before
implementation.

## Workflow

Run the following phases in order. Do not run dependent phases in parallel, and
do not accept a phase based only on a subagent's conclusion.

### 1. Plan

1. List the required behaviors and important error cases.
2. Propose the smallest implementation that satisfies `SPEC.md`.
3. Confirm the environment can run Python, pytest, Ruff, and the application.
4. Ask the user only about material blockers.

### 2. Implement

Delegate implementation to the `implementer` subagent. Give it `AGENTS.md`,
`SPEC.md`, the approved scope, and the expected output.

After it returns:

1. Inspect the diff and its test and lint evidence.
2. Confirm it added no unrelated features or infrastructure.
3. Return defects to the implementer and repeat this phase as needed.

Proceed only when the application starts, implementation tests pass, Ruff
passes, and the changes remain within scope.

### 3. Review

Delegate an independent specification review to the `reviewer` subagent. Give
it the specification and integrated implementation, but not the implementer's
conclusions.

Send accepted blocking or major findings back to the implementer. After fixes,
ask the reviewer to recheck the affected areas.

Proceed only when no accepted blocking or major finding remains.

### 4. Verify

Delegate independent acceptance verification to the `verifier` subagent.

For each failure:

- send production defects to the implementer;
- have the verifier correct only genuine test defects;
- ask the user about specification ambiguity; and
- rerun affected review and verification checks.

Proceed only when every automatable acceptance criterion has passing evidence
and no required test is skipped.

### 5. Final check

Independently:

1. Install dependencies in an isolated Python 3.12 environment.
2. Run `pytest`.
3. Run `ruff check .`.
4. Start the application using the README command.
5. Smoke-test every required endpoint.
6. Confirm tests do not modify the development database.
7. Inspect the final diff for unrelated changes and secrets.

Do not modify `SPEC.md` without user approval. Do not delete, skip, or weaken a
valid test to make the suite pass. Do not declare completion until all required
checks pass.

## Final report

Report:

- what was implemented;
- which subagents were used;
- important review findings and their resolutions;
- exact test, lint, startup, and end-to-end results;
- files changed; and
- remaining limitations or blockers.
