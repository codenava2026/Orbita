# Scientific Discovery Backend

Phase 1 and Phase 2 provide a Python 3.11+ backend foundation and deterministic analytical physics engine for reproducible mathematical experiments involving Keplerian two-body systems and hydrogen quantum states.

It stores experiment intent, inputs, formulas, jobs, and results in PostgreSQL. It does not fabricate scientific observations, generate hypotheses with an LLM, or label a candidate equation as a scientific law.

## Architecture

- `app/main.py` — FastAPI application and structured error responses.
- `app/api/` — health probes and read-only catalog endpoints.
- `app/core/` — environment configuration, logging, and scientific exceptions.
- `app/db/` — SQLAlchemy 2.x engine, models, and UTC timestamped persistence entities.
- `app/scientific/` — framework-independent constants, Pint units, Kepler dynamics, analytical hydrogen states, action variables, normalization, safe AST-to-SymPy parsing, and validation.
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
- `GET /api/science/constants`
- `GET /api/science/hydrogen/energy/{n}`
- `GET /api/science/hydrogen/state/{n}/{l}/{m}`

## Sample persistence verification

After migrating:

```bash
cd artifacts/api-server
uv run python -m scripts.create_sample_records
uv run pytest -q
```

The sample script creates metadata and a symbolic formula only. It deliberately does not create a scientific result.

## Phase 2 known physics

All public physics functions use SI quantities internally and document their inputs, outputs, equations, assumptions, and limitations in code.

### Central constants

`app/scientific/constants.py` contains one versioned set of CODATA-compatible values for `G`, `hbar`, `h`, `c`, elementary charge, `epsilon_0`, electron/proton/Earth/solar masses, astronomical unit, electron volt, and the Bohr radius.

### Kepler two-body engine

For positive point masses `M1`, `M2`, reduced mass and gravitational parameter are kept distinct:

```text
mu   = M1*M2/(M1+M2)
mu_g = G*(M1+M2)
```

The engine implements:

```text
T       = 2*pi*sqrt(a^3 / mu_g)
a       = (mu_g*T^2/(4*pi^2))^(1/3)
E       = -G*M1*M2/(2*a)
v       = sqrt(mu_g/a)
v^2     = mu_g*(2/r - 1/a)
L       = mu*sqrt(mu_g*a*(1-e^2))
h       = sqrt(mu_g*a*(1-e^2))
rp      = a*(1-e)
ra      = a*(1+e)
n_mean  = sqrt(mu_g/a^3)
```

The validator rejects non-bound eccentricities and returns structured checks, numerical errors, assumptions, and tolerances.

### Hydrogen engine

The non-relativistic analytical spectrum uses reduced electron-proton mass:

```text
k       = e^2/(4*pi*epsilon_0)
En      = -mu*k^2/(2*hbar^2*n^2)
a0      = hbar^2/(mu*k)
an      = n^2*a0
L^2     = l*(l+1)*hbar^2
Lz      = m*hbar
```

Quantum numbers are validated using `n >= 1`, `0 <= l <= n-1`, and `-l <= m <= l`. Node counts are analytical: `n-l-1`, `l`, and `n-1`.

These are hydrogen quantum-state relationships, not classical electron orbits. Phase 2 does not numerically solve the Schrödinger equation and does not calculate wavefunctions or probability densities.

### Known Kepler–Coulomb correspondence

For an attractive inverse-square potential `V(r) = -k/r`:

```text
Lambda = sqrt(mu*k*a)
Lambda = Jr + L
Jr     = (nr + 1/2)*hbar
L      = (l + 1/2)*hbar
n      = nr + l + 1
an     = n^2*hbar^2/(mu*k)
En     = -mu*k^2/(2*hbar^2*n^2)
```

This is known Kepler–Coulomb / hydrogen mathematics. It is not a discovery and does not imply that planetary systems are quantum systems. Planetary calculations use gravitational coupling; hydrogen calculations use Coulomb coupling.

### Dimensionless effective index

`n_eff` is explicitly labeled a **dimensionless effective index**, never a quantum number. Supported definitions are:

```text
n_eff = sqrt(a/a_ref)
n_eff = (T/T_ref)^(1/3)
n_eff = sqrt(E_ref/E)       # negative bound-state energies only
```

Normalization rejects incompatible units, and the comparison validator reports whether multiple definitions agree within an explicit tolerance.

## Scientific integrity rules

1. Never fabricate experimental results.
2. Never modify test data based on results.
3. Never tune a formula using the test set.
4. Never automatically label a candidate equation as a scientific law.
5. Keep training, validation, and test data logically separate.
6. Preserve experiment history and failed experiments.
7. Never overwrite previous scientific results.
8. Keep formulas reproducible and auditable.

Phase 1 uses an allowlisted Python AST parser before SymPy conversion; it does not call `eval()` on user-provided mathematical expressions. Phase 2 implements known analytical physics only. Symbolic discovery, observational data fitting, continuous workers, LLM hypothesis generation, and frontend work remain future phases.