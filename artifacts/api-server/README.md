# Scientific Discovery Backend

Phase 1 is a Python 3.11+ backend foundation for reproducible mathematical experiments involving future Keplerian and hydrogen-structure research.

It stores experiment intent, inputs, formulas, jobs, and results in PostgreSQL. It does not fabricate scientific observations, generate hypotheses with an LLM, or label a candidate equation as a scientific law.

## Architecture

- `app/main.py` — FastAPI application and structured error responses.
- `app/api/` — health probes and read-only catalog endpoints.
- `app/core/` — environment configuration, logging, and scientific exceptions.
- `app/db/` — SQLAlchemy 2.x engine, models, and UTC timestamped persistence entities.
- `app/scientific/` — framework-independent Pint, safe AST-to-SymPy parsing, and calculator interfaces.
- `migrations/` — Alembic baseline for the Phase 1 schema.
- `tests/` — startup, persistence, job lifecycle, units, and symbolic parsing tests.

The scientific layer has no FastAPI dependency. Later physics, discovery, validation, and worker phases can call it directly.

## Database tables

`datasets`, `dataset_versions`, `hypotheses`, `formulas`, `experiments`, `experiment_runs`, `results`, and `jobs`.

Dataset versions are append-only records identified by `(dataset_id, version)`. Experiments point to an exact dataset version and preserve the input configuration, random seed, software version, and status. Results are separate records and are never stored only in memory.

## Setup

The Replit project provides `DATABASE_URL` for PostgreSQL. For local development, copy `.env.example` and set it to a PostgreSQL connection string.

```bash
uv sync
cd artifacts/api-server
uv run alembic upgrade head
```

The service commands are also available through the workspace workflow:

```bash
pnpm --filter @workspace/api-server run dev
pnpm --filter @workspace/api-server run test
```

## API

- `GET /api/health` — application health.
- `GET /api/healthz` — startup probe alias.
- `GET /api/health/db` — live database check.
- `GET /api/catalog/datasets`
- `GET /api/catalog/experiments`
- `GET /api/catalog/hypotheses`
- `GET /api/catalog/formulas`
- `GET /api/catalog/jobs`

## Sample persistence verification

After migrating:

```bash
cd artifacts/api-server
uv run python -m scripts.create_sample_records
uv run pytest -q
```

The sample script creates metadata and a symbolic formula only. It deliberately does not create a scientific result.

## Scientific integrity rules

1. Never fabricate experimental results.
2. Never modify test data based on results.
3. Never tune a formula using the test set.
4. Never automatically label a candidate equation as a scientific law.
5. Keep training, validation, and test data logically separate.
6. Preserve experiment history and failed experiments.
7. Never overwrite previous scientific results.
8. Keep formulas reproducible and auditable.

Phase 1 uses an allowlisted Python AST parser before SymPy conversion; it does not call `eval()` on user-provided mathematical expressions.