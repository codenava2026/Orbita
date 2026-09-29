from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.db.models import Dataset, Experiment, Formula, Hypothesis, Job
from app.schemas.entities import DatasetRead, ExperimentRead, FormulaRead, HypothesisRead, JobRead

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/datasets", response_model=list[DatasetRead])
def list_datasets(db: Session = Depends(get_db)) -> list[Dataset]:
    return list(db.scalars(select(Dataset).order_by(Dataset.created_at.desc()).limit(100)))


@router.get("/experiments", response_model=list[ExperimentRead])
def list_experiments(db: Session = Depends(get_db)) -> list[Experiment]:
    return list(db.scalars(select(Experiment).order_by(Experiment.created_at.desc()).limit(100)))


@router.get("/hypotheses", response_model=list[HypothesisRead])
def list_hypotheses(db: Session = Depends(get_db)) -> list[Hypothesis]:
    return list(db.scalars(select(Hypothesis).order_by(Hypothesis.created_at.desc()).limit(100)))


@router.get("/formulas", response_model=list[FormulaRead])
def list_formulas(db: Session = Depends(get_db)) -> list[Formula]:
    return list(db.scalars(select(Formula).order_by(Formula.created_at.desc()).limit(100)))


@router.get("/jobs", response_model=list[JobRead])
def list_jobs(db: Session = Depends(get_db)) -> list[Job]:
    return list(db.scalars(select(Job).order_by(Job.created_at.desc()).limit(100)))