from dataclasses import dataclass
from typing import Literal

import pint

from app.core.exceptions import InvalidUnits

ureg = pint.UnitRegistry(autoconvert_offset_to_baseunit=True)
ureg.define("dimensionless_quantity = []")

QuantityKind = Literal[
    "mass", "length", "time", "energy", "velocity", "momentum",
    "angular_momentum", "eccentricity", "inclination", "semimajor_axis",
    "orbital_period", "dimensionless",
]

EXPECTED_DIMENSIONS: dict[QuantityKind, str] = {
    "mass": "[mass]",
    "length": "[length]",
    "time": "[time]",
    "energy": "[mass] * [length] ** 2 / [time] ** 2",
    "velocity": "[length] / [time]",
    "momentum": "[mass] * [length] / [time]",
    "angular_momentum": "[mass] * [length] ** 2 / [time]",
    "eccentricity": "dimensionless",
    "inclination": "dimensionless",
    "semimajor_axis": "[length]",
    "orbital_period": "[time]",
    "dimensionless": "dimensionless",
}


@dataclass(frozen=True)
class ScientificQuantity:
    value: float
    unit: str
    kind: QuantityKind

    def as_pint(self) -> pint.Quantity:
        quantity = self.value * ureg(self.unit)
        expected = EXPECTED_DIMENSIONS[self.kind]
        if expected == "dimensionless":
            if not quantity.dimensionless:
                raise InvalidUnits(f"{self.kind} must be dimensionless")
        elif quantity.dimensionality != ureg.get_dimensionality(expected):
            raise InvalidUnits(
                f"{self.kind} expects {expected}, received {quantity.dimensionality}"
            )
        return quantity


def validate_quantity(value: float, unit: str, kind: QuantityKind) -> ScientificQuantity:
    candidate = ScientificQuantity(value=value, unit=unit, kind=kind)
    try:
        candidate.as_pint()
    except (pint.errors.DimensionalityError, pint.errors.UndefinedUnitError, ValueError) as exc:
        raise InvalidUnits(f"Invalid {kind} quantity: {value} {unit}") from exc
    return candidate


def quantity(value: float, unit: str) -> pint.Quantity:
    try:
        return value * ureg(unit)
    except (pint.errors.DimensionalityError, pint.errors.UndefinedUnitError, ValueError) as exc:
        raise InvalidUnits(f"Invalid quantity: {value} {unit}") from exc