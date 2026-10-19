#!/usr/bin/env python3
"""Regression: reject impossible power accounting without claiming real measurements."""
import json
import unittest
from pathlib import Path

from check_motor_current_budget import engineering_review_readiness

HERE = Path(__file__).resolve().parent

def hypothetical_complete():
    """In-memory test fixture only. Never write to evidence JSON."""
    d = json.loads((HERE / "motor_current_acceptance.json").read_text())
    d["unverified_field_values"].update(
        motor_sku="TEST_ONLY", motor_peak_phase_current_a=.065,
        actual_driver_max_simultaneous_phases=2,
        efuse_min_current_limit_a=1.5, controller_3v3_peak_a=.4,
        buck_min_efficiency=.85, five_volt_supply_sku="TEST_ONLY",
        five_volt_supply_min_current_a=3.0,
        board_measured_peak_input_a=1.5, board_measured_peak_motor_a=.92,
        five_volt_raw_min_during_transient_v=4.7)
    d["physical_test_results"]={str(i): {"status":"PASS","evidence":{"file":"execution/evidence/TEST_ONLY","sha256":"0"*64,"instrument_or_vendor":"TEST ONLY","recorded_utc":"2026-10-18T00:00:00Z"}} for i in range(6)}
    return d

class InputPowerConsistency(unittest.TestCase):
    def test_feasible_hypothetical_stays_review_only(self):
        d=hypothetical_complete()
        self.assertEqual(engineering_review_readiness(d), "READY_FOR_ENGINEERING_REVIEW_NOT_POWER_RELEASE")
        self.assertIs(d["hardware_release"],False)
    def test_noncoincident_peak_samples_do_not_fake_a_failure(self):
        d=hypothetical_complete()
        d["unverified_field_values"]["board_measured_peak_input_a"]=.8
        self.assertEqual(engineering_review_readiness(d),"READY_FOR_ENGINEERING_REVIEW_NOT_POWER_RELEASE")
    def test_undersized_source_still_fails(self):
        d=hypothetical_complete()
        d["unverified_field_values"]["five_volt_supply_min_current_a"]=1.8
        self.assertEqual(engineering_review_readiness(d),"FAIL_5V_SOURCE_MINIMUM_WITH_HEADROOM")
    def test_3v3_overload_retains_specific_failure(self):
        d=hypothetical_complete()
        d["unverified_field_values"]["controller_3v3_peak_a"]=2.5
        self.assertEqual(engineering_review_readiness(d),"FAIL_BUCK_3V3_WITH_HEADROOM")
    def test_missing_evidence_never_released(self):
        d=json.loads((HERE/"motor_current_acceptance.json").read_text())
        self.assertEqual(engineering_review_readiness(d),"HOLD_MISSING_MEASUREMENTS")
        self.assertIs(d["hardware_release"],False)

if __name__=="__main__":
    unittest.main()
