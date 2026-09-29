import pytest

from app.core.exceptions import ScientificValidationError
from app.scientific.constants import CONSTANTS
from app.scientific.hydrogen import HydrogenCalculator
from tests.fixtures.scientific_data import hydrogen_ground_state, hydrogen_n2_state, hydrogen_n3_state


def test_hydrogen_ground_and_excited_state_energies() -> None:
    ground = hydrogen_ground_state()
    n2 = hydrogen_n2_state()
    n3 = hydrogen_n3_state()
    assert (ground.energy / CONSTANTS.electron_volt).magnitude == pytest.approx(-13.598, rel=2e-4)
    assert HydrogenCalculator.energy_ratio(1, 2) == pytest.approx(4.0)
    assert (HydrogenCalculator.binding_energy(2) / HydrogenCalculator.binding_energy(1)).magnitude == pytest.approx(0.25)
    assert (n2.energy / ground.energy).magnitude == pytest.approx(0.25)
    assert (n3.energy / ground.energy).magnitude == pytest.approx(1 / 9)


def test_hydrogen_bohr_radius_and_formal_scalings() -> None:
    a1 = HydrogenCalculator.characteristic_radius(1)
    a2 = HydrogenCalculator.characteristic_radius(2)
    t1 = HydrogenCalculator.formal_period(1)
    t2 = HydrogenCalculator.formal_period(2)
    v1 = HydrogenCalculator.formal_velocity(1)
    v2 = HydrogenCalculator.formal_velocity(2)
    assert a1.to("meter").magnitude == pytest.approx(HydrogenCalculator.bohr_radius().magnitude)
    assert a2.magnitude / a1.magnitude == pytest.approx(4.0)
    assert t2.magnitude / t1.magnitude == pytest.approx(8.0)
    assert v2.magnitude / v1.magnitude == pytest.approx(0.5)


def test_hydrogen_quantum_numbers_angular_momentum_and_nodes() -> None:
    state = hydrogen_n3_state()
    assert state.angular_momentum_squared.magnitude == pytest.approx(6 * CONSTANTS.hbar.magnitude**2)
    assert state.angular_momentum_z.magnitude == pytest.approx(CONSTANTS.hbar.magnitude)
    assert state.radial_nodes == 0
    assert state.angular_nodes == 2
    assert state.total_nodes == 2
    with pytest.raises(ScientificValidationError):
        HydrogenCalculator.state(2, 2, 0)
    with pytest.raises(ScientificValidationError):
        HydrogenCalculator.state(2, 1, 2)