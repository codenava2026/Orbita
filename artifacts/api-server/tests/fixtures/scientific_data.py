from app.scientific.constants import CONSTANTS
from app.scientific.hydrogen import HydrogenCalculator
from app.scientific.kepler import KeplerOrbit


def idealized_kepler_orbit() -> KeplerOrbit:
    return KeplerOrbit(
        mass_1=CONSTANTS.solar_mass,
        mass_2=CONSTANTS.earth_mass,
        semimajor_axis=CONSTANTS.astronomical_unit,
        eccentricity=0.2,
    )


def hydrogen_ground_state():
    return HydrogenCalculator.state(1, 0, 0)


def hydrogen_n2_state():
    return HydrogenCalculator.state(2, 1, 0)


def hydrogen_n3_state():
    return HydrogenCalculator.state(3, 2, 1)