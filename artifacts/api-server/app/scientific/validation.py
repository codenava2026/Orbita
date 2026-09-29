"""Structured scientific validation results."""

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class ValidationCheck:
    """One named validation comparison."""

    name: str
    passed: bool
    message: str
    absolute_error: float | None = None
    relative_error: float | None = None


@dataclass
class ValidationResult:
    """Structured outcome shared by scientific validators."""

    passed: bool
    checks: list[ValidationCheck] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    numerical_tolerances: dict[str, float] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        """Serialize this result into an API-safe dictionary."""
        return {
            "passed": self.passed,
            "checks": [asdict(check) for check in self.checks],
            "errors": self.errors,
            "warnings": self.warnings,
            "assumptions": self.assumptions,
            "numerical_tolerances": self.numerical_tolerances,
        }


def compare_values(
    name: str,
    actual: float,
    expected: float,
    *,
    relative_tolerance: float,
    absolute_tolerance: float | None = None,
) -> ValidationCheck:
    """Compare scalar values with explicit absolute and relative tolerances."""
    absolute_error = abs(actual - expected)
    denominator = max(abs(expected), 1e-300)
    relative_error = absolute_error / denominator
    passed = relative_error <= relative_tolerance or (
        absolute_tolerance is not None and absolute_error <= absolute_tolerance
    )
    return ValidationCheck(
        name=name,
        passed=passed,
        message="values agree within tolerance" if passed else "values differ beyond tolerance",
        absolute_error=absolute_error,
        relative_error=relative_error,
    )