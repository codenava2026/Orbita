from fastapi import APIRouter

from app.scientific.constants import CONSTANTS, CONSTANTS_VERSION, constants_as_si
from app.scientific.hydrogen import HydrogenCalculator

router = APIRouter(prefix="/science", tags=["science"])


def _quantity_payload(quantity) -> dict[str, float | str]:
    base = quantity.to_base_units()
    return {"value": float(base.magnitude), "unit": str(base.units)}


@router.get("/constants")
def constants() -> dict[str, object]:
    """Return the versioned centralized constants used by the engine."""
    return {"version": CONSTANTS_VERSION, "system": "SI", "constants": constants_as_si()}


@router.get("/hydrogen/energy/{n}")
def hydrogen_energy(n: int) -> dict[str, object]:
    """Return analytical bound-state energy and positive binding energy."""
    energy = HydrogenCalculator.energy(n)
    return {
        "n": n,
        "energy": _quantity_payload(energy),
        "binding_energy": _quantity_payload(HydrogenCalculator.binding_energy(n)),
        "energy_electron_volts": float((energy / CONSTANTS.electron_volt).magnitude),
        "assumptions": [
            "non-relativistic isolated hydrogen",
            "reduced electron-proton mass",
            "analytical quantum-state relationship, not a classical orbit",
        ],
    }


@router.get("/hydrogen/state/{n}/{l}/{m}")
def hydrogen_state(n: int, l: int, m: int) -> dict[str, object]:
    """Return deterministic analytical hydrogen-state observables."""
    state = HydrogenCalculator.state(n, l, m)
    return {
        "n": state.n,
        "l": state.l,
        "m": state.m,
        "energy": _quantity_payload(state.energy),
        "angular_momentum_squared": _quantity_payload(state.angular_momentum_squared),
        "angular_momentum_z": _quantity_payload(state.angular_momentum_z),
        "radial_nodes": state.radial_nodes,
        "angular_nodes": state.angular_nodes,
        "total_nodes": state.total_nodes,
        "limitations": ["radial wavefunctions and probability densities are not solved in Phase 2"],
    }