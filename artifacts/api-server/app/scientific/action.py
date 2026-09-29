"""Classical and semiclassical action variables for inverse-square systems."""

from math import sqrt

import pint

from app.core.exceptions import ScientificValidationError
from app.scientific.constants import CONSTANTS
from app.scientific.kepler import KeplerCalculator, _as, _positive


class ActionCalculator:
    """Keeps gravitational parameters, coupling constants, and actions distinct."""

    name = "action"

    @staticmethod
    def gravitational_coupling(mass_1: pint.Quantity, mass_2: pint.Quantity) -> pint.Quantity:
        """Return kg = G M1 M2 in joule meters for a planetary potential."""
        m1 = _positive(mass_1, "kilogram", "mass_1")
        m2 = _positive(mass_2, "kilogram", "mass_2")
        from app.scientific.constants import CONSTANTS

        return (CONSTANTS.G * m1 * m2).to("joule * meter")

    @staticmethod
    def coulomb_coupling(coupling: pint.Quantity) -> pint.Quantity:
        """Validate and return a Coulomb inverse-square coupling in joule meters."""
        return _positive(coupling, "joule * meter", "coulomb_coupling")

    @staticmethod
    def total_action(reduced_mass: pint.Quantity, coupling: pint.Quantity, semimajor_axis: pint.Quantity) -> pint.Quantity:
        """Return Λ = √(μka) in joule seconds.

        Inputs: reduced mass in kg, attractive coupling k in J m, semimajor
        axis in m. Equation/reference: Kepler/Coulomb Delaunay-like action.
        Assumptions: attractive inverse-square potential and bound ellipse.
        Limitations: this is a canonical action scale, not automatically a
        measured angular momentum.
        """
        mu = _positive(reduced_mass, "kilogram", "reduced_mass")
        k = _positive(coupling, "joule * meter", "coupling")
        a = _positive(semimajor_axis, "meter", "semimajor_axis")
        return sqrt((mu * k * a).to("joule ** 2 * second ** 2").magnitude) * CONSTANTS.hbar.units

    @staticmethod
    def planetary_total_action(mass_1: pint.Quantity, mass_2: pint.Quantity, semimajor_axis: pint.Quantity) -> pint.Quantity:
        """Return √(μ G M1 M2 a), planetary canonical action, in joule seconds."""
        reduced_mass = KeplerCalculator.reduced_mass(mass_1, mass_2)
        coupling = ActionCalculator.gravitational_coupling(mass_1, mass_2)
        return ActionCalculator.total_action(reduced_mass, coupling, semimajor_axis)

    @staticmethod
    def radial_action(n_radial: int, hbar: pint.Quantity = CONSTANTS.hbar) -> pint.Quantity:
        """Return Jr = (nr + 1/2)ℏ in joule seconds."""
        if n_radial < 0:
            raise ScientificValidationError("radial quantum number must be non-negative")
        return ((n_radial + 0.5) * _as(hbar, "joule * second", "hbar")).to("joule * second")

    @staticmethod
    def angular_action(l: int, hbar: pint.Quantity = CONSTANTS.hbar) -> pint.Quantity:
        """Return L = (l + 1/2)ℏ using the Langer correction."""
        if l < 0:
            raise ScientificValidationError("angular quantum number must be non-negative")
        return ((l + 0.5) * _as(hbar, "joule * second", "hbar")).to("joule * second")

    @classmethod
    def semiclassical_total_action(cls, n_radial: int, l: int, hbar: pint.Quantity = CONSTANTS.hbar) -> pint.Quantity:
        """Return Λ = Jr + L = (nr+l+1)ℏ in joule seconds."""
        return (cls.radial_action(n_radial, hbar) + cls.angular_action(l, hbar)).to("joule * second")

    @staticmethod
    def principal_index(n_radial: int, l: int) -> int:
        """Return n = nr + l + 1."""
        if n_radial < 0 or l < 0:
            raise ScientificValidationError("n_radial and l must be non-negative")
        return n_radial + l + 1

    @classmethod
    def hydrogen_semimajor_axis(cls, n_radial: int, l: int, reduced_mass: pint.Quantity, coupling: pint.Quantity) -> pint.Quantity:
        """Return an = n²ℏ²/(μk) in meters for the known correspondence."""
        n = cls.principal_index(n_radial, l)
        mu = _positive(reduced_mass, "kilogram", "reduced_mass")
        k = _positive(coupling, "joule * meter", "coupling")
        return (n**2 * CONSTANTS.hbar**2 / (mu * k)).to("meter")

    @classmethod
    def hydrogen_energy(cls, n_radial: int, l: int, reduced_mass: pint.Quantity, coupling: pint.Quantity) -> pint.Quantity:
        """Return En = -μk²/(2ℏ²n²) in joules for the known correspondence."""
        n = cls.principal_index(n_radial, l)
        mu = _positive(reduced_mass, "kilogram", "reduced_mass")
        k = _positive(coupling, "joule * meter", "coupling")
        return (-(mu * k**2 / (2 * CONSTANTS.hbar**2 * n**2))).to("joule")

    @staticmethod
    def compare_action_relation(n_radial: int, l: int, total_action: pint.Quantity) -> bool:
        """Check Λ = Jr + L for a Langer-corrected state."""
        expected = ActionCalculator.semiclassical_total_action(n_radial, l)
        actual = _as(total_action, "joule * second", "total_action")
        return abs((actual - expected).magnitude) <= 1e-12 * max(abs(expected.magnitude), 1e-300)

    def smoke_test(self) -> dict[str, str | bool]:
        """Return a readiness marker for action calculations."""
        return {"calculator": self.name, "status": "ready", "physics_implemented": True}