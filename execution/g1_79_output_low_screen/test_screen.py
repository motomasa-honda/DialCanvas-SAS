#!/usr/bin/env python3
"""Regression and fault injection: DC screening only, no real HIL/ERC."""
import copy
import json
import math
import unittest
from screen import (
    HERE, ROOT, check_original_28_lane_register, illustrative_below_vil,
    illustrative_cases, off_node_voltage
)


class G179ScreenTests(unittest.TestCase):
    def test_original_28_phases_and_motor_gate(self):
        self.assertEqual(check_original_28_lane_register(), 28)

    def test_28_independent_pulldown_disconnect_faults_caught(self):
        original = json.loads((ROOT / "g1_28phase_disabled" / "nets_208.json").read_text())["nets"]
        for a in range(1, 8):
            for p in range(1, 5):
                bad = copy.deepcopy(original)
                bad[f"MODULE_G{a}_PHASE{p}"].remove(f"R_PD_G{a}_{p}.1")
                with self.assertRaises(AssertionError, msg=f"axis {a}, phase {p}"):
                    check_original_28_lane_register(bad)

    def test_pullup_10k_cannot_claim_low(self):
        # Vpu=5V, Rpu=Rpd=10k => 2.5V. 0.8V VIL is hypothetical.
        v = off_node_voltage(5.0, 10000, 10000)
        self.assertAlmostEqual(v, 2.5)
        self.assertFalse(illustrative_below_vil(v, 0.8))

    def test_100k_pullup_passes_only_ideal_threshold(self):
        v = off_node_voltage(5.0, 100000, 10000)
        self.assertAlmostEqual(v, 5.0 / 11.0)
        self.assertTrue(illustrative_below_vil(v, 0.8))

    def test_source_leakage_alone_overrides_weak_pd(self):
        self.assertAlmostEqual(off_node_voltage(0, None, 10000, 100), 1.0)
        self.assertFalse(illustrative_below_vil(1.0, 0.8))

    def test_tolerances_make_hypothetical_worst_case_worse(self):
        self.assertAlmostEqual(off_node_voltage(5.25, 9500, 10500, 100), 3.255)

    def test_exact_fixture_cases(self):
        cases = illustrative_cases()
        self.assertEqual(len(cases), 4)
        results = [
            illustrative_below_vil(off_node_voltage(*values[:4]), values[4])
            for values in cases.values()
        ]
        self.assertEqual(results, [False, True, False, False])

    def test_reject_invalid_inputs(self):
        for args in [
            (-1, 10000, 10000, 0),
            (5, 0, 10000, 0),
            (5, 10000, 0, 0),
            (5, 10000, 10000, -1),
            (float("nan"), None, 10000, 0),
            (5, float("inf"), 10000, 0),
        ]:
            with self.assertRaises(ValueError):
                off_node_voltage(*args)
        with self.assertRaises(ValueError):
            illustrative_below_vil(1, -1)

if __name__ == "__main__":
    unittest.main()
