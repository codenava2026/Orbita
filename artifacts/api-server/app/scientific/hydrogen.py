"""Analytical non-relativistic hydrogen relationships.

These functions describe quantum states through the known analytical solution.
They do not model classical electron orbits and do not numerically solve the
Schrödinger equation.
"""

from dataclasses import dataclass
from math import pi, sqrt

import pint

from app.core.exceptions import ScientificValidationError
from app.scientific.constants import CONSTANTS
from app.scientific.kepler import _positive
from app.scientific.units import ureg


def _quantum_numbers(n: int, l: int, m: int) -> None:
    if n < 1:
        raise ScientificValidationError("principal quantum number n must satisfy n >= 1")
    if not 0 <= l <= n - 1:
        raise ScientificValidationError("angular quantum number l must satisfy 0 <= l <= n - 1")
    if not -l <= m <= l:
        raise ScientificValidationError("magnetic quantum number m must satisfy -l <= m <= l")


@dataclass(frozen=True)
class HydrogenState:
    """Validated hydrogen quantum state and analytical observables."""

    n: int
    l: int
    m: int
    energy: pint.Quantity
    angular_momentum_squared: pint.Quantity
    angular_momentum_z: pint.Quantity
    radial_nodes: int
    angular_nodes: int
    total_nodes: int


class HydrogenCalculator:
    """Analytical hydrogen atom calculator using reduced electron-proton mass."""

    name = "hydrogen"

    @staticmethod
    def reduced_mass() -> pint.Quantity:
        """Return μ = me mp/(me+mp) in kilograms.

        Inputs: centralized electron and proton masses.
        Output: reduced electron-proton mass.
        Equation/reference: non-relativistic two-body reduction.
        Assumptions: isolated hydrogen, point particles, non-relativistic limit.
        Limitations: no fine structure, Lamb shift, spin, or relativistic corrections.
        """
        return (CONSTANTS.electron_mass * CONSTANTS.proton_mass / (CONSTANTS.electron_mass + CONSTANTS.proton_mass)).to("kilogram")

    @staticmethod
    def coulomb_coupling() -> pint.Quantity:
        """Return k = e²/(4πε0) in joule meters."""
        return (CONSTANTS.elementary_charge**2 / (4 * pi * CONSTANTS.epsilon_0)).to("joule * meter")

    @classmethod
    def energy(cls, n: int) -> pint.Quantity:
        """Return En = -μk²/(2ℏ²n²) in joules.

        Inputs: integer principal quantum number n >= 1.
        Output: negative bound-state energy.
        Equation/reference: analytical non-relativistic hydrogen spectrum.
        Assumptions: isolated hydrogen and a stationary bound state.
        Limitations: excludes fine structure and external-field effects.
        """
        if n < 1:
            raise ScientificValidationError("principal quantum number n must satisfy n >= 1")
        mu = cls.reduced_mass()
        k = cls.coulomb_coupling()
        return (-(mu * k**2 / (2 * CONSTANTS.hbar**2 * n**2))).to("joule")

    @classmethod
    def energy_ratio(cls, n_1: int, n_2: int) -> float:
        """Return the signed ratio E(n1)/E(n2) for two bound states."""
        if n_1 < 1 or n_2 < 1:
            raise ScientificValidationError("principal quantum numbers must satisfy n >= 1")
        return float((cls.energy(n_1) / cls.energy(n_2)).to_base_units().magnitude)

    @classmethod
    def binding_energy(cls, n: int) -> pint.Quantity:
        """Return positive binding energy |En| in joules."""
        return (-cls.energy(n)).to("joule")

    @classmethod
    def bohr_radius(cls) -> pint.Quantity:
        """Return a0 = ℏ²/(μk), the reduced-mass Bohr radius, in meters."""
        return (CONSTANTS.hbar**2 / (cls.reduced_mass() * cls.coulomb_coupling())).to("meter")

    @classmethod
    def characteristic_radius(cls, n: int) -> pint.Quantity:
        """Return an = n²a0 in meters.

        This is a characteristic analytical radius, not a classical orbit radius.
        """
        if n < 1:
            raise ScientificValidationError("principal quantum number n must satisfy n >= 1")
        return (n**2 * cls.bohr_radius()).to("meter")

    @staticmethod
    def validate_quantum_numbers(n: int, l: int, m: int) -> None:
        """Validate n >= 1, 0 <= l <= n-1, and -l <= m <= l."""
        _quantum_numbers(n, l, m)

    @classmethod
    def angular_momentum_squared(cls, n: int, l: int, m: int) -> pint.Quantity:
        """Return L² = l(l+1)ℏ² in angular-momentum-squared units."""
        _quantum_numbers(n, l, m)
        return (l * (l + 1) * CONSTANTS.hbar**2).to("joule ** 2 * second ** 2")

    @classmethod
    def angular_momentum_z(cls, n: int, l: int, m: int) -> pint.Quantity:
        """Return Lz = mℏ in joule seconds."""
        _quantum_numbers(n, l, m)
        return (m * CONSTANTS.hbar).to("joule * second")

    @staticmethod
    def radial_nodes(n: int, l: int, m: int) -> int:
        """Return Nradial = n-l-1."""
        _quantum_numbers(n, l, m)
        return n - l - 1

    @staticmethod
    def angular_nodes(n: int, l: int, m: int) -> int:
        """Return Nangular = l."""
        _quantum_numbers(n, l, m)
        return l

    @staticmethod
    def total_nodes(n: int, l: int, m: int) -> int:
        """Return Ntotal = n-1."""
        _quantum_numbers(n, l, m)
        return n - 1

    @classmethod
    def state(cls, n: int, l: int, m: int) -> HydrogenState:
        """Return a deterministic analytical HydrogenState."""
        _quantum_numbers(n, l, m)
        return HydrogenState(
            n=n,
            l=l,
            m=m,
            energy=cls.energy(n),
            angular_momentum_squared=cls.angular_momentum_squared(n, l, m),
            angular_momentum_z=cls.angular_momentum_z(n, l, m),
            radial_nodes=cls.radial_nodes(n, l, m),
            angular_nodes=cls.angular_nodes(n, l, m),
            total_nodes=cls.total_nodes(n, l, m),
        )

    @classmethod
    def formal_period(cls, n: int) -> pint.Quantity:
        """Return formal Coulomb-Kepler period 2π√(μ an³/k) in seconds.

        This is a mathematical scaling correspondence, not a claim that an
        electron follows a classical orbit.
        """
        a_n = cls.characteristic_radius(n)
        return (2 * pi * sqrt((cls.reduced_mass() * a_n**3 / cls.coulomb_coupling()).to("second ** 2").magnitude)) * ureg.second

    @classmethod
    def formal_velocity(cls, n: int) -> pint.Quantity:
        """Return formal Coulomb-Kepler speed √(k/(μ an)) in meters/second."""
        a_n = cls.characteristic_radius(n)
        return sqrt((cls.coulomb_coupling() / (cls.reduced_mass() * a_n)).to("meter ** 2 / second ** 2").magnitude) * ureg("meter / second")

    def smoke_test(self) -> dict[str, str | bool]:
        """Return a readiness marker for the analytical engine."""
        return {"calculator": self.name, "status": "ready", "physics_implemented": True}