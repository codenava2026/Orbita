"""Create the Phase 1 scientific foundation.

Revision ID: 0001_initial
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _json_type() -> sa.types.TypeEngine:
    return sa.JSON()


def upgrade() -> None:
    op.create_table(
        "datasets",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("metadata", _json_type(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "dataset_versions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("dataset_id", sa.Uuid(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("content_hash", sa.String(length=128), nullable=False),
        sa.Column("data", _json_type(), nullable=False),
        sa.Column("metadata", _json_type(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["dataset_id"], ["datasets.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("dataset_id", "version", name="uq_dataset_version_number"),
    )
    op.create_table(
        "hypotheses",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("identifier", sa.String(length=255), nullable=False),
        sa.Column("statement", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("metadata", _json_type(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("identifier"),
    )
    op.create_table(
        "formulas",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("hypothesis_id", sa.Uuid()),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("human_expression", sa.Text(), nullable=False),
        sa.Column("symbolic_expression", sa.Text(), nullable=False),
        sa.Column("canonical_expression", sa.Text(), nullable=False),
        sa.Column("variables", _json_type(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["hypothesis_id"], ["hypotheses.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "experiments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("dataset_version_id", sa.Uuid(), nullable=False),
        sa.Column("hypothesis_id", sa.Uuid()),
        sa.Column("formula_id", sa.Uuid()),
        sa.Column("input_config", _json_type(), nullable=False),
        sa.Column("random_seed", sa.Integer()),
        sa.Column("software_version", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("metadata", _json_type(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["dataset_version_id"], ["dataset_versions.id"]),
        sa.ForeignKeyConstraint(["formula_id"], ["formulas.id"]),
        sa.ForeignKeyConstraint(["hypothesis_id"], ["hypotheses.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "experiment_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("experiment_id", sa.Uuid(), nullable=False),
        sa.Column("configuration_snapshot", _json_type(), nullable=False),
        sa.Column("random_seed", sa.Integer()),
        sa.Column("software_version", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("result_metadata", _json_type(), nullable=False),
        sa.Column("error_info", _json_type()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["experiment_id"], ["experiments.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "results",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("experiment_run_id", sa.Uuid(), nullable=False),
        sa.Column("result_type", sa.String(length=100), nullable=False),
        sa.Column("value", _json_type(), nullable=False),
        sa.Column("metadata", _json_type(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["experiment_run_id"], ["experiment_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("experiment_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("heartbeat_at", sa.DateTime(timezone=True)),
        sa.Column("error_info", _json_type()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["experiment_id"], ["experiments.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("jobs")
    op.drop_table("results")
    op.drop_table("experiment_runs")
    op.drop_table("experiments")
    op.drop_table("formulas")
    op.drop_table("hypotheses")
    op.drop_table("dataset_versions")
    op.drop_table("datasets")