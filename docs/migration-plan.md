# Migration Plan: Port Repository to Python

## Objective
Port the existing Node.js/TypeScript codebase to a clean, maintainable Python implementation with full test coverage.

## Phase 1 – Baseline Snapshot
1. Move the entire current codebase into `old/` for archival.
2. Ensure the project history remains intact via git.

## Phase 2 – Python Project Scaffolding
1. Create new Python package structure under `src/`.
2. Add `pyproject.toml` using Poetry (or requirements.txt + setup.cfg) to manage dependencies.
3. Configure linting and formatting (ruff/flake8, black, isort, mypy).

## Phase 3 – Feature Parity Port
Iteratively port functionality module-by-module:
1. Core business logic
2. CLI / API interfaces
3. Data models and persistence layers

For each module:
- Translate logic from TypeScript to idiomatic Python 3.12.
- Add/expand unit tests to validate behaviour.

## Phase 4 – Comprehensive Testing
1. Unit tests: `pytest` with `pytest-cov` for coverage.
2. Integration tests: exercise interactions between subsystems.
3. End-to-End (E2E) tests: simulate real user workflows through CLI/API.
4. Aim for ≥ 95% coverage.

## Phase 5 – Continuous Integration
1. GitHub Actions workflow: lint, type-check, test matrix (Linux, macOS, Windows).
2. Fail the build on <95% coverage or lint/type errors.

## Phase 6 – Validation & Bug-fix Loop
1. Run full test suite.
2. Fix failures, refactor for clarity/performance.
3. Repeat until the pipeline is 100% green.

## Deliverables
- `docs/migration-plan.md` (this file) detailing process and decisions.
- New Python source in `src/` with corresponding tests in `tests/`.
- CI pipeline definitions.
- Updated README with Python usage instructions.