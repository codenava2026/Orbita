"""Create auditable Phase 1 sample records; no scientific result is generated."""

import hashlib

from sqlalchemy import select

from app.core.config import get_settings
from app.db.database import SessionLocal
from app.db.models import Dataset, DatasetVersion, Experiment, Formula, Hypothesis, Job
from app.scientific.formula import parse_formula


def main() -> None:
    parsed = parse_formula("sqrt(a / a_ref)")
    with SessionLocal() as db:
        dataset = db.scalar(select(Dataset).where(Dataset.name == "TRAPPIST-1"))
        if dataset is None:
            dataset = Dataset(name="TRAPPIST-1", description="Sample dataset record only", metadata_json={"role": "fixture"})
            db.add(dataset)
            db.flush()
        version = db.scalar(
            select(DatasetVersion).where(
                DatasetVersion.dataset_id == dataset.id,
                DatasetVersion.version == 1,
            )
        )
        if version is None:
            version = DatasetVersion(
                dataset_id=dataset.id,
                version=1,
                content_hash=hashlib.sha256(b"TRAPPIST-1-phase-1-sample").hexdigest(),
                data={"rows": 0, "scientific_result": "not generated"},
                metadata_json={"role": "sample"},
            )
            db.add(version)
            db.flush()
        hypothesis = Hypothesis(
            identifier="phase-1-sample-hypothesis",
            statement="Candidate relationship recorded for architecture verification.",
            metadata_json={"scientific_claim": False},
        )
        db.add(hypothesis)
        db.flush()
        formula = Formula(
            hypothesis_id=hypothesis.id,
            name="reference-ratio",
            human_expression=parsed.human_expression,
            symbolic_expression=parsed.symbolic_expression,
            canonical_expression=parsed.canonical_expression,
            variables=list(parsed.variables),
        )
        db.add(formula)
        db.flush()
        experiment = Experiment(
            name="phase-1-reproducibility-smoke",
            dataset_version_id=version.id,
            hypothesis_id=hypothesis.id,
            formula_id=formula.id,
            input_config={"purpose": "persistence verification"},
            random_seed=0,
            software_version=get_settings().software_version,
        )
        db.add(experiment)
        db.flush()
        db.add(Job(experiment_id=experiment.id))
        db.commit()
        print(f"created sample experiment {experiment.id}")


if __name__ == "__main__":
    main()