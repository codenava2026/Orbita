import enum
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.base import Base


JSONType = JSON().with_variant(JSONB, "postgresql")


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class Dataset(Base, TimestampMixin):
    __tablename__ = "datasets"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column("metadata", JSONType, default=dict, nullable=False)

    versions: Mapped[list["DatasetVersion"]] = relationship(back_populates="dataset", cascade="all, delete-orphan")


class DatasetVersion(Base):
    __tablename__ = "dataset_versions"
    __table_args__ = (UniqueConstraint("dataset_id", "version", name="uq_dataset_version_number"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    dataset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("datasets.id"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    data: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column("metadata", JSONType, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    dataset: Mapped[Dataset] = relationship(back_populates="versions")
    experiments: Mapped[list["Experiment"]] = relationship(back_populates="dataset_version")


class Hypothesis(Base, TimestampMixin):
    __tablename__ = "hypotheses"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    identifier: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    statement: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="CANDIDATE", nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column("metadata", JSONType, default=dict, nullable=False)

    formulas: Mapped[list["Formula"]] = relationship(back_populates="hypothesis")
    experiments: Mapped[list["Experiment"]] = relationship(back_populates="hypothesis")


class Formula(Base, TimestampMixin):
    __tablename__ = "formulas"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    hypothesis_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("hypotheses.id"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    human_expression: Mapped[str] = mapped_column(Text, nullable=False)
    symbolic_expression: Mapped[str] = mapped_column(Text, nullable=False)
    canonical_expression: Mapped[str] = mapped_column(Text, nullable=False)
    variables: Mapped[list[str]] = mapped_column(JSONType, default=list, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    hypothesis: Mapped[Hypothesis | None] = relationship(back_populates="formulas")
    experiments: Mapped[list["Experiment"]] = relationship(back_populates="formula")


class Experiment(Base, TimestampMixin):
    __tablename__ = "experiments"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    dataset_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("dataset_versions.id"), nullable=False)
    hypothesis_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("hypotheses.id"))
    formula_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("formulas.id"))
    input_config: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict, nullable=False)
    random_seed: Mapped[int | None] = mapped_column(Integer)
    software_version: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="DRAFT", nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column("metadata", JSONType, default=dict, nullable=False)

    dataset_version: Mapped[DatasetVersion] = relationship(back_populates="experiments")
    hypothesis: Mapped[Hypothesis | None] = relationship(back_populates="experiments")
    formula: Mapped[Formula | None] = relationship(back_populates="experiments")
    runs: Mapped[list["ExperimentRun"]] = relationship(back_populates="experiment", cascade="all, delete-orphan")
    jobs: Mapped[list["Job"]] = relationship(back_populates="experiment", cascade="all, delete-orphan")


class ExperimentRun(Base, TimestampMixin):
    __tablename__ = "experiment_runs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    experiment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("experiments.id"), nullable=False)
    configuration_snapshot: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict, nullable=False)
    random_seed: Mapped[int | None] = mapped_column(Integer)
    software_version: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    result_metadata: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict, nullable=False)
    error_info: Mapped[dict[str, Any] | None] = mapped_column(JSONType)

    experiment: Mapped[Experiment] = relationship(back_populates="runs")
    results: Mapped[list["Result"]] = relationship(back_populates="experiment_run", cascade="all, delete-orphan")


class Result(Base):
    __tablename__ = "results"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    experiment_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("experiment_runs.id"), nullable=False)
    result_type: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column("metadata", JSONType, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    experiment_run: Mapped[ExperimentRun] = relationship(back_populates="results")


class Job(Base, TimestampMixin):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    experiment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("experiments.id"), nullable=False)
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus, native_enum=False), default=JobStatus.PENDING, nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_info: Mapped[dict[str, Any] | None] = mapped_column(JSONType)

    experiment: Mapped[Experiment] = relationship(back_populates="jobs")