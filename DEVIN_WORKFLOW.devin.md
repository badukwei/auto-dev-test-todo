# Spec-Driven Multi-Agent Workflow

## Outcome

Deliver the application described in `SPEC.md` using a primary Devin session
and three independent child sessions for implementation, review, and
verification.

## Inputs

Read these files before starting:

- `AGENTS.md` — repository rules and required commands
- `SPEC.md` — product behavior and acceptance criteria
- `README.md` — project purpose and usage

If a material requirement is ambiguous or contradictory, ask the user before
implementation.

## Roles

### Primary agent

- Read the requirements and create a short implementation plan.
- Create and brief each child session.
- Review and integrate child-session results.
- Decide whether each phase passes.
- Run final tests and report the result.

### Implementation agent

- Implement only the behavior required by `SPEC.md`.
- Write the endpoint and unit tests needed to support the implementation.
- Run relevant tests and lint checks.
- Fix implementation defects returned by the primary agent.

### Review agent

- Independently compare the implementation with `SPEC.md`.
- Look for incorrect behavior, missing cases, unnecessary complexity, and weak
  tests.
- Report findings with severity, evidence, and a recommended correction.
- Do not edit code unless the primary agent explicitly asks.

### Verification agent

- Derive acceptance and end-to-end tests independently from `SPEC.md`.
- Test externally observable behavior, including errors and persistence.
- Report exact reproduction steps for failures.
- Do not change production code or weaken valid expectations.

## Rules

- Run the phases below in order; do not run dependent phases in parallel.
- Use a separate child session for each role.
- Give every child `AGENTS.md`, `SPEC.md`, its scope, and expected output.
- The implementation agent owns tests in `tests/implementation/`.
- The verification agent owns tests in `tests/acceptance/`.
- Do not modify `SPEC.md` without user approval.
- Do not delete, skip, or weaken a valid test to make the suite pass.
- Do not add authentication, Docker, a frontend, cloud services, or other
  out-of-scope features.
- A phase passes only when the primary agent verifies its evidence.

## Procedure

### 1. Plan

The primary agent must:

1. Read all input documents.
2. List the required behaviors and important error cases.
3. Propose a minimal implementation plan.
4. Confirm the environment can run Python, tests, and child sessions.
5. Ask the user only about material blockers.

Proceed when the plan covers all requirements and no material ambiguity
remains.

### 2. Implement

Create the implementation child session and ask it to:

1. Implement `SPEC.md`.
2. Add endpoint tests and focused unit tests under `tests/implementation/`.
3. Run its tests and Ruff.
4. Start the application and confirm it responds.
5. Return changed files, commands, results, assumptions, and blockers.

The primary agent must inspect the diff and test results. If implementation
checks fail, return the defects to the implementation agent and repeat this
phase.

Proceed when the application starts, implementation tests pass, Ruff passes,
and no unrelated features were added.

### 3. Review

Create a fresh review child session. Give it the specification and integrated
implementation, but not the implementation agent's conclusions.

The reviewer must check:

- every required behavior and error case;
- HTTP and database behavior;
- test isolation and meaningful assertions;
- unnecessary scope or complexity; and
- README accuracy.

Send accepted blocking or major findings to the implementation agent. After
corrections, have the reviewer check the affected areas again.

Proceed only when no accepted blocking or major finding remains.

### 4. Verify

Create a fresh verification child session and ask it to:

1. Map each acceptance criterion to a test.
2. Add independent black-box tests under `tests/acceptance/`.
3. Cover success, validation, not-found, idempotency, persistence, and test
   isolation.
4. Run the complete test suite.
5. Return commands, results, failures, and reproduction steps.

For each failure:

- send production defects to the implementation agent;
- have the verification agent correct only genuine test defects;
- ask the user about specification ambiguity; and
- rerun review and verification after affected changes.

Proceed when every automatable acceptance criterion has passing evidence and no
required test is skipped.

### 5. Final check

The primary agent must independently:

1. Install dependencies in an isolated Python 3.12 environment.
2. Run `pytest`.
3. Run `ruff check .`.
4. Start the application using the README command.
5. Smoke-test all required endpoints.
6. Confirm tests do not modify the development database.
7. Inspect the final diff for unrelated changes or secrets.

If any check fails, return to the responsible phase and rerun affected checks.
Do not declare completion until all required checks pass.

## Final report

Report:

- what was implemented;
- which child sessions were used;
- important review findings and resolutions;
- exact test, lint, startup, and end-to-end results;
- changed files; and
- remaining limitations or blockers.
