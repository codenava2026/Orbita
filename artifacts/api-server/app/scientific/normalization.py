"""Dimension-safe normalization and explicitly non-quantum effective indices."""

from dataclasses import dataclass
from math import sqrt

import pint

from app.core.exceptions import InvalidUnits, ScientificValidationError
from app.scientific.units import ureg
from app.scientific.validation import ValidationCheck, ValidationResult, compare_values


def normalize(value: pint.Quantity, reference: pint.Quantity) -> float:
    """Return x/x_reference after requiring compatible dimensions.

    Inputs: Pint quantities with compatible dimensions.
    Output: dimensionless ratio.
    Equation/reference: direct dimensionless normalization.
    Assumptions: reference is non-zero.
    Limitations: normalization does not establish a physical relationship.
    """
    if not isinstance(value, pint.Quantity) or not isinstance(reference, pint.Quantity):
        raise InvalidUnits("normalization requires two Pint quantities")
    try:
        converted = value.to(reference.units)
    except pint.errors.DimensionalityError as exc:
        raise InvalidUnits("normalization requires compatible dimensions") from exc
    if reference.magnitude == 0:
        raise ScientificValidationError("normalization reference cannot be zero")
    return float((converted / reference).to_base_units().magnitude)


def dimensionless(value: float) -> pint.Quantity:
    """Wrap a scalar as an explicitly dimensionless quantity."""
    return value * ureg.dimensionless


@dataclass(frozen=True)
class EffectiveIndex:
    """An explicitly non-quantum dimensionless effective index."""

    value: float
    source: str
    label: str = "dimensionless effective index"
    is_quantum_number: bool = False

    def as_quantity(self) -> pint.Quantity:
        """Return the index as a dimensionless Pint quantity."""
        return dimensionless(self.value)


def n_eff_from_semimajor_axis(value: pint.Quantity, reference: pint.Quantity) -> EffectiveIndex:
    """Return neff = √(a/a_ref), labeled as a dimensionless effective index."""
    ratio = normalize(value, reference)
    if ratio < 0:
        raise ScientificValidationError("semimajor-axis normalization must be non-negative")
    return EffectiveIndex(sqrt(ratio), "semimajor_axis_ratio")


def n_eff_from_period(value: pint.Quantity, reference: pint.Quantity) -> EffectiveIndex:
    """Return neff = (T/T_ref)^(1/3), labeled as a dimensionless effective index."""
    ratio = normalize(value, reference)
    if ratio < 0:
        raise ScientificValidationError("period normalization must be non-negative")
    return EffectiveIndex(ratio ** (1 / 3), "period_ratio")


def n_eff_from_energy(value: pint.Quantity, reference: pint.Quantity) -> EffectiveIndex:
    """Return neff = √(E_ref/E) for negative bound-state energies."""
    normalized_value = value.to("joule") if isinstance(value, pint.Quantity) else None
    normalized_reference = reference.to("joule") if isinstance(reference, pint.Quantity) else None
    if normalized_value is None or normalized_reference is None:
        raise InvalidUnits("energy effective index requires Pint energy quantities")
    if normalized_value.magnitude >= 0 or normalized_reference.magnitude >= 0:
        raise ScientificValidationError("energy effective index requires negative bound-state energies")
    ratio = normalized_reference.magnitude / normalized_value.magnitude
    return EffectiveIndex(sqrt(ratio), "bound_energy_ratio")


def compare_effective_indices(
    definitions: dict[str, EffectiveIndex],
    *,
    relative_tolerance: float = 1e-9,
) -> ValidationResult:
    """Check whether named neff definitions agree numerically."""
    if not definitions:
        return ValidationResult(False, errors=["at least one effective-index definition is required"])
    reference_name, reference = next(iter(definitions.items()))
    checks = [
        compare_values(
            name=f"{reference_name}_vs_{name}",
            actual=index.value,
            expected=reference.value,
            relative_tolerance=relative_tolerance,
        )
        for name, index in definitions.items()
        if name != reference_name
    ]
    return ValidationResult(
        passed=all(check.passed for check in checks),
        checks=checks,
        assumptions=["neff is a dimensionless scaling index, not a quantum number"],
        numerical_tolerances={"relative_tolerance": relative_tolerance},
    )