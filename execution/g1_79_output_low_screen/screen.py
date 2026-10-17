#!/usr/bin/env python3
"""G1-79 ideal output-low screening only; never hardware safety approval.

The unknown motor-module pull-up and leakage are hypothetical parameters.
Circuit: Vpu -- Rpu -- node -- Rpd -- GND; positive I_source injects at node.
3-state buffer output is assumed Z, an UNVERIFIED physical premise.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def off_node_voltage(vpu, rpu_ohm, rpd_ohm, source_leakage_ua=0.0):
    """Ideal DC node V; None for absent module pull-up."""
    if not (math.isfinite(vpu) and vpu >= 0):
        raise ValueError("Vpu must be nonnegative/finite")
    if rpu_ohm is not None and not (math.isfinite(rpu_ohm) and rpu_ohm > 0):
        raise ValueError("Rpu must be positive/finite or None")
    if not (math.isfinite(rpd_ohm) and rpd_ohm > 0):
        raise ValueError("Rpd must be positive/finite")
    if not (math.isfinite(source_leakage_ua) and source_leakage_ua >= 0):
        raise ValueError("source leakage must be nonnegative/finite")
    gp = (1.0 / rpu_ohm) if rpu_ohm is not None else 0.0
    gd = 1.0 / rpd_ohm
    return (vpu * gp + source_leakage_ua * 1e-6) / (gp + gd)


def illustrative_below_vil(vnode, vil_max):
    """A hypothetical DC-only threshold screen, NOT a pass-to-energize."""
    if not (math.isfinite(vil_max) and vil_max >= 0):
        raise ValueError("VIL threshold must be nonnegative/finite")
    return vnode <= vil_max


def check_original_28_lane_register(nets_override=None):
    """Validate each registered external motor input has its own ground Rpd.

    This is an immutable-review netlist, not proof that a fabricated board
    or attached module actually has the registered wiring.
    """
    netdata = json.loads((ROOT / "g1_28phase_disabled" / "nets_208.json").read_text())
    contract = json.loads((ROOT / "g1_28phase_disabled" / "design_contract.json").read_text())
    arm = json.loads((ROOT / "g1_phase77_140pins" / "nets_140.json").read_text())["nets"]
    nets = nets_override if nets_override is not None else netdata["nets"]
    if (contract["active_lanes"], contract["motor_axes"], contract["phase_per_axis"]) != (28, 7, 4):
        raise AssertionError("28-lane contract changed")
    if len(nets) != 63:
        raise AssertionError("net count drift")
    pins = {}
    for net, pads in nets.items():
        for pad in pads:
            if pad in pins:
                raise AssertionError("duplicate pad: " + pad)
            pins[pad] = net
    if len(pins) != 208:
        raise AssertionError("pad count drift")
    fixed_oe = nets["PHASE_OE_N_FIXED_HIGH"]
    if set(fixed_oe) != (
        {f"U_BUF{n}.{p}" for n in range(1, 5) for p in (1, 19)}
        | {f"R_OE_PULL{n}.1" for n in range(1, 5)}
    ):
        raise AssertionError("OE is not fixed-high as reviewed")
    for idx in range(1, 5):
        if pins[f"R_OE_PULL{idx}.2"] != "VCC_3V3_AON":
            raise AssertionError("OE pull-up not tied to standby rail")
    for axis in range(1, 8):
        for phase in range(1, 5):
            mn = f"MCU_G{axis}_PHASE{phase}"
            dn = f"MODULE_G{axis}_PHASE{phase}"
            rpd = f"R_PD_G{axis}_{phase}"
            if set(nets[dn]) != {
                f"J_MODULE_G{axis}.{phase}", f"{rpd}.1",
                next((p for p in nets[dn] if p.startswith("U_BUF")), "MISSING_BUFFER"),
            }:
                raise AssertionError(f"driver output/pulldown missing: {dn}")
            if pins[f"{rpd}.2"] != "GND":
                raise AssertionError(f"pulldown does not reach ground: {dn}")
            if pins[f"J_MCU_G{axis}.{phase}"] != mn:
                raise AssertionError("MCU lane input drift")
            if mn == dn:
                raise AssertionError("input bypassed buffer")
    if set(arm["U7_EN_CLAMPED_DISABLED"]) != {"U7.1", "R_EN_PD.1"}:
        raise AssertionError("motor eFuse EN gate changed")
    if "R_EN_PD.2" not in arm["GND"]:
        raise AssertionError("eFuse EN is not grounded")
    if "U_ARM.5" not in arm["ARM_LATCH_Q_ISOLATED"]:
        raise AssertionError("arming output no longer isolated")
    return 28


def illustrative_cases():
    """These fixture values are NOT real module measurements or datasheet limits."""
    return {
        "5V_internal_pullup_10k": (5.0, 10000, 10000, 0.0, 0.8),
        "5V_internal_pullup_100k": (5.0, 100000, 10000, 0.0, 0.8),
        "unpowered_module_100uA_source": (0.0, None, 10000, 100.0, 0.8),
        "worst_illustrative_tolerances": (5.25, 9500, 10500, 100.0, 0.8),
    }


if __name__ == "__main__":
    n = check_original_28_lane_register()
    print(f"PASS static register: {n}/28 output resistors and eFuse EN still GND")
    for name, values in illustrative_cases().items():
        v = off_node_voltage(*values[:4])
        safe = illustrative_below_vil(v, values[4])
        print(f"{name}: Vnode={v:.3f}V, hypothetical <=VIL screen={'YES' if safe else 'NO'}")
    print("HOLD: ALL hardware gates; no actual driver VIL/leakage/pullup/IOFF/power-sequence measurement")
