# Scientific Discovery Backend

Python/FastAPI foundation for reproducible scientific computation and auditable mathematical experiments.

## Run & Operate

- `pnpm --filter @workspace/api-server run dev` — run the FastAPI server through the `/api` route
- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `cd artifacts/api-server && uv run alembic upgrade head` — apply database migrations
- `cd artifacts/api-server && uv run pytest -q` — run the backend tests
- Required env: `DATABASE_URL` — PostgreSQL connection string

## Stack

- Python 3.11+, FastAPI, SQLAlchemy 2.x, Alembic, Pydantic v2
- PostgreSQL via psycopg, Pint, NumPy, SciPy, SymPy, pytest
- The existing workspace still contains shared TypeScript scaffolding, but the API artifact is now Python.

## Where things live

- `artifacts/api-server/app/` — application and scientific modules
- `artifacts/api-server/migrations/` — Alembic schema history
- `artifacts/api-server/tests/` — backend verification
- `artifacts/api-server/README.md` — setup, API, schema, and scientific integrity rules

## Architecture decisions

- Scientific parsing is allowlisted AST-to-SymPy conversion; user expressions are never passed to `eval()`.
- Dataset versions are separate rows and experiments reference exact versions.
- Phase 1 exposes read-only catalog routes; mutation and worker orchestration remain explicit future work.
- The scientific package is independent from FastAPI so future calculators can run in jobs or scripts.

## Product

The backend records reproducible datasets, hypotheses, formulas, experiments, runs, results, and long-running job state for future mathematical discovery work.

## User preferences

- Do not add the frontend or an LLM before the backend phases are complete.

## Gotchas

- Apply Alembic migrations before using catalog routes against a new database.
- Use `uv run` for Python commands so the project-local environment is selected.

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
