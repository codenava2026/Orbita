"""Deterministic analytical Kepler two-body calculations in SI units."""

from dataclasses import dataclass
from math import pi, sqrt

import pint

from app.core.exceptions import InvalidUnits, ScientificValidationError
from app.scientific.constants import CONSTANTS
from app.scientific.units import ureg
from app.scientific.validation import ValidationCheck, ValidationResult, compare_values


def _as(quantity: pint.Quantity, unit: str, name: str) -> pint.Quantity:
    if not isinstance(quantity, pint.Quantity):
        raise InvalidUnits(f"{name} must be a Pint quantity expressed in {unit}")
    try:
        return quantity.to(unit)
    except pint.errors.DimensionalityError as exc:
        raise InvalidUnits(f"{name} must be convertible to {unit}") from exc


def _positive(quantity: pint.Quantity, unit: str, name: str) -> pint.Quantity:
    converted = _as(quantity, unit, name)
    if converted.magnitude <= 0:
        raise ScientificValidationError(f"{name} must be positive")
    return converted


def _eccentricity(eccentricity: float) -> float:
    if not 0 <= eccentricity < 1:
        raise ScientificValidationError("eccentricity must satisfy 0 <= e < 1 for a bound ellipse")
    return float(eccentricity)


@dataclass(frozen=True)
class KeplerOrbit:
    """Validated bound relative orbit parameters."""

    mass_1: pint.Quantity
    mass_2: pint.Quantity
    semimajor_axis: pint.Quantity
    eccentricity: float

    def __post_init__(self) -> None:
        _positive(self.mass_1, "kilogram", "mass_1")
        _positive(self.mass_2, "kilogram", "mass_2")
        _positive(self.semimajor_axis, "meter", "semimajor_axis")
        _eccentricity(self.eccentricity)


class KeplerCalculator:
    """Analytical relative two-body Kepler calculator.

    Planetary outputs are total relative mechanical quantities. The
    gravitational parameter and reduced mass are kept distinct.
    """

    name = "kepler"

    @staticmethod
    def reduced_mass(mass_1: pint.Quantity, mass_2: pint.Quantity) -> pint.Quantity:
        """Return μ = M1 M2 / (M1 + M2) in kilograms.

        Inputs: two positive masses convertible to kilograms.
        Output: reduced mass.
        Equation/reference: standard two-body reduction.
        Assumptions: Newtonian point masses with positive mass.
        Limitations: no extended-body, relativistic, or perturbation effects.
        """
        m1 = _positive(mass_1, "kilogram", "mass_1")
        m2 = _positive(mass_2, "kilogram", "mass_2")
        return (m1 * m2 / (m1 + m2)).to("kilogram")

    @staticmethod
    def gravitational_parameter(mass_1: pint.Quantity, mass_2: pint.Quantity) -> pint.Quantity:
        """Return μg = G(M1 + M2) in m³/s²."""
        m1 = _positive(mass_1, "kilogram", "mass_1")
        m2 = _positive(mass_2, "kilogram", "mass_2")
        return (CONSTANTS.G * (m1 + m2)).to("meter ** 3 / second ** 2")

    @classmethod
    def period_from_semimajor_axis(cls, mass_1: pint.Quantity, mass_2: pint.Quantity, semimajor_axis: pint.Quantity) -> pint.Quantity:
        """Return T = 2π√(a³ / G(M1+M2)) in seconds."""
        a = _positive(semimajor_axis, "meter", "semimajor_axis")
        mu_g = cls.gravitational_parameter(mass_1, mass_2)
        return (2 * pi * sqrt((a**3 / mu_g).to("second ** 2").magnitude)) * ureg.second

    @classmethod
    def semimajor_axis_from_period(cls, mass_1: pint.Quantity, mass_2: pint.Quantity, period: pint.Quantity) -> pint.Quantity:
        """Return a = [G(M1+M2)T²/(4π²)]^(1/3) in meters."""
        t = _positive(period, "second", "period")
        mu_g = cls.gravitational_parameter(mass_1, mass_2)
        return ((mu_g * t**2 / (4 * pi**2)) ** (1 / 3)).to("meter")

    @classmethod
    def total_orbital_energy(cls, mass_1: pint.Quantity, mass_2: pint.Quantity, semimajor_axis: pint.Quantity) -> pint.Quantity:
        """Return E = -G M1 M2/(2a), the total relative energy, in joules."""
        m1 = _positive(mass_1, "kilogram", "mass_1")
        m2 = _positive(mass_2, "kilogram", "mass_2")
        a = _positive(semimajor_axis, "meter", "semimajor_axis")
        return (-(CONSTANTS.G * m1 * m2 / (2 * a))).to("joule")

    @classmethod
    def circular_velocity(cls, mass_1: pint.Quantity, mass_2: pint.Quantity, semimajor_axis: pint.Quantity) -> pint.Quantity:
        """Return v = √(G(M1+M2)/a) in meters per second."""
        a = _positive(semimajor_axis, "meter", "semimajor_axis")
        mu_g = cls.gravitational_parameter(mass_1, mass_2)
        return sqrt((mu_g / a).to("meter ** 2 / second ** 2").magnitude) * ureg("meter / second")

    @classmethod
    def vis_viva_velocity(cls, mass_1: pint.Quantity, mass_2: pint.Quantity, radius: pint.Quantity, semimajor_axis: pint.Quantity) -> pint.Quantity:
        """Return v = √(G(M1+M2)(2/r - 1/a)) in meters per second."""
        r = _positive(radius, "meter", "radius")
        a = _positive(semimajor_axis, "meter", "semimajor_axis")
        if r.magnitude > 2 * a.magnitude:
            raise ScientificValidationError("vis-viva expression is negative for this radius and semimajor axis")
        speed_squared = cls.gravitational_parameter(mass_1, mass_2) * (2 / r - 1 / a)
        return sqrt(speed_squared.to("meter ** 2 / second ** 2").magnitude) * ureg("meter / second")

    @classmethod
    def specific_angular_momentum(cls, mass_1: pint.Quantity, mass_2: pint.Quantity, semimajor_axis: pint.Quantity, eccentricity: float) -> pint.Quantity:
        """Return h = √(G(M1+M2)a(1-e²)) in m²/s."""
        a = _positive(semimajor_axis, "meter", "semimajor_axis")
        e = _eccentricity(eccentricity)
        return sqrt((cls.gravitational_parameter(mass_1, mass_2) * a * (1 - e**2)).to("meter ** 4 / second ** 2").magnitude) * ureg("meter ** 2 / second")

    @classmethod
    def angular_momentum(cls, mass_1: pint.Quantity, mass_2: pint.Quantity, semimajor_axis: pint.Quantity, eccentricity: float) -> pint.Quantity:
        """Return L = μh, physical orbital angular momentum, in joule seconds."""
        return (cls.reduced_mass(mass_1, mass_2) * cls.specific_angular_momentum(mass_1, mass_2, semimajor_axis, eccentricity)).to("joule * second")

    @staticmethod
    def periapsis(semimajor_axis: pint.Quantity, eccentricity: float) -> pint.Quantity:
        """Return rp = a(1-e) in meters for a bound ellipse."""
        a = _positive(semimajor_axis, "meter", "semimajor_axis")
        return a * (1 - _eccentricity(eccentricity))

    @staticmethod
    def apoapsis(semimajor_axis: pint.Quantity, eccentricity: float) -> pint.Quantity:
        """Return ra = a(1+e) in meters for a bound ellipse."""
        a = _positive(semimajor_axis, "meter", "semimajor_axis")
        return a * (1 + _eccentricity(eccentricity))

    @classmethod
    def mean_motion(cls, mass_1: pint.Quantity, mass_2: pint.Quantity, semimajor_axis: pint.Quantity) -> pint.Quantity:
        """Return n = √(G(M1+M2)/a³) in inverse seconds."""
        a = _positive(semimajor_axis, "meter", "semimajor_axis")
        mu_g = cls.gravitational_parameter(mass_1, mass_2)
        return sqrt((mu_g / a**3).to("1 / second ** 2").magnitude) / ureg.second

    @staticmethod
    def period_from_mean_motion(mean_motion: pint.Quantity) -> pint.Quantity:
        """Return T = 2π/n in seconds."""
        n = _positive(mean_motion, "1 / second", "mean_motion")
        return (2 * pi / n).to("second")

    def smoke_test(self) -> dict[str, str | bool]:
        """Return a readiness marker without fabricating a physical result."""
        return {"calculator": self.name, "status": "ready", "physics_implemented": True}


class KeplerConsistencyValidator:
    """Cross-check a bound orbit against independent analytical equations."""

    @classmethod
    def validate(
        cls,
        orbit: KeplerOrbit,
        *,
        period: pint.Quantity | None = None,
        energy: pint.Quantity | None = None,
        angular_momentum: pint.Quantity | None = None,
        relative_tolerance: float = 1e-9,
    ) -> ValidationResult:
        """Return structured checks for period, energy, angular momentum, and geometry."""
        checks: list[ValidationCheck] = []
        errors: list[str] = []
        calculator = KeplerCalculator
        try:
            expected_period = calculator.period_from_semimajor_axis(orbit.mass_1, orbit.mass_2, orbit.semimajor_axis)
            expected_energy = calculator.total_orbital_energy(orbit.mass_1, orbit.mass_2, orbit.semimajor_axis)
            expected_angular_momentum = calculator.angular_momentum(
                orbit.mass_1, orbit.mass_2, orbit.semimajor_axis, orbit.eccentricity
            )
            periapsis = calculator.periapsis(orbit.semimajor_axis, orbit.eccentricity)
            apoapsis = calculator.apoapsis(orbit.semimajor_axis, orbit.eccentricity)
        except (InvalidUnits, ScientificValidationError) as exc:
            return ValidationResult(False, errors=[str(exc)], assumptions=["bound Newtonian ellipse"])

        if period is not None:
            actual = _as(period, "second", "period").magnitude
            checks.append(compare_values("keplers_third_law", actual, expected_period.magnitude, relative_tolerance=relative_tolerance))
        if energy is not None:
            actual = _as(energy, "joule", "energy").magnitude
            checks.append(compare_values("orbital_energy", actual, expected_energy.magnitude, relative_tolerance=relative_tolerance))
        if angular_momentum is not None:
            actual = _as(angular_momentum, "joule * second", "angular_momentum").magnitude
            checks.append(compare_values("angular_momentum", actual, expected_angular_momentum.magnitude, relative_tolerance=relative_tolerance))

        checks.append(
            ValidationCheck(
                "periapsis_apoapsis_geometry",
                periapsis.magnitude >= 0 and apoapsis.magnitude > periapsis.magnitude,
                "periapsis and apoapsis are physically ordered",
            )
        )
        return ValidationResult(
            passed=all(check.passed for check in checks) and not errors,
            checks=checks,
            errors=errors,
            assumptions=["Newtonian point masses", "bound elliptical orbit", "total relative orbital energy"],
            numerical_tolerances={"relative_tolerance": relative_tolerance},
        )