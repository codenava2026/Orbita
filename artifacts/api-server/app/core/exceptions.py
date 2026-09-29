from typing import Any


class ScientificError(Exception):
    code = "scientific_error"
    status_code = 400

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class InvalidUnits(ScientificError):
    code = "invalid_units"


class InvalidFormula(ScientificError):
    code = "invalid_formula"


class InvalidDataset(ScientificError):
    code = "invalid_dataset"


class ScientificValidationError(ScientificError):
    code = "scientific_validation_error"


class ExperimentExecutionError(ScientificError):
    code = "experiment_execution_error"
    status_code = 500