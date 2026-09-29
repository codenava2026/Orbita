from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.db.models.entities import JobStatus


class DatasetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class DatasetVersionCreate(BaseModel):
    version: int = Field(ge=1)
    content_hash: str = Field(min_length=1, max_length=128)
    data: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class HypothesisCreate(BaseModel):
    identifier: str = Field(min_length=1, max_length=255)
    statement: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class FormulaCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    human_expression: str = Field(min_length=1)
    hypothesis_id: UUID | None = None


class ExperimentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    dataset_version_id: UUID
    hypothesis_id: UUID | None = None
    formula_id: UUID | None = None
    input_config: dict[str, Any] = Field(default_factory=dict)
    random_seed: int | None = None
    software_version: str = Field(min_length=1, max_length=100)
    metadata: dict[str, Any] = Field(default_factory=dict)


class JobCreate(BaseModel):
    experiment_id: UUID


class ReadModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class DatasetRead(ReadModel):
    id: UUID
    name: str
    description: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class DatasetVersionRead(ReadModel):
    id: UUID
    dataset_id: UUID
    version: int
    content_hash: str
    created_at: datetime


class HypothesisRead(ReadModel):
    id: UUID
    identifier: str
    statement: str
    status: str
    created_at: datetime
    updated_at: datetime


class FormulaRead(ReadModel):
    id: UUID
    hypothesis_id: UUID | None
    name: str
    human_expression: str
    symbolic_expression: str
    canonical_expression: str
    variables: list[str]
    version: int
    created_at: datetime
    updated_at: datetime


class ExperimentRead(ReadModel):
    id: UUID
    name: str
    dataset_version_id: UUID
    hypothesis_id: UUID | None
    formula_id: UUID | None
    random_seed: int | None
    software_version: str
    status: str
    created_at: datetime
    updated_at: datetime


class JobRead(ReadModel):
    id: UUID
    experiment_id: UUID
    status: JobStatus
    attempts: int
    started_at: datetime | None
    finished_at: datetime | None
    heartbeat_at: datetime | None
    created_at: datetime
    updated_at: datetime