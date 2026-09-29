import pytest

from app.core.exceptions import ScientificValidationError
from app.scientific.constants import CONSTANTS
from app.scientific.kepler import KeplerCalculator, KeplerConsistencyValidator
from tests.fixtures.scientific_data import idealized_kepler_orbit


def test_kepler_third_law_and_inverse_semimajor_axis() -> None:
    orbit = idealized_kepler_orbit()
    period = KeplerCalculator.period_from_semimajor_axis(orbit.mass_1, orbit.mass_2, orbit.semimajor_axis)
    recovered = KeplerCalculator.semimajor_axis_from_period(orbit.mass_1, orbit.mass_2, period)
    assert period.to("day").magnitude == pytest.approx(365.2569, rel=2e-4)
    assert recovered.to("meter").magnitude == pytest.approx(orbit.semimajor_axis.magnitude, rel=1e-12)


def test_kepler_energy_vis_viva_and_circular_velocity() -> None:
    orbit = idealized_kepler_orbit()
    energy = KeplerCalculator.total_orbital_energy(orbit.mass_1, orbit.mass_2, orbit.semimajor_axis)
    circular = KeplerCalculator.circular_velocity(orbit.mass_1, orbit.mass_2, orbit.semimajor_axis)
    vis_viva = KeplerCalculator.vis_viva_velocity(
        orbit.mass_1, orbit.mass_2, orbit.semimajor_axis, orbit.semimajor_axis
    )
    expected_energy = -(CONSTANTS.G * orbit.mass_1 * orbit.mass_2 / (2 * orbit.semimajor_axis)).to("joule")
    assert energy.magnitude == pytest.approx(expected_energy.magnitude, rel=1e-12)
    assert vis_viva.magnitude == pytest.approx(circular.magnitude, rel=1e-12)
    assert energy.magnitude < 0


def test_kepler_angular_momentum_geometry_and_mean_motion() -> None:
    orbit = idealized_kepler_orbit()
    h_specific = KeplerCalculator.specific_angular_momentum(
        orbit.mass_1, orbit.mass_2, orbit.semimajor_axis, orbit.eccentricity
    )
    angular = KeplerCalculator.angular_momentum(
        orbit.mass_1, orbit.mass_2, orbit.semimajor_axis, orbit.eccentricity
    )
    assert angular.to("joule * second").magnitude == pytest.approx(
        (KeplerCalculator.reduced_mass(orbit.mass_1, orbit.mass_2) * h_specific).to("joule * second").magnitude,
        rel=1e-12,
    )
    assert KeplerCalculator.periapsis(orbit.semimajor_axis, orbit.eccentricity).magnitude == pytest.approx(
        0.8 * orbit.semimajor_axis.magnitude
    )
    assert KeplerCalculator.apoapsis(orbit.semimajor_axis, orbit.eccentricity).magnitude == pytest.approx(
        1.2 * orbit.semimajor_axis.magnitude
    )
    mean_motion = KeplerCalculator.mean_motion(orbit.mass_1, orbit.mass_2, orbit.semimajor_axis)
    assert KeplerCalculator.period_from_mean_motion(mean_motion).magnitude == pytest.approx(
        KeplerCalculator.period_from_semimajor_axis(
            orbit.mass_1, orbit.mass_2, orbit.semimajor_axis
        ).magnitude,
        rel=1e-12,
    )


def test_kepler_consistency_validator_passes_and_rejects_invalid_eccentricity() -> None:
    orbit = idealized_kepler_orbit()
    period = KeplerCalculator.period_from_semimajor_axis(orbit.mass_1, orbit.mass_2, orbit.semimajor_axis)
    energy = KeplerCalculator.total_orbital_energy(orbit.mass_1, orbit.mass_2, orbit.semimajor_axis)
    angular = KeplerCalculator.angular_momentum(
        orbit.mass_1, orbit.mass_2, orbit.semimajor_axis, orbit.eccentricity
    )
    result = KeplerConsistencyValidator.validate(orbit, period=period, energy=energy, angular_momentum=angular)
    assert result.passed
    assert all(check.passed for check in result.checks)
    with pytest.raises(ScientificValidationError):
        KeplerCalculator.periapsis(orbit.semimajor_axis, 1.0)