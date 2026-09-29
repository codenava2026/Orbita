"""Versioned CODATA-compatible physical constants.

All engine calculations use SI quantities from this module. The values are
centralized so a future constants revision can be introduced without
duplicating or silently changing constants across calculators.
"""

from dataclasses import dataclass

from app.scientific.units import ureg

CONSTANTS_VERSION = "CODATA-2018-compatible"


@dataclass(frozen=True)
class PhysicalConstants:
    """Central physical constants used by the Phase 2 analytical engines."""

    G = 6.67430e-11 * ureg("meter ** 3 / kilogram / second ** 2")
    hbar = 1.054571817e-34 * ureg("joule * second")
    h = 6.62607015e-34 * ureg("joule * second")
    c = 299_792_458 * ureg("meter / second")
    elementary_charge = 1.602176634e-19 * ureg("coulomb")
    epsilon_0 = 8.8541878128e-12 * ureg("farad / meter")
    electron_mass = 9.1093837015e-31 * ureg("kilogram")
    proton_mass = 1.67262192369e-27 * ureg("kilogram")
    earth_mass = 5.9722e24 * ureg("kilogram")
    solar_mass = 1.98847e30 * ureg("kilogram")
    astronomical_unit = 149_597_870_700 * ureg("meter")
    electron_volt = 1.602176634e-19 * ureg("joule")
    bohr_radius = 5.29177210903e-11 * ureg("meter")


CONSTANTS = PhysicalConstants()


def constants_as_si() -> dict[str, dict[str, float | str]]:
    """Return the centralized constants as JSON-safe SI values.

    Returns:
        A mapping of constant names to SI magnitude and unit strings.
    """
    values = {
        "G": CONSTANTS.G,
        "hbar": CONSTANTS.hbar,
        "h": CONSTANTS.h,
        "c": CONSTANTS.c,
        "elementary_charge": CONSTANTS.elementary_charge,
        "epsilon_0": CONSTANTS.epsilon_0,
        "electron_mass": CONSTANTS.electron_mass,
        "proton_mass": CONSTANTS.proton_mass,
        "earth_mass": CONSTANTS.earth_mass,
        "solar_mass": CONSTANTS.solar_mass,
        "astronomical_unit": CONSTANTS.astronomical_unit,
        "electron_volt": CONSTANTS.electron_volt,
        "bohr_radius": CONSTANTS.bohr_radius,
    }
    return {
        name: {"value": float(quantity.to_base_units().magnitude), "unit": str(quantity.to_base_units().units)}
        for name, quantity in values.items()
    }