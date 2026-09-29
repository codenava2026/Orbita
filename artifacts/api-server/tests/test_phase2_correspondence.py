import pytest

from app.core.exceptions import InvalidUnits
from app.scientific.action import ActionCalculator
from app.scientific.constants import CONSTANTS
from app.scientific.hydrogen import HydrogenCalculator
from app.scientific.normalization import (
    compare_effective_indices,
    n_eff_from_energy,
    n_eff_from_period,
    n_eff_from_semimajor_axis,
    normalize,
)
from app.scientific.units import quantity


def test_langer_action_relation_and_principal_index() -> None:
    total = ActionCalculator.semiclassical_total_action(2, 1)
    assert ActionCalculator.principal_index(2, 1) == 4
    assert ActionCalculator.compare_action_relation(2, 1, total)
    assert total.magnitude == pytest.approx(4 * CONSTANTS.hbar.magnitude)


def test_hydrogen_correspondence_scales_a_and_energy() -> None:
    mu = HydrogenCalculator.reduced_mass()
    coupling = HydrogenCalculator.coulomb_coupling()
    a1 = ActionCalculator.hydrogen_semimajor_axis(0, 0, mu, coupling)
    a2 = ActionCalculator.hydrogen_semimajor_axis(1, 0, mu, coupling)
    e1 = ActionCalculator.hydrogen_energy(0, 0, mu, coupling)
    e2 = ActionCalculator.hydrogen_energy(1, 0, mu, coupling)
    assert a2.magnitude / a1.magnitude == pytest.approx(4)
    assert e2.magnitude / e1.magnitude == pytest.approx(0.25)


def test_dimension_safe_normalization_and_effective_index_consistency() -> None:
    a_ref = quantity(1, "meter")
    t_ref = quantity(1, "second")
    energy_ref = quantity(-1, "joule")
    a_index = n_eff_from_semimajor_axis(quantity(4, "meter"), a_ref)
    t_index = n_eff_from_period(quantity(8, "second"), t_ref)
    energy_index = n_eff_from_energy(quantity(-0.25, "joule"), energy_ref)
    result = compare_effective_indices({"a": a_index, "t": t_index, "e": energy_index})
    assert result.passed
    assert a_index.value == pytest.approx(2)
    assert not a_index.is_quantum_number
    assert a_index.label == "dimensionless effective index"
    assert normalize(quantity(5, "meter"), quantity(2, "centimeter")) == pytest.approx(250)
    with pytest.raises(InvalidUnits):
        normalize(quantity(5, "meter"), quantity(2, "second"))