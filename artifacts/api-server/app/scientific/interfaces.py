from dataclasses import dataclass
from typing import Any

from app.core.exceptions import ScientificValidationError
from app.scientific.action import ActionCalculator
from app.scientific.formula import FormulaEvaluator, ParsedFormula
from app.scientific.hydrogen import HydrogenCalculator
from app.scientific.kepler import KeplerCalculator
from app.scientific.units import ScientificQuantity


@dataclass(frozen=True)
class CalculationResult:
    calculator: str
    status: str
    details: dict[str, Any]


class DimensionalAnalyzer:
    @staticmethod
    def require_compatible(left: ScientificQuantity, right: ScientificQuantity) -> None:
        left_dimension = left.as_pint().dimensionality
        right_dimension = right.as_pint().dimensionality
        if left_dimension != right_dimension:
            raise ScientificValidationError(f"Incompatible dimensions: {left_dimension} and {right_dimension}")


class ExperimentRunner:
    """Stable extension point; Phase 1 records intent but produces no scientific result."""

    def prepare(self, formula: ParsedFormula) -> CalculationResult:
        return CalculationResult(
            calculator="experiment_runner",
            status="ready",
            details={"variables": formula.variables, "result_generated": False},
        )


__all__ = [
    "ActionCalculator", "DimensionalAnalyzer", "ExperimentRunner",
    "FormulaEvaluator", "HydrogenCalculator", "KeplerCalculator",
]