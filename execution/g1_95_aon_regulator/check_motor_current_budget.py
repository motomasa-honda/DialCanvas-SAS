#!/usr/bin/env python3
"""G1-05 source-current evidence gate.

Converts the identified TPS259474/7-axis current-limit mismatch into an
explicit, executable engineering HOLD. This is analysis of candidate loads,
NOT hardware qualification. No motor is enabled or controlled.
"""
import json
import unittest
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "motor_current_acceptance.json"

@dataclass(frozen=True)
class Budget:
    limit_typ_a: float
    total_phase_current_a: float
    reserve_target_a: float
    per_phase_typ_a: float
    per_phase_reserve_a: float
    status: str

def evaluate(max_axes: int, phases_per_axis: int, phase_current_a: float,
             r_ilm_ohm: float = 2210.0, headroom_fraction: float = .20) -> Budget:
    """Conservative simultaneous-phase bounding; an example, not actual loads."""
    assert 1 <= max_axes <= 7
    assert 1 <= phases_per_axis <= 4
    assert 0 < r_ilm_ohm and 0 < phase_current_a < 10
    assert 0 <= headroom_fraction < 1
    # Manufacturer datasheet typical eFuse current limit equation as used in
    # existing G1-95 review; NOT guaranteed minimum, max, or thermally tested.
    typ = 3334.0 / r_ilm_ohm
    n = max_axes * phases_per_axis
    total = n * phase_current_a
    reserve = typ * (1 - headroom_fraction)
    status = "FAIL_VS_TYP" if total >= typ else (
        "FAIL_DESIGN_HEADROOM" if total >= reserve else "CONDITIONAL_ONLY")
    return Budget(typ, total, reserve, typ/n, reserve/n, status)

def input_current_requirement(motor_a: float, aon_output_a: float, buck_efficiency: float,
                              v_motor: float = 5.0, v_aon: float = 3.3,
                              v_input: float = 5.0) -> float:
    """Illustrative common-5V input burden. Must use proven loads to qualify."""
    assert motor_a >= 0 and aon_output_a >= 0
    assert 0 < buck_efficiency <= 1.0
    assert v_motor > 0 and v_aon > 0 and v_input > 0
    return motor_a*v_motor/v_input + (v_aon*aon_output_a)/(v_input*buck_efficiency)

class Contract(unittest.TestCase):
    def test_evidence_is_not_fabricated(self):
        d=json.loads(EVIDENCE.read_text(encoding="utf-8"))
        self.assertEqual(d["scope"], "G1-05/G1-06 design HOLD, never manufacturing approval")
        self.assertEqual(d["hardware_release"], False)
        self.assertEqual(d["manufacturer_release_gates_closed"], 0)
        self.assertEqual(d["assumptions"]["motor_axes"], 7)
        self.assertEqual(d["assumptions"]["simultaneous_phases_per_axis"], 2)
        self.assertEqual(d["assumptions"]["r_ilm_ohm"], 2210)
        self.assertEqual(d["assumptions"]["headroom_target_fraction"], .20)
        for field in ("motor_sku","motor_peak_phase_current_a","actual_driver_max_simultaneous_phases",
                      "efuse_min_current_limit_a","controller_3v3_peak_a","buck_min_efficiency",
                      "five_volt_supply_sku","five_volt_supply_min_current_a",
                      "board_measured_peak_input_a","board_measured_peak_motor_a"):
            self.assertIsNone(d["unverified_field_values"][field],field)
        self.assertEqual(len(d["physical_tests_required"]),6)

    def test_typical_eFuse_and_temporary_margin(self):
        b=evaluate(7,2,.080)
        self.assertAlmostEqual(b.limit_typ_a,3334/2210,places=7)
        self.assertAlmostEqual(b.per_phase_typ_a,3334/(2210*14),places=7)
        self.assertAlmostEqual(b.per_phase_reserve_a,(3334/2210)*.8/14,places=7)
        self.assertEqual(b.status,"CONDITIONAL_ONLY")

    def test_100ma_passes_typical_but_not_margin(self):
        self.assertEqual(evaluate(7,2,.1).status,"FAIL_DESIGN_HEADROOM")

    def test_160ma_would_exceed_eFuse(self):
        b=evaluate(7,2,.16)
        self.assertAlmostEqual(b.total_phase_current_a,2.24)
        self.assertGreater(b.total_phase_current_a,b.limit_typ_a)
        self.assertEqual(b.status,"FAIL_VS_TYP")

    def test_same_five_volt_source_must_include_always_on_buck(self):
        # Illustrative 1A on 3V3 and 85% efficiency, NOT a real reading.
        input_a=input_current_requirement(1.5,1.,.85)
        self.assertGreater(input_a,2.27)
        self.assertLess(input_a,2.28)
        self.assertLess(input_current_requirement(0,1.,.85),input_a)
        self.assertGreater(input_a,2.0)
        # Cannot declare a 2A adapter sufficient just because eFuse max is ~1.5A.

    def test_unspecified_parts_can_never_pass(self):
        d=json.loads(EVIDENCE.read_text(encoding="utf-8"))
        if any(x is None for x in d["unverified_field_values"].values()):
            verdict="HOLD_UNMEASURED_AND_UNSPECIFIED"
        else:
            verdict="REQUIRE_PHYSICAL_HIL_REVIEW"
        self.assertEqual(verdict,"HOLD_UNMEASURED_AND_UNSPECIFIED")

if __name__ == "__main__":
    print("G1-05/G1-06 current envelope: 7 axes x 2 phases = 14 simultaneous (conservative candidate)")
    v=evaluate(7,2,.160)
    print(f"HOLD: TPS259474 review RILM 2.21kohm gives typical {v.limit_typ_a:.3f}A; "
          f"with 20% design reserve {v.reserve_target_a:.3f}A => {v.per_phase_reserve_a*1000:.1f}mA/phase.")
    print(f"FAIL conditional 160mA/phase => {v.total_phase_current_a:.2f}A exceeds typical limit.")
    print("HOLD: real motor/driver/5V adapter/3V3 peak/efficiency/current waveform absent; never power device.")
    unittest.main(verbosity=2)
