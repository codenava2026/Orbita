import hashlib
import uuid

from app.db.models import Dataset, DatasetVersion, Experiment, Formula, Hypothesis, Job, JobStatus


def test_dataset_and_version_are_persisted_with_immutable_version_number(db_session) -> None:
    dataset = Dataset(name="TRAPPIST-1", description="Phase 1 fixture", metadata_json={"split": "validation"})
    db_session.add(dataset)
    db_session.flush()
    version = DatasetVersion(
        dataset_id=dataset.id,
        version=1,
        content_hash=hashlib.sha256(b"phase-1-fixture").hexdigest(),
        data={"rows": 0},
        metadata_json={"source": "test"},
    )
    db_session.add(version)
    db_session.commit()

    saved = db_session.get(DatasetVersion, version.id)
    assert saved is not None
    assert saved.dataset_id == dataset.id
    assert saved.version == 1
    assert saved.content_hash


def test_experiment_hypothesis_formula_and_job_lifecycle(db_session) -> None:
    dataset = Dataset(name=f"dataset-{uuid.uuid4()}")
    db_session.add(dataset)
    db_session.flush()
    version = DatasetVersion(dataset_id=dataset.id, version=1, content_hash="abc123", data={"rows": 0})
    hypothesis = Hypothesis(identifier=f"H-{uuid.uuid4()}", statement="A candidate relationship")
    db_session.add_all([version, hypothesis])
    db_session.flush()
    formula = Formula(
        hypothesis_id=hypothesis.id,
        name="reference-ratio",
        human_expression="sqrt(a / a_ref)",
        symbolic_expression="sqrt(a/a_ref)",
        canonical_expression="Pow(Mul(Symbol('a'), Pow(Symbol('a_ref'), Integer(-1))), Rational(1, 2))",
        variables=["a", "a_ref"],
    )
    db_session.add(formula)
    db_session.flush()
    experiment = Experiment(
        name="smoke experiment",
        dataset_version_id=version.id,
        hypothesis_id=hypothesis.id,
        formula_id=formula.id,
        input_config={"split": "validation"},
        random_seed=7,
        software_version="test",
    )
    db_session.add(experiment)
    db_session.flush()
    job = Job(experiment_id=experiment.id)
    db_session.add(job)
    db_session.commit()

    assert job.status == JobStatus.PENDING
    job.status = JobStatus.RUNNING
    job.attempts += 1
    db_session.commit()
    assert db_session.get(Job, job.id).status == JobStatus.RUNNING

    job.status = JobStatus.COMPLETED
    db_session.commit()
    assert db_session.get(Job, job.id).status == JobStatus.COMPLETED