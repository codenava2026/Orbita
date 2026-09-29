import pytest

from app.core.exceptions import InvalidFormula, InvalidUnits, ScientificValidationError
from app.scientific.formula import FormulaEvaluator, parse_formula
from app.scientific.units import validate_quantity
from app.scientific.interfaces import DimensionalAnalyzer


def test_formula_parsing_is_symbolic_and_evaluable() -> None:
    parsed = parse_formula("sqrt(a / a_ref)")
    assert parsed.variables == ("a", "a_ref")
    assert "sqrt" not in parsed.canonical_expression
    assert FormulaEvaluator.evaluate(parsed, {"a": 9, "a_ref": 1}) == pytest.approx(3)


def test_unsafe_formula_syntax_is_rejected_without_eval() -> None:
    with pytest.raises(InvalidFormula):
        parse_formula("__import__('os').system('echo should-not-run')")


def test_pint_rejects_incompatible_units() -> None:
    assert validate_quantity(5, "meter", "length").as_pint().magnitude == 5
    assert validate_quantity(5, "dimensionless_quantity", "eccentricity").as_pint().dimensionless
    with pytest.raises(InvalidUnits):
        validate_quantity(5, "meter", "mass")


def test_dimensional_analyzer_rejects_mismatched_dimensions() -> None:
    length = validate_quantity(5, "meter", "length")
    time = validate_quantity(2, "second", "time")
    with pytest.raises(ScientificValidationError):
        DimensionalAnalyzer.require_compatible(length, time)