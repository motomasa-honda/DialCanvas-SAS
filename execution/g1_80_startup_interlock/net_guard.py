#!/usr/bin/env python3
"""Existing physical register boundaries remain disabled; no KiCad/ERC/HIL."""
import json
from pathlib import Path
root = Path(__file__).resolve().parent.parent
n77 = json.loads((root / "g1_phase77_140pins/nets_140.json").read_text())["nets"]
n78 = json.loads((root / "g1_28phase_disabled/nets_208.json").read_text())["nets"]
c78 = json.loads((root / "g1_28phase_disabled/design_contract.json").read_text())
def inverse(nets):
    pins = {}
    for name, endpoints in nets.items():
        for pad in endpoints:
            if pad in pins:
                raise AssertionError(f"duplicate physical pad {pad}")
            pins[pad] = name
    return pins
p77 = inverse(n77)
p78 = inverse(n78)
assert len(p77) == 140 and len(n77) == 39
assert len(p78) == 208 and len(n78) == 63
assert p77["U7.1"] == p77["R_EN_PD.1"] == "U7_EN_CLAMPED_DISABLED"
assert p77["R_EN_PD.2"] == "GND"
assert p77["U_ARM.5"] == "ARM_LATCH_Q_ISOLATED"
assert p77["U7.3"] == "EFUSE_PG_OD"  # cannot be truthy power-good without rail sense
assert p77["U7.4"] == "PGTH_SENSE"
assert p77["U7.6"] == "5V_MOTOR"
assert p77["U7.5"] == "5V_RAW"
assert c78["actual_secondary_gating_status"].startswith("TRISTATE_AND_PULLDOWN_UNQUALIFIED")
assert c78["physical_enable_condition"].startswith("NOT_CONNECTED")
for chip in range(1, 5):
    for pin in (1, 19):
        assert p78[f"U_BUF{chip}.{pin}"] == "PHASE_OE_N_FIXED_HIGH"
    assert p78[f"R_OE_PULL{chip}.2"] == "VCC_3V3_AON"
for axis in range(1, 8):
    for phase in range(1, 5):
        name = f"MODULE_G{axis}_PHASE{phase}"
        assert p78[f"R_PD_G{axis}_{phase}.1"] == name
        assert p78[f"R_PD_G{axis}_{phase}.2"] == "GND"
        assert p78[f"J_MODULE_G{axis}.{phase}"] == name
print("PASS: original physical 140/208 pad registers, motor rail grounded and 28 OE disabled")
print("HOLD: no real PG-fault latch, 2nd motor-rail supervisor, runtime OE or EN gate wired")
