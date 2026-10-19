#!/usr/bin/env python3
"""Reject missing loads, underrated paths, motor/AON excess and false release."""
import copy
import json
from pathlib import Path
import unittest

from power_budget import estimate, evaluate_bounds

HERE = Path(__file__).resolve().parent


class PowerBudget(unittest.TestCase):
    def baseline(self):
        return json.loads((HERE / "components.json").read_text())

    def fixture(self):
        # IN-MEMORY NUMBERS ONLY. Never written as observed hardware evidence.
        d = self.baseline()
        d["adapter"].update(jack_part="TEST_ONLY", qualified_harness_current_a=5.0)
        d["qualified_raw_voltage_window_v"] = [4.5, 5.5]
        d["converter"].update(qualified_input_min_v=4.0, qualified_output_window_v=[3.1, 3.5])
        b = dict(waveshare_total_5v_peak_a=1.0, seven_driver_board_overhead_5v_peak_a=.1,
                 external_aon_total_3v3_peak_a=.1, aon_min_efficiency=.8,
                 motor_total_peak_a=1.0, lighting_total_peak_a=.3, fan_start_stall_peak_a=.09,
                 other_raw_5v_peak_a=0., efuse_guaranteed_min_limit_a=1.5,
                 measured_total_input_peak_a=2.5, minimum_raw_voltage_during_transient_v=4.7,
                 maximum_source_voltage_including_transient_v=5.25)
        return d, b

    def evaluate(self, d, b, **overrides):
        args = dict(source_min_a=5., raw_min_v=4.7, aon_max_v=3.432,
                    aon_qualified_a=.5, efuse_min_a=1.5, bounds=b)
        args.update(overrides)
        return evaluate_bounds(d, **args)

    def test_catalog_subtotal_does_not_fill_unknowns(self):
        d = self.baseline()
        before = copy.deepcopy(d)
        r = estimate(d)
        self.assertEqual(d, before)
        self.assertAlmostEqual(r["motor_coil_ohmic_estimate_a"], 7 * 5 / 21)
        self.assertAlmostEqual(r["partial_catalog_subtotal_a"], 7 * 5 / 21 + 20 / 60 * 4 / 5 + .045)
        self.assertAlmostEqual(r["motor_all_axes_upper_bound_by_phases_a"]["1"],
                               7 * 5.25 / (21 * (1 - .07)))
        self.assertAlmostEqual(r["motor_all_axes_upper_bound_by_phases_a"]["2"],
                               14 * 5.25 / (21 * (1 - .07)))
        self.assertAlmostEqual(r["source_comparison"][0]["remaining_for_all_unknowns_a"],
                               3 * .8 - r["partial_catalog_subtotal_a"])
        self.assertAlmostEqual(r["source_comparison"][1]["remaining_for_all_unknowns_a"],
                               5 * .8 - r["partial_catalog_subtotal_a"])
        self.assertIn("waveshare_total_5v_peak_a", r["missing"])
        self.assertFalse(r["hardware_release"])

    def test_no_missing_load_can_be_treated_as_zero(self):
        d, b = self.fixture()
        for field in b:
            case = b.copy()
            case[field] = None
            self.assertEqual(self.evaluate(d, case)["decision"], "HOLD_MISSING_BOUNDS", field)

    def test_input_path_and_voltage_qualification_are_required(self):
        d, b = self.fixture()
        self.assertEqual(self.evaluate(self.baseline(), b)["decision"], "HOLD_INPUT_PATH_UNQUALIFIED")
        d["qualified_raw_voltage_window_v"] = None
        self.assertEqual(self.evaluate(d, b)["decision"], "HOLD_VOLTAGE_COMPATIBILITY_UNQUALIFIED")

    def test_every_load_counts_and_small_jack_is_not_hidden_by_5a_adapter(self):
        d, b = self.fixture()
        self.assertEqual(self.evaluate(d, b)["decision"], "CONDITIONAL_NUMERIC_SCREEN_ONLY")
        for field in ("waveshare_total_5v_peak_a", "seven_driver_board_overhead_5v_peak_a",
                      "lighting_total_peak_a", "fan_start_stall_peak_a", "other_raw_5v_peak_a",
                      "measured_total_input_peak_a"):
            case = b.copy()
            case[field] = 5.
            self.assertEqual(self.evaluate(d, case)["decision"], "FAIL_INPUT_LIMIT_MARGIN", field)
        d["adapter"]["qualified_harness_current_a"] = 2.0
        self.assertEqual(self.evaluate(d, b)["decision"], "FAIL_INPUT_LIMIT_MARGIN")

    def test_motor_and_aon_limits_cannot_be_raised_by_supplying_bigger_source(self):
        d, b = self.fixture()
        b["motor_total_peak_a"] = 1.3
        self.assertEqual(self.evaluate(d, b)["decision"], "FAIL_MOTOR_LIMIT_MARGIN")
        b["motor_total_peak_a"] = 1.0
        b["external_aon_total_3v3_peak_a"] = .41
        self.assertEqual(self.evaluate(d, b)["decision"], "FAIL_AON_LIMIT_MARGIN")

    def test_transient_voltage_and_converter_tolerance_are_checked(self):
        d, b = self.fixture()
        b["minimum_raw_voltage_during_transient_v"] = 3.9
        self.assertEqual(self.evaluate(d, b)["decision"], "FAIL_VOLTAGE_COMPATIBILITY")
        b["minimum_raw_voltage_during_transient_v"] = 4.7
        b["maximum_source_voltage_including_transient_v"] = 9.
        self.assertEqual(self.evaluate(d, b)["decision"], "FAIL_VOLTAGE_COMPATIBILITY")
        b["maximum_source_voltage_including_transient_v"] = 5.25
        d["converter"]["qualified_output_window_v"] = [3.2, 3.4]
        self.assertEqual(self.evaluate(d, b)["decision"], "FAIL_VOLTAGE_COMPATIBILITY")

    def test_invalid_numbers_are_rejected_and_no_numeric_pass_enables_hardware(self):
        d, b = self.fixture()
        for value in (float("nan"), float("inf"), -1., True):
            case = b.copy()
            case["motor_total_peak_a"] = value
            with self.assertRaises(ValueError):
                self.evaluate(d, case)
        b["aon_min_efficiency"] = 1.01
        with self.assertRaises(ValueError):
            self.evaluate(d, b)
        d, b = self.fixture()
        self.assertFalse(self.evaluate(d, b)["hardware_release"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
